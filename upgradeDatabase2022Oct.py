'''
An update in Oct. 2022 was not backward-compatible.  
Run this script to upgrade your database into the new format.  
'''

from requests_futures.sessions import FuturesSession
from tqdm import tqdm

from legacy.oct2022.database import database as oldDb
import legacy.oct2022.old_doc as old_doc
import legacy.oct2022.old_tag as old_tag
import database
from doc import Doc
from tag import TagInfo, Tag
from nozo import getJSONs

def main():
    database.DOCS = 'new_docs.shelve'
    database.TAGS = 'new_tags.shelve'
    BATCH_SIZE = 4

    with FuturesSession(max_workers=BATCH_SIZE) as session:
        with database.Database().context() as db, oldDb:
            collate = []
            for doc_id in tqdm(oldDb.listAllDocs(), 'docs'):
                collate.append(doc_id)
                if len(collate) == BATCH_SIZE:
                    jsons = getJSONs(collate, session)
                    for doc_id, json in zip(collate, jsons):
                        if json is None:
                            continue
                        newDoc = Doc(json)
                        oldDoc: old_doc.Doc = oldDb.loadDoc(doc_id)
                        # newDoc.id = oldDoc.id
                        # newDoc.tags = []
                        # newDoc.img_urls = oldDoc.img_urls
                        # newDoc.img_type = oldDoc.img_type
                        # newDoc.width = oldDoc.width
                        # newDoc.height = oldDoc.height
                        # newDoc.date = oldDoc.date
                        newDoc.response = oldDoc.response
                        # newDoc.local_filenames = oldDoc.local_filenames
                        # for oldTag in oldDoc.tags:
                        #     oldTag: old_tag.TagInfo
                        #     newTag = TagInfo(Tag(oldTag.name, oldTag.display, oldTag.type))
                        #     newTag.responses = oldTag.n_responses
                        #     newDoc.tags.append(newTag)
                        db.saveDoc(newDoc)
                    collate.clear()

main()
