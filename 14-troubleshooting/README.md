# 14 - Troubleshooting

A rough order of operations I want to follow instead of guessing.

## 1. What state is it in?

    kubectl get pods -o wide
    kubectl describe pod NAME                       # read the Events at the bottom first
    kubectl get events --sort-by=.lastTimestamp
    kubectl logs NAME [-c CONTAINER] [--previous]

| Status | Usually means | Look at |
|---|---|---|
| `Pending` | not scheduled yet | `describe` events: `Insufficient cpu/memory`, taints, `nodeSelector`, unbound PVC |
| `ContainerCreating` (long) | volume mount or image pull is slow or stuck | `describe`: `FailedMount`, pull events |
| `ErrImagePull` / `ImagePullBackOff` | image name/tag wrong, private registry, no network | image string, `imagePullSecrets` |
| `CrashLoopBackOff` | the container starts and exits | `logs --previous`, exit code |
| `CreateContainerConfigError` | missing ConfigMap/Secret/key | `describe` event names the object |
| `OOMKilled` (exit 137) | memory limit too low or leak | limits, `kubectl top` |
| `Running` but `0/1` | readiness probe failing | probe path/port, `describe` |
| `Running` but restarting | liveness probe failing or app crashing | `describe`, `logs --previous` |
| `Terminating` (stuck) | finalizer or a node that went away | `kubectl get pod -o yaml` finalizers |

## 2. Is the Service sending traffic to it?

    kubectl get service NAME -o wide
    kubectl get endpointslices -l kubernetes.io/service-name=NAME
    kubectl get pods --show-labels                     # compare with the Service selector
    kubectl run tmp --rm -it --image=busybox:1.37.0 --restart=Never -- wget -qO- --timeout=3 http://NAME

No endpoints means the selector matches nothing or no matching Pod is Ready. Endpoints but no
connection usually means `targetPort` is wrong.

## 3. Get a shell next to the problem

    kubectl exec -it POD -- sh
    kubectl debug -it POD --image=busybox:1.37.0 --target=CONTAINER     # ephemeral container for images with no shell
    kubectl port-forward POD 8080:80

## Habits

- Read `describe` events before `logs`; many failures never reach a running container.
- Change one thing at a time, and diff what is applied: `kubectl diff -f FILE`.
- Check `kubectl config current-context` before deleting anything.

The `scenarios/` folder has manifests that fail on purpose, one per symptom in the table. Next commit.
