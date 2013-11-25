#Twisted is a lot. - Kyle
#A great help with twisted:
#http://krondo.com/blog/?p=1595

from twisted.internet import protocol, gireactor

class TISCapProtocol(protocol.Protocol):
    _UNAME_TAKEN = 49
    _MESSAGE = 343
    _PRIVATE_MESSAGE = 2401
    _USER_LIST = 16807
    
    def connectionMade(self):
        #print dir(self.transport)
        #printf
        #print dir(self)
        pass
    
    def dataReceived(self, data):
        #self.factory.reply_q.put(data)
        self.factory.msgReceived(data)
        #self.errorReceived("ASDF")
        
    def login(self, uname):
        self.transport.write("/login " + uname + "\r\n")
        
    def sendMessage(self, message):
        #print dir(self.transport)
        print "Sending: " + str(message)
        self.transport.writeSomeData("/public\r\n" + message)
        
    def userListReceived(self, usr):
        pass
        
    def messageReceived(self, msg):
        pass
        
    def errorReceived(self, err):
        #print dir(self)
        pass
      

class ClientFac(protocol.ClientFactory):
    uname = None
    
    def __init__(self, rcv, usr, err):
        self.protocol = TISCapProtocol
        self.instance = None
        self.received_cb = rcv
    
    def startedConnecting(self, connector):
        print 'Connecting'

    def buildProtocol(self, addr):
        print 'Connected.'
        self.instance = self.protocol()   
        self.instance.factory = self
        
        return self.instance

    def clientConnectionLost(self, connector, reason):
        print reason

    def clientConnectionFailed(self, connector, reason):
        print reason
        
    def msgReceived(self, data):
        self.received_cb(data)
















