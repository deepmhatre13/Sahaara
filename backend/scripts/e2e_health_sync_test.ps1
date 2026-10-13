# End-to-end test for the health-data sync path that was 500-ing.
# Creates a user, then calls the exact endpoint that raised NameError.
$ErrorActionPreference = 'Stop'
$base = 'http://127.0.0.1:8001/api'
$stamp = Get-Date -Format 'HHmmss'
$email = "hsync$stamp@example.com"

Write-Host "=== 1) create user ($email) ==="
$body = @{ full_name = 'Health Sync Test'; email = $email; password = 'password123' } | ConvertTo-Json
$su = Invoke-RestMethod -Uri "$base/auth/signup" -Method POST -ContentType 'application/json' -Body $body -TimeoutSec 25
$uid = $su.user.id
$hdr = @{ Authorization = "Bearer $($su.access_token)" }
Write-Host "  user_id=$uid"

Write-Host "`n=== 2) POST /health-data/$uid/sync  (was: NameError -> 500) ==="
$sync = Invoke-RestMethod -Uri "$base/health-data/$uid/sync" -Method POST -Headers $hdr -TimeoutSec 25
Write-Host "  SYNC OK -> created $($sync.Count) metrics"
foreach ($m in $sync) { Write-Host "     $($m.metric_type) = $($m.value) $($m.unit)  source=$($m.source)" }

Write-Host "`n=== 3) verify source came from provider.name (not hardcoded) ==="
$bad = $sync | Where-Object { $_.source -ne 'mock' }
if ($bad) { Write-Host "  UNEXPECTED source values: $($bad.source)"; exit 1 }
Write-Host "  OK  all sources = 'mock' (from MockHealthDataProvider.name)"

Write-Host "`n=== 4) GET /health-data/$uid/summary ==="
$sum = Invoke-RestMethod -Uri "$base/health-data/$uid/summary" -Headers $hdr -TimeoutSec 25
Write-Host "  hr=$($sum.heart_rate) steps=$($sum.steps) sleep=$($sum.sleep_minutes) spo2=$($sum.spo2)"

Write-Host "`n=== 5) GET /health-data/$uid/metrics?metric_type=heart_rate ==="
$met = Invoke-RestMethod -Uri "$base/health-data/$uid/metrics?metric_type=heart_rate" -Headers $hdr -TimeoutSec 25
Write-Host "  returned $($met.Count) heart_rate metric(s)"

Write-Host "`nHEALTH-DATA SYNC E2E PASSED"
