#!/usr/bin/env python2

import sys
import os.path
import shlex
import subprocess
import string
import re
from itertools import imap 

url_regex = re.compile(r'(?P<url>https?://[^\s]+)')
url_with_sub = re.compile(r'https?://github.com/(?P<user>[^\s/]+)/(?P<repo>[^\s/]+)/tree/(?P<branch>[^\s/]+)/(?P<path>[^\s]+)')
url_to_branch = re.compile(r'https?://github.com/([^\s/]+)/([^\s/]+)/tree/([^\s/]+)')

def parse_url(match, line):
    url = match.group("url")
    (pre, url, directory) = line.partition(url)
    return (url, directory)

def parse_url_with_sub(match):
    repo = match.group("repo")
    user = match.group("user")
    branch = match.group("branch")
    directory = match.group("path")
    return ("https://github.com/{}/{}.git".format(user,repo), directory)

def url_iterator(iterable):
    for line in iterable:
        match = url_regex.search(line)
        if match:
            url = match.group("url")
            match_sub = url_with_sub.search(url)
            match_branch = url_to_branch.search(url)
            if match_sub:
                yield parse_url_with_sub(match_sub)
            else:
                yield parse_url(match,line)
        #elif match_branch:
         #   sys.stderr.write("URL to Branch not implemented: {}\n".format(line))

for (pid, file_path) in imap(shlex.split, sys.stdin):
    file_path = os.path.realpath(file_path)
    
    #pandoc -f html -t plain
    pandoc_command = ['pandoc','-f','html','-t','plain', file_path]
    submission_text = subprocess.check_output(pandoc_command)
    lines = submission_text.splitlines()

    found_match = False
        #not sure why pandoc would insert a literal non-breaking space in 'plain' output, but whatevz
    #for url in ( match.group("url") for match in url_regex.search(imap(lambda x: x.replace('\302\240', ' '), lines)) if match ):
    for (url, directory) in url_iterator( line for line in imap(lambda x: x.replace('\302\240', ' '), lines)):
        found_match = True
        print "{} \"{}\" \"{}\"".format(pid,url,directory.strip(' ()[]{}/'))
 
    if not found_match:
        sys.stderr.write("{}: No match found\n".format(pid))
        if len(submission_text) > 1 and len(submission_text) < 100:
            sys.stderr.writelines(submission_text)


