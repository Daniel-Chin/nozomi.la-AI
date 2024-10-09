from contextlib import contextmanager
import typing as tp
import time
from threading import Lock
import base64

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By

from database import Database
from doc import Doc

REFERRER = 'https://nozomi.la/'

class SeleBrowser:
    def __init__(self, db: Database):
        self.db = db
        self.driver = None
        self.roster: tp.Dict[str, str] = {}
        self.lock = Lock()
    
    @contextmanager
    def context(self):
        options = Options()
        options.add_argument("-private")
        self.driver = webdriver.Firefox(options=options)
        self.driver.get(REFERRER)
        self.referrer_handle = self.driver.current_window_handle
        with self.driver:
            yield self
    
    def __injectImg(self, url: str):
        assert self.driver is not None
        self.driver.execute_script(f"""
var script = document.createElement('script');
script.id = 'ai-injector-3nwerluq274';
script.innerHTML = `
    window.open("{url}", '_blank');
    var selfScript = document.getElementById('ai-injector-3nwerluq274');
    selfScript.parentNode.removeChild(selfScript);
`
document.body.appendChild(script);
        """)
    
    def newTab(self, doc_id: str, url: str):
        with self.lock:
            assert self.driver is not None
            self.roster[url] = doc_id   # memory leak but it's ok
            self.driver.switch_to.window(self.referrer_handle)
            self.__injectImg(url)
            self.driver.switch_to.window(self.driver.window_handles[-1])
    
    def __seekDocId(self, doc_id: str):
        assert self.driver is not None
        last = self.driver.window_handles[-1]
        for h in self.driver.window_handles[1:]:
            self.driver.switch_to.window(h)
            try:
                this_doc_id = self.roster[self.driver.current_url]
            except KeyError:
                continue
            else:
                if this_doc_id == doc_id:
                    break
        else:
            assert False, doc_id
        assert h == last

    def closeTabOfDocId(self, doc_id: str):
        with self.lock:
            assert self.driver is not None
            self.__seekDocId(doc_id)
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[-1])
    
    def save(self, doc: Doc):
        with self.lock:
            assert self.driver is not None
            self.__seekDocId(doc.id)

            image_element = self.driver.find_element(By.XPATH, "//img[@src]")

            # Extract the image as base64 data using JavaScript
            image_base64 = self.driver.execute_script("""
                var img = arguments[0];
                var canvas = document.createElement('canvas');
                canvas.width = img.width * 4;
                canvas.height = img.height * 4;
                var ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                return canvas.toDataURL('image/webp').substring(22);  // Remove the "data:image/webp;base64," prefix
            """, image_element)

            # Decode the base64 string
            image_data = base64.b64decode(image_base64)

            self.db.saveImg(doc, [image_data])
    
    def getCurrentDocUrl(self):
        with self.lock:
            assert self.driver is not None
            self.driver.switch_to.window(self.driver.window_handles[-1])
            doc_id = self.roster[self.driver.current_url]
            url = f'https://nozomi.la/post/{doc_id}.html'
            return url
