import csv

already = set()
with open('already_tags.txt', 'r', encoding='utf-8') as f:
    for line in f:
        already.add(line.strip())

with open('tags_summary.csv', 'r', encoding='utf-8') as fin:
    with open('tags_subtract.csv', 'w', encoding='utf-8', newline='') as fout:
        cin = csv.reader(fin)
        cout = csv.writer(fout)
        cout.writerow(next(cin))
        for row in cin:
            if row[3] not in already:
                cout.writerow(row)
