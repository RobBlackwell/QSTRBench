#!/usr/bin/env bash
find ../data -type f -name "*.jsonl.xz" -exec xz -dk {} \;
