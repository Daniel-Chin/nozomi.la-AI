import os
from threading import Lock

import webbrowser
from requests_futures.sessions import FuturesSession

import myhttp

from parameters import *
from imagePool import ImagePool
from nozo import ImageRequester
from server import startServer
from database import Database
import ai

def main():
  abspath = os.path.abspath(__file__)
  dname = os.path.dirname(abspath)
  os.chdir(dname)

  if not DEBUG:
    openBrowser()
  
  exitLock = Lock()
  exitLock.acquire()
  imagePool = ImagePool()
  with Database().context() as db:
    server = startServer(imagePool, db)
    with FuturesSession(max_workers=JOB_POOL_SIZE) as session:
      imageRequester = ImageRequester(session, exitLock, imagePool)
      hIL = ai.HumanInLoop(session, imageRequester, db)
      imagePool.activate(JOB_POOL_SIZE, lambda : next(hIL))
      try:
        while True:
          if input('Enter "q" to quit.').lower() == 'q':
            break
      finally:
        exitLock.release()
        server.close()
        print('server closed.')
    print('FuturesSession closed.')
  print('db closed.')

def openBrowser():
  myhttp.myLogger.verbose = False
  url = f'http://localhost:{PORT}/'
  if not EXPERT:
    url += 'welcome.html'
  webbrowser.open(url)

if __name__ == '__main__':
  main()
