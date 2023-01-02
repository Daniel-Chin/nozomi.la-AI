from os import path
from threading import Lock
from typing import List
from requests import get

from tqdm import tqdm

from shared import *
from database import Database
from doc import Doc
from nozo import IMAGE_HEADERS

def getImage(url: str):
  response = get(url, headers=IMAGE_HEADERS)
  return response.content

def main():
  exitLock = Lock()
  exitLock.acquire()
  with Database(exitLock) as database:
    all_imgs = [x.split('_')[0] for x in database.listAllImgs()]
    print(len(all_imgs), 'images on disk')
    all_docs = database.listAllDocs()
    print(len(all_docs), 'docs viewed')
    wows: List[Doc] = []
    saves: List[Doc] = []
    for doc_id in tqdm(all_docs, 'filtering'):
      doc: Doc = database.loadDoc(doc_id)
      if doc.response == RES_SAVE:
        saves.append(doc)
      elif doc.response == RES_WOW:
        wows.append(doc)
    lacks = set([x.id for x in saves]) - set(all_imgs)
    if lacks:
      print('Document response is SAVE but image not on disk:')
      [print(x) for x in lacks]
      print('Download now?')
      if input('y/n ').lower() == 'y':
        for id in lacks:
          doc = [x for x in saves if x.id == id][0]
          print('Getting', doc.id, '...')
          imgs = [getImage(x) for x in doc.img_urls]
          database.saveImg(doc, imgs)
        print('Complete.')
    p = input('Input path to download to: ')
    fns = [(path.join(p, doc.id) + '.' + doc.img_type, doc) for doc in wows]
    missing_fns = [x for x in fns if not path.exists(x[0])]
    print(f'There are {len(fns)} wow ones. {len(missing_fns)} are not on disk.')
    for fn, doc in tqdm(missing_fns):
      img = getImage(doc.img_urls[0])
      with open(fn, 'wb') as f:
        f.write(img)
    input('Ok. Press enter to quit...')

main()
