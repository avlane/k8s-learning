# 12 - Jobs and CronJobs

A Job runs Pods to completion. A CronJob creates Jobs on a schedule.

Files: `job.yaml`, `cronjob.yaml`

## Run it

    kubectl apply -f job.yaml
    kubectl get job batch-demo --watch
    kubectl get pods -l job-name=batch-demo
    kubectl logs -l job-name=batch-demo
    kubectl apply -f cronjob.yaml
    kubectl get cronjob heartbeat
    kubectl create job manual-run --from=cronjob/heartbeat      # run it now
    kubectl get jobs

## What to observe

Expected: `COMPLETIONS` goes 0/3, 1/3, 2/3, 3/3 as three Pods run one after another
(`parallelism: 1`); the Pods end up `Completed`, not deleted, so logs stay readable.
The CronJob has no jobs until the next five-minute mark; `LAST SCHEDULE` shows when it last fired.

## Naive bits to fix later

- The CronJob has no `concurrencyPolicy`, so a slow run overlaps the next one.
- Finished Jobs and Pods pile up (the CronJob keeps 3 successful and 1 failed Jobs by default, a plain Job keeps itself forever).
