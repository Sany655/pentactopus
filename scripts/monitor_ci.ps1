param(
    [string]$Tag = "v2.7.0",
    [int]$MaxMinutes = 30
)

# Dynamically retrieve GitHub credentials from git credential helper
$token = $null
try {
    $credOutput = cmd.exe /c "echo protocol=https&echo host=github.com&echo." | git credential fill 2>$null
    foreach ($line in $credOutput) {
        if ($line -like "password=*") {
            $token = $line.Substring(9).Trim()
            break
        }
    }
} catch {
    Write-Host "Warning: could not get git credential helper token"
}

$headers = @{
    "User-Agent" = "Pentactopus-Agent"
    "Accept"     = "application/vnd.github.v3+json"
}
if ($token) {
    $headers["Authorization"] = "Bearer $token"
    Write-Host "Authenticated with GitHub token."
} else {
    Write-Host "No GitHub token found, running unauthenticated."
}

Write-Host "=== Pentactopus CI Monitor for tag: $Tag ==="
$startTime = Get-Date
$runId = $null

# Step 1: Find the workflow run for this tag
while (-not $runId) {
    if (((Get-Date) - $startTime).TotalMinutes -ge 5) {
        Write-Host "Timed out waiting for workflow run to register on GitHub."
        exit 1
    }
    try {
        $res = Invoke-RestMethod -Uri "https://api.github.com/repos/Sany655/pentactopus/actions/runs?event=push" -Headers $headers
        $targetRun = $res.workflow_runs | Where-Object { $_.head_branch -eq $Tag } | Select-Object -First 1
        if ($targetRun) {
            $runId = $targetRun.id
            Write-Host "Found workflow run ID: $runId ($($targetRun.name))"
            Write-Host "URL: $($targetRun.html_url)"
            break
        }
    } catch {
        Write-Host "API check error: $_"
    }
    Start-Sleep -Seconds 10
}

# Step 2: Poll workflow run status until completion
while ($true) {
    $elapsed = [math]::Round(((Get-Date) - $startTime).TotalMinutes, 1)
    if ($elapsed -ge $MaxMinutes) {
        Write-Host "Workflow run exceeded max wait time ($MaxMinutes min)."
        exit 1
    }

    try {
        $run = Invoke-RestMethod -Uri "https://api.github.com/repos/Sany655/pentactopus/actions/runs/$runId" -Headers $headers
        $jobs = Invoke-RestMethod -Uri "https://api.github.com/repos/Sany655/pentactopus/actions/runs/$runId/jobs" -Headers $headers
        
        Write-Host "[$elapsed m] Status: $($run.status) | Conclusion: $($run.conclusion)"
        foreach ($j in $jobs.jobs) {
            Write-Host "  - Job: $($j.name) -> $($j.status) ($($j.conclusion))"
        }

        if ($run.status -eq "completed") {
            Write-Host "=== Workflow Completed with Conclusion: $($run.conclusion) ==="
            if ($run.conclusion -eq "success") {
                exit 0
            } else {
                exit 2
            }
        }
    } catch {
        Write-Host "Polling error: $_"
    }

    Start-Sleep -Seconds 25
}
