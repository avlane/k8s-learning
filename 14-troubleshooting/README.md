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

## Scenarios (expected symptoms)

| file | expected status | where to see why |
|---|---|---|
| `pending-too-big.yaml` | `Pending` | `describe`: `0/2 nodes are available: ... Insufficient cpu` |
| `node-selector.yaml` | `Pending` | `describe`: `node(s) didn't match Pod's node affinity/selector` |
| `bad-configmap-key.yaml` | `CreateContainerConfigError` | `describe`: `couldn't find key absent in ConfigMap default/scenario-config` |
| `readiness-never.yaml` | `Running`, `0/1` | `describe`: `Readiness probe failed: HTTP probe failed with statuscode: 404` |
| `wrong-command.yaml` | `StartError` / `RunContainerError` | `describe`: `exec: "/usr/bin/does-not-exist": no such file or directory` |

Lessons 01 to 06 have more (ImagePullBackOff, CrashLoopBackOff, OOMKilled, Pending PVC).
Apply one at a time with `kubectl apply -f scenarios/NAME.yaml`, work out the cause from
`describe` and `logs` alone, then clean up with `kubectl delete -f`.

## Debugging a container with no shell

Minimal images (distroless, scratch-based) have no `sh`, so `kubectl exec -it ... -- sh` fails with
`executable file not found`. An **ephemeral container** attaches a debug image to the running Pod:

    kubectl debug -it POD --image=busybox:1.37.0 --target=CONTAINER
    # inside: ps, ls /proc/1/root/ (the target's filesystem when process namespaces are shared), wget, nslookup
    kubectl debug POD -it --copy-to=POD-debug --container=app --image=busybox:1.37.0 -- sh   # debug a copy, change the command

Ephemeral containers cannot be removed from a Pod once added, and `--target` only shares the process
namespace if the container runtime supports it. `kubectl debug node/NODE -it --image=busybox:1.37.0` starts a
Pod on a node with the host filesystem mounted at `/host`.

## Node problems

    kubectl get nodes
    kubectl describe node NODE            # Conditions: Ready, MemoryPressure, DiskPressure, PIDPressure
    kubectl cordon NODE                   # stop new Pods landing there
    kubectl drain NODE --ignore-daemonsets --delete-emptydir-data
    kubectl uncordon NODE

`NotReady` nodes usually mean the kubelet or the container runtime is down. Pods on them show `Terminating`
or `Unknown` for a while (the default toleration window is 5 minutes) before they are rescheduled. On kind a node is a
Docker container, so `docker restart learning-worker` is the equivalent of a reboot.

## Permission, DNS and network symptoms

- **`Error from server (Forbidden): ... cannot list resource "pods" in API group "" in the namespace "x"`**: the message
  names the subject, verb, resource and namespace. Test with `kubectl auth can-i VERB RESOURCE --as=SUBJECT -n NS`
  (lesson 08), then grant exactly that.
- **`bad address 'web'` / `could not resolve host`**: DNS. From a throwaway Pod, `nslookup kubernetes.default`. If that
  fails look at CoreDNS: `kubectl -n kube-system get pods -l k8s-app=kube-dns` and its logs. An egress NetworkPolicy without a DNS rule produces the same symptom (lesson 09).
- **Timeout versus refused**: a NetworkPolicy drop looks like a *timeout*; nothing listening on the port looks like *connection refused*.
- **Works by Pod IP, fails by Service name**: DNS or Service selector. **Works by Service name from one namespace but not another**: use the full `web.NAMESPACE.svc.cluster.local`.
- **Works in `port-forward` but not through the Ingress**: look at the Ingress class, host header and the Service port (lesson 07).
