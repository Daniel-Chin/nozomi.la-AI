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
        saveImg(doc, imgs)
      print('Complete.')
  p = input('Input path to download to: ')
  fns = [(osp.join(p, doc.id) + '.' + doc.img_type, doc) for doc in wows]
  missing_fns = [x for x in fns if not osp.exists(x[0])]
  print(f'There are {len(fns)} wow ones. {len(missing_fns)} are not on disk.')
  with Jdt(len(missing_fns)) as j:
    for fn, doc in missing_fns:
      j.acc()
      img = getImage(doc.img_urls[0])
      with open(fn, 'wb+') as f:
        f.write(img)
  input('Ok. Press enter to quit...')

main()
