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
        
        #This should be eliminated
        self.o_c_tag = None
        self.m_c_tag = None
        #End elimination...
    
    def start(self): 
        self.logged_in = False
        
        self.builder = Gtk.Builder()
        self.builder.add_from_file("ui.glade")
        
        self.setup_ui()

        
        self.cf = ClientFac(self.msg_rcvd_callback, self.user_list_callback,
                            self.private_callback, self.welcome_callback, None, self.login_callback)
        
        reactor.run()
        

    def setup_ui(self):
        self.window = self.builder.get_object("main_window")
        self.window.connect("delete-event", self.quit)
        
        #The different views the window may hold...
        self.main_content = self.builder.get_object("main_content")
        self.main_loading = self.builder.get_object("main_loading")
        self.main_login = self.builder.get_object("main_login")
        self.main_private = self.builder.get_object("main_private")
        #########################################
        
        #self.window.add(self.main_content)
        
        self.user_model = self.builder.get_object("user_store")
        
        #Main content stuff.
        
        send_btn = self.builder.get_object("send_btn")
        send_btn.connect("clicked", lambda x: self.send_message())
        
        entry_text = self.builder.get_object("send_entry")
        entry_text.connect("key-press-event", self.entry_keypress)
        
        self._sw = self.builder.get_object("chat_scroll")
        self._sw.connect("size-allocate", self._autoscroll)
        
        user_tree = self.builder.get_object("user_tree")
        user_tree.connect("row-activated", self.user_clicked)
        
        ##############
        
        #Login content stuff
        
        connect_btn = self.builder.get_object("login_connect_btn")
        connect_btn.connect("clicked", self.connect_clicked)
        
        #####################
        
        
        #Private Message Stuff
        
        pm_send_btn = self.builder.get_object("private_message_send")
        pm_send_btn.connect("clicked", self.private_send_clicked)
        
        pm_okay_btn = self.builder.get_object("private_message_ok")
        pm_okay_btn.connect("clicked", lambda x: self.display_main())
        
        ######################
        
        self.window.show_all()
        
        self.display_login()
        
    #Misc Methods    
    def quit(self, something, something_else):
        self.logged_in = False
        #Gtk.main_quit()
        if (self.cf.instance != None):
            self.cf.instance.transport.loseConnection()
        
        reactor.stop()
        
    def _autoscroll(self, *args):
        """The actual scrolling method"""
        adj = self._sw.get_vadjustment()
        adj.set_value(adj.get_upper() - adj.get_page_size())
        
    def entry_keypress(self, widget, event):
        if event.keyval == 65293:
            self.send_message()
            return True
        
        return False
    #End Misc Methods    
        
    def send_message(self):
        send_entry = self.builder.get_object("send_entry")
        txt = send_entry.get_text()
        send_entry.set_text("")
        self.cf.instance.sendMessage(txt)
        
    ####################################
    ## Switching Around Visible Views ##
    ####################################
    
    def display_login(self, msg=None):
        self.hide_content_panes()
        
        self.window.add(self.main_login)
        self.main_login.show_all()
        
        #Set a nice message displaying what went wrong... 
        #If relevant.
        if (msg != None):
            err_lbl = self.builder.get_object("login_error_label")
            err_lbl.set_text(msg)
    
    def display_main(self):
        self.hide_content_panes() 
        
        self.window.add(self.main_content)
        self.main_content.show_all()
        
    def display_loading(self):
        self.hide_content_panes()
        
        self.window.add(self.main_loading)
        
        spinner = self.builder.get_object("spinner1")
        spinner.start()
        
        self.main_loading.show_all()
        
    def display_private(self, usr, msg=None):
        self.hide_content_panes()

        #If message is none, it is an initial message to a user
        #If message has content, it's displaing a private message,
        #and the person can respond.
        
        pm_label = self.builder.get_object("private_message_user")
        pm_label.set_markup("<span size='xx-large' weight='light'>" + usr + "</span>")
        
        in_content = self.builder.get_object("private_message_in_content")
        in_buff = in_content.get_buffer()
        in_buff.delete(in_buff.get_start_iter(), in_buff.get_end_iter())
        
        if (msg != None):
            in_buff.insert(in_buff.get_start_iter(), msg)
            
        self.window.add(self.main_private)
        self.main_private.show_all()
             
    #helper method to hide everything.
    def hide_content_panes(self):
        #Content
        try:
            self.window.remove(self.main_content)
        except:
            pass
        
        #Login        
        try: 
            self.window.remove(self.main_login)
        except:
            pass
        
        #Loading
        try:
            self.window.remove(self.main_loading)
        except:
            pass
        
        #Private
        try:
            self.window.remove(self.main_private)
        except:
            pass   
    #End Switcher methods    
        
        
    ##############    
    #Login Methods
    def connect_clicked(self, btn):
        uname_e = self.builder.get_object("login_uname_entry")
        server_e = self.builder.get_object("login_ip_entry")
        
        if (uname_e.get_text() != ""):
            self.login_to_server(server_e.get_text(), uname_e.get_text())
        else:
            err_lbl = self.builder.get_object("login_error_label")
            err_lbl.set_text("You must enter a user name")
        
    def login_to_server(self, server, uname):
        self.display_loading()
        
        if server == "":
            server = "127.0.0.1"
        
        
        self.cf.uname = uname
        reactor.connectTCP(server, 4020, self.cf)
        reactor.callLater(0.25, self.try_login, uname)
        
        self.logged_in = True
        
    def try_login(self, uname):
        if (self.cf.instance != None):
            self.cf.instance.login(uname)
            return True
        
        reactor.callLater(0.25, self.try_login, uname)
    #End Login Methods    
        
    #Private Message Methods    
    def user_clicked(self, view, index, column):
        to_user = self.user_model[index][0]
        self.display_private(to_user)
        
    def private_send_clicked(self, btn):
        to_user = self.builder.get_object("private_message_user").get_text()
        msg_buff = self.builder.get_object("private_message_content").get_buffer()
        msg_text = msg_buff.get_text(msg_buff.get_start_iter(), msg_buff.get_end_iter(), False)
        msg_buff.delete(msg_buff.get_start_iter(), msg_buff.get_end_iter())
        
        self.cf.instance.sendPrivateMessage(to_user, msg_text)
        
        self.display_main()
        
    #End PM Methods    
        
    ##############################
    ## Call backs from twisted. ##
    ##############################   
        
    def msg_rcvd_callback(self, user, msg):
        mt = self.builder.get_object("message_text")
        
        if mt.get_buffer() == None:
            buff = Gtk.TextBuffer()
        else:
            buff = mt.get_buffer()
        
        mt.set_buffer(buff)
        
        ei = buff.get_end_iter()
        
        #Should probably find nicer colors here...
        if (self.o_c_tag == None):
            self.o_c_tag = buff.create_tag( "them_colored", foreground="#FFFF00", background="#0000FF")      
            
        if (self.m_c_tag == None):
            self.m_c_tag = buff.create_tag( "me_colored", foreground="#FFFF00", background="#F3C300")      
            
        if (user == self.cf.uname):
            buff.insert_with_tags(ei, user + ":" , self.m_c_tag)
        else:
            buff.insert_with_tags(ei, user + ":" , self.o_c_tag)
        
        ei = buff.get_end_iter()
        buff.insert(ei, " " + msg + "\n")
                
    def user_list_callback(self, users):
        #Update the user list store
        self.user_model.clear()
        
        for u in users:
            self.user_model.append([u])
        
    def welcome_callback(self):
        #unlock the ui and do things in this method. 
        self.display_main()
        
    def login_callback(self, msg):
        self.display_login(msg)
        
    def private_callback(self, uname, msg):
        self.display_private(uname, msg)
    #End Callback Methods
        
if __name__ == "__main__":
    client = TISCaPClient()
    client.start()