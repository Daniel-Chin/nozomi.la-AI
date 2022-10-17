from dataclasses import dataclass
from concurrent.futures import Future
from threading import Lock
from typing import Callable, List

from doc import Doc

@dataclass
class PoolItem:
    doc: Doc
    image: bytes
    mode: str

class ImagePool:
    def __init__(self) -> None:
        self.n_idle = 0
        self.n_download = 0
        self.n_ready = 0

        self.lock = Lock()
        self.queue: List[PoolItem] = []
        self.waiter = None
    
    def activate(self, size: int, request: Callable[[], Future]):
        self.request = request
        for _ in range(size):
            self._request()
    
    def _request(self):
        self.request()

        with self.lock:
            self.n_idle -= 1
            self.n_download += 1
            self.printAnalytics()
    
    def receive(self, item: PoolItem):
        with self.lock:
            self.n_download -= 1
            self.n_ready += 1
            self.printAnalytics()

            self.queue.append(item)
            if self.waiter is None:
                self.waiter(item)
                self.waiter = None
    
    def consume(self, callback: Callable[[PoolItem]]):
        with self.lock:
            if self.queue:
                item = self.queue[0]
                callback(item)
            else:
                self.waiter = callback
    
    def pop(self):
        with self.lock:
            item = self.queue.pop(0)
        
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
