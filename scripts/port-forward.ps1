$ErrorActionPreference = "Stop"
Write-Host "Keep this window open. Press Ctrl+C to stop the tunnel."
minikube kubectl -- port-forward -n soundops service/soundops-soundops 8000:80
