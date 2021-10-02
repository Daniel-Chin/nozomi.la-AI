from parameters import JOB_POOL_SIZE, PORT

from threading import Semaphore, Lock, Thread
from myhttp import Server, OneServer, respond
from collections import namedtuple
import json
from ai import ALL_RESPONSES

trusted_ip = []

Job = namedtuple('Job', ['doc', 'imageWorker', 'mode'])

class G:
  def __init__(self):
    self.conSem = Semaphore(JOB_POOL_SIZE)
    self.proSem = Semaphore(JOB_POOL_SIZE)
    self.jobsLock = Lock()
    for _ in range(JOB_POOL_SIZE):
      self.conSem.acquire()
    self.jobs = []
  
  def printJobs(self):
    print('jobs', ['I' if x.imageWorker.result is not None else '_' for x in self.jobs])

g = G()

from ai import recordResponse

class MyOneServer(OneServer):
  def handle(self, request):
    if request.target == '/':
      with open('index.html', 'rb') as f:
        respond(self.socket, f.read())
    elif request.target in ['/styles.css', '/scripts.js', '/welcome.html']:
      with open(request.target.lstrip('/'), 'rb') as f:
        respond(self.socket, f.read())
    elif request.target == '/':
      with open('index.html', 'rb') as f:
        respond(self.socket, f.read())
    elif request.target.split('?')[0] == '/next':
      g.conSem.acquire()
      with g.jobsLock:
        for doc, imageWorker, mode in g.jobs:
          with imageWorker.lock:
            if imageWorker.result is not None:
              _id = doc.id
              _mode = mode
              break
        else:
          raise Exception('Error 32759832')
      respond(self.socket, json.dumps({
        'doc_id': _id, 
        'mode': mode,
      }).encode())
    elif request.target.split('?')[0] == '/response':
      params = request.target.split('?')[1].split('&')
      doc_id = params[0].lstrip('doc_id=')
      response = params[1].lstrip('response=')
      with g.jobsLock:
        for i, (doc, imageWorker, _) in enumerate(g.jobs):
          if doc.id == doc_id:
            break 
        g.jobs.pop(i)
        g.printJobs()
      g.proSem.release()
      Thread(
        target = recordResponse, 
        args = (response, doc, imageWorker.result), 
      ).start()
      respond(self.socket, b'ok')
    elif request.target.split('?')[0] == '/img':
      param = request.target.split('?')[1]
      doc_id = param.lstrip('doc_id=')
      with g.jobsLock:
        for doc, imageWorker, _ in g.jobs:
          if doc.id == doc_id:
            break 
      respond(self.socket, imageWorker.result)
    elif request.target in ['/favicon.ico']:
      pass
    else:
      print('Unknown request:', request.target)

class MyServer(Server):
  def onConnect(self, addr):
    global trusted_ip
    if not trusted_ip:
      trusted_ip = addr[0]
    elif addr[0] != trusted_ip:
      print('SOMEONE IS ATTACKING!', addr)
      self.close()

def startServer():
  server = MyServer(MyOneServer, PORT, name='localhost')
  server.start()
  return server
