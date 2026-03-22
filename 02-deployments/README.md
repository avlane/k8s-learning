# 02 - Deployments

A Deployment manages a ReplicaSet, which manages the Pods. You declare the
desired state (3 replicas of this Pod template) and the controllers keep
reconciling towards it.

Files: `deployment.yaml`

## Run it

    kubectl apply -f deployment.yaml
    kubectl get deployment,replicaset,pods -l app=web
    kubectl delete pod -l app=web --wait=false      # watch them come back
    kubectl scale deployment web --replicas=5
    kubectl set image deployment/web nginx=nginxinc/nginx-unprivileged:1.29.0
    kubectl rollout status deployment/web
    kubectl rollout history deployment/web
    kubectl rollout undo deployment/web

## What to observe

Expected:

    $ kubectl get deployment web
    NAME   READY   UP-TO-DATE   AVAILABLE   AGE
    web    3/3     3            3           30s

- Pod names look like `web-<replicaset-hash>-<random>`. The hash changes when the Pod template changes.
- After `set image` there are two ReplicaSets: the new one scales up while the old one scales down. The old one stays at 0 replicas so that `rollout undo` can use it.
- Scaling does not change the template, so it does not create a new ReplicaSet.
- The change cause column in `rollout history` is empty unless you set the `kubernetes.io/change-cause` annotation.

## What was added after the first version

- Requests and a memory limit (no CPU limit on purpose, see lesson 13), plus readiness and liveness probes.
  With the probes, `maxUnavailable: 0` now means something: a new Pod must pass its readiness probe before an old one goes.

## Running as non-root

The official `nginx` image starts as root, binds port 80 and writes to `/var/cache/nginx`, so dropping all capabilities
or forcing `runAsNonRoot` on it would most likely crash it. The Deployment now uses `nginxinc/nginx-unprivileged`,
which runs as an unprivileged user and listens on **8080**. Consequences:

- The container port is now 8080, and the probes use the port *name* (`http`) so only one line mentions the number.
- A Service in front of it must use `targetPort: 8080` (or `http`). See lesson 03.
- `runAsNonRoot: true` works without `runAsUser` here because the image declares a numeric non-root USER.
- `seccompProfile: RuntimeDefault` applies the container runtime's default syscall filter.

`readOnlyRootFilesystem: true` probably needs `emptyDir` mounts for the paths nginx writes to.

## Still naive

- The image tag is pinned but is bumped by hand.

## Mistakes and fixes

### Selector does not match the template labels

`broken/selector-mismatch.yaml` selects `app=web` but labels its Pods `app=webapp`.

    kubectl apply -f broken/selector-mismatch.yaml

Expected: in `apps/v1` the API server rejects this at apply time
with an error along the lines of `spec.template.metadata.labels: Invalid value ...:
selector does not match template labels`. In the old `extensions/v1beta1` and
`apps/v1beta1` days a mismatch was accepted and produced a Deployment that never
owned its Pods, which is a good reason to stay on `apps/v1`.

Related mistakes:

- `spec.selector` is immutable after creation. Changing the labels of a running
  Deployment means deleting and recreating it.
- Two Deployments with overlapping selectors fight over the same Pods. Keep a unique label such as `app.kubernetes.io/instance`.
- A **Service** with a selector that matches nothing is not rejected. It just has no endpoints (lesson 03).

## Rolling update settings

`maxSurge: 1, maxUnavailable: 0` means: start one extra Pod first, wait until it is
Ready (plus `minReadySeconds`), then remove an old one. Capacity never drops
below the desired replica count. The defaults are 25% for both, which rounds
`maxSurge` up and `maxUnavailable` down.

Without a readiness probe a Pod counts as Ready as soon as its container starts,
so a rollout can "succeed" while the new version is still booting. That is the
motivation for lesson 05.

`revisionHistoryLimit: 5` keeps five old ReplicaSets for `rollout undo`. The
default is 10, which clutters `kubectl get rs`.

## Labels

Besides `app: web` the Deployment and its Pods carry the recommended `app.kubernetes.io/*` labels
(`name`, `component`, `part-of`), which tools such as dashboards and Helm look for.
The **selector stays `app: web`**: `spec.selector` cannot be changed after creation, and a selector that includes
labels the Pods do not all have would orphan them. Adding labels to the Pod template is safe, changing the selector is not.

## Surviving voluntary disruptions

`pdb.yaml` says at least 2 `app=web` Pods must stay available during *voluntary* disruptions such as `kubectl drain`.
Eviction requests that would drop below 2 are refused until another Pod is ready, so a drain can appear to hang.
It does nothing for crashes or node failures. `topologySpreadConstraints` asks the scheduler to spread the replicas
across nodes (`ScheduleAnyway` makes it a preference, so a one-node cluster still schedules everything).

    kubectl apply -f pdb.yaml
    kubectl get pdb web
    kubectl drain learning-worker --ignore-daemonsets --delete-emptydir-data

Expected: `ALLOWED DISRUPTIONS` is 1 with three healthy replicas.
A PDB with `minAvailable` equal to the replica count blocks every drain, which is the usual way this goes wrong.
