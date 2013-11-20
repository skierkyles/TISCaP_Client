#!/usr/bin/python
from gi.repository import Gtk



class TISCaPClient:
    def __init__(self):
        pass
    
    def start(self): 
        self.builder = Gtk.Builder()
        self.builder.add_from_file("ui.glade")
        
        self.setup_ui()
        
        Gtk.main() 
        
    def setup_ui(self):
        self.window = self.builder.get_object("main_window")
        self.window.connect("delete-event", Gtk.main_quit)
        
        login_btn = self.builder.get_object("login_btn")
        login_btn.connect("clicked", self.login_btn_click)
        
        self.window.show_all()
        
    def login_btn_click(self, button):
        self.show_login_dialog()
    
    def show_login_dialog(self):
        #TODO Figure out why the dialog is blank when you click it a second time.
        content = self.builder.get_object("login_dialog_content")
        
        dialog = LoginDialog(self.window, content)
        res = dialog.run()
        
        if res == Gtk.ResponseType.OK:
            print "Connection times."
            
        elif res == Gtk.ResponseType.CANCEL:
            print "Not time to connect."
        
        dialog.destroy()
        
    
class LoginDialog(Gtk.Dialog):
    def __init__(self, parent, content):
        Gtk.Dialog.__init__(self, "Connect to a Server", parent, 0, 
                            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                             Gtk.STOCK_CONNECT, Gtk.ResponseType.OK))
        self.set_default_size(300, 175)
                            
        box = self.get_content_area()
        box.add(content)
        
        self.show_all()
    
if __name__ == "__main__":
    client = TISCaPClient()
    client.start()