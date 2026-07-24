# Security

## Current controls

- Runs as a non-root user with a fixed UID/GID.
- Drops all Linux capabilities.
- Disables privilege escalation.
- Uses the runtime-default seccomp profile.
- Uses a read-only root filesystem with writable `emptyDir` mounts only for
  temporary data and the Hugging Face cache.
- Disables automatic service-account token mounting.
- Applies resource requests, limits, ResourceQuota, LimitRange, and ingress
  NetworkPolicy.
- Rejects unsupported content types, empty files, and oversized uploads.
- CI runs linting, unit tests, and a clean container build.

## Production hardening backlog

- Pin the model to an immutable Hugging Face revision.
- Generate and attest an SBOM.
- Scan dependencies and container images for vulnerabilities.
- Sign images and enforce admission policies.
- Add authentication, authorization, TLS, and rate limiting.
- Restrict egress after providing an internal or preloaded model artifact.
- Store images in a private registry and use managed workload identity.
