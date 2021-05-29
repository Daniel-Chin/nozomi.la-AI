DOCS = 'docs'
IMGS = 'imgs'
TAGS = 'tags'
OVERALL = 'overall.pickle'

import os
from nozo import getImage
import pickle
from tag import TagInfo
from ai import ALL_RESPONSES, DEBUG
import os.path as os_path
from threading import Lock

fileLock = Lock()
accLock = Lock()

def listAll(x):
  return os.listdir(x)

def saveImg(doc, imgs):
  # also writes `doc.local_filenames`
  doc.local_filenames = []
  for i, content in enumerate(imgs):
    filename = f'{doc.id}_{i}.{doc.img_type}'
    with open(f'{IMGS}/{filename}', 'wb+') as f:
      f.write(content)
    doc.local_filenames.append(filename)

def saveDoc(doc):
  with open(f'{DOCS}/{doc.id}', 'wb+') as f:
    pickle.dump(doc, f)

def loadDoc(doc_id):
  with open(f'{DOCS}/{doc_id}', 'rb') as f:
    return pickle.load(f)

def legalizeTagName(name):
  result = ''
  for char in name:
    if char.isalnum() or char == '_':
      result += char
    else:
      result += f'chr({ord(char)})'
  return result

def loadTagInfo(name):
  with fileLock:
    with open(f'{TAGS}/{legalizeTagName(name)}', 'rb') as f:
      return pickle.load(f)

def saveTagInfo(tagInfo):
  with fileLock:
    if tagInfo.name == 'artist':
      print("saveTagInfo: tagInfo.name == 'artist'")
      from console import console
      console({**locals(), **globals()})
    with open(f'{TAGS}/{legalizeTagName(tagInfo.name)}', 'wb+') as f:
      pickle.dump(tagInfo, f)

def accTagInfo(tag, response):
  with accLock:
    try:
      tagInfo = loadTagInfo(tag.name)
    except FileNotFoundError:
      saveNewTagInfo(tag)
      tagInfo = loadTagInfo(tag.name)
    tagInfo.n_responses[response] = tagInfo.n_responses.get(
      response, 0
    ) + 1
    saveTagInfo(tagInfo)

def saveNewTagInfo(tag):
  tagInfo = TagInfo()
  tagInfo.parseTag(tag)
  try:
    saveTagInfo(tagInfo)
  except FileNotFoundError:
    raise Exception('Tag name contains too many non-ascii characters!')

def loadOverall():
  try:
    with fileLock:
      with open(OVERALL, 'rb') as f:
        return pickle.load(f)
  except FileNotFoundError:
    overall = {}
    for response in ALL_RESPONSES:
      overall[response] = 0
    saveOverall(overall)
    return overall

def saveOverall(overall):
  with fileLock:
    with open(OVERALL, 'wb+') as f:
      pickle.dump(overall, f)

def accOverall(response):
  overall = loadOverall()
  overall[response] = overall.get(response, 0) + 1
  saveOverall(overall)
  if DEBUG:
    print('overall', overall)

def doExist(x, name):
  return os_path.isfile(x + '/' + name)

def init():
  for i in [DOCS, TAGS, IMGS]:
    if not os_path.isdir(i):
      os.mkdir(i)
