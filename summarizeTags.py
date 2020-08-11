# todo: also filter for occurance

from ai import score
from database import listAll, loadTagInfo, TAGS, loadOverall

def main():
  overall = loadOverall()
  baseline = score(overall)
  tagInfos = []
  for i in listAll(TAGS):
    ti = loadTagInfo(i)
    try:
      s = score(ti.n_responses) - baseline
    except ZeroDivisionError:
      s = 0
    if abs(s) > 0.3:
      tagInfos.append((ti, s))
  tagInfos.sort(key=lambda x: x[1])
  for ti, s in tagInfos:
    print(ti.type, ti.display, format(s, '.1f'))

main()
input()
