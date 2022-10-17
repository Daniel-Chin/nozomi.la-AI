import os

import webbrowser
from requests_futures.sessions import FuturesSession

import myhttp
from n.imagePool import ImagePool

from parameters import *
from imagePool import ImagePool
import ai
from server import startServer
from database import Database

def main():
  abspath = os.path.abspath(__file__)
  dname = os.path.dirname(abspath)
  os.chdir(dname)
  imagePool = ImagePool(...)
  with Database().context() as db:
    if not DEBUG:
      myhttp.myLogger.verbose = False
      url = f'http://localhost:{PORT}/'
      if not EXPERT:
        url += 'welcome.html'
      webbrowser.open(url)
    server = startServer(imagePool, db)
    with FuturesSession(max_workers=JOB_POOL_SIZE) as session:
      try:
        roll(session)
      except KeyboardInterrupt:
        pass
      finally:
        g.close()
        server.close()
        print('server closed.')
    print('FuturesSession closed.')
  print('db closed.')

if __name__ == '__main__':
    main()
