#!/usr/bin/python
from gi.repository import Gtk, GLib
#from communicator import CommThread, ClientCommand, ServerReply, Reciever, ClientFac
from communicator import ClientFac
import Queue
import threading
import string

from twisted.internet import protocol, gtk3reactor
gtk3reactor.install()
from twisted.internet import reactor

class TISCaPClient:
    def __init__(self):
        self.server = None
        
        self.uname = None
        
        self.builder = None
        self.window = None
        
        #This should be eliminated
        self.o_c_tag = None
        self.m_c_tag = None
        #End elimination...
    
    def start(self):         
        self.builder = Gtk.Builder()
        self.builder.add_from_file("ui.glade")
        
        self.setup_ui()

        
        self.cf = ClientFac(self.msg_rcvd_callback, self.user_list_callback,
                            self.private_callback, self.welcome_callback, self.error_callback, self.login_callback)
        
        reactor.run()
        

    def setup_ui(self):
        self.window = self.builder.get_object("main_window")
        self.window.connect("delete-event", self.quit)
        
        self.window.set_title("Yet Another TISCaP Client")
        
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
        
        utf8_btn = self.builder.get_object("char_btn")
        utf8_btn.connect("clicked", self.silly_char)
        
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
                
        #Prevent the user from going bonkers with their uname
        def filter_chars_check_input(entry, *args):
            text = entry.get_text().strip()
            entry.set_text(''.join([i for i in text if i in string.ascii_letters]))
            
            if (len(text) > 0):
                connect_btn.set_sensitive(True)
            else:
                connect_btn.set_sensitive(False)
                
        uname_entry = self.builder.get_object("login_uname_entry")
        uname_entry.connect('changed', filter_chars_check_input)
                
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
        #Gtk.main_quit()
        if (self.cf.instance != None):
            self.cf.instance.close()
        
        reactor.stop()
        
    def _autoscroll(self, *args):
        """The actual scrolling method"""
        adj = self._sw.get_vadjustment()
        adj.set_value(adj.get_upper() - adj.get_page_size())
        
    def entry_keypress(self, widget, event):
        if event.keyval == 65293 and len(widget.get_text()) > 0:
            self.send_message()
            return True
        
        send_btn = self.builder.get_object("send_btn")
        if len(widget.get_text()) == 0:
            #Make button active
            send_btn.set_sensitive(False)
        else: 
            #Make button inactive
            send_btn.set_sensitive(True)
        
        return False
    #End Misc Methods    
        
    def send_message(self):
        send_entry = self.builder.get_object("send_entry")
        send_btn = self.builder.get_object("send_btn")
        txt = send_entry.get_text()
        send_entry.set_text("")
        send_btn.set_sensitive(False)
        
        print "Sending " + txt
        
        self.cf.instance.sendMessage(txt)
        
    def silly_char(self, btn):
        pass
    
    def return_random_char(self):
        return 'K'
        
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
        in_label = self.builder.get_object("private_in_text")
        in_buff = in_content.get_buffer()
        in_buff.delete(in_buff.get_start_iter(), in_buff.get_end_iter())
        
            
        self.window.add(self.main_private)
        self.main_private.show_all()
        
        if (msg != None):
            in_buff.insert(in_buff.get_start_iter(), msg)
        else:
            in_content.hide()
            in_label.hide()
             
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
        
        #This else shouldn't ever happen I guess
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
                
    def try_login(self, uname):
        if (self.cf.instance != None):
            self.cf.instance.login(uname)
            self.uname = uname
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
            self.o_c_tag = buff.create_tag( "them_colored", foreground="#FFFFFF", background="#2C30FF", weight=700)      
            
        if (self.m_c_tag == None):
            self.m_c_tag = buff.create_tag( "me_colored", foreground="#FFFFFF", background="#3BB212")      
            
        if (user == self.cf.uname):
            buff.insert_with_tags(ei, user + ":" , self.m_c_tag)
        else:
            buff.insert_with_tags(ei, user + ":" , self.o_c_tag)
        
        ei = buff.get_end_iter()
        buff.insert(ei, " " + msg + "\n")
                
    def user_list_callback(self, users):
        #Update the user list store
        self.user_model.clear()
        
        #Make the user's name be at the top in bold.
        users.remove(self.uname)
        self.user_model.append([self.uname, 700])
        
        for u in users:
            self.user_model.append([u, 400])
        
    def welcome_callback(self):
        #unlock the ui and do things in this method. 
        self.display_main()
        
    def login_callback(self, msg):
        self.display_login(msg)
        
    def private_callback(self, uname, msg):
        self.display_private(uname, msg)
        
    def error_callback(self, data):
        #Do things here to the status bar thingimebob.
        #sb = self.builder.get_object("info_bar")
        #sb.push(0, str(data))
        
        #I don't like status bars. So this won't have one.
        pass
        
        
    #End Callback Methods
        
if __name__ == "__main__":
    client = TISCaPClient()
    client.start()