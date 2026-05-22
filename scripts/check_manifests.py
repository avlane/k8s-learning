#!/usr/bin/env python3
"""Tiny structural check for the manifests in this repo.

This only looks at the text: every
document needs apiVersion, kind and metadata.name, no tabs, and images need a
tag that is not "latest". Workloads without limits or a securityContext get a note
(not an error). It is not a YAML parser and it validates nothing
against the Kubernetes API.

usage: python3 scripts/check_manifests.py [directory]
"""
import re
import sys
from pathlib import Path

SKIP_DIRS = {"broken", "scenarios", "templates", ".git"}
SKIP_NAMES = {"kustomization.yaml", "kind-config.yaml", "Chart.yaml", "values.yaml"}


def documents(text):
    docs = [[]]
    for line in text.splitlines():
        if line.startswith("---"):
            docs.append([])
        else:
            docs[-1].append(line)
    return [d for d in docs if any(l.strip() and not l.lstrip().startswith("#") for l in d)]


def has_top_level(doc, key):
    return any(re.match(key + r":\s*\S", line) for line in doc)


def has_metadata_name(doc):
    inside = False
    for line in doc:
        if line.startswith("metadata:"):
            inside = True
        elif inside and re.match(r"\S", line):
            return False
        elif inside and re.match(r"  name:\s*\S", line):
            return True
    return False


WORKLOADS = {"Pod", "Deployment", "StatefulSet", "DaemonSet", "Job", "CronJob"}


def kind_of(doc):
    for line in doc:
        match = re.match(r"kind:\s*(\S+)", line)
        if match:
            return match.group(1)
    return None


def check_file(path):
    problems = []
    notes = []
    text = path.read_text()
    if "\t" in text:
        problems.append("contains a tab character")
    for number, doc in enumerate(documents(text), 1):
        for key in ("apiVersion", "kind"):
            if not has_top_level(doc, key):
                problems.append("document {}: missing {}".format(number, key))
        if not has_metadata_name(doc):
            problems.append("document {}: missing metadata.name".format(number))
        if kind_of(doc) in WORKLOADS:
            body = "\n".join(doc)
            if "limits:" not in body:
                notes.append("document {}: no resource limits".format(number))
            if "securityContext:" not in body:
                notes.append("document {}: no securityContext".format(number))
        for line in doc:
            match = re.match(r"\s*(?:- )?image:\s*(\S+)", line)
            if match:
                image = match.group(1).strip("'\"")
                last = image.split("/")[-1]
                if ":" not in last and "@" not in image:
                    problems.append("image {} has no tag".format(image))
                elif image.endswith(":latest"):
                    problems.append("image {} uses :latest".format(image))
    return problems, notes


def main(argv):
    root = Path(argv[0] if argv else ".")
    failed = 0
    checked = 0
    for path in sorted(list(root.rglob("*.yaml")) + list(root.rglob("*.yml"))):
        parts = set(path.relative_to(root).parts)
        if parts & SKIP_DIRS or path.name in SKIP_NAMES or "{{" in path.read_text():
            continue
        checked += 1
        problems, notes = check_file(path)
        for problem in problems:
            failed += 1
            print("{}: {}".format(path, problem))
        for note in notes:
            print("{}: note: {}".format(path, note))
    print("checked {} files, {} problems".format(checked, failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
