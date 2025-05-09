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
(Any status from 200 to 399 passes.) This manifest has that bug in on purpose; the fix is in the next commit.
