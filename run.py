import os
import sys

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)
os.chdir('n')
command = sys.argv[0]
if command in ('py', 'python', 'python3'):
  os.system(f'{command} main.py')
else:
  os.system('main.py')
