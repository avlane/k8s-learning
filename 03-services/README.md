# 03 - Services

Pods come and go and get new IPs. A Service gives a set of Pods one stable
virtual IP and DNS name, and load-balances across the Pods that match its
selector and are Ready.

Files: `service-clusterip.yaml`. It fronts the Deployment from lesson 02, so apply that first.

## Run it

    kubectl apply -f ../02-deployments/deployment.yaml
    kubectl apply -f service-clusterip.yaml
    kubectl get service web
    kubectl get endpointslices -l kubernetes.io/service-name=web
    kubectl port-forward service/web 8080:80       # curl localhost:8080
    kubectl run tmp --rm -it --image=busybox:1.37.0 --restart=Never -- wget -qO- http://web

## What to observe

Expected:

    $ kubectl get service web
    NAME   TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)   AGE
    web    ClusterIP   10.96.x.x      <none>        80/TCP    5s

- The EndpointSlice should list the three Pod IPs.
- Inside the cluster `web` resolves from the same namespace, and `web.default.svc.cluster.local` resolves from anywhere.
- `port` is what clients use on the Service, `targetPort` is the port the container listens on. The Services here use `targetPort: http`, the *name* of the container port (8080 since lesson 02 switched to the unprivileged nginx image), which is the more robust form.

## Other Service types

- `service-nodeport.yaml`: also opens port 30080 (the NodePort range is 30000-32767 by default) on every node. With kind the node is a container, so reaching it from the host needs `extraPortMappings` in the kind config. `port-forward` is easier.
- `service-headless.yaml`: `clusterIP: None` gives no virtual IP. DNS returns the Pod IPs directly (one A record per ready Pod). StatefulSets use this for stable per-Pod names (lesson 06).
- `type: LoadBalancer` needs a cloud provider or something like MetalLB. On a local cluster the EXTERNAL-IP stays `<pending>`.

Expected: `nslookup web-headless` from the toolbox returns three addresses,
while `nslookup web` returns the single ClusterIP.

## Mistakes and fixes

### Selector matches nothing

`broken/wrong-selector.yaml`: the Service is created without complaint, but

    kubectl get endpointslices -l kubernetes.io/service-name=web-wrong-selector
    kubectl describe service web-wrong-selector

Expected: the EndpointSlice has no endpoints and `describe` shows
`Endpoints: <none>`. Requests to the Service hang or are refused. Compare the
Service selector with `kubectl get pods --show-labels`. This is the most common Service bug.

### Right Pods, wrong targetPort

`broken/wrong-targetport.yaml`: endpoints exist (the Pods match) but they point at port 9090.

Expected: `kubectl get endpointslices` lists the Pod IPs with port 9090,
and `wget http://web-wrong-port` fails with "connection refused", since nothing listens on 9090.
Fix `targetPort` to the container's real port, or give the container port a name and
use the name in `targetPort` so that only the Pod spec needs to change.

### A Pod that is not Ready is not an endpoint

If the readiness probe fails (lesson 05) the Pod is removed from the EndpointSlice
but keeps running. A Service with zero ready Pods behaves like the no-selector case.
### Forgetting a Service after changing the container port

When lesson 02 moved nginx from port 80 to 8080, these Services kept `targetPort: 80` for a while and would have
shown healthy endpoints that refuse connections. Using the port name avoids that class of bug.
