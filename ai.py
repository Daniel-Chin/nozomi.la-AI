DEBUG = False

EXPLORE_PROB = .2
POOL_SIZE = 64
VIEW_RATIO = .2

RES_NEGATIVE = 'RES_NEGATIVE'
RES_FINE = 'RES_FINE'
RES_BETTER = 'RES_BETTER'
RES_WOW = 'RES_WOW'
RES_SAVE = 'RES_SAVE'

ALL_RESPONSES = [RES_NEGATIVE, RES_FINE, RES_BETTER, RES_WOW, RES_SAVE]

SCORE = {
  RES_NEGATIVE: -1,
  RES_FINE: 0,
  RES_BETTER: .5,
  RES_WOW: 2,
  RES_SAVE: 10,
}

WEIGHT = {
  'artist': 4,
  'character': 2,
}

EXPLOIT = 'EXPLOIT'
EXPLORE = 'EXPLORE'

def recordResponse(response, doc, img):
  doc.response = response
  database.saveDoc(doc)
  database.accOverall(response)
  for tag in doc.tags:
    database.accTagInfo(tag.name, response)
    if DEBUG:
      print(database.loadTagInfo(tag.name))
  print(doc)
  if response == RES_SAVE:
    database.saveImg(doc, [img])

from doc import Doc, Tag, DocNotSuitable
import database
import random
from nozo import getJSON, askMaster, ImageWorker
from itertools import count
from forcemap import forceMap

def score(n_responses):
  sum = 0
  for response in ALL_RESPONSES:
    sum += n_responses[response]
  score = 0
  for response in ALL_RESPONSES:
    score += n_responses[response] / sum * SCORE[response]
  return score

def predict(doc: Doc):
  overall = database.loadOverall()
  try:
    score_baseline = score(overall)
  except ZeroDivisionError:
    score_baseline = 0

  result = 0
  for tag in doc.tags:
    try:
      tagInfo = database.loadTagInfo(tag.name)
    except FileNotFoundError:
      database.saveNewTagInfo(tag)
      tagInfo = database.loadTagInfo(tag.name)
    try:
      goodness = score(tagInfo.n_responses) - score_baseline
    except ZeroDivisionError:
      goodness = 0
    else:
      goodness *= WEIGHT.get(tag.type, 1)
    result += goodness
  if DEBUG:
    print('predict', doc.id, result)
  return result

def sample(population):
  if random.random() < EXPLORE_PROB:
    # Explore
    doc_id = random.choice(population)
    return (doc_id, EXPLORE)
  else:
    # Exploit
    jsons = forceMap(getJSON, population, thread_max=8)
    docs = []
    for j in jsons:
      try:
        docs.append(Doc(j))
      except DocNotSuitable:
        continue
    y_hats = [(x.id, predict(x)) for x in docs]
    highscore = max(*[y for x, y in y_hats])
    results = [x for x, y in y_hats if y == highscore]
    return (results[0], EXPLOIT)

def roll():
  epoch = 0
  epoch_step = 1
  while True:
    print('epoch', epoch)
    pool = askMaster(epoch * POOL_SIZE, (epoch + 1) * POOL_SIZE)
    population = [x for x in pool if not database.doExist(database.DOCS, x)]
    has_stuff = False
    while len(population) >= POOL_SIZE * (1 - VIEW_RATIO):
      has_stuff = True
      doc_id, mode = sample(population)
      population.pop(population.index(doc_id))
      try:
        doc = Doc(getJSON(doc_id))
      except DocNotSuitable:
        continue
      if DEBUG:
        print('Waiting for proSem...')
      g.proSem.acquire()
      if DEBUG:
        print('proSem acquired')
      job = Job(doc, ImageWorker(doc.img_urls[0]), mode)
      job.imageWorker.todo = g.conSem.release
      with g.jobsLock:
        g.jobs.append(job)
        g.printJobs()
      job.imageWorker.start()
    if not has_stuff:
      epoch_step += 1
    else:
      epoch_step = 1
    epoch += epoch_step

from server import g, Job
