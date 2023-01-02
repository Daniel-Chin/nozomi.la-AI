'''
Manually change your response to a doc you already 
gave a response to earlier.  
'''

from threading import Lock
from shared import *

from database import Database

def main():
    exitLock = Lock()
    exitLock.acquire()
    with Database(exitLock) as database:
        doc_id = input('doc_id=')
        doc = database.loadDoc(doc_id)
        print(doc)
        print()
        print('Which responses to change to?')
        print(
            '', ALL_RESPONSES, 
            sep = '\n  ', 
        )
        print()
        new_response = input('new_response=')
        assert new_response in ALL_RESPONSES
        doc.response = new_response
        database.saveDoc(doc)
        database.accOverall(new_response)
        for tag in doc.tags:
            database.accTagInfo(tag, new_response)
        print(doc)

main()
