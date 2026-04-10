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
The output I got is recorded at the bottom of this file.

Things I noticed:

- The `images:` transformer matches on the image *name* (`nginx`) and changes only the tag here.
- `namePrefix` also rewrites references (a Service name used by an Ingress, for example) when they are known fields.
- `namespace:` sets the namespace on every resource but does not create the Namespace object.

## Patches and generators

`overlays/prod/resources-patch.yaml` is a strategic merge patch: it names the Deployment and the
container (`nginx`) so that the lists merge by name instead of replacing the whole container list.
The `configMapGenerator` creates `web-config-<hash>`; if the content changes, the hash and
so the name changes, and anything referencing it rolls out again (which fixes the "ConfigMap
changed but Pods did not restart" problem from lesson 04).

Mistake to avoid: a patch whose `metadata.name` does not match a resource in the base fails with
`no matches for Id ...`, and a patch container name that does not match adds a **second** container.

## Rendered output

<!-- rendered:start -->
Captured on this machine with the client-side kubectl v1.34.1 (built-in Kustomize v5.7.1); no cluster was involved.

```
$ kubectl kustomize overlays/dev
apiVersion: v1
kind: Service
metadata:
  labels:
    app.kubernetes.io/part-of: k8s-learning
  name: dev-web
  namespace: dev
spec:
  ports:
  - port: 80
    targetPort: 80
  selector:
    app: web
---
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: web
    app.kubernetes.io/part-of: k8s-learning
  name: dev-web
  namespace: dev
spec:
  replicas: 1
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - image: nginx:1.27.4
        name: nginx
        ports:
        - containerPort: 80

$ kubectl kustomize overlays/prod
apiVersion: v1
data:
  APP_MODE: production
kind: ConfigMap
metadata:
  name: web-config-c97tt9cdc2
  namespace: prod
---
apiVersion: v1
kind: Service
metadata:
  labels:
    app.kubernetes.io/part-of: k8s-learning
  name: web
  namespace: prod
spec:
  ports:
  - port: 80
    targetPort: 80
  selector:
    app: web
---
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: web
    app.kubernetes.io/part-of: k8s-learning
  name: web
  namespace: prod
spec:
  replicas: 4
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - image: nginx:1.27.5
        name: nginx
        ports:
        - containerPort: 80
        resources:
          limits:
            cpu: 500m
            memory: 256Mi
          requests:
            cpu: 100m
            memory: 128Mi
```
<!-- rendered:end -->
