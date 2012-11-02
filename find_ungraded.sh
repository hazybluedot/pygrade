#!/usr/bin/env sh

find "$1" -name "$2" -print0 | xargs -0 grep -L '###DKM' | sed -r 's/^(.*)$/"\1"/g'
