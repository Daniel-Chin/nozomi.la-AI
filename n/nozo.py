MASTER_URL = 'https://n.nozomi.la/index.nozomi'
TAG_URL = 'https://n.nozomi.la/nozomi/%s.nozomi'

from parameters import FILTER
if FILTER:
  MASTER_URL = TAG_URL % FILTER
from time import time, sleep
from requests import get
from math import floor
from json import loads
from json.decoder import JSONDecodeError
from functools import lru_cache
from ai import POOL_SIZE, DEBUG
from threading import Thread, Lock
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

@lru_cache(maxsize=POOL_SIZE)
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

def getImage(url):
  r = get(url, headers = {
    'Host': 'i.nozomi.la',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:68.0) Gecko/20100101 Firefox/68.0',
    'Accept': 'image/webp,*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://nozomi.la/',
    'Connection': 'keep-alive',
  })
  assert r.content is not None
  return r.content

class ImageWorker(Thread):
  last_request = time()
  last_request_lock = Lock()

  def __init__(self, url):
    super().__init__()
    self.url = url
    self.lock = Lock()
    self.result = None
  
  def run(self):
    with __class__.last_request_lock:
      my_time = max(time(), __class__.last_request + 2)
      __class__.last_request = my_time
    sleep(max(0, my_time - time()))
    if DEBUG:
      print('ImageWorker starts...')
    content = getImage(self.url)
    with self.lock:
      self.result = content
    g.printJobs()
    self.todo()
    if DEBUG:
      print('ImageWorker ends.')
  
  def check(self):
    with self.lock:
      return self.result
