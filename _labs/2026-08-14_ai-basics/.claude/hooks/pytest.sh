#!/bin/bash
f=$(jq -r '.tool_input.file_path // empty')
case "$f" in *.py) ;; *) exit 0 ;; esac
python3 -m pytest -q --tb=no >&2 || exit 2
