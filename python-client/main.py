#!/usr/bin/python
from gi.repository import Gtk, GLib
from communicator import CommThread, ClientCommand, ServerReply, Reciever, ClientFac
import Queue
import threading

from twisted.internet import protocol, reactor

class TISCaPClient:
    def __init__(self):
        self.uname = None
        self.server = None
        
        self.builder = None
        self.window = None
    
    def start(self): 
        self.logged_in = False
        
        self.builder = Gtk.Builder()
        self.builder.add_from_file("ui.glade")
        
        self.setup_ui()
        
        #Connecting to teh server

        #self.communicator = CommThread()
        #self.communicator.start()
        
        reactor.connectTCP('localhost', 4020, ClientFac())
        reactor.run()

        #GLib.timeout_add(100, self.check_queues)


        Gtk.main() 
        

    def setup_ui(self):
        self.window = self.builder.get_object("main_window")
        self.window.connect("delete-event", self.quit)
        
        login_btn = self.builder.get_object("login_btn")
        login_btn.connect("clicked", self.login_btn_click)
        
        refresh_btn = self.builder.get_object("refresh_users_btn")
        refresh_btn.connect("clicked", self.refresh_users_click)
        
        self.window.show_all()
        
    def quit(self, something, something_else):
        self.logged_in = False
        Gtk.main_quit()
        
    def check_queues(self):
        #if (self.logged_in):
            #self.communicator.cmd_q.put(ClientCommand(ClientCommand.RECEIVE))
        
        try: 
            reply = self.communicator.reply_q.get(block=False)
            if reply.type == ServerReply.SUCCESS:
                print reply.data
        except Queue.Empty:
            pass
        
        if self.logged_in and self.communicator.reply_q.empty():
                print "Just happened"
                print self.communicator.cmd_q
                self.communicator.cmd_q.put(ClientCommand(ClientCommand.RECEIVE))
        
        #Need to return true to keep the timer going.
        return True
        
    def update_users_list(self):
        pass
        
    def refresh_users_click(self, button):
        self.update_users_list()
        
    def login_btn_click(self, button):
        self.show_login_dialog()
    
    def show_login_dialog(self):
        #TODO Figure out why the dialog is blank when you click it a second time.
        content = self.builder.get_object("login_dialog_content")
        content.show_all()
        
        dialog = LoginDialog(self.window, content, self.builder.get_object("uname_entry"), self.builder.get_object("ip_entry"))
        res = dialog.run()
        
        if res is not None:
            self.uname = res[0]
            self.server = res[1]
            
            self.login_to_server(self.server, self.uname)
            
            
        dialog.destroy()
        
    def login_to_server(self, server, uname):
        if server == "":
            server = "127.0.0.1"
        
        self.communicator.cmd_q.put(ClientCommand(ClientCommand.CONNECT, ("127.0.0.1", 4020)))
        self.communicator.cmd_q.put(ClientCommand(ClientCommand.SEND, "/login " + uname + "\r\n"))
        
        self.logged_in = True
    
class LoginDialog(Gtk.Dialog):
    def __init__(self, parent, content, uname, server):
        Gtk.Dialog.__init__(self, "Connect to a Server", parent, 0, 
                            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                             Gtk.STOCK_CONNECT, Gtk.ResponseType.OK))
        self.set_default_size(300, 175)
        
        self.content = content
        self.uname = uname
        self.server = server
        
        box = self.get_content_area()
        box.add(self.content)
        
        self.show_all()

        
    def run(self): 
        result = super(LoginDialog, self).run()
        
        if result == Gtk.ResponseType.OK:
            text = (self.uname.get_text(), self.server.get_text())
        else:
            text = None
            
        return text
    
if __name__ == "__main__":
    client = TISCaPClient()
    client.start()