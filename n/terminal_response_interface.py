import threading

from shared import *
from server import MyServer
from sele_browser import SeleBrowser

shortcuts = [
    ('n', RES_NEGATIVE), 
    ('o', RES_FINE), 
    ('h', RES_BETTER), 
    ('m', RES_MORE), 
    ('g', RES_WOW), 
    ('s', RES_SAVE), 
]

def interactive(server: MyServer, seleB: SeleBrowser):
    while True:
        print(*shortcuts, sep='\n')
        print('"q" to quit.')
        op = input('response > ').lower()
        for s, response in shortcuts:
            if s == op:
                break
        else:
            if op == 'q':
                return
            print('invalid response')
            continue
        poolItem, todo = server.imagePool.pop()
        doc = poolItem.doc
        server.recordResponse(response, doc, poolItem.image)
        if response == RES_SAVE:
            seleB.save(doc)
        seleB.closeTabOfDocId(doc.id)
        threading.Thread(target=todo).start()
