# Repete a frio e a quente as consultas DAX que os visuais pediram ao modelo.
#
# Entrada: o JSON exportado pelo analisador de desempenho do Desktop. Cada evento
# "Execute DAX Query" traz o texto completo da consulta em metrics.QueryText; o script
# sobe pela cadeia de parentId ate achar o visual dono da consulta e descarta repeticoes.
#
# Frio: o cache do banco e limpo imediatamente antes de cada execucao, e so a execucao
# entra no cronometro. Quente: as mesmas consultas, sem limpar. O tempo inclui ler todas
# as linhas do resultado. Isso mede o motor (a consulta DAX); o desenho do visual na tela
# so existe no JSON do analisador.
#
# Conferencia do frio: a mediana a frio tem que sair maior que a mediana a quente. Se nao
# sair, a consulta fica marcada "suspeito" e a rodada nao serve para afirmar nada. Consulta
# que roda abaixo do piso nos dois modos fica "indistinguivel", porque ali o ruido manda.
#
# Uso:
#   .\medir_consultas.ps1 -Json local\performance\<painel>\analisador.json `
#                         -Saida local\performance\<painel>\antes [-Port 50810] [-Runs 5]
#                         [-Consultas q03,q07] [-SoListar]
#
# -SoListar le o JSON e mostra as consultas por visual, sem conectar no modelo.
# -Consultas limita a remedicao a um subconjunto, pelos ids gravados em consultas.json.
#
# Grava em -Saida: consultas.json (id, visual e texto da consulta), consultas_execucoes.csv
# (uma linha por execucao), consultas_resumo.csv e consultas_meta.json. O texto da consulta
# pode levar valor literal de filtro, e por isso fica so em arquivo local, nunca na tela.

param(
    [Parameter(Mandatory)][string]$Json,
    [string]$Saida,
    [int]$Port,
    [int]$Runs = 5,
    [string[]]$Consultas,
    [double]$PisoMs = 10,
    [int]$TimeoutSeg = 600,
    [switch]$SoListar
)

. "$PSScriptRoot\_comum.ps1"

# ---------- leitura do JSON do analisador ----------
Add-Type -AssemblyName System.Web.Extensions
$ser = New-Object System.Web.Script.Serialization.JavaScriptSerializer
$ser.MaxJsonLength = [int]::MaxValue
$raiz = $ser.DeserializeObject((Get-Content $Json -Raw -Encoding UTF8))
$eventos = @($raiz['events'])
if (-not $eventos.Count) { throw "O arquivo nao tem a lista 'events'. Confira se e o export do analisador de desempenho." }

function Get-Campo($d, [string]$k) { if ($d -and $d.ContainsKey($k)) { $d[$k] } }
function Get-Instante($s) { if ($s) { [datetime]::Parse($s, $null, [Globalization.DateTimeStyles]::RoundtripKind) } }

$porId = @{}
foreach ($e in $eventos) { $id = Get-Campo $e 'id'; if ($id) { $porId[$id] = $e } }

# Blocos: cada User Action (atualizar visuais, trocar de pagina) abre um bloco pelo tempo.
$acoes = @($eventos | Where-Object { (Get-Campo $_ 'name') -eq 'User Action' } |
    ForEach-Object { Get-Instante (Get-Campo $_ 'start') } | Sort-Object)

function Get-Visual($e) {
    $atual = $e; $passos = 0
    while ($atual -and $passos -lt 20) {
        $m = Get-Campo $atual 'metrics'
        $vid = Get-Campo $m 'visualId'
        if ($vid) {
            return [pscustomobject]@{ id = $vid; titulo = [string](Get-Campo $m 'visualTitle'); tipo = [string](Get-Campo $m 'visualType') }
        }
        $pai = Get-Campo $atual 'parentId'
        $atual = if ($pai) { $porId[$pai] } else { $null }
        $passos++
    }
    [pscustomobject]@{ id = '(sem visual)'; titulo = ''; tipo = '' }
}

$vistas = [ordered]@{}
foreach ($e in $eventos) {
    if ((Get-Campo $e 'name') -ne 'Execute DAX Query') { continue }
    $texto = [string](Get-Campo (Get-Campo $e 'metrics') 'QueryText')
    if (-not $texto.Trim()) { continue }
    $chave = ($texto -replace '\s+', ' ').Trim()
    $inicio = Get-Instante (Get-Campo $e 'start')
    $fim = Get-Instante (Get-Campo $e 'end')
    $ms = if ($inicio -and $fim) { ($fim - $inicio).TotalMilliseconds } else { $null }
    if ($vistas.Contains($chave)) {
        $vistas[$chave].ocorrencias++
        if ($null -ne $ms) { $vistas[$chave].ms_analisador += $ms }
        continue
    }
    $bloco = @($acoes | Where-Object { $_ -le $inicio }).Count
    $v = Get-Visual $e
    $vistas[$chave] = [pscustomobject]@{
        id = ''; visual_id = $v.id; visual_titulo = $v.titulo; visual_tipo = $v.tipo
        bloco = $bloco; ocorrencias = 1; ms_analisador = @($ms | Where-Object { $null -ne $_ }); texto = $texto
    }
}
$lista = @($vistas.Values)
for ($i = 0; $i -lt $lista.Count; $i++) { $lista[$i].id = 'q{0:D2}' -f ($i + 1) }
if (-not $lista.Count) { throw 'Nenhum evento Execute DAX Query com texto no arquivo.' }

"{0} consultas distintas em {1} visuais, {2} blocos de acao" -f $lista.Count, @($lista.visual_id | Sort-Object -Unique).Count, $acoes.Count
foreach ($q in $lista) {
    $ma = if ($q.ms_analisador.Count) { '{0,8:N0} ms no analisador' -f (Get-Mediana ([double[]]$q.ms_analisador)) } else { '' }
    "  {0}  bloco {1}  {2,-18} {3}  x{4} {5}" -f $q.id, $q.bloco, $q.visual_tipo, $q.visual_titulo, $q.ocorrencias, $ma
}
if ($SoListar) { return }
if (-not $Saida) { throw 'Informe -Saida para medir.' }

if ($Consultas) {
    $lista = @($lista | Where-Object { $_.id -in $Consultas })
    if (-not $lista.Count) { throw "Nenhuma das consultas pedidas existe: $($Consultas -join ', ')" }
}

New-Item -ItemType Directory -Force $Saida | Out-Null
$lista | Select-Object id, visual_id, visual_titulo, visual_tipo, bloco, ocorrencias, texto |
    ConvertTo-Json -Depth 4 | Out-File (Join-Path $Saida 'consultas.json') -Encoding utf8

# ---------- medicao ----------
function Measure-Consulta($conn, [string]$Dax) {
    $c = $conn.CreateCommand(); $c.CommandText = $Dax; $c.CommandTimeout = $TimeoutSeg
    $sw = [Diagnostics.Stopwatch]::StartNew()
    $r = $c.ExecuteReader()
    $n = 0; while ($r.Read()) { $n++ }
    $r.Close()
    $sw.Stop()
    [pscustomobject]@{ ms = [math]::Round($sw.Elapsed.TotalMilliseconds, 1); linhas = $n }
}

$Port = Resolve-PbiPorta $Port
$conn = Open-PbiConexao $Port
$execucoes = New-Object System.Collections.Generic.List[object]
$resumo = New-Object System.Collections.Generic.List[object]
try {
    $banco = Get-PbiBanco $conn
    $meta = Get-MetaMedicao $conn $Port 'consultas'
    $meta.banco = $banco.Nome
    $meta.json_origem = Split-Path $Json -Leaf
    $meta.rodadas = $Runs
    $meta.piso_ms = $PisoMs
    ""
    "Medindo na porta $Port, $Runs a frio e $Runs a quente por consulta. Nao mexa no Desktop."
    foreach ($q in $lista) {
        $frio = @(); $quente = @(); $erro = ''; $linhas = $null
        try {
            for ($r = 1; $r -le $Runs; $r++) {
                Clear-PbiCache $conn $banco.Id
                $m = Measure-Consulta $conn $q.texto
                $frio += $m.ms; $linhas = $m.linhas
                $execucoes.Add([pscustomobject]@{ consulta = $q.id; visual_id = $q.visual_id; rodada = $r; cache = 'frio'; ms = $m.ms; linhas = $m.linhas })
            }
            for ($r = 1; $r -le $Runs; $r++) {
                $m = Measure-Consulta $conn $q.texto
                $quente += $m.ms
                $execucoes.Add([pscustomobject]@{ consulta = $q.id; visual_id = $q.visual_id; rodada = $r; cache = 'quente'; ms = $m.ms; linhas = $m.linhas })
            }
        } catch {
            $erro = ($_.Exception.Message -split "`n")[0]
            if ($erro.Length -gt 200) { $erro = $erro.Substring(0, 200) }
        }
        $mf = Get-Mediana ([double[]]$frio); $mq = Get-Mediana ([double[]]$quente)
        $status = if ($erro) { 'erro' }
                  elseif ($mf -lt $PisoMs -and $mq -lt $PisoMs) { 'indistinguivel' }
                  elseif ($mf -gt $mq) { 'ok' }
                  else { 'suspeito' }
        $linha = [pscustomobject]@{
            consulta = $q.id; visual_id = $q.visual_id; visual_titulo = $q.visual_titulo; visual_tipo = $q.visual_tipo
            bloco = $q.bloco; linhas = $linhas
            frio_mediana = $mf; frio_min = ($frio | Measure-Object -Minimum).Minimum; frio_max = ($frio | Measure-Object -Maximum).Maximum
            quente_mediana = $mq; quente_min = ($quente | Measure-Object -Minimum).Minimum; quente_max = ($quente | Measure-Object -Maximum).Maximum
            status = $status; erro = $erro
        }
        $resumo.Add($linha)
        "  {0}  frio {1,9:N1} ms [{2:N1} a {3:N1}]  quente {4,9:N1} ms  {5}  {6}" -f $q.id, $mf, $linha.frio_min, $linha.frio_max, $mq, $status, $q.visual_titulo
    }
} finally { $conn.Close() }

$execucoes | Export-Csv (Join-Path $Saida 'consultas_execucoes.csv') -NoTypeInformation -Delimiter ';' -Encoding UTF8
$resumo | Export-Csv (Join-Path $Saida 'consultas_resumo.csv') -NoTypeInformation -Delimiter ';' -Encoding UTF8

$avaliaveis = @($resumo | Where-Object { $_.status -in 'ok', 'suspeito' })
$suspeitas = @($avaliaveis | Where-Object { $_.status -eq 'suspeito' })
$meta.consultas = $resumo.Count
$meta.suspeitas = $suspeitas.Count
$meta.erros = @($resumo | Where-Object { $_.status -eq 'erro' }).Count
$meta.frio_valido = -not ($avaliaveis.Count -and ($suspeitas.Count / $avaliaveis.Count) -gt 0.3)
Save-Meta $meta $Saida 'consultas_meta.json'

""
"Mais lentas a frio:"
$resumo | Where-Object { $_.status -ne 'erro' } | Sort-Object frio_mediana -Descending | Select-Object -First 10 | ForEach-Object {
    "  {0,9:N1} ms  {1}  {2} ({3})" -f $_.frio_mediana, $_.consulta, $_.visual_titulo, $_.visual_tipo
}
if ($meta.erros) { ""; "Consultas com erro: $($meta.erros). Detalhe em consultas_resumo.csv." }
if (-not $meta.frio_valido) {
    ""
    "ATENCAO: $($suspeitas.Count) de $($avaliaveis.Count) consultas nao ficaram mais lentas a frio. A limpeza de cache nao pegou, e esta rodada nao serve de linha de base."
}
