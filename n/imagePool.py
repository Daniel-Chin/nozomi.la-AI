import os
from dataclasses import dataclass
from concurrent.futures import Future
from threading import Lock
from typing import Callable, List

from parameters import *
from doc import Doc
import webbrowser_wrap
from sele_browser import SeleBrowser

@dataclass
class PoolItem:
    doc: Doc
    image: bytes
    mode: str

class ImagePool:
    def __init__(self, seleB: SeleBrowser) -> None:
        self.seleB = seleB

        self.n_idle = 0
        self.n_download = 0
        self.n_ready = 0

        self.lock = Lock()
        self.queue: List[PoolItem] = []
        self.waiter = None

        self.is_over = False
    
    def activate(
        self, size: int, request: Callable[[], Future], 
    ):
        self.n_idle = size
        self.request = request
        for _ in range(size):
            self._request()
    
    def _request(self):
        try:
            self.request()
        except StopIteration:
            return

        with self.lock:
            self.n_idle -= 1
            self.n_download += 1
            self.printAnalytics()
    
    def receive(self, item: PoolItem):
        if DEBUG:
            print('receive')
        with self.lock:
            self.n_download -= 1
            self.n_ready += 1
            self.printAnalytics()
            if DEBUG:
                print(f'{item.doc.id = }')
                print(f'{item.doc.img_urls = }')

            self.queue.append(item)
            if self.waiter is not None:
                self.waiter(item)
                self.waiter = None
            
            if IMG_DOWNLOAD_IN_BROWSER:
                img_urls = item.doc.getImgUrls()
                if len(img_urls) == 1 and item.doc.img_type != 'mp4':
                    img_url = img_urls[0]
                else:
                    img_url = f'https://nozomi.la/post/{item.doc.id}.html'
                # webbrowser_wrap.openNoBlock(
                #     f'http://localhost:{PORT}/panel?doc_id={item.doc.id}&img_url={img_url}', 
                #     new=1, 
                #     autoraise=False, 
                # )
                self.seleB.newTab(item.doc.id, img_url)
    
    def consume(self, callback: Callable[[PoolItem], None]):
        with self.lock:
            if self.queue:
                if DEBUG:
                    print('hitter')
                item = self.queue[0]
                callback(item)
            else:
                if DEBUG:
                    print('waiter')
                self.waiter = callback
    
    def pop(self):
        with self.lock:
            try:
                item = self.queue.pop(0)
            except IndexError:
                if self.is_over:
                    raise EOFError('Queue empty after over. This is normal.')
                raise
        
            self.n_ready -= 1
            self.n_idle += 1
            self.printAnalytics()

        return item, self._request

    def printAnalytics(self):
        print(
            'image pool: [', 
            ' ' * self.n_idle, 
            '_' * self.n_download, 
            '|' * self.n_ready, 
            ']', sep = '', 
        )
