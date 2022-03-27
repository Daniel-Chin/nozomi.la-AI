'''
Use a file to denote whether a program is running.  
'''

class Exclusive:
    def __init__(self, filename) -> None:
        self.filename = filename
    
    def acquire(self):
        try:
            with open(self.filename, 'r+b') as f:
                if f.read(1) == b'1':
                    raise Occupied
                else:   # Possible race condition. Too bad. 
                    f.seek(0)
                    f.write(b'1')
                    f.flush()
        except FileNotFoundError:
            open(self.filename, 'wb').close()
            self.acquire()
    
    def release(self):
        with open(self.filename, 'r+b') as f:
            f.write(b'0')
    
    def __enter__(self):
        self.acquire()
    
    def __exit__(self, *_):
        self.release()
        return False

class Occupied(Exception): pass
