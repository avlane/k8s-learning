# 08 - RBAC

Authorization in Kubernetes is additive: you grant verbs on resources to subjects. There are no deny rules.

- **Role / ClusterRole**: a set of permissions (namespaced / cluster-wide).
- **RoleBinding / ClusterRoleBinding**: attach a role to users, groups or ServiceAccounts.

Files: `serviceaccount.yaml`, `role.yaml`, `rolebinding.yaml`, `pod-as-sa.yaml`

## Run it

    kubectl apply -f serviceaccount.yaml -f role.yaml -f rolebinding.yaml
    kubectl auth can-i list pods   --as=system:serviceaccount:default:pod-reader
    kubectl auth can-i delete pods --as=system:serviceaccount:default:pod-reader
    kubectl auth can-i list secrets --as=system:serviceaccount:default:pod-reader
    kubectl auth can-i --list --as=system:serviceaccount:default:pod-reader

Expected: `yes`, `no`, `no`, and a table that lists `pods [] [] [get list watch]`
plus the few default discovery rules every authenticated subject gets.

From inside a Pod (uses the mounted token):

    kubectl apply -f pod-as-sa.yaml
    kubectl exec api-client -- sh -c 'curl -s --cacert /var/run/secrets/kubernetes.io/serviceaccount/ca.crt \
      -H "Authorization: Bearer $(cat /var/run/secrets/kubernetes.io/serviceaccount/token)" \
      https://kubernetes.default.svc/api/v1/namespaces/default/pods | head -n 20'

Expected: a JSON `PodList`. Changing the URL to `.../secrets` should return a `403 Forbidden` status
object saying the ServiceAccount "cannot list resource secrets".

## Mistakes and fixes

- **Binding cluster-admin to make errors go away.** The first version of this lesson did that. Start with
  `kubectl auth can-i` and the exact verb/resource in the 403 message, then write the smallest Role that covers it.
- **Role vs ClusterRole mix-ups.** A RoleBinding can reference a ClusterRole but then grants it only in the binding's namespace.
- **Empty string API group.** Core resources (pods, services, configmaps) use `apiGroups: [""]`. `deployments` is in `apps`.
- **Wrong subject namespace.** A ServiceAccount subject needs `namespace:` and a typo here silently grants nothing.
- Roles do not give access to subresources automatically: `pods/log` and `pods/exec` are separate resources.
