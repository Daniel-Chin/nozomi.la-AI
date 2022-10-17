'''
An update in Mar. 2022 was not backward-compatible.  
Run this script to upgrade your database into the new format.  
'''

import legacy.mar2022.database as oldDb
from database import database
from jdt import jdtIter

def main():
    with database:
        # for doc_id in jdtIter(oldDb.listAll(oldDb.DOCS), 'docs'):
        #     doc = oldDb.loadDoc(doc_id)
        #     database.saveDoc(doc)
        good = 0
        bad = 0
        for tag_name in jdtIter(oldDb.listAll(oldDb.TAGS), 'tags'):
            try:
                tag = oldDb.loadTagInfo(tag_name)
            except FileNotFoundError:
                bad += 1
            else:
                database.saveTagInfo(tag)
                good += 1
        print('bad:', bad / (good + bad))
        # overall = oldDb.loadOverall()
        # database.saveOverall(overall)

# main()
