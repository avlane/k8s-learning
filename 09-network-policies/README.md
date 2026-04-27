# 09 - Network policies

By default every Pod can talk to every other Pod. A NetworkPolicy restricts that, but
**only if the cluster's network plugin (CNI) enforces policies**. If it does not, the objects are accepted and
silently do nothing. I need to check what the CNI in my kind cluster does before believing any result here.

Files: `default-deny-all.yaml`, `allow-web-from-clients.yaml`, `allow-dns-egress.yaml`, `allow-client-egress-to-web.yaml`

## Run it

    kubectl apply -f ../02-deployments/deployment.yaml -f ../03-services/service-clusterip.yaml
    kubectl run client --image=busybox:1.37.0 --labels=role=client --restart=Never -- sleep 3600
    kubectl run stranger --image=busybox:1.37.0 --restart=Never -- sleep 3600
    kubectl exec client   -- wget -qO- --timeout=2 http://web      # works before any policy
    kubectl apply -f default-deny-all.yaml
    kubectl exec client   -- wget -qO- --timeout=2 http://web      # now blocked (even the DNS lookup)
    kubectl apply -f allow-dns-egress.yaml
    kubectl exec client   -- wget -qO- --timeout=2 http://web      # name resolves, connection still blocked
    kubectl apply -f allow-web-from-clients.yaml -f allow-client-egress-to-web.yaml
    kubectl exec client   -- wget -qO- --timeout=2 http://web      # allowed again
    kubectl exec stranger -- wget -qO- --timeout=2 http://web      # still blocked

## What to observe

Expected (and only on a CNI that enforces policies): blocked requests time out
(`wget: download timed out`) rather than being refused. Policies are additive allow rules on top of
a deny: a Pod is only isolated if some policy selects it, and then only the union of the allowed traffic gets through.

## Mistakes and fixes

- **Nothing changes.** The CNI does not implement NetworkPolicy.
- **`podSelector: {}`** selects *all* Pods in the namespace. `from: - podSelector` and `- namespaceSelector` as two list items mean OR; both keys inside one item mean AND. Indentation matters here.
- Policies match the **Pod's** port (`containerPort`), not the Service port. After lesson 02 moved nginx to 8080, this allow rule still said 80 and would have blocked everything it was meant to allow.
- **Egress deny breaks DNS.** Once egress is denied, `wget http://web` fails with `bad address 'web'` because the Pod can no longer reach CoreDNS. `allow-dns-egress.yaml` allows UDP and TCP 53 to the `kube-dns` Pods in `kube-system`.
- **Both ends need a rule.** With egress denied, the client needs an egress rule to `web` and `web` needs an ingress rule from the client. The first version of this lesson only denied ingress, so only one side was needed.
- The namespace selector relies on the `kubernetes.io/metadata.name` label that Kubernetes puts on every namespace automatically.
