'''
My threading utils
'''
from threading import Condition

class Safe(Condition):
    def __init__(self, value = None):
        Condition.__init__(self)
        self.set(value)
    
    def set(self, value):
        with self:
            self.value = value
    
    def get(self):
        with self:
            return self.value
    
    def call(self, classMethod, *args, **kw):
        with self:
            return classMethod(self.value, *args, **kw)
