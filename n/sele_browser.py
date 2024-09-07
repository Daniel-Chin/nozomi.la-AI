from contextlib import contextmanager
import typing as tp
import time
from threading import Lock

from selenium import webdriver
import selenium.common.exceptions
from selenium.webdriver.firefox.options import Options

REFERRER = 'https://nozomi.la/'

class SeleBrowser:
    def __init__(self):
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
    
    def closeTabOfDocId(self, doc_id: str):
        with self.lock:
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
                        self.driver.close()
                        break
            else:
                assert False, doc_id
            assert h == last
            self.driver.switch_to.window(self.driver.window_handles[-1])
