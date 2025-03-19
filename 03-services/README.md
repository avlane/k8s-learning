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
- `port` is what clients use on the Service, `targetPort` is the port the container listens on.
