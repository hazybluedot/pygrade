#!/usr/bin/env python2

prog1 = { 'path': 'shells.py', 'env': '/usr/bin/env python2',
          'trials': [ {'stdin': None, 'args': None},
                      {'stdin': '/etc/passwd', 'args': None}
                      ]
          }

import subprocess

def run_tests(t):
    args = [t['env'], t['path']]
    for trial in t['trials']:
        myargs = args
        for arg in t['args']:
            myargs.append(arg)

        ret = subprocess.check_call(args, stdout=of, sterr=ef)
