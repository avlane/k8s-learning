# 05 - Probes and resources

Probes tell Kubernetes whether a container is alive and whether it can take
traffic. Requests and limits tell the scheduler and the kubelet how much CPU and
memory a container needs and may use.

Files: `deployment-probes.yaml`

## Probes

- **readinessProbe**: failing means the Pod is removed from Service endpoints. The container keeps running.
- **livenessProbe**: failing means the kubelet restarts the container.
- **startupProbe**: holds off the other two until the app has started (for slow starters).

## Run it

    kubectl apply -f deployment-probes.yaml
    kubectl get pods -l app=probes-demo --watch
    kubectl describe pod -l app=probes-demo

## What to observe

Expected: the Pods become Ready after a few seconds, then
`RESTARTS` starts climbing about every 30 seconds. `describe` shows events like
`Liveness probe failed: HTTP probe failed with statuscode: 404` followed by
`Container nginx failed liveness probe, will be restarted`.

The stock nginx image has no `/healthz` route, so the liveness probe gets a 404 and 4xx is a failure.
(Any status from 200 to 399 passes.) The first version of this manifest had that bug. The liveness path is now `/`.

## Requests and limits

- **requests** are what the scheduler reserves when placing the Pod. A Pod whose requests do not fit on any node stays `Pending`.
- **limits** are enforced at runtime. Over the CPU limit the container is throttled. Over the memory limit it is killed (`OOMKilled`, exit code 137).
- `50m` is 50 millicores (5% of a core). `64Mi` is mebibytes (`64M` would be megabytes, a small but real difference).

QoS class, shown in `kubectl describe pod`:

| class | when |
|---|---|
| Guaranteed | every container has requests equal to limits for both CPU and memory |
| Burstable | at least one request or limit is set, but not Guaranteed |
| BestEffort | nothing set; first to be evicted under node pressure |

The Deployment here is Burstable.
