Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoOwner = "FranBarInstance"
$RepoName = "meneame-expandido"
$RepoSlug = "$RepoOwner/$RepoName"
$TagsApiUrl = "https://api.github.com/repos/$RepoSlug/tags?per_page=1"

function Say {
    param([string]$Message)
    Write-Host $Message
}

function Warn {
    param([string]$Message)
    Write-Warning $Message
}

function Die {
    param([string]$Message)
    throw $Message
}

function Prompt-Value {
    param(
        [string]$Message,
        [string]$Default = ""
    )

    if ([string]::IsNullOrWhiteSpace($Default)) {
        $value = Read-Host "$Message"
    } else {
        $value = Read-Host "$Message [$Default]"
    }

    if ([string]::IsNullOrWhiteSpace($value)) {
        return $Default
    }
    return $value
}

function Prompt-YesNo {
    param(
        [string]$Message,
        [bool]$DefaultYes = $true
    )

    $default = if ($DefaultYes) { "y" } else { "n" }
    $value = Prompt-Value "$Message (y/n)" $default
    switch -Regex ($value) {
        "^(y|yes)$" { return $true }
        "^(n|no)$" { return $false }
        default {
            Warn "Respuesta no válida, se usa '$default'."
            return $DefaultYes
        }
    }
}

function Get-LatestTag {
    $response = Invoke-RestMethod -Uri $TagsApiUrl -Method Get
    if (-not $response -or -not $response[0] -or -not $response[0].name) {
        Die "No se pudo resolver el último tag del repositorio."
    }
    return [string]$response[0].name
}

function Get-PythonCommand {
    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCmd) {
        return @($pythonCmd.Source)
    }

    $pyCmd = Get-Command py -ErrorAction SilentlyContinue
    if ($pyCmd) {
        return @($pyCmd.Source, "-3")
    }

    Die "No se encontró Python (python o py)."
}

function New-SecretKey {
    $bytes = New-Object byte[] 32
    [System.Security.Cryptography.RandomNumberGenerator]::Fill($bytes)
    return ([Convert]::ToHexString($bytes)).ToLowerInvariant()
}

function Get-EnvValue {
    param(
        [string]$FilePath,
        [string]$Key
    )
    $line = Select-String -Path $FilePath -Pattern "^$Key=(.*)$" | Select-Object -First 1
    if (-not $line) { return "" }
    return $line.Matches[0].Groups[1].Value
}

function Install-FromTag {
    param(
        [string]$Tag,
        [string]$TargetDir
    )

    $tmpDir = Join-Path ([System.IO.Path]::GetTempPath()) ("$RepoName-install-" + [guid]::NewGuid().ToString("N"))
    $archivePath = Join-Path $tmpDir "source.zip"
    $extractDir = Join-Path $tmpDir "extract"
    $archiveUrl = "https://github.com/$RepoSlug/archive/refs/tags/$Tag.zip"
    $extractedRoot = Join-Path $extractDir "$RepoName-$Tag"

    New-Item -ItemType Directory -Path $tmpDir -Force | Out-Null
    New-Item -ItemType Directory -Path $extractDir -Force | Out-Null
    New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null

    Say "Descargando $RepoSlug tag $Tag..."
    Invoke-WebRequest -Uri $archiveUrl -OutFile $archivePath
    Expand-Archive -Path $archivePath -DestinationPath $extractDir -Force

    if (-not (Test-Path -LiteralPath $extractedRoot)) {
        Die "No se encontró carpeta extraída esperada: $extractedRoot"
    }

    Get-ChildItem -LiteralPath $extractedRoot -Force | ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination $TargetDir -Recurse -Force
    }

    Remove-Item -LiteralPath $tmpDir -Recurse -Force
}

function New-WindowsLauncher {
    param(
        [string]$InstallDir,
        [string]$AppUrl
    )

    $launcherPath = Join-Path $InstallDir "bin\launch-expanse-windows.ps1"

    New-Item -ItemType Directory -Path (Join-Path $InstallDir "bin") -Force | Out-Null

    $launcherContent = @"
Set-StrictMode -Version Latest
`$ErrorActionPreference = "Stop"
`$InstallDir = "$InstallDir"
`$AppUrl = "$AppUrl"
`$venvPython = Join-Path `$InstallDir ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath `$venvPython)) {
    throw "No se encontró `$venvPython"
}
`$process = Start-Process -FilePath `$venvPython -ArgumentList "src/run.py" -WorkingDirectory `$InstallDir -PassThru
Start-Sleep -Seconds 2
Start-Process `$AppUrl | Out-Null
`$process | Wait-Process
"@
    Set-Content -LiteralPath $launcherPath -Value $launcherContent -Encoding UTF8

    Say "Lanzador creado: $launcherPath"
    return $launcherPath
}

function New-WindowsDesktopShortcut {
    param(
        [string]$InstallDir,
        [string]$LauncherPath
    )

    if (-not (Test-Path -LiteralPath $LauncherPath)) {
        Warn "No existe el lanzador para crear el acceso directo: $LauncherPath"
        return
    }

    $desktopDir = [Environment]::GetFolderPath("Desktop")
    $shortcutPath = Join-Path $desktopDir "Expanse.lnk"
    $iconPath = Join-Path $InstallDir "public\favicon.ico"

    $wsh = New-Object -ComObject WScript.Shell
    $shortcut = $wsh.CreateShortcut($shortcutPath)
    $shortcut.TargetPath = "powershell.exe"
    $shortcut.Arguments = "-ExecutionPolicy Bypass -File `"$LauncherPath`""
    $shortcut.WorkingDirectory = $InstallDir
    if (Test-Path -LiteralPath $iconPath) {
        $shortcut.IconLocation = $iconPath
    }
    $shortcut.Save()

    Say "Acceso directo: $shortcutPath"
}

try {
    $latestTag = Get-LatestTag
    Say "Último tag detectado: $latestTag"

    $cwd = (Get-Location).Path
    $useCurrent = Prompt-YesNo "¿Instalar en el directorio actual ($cwd)?" $false
    if ($useCurrent) {
        $installDir = $cwd
    } else {
        $installDir = Prompt-Value "Directorio de instalación" (Join-Path $cwd $RepoName)
    }

    if ([string]::IsNullOrWhiteSpace($installDir)) {
        Die "El directorio de instalación no puede estar vacío."
    }

    if (Test-Path -LiteralPath $installDir) {
        $hasContent = @(Get-ChildItem -LiteralPath $installDir -Force -ErrorAction SilentlyContinue).Count -gt 0
        if ($hasContent) {
            $continue = Prompt-YesNo "El directorio $installDir no está vacío. ¿Continuar y sobrescribir archivos?" $false
            if (-not $continue) {
                Die "Instalación cancelada por el usuario."
            }
        }
    }

    Install-FromTag -Tag $latestTag -TargetDir $installDir
    Say "Código instalado en: $installDir"

    $pythonCommand = Get-PythonCommand
    Say ("Python detectado: " + ($pythonCommand -join " "))

    Push-Location $installDir
    try {
        $pythonCmdArgs = @()
        if ($pythonCommand.Count -gt 1) {
            $pythonCmdArgs = @($pythonCommand | Select-Object -Skip 1)
        }
        & $pythonCommand[0] @pythonCmdArgs -m venv .venv

        $venvPython = Join-Path $installDir ".venv\Scripts\python.exe"
        if (-not (Test-Path -LiteralPath $venvPython)) {
            Die "No se encontró Python del entorno virtual: $venvPython"
        }

        & $venvPython -m pip install -r requirements.txt

        $envPath = Join-Path $installDir "config\.env"
        $envExamplePath = Join-Path $installDir "config\.env.example"
        if (-not (Test-Path -LiteralPath $envPath)) {
            Copy-Item -LiteralPath $envExamplePath -Destination $envPath -Force
        }

        $secretKey = New-SecretKey
        (Get-Content -LiteralPath $envPath) `
            -replace "^SECRET_KEY=.*$", "SECRET_KEY=$secretKey" `
            | Set-Content -LiteralPath $envPath -Encoding UTF8

        Say "Configuración base lista en config/.env"

        $userName = Prompt-Value "Nombre del usuario" "Admin"
        $userEmail = Prompt-Value "Email del usuario" "email@example.com"
        while ([string]::IsNullOrWhiteSpace($userEmail)) {
            Warn "El email no puede estar vacío."
            $userEmail = Prompt-Value "Email del usuario" "email@example.com"
        }

        $userPassword = Prompt-Value "Password del usuario" ""
        while ([string]::IsNullOrWhiteSpace($userPassword) -or $userPassword.Length -lt 9) {
            Warn "La contraseña debe tener al menos 9 caracteres."
            $userPassword = Prompt-Value "Password del usuario" ""
        }

        $userBirthdate = Prompt-Value "Fecha de nacimiento ISO (YYYY-MM-DD)" "1990-01-01"
        $userLocale = Prompt-Value "Locale del usuario" "es"
        $userRegion = Prompt-Value "Región del usuario (opcional)" ""

        & $venvPython "bin/create_user.py" `
            $userName `
            $userEmail `
            $userPassword `
            $userBirthdate `
            --locale $userLocale `
            --region $userRegion

        $appIp = Get-EnvValue -FilePath $envPath -Key "APP_BIND_IP"
        if ([string]::IsNullOrWhiteSpace($appIp)) { $appIp = "localhost" }
        $appPort = Get-EnvValue -FilePath $envPath -Key "APP_BIND_PORT"
        if ([string]::IsNullOrWhiteSpace($appPort)) { $appPort = "55000" }

        $appUrl = "http://$appIp`:$appPort"
        if (Prompt-YesNo "¿Quieres crear lanzador de aplicación?" $true) {
            $launcherPath = New-WindowsLauncher -InstallDir $installDir -AppUrl $appUrl
            if (Prompt-YesNo "¿Quieres crear icono en el escritorio?" $true) {
                New-WindowsDesktopShortcut -InstallDir $installDir -LauncherPath $launcherPath
            }
        }

        Say ""
        Say "Instalación completada."
        Say "Aplicación disponible en: $appUrl"
        Say "Directorio: $installDir"

        if (Prompt-YesNo "¿Quieres ejecutar la aplicación ahora?" $true) {
            Say "Ejecutando app en $appUrl ..."
            & $venvPython "src/run.py"
        } else {
            Say "Para arrancar después:"
            Say "cd `"$installDir`"; .\.venv\Scripts\python.exe src/run.py"
        }
    }
    finally {
        Pop-Location
    }
}
catch {
    Write-Error $_
    exit 1
}
