# 09 - Network policies

By default every Pod can talk to every other Pod. A NetworkPolicy restricts that, but
**only if the cluster's network plugin (CNI) enforces policies**. If it does not, the objects are accepted and
silently do nothing. I need to check what the CNI in my kind cluster does before believing any result here.

Files: `default-deny-ingress.yaml`, `allow-web-from-clients.yaml`

## Run it

    kubectl apply -f ../02-deployments/deployment.yaml -f ../03-services/service-clusterip.yaml
    kubectl run client --image=busybox:1.37.0 --labels=role=client --restart=Never -- sleep 3600
    kubectl run stranger --image=busybox:1.37.0 --restart=Never -- sleep 3600
    kubectl exec client   -- wget -qO- --timeout=2 http://web      # works before any policy
    kubectl apply -f default-deny-ingress.yaml
    kubectl exec client   -- wget -qO- --timeout=2 http://web      # now blocked
    kubectl apply -f allow-web-from-clients.yaml
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
- Only `Ingress` is denied so far. Egress policies come later, and they will break DNS if not planned for.
