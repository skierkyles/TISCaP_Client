import socket
import struct
import threading
import Queue

#Lots of help from here.
#http://eli.thegreenplace.net/2011/05/18/code-sample-socket-client-thread-in-python/

class ClientCommand(object):
    """ A command to the client thread.
        Each command type has its associated data:

        CONNECT:    (host, port) tuple
        SEND:       Data string
        RECEIVE:    None
        CLOSE:      None
    """
    CONNECT, SEND, RECEIVE, CLOSE = range(4)
    
    def __init__(self, type, data=None):
        self.type = type
        self.data = data
        
class ServerReply(object): 
    """ A reply from the client thread.
        Each reply type has its associated data:

        ERROR:      The error string
        SUCCESS:    Depends on the command - for RECEIVE it's the received
                    data string, for others None.
    """
    ERROR, SUCCESS = range(2)
    
    def __init__(self, type, data=None):
        self.type = type
        self.data = data

class CommThread(threading.Thread):
    def __init__(self, cmd_q=None, reply_q=None):
        super(CommThread, self).__init__()
        
        #A queue of commands
        self.cmd_q = cmd_q or Queue.Queue()
        
        #A queue of replys
        self.reply_q = reply_q or Queue.Queue()
    
        self.alive = threading.Event()
        self.alive.set()
        
        self.socket = None
        
        self.handlers = {
                ClientCommand.CONNECT: self._handle_CONNECT,
                ClientCommand.CLOSE: self._handle_CLOSE,
                ClientCommand.SEND: self._handle_SEND,
                ClientCommand.RECEIVE: self._handle_RECEIVE,
        }

    def run(self):
        while self.alive.isSet():
            try:
                cmd = self.cmd_q.get(True, 0.1)
                self.handlers[cmd.type](cmd)
            except Queue.Empty as e:
                continue
    
    def join(self, timeout=None):
        self.alive.clear()
        threading.Thread.join(self, timeout)
    
    def _handle_CONNECT(self, cmd):
        try:
            self.socket = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((cmd.data[0], cmd.data[1]))
            self.reply_q.put(self._success_reply())
        except IOError as ioe:
            self.reply_q.put(self._error_reply(str(ioe)))
        
    def _handle_CLOSE(self, cmd):
        self.socket.shutdown()
        self.socket.close()
        reply = ServerReply(ServerReply.SUCCESS)
        self.reply_q.put(reply)
    
    def _handle_SEND(self, cmd):
        print "Going in with: " + cmd.data
        try:
            self.socket.sendall(cmd.data)
            print "Sent " + cmd.data
            self.reply_q.put(self._success_reply())
        except IOError as ioe:
            self.reply_q.put(self._error_reply(str(ioe)))
    
    def _handle_RECEIVE(self, cmd):
        try:
            data = self.socket.recv(4096)
            self.reply_q.put(self._success_reply(data))
            return
        except IOError as ioe:
            self.reply_q.put(self._error_reply(str(e)))

    def _error_reply(self, errstr):
        return ServerReply(ServerReply.ERROR, errstr)
    
    def _success_reply(self, data=None):
        return ServerReply(ServerReply.SUCCESS, data)


#USE TWISTED FOR THIS!

from twisted.internet import protocol, reactor

class Client(protocol.Protocol):
    def dataReceived(self, data):
        


















