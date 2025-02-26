# 02 - Deployments

A Deployment manages a ReplicaSet, which manages the Pods. You declare the
desired state (3 replicas of this Pod template) and the controllers keep
reconciling towards it.

Files: `deployment.yaml`

## Run it

    kubectl apply -f deployment.yaml
    kubectl get deployment,replicaset,pods -l app=web
    kubectl delete pod -l app=web --wait=false      # watch them come back
    kubectl scale deployment web --replicas=5
    kubectl set image deployment/web nginx=nginx:1.27.5
    kubectl rollout status deployment/web
    kubectl rollout history deployment/web
    kubectl rollout undo deployment/web

## What to observe

Expected:

    $ kubectl get deployment web
    NAME   READY   UP-TO-DATE   AVAILABLE   AGE
    web    3/3     3            3           30s

- Pod names look like `web-<replicaset-hash>-<random>`. The hash changes when the Pod template changes.
- After `set image` there are two ReplicaSets: the new one scales up while the old one scales down. The old one stays at 0 replicas so that `rollout undo` can use it.
- Scaling does not change the template, so it does not create a new ReplicaSet.
- The change cause column in `rollout history` is empty unless you set the `kubernetes.io/change-cause` annotation.

## Naive bits to fix later

- No resource requests or limits, no probes, no securityContext.
- The image tag is pinned but is bumped by hand.
