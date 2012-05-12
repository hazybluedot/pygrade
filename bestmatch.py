#!/usr/bin/env python2

import os
import argparse
from sys import argv

class BestMatch:
    """Find files that match a name in a directory tree.
    If no matches are found for a given name then the search is incrementally
    weakend until a match is found"""

    def __init__(self, basedir, file_name, traverse=False, verbose=False):
        self.basedir = basedir
        self.file_name = file_name
        self.traverse = traverse
        self.verbose = verbose
        self.find_alternatives(self.basedir, self.file_name)
        #self.get_choices(self.basedir, self.file_name)

    def find_alternatives(self, basedir, _basename):
        basename=_basename
        while (self.files_found == 0 and len(basename) > 0):
            if (self.verbose):
                print "Searching %s for files starting with %s." % (basedir, basename)
            self.get_choices(basedir, basename)
            basename = basename[0:-1]

    def get_choices(self, basedir, basename):
        self.files_found = 0

        if os.path.isdir(basedir):
            for dirpath,dirname,filenames in os.walk(basedir):
                for myfile in filenames:
                    try:
                        if myfile.lower().index(basename.lower()) == 0:
                            self.file_list.append(os.path.join(dirpath,myfile))
                    except ValueError:
                        pass

        self.files_found = len(self.file_list)
        if (self.verbose):
            print "Found %d files that match %s." % (self.files_found,basename)

    def getonlyone(self):
        if self.files_found == 0:
            return ""
        if self.files_found == 1:
            return self.file_list[0]
        else:
            nn = 0
            for myfile in self.file_list:
                print "%d) %s" % (nn, myfile)
                nn += 1

            choice = int(raw_input(">> "))
            return self.file_list[choice]

    file_list = []
    basedir = ""
    file_name = ""
    verbose = False
    files_found = 0

if __name__ == "__main__":
    basedir=argv[1]
    myfile=argv[2]
    bm=BestMatch(basedir,myfile,False,True)
    filename=bm.getonlyone()
    print "Using %s." % filename
