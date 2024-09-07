import sys
import subprocess
import time
import threading

import webbrowser

browser_desktop_entry = subprocess.check_output(["xdg-settings", "get", "default-web-browser"]).decode().strip()
browser_name = browser_desktop_entry.replace('.desktop', '')
browser_path = subprocess.check_output(["which", browser_name]).decode().strip()
controller = webbrowser.get(
    browser_path + ' --private-window %s'
)

def open(url, new: int = 0, autoraise: bool = True):
    controller.open(url, new=new, autoraise=autoraise)

def openNoBlock(url, new: int = 0, autoraise: bool = True):
    threading.Thread(
        target=open, args=[url], 
        kwargs={'new': new, 'autoraise': autoraise}, 
        name='webbrowser_wrap.open', 
    ).start()

def main():
    if '-b' in sys.argv:
        url = sys.argv[-1]
        open(url, new=1, autoraise=False)
    else:
        test()

def test():
    print('sleeping 1 sec...')
    time.sleep(1)
    open('https://www.example.com')

if __name__ == '__main__':
    main()
