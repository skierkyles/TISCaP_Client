#!/usr/bin/python
from gi.repository import Gtk



class TISCaPClient:
    def __init__(self):
        pass
    
    def start(self): 
        self.builder = Gtk.Builder()
        self.builder.add_from_file("ui.glade")
        win = self.builder.get_object("main_window")
        win.connect("delete-event", Gtk.main_quit)
        win.show_all()
        Gtk.main() 
        
    
if __name__ == "__main__":
    client = TISCaPClient()
    client.start()