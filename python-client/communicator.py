#!/usr/bin/python
# -*- coding: utf-8 -*-

#Twisted is a lot. - Kyle
#A great help with twisted:
#http://krondo.com/blog/?p=1595

from twisted.internet import protocol, gireactor

class TISCapProtocol(protocol.Protocol):    
    def connectionMade(self):
        pass
    
    def dataReceived(self, data):
        #print "Data Received: " + data
        if (len(data) == 0):
            return
        
        t = data.split(" ")
        
        #Protocol is bananas here.
        if (len(t) == 1):
            t = data.split("\r\n")
        
        msg_type = t[0].lower()
        msg_type = msg_type[1:]
        msg_type = msg_type.strip()
        
        
        if (msg_type == "activeusers"):
            self.factory.userListReceived(data)
        elif (msg_type == "public"):
            self.factory.msgReceived(data)
        elif (msg_type == "connected" or msg_type == "disconnected"):
            #Now this is pretty clever.
            self.users()
        elif (msg_type == "welcome"):
            self.factory.connectionEstablished()
        elif (msg_type == "private"):
            self.factory.prvMsgReceived(data)
        elif (msg_type == "usernametaken"):
            self.factory.userNameTaken()
        elif (msg_type == "error" or msg_type == "badsyntax"):
            self.factory.error(data)
        else: 
            print "No case for this: '" + msg_type + "'"
            #A shim to maybe make some things work.
            shim = msg_type.split("]")[0]
            
            if (len(shim) > 1):
                print "Something went wrong with the byte stream."
                print "Everything should still work though"
                self.dataReceived("]" + shim)
                self.users()

        
    def login(self, uname):
        self.transport.writeSomeData("/login " + uname + "\r\n")
        
    def close(self):
        self.transport.writeSomeData("/close\r\n")
        self.transport.loseConnection()
        
    def users(self):
        self.transport.writeSomeData("/users\r\n")
        
    def sendMessage(self, message):
        message = message.decode('utf-8')
        msg = "/public\r\n" + message + u"\u0004"
        utf8 = msg.encode('utf-8')

        self.transport.writeSomeData(utf8)
        
    def sendPrivateMessage(self, user, message):
        #Say, this string is actually in utf-8.
        message = message.decode('utf-8')
        msg = "/private " + user + "\r\n" + message + u"\u0004"
        utf8 = msg.encode('utf-8')

        self.transport.writeSomeData(utf8)


class ClientFac(protocol.ClientFactory):    
    def __init__(self, rcv, usr, prv, wlc, err, lgn):
        self.protocol = TISCapProtocol
        self.instance = None
        self.received_cb = rcv
        self.user_cb = usr
        self.private_cb = prv
        self.welcome_cb = wlc
        self.error_cb = err
        self.login_cb = lgn
    
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
        self.login_cb("Connection Failed")
        
    def connectionEstablished(self):
        self.welcome_cb()
        
    def msgReceived(self, data):
        #print "Message Received"
        #Parse the data down to a nice user and message.
        trimed = data[7:]
        (uname, sep, data) = trimed.partition("\r\n")
        
        #Strip off the 0004
        data = data[:-1]
        uname = uname.strip()
        
        self.received_cb(uname, data)

    def prvMsgReceived(self, data):
        trimed = data[9:]
        (uname, sep, data) = trimed.partition("\r\n")
        data = data[:-1]
        uname = uname.strip()
        
        self.private_cb(uname, data)

    def userListReceived(self, data):
        #print "User List Received"
        #Parse the data down to a nice python like list.
        
        #Remove the activeusers part.
        trimed = data[12:].strip()
        #Now remove the brackets,
        #trimed = trimed[1:-1]
        
        users = trimed.split(",")
                
        self.user_cb(users)

    def userNameTaken(self):
        self.login_cb("Username Taken")

    def error(self, data):
        self.error_cb(data)











