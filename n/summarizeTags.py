# todo: also filter for occurance

ARTIST_TOTAL_THRESHOLD = 0

import csv
from threading import Lock
from typing import List, Tuple
from tqdm import tqdm

from gt import printTable

from shared import *
from database import Database
from ai import score
from tag import TagInfo

def main():
  exitLock = Lock()
  exitLock.acquire()
  with Database(exitLock) as database:
    print('ls...')
    overall = database.loadOverall()
    baseline = score(overall)
    tagInfos: List[Tuple[TagInfo, float]] = []
    la = database.listAllTagInfos()
    for i in tqdm(la):
      try:
        ti = database.loadTagInfo(i)
      except KeyError as e:
        print(e)
        continue
      total = 0
      for r in ALL_RESPONSES:
        total += ti.responses.get(r, 0)
      if ti.tag.type == 'artist':
        if total < ARTIST_TOTAL_THRESHOLD:
          continue
      else:
        if total < 10:
          continue
      try:
        s = score(ti.responses) - baseline
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
          format(s, '+.1f'), str(ti.tag.type), ti.tag.display, ti.tag.name, 
        ])
    input('Press Enter to display...')
    with open(FILENAME, 'r', encoding='utf-8') as f:
      c = csv.reader(f)
      table = [*c]
    printTable(table)

main()
input()
