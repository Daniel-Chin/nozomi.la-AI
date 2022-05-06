'''
compile tag info from doc info.  
Delete tag.shelve.* (if you are sure) before running  
this script.  
'''

import ai
from database import database
from doc import Doc
from jdt import jdtIter

def main():
    with database:
        overall = database.loadOverall()
        for key in overall:
            overall[key] = 0
        database.saveOverall(overall)
        del overall
        doc_ids = database.listAllDocs()
        for doc_id in jdtIter(doc_ids, UPP = 16):
            doc : Doc = database.loadDoc(doc_id)
            database.accOverall(doc.response)
            for tag in doc.tags:
                database.accTagInfo(tag, doc.response)

main()
