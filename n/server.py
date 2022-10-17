from __future__ import annotations

import json
from threading import Thread

from myhttp import Server, OneServer, respond, Request

from parameters import *
from shared import *
from database import Database
from doc import Doc
from imagePool import ImagePool, PoolItem

trusted_ip = []

class MyOneServer(OneServer):
  def __init__(self, addr, socket, parent: Server):
    super().__init__(addr, socket, parent)
    self.parent: MyServer
  
  def handle(self, request: Request):
    if request.target == '/':
      with open('index.html', 'rb') as f:
        respond(self.socket, f.read())
    elif request.target in ['/styles.css', '/scripts.js', '/welcome.html']:
      with open(request.target.lstrip('/'), 'rb') as f:
        respond(self.socket, f.read())
    elif request.target.split('?')[0] == '/next':
      def callback(poolItem: PoolItem):
        respond(self.socket, json.dumps({
          'doc_id': poolItem.doc.id, 
          'mode': poolItem.mode,
          'artists': poolItem.doc.getArtists(), 
        }).encode())
      self.parent.imagePool.consume(callback)
    elif request.target.split('?')[0] == '/img':
      param = request.target.split('?')[1]
      doc_id = param.lstrip('doc_id=')
      def callback(poolItem: PoolItem):
        respond(self.socket, poolItem.image)
      self.parent.imagePool.consume(callback)
    elif request.target.split('?')[0] == '/response':
      params = request.target.split('?')[1].split('&')
      doc_id = params[0].lstrip('doc_id=')
      response = params[1].lstrip('response=')
      poolItem, todo = self.parent.imagePool.pop()
      doc = poolItem.doc
      assert doc_id == doc.id
      respond(self.socket, b'ok')
      self.recordResponse(response, doc, poolItem.image)
      todo()
    elif request.target in ['/favicon.ico']:
      pass
    else:
      print('Unknown request:', request.target)
  
  def recordResponse(self, response: str, doc: Doc, image: bytes):
    if self.parent.db.doesDocExist(doc.id):
      raise Exception('Error 2049284234')
    doc.response = response
    self.parent.db.saveDoc(doc)
    self.parent.db.accOverall(response)
    for tag in doc.tags:
      self.parent.db.accTagInfo(tag, response)
      if DEBUG:
        print(self.parent.db.loadTagInfo(tag.name))
    print(doc)
    if response == RES_SAVE:
      Thread(target=self.parent.db.saveImg, args=[
        doc, [image], 
      ]).start()

class MyServer(Server):
  def __init__(
    self, imagePool: ImagePool, db: Database, 
    my_OneServer=..., port=80, listen=1, accept_timeout=0.5, 
  ):
    super().__init__(my_OneServer, port, listen, accept_timeout)
    self.imagePool = imagePool
    self.db = db

  def onConnect(self, addr):
    global trusted_ip
    if not trusted_ip:
      trusted_ip = addr[0]
    elif addr[0] != trusted_ip:
      print('SOMEONE IS ATTACKING!', addr)
      self.close()

def startServer(imagePool, db):
  server = MyServer(
    imagePool, db, MyOneServer, PORT, name='localhost', 
  )
  server.start()
  return server
