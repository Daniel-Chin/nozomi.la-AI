import os
from threading import Lock, Thread

import webbrowser
from requests_futures.sessions import FuturesSession

import myhttp

from parameters import *
from imagePool import ImagePool
from nozo import ImageRequester
from server import startServer
from database import Database
import ai
from sele_browser import SeleBrowser
from terminal_response_interface import interactive

def main():
  abspath = os.path.abspath(__file__)
  dname = os.path.dirname(abspath)
  os.chdir(dname)

  openBrowser()
  
  exitLock = Lock()
  exitLock.acquire()
  with SeleBrowser().context() as seleB:
    imagePool = ImagePool(seleB)
    with Database(exitLock) as db:
      server = startServer(imagePool, db)
      with FuturesSession(max_workers=MAX_WORKERS) as session:
        imageRequester = ImageRequester(
          session, exitLock, imagePool, 
        )
        hIL = ai.HumanInLoop(
          session, imageRequester, db, exitLock, 
        )
        aiLock = Lock()
        def request():
          with aiLock:
            return next(hIL)
        def activate():
          print('Activating...')
          imagePool.activate(JOB_POOL_SIZE, request)
        Thread(target=activate, name='activate').start()
        try:
          if IMG_DOWNLOAD_IN_BROWSER:
            interactive(server, seleB)
          else:
            while True:
              print('Enter "q" to quit.')
              if input().lower() == 'q':
                break
        finally:
          exitLock.release()
          print('exitLock released.')
          server.close()
          print('server closed.')
      print('FuturesSession closed.')
  print('db closed.')

def openBrowser():
  myhttp.myLogger.verbose = False
  url = f'http://localhost:{PORT}/'
  url += 'welcome.html'
  if EXPERT:
    print(url)
    return
  webbrowser.open(url)

if __name__ == '__main__':
  main()
