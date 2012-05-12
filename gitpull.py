#!/usr/bin/env python2

import argparse
from sys import argv,stdout,stderr,stdin,exit
import os
from github import *
import subprocess

parser = argparse.ArgumentParser(description='Checkout/pull a list of git repositories from github.')
parser.add_argument('csvfile', nargs='?', type=argparse.FileType('r'),default=stdin,
                   help='filename of a comma deliminated file containing a list of usernames')


args = parser.parse_args()
print args
def create_dir(dirname):
    if not os.path.exists(dirname):
        try:
            os.makedirs(dirname)
        except OSError,e:
            return False
        return True
    else:
        return True

if args.csvfile:
    import csv
    gitusersFile = csv.reader(args.csvfile)
    gitusers = []
    for row in gitusersFile:
        if not row[-1]=="":
            gitusers.append(row[-1])

for address in stdin:
    
gh = github.GitHub()

def sync_repo(username, reponame):
    userpath = os.path.join(os.path.curdir,username)
    create_dir(userpath)

    reponame = 'ece2524'
    repo = None
    try:
        repo = gh.repos.show(username, reponame)
    except:
        stderr.write("No repo %s for %s\n" % (reponame,username))
        next

    if repo:
        url = repo.url
        repopath = os.path.join(userpath, repo.name)
        if os.path.exists(os.path.join(repopath,'.git')):
            action = 'pull'
        else:
            action = 'clone'

        command = "cd %s; git %s %s" % (repopath,action,url)
        print command
        subprocess.call(command, shell=True)
