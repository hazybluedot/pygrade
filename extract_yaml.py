#!/usr/bin/env python2

import yaml
import sys
import argparse
import fileinput
import re

class YParser:
    yaml_string = ""

    def __init__(self,indent=0):
        #sys.stderr.write("{}: Initialing YAML parser thingy\n".format(self))
        self.yaml_string = ""
        self.indent=indent

    def on_yaml(self,line):
        #sys.stderr.write("{}: appending line to thingy\n".format(self))
        self.yaml_string += line

    def reset(self, indent=0):
        self.__init__(indent)

    def done(self):
        #sys.stderr.write("{}: converting to yaml: {}\n".format(self,self.yaml_string))
        return (yaml.load(self.yaml_string), self.indent)

if __name__=='__main__':

    parser = argparse.ArgumentParser("Extract YAML blocks from text file")
    parser.add_argument("-v","--verbose", action='store_true', help="be verbose")
    parser.add_argument("files", nargs='*')
    args = parser.parse_args()

    yparser = YParser()
    blocks = []
    context = "default"
    for line in fileinput.input(args.files):
        if context == "default":
            m = re.match(r'((\s*)<!--(%yaml|-)[\s]+).*', line)
            if m:
                #print "line {}: Processing lines as yaml".format(lineno)
                (blank, match, line) = line.partition(m.groups()[0])
                indent_level = len(m.groups()[1])
                yparser.reset(indent_level)
                context = 'yaml'
                blocks.append({'lineno': fileinput.lineno(), 'indent': indent_level, 'obj': {}})
                #sys.stdout.write(yaml.dump(blocks[-1]))

        if context == 'yaml':
            m = re.search(r'(\s*)-->', line)
            if m:
                #print "line{0}: Processing lines as default".format(lineno)
                (blank, match, line) = line.partition('-->')
                (myaml, block_indent) = yparser.done()
                blocks[-1]['obj'] = myaml

                if args.verbose:
                    sys.stderr.write("stting block_indent={0}\n".format(block_indent))
                if args.verbose:
                    sys.stderr.write("{0}\n".format(myaml))
                context = 'default'

        if context == 'yaml':
            try:
                yparser.on_yaml(line)
            except yaml.scanner.ScannerError as e:
                sys.stderr.write("ScannerError on line {0}: {1}\n".format(fileinput.lineno(), line))

    sys.stdout.write(yaml.dump(blocks))
