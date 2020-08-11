import os
from ai import roll
from server import startServer

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

startServer()
roll()
