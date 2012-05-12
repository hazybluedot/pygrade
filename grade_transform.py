#!/usr/bin/env python2

from os import path
import re
import csv
from sys import stderr

def extract_grade(data):
    grade = None
    for line in data:
        m = re.findall(r'\[([\d]+)\].*', line)
        if m:
            grade = m[0]
    return grade

def make_student_dir(record):
    return ("%s, %s(%s)" % (record[0], record[1], record[2]))

class StudentData:
    def __init__(self, aka_file, scholar_archive):
        self.reader = csv.reader(aka_file)
        self.github_dict = {}
        header = self.reader.next()
        for row in self.reader:
            self.github_dict[row[3]] = row[0:3]

        if not path.isdir(scholar_archive):
            raise Exception('%s: Could not open Scholar archive' % scholar_archive)
        else:
            self.archive_dir = scholar_archive
            grades_file = path.join(self.archive_dir, 'grades.csv')
            with open(grades_file, 'r') as f:
                self.grades_header = [f.next() for x in xrange(3)]
                self.grades_file = grades_file
                grades_csv = csv.reader(f)
                #grades_csv.next()
                self.grades = []
                for record in grades_csv:
                    self.grades.append(record)

    def get_id_by_username(self,username):
        try:
            record = self.github_dict[username]
            return record
        except KeyError:
            stderr.write("KeyError: %s\n" % username)
            return None

    def update_grade(self,args,grade):
        if not grade == None:
            try:
                grade = float(grade)
                for record in self.grades:
                    if len(record) > 0 and args[2] == record[1]:
                        record[4] = grade
            except ValueError:
                return False

    def add_comment(self,comment_file):
        comment_file = comment_file.rstrip()
        with open(comment_file, 'r') as f:
            (basename, ext) = path.splitext(path.basename(comment_file))
            record = self.get_id_by_username(basename)
            if not record == None:
                comments = f.read()
                f.seek(0)
                grade = extract_grade(f)
                comments_path = path.join(self.archive_dir,make_student_dir(record),'comments.txt')
                self.update_grade(record,grade)
                try:
                    comments_file = open(comments_path, 'w')
                    comments_file.write(comments)
                except IOError:
                    stderr.write("%s: Could not open for writing\n" % comments_path)

    def print_grades(self):
        for record in self.grades:
            print record

    def write_grades(self):
        temp_file = self.grades_file + ".tmp"
        with open(temp_file, 'wt') as f:
            writer = csv.writer(f)
            header = ('').join(self.grades_header)
            f.write(header)
            writer.writerows(self.grades)


if __name__ == "__main__":
    from sys import argv,stdin
    
    verbose = True
    with open(argv[1], 'r') as f:
        sd = StudentData(f,argv[2])
        
        for line in stdin:
            sd.add_comment(line)

        sd.write_grades()
