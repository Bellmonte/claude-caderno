# Tamanho do modelo aberto no Desktop, pela mesma fonte do VertiPaq Analyzer.
#
# Total = dicionario das colunas de dados + tamanho usado de todos os segmentos.
# POS_TO_ID, ID_TO_POS (indices da tabela), RowNumber e o que mais nao for coluna de dados
# entram no total e ficam fora do ranking de colunas.
#
# Uso:
#   .\tamanho_modelo.ps1 -Saida local\performance\<painel>\antes [-Port 50810] [-Top 10]
#
# Grava tamanho_colunas.csv, tamanho_tabelas.csv e tamanho_meta.json na pasta de saida.
# A tela mostra so agregados: nenhum dado do modelo, apenas nomes de tabela e coluna.

param([int]$Port, [Parameter(Mandatory)][string]$Saida, [int]$Top = 10)

. "$PSScriptRoot\_comum.ps1"

$Port = Resolve-PbiPorta $Port
$conn = Open-PbiConexao $Port
try {
    $segmentos = Invoke-PbiDax $conn @'
EVALUATE
GROUPBY(
    SELECTCOLUMNS(INFO.STORAGETABLECOLUMNSEGMENTS(), "t", [DIMENSION_NAME], "c", [COLUMN_ID], "b", [USED_SIZE]),
    [t], [c], "dados", SUMX(CURRENTGROUP(), [b])
)
'@
    $dicionario = Invoke-PbiDax $conn @'
EVALUATE
SELECTCOLUMNS(
    FILTER(INFO.STORAGETABLECOLUMNS(), [COLUMN_TYPE] = "BASIC_DATA"),
    "t", [DIMENSION_NAME], "c", [COLUMN_ID], "nome", [ATTRIBUTE_NAME], "dic", [DICTIONARY_SIZE]
)
'@
    $meta = Get-MetaMedicao $conn $Port 'tamanho'
    $meta.banco = (Get-PbiBanco $conn).Nome
} finally { $conn.Close() }

$dados = @{}
foreach ($s in $segmentos) { $dados["$($s.t)|$($s.c)"] = [double]$s.dados }

$colunas = foreach ($d in $dicionario) {
    $chave = "$($d.t)|$($d.c)"
    $dd = if ($dados.ContainsKey($chave)) { $dados[$chave] } else { 0 }
    $dados.Remove($chave)
    [pscustomobject]@{
        tabela = $d.t; coluna = $d.nome; dicionario = [double]$d.dic; dados = $dd
        total = [double]$d.dic + $dd
    }
}
$colunas = @($colunas | Where-Object { $_.coluna -notlike 'RowNumber*' } | Sort-Object total -Descending)

# O que sobrou nos segmentos sem par no dicionario e indice ou estrutura interna.
$internoPorTabela = @{}
foreach ($k in $dados.Keys) {
    $t = $k.Split('|')[0]
    $internoPorTabela[$t] = [double]$internoPorTabela[$t] + $dados[$k]
}
$rowNumber = $dicionario | Where-Object { $_.nome -like 'RowNumber*' }
foreach ($r in $rowNumber) { $internoPorTabela[$r.t] = [double]$internoPorTabela[$r.t] + [double]$r.dic }

$tabelas = $colunas | Group-Object tabela | ForEach-Object {
    $col = ($_.Group | Measure-Object total -Sum).Sum
    $int = [double]$internoPorTabela[$_.Name]
    [pscustomobject]@{ tabela = $_.Name; colunas = $col; indices_internos = $int; total = $col + $int }
}
foreach ($t in $internoPorTabela.Keys | Where-Object { $_ -notin $colunas.tabela }) {
    $tabelas = @($tabelas) + [pscustomobject]@{ tabela = $t; colunas = 0; indices_internos = $internoPorTabela[$t]; total = $internoPorTabela[$t] }
}
$tabelas = @($tabelas | Sort-Object total -Descending)
$totalModelo = ($tabelas | Measure-Object total -Sum).Sum
$meta.total_bytes = $totalModelo

New-Item -ItemType Directory -Force $Saida | Out-Null
$colunas | Export-Csv (Join-Path $Saida 'tamanho_colunas.csv') -NoTypeInformation -Delimiter ';' -Encoding UTF8
$tabelas | Export-Csv (Join-Path $Saida 'tamanho_tabelas.csv') -NoTypeInformation -Delimiter ';' -Encoding UTF8
Save-Meta $meta $Saida 'tamanho_meta.json'

$mb = { param($b) '{0,9:N2} MB' -f ($b / 1MB) }
"Modelo: $(& $mb $totalModelo)  ($($tabelas.Count) tabelas, $($colunas.Count) colunas de dados)"
"Desktop $($meta.versao_desktop), maquina $($meta.maquina)"
""
"Tabelas:"
$tabelas | Select-Object -First $Top | ForEach-Object { "  $(& $mb $_.total)  $($_.tabela)   (indices e internos $(& $mb $_.indices_internos))" }
""
"Maiores colunas:"
$colunas | Select-Object -First $Top | ForEach-Object {
    $pct = if ($_.total) { $_.dicionario / $_.total } else { 0 }
    "  $(& $mb $_.total)  $($_.tabela)[$($_.coluna)]   dicionario {0:P0}" -f $pct
}
