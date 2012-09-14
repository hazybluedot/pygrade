#!/usr/bin/env python2

import re
import sys

pid_regex = re.compile(r'\((\w+)\)')

for line in sys.stdin:
    pid = pid_regex.findall(line)[0]
    sys.stdout.write("{} \"{}\"\n".format(pid, line.rstrip()))
