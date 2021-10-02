# todo: also filter for occurance

ARTIST_TOTAL_THRESHOLD = 10

import csv
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
        total += ti.n_responses.get(r, 0)
      if ti.type == 'artist':
        if total < ARTIST_TOTAL_THRESHOLD:
          continue
      else:
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
  FILENAME = 'tags_summary.csv'
  print(f'writing {FILENAME}...')
  header = ['Score', 'Type', 'Display', 'Name']
  with open(FILENAME, 'w', encoding='utf-8', newline='') as f:
    c = csv.writer(f)
    c.writerow(header)
    for ti, s in tagInfos:
      c.writerow([
        format(s, '+.1f'), str(ti.type), ti.display, ti.name, 
      ])
  with open(FILENAME, 'r', encoding='utf-8') as f:
    c = csv.reader(f)
    table = [*c]
  printTable(table)

main()
input()
