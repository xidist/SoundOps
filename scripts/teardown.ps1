param(
    [switch]$DeleteNamespace
)

helm uninstall soundops --namespace soundops

if ($DeleteNamespace) {
    minikube kubectl -- delete namespace soundops
}

Write-Host "Minikube is still running. Use 'minikube stop' when finished."
