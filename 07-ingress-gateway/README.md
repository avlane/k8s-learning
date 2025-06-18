# 07 - Ingress and Gateway API

A Service of type ClusterIP is only reachable inside the cluster. An Ingress describes
HTTP routing (host and path to Service) from outside, but it is **only a description**:
nothing happens until an ingress controller is installed that watches Ingress objects.

Files: `ingress.yaml`. It routes to the `web` Service from lessons 02 and 03.

## Run it (ingress-nginx on kind)

The kind config in `../00-setup/kind-config.yaml` labels the control-plane node
`ingress-ready=true` and maps host ports 80 and 443 to it, which is what the
ingress-nginx kind manifest expects.

    kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.12.1/deploy/static/provider/kind/deploy.yaml
    kubectl wait --namespace ingress-nginx --for=condition=ready pod --selector=app.kubernetes.io/component=controller --timeout=90s
    kubectl apply -f ../02-deployments/deployment.yaml -f ../03-services/service-clusterip.yaml
    kubectl apply -f ingress.yaml
    kubectl get ingress
    curl -i -H 'Host: web.example.test' http://localhost/

The controller version above is the one I picked from the project's release page; check its
compatibility table against your cluster version before using it.

## What to observe

Expected: the Ingress gets an ADDRESS (localhost or the node IP), and the
`curl` returns `HTTP/1.1 200 OK` with the nginx welcome page. Without the `Host` header
the controller's default backend answers `404`, which is how to tell routing from a broken controller.
