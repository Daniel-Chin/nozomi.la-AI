# todo: also filter for occurance

ARTIST_TOTAL_THRESHOLD = 0

import csv
from ai import score, ALL_RESPONSES
from database import database
from jdt import Jdt
from gt import printTable

def main():
  with database:
    print('ls...')
    overall = database.loadOverall()
    baseline = score(overall)
    tagInfos = []
    la = database.listAllTags()
    with Jdt(len(la), 'Evaluating...', UPP=8) as j:
      for i in la:
        j.acc()
        try:
          ti = database.loadTagInfo(i)
        except KeyError as e:
          print(e)
          continue
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
    input('Press Enter to display...')
    with open(FILENAME, 'r', encoding='utf-8') as f:
      c = csv.reader(f)
      table = [*c]
    printTable(table)

main()
input()
