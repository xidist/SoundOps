# Three-minute interview demo

## 1. Explain the goal

> I built SoundOps to reinforce the Linux Foundation Kubernetes material with
> a real inference workload. It accepts an audio file, runs a pretrained
> Hugging Face classifier, and exposes operational endpoints and metrics.

## 2. Show the running objects

```powershell
.\scripts\status.ps1
```

Point out:

- Dedicated `soundops` namespace
- Deployment, ReplicaSet, pod, and stable Service
- Resource requests and limits
- Namespace ResourceQuota and LimitRange
- NetworkPolicy
- Startup, readiness, and liveness probes
- Non-root container with dropped Linux capabilities

## 3. Show the browser

```powershell
.\scripts\port-forward.ps1
```

Open `http://127.0.0.1:8000`, upload a short audio clip, and display the
predictions.

## 4. Show observability

Open:

- `http://127.0.0.1:8000/readyz`
- `http://127.0.0.1:8000/metrics`
- `http://127.0.0.1:8000/docs`

## 5. Explain reconciliation

Scale to two replicas, then back to one:

```powershell
minikube kubectl -- scale deployment soundops-soundops -n soundops --replicas=2
minikube kubectl -- get pods -n soundops -w
minikube kubectl -- scale deployment soundops-soundops -n soundops --replicas=1
```

## 6. Close honestly

> This is a local learning project rather than production AKS or EKS
> experience. It helped me practice the same core objects and operational
> reasoning: repeatable deployment, desired-state reconciliation, health
> gating, resource governance, network isolation, and troubleshooting.
