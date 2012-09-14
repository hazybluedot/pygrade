#!/usr/bin/env python2

import argparse
from sys import argv,stdout,stderr,stdin,exit
import os
import subprocess
import shlex
from github import Github #easy_install PyGitHub
from git import * # aur/gitpython on Arch

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

def sync_repo(username, url):
    userpath = os.path.join(os.path.curdir,username)
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

    if not os.path.exists(repopath):
        create_dir(repopath)
        action = 'clone'
    else:
        action = 'pull'

    repo = Repo(repopath)

    if action == 'clone':
        repo.clone_from(url,repopath)
    else:
        remote = repo.remote(name='origin')
        try:
            remote.pull()
        except AssertionError as e:
            stderr.write("Error on {}:\n\t{}\n".format(username,e))

    #command = "cd {}; git {} {}".format(repopath,action,url)
    #print command
    #subprocess.call(command, shell=True)
    return repopath

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Checkout/pull a list of git repositories from github.')
    #parser.add_argument('csvfile', nargs='?', type=argparse.FileType('r'),default=stdin,
     #                  help='filename of a comma delimited file containing a list of usernames')


    args = parser.parse_args()
    
    for line in stdin:
        (pid,url,project_directory) = shlex.split(line)
        repopath = sync_repo(pid,url)
        project_directory = os.path.join(repopath,project_directory)
        print "{} \"{}\"".format(pid,os.path.realpath(project_directory))
