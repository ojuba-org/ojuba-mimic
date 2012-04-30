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

class spinButton(Gtk.SpinButton):
    """
        comboBox = Gtk.SpinButton
            Adj              : Adjustment tuple
            
        Attributes:
            None             : there is no Attributes
        
        Methods:
            set_Adjustment   : set_adjustment
            
    """
    __gtype_name__ = "MiMicSpinButton"
    def __init__(self, *Adj):
        Gtk.SpinButton.__init__(self)
        self.set_Adjustment(*Adj)
    
    def set_Adjustment(self, *Adj):
        #lo, va, up, ps, st, pa = Adj
        adj = Gtk.Adjustment(*Adj)
        self.set_adjustment(adj)
        
class hScale(Gtk.HScale):
    """
        comboBox = Gtk.HScale
            Adj              : Adjustment tuple
           
        Attributes:
            None             : there is no Attributes
        
        Methods:
            set_Adjustment   : set_adjustment
            
    """
    __gtype_name__ = "MiMicHScale"
    def __init__(self, *Adj):
        Gtk.HScale.__init__(self)
        self.set_property("value-pos", Gtk.PositionType.LEFT)
        self.set_Adjustment(*Adj)
    
    def set_Adjustment(self, *Adj):
        #va, lo, up, st = Adj
        adj = Gtk.Adjustment(*Adj)
        self.set_adjustment(adj)
        
class labeldBox(Gtk.HBox):
    """
        labeldBox = Gtk.HBox
            caption          : wiget title
            widgets          : widget you may need to pack in child box
            chk_box          : CheckBox to enable/disabl child box
            cap_width        : title width
            
        Attributes:
            childs:
                child_hbox   : child HBox
                chk          : CheckButton
        
        Methods:
            set_active       : Change CheckButton activety, True is default
            get_active       : Return CheckButton activety
            
    """
    __gtype_name__ = "MiMicLabeldBox"
    def __init__(self, caption, widgets = [], chk_box = False, cap_width = 200):
        Gtk.HBox.__init__(self, False, 4)
        if chk_box:
            self.chk = c = Gtk.CheckButton(caption)
            c.connect('toggled', lambda a: hb.set_sensitive(self.chk.get_active()))
            hb = Gtk.HBox(False, 4)
            self.pack_start(c, False, False, 4)
            self.pack_start(hb, True, True, 2)
            hb.set_sensitive(False)
        else:
            hb = self
            c = Gtk.Label(caption, xalign = 0)
            self.pack_start(c, False, False, 4)
        if cap_width:
            c.set_size_request(cap_width, -1)
        if widgets:
            for w in widgets:
                stat = type(w) in [hScale, Gtk.ComboBox]
                hb.pack_start(w, stat, stat, 4)
   
    def get_active(self, *w):
        """
            for check button
            return get_active()
        """
        return self.chk.get_active()
    
    def set_active(self, v=True, *w):
        """
            for check button
            return set_active(v)
            v = True by default
        """
        return self.chk.set_active(v)
        
class comboBox(labeldBox):
    """
        comboBox = labeldBox
            caption          : wiget title
            List             : ComboBox List
            callback         : fuction to connect with ComboBox
            chk_box          : CheckBox to enable/disabl child box
            widgets          : widget you may need to pack in child box
            cap_width        : title width
            
        Attributes:
            List             : ComboBox List
            childs:
                cb           : ComboBox widget
                child_hbox   : child HBox
                chk          : CheckButton
        
        Methods:
            __connect        : To connect ComboBox with object and arges ( internal method )
            build_list_cb    : Build ComboBox list
            set_value        : To set ComboBox active text, or id
            get_value        : Retrun ComboBox active text, or id
            
    """
    __gtype_name__ = "MiMicComboBox"
    def __init__(self, caption, List, callback = None, chk_box = False, widgets = [], cap_width = 200):
        
        self.List = List
        cb_list = Gtk.ListStore(str)
        self.cb = Gtk.ComboBox.new_with_model(cb_list)
        cell = Gtk.CellRendererText()
        self.cb.pack_start(cell, True)
        warp_width = 1
        self.cb.add_attribute(cell, 'text', 0)
        
        if len(List) > 5:
            warp_width = len(List) / 5
            self.cb.set_wrap_width(warp_width)
        self.build_list_cb(List)
        if widgets:
            widgets.insert(0, self.cb)
        else:
            widgets = [self.cb]
        labeldBox.__init__(self, caption, widgets, chk_box, cap_width)
        
        if callback:
            self.__connect(callback)
            
    def __connect(self, callback, *args):
        self.cb.connect_object('changed', callback, self, *args)
        
    def build_list_cb(self, List):
        """
            for combo box 
            build module list
        """
        self.List = List
        cb_list = self.cb.get_model()
        cb_list.clear()
        for i in List:
          cb_list.append([i])
        self.cb.set_active(0)
        
    def set_value(self, v, by_id = False):
        """
            for combo box 
            return set active by text
            
            by_id = False   : set combo box active text
                  = True    : set combo box active id
        """
        if by_id:
            return self.cb.set_active(v)
        try:
            self.cb.set_active(self.List.index(v))
        except ValueError, e:
            print e
    
    def get_value(self, by_id = False):
        """
            for combo box
            return active text
            
            by_id = False   : return combo box active text
                  = True    : return combo box active id
        """
        if by_id:
            return self.cb.get_active()
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

def create_chk_combo(c, ls, w=1):
    cb = comboBox(None, ls)
    chk = checkBox(c, cb)
    return chk
