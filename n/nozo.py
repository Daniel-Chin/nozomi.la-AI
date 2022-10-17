from time import time, sleep
from requests import get, Response
from functools import lru_cache
from threading import Lock, Thread
import concurrent.futures as futures
from json import loads
from json.decoder import JSONDecodeError

from requests_futures.sessions import FuturesSession

from parameters import *
from doc import Doc
from imagePool import ImagePool, PoolItem

MASTER_URL = 'https://n.nozomi.la/index.nozomi'
TAG_URL = 'https://n.nozomi.la/nozomi/%s.nozomi'
IMAGE_HEADERS = {
  'Host': 'i.nozomi.la',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:68.0) Gecko/20100101 Firefox/68.0',
  'Accept': 'image/webp,*/*',
  'Accept-Language': 'en-US,en;q=0.5',
  'Accept-Encoding': 'gzip, deflate, br',
  'Referer': 'https://nozomi.la/',
  'Connection': 'keep-alive',
}

class PageOutOfRange(Exception): pass

def decodeNozomi(n, /):
  try:
    for i in range(0, len(n), 4):
      yield str((n[i] << 24) + (n[i+1] << 16) + (n[i+2] << 8) + n[i+3])
  except IndexError:
    raise PageOutOfRange()

def askMaster(start: int, end: int):
  if FILTER:
    url = TAG_URL % FILTER
  else:
    url = MASTER_URL
  r = get(url, headers={
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
  
  post_ids = list(decodeNozomi(r.content))
  return post_ids

def urlJSON(doc_id):
  a = doc_id[-1]
  b = doc_id[-3:-1]
  return f'https://j.nozomi.la/post/{a}/{b}/{doc_id}.json'

@lru_cache(maxsize = BATCH_SIZE * 3)
def getJSON(doc_id: str):
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
  if r.status_code == 404:
    print(f'{doc_id} has 404 not found')
    return None
  try:
    return loads(r.text)
  except JSONDecodeError as e:
    print('json not well formed.')
    print(r.text)
    raise e

class ImageRequester:
  def __init__(
    self, session: FuturesSession, exitLock: Lock, 
    imagePool: ImagePool, 
  ) -> None:
    self.session = session
    self.exitLock = exitLock
    self.imagePool = imagePool

    self.last_request = time()
    self.lock = Lock()

  def sched(self, poolItem: PoolItem):
    url = poolItem.doc.img_urls[0]
    with self.lock:
      my_time = max(time(), self.last_request + JOB_POOL_THROTTLE)
      self.last_request = my_time
    dt = max(0, my_time - time())
    if dt == 0:
      self._do(url, 0)
    else:
      Thread(target=self._do, args=[url, dt, poolItem]).start()
  
  def _do(self, url: str, wait_time: float, poolItem):
    if wait_time != 0:
      if self.exitLock.acquire(timeout=wait_time):
        self.exitLock.release()
        return
    if DEBUG:
      print('Requesting image...')
    try:
      future: futures.Future = self.session.get(
        url, headers=IMAGE_HEADERS, 
      )
    except RuntimeError as e:
      print('warning:', e, *e.args)
      return
    future.add_done_callback(
      lambda x : self.onReceive(x, poolItem)
    )
    # g.printJobs()
    # self.todo()
  
  def onReceive(
    self, future: futures.Future[Response], 
    poolItem: PoolItem, 
  ):
    if self.exitLock.acquire():
      self.exitLock.release()
      return
    poolItem.image = future.result().content
    self.imagePool.receive(poolItem)
