from ai import RES_SAVE, RES_WOW
from database import listAll, loadDoc, IMGS, DOCS, saveImg
from doc import Doc
from jdt import Jdt
from nozo import getImage
import os.path as osp

def main():
  all_imgs = [x.split('_')[0] for x in listAll(IMGS)]
  print(len(all_imgs), 'images on disk')
  all_docs = listAll(DOCS)
  print(len(all_docs), 'docs viewed')
  wows = []
  saves = []
  with Jdt(len(all_docs), 'filtering', UPP=4) as j:
    for doc_id in all_docs:
      j.acc()
      doc: Doc = loadDoc(doc_id)
      if doc.response == RES_SAVE:
        saves.append(doc)
      elif doc.response == RES_WOW:
        wows.append(doc)
  if all_imgs != saves:
    lacks = set([x.id for x in saves]) - set(all_imgs)
    print('Document response is SAVE but image not on disk:')
    [print(x) for x in lacks]
  print('Download now?')
  if input('y/n ').lower() == 'y':
    for id in lacks:
      doc = [x for x in saves if x.id == id][0]
      print('Getting', doc.id, '...')
      imgs = [getImage(x) for x in doc.img_urls]
      saveImg(doc, imgs)
    print('Complete.')
  print('All wow ones:')
  [print(x.id) for x in wows]
  p = input('Input path to download to: ')
  with Jdt(len(wows)) as j:
    for doc in wows:
      j.acc()
      fn = osp.join(p, doc.id)
      if osp.exists(fn):
        print()
        print('Skipping', doc.id, '. Already exists. ')
      else:
        img = getImage(doc.img_urls[0])
        with open(fn + '.' + doc.img_type, 'wb+') as f:
          f.write(img)
    input('Ok. Press enter to quit...')

main()
