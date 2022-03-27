'''
Manually change your response to a doc you already 
gave a response to earlier.  
'''

import ai
from database import database

def main():
    with database:
        doc_id = input('doc_id=')
        doc = database.loadDoc(doc_id)
        print(doc)
        print()
        print('Which responses to change to?')
        print(
            '', *ai.ALL_RESPONSES, 
            sep = '\n  ', 
        )
        print()
        new_response = input('new_response=')
        assert new_response in ai.ALL_RESPONSES
        doc.response = new_response
        database.saveDoc(doc)
        database.accOverall(new_response)
        for tag in doc.tags:
            database.accTagInfo(tag, new_response)
        print(doc)

main()
