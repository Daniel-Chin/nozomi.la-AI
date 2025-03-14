import threading

try:
    from readchar import readkey
except ImportError:
    readkey = input

from shared import *
from parameters import *
from server import MyServer
from sele_browser import SeleBrowser
from webbrowser_wrap import openNoBlock

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
        if not EXPERT:
            print(*shortcuts, sep='\n')
            print('"q" to quit.')
        print('response > ', end='', flush=True)
        op = input().lower()
        for s, response in shortcuts:
            if s == op:
                break
        else:
            if op == 'q':
                return
            elif op == 'open':
                url = seleB.getCurrentDocUrl()
                openNoBlock(url, 1)
                continue
            print('invalid response. commands:')
            print('q, open', *shortcuts, sep=', ')
            continue
        try:
            poolItem, todo = server.imagePool.pop()
        except EOFError:
            return
        doc = poolItem.doc
        server.recordResponse(response, doc, poolItem.image)
        if response == RES_SAVE:
            seleB.save(doc)
        seleB.closeTabOfDocId(doc.id)
        threading.Thread(target=todo).start()
