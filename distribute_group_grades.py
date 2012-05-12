#!/usr/bin/env python2

if __name__ == '__main__':
    """
    Accept a list of text files as input.  Each file must have a line begining "contributors:" followed by a comma separated list of github usernames
    A file for each user will be generated and stored in the output directory
    """

    from sys import stdin,stderr
    import re
    import argparse as ap
    import os
    verbose=False

    parser = ap.ArgumentParser(description="Update grade file")
    parser.add_argument('-o', '--output-dir',help="output directory") 
    parser.add_argument('-v', '--verbose',action='store_true',help="Be verbose")
    args = parser.parse_args()

    if args.verbose:
        verbose = args.verbose

    output_dir = os.curdir
    if args.output_dir:
        if os.path.isdir(args.output_dir):
            output_dir = os.path.realpath(args.output_dir)

    contributor = re.compile(r'^contribut[oe]rs:(.*)')

    for fname in stdin:
        fname = fname.rstrip()
        with open(fname, 'r') as f:
            data = f.read()
            f.seek(0)
            for line in f:
                m = contributor.search(line)
                if m:
                    contribs = m.groups(1)[0].split(',')
                    if (verbose):
                        stderr.write("For file %s found contributors %r\n" % (f.name, contribs))
                    for contrib in contribs:
                        contrib_file = os.path.join(output_dir, contrib.lstrip() + ".txt")
                        if (verbose):
                            stderr.write("\twriting file %r\n" % (contrib_file))
                        with open(contrib_file,'w') as of:
                            of.write(data)
