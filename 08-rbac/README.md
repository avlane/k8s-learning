# 08 - RBAC

Authorization in Kubernetes is additive: you grant verbs on resources to subjects. There are no deny rules.

- **Role / ClusterRole**: a set of permissions (namespaced / cluster-wide).
- **RoleBinding / ClusterRoleBinding**: attach a role to users, groups or ServiceAccounts.

Files: `serviceaccount.yaml`, `clusterrolebinding-admin.yaml` (the first, bad attempt)

## Run it

    kubectl apply -f serviceaccount.yaml -f clusterrolebinding-admin.yaml
    kubectl auth can-i list pods --as=system:serviceaccount:default:pod-reader
    kubectl auth can-i delete nodes --as=system:serviceaccount:default:pod-reader

Expected: both print `yes`. That is the problem: a ServiceAccount that only needs to
read Pods can now do anything in the cluster, and so can anything running with its token.
Next commit replaces this with a Role.
