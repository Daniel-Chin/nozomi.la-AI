RES_NEGATIVE = 'RES_NEGATIVE'
RES_FINE = 'RES_FINE'
RES_WOW = 'RES_WOW'
RES_SAVE = 'RES_SAVE'

ALL_RESPONSES = [RES_NEGATIVE, RES_FINE, RES_WOW, RES_SAVE]

SCORE = {
  RES_NEGATIVE: -1,
  RES_FINE: 0,
  RES_WOW: 2,
  RES_SAVE: 10,
}

WEIGHT = {
  'artist': 4,
  'character': 2,
}

from doc import Doc, Tag
import database

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
  score_baseline = score(overall)

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
  return result
