'''
compile tag info from doc info.  
Delete tag.shelve.* (if you are sure) before running  
this script.  
'''

from database import Database
from doc import Doc
from tqdm import tqdm

def main():
    with Database().context() as db:
        overall = db.loadOverall()
        for key in overall:
            overall[key] = 0
        db.saveOverall(overall)
        del overall
        doc_ids = db.listAllDocs()
        for doc_id in tqdm(doc_ids):
            doc : Doc = db.loadDoc(doc_id)
            db.accOverall(doc.response)
            for tag in doc.tags:
                db.accTagInfo(tag, doc.response)

main()
