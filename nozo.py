from requests import get
from math import floor
from json import loads

def askMaster(start, end):
  r = get('https://n.nozomi.la/index.nozomi', headers={
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
  buffer = r.content
  result = []
  for i in range(len(buffer) // 4):
    result.append(str(int.from_bytes(
      buffer[i*4 : (i+1)*4], 'big', signed=False,
    )))
  return result

def urlJSON(doc_id):
  a = doc_id[-1]
  b = doc_id[-3:-1]
  return f'https://j.nozomi.la/post/{a}/{b}/{doc_id}.json'

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
  return loads(r.text)

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
  return r.content
