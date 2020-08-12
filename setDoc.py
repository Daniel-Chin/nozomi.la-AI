import ai
import database
from doc import Doc
from nozo import getJSON

def main():
  print(ai.ALL_RESPONSES)
  while True:
    doc_id = input('doc_id=')
    response = input('response=')
    if database.doExist(database.DOCS, doc_id):
      raise Exception('Error 24154035')
    doc = Doc(getJSON(doc_id))
    doc.response = response
    database.saveDoc(doc)
    database.accOverall(response)
    for tag in doc.tags:
      database.accTagInfo(tag, response)
    print(doc)

main()
