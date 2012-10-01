#!/bin/sh

PATH=$HOME/workspace/pygrade:$PATH

if [ -d "$1" ]; then
    find "$1" -name '*submissionText.html' | extract_pid.py | extract_url.py | tee repo.urls | gitpull.py repos/ | tee repo.dirs
else
    echo -e "Usage: fetch.sh DIR\t DIR = root directory of Scholar's unpacked bulkDownloads.zip" >&2
fi
