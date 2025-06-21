import os
from threading import Lock

from parameters import *
from database import Database

def main():
  abspath = os.path.abspath(__file__)
  dname = os.path.dirname(abspath)
  os.chdir(dname)

  exitLock = Lock()
  exitLock.acquire()
  with Database(exitLock) as db:
    load = db.loadDoc
    def a(id):
      id = str(id)
      doc = load(id)
      for tag in doc.tags:
        if tag.type == 'artist':
          print(tag.name)

    from console import console
    console({**globals(), **locals()})
  print('db closed.')

if __name__ == '__main__':
  main()
