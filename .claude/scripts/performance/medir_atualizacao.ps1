# Tempo de atualizacao completa do modelo aberto no Desktop, por comando TMSL.
#
# A execucao 0 e aquecimento e sai da conta. O Desktop precisa estar aberto e parado
# enquanto o script roda: a atualizacao ocupa o modelo e pode levar varios minutos.
#
# Uso:
#   .\medir_atualizacao.ps1 -Saida local\performance\<painel>\antes [-Port 50810] [-Runs 6]
#
# Grava atualizacao.csv (execucao;segundos;aquecimento) e atualizacao_meta.json.

param([int]$Port, [Parameter(Mandatory)][string]$Saida, [int]$Runs = 6, [int]$TimeoutSeg = 1800)

. "$PSScriptRoot\_comum.ps1"

$Port = Resolve-PbiPorta $Port
$conn = Open-PbiConexao $Port
$linhas = @()
try {
    $banco = Get-PbiBanco $conn
    $meta = Get-MetaMedicao $conn $Port 'atualizacao'
    $meta.banco = $banco.Nome
    $tmsl = '{"refresh":{"type":"full","objects":[{"database":"' + $banco.Nome + '"}]}}'
    for ($i = 0; $i -lt $Runs; $i++) {
        $c = $conn.CreateCommand(); $c.CommandText = $tmsl; $c.CommandTimeout = $TimeoutSeg
        $sw = [Diagnostics.Stopwatch]::StartNew()
        $null = $c.ExecuteNonQuery()
        $sw.Stop()
        $seg = [math]::Round($sw.Elapsed.TotalSeconds, 2)
        $linhas += [pscustomobject]@{ execucao = $i; segundos = $seg; aquecimento = [int]($i -eq 0) }
        "{0};{1}{2}" -f $i, $seg, $(if ($i -eq 0) { ' (aquecimento)' } else { '' })
    }
} finally { $conn.Close() }

$validas = [double[]]($linhas | Where-Object { -not $_.aquecimento } | ForEach-Object segundos)
$meta.execucoes = $validas.Count
$meta.mediana_seg = Get-Mediana $validas
$meta.min_seg = ($validas | Measure-Object -Minimum).Minimum
$meta.max_seg = ($validas | Measure-Object -Maximum).Maximum

New-Item -ItemType Directory -Force $Saida | Out-Null
$linhas | Export-Csv (Join-Path $Saida 'atualizacao.csv') -NoTypeInformation -Delimiter ';' -Encoding UTF8
Save-Meta $meta $Saida 'atualizacao_meta.json'

""
"Atualizacao completa: mediana {0:N2} s, faixa {1:N2} a {2:N2} s, {3} execucoes validas" -f $meta.mediana_seg, $meta.min_seg, $meta.max_seg, $meta.execucoes
