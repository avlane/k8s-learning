# 04 - ConfigMaps and Secrets

Configuration lives outside the image. A ConfigMap holds non-secret key/value
data; a Secret holds sensitive data. Both can be injected as environment
variables or mounted as files.

Files: `configmap.yaml`, `pod-config.yaml`

## Run it

    kubectl apply -f configmap.yaml
    kubectl apply -f pod-config.yaml
    kubectl exec config-demo -- env | grep -E 'APP_MODE|LOG_LEVEL'
    kubectl exec config-demo -- cat /usr/share/nginx/html/index.html
    kubectl port-forward pod/config-demo 8080:80      # curl localhost:8080

## What to observe

Expected: `APP_MODE=demo` and `LOG_LEVEL=info` appear in the environment,
and nginx serves the page from the ConfigMap.

- `envFrom` turns every key into an environment variable. Keys that are not valid
  variable names (like `index.html`) are skipped, with an event on the Pod.
- Environment variables are read once at container start. Editing the ConfigMap
  does **not** change a running container's environment; restart the Pod.
- A volume-mounted ConfigMap is refreshed by the kubelet after a delay (up to about a minute),
  **except** when mounted with `subPath`, which never updates. This example uses
  `subPath` on purpose so you can see that.

## Secrets

    kubectl apply -f secret.yaml
    kubectl apply -f pod-secret.yaml
    kubectl get secret db-credentials -o yaml
    kubectl get secret db-credentials -o jsonpath='{.data.DB_PASSWORD}' | base64 -d
    kubectl exec secret-demo -- env | grep DB_

Expected: the YAML shows the values base64-encoded under `data:`
(`stringData` is write-only convenience and is converted on the way in).

**base64 is encoding, not encryption.** Anyone who can read the Secret can decode it,
and by default Secrets are stored unencrypted in etcd unless encryption at rest is
configured. The password in `secret.yaml` is a placeholder, but committing a real
one would be a leak. See the mistakes below.

## Mistakes and fixes

### CreateContainerConfigError

`broken/missing-configmap.yaml` refers to a ConfigMap that is not there.

    kubectl apply -f broken/missing-configmap.yaml
    kubectl get pod missing-config
    kubectl describe pod missing-config

Expected: STATUS `CreateContainerConfigError`; the event says
`configmap "does-not-exist" not found`. The container is never started, so there are
no logs. Create the ConfigMap and the kubelet retries on its own. Add
`optional: true` to the reference if the config really is optional.

The same happens with a `secretKeyRef` to a missing Secret or key.

### Config changed but the app did not notice

Env vars are fixed at start (restart with `kubectl rollout restart deployment/NAME`).
Files mounted with `subPath` never update. Many apps only read config at startup anyway.

### Immutable ConfigMaps and Secrets

Setting `immutable: true` stops edits (and saves the kubelet from watching them).
To change one you create a new object with a new name and point the workload at it.
Appending a short content hash to the name is the usual pattern, and is what
Kustomize's `configMapGenerator` does (lesson 11).
