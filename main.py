import os
from ai import roll, DEBUG, setBlackList
from server import startServer, PORT
import webbrowser
import myhttp
import database

def main():
  abspath = os.path.abspath(__file__)
  dname = os.path.dirname(abspath)
  os.chdir(dname)
  database.init()
  parseBlacklist()
  if not DEBUG:
    myhttp.myLogger.verbose = False
    webbrowser.open(f'http://localhost:{PORT}/welcome.html')
  startServer()
  roll()

def parseBlacklist():
  blacklist = []
  try:
    with open('blacklist.txt', 'r') as f:
      for line in f:
        line = line.strip()
        if line:
          try:
            database.loadTagInfo(line)
          except FileNotFoundError:
            raise ValueError(f'"{line}" is not a valid tag name, or it is not cached yet.')
          else:
            blacklist.append(line)
  except FileNotFoundError:
    with open('blacklist.txt', 'w+') as f:
      f.write('\n')
  setBlackList(blacklist)

main()
