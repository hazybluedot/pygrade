#!/usr/bin/env python2

import argparse
import sys
import os
import shlex
from github import Github #easy_install PyGitHub
from git import * # aur/gitpython on Arch
from itertools import imap

github = Github()

def create_dir(dirname):
    if not os.path.exists(dirname):
        try:
            os.makedirs(dirname)
        except OSError,e:
            return False
        return True
    else:
        return True

def sync_repo(username, url, basepath, **kwargs):
    pretend = False
    if 'pretend' in kwargs:
        pretend = kwargs['pretend']

    userpath = os.path.join(basepath,username)
    if not pretend:
        create_dir(userpath)
        
    values = url.split('/')
    username = values[3]
    try:
        (reponame,dot,ext) = values[4].partition('.')
    except IndexError:
        reponame = 'ECE2524'

    repo = github.get_user(username).get_repo(reponame)
    url = repo.clone_url
    repopath = os.path.join(userpath, reponame)

    if not os.path.exists(repopath) and not pretend:
        create_dir(repopath)
        action = 'clone'
    else:
        action = 'pull'

    repo = Repo(repopath)

    if not pretend:
        if action == 'clone':
            repo.clone_from(url,repopath)
        else:
            remote = repo.remote(name='origin')
            try:
                remote.pull()
            except AssertionError as e:
                sys.stderr.write("Error on {} with {}:\n\t{}\n".format(username,repopath,e))
            
    return repopath

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Checkout/pull a list of git repositories from github.')
    parser.add_argument("-p","--pretend", action="store_true", help="Do everything except pull/clone repositories")
    parser.add_argument("-r","--raw", action="store_true", help="Read input as raw git repositories to sync")
    parser.add_argument("basepath", nargs=1, help="Base path")

    args = parser.parse_args()
    
    basepath = os.path.realpath(args.basepath[0])

    if not os.path.isdir(basepath):
        sys.stderr.write("{}: not a real directory\n".format(basepath))
        sys.exit(1)

    if args.raw:
        for repodir in imap(str.strip, sys.stdin):
            (repodir,git) = os.path.split(repodir)
            repo = Repo(repodir)
            origin = repo.remotes.origin
            sys.stderr.write("Pulling from {}\n".format(repodir))
            try:
                origin.pull()
            except AssertionError as e:
                sys.stderr.write("{}: AssertionError\n".format(repodir))
    else:
        for (pid,url,project_directory) in imap(shlex.split, sys.stdin):
            repopath = sync_repo(pid,url,basepath,pretend=args.pretend)
            project_directory = os.path.join(repopath,project_directory)
            print "{} \"{}\"".format(pid,os.path.realpath(project_directory))
