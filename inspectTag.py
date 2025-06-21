'''
Inspect one tag. 
'''

from threading import Lock

from tqdm import tqdm

from database import Database
from doc import Doc
import ai

def main():
    with Database(Lock()) as db:
        the_tag = input("tag=")
        tagInfo = db.loadTagInfo(the_tag)
        print(tagInfo)
        print(tagInfo.responses)
        score = ai.score(tagInfo.responses)
        print(f'{score = }')
        overall = db.loadOverall()
        baseline = ai.score(overall)
        print(f'{score - baseline = }', )
        input('Enter...')
        relevant_docs = []
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
