$content = Get-Content "$env:USERPROFILE\.aws\credentials"
$content | Where-Object { $_ -match "environment\s*=" } | ForEach-Object { ($_ -split "=")[1].Trim() }