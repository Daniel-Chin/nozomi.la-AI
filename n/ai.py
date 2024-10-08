import random
from threading import Lock
from typing import Any, Dict, List

from shared import *
from parameters import *
from imagePool import PoolItem
from doc import Doc, DocNotSuitable
from tag import TagInfo
from database import Database
from nozo import ImageRequester, getJSONs, askMaster, PageOutOfRange

SCORE = {
  RES_NEGATIVE: -2,
  RES_FINE: 0,
  RES_BETTER: 1,
  RES_MORE: 5, 
  RES_WOW: 15,
  RES_SAVE: 15,
}

WEIGHT = {
  'artist': 4,
  'character': 2,
}

EXPLOIT = 'EXPLOIT'
EXPLORE = 'EXPLORE'

def sumNResponses(responses: Dict[str, int]):
  s = 0
  for response in ALL_RESPONSES:
    s += responses.get(response, 0)
  return s

def score(responses: Dict[str, int]):
  s = sumNResponses(responses)
  if s == 0:
    return ATTITUDE_TOWARDS_NOVEL_TAGS
  
  score = 0
  for response in ALL_RESPONSES:
    score += responses.get(response, 0) / s * SCORE[response]
  return score

def predict(doc: Doc, db: Database):
  overall = db.loadOverall()
  if sumNResponses(overall) == 0:
    score_baseline = SCORE[RES_FINE]
  else:
    score_baseline = score(overall)

  result = 0
  for tag in doc.tags:
    try:
      tagInfo = db.loadTagInfo(tag.name)
    except KeyError:
      db.saveTagInfo(TagInfo(tag))
      tagInfo = db.loadTagInfo(tag.name)
    goodness = score(tagInfo.responses) - score_baseline
    goodness *= WEIGHT.get(tag.type, 1)
    if goodness < 0:
      _sum = sumNResponses(tagInfo.responses)
      if _sum in range(1, 5):
        # novel "maybe bad" tags may be good. 
        # novel "maybe good" tags can safely emerge, 
        # maybe turning into non-novel bad tags. 
        goodness *= _sum / 5
    result += goodness
  # if DEBUG:
  #   print('predict', doc.id, result)
  return result

def sample(json_lookup: Dict[str, Any], db, exitLock: Lock):
  docs: List[Doc] = []
  for json in json_lookup.values():
    try:
      docs.append(Doc(json))
    except DocNotSuitable:
      continue
  if not docs:
    raise EOFError
  
  if random.random() < EXPLORE_PROB:
    # Explore
    doc = random.choice(docs)
    return doc, EXPLORE
  else:
    # Exploit
    y_hats = []
    for doc in docs:
      if not exitLock.locked: return
      try:
        y_hat = predict(doc, db)
      except EOFError as e:
        print(e)
        print(
          '\n'
          'Database may be corrupted. Delete all '
          'tag files and run `comileTags.py`. '
          '\n'
        )
        raise ValueError
      y_hats.append((doc, y_hat))
    highscore = max([y for _, y in y_hats])
    results = [x for x, y in y_hats if y == highscore]
    return results[0], EXPLOIT

def HumanInLoop(
  session, imageRequester: ImageRequester, db: Database, 
  exitLock: Lock, 
):
  def noMore():
    print('There is no more! Enter "q" to quit...')
    imageRequester.imagePool.is_over = True
  
  blacklist = parseBlacklist(db)
  print('blacklist is', blacklist)
  print('If at least one of them show up in a doc, the doc will not show up, not even in EXPLORE mode.')
  batch_i = START_BATCH
  batch_step = 1
  patient = 1
  traversed = set()
  while True:
    has_stuff = False
    if batch_i not in traversed:
      traversed.add(batch_i)
      print('batch', batch_i)
      if not exitLock.locked: return
      try:
        pool = askMaster(batch_i * BATCH_SIZE, (batch_i + 1) * BATCH_SIZE)
      except PageOutOfRange:
        noMore()
        return
      if DEBUG:
        print('asked master')
      population = [x for x in pool if not db.doesDocExist(x)]
      json_lookup = {}
      if not exitLock.locked: return
      jsons = getJSONs(population, session)
      if DEBUG:
        print('got jsons')
      for i, json in enumerate(jsons):
        if json is not None:
          json_lookup[population[i]] = json
      if not json_lookup:
        noMore()
        return
      while len(json_lookup) >= len(pool) * (1 - VIEW_RATIO):
        has_stuff = True
        if not exitLock.locked: return
        try:
          doc, mode = sample(json_lookup, db, exitLock)
        except EOFError:
          break
        if DEBUG:
          print('sampled')
        del json_lookup[doc.id]
        if isBlacklisted(doc, blacklist):
          continue
        if not exitLock.locked: return
        yield imageRequester.sched(PoolItem(doc, None, mode))
        if DEBUG:
          print('after yield')
    if not FILTER:
      if has_stuff:
        patient = 1
        if batch_step != 1:
          batch_i -= batch_step - 1
          batch_step = 1
        else:
          batch_step += 1
          batch_step = min(15, batch_step)
      else:
        if patient == 1:
          patient = 0
        else:
          batch_step *= 2
          if random.random() < .3:
            batch_i -= random.randint(0, batch_step)
        batch_i += batch_step
    else:
      batch_i += 1

def isBlacklisted(doc: Doc, blacklist):
  for tag in doc.tags:
    if tag.name in blacklist:
      print(doc.id, 'is blacklisted for having', tag.name)
      return True
  return False

def parseBlacklist(db: Database):
  blacklist = []
  try:
    with open('blacklist.txt', 'r', encoding='utf-8') as f:
      for line in f:
        line = line.strip()
        if line:
          try:
            db.loadTagInfo(line)
          except KeyError:
            raise ValueError(f'"{line}" is not a valid tag name, or it is not cached yet.')
          else:
            blacklist.append(line)
  except FileNotFoundError:
    with open('blacklist.txt', 'w') as f:
      f.write('\n')
  return blacklist
