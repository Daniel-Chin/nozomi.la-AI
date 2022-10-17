MASTER_URL = 'https://n.nozomi.la/index.nozomi'
TAG_URL = 'https://n.nozomi.la/nozomi/%s.nozomi'

from parameters import FILTER, JOB_POOL_THROTTLE
if FILTER:
  MASTER_URL = TAG_URL % FILTER
from time import time, sleep
from requests import get, Response
from json import loads
from json.decoder import JSONDecodeError
from functools import lru_cache
from ai import BATCH_SIZE, DEBUG
from threading import Thread, Lock
import concurrent.futures as futures
from requests_futures.sessions import FuturesSession
from server import g

class PageOutOfRange(Exception): pass

def decode_nozomi(n):
  try:
    for i in range(0, len(n), 4):
      yield str((n[i] << 24) + (n[i+1] << 16) + (n[i+2] << 8) + n[i+3])
  except IndexError:
    raise PageOutOfRange()

def askMaster(start, end):
  r = get(MASTER_URL, headers={
    'Host': 'n.nozomi.la',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:68.0) Gecko/20100101 Firefox/68.0',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://nozomi.la/',
    'Range': f'bytes={start * 4}-{end * 4 - 1}',
    'Origin': 'https://nozomi.la',
    'Connection': 'keep-alive',
    'TE': 'Trailers',
  })
  
  post_ids = list(decode_nozomi(r.content))
  return post_ids

def urlJSON(doc_id):
  a = doc_id[-1]
  b = doc_id[-3:-1]
  return f'https://j.nozomi.la/post/{a}/{b}/{doc_id}.json'

@lru_cache(maxsize=BATCH_SIZE)
def getJSON(doc_id):
  url = urlJSON(doc_id)
  r = get(url, headers = {
    'Host': 'j.nozomi.la',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:68.0) Gecko/20100101 Firefox/68.0',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://nozomi.la/',
    'Origin': 'https://nozomi.la',
    'Connection': 'keep-alive',
    'TE': 'Trailers',
  })
  if '404 Not Found' in r.text:
    print(f'{doc_id} has 404 not found')
    return None
  try:
    return loads(r.text)
  except JSONDecodeError as e:
    print('json not formatted.')
    print(r.text)
    raise e

def imageHeaders():
  return {
    'Host': 'i.nozomi.la',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:68.0) Gecko/20100101 Firefox/68.0',
    'Accept': 'image/webp,*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://nozomi.la/',
    'Connection': 'keep-alive',
  }

class ImageWorker(Thread):
  last_request = time()
  last_request_lock = Lock()

  def __init__(self, url, session: FuturesSession):
    super().__init__()
    self.url = url
    self.session = session
    self.lock = Lock()
    self.result = None
    self.go_on = True
  
  def close(self):
    self.go_on = False
  
  def sleep(self, t):
    while True:
      if not self.go_on:
        return
      if t < .5:
        sleep(t)
        break
      else:
        sleep(.5)
        t -= .5
  
  def run(self):
    with __class__.last_request_lock:
      my_time = max(time(), __class__.last_request + JOB_POOL_THROTTLE)
      __class__.last_request = my_time
    self.sleep(max(0, my_time - time()))
    if self.go_on:
      if DEBUG:
        print('going on...')
    else:
      return
    if DEBUG:
      print('ImageWorker starts...')
    try:
      future: futures.Future = self.session.get(
        self.url, headers=imageHeaders(), 
      )
    except RuntimeError as e:
      print('warning:', e, *e.args)
      return
    while True:
      try:
        response: Response = future.result(timeout=1)
      except futures.TimeoutError:
        if not self.go_on:
          return
      else:
        break
    with self.lock:
      self.result = response.content
    g.printJobs()
    self.todo()
    if DEBUG:
      print('ImageWorker ends.')
  
  def check(self):
    with self.lock:
      return self.result
