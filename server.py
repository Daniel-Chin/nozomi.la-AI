JOB_POOL_SIZE = 4

from threading import Semaphore, Lock
from myhttp import Server, OneServer, respond
import json
from ai import ALL_RESPONSES

class G:
  def __init__(self):
    self.conSem = Semaphore(JOB_POOL_SIZE)
    self.proSem = Semaphore(JOB_POOL_SIZE)
    self.jobsLock = Lock()
    for _ in range(JOB_POOL_SIZE):
      self.proSem.acquire()
    self.jobs = []

g = G()

from ai import recordResponse

class Job:
  __slots__ = ['doc', 'imageWorker', 'mode']

class MyOneServer(OneServer):
  def handle(self, request):
    if request.target == '/':
      with open('index.html', 'rb') as f:
        respond(self.socket, f.read())
    elif request.target.split('?')[0] == '/next':
      g.conSem.acquire()
      with g.jobsLock:
        for doc, imageWorker, mode in g.jobs:
          with imageWorker.lock:
            if imageWorker.result is not None:
              break
      respond(self.socket, json.dumps({
        'doc_id': doc.id, 
        'mode': mode,
      }).encode())
    elif request.target.split('?')[0] == '/response':
      params = request.target.split('?')[1].split('&')
      doc_id = params[0].lstrip('doc_id=')
      response = params[1].lstrip('response=')
      with g.jobsLock:
        for i, (doc, _, _) in enumerate(g.jobs):
          if doc.id == doc_id:
            break 
        g.jobs.pop(i)
      g.proSem.release()
      recordResponse(response, doc)
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
