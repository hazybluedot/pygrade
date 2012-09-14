#!/bin/sh

if [ -d "$1" ]; then
    find "$1" -name '*submissionText.html' | ~/workspace/pygrade/extract_pid.py | ~/workspace/pygrade/extract_url.py | ~/workspace/pygrade/gitpull.py
else
    echo -e "Usage: fetch.sh DIR\t DIR = root directory of Scholar's unpacked bulkDownloads.zip" >&2
fi
