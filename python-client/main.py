#!/usr/bin/python
from gi.repository import Gtk



class TISCaPClient:
    def __init__(self):
        self.uname = None
        self.server = None
        
        self.builder = None
        self.window = None
    
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
        content.show_all()
        
        dialog = LoginDialog(self.window, content, self.builder.get_object("uname_entry"), self.builder.get_object("ip_entry"))
        res = dialog.run()
        
        if res is not None:
            self.uname = res[0]
            self.server = res[1]
            
        dialog.destroy()
        
    
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