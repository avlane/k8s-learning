# 13 - Autoscaling

The HorizontalPodAutoscaler (HPA) changes a workload's replica count based on metrics. CPU and memory
metrics come from **metrics-server**, which is not installed by default (and not in kind).

Files: `deployment.yaml` (with a Service), `hpa.yaml`, `loadgen.yaml`

## Run it

    kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/download/v0.7.2/components.yaml
    kubectl -n kube-system patch deployment metrics-server --type=json \
      -p '[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]'   # kind only
    kubectl top nodes
    kubectl apply -f deployment.yaml -f hpa.yaml
    kubectl get hpa web-hpa --watch
    kubectl apply -f loadgen.yaml          # then watch the replicas climb

The `--kubelet-insecure-tls` patch is the workaround usually quoted for kind because the kubelet certificates are self-signed.

## What to observe

Expected (if everything worked): `TARGETS` shows `cpu: 0%/50%` when idle and rises
under load; `REPLICAS` grows towards 6, then shrinks back slowly after the load stops (the default
scale-down stabilization window is 5 minutes).

## Why this first version will not work

The Deployment has no CPU **request**. Utilization is a percentage of the request, so with none set the
HPA reports `<unknown>/50%` and events like `failed to get cpu utilization: missing request for cpu`.
Fixed in the next commit.
