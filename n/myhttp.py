'''
Serves through a (super) simplified version of http protocol. 
Warning: Running this may expose your computer to attacks. 
Don't run this. 
'''
from threading import Thread
from queue import Queue, Empty
from socket import socket as Socket, timeout, gethostname, gethostbyname
import logging
from mythread import Safe

__all__ = ['BadRequest', 'ClientShutdown', 'Request', 
           'OneServer', 'Server', 'Intent', 'log', 'logging', 
           'respond', 'myLogger',
]

class BadRequest(BaseException):
    pass

class ClientShutdown(BaseException):
    pass

logging.basicConfig(format='%(asctime)s %(message)s', 
                    filename = 'log.log')
logging.root.setLevel(logging.NOTSET)

class MyLogger:
    def __init__(self):
        self.verbose = True
    
    def log(self, *args, sep = ' ', end = '\n', flush = False, level = logging.INFO):
        text = sep.join([str(x) for x in args]) + end
        if self.verbose:
            print(text, flush = flush, end = '')
        logging.log(level, text)

myLogger = MyLogger()
log = myLogger.log

class Intent:
    pass

class DeregisterOneServer(Intent):
    def __init__(self, oneServer):
        self.oneServer = oneServer

class Request:
    def __init__(self, command, target, http_version):
        self.command = command
        self.target = target
        self.http_version = http_version
        self.options = {}
        self.body = ''
    
    def add(self, kw, value):
        self.options[kw] = value
    
    def get(self, kw):
        return self.options[kw]
    
    def __str__(self):
        if self.command == 'POST':
            return self.command + ' ' + self.target + ' ' + self.body
        else:
            return self.command + ' ' + self.target

def parseHead(text):
    whats_bad = ''
    try:
        lines = text.split('\r\n')
        whats_bad = lines[0]
        request = Request(*lines[0].split(' '))
        for line in lines[1:]:
            whats_bad = line
            kw, value = line.split(':', 1)
            kw = kw.strip(' ')
            value = value.strip(' ')
            request.add(kw, value)
        return request
    except Exception as e:
        log('Bad line:', whats_bad, level = logging.ERROR)
        raise BadRequest

def respond(socket, data):
    response = '''HTTP/1.1 200 OK\r
Content-Length: %d\r
Content-Type: text/html\r\n\r\n''' % len(data)
    socket.send(response.encode())
    socket.send(data)

class OneServer(Thread):
    '''
    Subclass this class and override: 
        handle(request) where request is a Request object
        request_filter is a list of request that you don't wanna log 
    `close()`
    '''
    request_filter = []
    
    def __init__(self, addr, socket, parentQueue):
        '''
        You shouldn't override this. OneServer doesn't need any 
        runtime state. Keep-alive should not be abused. 
        '''
        Thread.__init__(self)
        self.addr = addr
        self.socket = socket  
        socket.settimeout(.4)
        self.parentQueue = parentQueue
        self.queue = Queue()
        self._go_on = Safe(True)
    
    def close(self):
        self._go_on.set(False)
    
    def respond(self, data, do_log = True):
        respond(self.socket, data)
        if do_log:
            if len(data) < 50:
                log(self, data.decode())
    
    def handle(self, request):
        # Override this
        respond(self.socket, b'''<html>What a shame. 
The programmer didn't override the request handler. </html>''')
    
    def __str__(self):
        return self.addr.__str__()
    
    def run(self):
        log(self, 'service begin. ')
        chunk = b''
        try:
            while self._go_on.get():
                try:
                    recved = self.socket.recv(4096)
                    if recved == b'':
                        raise ClientShutdown
                    else:
                        chunk += recved
                    while b'\r\n\r\n' in chunk:
                        bytes_head, chunk = chunk.split(b'\r\n\r\n', 1)
                        request = parseHead(bytes_head.decode())
                        if request.command == 'POST':
                            content_len = int(request.get('Content-Length'))
                            if len(chunk) >= content_len:
                                bytes_body = chunk[:content_len]
                                chunk = chunk[content_len:]
                                request.body = bytes_body.decode()
                            else:
                                chunk = b'\r\n\r\n'.join([bytes_head, chunk])
                                break
                        do_log = True
                        for filter in self.request_filter:
                            if filter in request.target:
                                do_log = False
                                break
                        if do_log:
                            log(self, 'Request', request)
                        self.handle(request)
                except timeout:
                    pass
            # self.close() called
        except (ClientShutdown, ConnectionAbortedError, ConnectionResetError):
            log(self, 'client shutdown')
        finally:
            self.parentQueue.put(DeregisterOneServer(self))
            self.socket.close()
            log(self, 'Thread has stopped. ')

class Server(Thread):
    '''
    Subclass this class and override: 
        handleQueue()
        interval()
    `close()`
    '''
    def __init__(self, my_OneServer = OneServer, port = 80, 
                 listen = 1, accept_timeout = .5):
        # Pass in your subclassed OneServer
        Thread.__init__(self)
        self.queue = Queue()
        self.OneServer = my_OneServer
        self.listen = listen
        self.socket = Socket()
        self.socket.bind(('', port))
        self.socket.settimeout(accept_timeout)
        self._go_on = Safe(True)
        self.oneServers = []
        self.max_connection = Safe(4 * 32)
        self.showing_max_waring = False
    
    def setMaxConnection(self, number):
        self.max_connection.set(number)
    
    def getMaxConnection(self):
        return self.max_connection.get()
    
    def interval(self):
        '''
        Override this.
        '''
        pass
    
    def handleQueue(self, intent):
        '''
        Override this.
        '''
        pass
    
    def __handleQueue(self, intent):
        if type(intent) is DeregisterOneServer:
            self.oneServers.remove(intent.oneServer)
        else:
            self.handleQueue(intent)
    
    def close(self):
        if self.isAlive():
            with self._go_on:
                self._go_on.value = False
            #self.join()    public method
    
    def onConnect(self, addr):
        pass    # to override.
    
    def run(self):
        self.socket.listen(self.listen)
        log('listening at', gethostbyname(gethostname()), '...')
        while self._go_on.get():
            if len(self.oneServers) >= self.getMaxConnection():
                if not self.showing_max_waring:
                    log('Max connection reached. ')
                    self.showing_max_waring = True
            else:
                if self.showing_max_waring:
                    log("Max connection isn't reached anymore. ")
                    self.showing_max_waring = False
                try:
                    socket, addr = self.socket.accept()
                    log(addr, 'Accepted. ')
                    self.onConnect(addr)
                    oneServer = self.OneServer(addr, socket, self.queue)
                    self.oneServers.append(oneServer)
                    oneServer.start()
                except timeout:
                    pass
            try:
                while self._go_on.get():
                    self.__handleQueue(self.queue.get_nowait())
            except Empty:
                pass
            self.interval()
        self.socket.close()
        log('Closing', len(self.oneServers), 'oneServers.')
        for oneServer in self.oneServers:
            oneServer.close()
        log('Server thread has stopped. ')
