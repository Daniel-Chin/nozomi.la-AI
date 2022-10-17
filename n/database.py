import os
from os import path
from contextlib import contextmanager
from threading import Lock
import pickle
import shelve
from typing import Dict, List

from exclusive import Exclusive

from shared import *
from parameters import *
from tag import Tag, TagInfo
from doc import Doc

DOCS = 'docs.shelve'
TAGS = 'tags.shelve'
IMGS = 'imgs'
OVERALL = 'overall.pickle'

class Database:
  def __init__(self, exitLock: Lock) -> None:
    self.lock = Lock()
    self.accLock = Lock()
    self.exclusive = Exclusive('exclusive')
    self.exitLock = exitLock
  
  @contextmanager
  def context(self):
    with self.exclusive, \
         shelve.open(DOCS) as self._docs, \
         shelve.open(TAGS) as self._tagInfos:
      os.makedirs(IMGS, exist_ok=True)
      try:
        yield self
      finally:
        self.lock.acquire(timeout=1)
    self.lock.release()
  
  @contextmanager
  def okAfterClose(self):
    try:
      yield self
    except ValueError as e:
      if e.args[0] == 'invalid operation on closed shelf':
        assert not self.exitLock.locked
      else:
        raise e
  
  def listAllDocs(self):
    with self.okAfterClose():
      return self._docs.keys()

  def listAllTagInfos(self):
    with self.okAfterClose():
      return self._tagInfos.keys()
  
  def listAllImgs(self):
    with self.okAfterClose():
      return os.listdir(IMGS)

  def doesDocExist(self, doc_id: str):
    with self.okAfterClose():
      return doc_id in self._docs

  def saveImg(self, doc: Doc, imgs: List[bytes]):
    # also writes `doc.local_filenames`
    doc.local_filenames = []
    for i, content in enumerate(imgs):
      filename = f'{doc.id}_{i}.{doc.img_type}'
      with open(path.join(IMGS, filename), 'wb') as f:
        f.write(content)
      doc.local_filenames.append(filename)

  def saveDoc(self, doc: Doc):
    with self.okAfterClose():
      with self.lock:
        self._docs[doc.id] = doc

  def loadDoc(self, doc_id) -> Doc:
    with self.okAfterClose():
      return self._docs[doc_id]

  def saveTagInfo(self, tagInfo: TagInfo):
    with self.okAfterClose():
      with self.lock:
        self._tagInfos[tagInfo.tag.name] = tagInfo

  def loadTagInfo(self, name: str) -> TagInfo:
    with self.okAfterClose():
      with self.lock:
        return self._tagInfos[name]

  def accTagInfo(self, tag: Tag, response: str):
    with self.accLock:
      try:
        tagInfo: TagInfo = self.loadTagInfo(tag.name)
      except KeyError:
        self.saveTagInfo(TagInfo(tag))
        tagInfo: TagInfo = self.loadTagInfo(tag.name)
      tagInfo.responses[response] = tagInfo.responses.get(
        response, 0, 
      ) + 1
      self.saveTagInfo(tagInfo)

  def saveOverall(self, overall: Dict[str, int]):
    with self.lock:
      with open(OVERALL, 'wb') as f:
        pickle.dump(overall, f)

  def loadOverall(self) -> Dict[str, int]:
    try:
      with self.lock:
        with open(OVERALL, 'rb') as f:
          return pickle.load(f)
    except FileNotFoundError:
      overall = {}
      self.saveOverall(overall)
      return overall

  def accOverall(self, response: str):
    with self.accLock:
      overall = self.loadOverall()
      overall[response] = overall.get(response, 0) + 1
      self.saveOverall(overall)
    if DEBUG:
      print(f'{overall = }')
