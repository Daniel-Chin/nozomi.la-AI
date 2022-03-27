DOCS = 'docs.shelve'
TAGS = 'tags.shelve'
IMGS = 'imgs'
OVERALL = 'overall.pickle'

import os
import os.path as os_path
from threading import Lock
import pickle
import shelve
from exclusive import Exclusive
from tag import TagInfo
from ai import ALL_RESPONSES, DEBUG
from doc import Doc

class Database:
  def __init__(self) -> None:
    self.lock = Lock()
    self.accLock = Lock()
    self.exclusive = Exclusive('exclusive')
  
  def __enter__(self):
    self.exclusive.acquire()
    self.docs = shelve.open(DOCS)
    self.tags = shelve.open(TAGS)
    self.docs.__enter__()
    self.tags.__enter__()
    os.makedirs(IMGS, exist_ok=True)
    return self
  
  def __exit__(self, *_):
    self.docs.__exit__(None, None, None)
    self.tags.__exit__(None, None, None)
    self.exclusive.release()
    return False

  def listAllDocs(self):
    return self.docs.keys()

  def listAllTags(self):
    return self.tags.keys()
  
  def listAllImgs(self):
    return os.listdir(IMGS)

  def saveImg(self, doc : Doc, imgs):
    # also writes `doc.local_filenames`
    doc.local_filenames = []
    for i, content in enumerate(imgs):
      filename = f'{doc.id}_{i}.{doc.img_type}'
      with open(os_path.join(IMGS, filename), 'wb') as f:
        f.write(content)
      doc.local_filenames.append(filename)

  def saveDoc(self, doc : Doc):
    self.docs[doc.id] = doc

  def loadDoc(self, doc_id):
    return self.docs[doc_id]

  def loadTagInfo(self, name):
    with self.lock:
      return self.tags[name]

  def saveTagInfo(self, tagInfo : TagInfo):
    with self.lock:
      self.tags[tagInfo.name] = tagInfo

  def accTagInfo(self, tag : TagInfo, response):
    with self.accLock:
      try:
        tagInfo = self.loadTagInfo(tag.name)
      except KeyError:
        self.saveNewTagInfo(tag)
        tagInfo = self.loadTagInfo(tag.name)
      tagInfo.n_responses[response] = tagInfo.n_responses.get(
        response, 0
      ) + 1
      self.saveTagInfo(tagInfo)

  def saveNewTagInfo(self, tag):
    tagInfo = TagInfo()
    tagInfo.parseTag(tag)
    self.saveTagInfo(tagInfo)

  def loadOverall(self):
    try:
      with self.lock:
        with open(OVERALL, 'rb') as f:
          return pickle.load(f)
    except FileNotFoundError:
      overall = {}
      for response in ALL_RESPONSES:
        overall[response] = 0
      self.saveOverall(overall)
      return overall

  def saveOverall(self, overall):
    with self.lock:
      with open(OVERALL, 'wb') as f:
        pickle.dump(overall, f)

  def accOverall(self, response):
    with self.accLock:
      overall = self.loadOverall()
      overall[response] = overall.get(response, 0) + 1
      self.saveOverall(overall)
    if DEBUG:
      print('overall', overall)

  def docExists(self, doc_id):
    return doc_id in self.docs

database = Database()
