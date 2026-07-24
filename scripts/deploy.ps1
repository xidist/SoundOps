param(
    [string]$ImageTag = "0.1.0"
)

$ErrorActionPreference = "Stop"

Write-Host "Checking Minikube..."
minikube status *> $null
if ($LASTEXITCODE -ne 0) {
    minikube start --driver=docker --cpus=4 --memory=6144
}

Write-Host "Building soundops:$ImageTag..."
docker build --build-arg "APP_VERSION=$ImageTag" -t "soundops:$ImageTag" .

Write-Host "Loading image into Minikube..."
minikube image load "soundops:$ImageTag"

Write-Host "Deploying with Helm..."
helm upgrade --install soundops .\helm\soundops `
    --namespace soundops `
    --create-namespace `
    --set "image.tag=$ImageTag" `
    --wait `
    --timeout 15m

minikube kubectl -- get deployments,pods,services -n soundops
Write-Host ""
Write-Host "Run .\scripts\port-forward.ps1, then open http://127.0.0.1:8000"
