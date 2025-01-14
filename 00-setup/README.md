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
