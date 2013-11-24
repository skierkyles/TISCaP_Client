#Twisted is a lot. - Kyle

from twisted.internet import protocol, gireactor

class TISCapProtocol(protocol.Protocol):
    def connectionMade(self):
        #print dir(self.transport)
        #printf
        self.transport.write("/login kyfffafasdffsdfle\r\n")
        #print dir(self)
        

    
    def dataReceived(self, data):
        #self.factory.reply_q.put(data)
        self.factory.data_recieved(data)
      

class ClientFac(protocol.ClientFactory):
    uname = None
    
    def __init__(self, gui, callback):
        self.gui = gui
        self.protocol = TISCapProtocol
        self.instance = None
        self.callback = callback
    
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
        
    def data_recieved(self, data):
        self.callback(data)
















