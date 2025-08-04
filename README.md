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
