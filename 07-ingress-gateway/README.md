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

## Gateway API

The Gateway API is the newer, more expressive replacement for Ingress. Its pieces are
split by who owns them:

- **GatewayClass**: which implementation (controller) handles Gateways. Provided by the implementation.
- **Gateway**: a listener (port, protocol, hostnames). Owned by the platform side.
- **HTTPRoute**: routing rules attached to a Gateway with `parentRefs`. Owned by the app team.

It is not built into Kubernetes: the CRDs are installed separately, and so is an implementation.

    kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.3.0/standard-install.yaml
    kubectl get gatewayclass                         # pick a class and put its name into gateway.yaml
    kubectl apply -f gateway.yaml -f httproute.yaml
    kubectl get gateway,httproute
    kubectl describe httproute web                   # look at status.parents[].conditions

Expected: the Gateway reports `Programmed: True` and an address, and the
HTTPRoute reports `Accepted: True` and `ResolvedRefs: True` for its parent.
