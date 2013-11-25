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
        #print "Data Received: " + data
        
        if (len(data) == 0):
            return
        
        t = data.split(" ")
        msg_type = t[0].lower()
        msg_type = msg_type[1:]
        
        
        if (msg_type == "activeusers"):
            self.userListReceived(data)
        if (msg_type == "public"):
            self.messageReceived(data)
        else: 
            print "No case for this..."
            print data

        
    def login(self, uname):
        self.transport.writeSomeData("/login " + uname + "\r\n")
        
    def users(self):
        self.transport.writeSomeData("/users\r\n")
        
    def sendMessage(self, message):
        self.transport.writeSomeData("/public\r\n" + message)
        
    def userListReceived(self, usr):
        self.factory.userListReceived(usr)
        
    def messageReceived(self, msg):
        self.factory.msgReceived(msg)
        
    def errorReceived(self, err):
        pass
      

class ClientFac(protocol.ClientFactory):
    uname = None
    
    def __init__(self, rcv, usr, err):
        self.protocol = TISCapProtocol
        self.instance = None
        self.received_cb = rcv
        self.user_cb = usr
    
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
        #Parse the data down to a nice user and message.
        trimed = data[7:]
        (uname, sep, data) = trimed.partition("\r\n")
        
        uname = uname.strip()
        
        self.received_cb(uname, data)

    def userListReceived(self, data):
        #Parse the data down to a nice python like list.
        
        #Remove the activeusers part.
        trimed = data[12:].strip()
        #Now remove the brackets,
        trimed = trimed[1:-1]
        
        users = trimed.split(",")
                
        self.user_cb(users)















