#!/usr/bin/env python2

import sys
import os.path
import shlex
import subprocess
import string
import re
from itertools import imap 

url_regex = re.compile(r'(?P<url>https?://[^\s]+)')
url_to_branch = re.compile(r'https?://github.com/([^\s/]+)/([^\s/]+)/tree/([^\s/]+)')
url_with_sub = re.compile(r'https?://github.com/(?P<user>[^\s/]+)/(?P<repo>[^\s/]+)/tree/(?P<branch>[^\s/]+)/(?P<path>[^\s]+)')

def parse_url(match):
    url = match.group("url")
    (pre, url, directory) = line.partition(url)
    return (url, directory)

def parse_url_with_sub(match):
    repo = match.group("repo")
    user = match.group("user")
    branch = match.group("branch")
    directory = match.group("path")
    return ("https://github.com/{}/{}.git".format(user,repo), directory)

for (pid, file_path) in imap(shlex.split, sys.stdin):
    file_path = os.path.realpath(file_path)
    
    #pandoc -f html -t plain
    pandoc_command = ['pandoc','-f','html','-t','plain', file_path]
    submission_text = subprocess.check_output(pandoc_command)
    lines = submission_text.splitlines()

    found_match = False
    urls = {}
    for line in lines:
        #not sure why pandoc would insert a literal non-breaking space in 'plain' output, but whatevz
        line = line.replace('\302\240', r' ')
        match = url_regex.search(line)
        match2 = url_with_sub.search(line)
        match_branch = url_to_branch.search(line)

        if match:
            (url, directory) = parse_url(match)
        elif match2:
            (url, directory) = parse_url_with_sub(match2)
        elif match_branch:
            sys.stderr.write("URL to Branch not implemented: {}\n".format(line))

        if match or match2:
            print "{} \"{}\" \"{}\"".format(pid,url,directory.strip(' ()[]{}/'))
            try:
                values = shlex.split(line)
            except ValueError:
                sys.stderr.write("{}: Unable to parse text: length {}\n".format(pid))
            else:
                urls[pid] = values[0]
                found_match = True
                try:
                    path = values[1]
                except IndexError:
                    path = "."
            break
    if not found_match:
        sys.stderr.write("{}: No match found\n".format(pid))
        if len(submission_text) > 1:
            sys.stderr.writelines(submission_text)


