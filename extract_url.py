#!/usr/bin/env python2

import sys
import os.path
import shlex
import subprocess
import string
import re

url_regex = re.compile(r'(?P<url>https?://[^\s]+)')

for line in sys.stdin:
    (pid, file_path) = shlex.split(line)
    file_path = os.path.realpath(file_path)
    
    #pandoc -f html -t plain
    pandoc_command = ['pandoc','-f','html','-t','plain', file_path]
    submission_text = subprocess.check_output(pandoc_command)
    lines = submission_text.splitlines()

    for line in lines:
        #not sure why pandoc would insert a literal non-breaking space in 'plain' output, but whatevz
        line = line.replace('\302\240', r' ')
        match = url_regex.search(line)
        if match:
            url = match.group("url")
            (pre, url, directory) = line.partition(url)
            print "{} \"{}\" \"{}\"".format(pid,url,directory.strip(' ()[]{}/'))
            try:
                values = shlex.split(line)
            except ValueError:
                print "Unable to parse text for {}: length {}".format(pid)
            else:
                url = values[0]
                try:
                    path = values[1]
                except IndexError:
                    path = "."
            break


