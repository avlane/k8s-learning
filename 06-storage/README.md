# 06 - Storage

Container filesystems vanish with the container. Volumes outlive container restarts,
and PersistentVolumes outlive Pods.

Files: `pod-emptydir.yaml`, `pvc.yaml`, `pod-pvc.yaml`

## Run it

    kubectl apply -f pod-emptydir.yaml
    kubectl exec emptydir-demo -- cat /data/started
    kubectl apply -f pvc.yaml -f pod-pvc.yaml
    kubectl get pvc,pv
    kubectl get storageclass
    kubectl exec pvc-demo -- cat /data/log.txt
    kubectl delete pod pvc-demo && kubectl apply -f pod-pvc.yaml     # data should survive
    kubectl exec pvc-demo -- cat /data/log.txt                       # two lines now

## What to observe

Expected:

    $ kubectl get pvc
    NAME         STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   AGE
    data-claim   Bound    pvc-0f3c...                                1Gi        RWO            standard       10s

- `emptyDir` lives as long as the **Pod** (it survives container restarts, not Pod deletion).
- The PVC does not set `storageClassName`, so the cluster's default StorageClass is used and a PV is provisioned dynamically.
- `ReadWriteOnce` means one **node** at a time can mount it, not one Pod.

## StatefulSet

`statefulset.yaml` creates `store-0` and `store-1`. Unlike a Deployment:

- Pods get stable names and are created in order (`store-0` first, then `store-1`).
- Each Pod gets its **own** PVC from `volumeClaimTemplates` (`data-store-0`, `data-store-1`).
- The headless Service gives each Pod a DNS name: `store-0.store.default.svc.cluster.local`.
- If `store-0` is deleted it comes back with the same name and re-attaches the same PVC.

    kubectl apply -f statefulset.yaml
    kubectl get pods -l app=store --watch
    kubectl get pvc
    kubectl delete pod store-0
    kubectl exec store-0 -- cat /data/hosts      # should show store-0 twice after the restart

## Mistakes and fixes

### PVC stuck in Pending

`broken/pvc-no-class.yaml` names a StorageClass (`fast-ssd`) the cluster does not have.

    kubectl apply -f broken/pvc-no-class.yaml
    kubectl get pvc pvc-no-class
    kubectl describe pvc pvc-no-class

Expected: STATUS stays `Pending`; the event says `storageclass.storage.k8s.io "fast-ssd" not found`.
Other reasons for Pending: no default StorageClass at all, or a class with
`volumeBindingMode: WaitForFirstConsumer`, where the PVC stays Pending **on purpose**
until a Pod that uses it is scheduled. A Pod that references a Pending PVC is itself
`Pending` with `unbound immediate PersistentVolumeClaims`.

### Data deleted when you did not expect it

The `reclaimPolicy` of the StorageClass decides what happens to the PV when the PVC goes away.
Dynamically provisioned volumes usually default to `Delete`. For anything you care about
use `Retain` (set on the StorageClass, or patch the PV).

### PVCs left behind by a StatefulSet

Deleting a StatefulSet or scaling it down does not delete its PVCs by default, which protects data
but also leaks storage. `persistentVolumeClaimRetentionPolicy` (`whenDeleted` / `whenScaled`:
`Retain` or `Delete`) controls this. Clean up manually with `kubectl delete pvc -l app=store`.

### Volume permissions

A non-root container may not be able to write to a freshly provisioned volume owned by root.
`securityContext.fsGroup` on the Pod makes the kubelet adjust group ownership. This matters a lot for databases.

## Why fsGroup is in the manifests now

Once the writers run as UID 65534 instead of root, a new volume owned by root would refuse their writes
(`Permission denied`). `fsGroup: 65534` on the Pod makes the kubelet set the group ownership of supported volumes
(emptyDir, most dynamically provisioned PVCs) to that group and make them group-writable. Some storage types
ignore `fsGroup`, and on large volumes the recursive ownership change slows Pod start. `fsGroupChangePolicy: OnRootMismatch` helps there.

## Retention policy and expanding a volume

`persistentVolumeClaimRetentionPolicy` in `statefulset.yaml` spells out the default (`Retain` on delete and on scale
down). Setting `whenDeleted: Delete` removes the PVCs together with the StatefulSet. That field went through alpha and
beta before becoming stable, so check that your cluster version accepts it.

To grow a PVC, edit `spec.resources.requests.storage` to a larger value. This works only when the StorageClass has
`allowVolumeExpansion: true` and the driver supports it (`kubectl get storageclass -o yaml`). Shrinking is not possible.
For a StatefulSet the `volumeClaimTemplates` are immutable, so you edit each PVC by hand and then recreate the
StatefulSet with `kubectl delete statefulset store --cascade=orphan` so the Pods keep running.
