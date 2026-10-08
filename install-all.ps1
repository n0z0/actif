[CmdletBinding()]
param (
    [switch]$FromSource = $false
)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " ACTIF Ecosystem - Master Installer (5 Deception Daemons)" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$root = $PSScriptRoot
$apps = @("cachedb", "synwatcher", "scp", "lemes", "ClassRoot")

if ($FromSource) {
    Write-Host "[*] Memasang kelima aplikasi dari Source Code lokal (go build)..." -ForegroundColor Yellow
    $binDir = "$env:LOCALAPPDATA\Programs\actif\bin"
    if (-not (Test-Path $binDir)) {
        New-Item -ItemType Directory -Path $binDir -Force | Out-Null
    }

    foreach ($app in $apps) {
        $appPath = Join-Path $root $app
        if (Test-Path $appPath) {
            Write-Host "[*] Mengompilasi $app..." -ForegroundColor Cyan
            $outputExe = Join-Path $binDir "$($app.ToLower()).exe"
            # Khusus scp dan classroot
            if ($app -eq "ClassRoot") {
                $outputExe = Join-Path $binDir "classroot.exe"
            }
            try {
                $p = Start-Process -FilePath "go" -ArgumentList "build", "-o", $outputExe, "." -WorkingDirectory $appPath -NoNewWindow -Wait -PassThru
                if ($p.ExitCode -eq 0) {
                    Write-Host "    [OK] $app berhasil dikompilasi -> $outputExe" -ForegroundColor Green
                } else {
                    Write-Host "    [FAIL] Gagal mengompilasi $app (ExitCode $($p.ExitCode))" -ForegroundColor Red
                }
            } catch {
                Write-Host "    [FAIL] Error: $_" -ForegroundColor Red
            }
        }
    }

    # Tambahkan $binDir ke PATH jika belum ada
    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
    if ($userPath -notlike "*$binDir*") {
        $updatedPath = $userPath.TrimEnd(';') + ';' + $binDir
        [Environment]::SetEnvironmentVariable("Path", $updatedPath, "User")
        $env:Path = "$env:Path;$binDir"
        Write-Host "[OK] Direktori $binDir berhasil didaftarkan ke User PATH!" -ForegroundColor Green
    }
} else {
    Write-Host "[*] Menjalankan script installer bawaan masing-masing aplikasi..." -ForegroundColor Yellow
    foreach ($app in $apps) {
        $installer = Join-Path (Join-Path $root $app) "install.ps1"
        if (Test-Path $installer) {
            Write-Host "`n---> Menjalankan $app installer..." -ForegroundColor Cyan
            try {
                & $installer
            } catch {
                Write-Host "    Peringatan: Gagal unduh binary rilis $app, mencoba kompilasi lokal..." -ForegroundColor Yellow
                $appPath = Join-Path $root $app
                $outputExe = "$env:LOCALAPPDATA\Programs\$($app.ToLower())\$($app.ToLower()).exe"
                $outDir = Split-Path $outputExe
                if (-not (Test-Path $outDir)) { New-Item -ItemType Directory -Path $outDir -Force | Out-Null }
                Start-Process -FilePath "go" -ArgumentList "build", "-o", $outputExe, "." -WorkingDirectory $appPath -NoNewWindow -Wait
                $env:Path = "$env:Path;$outDir"
            }
        }
    }
}

Write-Host "`n==========================================================" -ForegroundColor Green
Write-Host " [SUKSES] Seluruh 5 Daemon Deception Kini Portabel & Global!" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "Anda dapat langsung memanggilnya dari terminal/PowerShell mana pun:"
Write-Host "   1. cachedb -port 50051 -ttl 36000" -ForegroundColor Yellow
Write-Host "   2. synwatcher -logfile synwatcher_cti.jsonl" -ForegroundColor Yellow
Write-Host "   3. scp" -ForegroundColor Yellow
Write-Host "   4. lemes -port :50505 -ctilog lemes_cti.jsonl" -ForegroundColor Yellow
Write-Host "   5. classroot" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Green
