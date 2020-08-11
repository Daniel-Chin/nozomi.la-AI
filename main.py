import os
from ai import roll
from server import startServer, PORT
import webbrowser

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

startServer()
webbrowser.open(f'http://localhost:{PORT}')
roll()
