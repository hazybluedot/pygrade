import os
import subprocess
from maybe import maybe
from sys import stderr

class EmacsClient:
    def __init__(self,servername=None):
        self.args = ['emacsclient']
        if servername:
            self.args.expand(['--server-file',servername])
        self.buffers = []

    def open_file(self,name,**kwargs):
        verbose = maybe(kwargs,'verbose',False)
        args = self.args[:]
        if 'nowait' in kwargs:
            args.append('-n')
        #args.append('-e')
        #args.append("(find file {})".format(name))
        #args.append('-c')
        #args.append('-nw')
        args.append(name)
        #tmux_args = ['tmux','split-window']
        #tmux_args.extend(args)
        #print tmux_args
        if verbose:
            stderr.write("EmacsClient open_file with args={}\n".format(args))
        ret = subprocess.check_call(args)
        self.buffers.append(os.path.basename(name))

    def kill_buffer(self,name):
        args = self.args[:]
        args.append('-e')
        args.append('(kill-buffer \"{}\")'.format(name))
        try:
            subprocess.check_call(args)
        except subprocess.CalledProcessError as e:
            pass
            
    def kill_all(self):
        for buffer in self.buffers:
            self.kill_buffer(buffer)
        self.buffers = []
