#!/usr/bin/env python2

import argparse
import sys
import os
import shlex
from git import * # aur/gitpython on Arch
from itertools import imap

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser("Quick little utility to switch active branches on a list of git repositories")
    parser.add_argument("-v","--verbose", action="store_true", help="Be Verbose")
    parser.add_argument("-b","--branch-name", help="Name of the branch to switch to")

    args = parser.parse_args()

    for (pid, project_path) in imap(shlex.split, sys.stdin):
        sys.stderr.write("{}\n".format(project_path))
        repo = Repo(project_path)
        
        for branch in repo.heads:
            sys.stderr.write("\tbranch: {}\n".format(branch.name))
            if branch.name == args.branch_name:
                branch.checkout()
            else:
                #git = repo.git
                #git.checkout('head', b=args.branch_name)
                new_branch = repo.create_head(args.branch_name)
                new_branch.checkout()
        #grading_branch = repo.create_head(args.branch_name)
        #repo.head.reference = grading_branch
