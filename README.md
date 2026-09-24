# k8s-learning

Notes and manifests from learning Kubernetes, one folder per topic. Each lesson
has the manifests, a README with the commands to run and what to look for, and a
list of mistakes I expect to make with the fix.

## Lessons

- [00-setup](00-setup/README.md): cluster options and kubectl basics

- [01-pods](01-pods/README.md): a single Pod, logs, exec, port-forward

- [02-deployments](02-deployments/README.md): Deployments, ReplicaSets, rollouts

- [03-services](03-services/README.md): ClusterIP, NodePort, headless Services and DNS

- [04-config-secrets](04-config-secrets/README.md): ConfigMaps, Secrets, env vars vs files

- [05-probes-resources](05-probes-resources/README.md): probes, requests and limits, QoS

- [06-storage](06-storage/README.md): emptyDir, PVCs, StatefulSets

- [07-ingress-gateway](07-ingress-gateway/README.md): Ingress, then the Gateway API

- [08-rbac](08-rbac/README.md): ServiceAccounts, Roles, RoleBindings, `auth can-i`

- [09-network-policies](09-network-policies/README.md): default deny and allow rules

- [10-helm](10-helm/README.md): a hand-written chart, values, releases

- [11-kustomize](11-kustomize/README.md): base and overlays, `kubectl kustomize`

- [12-jobs-cronjobs](12-jobs-cronjobs/README.md): Jobs, CronJobs, retries and cleanup

- [13-autoscaling](13-autoscaling/README.md): metrics-server and the HorizontalPodAutoscaler

- [14-troubleshooting](14-troubleshooting/README.md): symptom table and broken scenarios

## Checking the YAML

`python3 scripts/check_manifests.py` runs a text-level check over the manifests (apiVersion, kind,
metadata.name, image tags) and prints notes for workloads without limits or a securityContext. It skips `broken/` and
`scenarios/` on purpose, plus Helm templates. It is not a validator.

`kubectl apply --dry-run=client` does not help for this: it still asks a cluster's discovery endpoint which resource types exist.
