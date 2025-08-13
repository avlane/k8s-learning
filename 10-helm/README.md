# 10 - Helm

Helm templates Kubernetes manifests with Go templates and tracks each install as a
**release** (with revisions you can roll back). The chart in `webapp/` re-packages the
Deployment and Service from earlier lessons.

## Layout

    webapp/
      Chart.yaml        chart metadata (apiVersion v2 = Helm 3)
      values.yaml       defaults, overridable with --set or -f
      templates/        manifests with {{ }} placeholders; _helpers.tpl holds named templates

## Commands

    helm lint webapp
    helm template demo webapp                              # render locally, no cluster needed
    helm template demo webapp --set replicaCount=3 --set image.tag=1.27.5
    helm install demo webapp
    helm upgrade demo webapp --set replicaCount=4
    helm list
    helm history demo
    helm rollback demo 1
    helm uninstall demo

## What to observe

Expected: `helm template` prints a Deployment named `demo-webapp` and a Service of the same name,
both labelled `app.kubernetes.io/instance: demo`. `helm history` shows one revision per install/upgrade/rollback
(a rollback creates a *new* revision).

## Mistakes to watch for

- **`indent` instead of `nindent`**: `nindent` adds a leading newline, which is what you need after a key like `labels:`. With `indent` the first line stays on the key's line and the YAML breaks.
- **Version tags that look like numbers**: `tag: 1.27` is a float in YAML (and would turn `1.20` into `1.2`). Quote versions, or leave `tag: ""` and fall back to `appVersion`.
- **Whitespace trimming**: `{{-` removes whitespace before the tag, `-}}` after. Too much trimming glues lines together, too little leaves blank lines.
- **Debugging**: `helm template --debug` prints the rendered output even when it is invalid YAML, which is the easiest way to find the broken line.
- **Selectors are immutable**: do not put anything that changes per release (like the chart version) into `selectorLabels`.
