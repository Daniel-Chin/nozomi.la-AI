from parameters import DEBUG, START_EPOCH, EXPLORE_PROB, POOL_SIZE, JSON_MAX, VIEW_RATIO, ATTITUDE_TOWARDS_NOVEL_TAGS

RES_NEGATIVE = 'RES_NEGATIVE'
RES_FINE = 'RES_FINE'
RES_BETTER = 'RES_BETTER'
RES_MORE = 'RES_MORE'
RES_WOW = 'RES_WOW'
RES_SAVE = 'RES_SAVE'

ALL_RESPONSES = [RES_NEGATIVE, RES_FINE, RES_BETTER, RES_MORE, RES_WOW, RES_SAVE]

SCORE = {
  RES_NEGATIVE: -2,
  RES_FINE: 0,
  RES_BETTER: 1,
  RES_MORE: 2, 
  RES_WOW: 8,
  RES_SAVE: 20,
}

WEIGHT = {
  'artist': 4,
  'character': 2,
}

EXPLOIT = 'EXPLOIT'
EXPLORE = 'EXPLORE'

blacklist = []

def recordResponse(response, doc, img):
  if database.doExist(database.DOCS, doc.id):
    raise Exception('Error 2049284234')
  doc.response = response
  database.saveDoc(doc)
  database.accOverall(response)
  for tag in doc.tags:
    database.accTagInfo(tag, response)
    if DEBUG:
      print(database.loadTagInfo(tag.name))
  print(doc)
  if response == RES_SAVE:
    database.saveImg(doc, [img])

from doc import Doc, Tag, DocNotSuitable
import database
import random
from nozo import getJSON, askMaster, ImageWorker, PageOutOfRange
from itertools import count
from forcemap import forceMap

def score(n_responses):
  sum = 0
  for response in ALL_RESPONSES:
    sum += n_responses.get(response, 0)
  if sum < .5:  # round(sum) == 0
    return ATTITUDE_TOWARDS_NOVEL_TAGS
  score = 0
  for response in ALL_RESPONSES:
    score += n_responses.get(response, 0) / sum * SCORE[response]
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
      _sum = tagInfo.sum()
      if _sum < 5:
        goodness *= _sum / 5
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
    jsons = [getJSON(x) for x in population]
    docs = []
    for j in jsons:
      try:
        docs.append(Doc(j))
      except DocNotSuitable:
        continue
    y_hats = [(x.id, predict(x)) for x in docs]
    highscore = max([y for x, y in y_hats])
    results = [x for x, y in y_hats if y == highscore]
    return (results[0], EXPLOIT)

def roll():
  print('blacklist is', blacklist)
  print('If at least one of them show up in a doc, the doc will not show up, not even in EXPLORE mode.')
  epoch = START_EPOCH
  epoch_step = 1
  patient = 1
  traversed = {}
  while True:
    has_stuff = False
    if not traversed.get(epoch, False):
      print('epoch', epoch)
      traversed[epoch] = True
      try:
        pool = askMaster(epoch * POOL_SIZE, (epoch + 1) * POOL_SIZE)
      except PageOutOfRange:
        print('There is no more. Enter to quit...')
        input()
        return
      population = [x for x in pool if not database.doExist(database.DOCS, x)]
      checked_404 = False
      while len(population) >= len(pool) * (1 - VIEW_RATIO):
        if not checked_404:
          jsons = forceMap(getJSON, population, thread_max=JSON_MAX)
          population = [x for x, y in zip(population, jsons) if y is not None]
          checked_404 = True
          if not population:
            print('There is no more. Enter to quit...')
            input()
            return
          continue
        has_stuff = True
        doc_id, mode = sample(population)
        population.pop(population.index(doc_id))
        try:
          doc = Doc(getJSON(doc_id))
        except DocNotSuitable:
          continue
        if isBlacklisted(doc):
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
    if has_stuff:
      patient = 1
      if epoch_step != 1:
        epoch -= epoch_step - 1
        epoch_step = 1
      else:
        epoch_step += 1
        epoch_step = min(15, epoch_step)
    else:
      if patient == 1:
        patient = 0
      else:
        epoch_step *= 2
        if random.random() < .3:
          epoch -= random.randint(0, epoch_step)
      epoch += epoch_step

def setBlackList(bl):
  blacklist.clear()
  blacklist.extend(bl)

def isBlacklisted(doc):
  try:
    for tag in doc.tags:
      if tag.name in blacklist:
        print(doc.id, 'is blacklisted for having', tag.name)
        return True
  except DocNotSuitable:
    pass
  return False

from server import g, Job
