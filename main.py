import os
from ai import roll, DEBUG
from server import startServer, PORT
import webbrowser
import myhttp

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)
if not DEBUG:
  myhttp.myLogger.verbose = False
  webbrowser.open(f'http://localhost:{PORT}/welcome.html')
startServer()
roll()
