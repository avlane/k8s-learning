# 00 - Setup

## Cluster options

Three ways to get a cluster locally:

  - **kind** (Kubernetes in Docker): `kind create cluster --config kind-config.yaml`
  - **minikube**: `minikube start`
  - the Kubernetes option in Docker Desktop

Both kind and Docker Desktop need a running Docker daemon.

## Plan

Create a cluster with `kind-config.yaml` (one control plane, one worker), check
`kubectl get nodes`, then work through the lessons in order.

Expected:

    $ kubectl get nodes
    NAME                     STATUS   ROLES           AGE   VERSION
    learning-control-plane   Ready    control-plane   1m    v1.32.0
    learning-worker          Ready    <none>          1m    v1.32.0

## kubectl cheat sheet

    kubectl get pods -o wide             # more columns, including the node and pod IP
    kubectl get pods --show-labels
    kubectl describe pod NAME            # events at the bottom are the most useful part
    kubectl logs NAME [-c CONTAINER] [--previous]
    kubectl exec -it NAME -- sh
    kubectl apply -f FILE                # create or update
    kubectl delete -f FILE
    kubectl explain pod.spec.containers  # field documentation (needs a cluster)
    kubectl run x --image=IMAGE --dry-run=client -o yaml   # generate YAML instead of typing it
    kubectl get events --sort-by=.lastTimestamp
    kubectl config get-contexts          # which cluster am I talking to?

## A namespace for the lessons

Everything so far lands in `default`. `namespace.yaml` creates a `learning` namespace with Pod Security
Admission labels:

- `enforce: baseline` rejects the clearly dangerous things (privileged containers, host namespaces, `hostPath` volumes).
- `warn` and `audit: restricted` do not block anything but print a warning when a Pod would not pass the stricter `restricted`
  profile (non-root, no privilege escalation, dropped capabilities, seccomp profile).

    kubectl apply -f namespace.yaml
    kubectl config set-context --current --namespace=learning
    kubectl apply -f ../01-pods/pod.yaml

Expected: Pods that follow the hardening in these lessons apply silently; the lessons that still run
the root nginx image should print a `would violate PodSecurity "restricted:latest"` warning that lists the failing fields.
The `broken/` examples are plain Pods and are not meant to be hardened. Some manifests (the kustomize overlays) set
their own namespaces, so check `kubectl config view --minify` before wondering where something went.
