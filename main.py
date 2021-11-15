from subprocess import *

def generate_nodes():
      pass

def generate_identities():
      pass

cmd =['gnome-terminal',
      '--tab', '-e', 'python  ./node.py 1',
      '--tab', '-e', 'python  ./node.py 2',
      '--tab', '-e', 'python  ./node.py 3']
call(cmd)



