<#
.SYNOPSIS
Detecta archivos huérfanos sin extensión válida en raíz del repo (potencialmente
creados por bugs de heredoc PowerShell durante commits).

.DESCRIPTION
Ejecuta antes de cada commit. Whitelist archivos legítimos conocidos sin extensión.
Cualquier otro archivo sin extensión .xxx en raíz del repo = sospechoso.

Bug histórico: 2026-05-08 SPR-009 F-C-3e (ver docs/WORKFLOW.md sección
"Commits con messages multi-línea").

.EXAMPLE
.\scripts\maintenance\check_orphan_files.ps1

# Output verde si limpio. Output rojo + exit 1 si detecta huérfanos.
#>

param(
    [string]$RepoPath = "F:\Noobs\RPG_Survival"
)

# Whitelist: archivos legítimos sin extensión esperados en raíz del repo.
# Añadir aquí cualquier dotfile o archivo especial que sea legítimo.
$Whitelist = @(
    '.dailylog_user',
    '.gitignore',
    '.gitattributes',
    'LICENSE',
    'README',
    'RPG_Survival.code-workspace'
)

# Buscar archivos sin extensión .xxx (regex: nombre NO termina en .alphanumeric)
# que tampoco están en whitelist.
$orphans = Get-ChildItem -Path $RepoPath -File -Force -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -notmatch '\.[a-zA-Z0-9]+$' } |
    Where-Object { $Whitelist -notcontains $_.Name }

if ($orphans) {
    Write-Host ""
    Write-Host "❌ ORPHAN FILES DETECTED in working dir:" -ForegroundColor Red
    Write-Host ""
    foreach ($file in $orphans) {
        Write-Host "  $($file.Name)" -ForegroundColor Yellow
        Write-Host "    Size: $($file.Length) bytes" -ForegroundColor DarkYellow
        Write-Host "    Modified: $($file.LastWriteTime)" -ForegroundColor DarkYellow
    }
    Write-Host ""
    Write-Host "Probable cause: heredoc PowerShell bug during recent commit." -ForegroundColor Cyan
    Write-Host "See docs/WORKFLOW.md section 'Commits con messages multi-linea'." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Cleanup commands:" -ForegroundColor Cyan
    Write-Host "  # Standard delete:" -ForegroundColor Gray
    Write-Host "  Get-ChildItem -Path '$RepoPath' -File -Force | Where-Object { `$_.Name -in @('<name1>','<name2>') } | ForEach-Object { Remove-Item -LiteralPath `$_.FullName -Force }" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  # If standard delete fails (trailing dot, unicode chars):" -ForegroundColor Gray
    Write-Host "  Remove-Item -LiteralPath '\\?\$RepoPath\<filename>' -Force" -ForegroundColor Gray
    Write-Host ""
    Write-Host "BLOCK COMMIT until working dir is clean." -ForegroundColor Red
    exit 1
} else {
    Write-Host "✅ Working dir clean. No orphan files detected." -ForegroundColor Green
    exit 0
}
