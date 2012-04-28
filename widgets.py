# -*- coding: UTF-8 -*-
# -*- Mode: Python; py-indent-offset: 4 -*-
# Multi Media Converter that utilize gstreamer and/or ffmpeg
# Copyright © 2008-2012, Ojuba.org <core@ojuba.org>
# Released under terms of Waqf Public License

from gi.repository import Gtk, Gdk
from dects import *

license=_("""
    Released under terms of Waqf Public License.
This program is free software; you can redistribute it and/or modify
it under the terms of the latest version Waqf Public License as
published by Ojuba.org.

    This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

    The Latest version of the license can be found on
"http://waqf.ojuba.org/license"

    """)
class comboBox(Gtk.HBox):
    def __init__(self, caption, List, connect=None):
        Gtk.HBox.__init__(self,False,4)
        self.List=List
        cb_list = Gtk.ListStore(str)
        self.cb = Gtk.ComboBox.new_with_model(cb_list)
        cell = Gtk.CellRendererText()
        self.cb.pack_start(cell, True)
        warp_width = 1
        self.cb.add_attribute(cell, 'text', 0)
        if len(List) > 10:
            warp_width = len(List) / 10
            self.cb.set_wrap_width(warp_width)
        self.build_list_cb(List)
        self.cb.set_size_request(100,-1)
        self.pack_start(Gtk.Label(caption),False,False,4)
        self.pack_start(self.cb,True,True,4)
        if connect:
            self.cb.connect('changed', connect)
            
    def build_list_cb(self, List):
        self.List = List
        cb_list = self.cb.get_model()
        cb_list.clear()
        for i in List:
          cb_list.append([i])
        self.cb.set_active(0)
        
    def set_active(self, v):
        try: self.cb.set_active(self.List.index(v))
        except ValueError: pass
    
    def get_active(self):
        tree_iter = self.cb.get_active_iter()
        if not tree_iter: return
        return self.cb.get_model()[tree_iter][0]
    
class add_dlg(Gtk.FileChooserDialog):
    def __init__(self, parent):
        Gtk.FileChooserDialog.__init__(self,_("Select files to convert"),
                                       parent=parent,
                                       buttons =(Gtk.STOCK_CANCEL,
                                                 Gtk.ResponseType.REJECT,
                                                 Gtk.STOCK_OK, 
                                                 Gtk.ResponseType.ACCEPT))
        ff=Gtk.FileFilter()
        ff.set_name(_('All media files'))
        ff.add_mime_type('video/*')
        ff.add_mime_type('audio/*')
        ff.add_pattern('*.[Rr][AaMm]*')
        self.add_filter(ff)
        ff=Gtk.FileFilter()
        ff.set_name(_('All video files'))
        ff.add_mime_type('video/*')
        ff.add_pattern('*.[Rr][AaMm]*')
        self.add_filter(ff)
        ff=Gtk.FileFilter()
        ff.set_name(_('All audio files'))
        ff.add_mime_type('audio/*')
        ff.add_pattern('*.[Rr][AaMm]*')
        self.add_filter(ff)    
        ff=Gtk.FileFilter()
        ff.set_name(_('All files'))
        ff.add_pattern('*')
        self.add_filter(ff)
        self.set_select_multiple(True)
        self.connect('delete-event', lambda *w: self.hide())
        self.connect('response', lambda *w: self.hide())

class about_dlg(Gtk.AboutDialog):
    def __init__(self, Parent):
        Gtk.AboutDialog.__init__(self, parent = Parent)
        self.set_default_response(Gtk.ResponseType.CLOSE)
        try: self.set_program_name(_("MiMiC"))
        except AttributeError: pass
        self.set_logo_icon_name('ojuba-mimic')
        self.set_name(_("MiMiC"))
        self.set_wrap_license(True)
        self.set_copyright(_("Copyright © 2008-2012 Ojuba.org <core@ojuba.org>"))
        self.set_comments(_("Multi Media Converter"))
        self.set_license(license)
        self.set_website("http://www.ojuba.org/")
        self.set_website_label("http://www.ojuba.org")
        self.set_authors(["Muayyad Saleh Alsadi <alsadi@ojuba.org>",
                          "Ehab El-Gedawy <ehabsas@gmail.com>",
                          "Faisal Shamikh <chamfay@gmail.com>"])
        self.connect('delete_event', self.delete)
        self.run()
        self.destroy()
    
    def delete(self, widget, data):
        return True

class MessageDialog(Gtk.MessageDialog):
    __MsgTypes={
                    'sure': [Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO],
                    'info': [Gtk.MessageType.INFO, Gtk.ButtonsType.OK], 
                    'error': [Gtk.MessageType.ERROR, Gtk.ButtonsType.CLOSE],
                    'wait': [Gtk.MessageType.OTHER ,Gtk.ButtonsType.NONE]
                }
    def __init__(self, msg_type, sec_text, parent, text=''):
        msg=None
        if not msg_type == 'wait': msg=sec_text
        Gtk.MessageDialog.__init__(self, parent , 1, self.__MsgTypes[msg_type][0],
                                     self.__MsgTypes[msg_type][1], text)
        self.format_secondary_text(msg)
            
def sure(msg, parent=None, sec_msg=''):
    dlg = MessageDialog('sure', msg, parent, sec_msg)
    r = dlg.run()
    dlg.destroy()
    return r==Gtk.ResponseType.YES

def info(msg, parent=None, sec_msg=''):
    dlg = MessageDialog('info', msg, parent, sec_msg)
    r = dlg.run()
    dlg.destroy()
    return True

def error(msg, parent=None, sec_msg=''):
    dlg = MessageDialog('error', msg, parent, sec_msg)
    r = dlg.run()
    dlg.destroy()
    return True
    
def update_combo(c, ls):
    c.get_model().clear()
    for i in ls: c.append_text(i)

def create_combo(c, ls, w=1):
    c.set_entry_text_column(0) 
    c.set_wrap_width(w)
    for i in ls:
        c.append_text(i)
    c.set_active(0)
    return c

