# Architecture

```mermaid
flowchart LR
    U[Browser or curl] -->|multipart audio| S[Kubernetes Service]
    S --> P[SoundOps Pod]
    P --> A[FastAPI]
    A --> M[Hugging Face AST model]
    A --> X[/metrics]
    K[Kubernetes probes] -->|healthz / readyz| A
    PR[Prometheus] -. scrape .-> X
    G[Grafana] -. query .-> PR
    CI[GitHub Actions] -->|lint, test, build| IMG[Container image]
    H[Helm] -->|desired state| K8S[Minikube / Kubernetes]
    IMG --> K8S
```

## Control flow

1. The container starts as an unprivileged Linux user.
2. FastAPI becomes live and begins loading the Hugging Face model.
3. `/healthz` reports process health.
4. `/readyz` remains `503` until model loading completes.
5. The Kubernetes Service sends traffic only to ready pods.
6. `/metrics` exposes request, upload-size, readiness, and latency metrics.
7. Helm owns the Deployment, Service, quota, limits, and network policy.

## Deliberate trade-offs

- **Local cluster, not AKS/EKS:** demonstrates Kubernetes primitives without
  pretending Minikube equals operating a managed production cluster.
- **Runtime model download:** keeps the source repository and CI image build
  simpler, but increases cold-start time. A production version would bake a
  pinned model revision into the image or use a persistent model cache.
- **Single service:** appropriate for a weekend MVP. Production could separate
  asynchronous ingestion, inference workers, and result storage.
- **CPU inference:** portable and inexpensive for a demo. Production sizing
  would be based on measured throughput, latency, and accelerator availability.
