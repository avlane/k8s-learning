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

## Mistakes and fixes

### restartPolicy: Always

`broken/job-restart-always.yaml` should be rejected on apply: `Unsupported value: "Always": supported values: "OnFailure", "Never"`.
`Never` makes a failed Pod stay around and the Job creates a *new* Pod for each retry. `OnFailure` restarts the container in the same Pod.

### Retries

`broken/job-fails.yaml` exits with status 3. Expected: `backoffLimit: 2` leads to about three Pods in
`Error`, with growing delays, and the Job ends with condition `Failed` and reason `BackoffLimitExceeded`.

### Overlapping and piling up (the CronJob fixes)

- `concurrencyPolicy: Forbid` skips a run if the previous one is still going (`Allow` is the default, `Replace` kills the old one).
- `startingDeadlineSeconds` gives up on a run that could not start in time (for example the controller was down). If more than 100 runs are missed the CronJob stops scheduling; a deadline limits what counts.
- `activeDeadlineSeconds` kills a Job that runs too long; `backoffLimit` caps retries.
- `ttlSecondsAfterFinished` deletes finished Jobs (and their Pods) automatically.
- `timeZone: "Etc/UTC"` pins the schedule's time zone. Without it the schedule follows the controller manager's zone (usually UTC, but not something to rely on). Use IANA names such as `Europe/Berlin`.

## Pausing

    kubectl patch cronjob heartbeat -p '{"spec":{"suspend":true}}'
    kubectl patch cronjob heartbeat -p '{"spec":{"suspend":false}}'

Suspending stops new runs; running Jobs continue. Runs that were due while suspended are not replayed
(though one inside `startingDeadlineSeconds` may fire right after resuming).
