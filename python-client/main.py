#!/usr/bin/python
from gi.repository import Gtk, GLib
#from communicator import CommThread, ClientCommand, ServerReply, Reciever, ClientFac
from communicator import ClientFac
import Queue
import threading

from twisted.internet import protocol, gtk3reactor
gtk3reactor.install()
from twisted.internet import reactor

class TISCaPClient:
    def __init__(self):
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
        
        self.cf = ClientFac(self.twisted_callback, None, None)
        
        #reactor.connectTCP("127.0.0.1", 4020, self.cf)
        reactor.run()
        
        
        #GLib.timeout_add(100, self.check_queues)
        
        
        #Gtk.main() 
        

    def setup_ui(self):
        self.window = self.builder.get_object("main_window")
        self.window.connect("delete-event", self.quit)
        
        login_btn = self.builder.get_object("login_btn")
        login_btn.connect("clicked", self.login_btn_click)
        
        refresh_btn = self.builder.get_object("refresh_users_btn")
        refresh_btn.connect("clicked", self.refresh_users_click)
        
        send_btn = self.builder.get_object("send_btn")
        send_btn.connect("clicked", self.send_btn_clicked)
        
        self.window.show_all()
        
    def quit(self, something, something_else):
        self.logged_in = False
        #Gtk.main_quit()
        reactor.stop()
        
    def send_btn_clicked(self, btn):
        self.send_message()
        
    def send_message(self):
        send_entry = self.builder.get_object("send_entry")
        txt = send_entry.get_text()
        self.cf.instance.sendMessage(txt)
        
    def update_users_list(self):
        self.cf.instance.login("KYLE!")
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
        
        
        self.cf.uname = uname
        reactor.connectTCP(server, 4020, self.cf)
        reactor.callLater(1, self.try_login, uname)
        
        self.logged_in = True
        
    def try_login(self, uname):
        if (self.cf.instance != None):
            self.cf.instance.login(uname)
            return True
        
        reactor.callLater(1, self.try_login, uname)
        
    def twisted_callback(self, d):
        mt = self.builder.get_object("message_text")
        buff = Gtk.TextBuffer()
        mt.set_buffer(buff)
        buff.set_text(d)
        
        print d
    
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