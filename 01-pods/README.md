# 01 - Pods

A Pod is one or more containers that share a network namespace and volumes. You
rarely create bare Pods in real life (a Deployment does it for you), but they are
the smallest unit to learn on.

Files: `pod.yaml`

## Run it

    kubectl apply -f pod.yaml
    kubectl get pods
    kubectl get pods -o wide
    kubectl describe pod hello-nginx
    kubectl logs hello-nginx
    kubectl port-forward pod/hello-nginx 8080:80      # then, in another terminal: curl -i localhost:8080
    kubectl exec -it hello-nginx -- sh
    kubectl delete -f pod.yaml

## What to observe

Expected:

    $ kubectl apply -f pod.yaml
    pod/hello-nginx created

    $ kubectl get pods
    NAME          READY   STATUS    RESTARTS   AGE
    hello-nginx   1/1     Running   0          20s

- `describe` lists the events: Scheduled, Pulling, Pulled, Created, Started.
- `READY 1/1` means 1 of 1 containers is ready.
- Deleting a bare Pod is final. Nothing recreates it.
- `curl` through the port-forward should return the nginx welcome page with `HTTP/1.1 200 OK`.

## Naive bits to fix later

- No resource requests or limits.
- No `securityContext`, so nginx runs as root.
- It lives in the `default` namespace.
