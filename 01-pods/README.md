# 01 - Pods

A Pod is one or more containers that share a network namespace and volumes. You
rarely create bare Pods in real life (a Deployment does it for you), but they are
the smallest unit to learn on.

Files: `pod.yaml`, `toolbox.yaml` (a busybox Pod to run commands from inside the cluster)

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

## Talking to the Pod from another Pod

    kubectl apply -f toolbox.yaml
    kubectl get pod hello-nginx -o wide                      # note the IP column
    kubectl exec toolbox -- wget -qO- http://POD_IP          # busybox has wget, not curl

Pod IPs change every time a Pod is recreated, which is why Services exist (lesson 03).

## Mistakes and fixes

### ImagePullBackOff / ErrImagePull

`broken/imagepull-typo.yaml` asks for a tag that does not exist.

    kubectl apply -f broken/imagepull-typo.yaml
    kubectl get pods --watch

Expected: STATUS goes `ErrImagePull`, then `ImagePullBackOff`, with
growing delays between retries. `kubectl describe pod imagepull-typo` should show
a `Failed to pull image` event saying the manifest for `nginx:1.27.33` was not found.

Common causes: typo in the name or tag, private registry without an
`imagePullSecret`, or no network access from the node.

Fix: correct the tag (or add the pull secret) and re-apply. For a bare Pod most
fields are immutable, so `kubectl delete pod` and apply again. The image field is one
of the few you can change in place with `kubectl set image` or `kubectl edit`.
### CrashLoopBackOff

`broken/crashloop.yaml` prints an error and exits with status 1. The default
`restartPolicy` of a Pod is `Always`, so the kubelet restarts it, with an
exponential back-off (10s, 20s, 40s ... up to 5 minutes).

    kubectl apply -f broken/crashloop.yaml
    kubectl get pod crashloop --watch
    kubectl logs crashloop --previous
    kubectl describe pod crashloop

Expected: RESTARTS climbs, STATUS alternates between `Error` and
`CrashLoopBackOff`. `logs --previous` shows the output of the last crashed run
(`starting` and `config file missing`). `describe` shows `Last State: Terminated`
with `Exit Code: 1`.

Reading the exit code: 1 is the app's own failure, 137 is SIGKILL (often OOM, see
lesson 05), 143 is SIGTERM, 126/127 is a command that could not run or was not found.
CrashLoopBackOff is a symptom, not a cause. The cause is in `logs --previous` or the exit code.
