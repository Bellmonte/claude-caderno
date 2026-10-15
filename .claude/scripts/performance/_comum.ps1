# Funcoes compartilhadas pelos scripts de medicao de performance do Power BI.
# Carregar com: . "$PSScriptRoot\_comum.ps1"
#
# Tudo aqui conversa com o Desktop aberto na maquina, pela biblioteca de cliente que vem
# dentro do proprio Power BI Desktop. Nenhuma credencial, nenhum servico: localhost.

$ErrorActionPreference = 'Stop'

$script:PbiBin = 'C:\Program Files\Microsoft Power BI Desktop\bin'
$script:AdomdDll = Join-Path $PbiBin 'Microsoft.PowerBI.AdomdClient.dll'

function Import-Adomd {
    if (-not (Test-Path $AdomdDll)) { throw "AdomdClient nao encontrada em $AdomdDll" }
    Add-Type -Path $AdomdDll
}

# Lista as instancias do Desktop abertas: porta, PID e o titulo da janela (nome do arquivo).
# A porta muda a cada abertura e fica em msmdsrv.port.txt (UTF-16) na pasta de trabalho.
function Get-PbiInstancias {
    $bases = @(
        "$env:LOCALAPPDATA\Microsoft\Power BI Desktop\AnalysisServicesWorkspaces",
        "$env:USERPROFILE\Microsoft\Power BI Desktop Store App\AnalysisServicesWorkspaces"
    ) | Where-Object { Test-Path $_ }
    $procs = @{}
    Get-CimInstance Win32_Process -Filter "Name='msmdsrv.exe'" | ForEach-Object { $procs[[int]$_.ProcessId] = [int]$_.ParentProcessId }
    foreach ($b in $bases) {
        Get-ChildItem $b -Recurse -Filter msmdsrv.port.txt -ErrorAction SilentlyContinue | ForEach-Object {
            $porta = [int]((Get-Content $_.FullName -Encoding Unicode -Raw).Trim())
            $conexao = Get-NetTCPConnection -LocalPort $porta -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
            if (-not $conexao) { return }  # pasta de sessao antiga, Desktop ja fechado
            $pidSrv = [int]$conexao.OwningProcess
            $titulo = ''
            if ($procs.ContainsKey($pidSrv)) {
                $pai = Get-Process -Id $procs[$pidSrv] -ErrorAction SilentlyContinue
                if ($pai) { $titulo = $pai.MainWindowTitle }
            }
            [pscustomobject]@{ Porta = $porta; Pid = $pidSrv; Titulo = $titulo }
        }
    }
}

# Resolve a porta: a informada, ou a unica instancia aberta. Com mais de uma, para e lista.
function Resolve-PbiPorta([int]$Port) {
    if ($Port) { return $Port }
    $inst = @(Get-PbiInstancias)
    if ($inst.Count -eq 1) { return $inst[0].Porta }
    if ($inst.Count -eq 0) { throw 'Nenhum Power BI Desktop aberto nesta maquina.' }
    $lista = ($inst | ForEach-Object { "  porta $($_.Porta)  $($_.Titulo)" }) -join "`n"
    throw "Mais de um Desktop aberto. Informe -Port:`n$lista"
}

function Open-PbiConexao([int]$Port) {
    Import-Adomd
    $conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:$Port")
    $conn.Open()
    $conn
}

# Nome e id do banco. No Desktop existe um banco so, e o id costuma ser igual ao nome.
function Get-PbiBanco($conn) {
    $cmd = $conn.CreateCommand()
    $cmd.CommandText = 'SELECT [CATALOG_NAME] FROM $SYSTEM.DBSCHEMA_CATALOGS'
    $r = $cmd.ExecuteReader(); $null = $r.Read(); $nome = $r.GetString(0); $r.Close()
    $id = $nome
    try {
        $cmd.CommandText = 'SELECT [DATABASE_ID] FROM $SYSTEM.DBSCHEMA_CATALOGS'
        $r = $cmd.ExecuteReader(); $null = $r.Read(); $id = $r.GetString(0); $r.Close()
    } catch { }
    [pscustomobject]@{ Nome = $nome; Id = $id }
}

function Clear-PbiCache($conn, [string]$DatabaseId) {
    $c = $conn.CreateCommand()
    $c.CommandText = '<ClearCache xmlns="http://schemas.microsoft.com/analysisservices/2003/engine"><Object><DatabaseID>' + $DatabaseId + '</DatabaseID></Object></ClearCache>'
    $null = $c.ExecuteNonQuery()
}

# Executa DAX e devolve as linhas como objetos, com as colunas pelo nome sem colchetes.
function Invoke-PbiDax($conn, [string]$Dax) {
    $c = $conn.CreateCommand(); $c.CommandText = $Dax
    $r = $c.ExecuteReader()
    $nomes = 0..($r.FieldCount - 1) | ForEach-Object { $r.GetName($_).Trim('[', ']') -replace '^.*\[', '' }
    $linhas = New-Object System.Collections.Generic.List[object]
    while ($r.Read()) {
        $o = [ordered]@{}
        for ($i = 0; $i -lt $r.FieldCount; $i++) { $o[$nomes[$i]] = $r.GetValue($i) }
        $linhas.Add([pscustomobject]$o)
    }
    $r.Close()
    $linhas
}

# Cabecalho de toda medicao. Linha de base e remedicao so se comparam com a mesma versao.
function Get-MetaMedicao($conn, [int]$Port, [string]$Grandeza) {
    $exe = Join-Path $PbiBin 'PBIDesktop.exe'
    [ordered]@{
        grandeza        = $Grandeza
        data            = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
        maquina         = $env:COMPUTERNAME
        versao_desktop  = ((Get-Item $exe).VersionInfo.ProductVersion -split '\+')[0].Trim()
        versao_servidor = $conn.ServerVersion
        porta           = $Port
    }
}

function Save-Meta($meta, [string]$Pasta, [string]$Nome) {
    New-Item -ItemType Directory -Force $Pasta | Out-Null
    $meta | ConvertTo-Json -Depth 5 | Out-File (Join-Path $Pasta $Nome) -Encoding utf8
}

function Get-Mediana([double[]]$v) {
    if (-not $v -or $v.Count -eq 0) { return $null }
    $s = $v | Sort-Object
    $n = $s.Count
    if ($n % 2) { return [double]$s[($n - 1) / 2] }
    ([double]$s[$n / 2 - 1] + [double]$s[$n / 2]) / 2
}
