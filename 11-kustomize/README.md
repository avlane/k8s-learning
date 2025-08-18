# 11 - Kustomize

Kustomize customizes plain YAML without templates: a **base** plus **overlays** that
patch it. It is built into kubectl (`kubectl kustomize DIR` renders, `kubectl apply -k DIR` applies).

Files: `base/`, `overlays/dev/`, `overlays/prod/`

## Run it

    kubectl kustomize base
    kubectl kustomize overlays/dev
    kubectl kustomize overlays/prod
    kubectl create namespace dev && kubectl apply -k overlays/dev
    kubectl get all -n dev

## What to observe

`kubectl kustomize` only renders, so it works without a cluster, and I have run it on these directories.
`overlays/dev` should output the Service and Deployment named `dev-web` in namespace `dev` with 1 replica, and
`overlays/prod` the same names unprefixed in namespace `prod` with 4 replicas and `nginx:1.27.5`.
Things I noticed:

- The `images:` transformer matches on the image *name* (`nginx`) and changes only the tag here.
- `namePrefix` also rewrites references (a Service name used by an Ingress, for example) when they are known fields.
- `namespace:` sets the namespace on every resource but does not create the Namespace object.
