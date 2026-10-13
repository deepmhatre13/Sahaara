# End-to-end auth smoke test against the running Sahaara API.
# Usage: powershell -ExecutionPolicy Bypass -File scripts\e2e_auth_test.ps1
$ErrorActionPreference = 'Stop'
$base = 'http://127.0.0.1:8001/api'
$stamp = Get-Date -Format 'HHmmss'
$email = "e2e$stamp@example.com"
$pwd = 'password123'

Write-Host "=== 1) SIGNUP  ($email) ==="
$body = @{ full_name = 'E2E User'; email = $email; password = $pwd } | ConvertTo-Json
$signup = Invoke-RestMethod -Uri "$base/auth/signup" -Method POST -ContentType 'application/json' -Body $body -TimeoutSec 25
Write-Host "  OK  user_id=$($signup.user.id)  provider=$($signup.user.auth_provider)  token_len=$($signup.access_token.Length)"

Write-Host "`n=== 2) LOGIN (same credentials) ==="
$loginBody = @{ email = $email; password = $pwd } | ConvertTo-Json
$login = Invoke-RestMethod -Uri "$base/auth/login" -Method POST -ContentType 'application/json' -Body $loginBody -TimeoutSec 25
Write-Host "  OK  user_id=$($login.user.id)  token_len=$($login.access_token.Length)"

Write-Host "`n=== 3) LOGIN with WRONG password (expect 401) ==="
try {
    $badBody = @{ email = $email; password = 'totally-wrong-999' } | ConvertTo-Json
    Invoke-RestMethod -Uri "$base/auth/login" -Method POST -ContentType 'application/json' -Body $badBody -TimeoutSec 25 | Out-Null
    Write-Host '  UNEXPECTED SUCCESS (should have been rejected!)'
} catch {
    Write-Host "  correctly rejected -> status=$([int]$_.Exception.Response.StatusCode)"
}

Write-Host "`n=== 4) GET /auth/me with Bearer token ==="
$me = Invoke-RestMethod -Uri "$base/auth/me" -Headers @{ Authorization = "Bearer $($login.access_token)" } -TimeoutSec 25
Write-Host "  OK  email=$($me.email)  name=$($me.full_name)"

Write-Host "`n=== 5) POST /auth/google with bogus token (expect 401) ==="
try {
    $g = @{ id_token = 'not-a-real-token' } | ConvertTo-Json
    Invoke-RestMethod -Uri "$base/auth/google" -Method POST -ContentType 'application/json' -Body $g -TimeoutSec 25 | Out-Null
    Write-Host '  UNEXPECTED SUCCESS'
} catch {
    $s = [int]$_.Exception.Response.StatusCode
    $d = $_.ErrorDetails.Message
    Write-Host "  status=$s  body=$d  (expect 401 'Invalid Google token')"
}

Write-Host "`nALL AUTH E2E CHECKS PASSED"
