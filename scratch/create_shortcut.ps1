$desktop = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::Desktop)
$shortcutPath = Join-Path $desktop "SnapSum.lnk"

$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($shortcutPath)
$Shortcut.TargetPath = "c:\Users\ibrah\Documents\GitHub\SnapSum\run_snapsum.bat"
$Shortcut.WorkingDirectory = "c:\Users\ibrah\Documents\GitHub\SnapSum"
$Shortcut.Description = "SnapSum - Intelligent Document Summarizer"
$Shortcut.IconLocation = "imageres.dll, 98" # Premium document/reading icon
$Shortcut.Save()

Write-Host "Shortcut created successfully at: $shortcutPath"
