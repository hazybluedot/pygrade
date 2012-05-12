#!/usr/bin/env python2

if __name__ == '__main__':
    from sys import stdin,stderr
    import subprocess, re, tarfile, os

    for archive in stdin:
        ftype = subprocess.check_output(["file", "-ib", archive.rstrip()])
        archive = archive.rstrip()
        try:
            tar = tarfile.open(archive)
        except IOError,e
            break
        parts = archive.split("_")
        if len(parts) < 4:
            stderr.write("%r\n" % parts)
        else:
            student_directory="%s, %s(%s)" % (parts[0], parts[1], parts[2])
            try:
                os.mkdir(student_directory)
            except OSError,e:
                stderr.write("%r" % e)
                stderr.write("On directory: %s" % student_directory)
            
            try:
                tar.extractall(student_directory)
            except OSError,e:
                stderr.write("%r\n" % e)
                stderr.write("Archive: %s, output directory: %s\n" % (archive,student_directory))
            #print student_directory
        #tar.list()
        tar.close()            
