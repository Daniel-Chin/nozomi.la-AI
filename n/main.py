import os
from parameters import DEBUG, PORT
from ai import roll, setBlackList
from server import startServer
import webbrowser
import myhttp
from database import database

def main():
  abspath = os.path.abspath(__file__)
  dname = os.path.dirname(abspath)
  os.chdir(dname)
  with database:
    parseBlacklist()
    if not DEBUG:
      myhttp.myLogger.verbose = False
      webbrowser.open(f'http://localhost:{PORT}/welcome.html')
    server = startServer()
    try:
      roll()
    except KeyboardInterrupt:
      pass
    finally:
      server.close()
      print('server closed.')
  print('db closed.')

def parseBlacklist():
  blacklist = []
  try:
    with open('blacklist.txt', 'r', encoding='utf-8') as f:
      for line in f:
        line = line.strip()
        if line:
          try:
            database.loadTagInfo(line)
          except KeyError:
            raise ValueError(f'"{line}" is not a valid tag name, or it is not cached yet.')
          else:
            blacklist.append(line)
  except FileNotFoundError:
    with open('blacklist.txt', 'w') as f:
      f.write('\n')
  setBlackList(blacklist)

if __name__ == '__main__':
    main()
