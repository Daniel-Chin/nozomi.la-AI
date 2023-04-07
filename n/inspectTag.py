'''
Inspect one tag. 
'''

from threading import Lock

from tqdm import tqdm

from database import Database
from doc import Doc
import ai

def main():
    the_tag = input("tag=")
    relevant_docs = []
    with Database(Lock()) as db:
        doc_ids = db.listAllDocs()
        for doc_id in tqdm(doc_ids):
            doc : Doc = db.loadDoc(doc_id)
            for tag in doc.tags:
                if tag.name == the_tag:
                    print()
                    print(doc)
                    relevant_docs.append(doc)
    print()
    print('OK. The list:')
    def keyOf(doc: Doc):
        return ai.SCORE[doc.response]
    relevant_docs.sort(key=keyOf, reverse=True)
    print(*relevant_docs, sep='\n')

main()
