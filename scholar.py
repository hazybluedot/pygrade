import shutil
import os
import re
import ast

class ScholarArchive:
   def __init__(self, path):
      self.path = os.path.realpath(path)
      self.grades_file = os.path.join(self.path, 'grades.csv')
      if not os.path.isfile(self.grades_file):
         raise ScholarError("{}: can't find grades file.  Are you in the right directory?\n".format(grades_file))
      self.students = {}
      for mdir in os.listdir(self.path):
         m = re.search(r'[\w, -]+\((\w+)\)', mdir)
         if m:
            student = m.groups(0)[0]
            self.students[student] = os.path.join(self.path, mdir)
         else:
            pass #sys.stderr.write("Skipping {}: Could not determine student\n".format(mdir))

   def comments_file(self,pid):
      return os.path.join(self.students[pid], 'comments.txt')

   def feedback_attachments(self,pid):
      return os.path.join(self.students[pid], 'Feedback Attachment(s)')

   def copy_to_feedback(self,pid,src):
      shutil.copy(src, self.feedback_attachments(pid))

def open_homework(f):
   try:
      homework = ast.literal_eval(f.read())
      f.close()
   except SyntaxError as e:
       f.close()
       sys.stderr.write("{}: Problem parsing file. {}\n".format(args.f.name, e))
       sys.exit(1)
   else:
       scholar_path = os.path.join(os.getcwd(), homework['name'])
       scholar = ScholarArchive(scholar_path)
       return (homework, scholar)

if __name__=='__main__':
    pass
