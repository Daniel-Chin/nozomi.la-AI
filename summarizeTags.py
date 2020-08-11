# todo: also filter for occurance

from ai import score, ALL_RESPONSES
from database import listAll, TAGS, loadOverall
import pickle
from jdt import Jdt
from gt import printTable

def load(name):
  with open(f'{TAGS}/{name}', 'rb') as f:
    return pickle.load(f)

def main():
  print('ls...')
  overall = loadOverall()
  baseline = score(overall)
  tagInfos = []
  la = listAll(TAGS)
  with Jdt(len(la), 'Evaluating...', UPP=8) as j:
    for i in la:
      j.acc()
      ti = load(i)
      total = 0
      for r in ALL_RESPONSES:
        total += ti.n_responses[r]
      if total < 10:
        continue
      try:
        s = score(ti.n_responses) - baseline
      except ZeroDivisionError:
        s = 0
      if abs(s) > 0.2:
        tagInfos.append((ti, s))
  print('Sorting...')
  tagInfos.sort(key=lambda x: x[1])
  print()
  table = []
  for ti, s in tagInfos:
    table.append([format(s, '+.1f'), ti.type, ti.display])
  printTable(table)

main()
input()