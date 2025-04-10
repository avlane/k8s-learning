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
