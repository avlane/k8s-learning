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
