# -*- coding: UTF-8 -*-
# -*- Mode: Python; py-indent-offset: 4 -*-
"""
    Multi Media Converter that utilize gstreamer and/or ffmpeg
    Copyright © 2008-2015, Ojuba.org <core@ojuba.org>
    Released under terms of Waqf Public License
"""

from gi.repository import GObject
import random
import signal
import re
from urllib import unquote
from subprocess import Popen, PIPE
from datetime import timedelta
from widgets import *

    
class MainWindow(Gtk.Window):
    """
    Ojuba Multi media converter main wondow class
    
    Attributes:
          cur_src_dir = sources directory
          working_ls  = this list to control subprocess
          ouput_fn    = temp file to save subprocess outputs
          if_dura     = input file duration
          done_ls     = to control done works
          if_dura_re  = input file duration regular expression
          of_dura_re  = output file duration regular expression
    """
    __gtype_name__ = 'Ojuba-MiMiC_Main_Window'
    if_dura_re = re.compile(r'''Duration:\s*(\d+):(\d+):(\d+.?\d*)''')
    of_dura_re = re.compile(r'''time=\s*(\d+):(\d+):(\d+.?\d*)''')
    def __init__(self):
        Gtk.Window.__init__(self)
        self.set_default_icon_name('ojuba-mimic')
        self.set_border_width(4)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.cur_src_dir = None
        self.working_ls = []
        self.ouput_fn = '/tmp/mimic.tmp'
        self.if_dura = 0
        self.done_ls = []
        self.fileman = FileManager()
        self.set_title(_('MiMiC :: Multi Media Converter'))
        self.connect('destroy', self.quit_cb)
        self.connect('delete_event', self.quit_cb)
        self.set_size_request(-1, 350)
        
        ## prepare dnd 
        targets = Gtk.TargetList.new([])
        targets.add_uri_targets((1<<5)-1)
        self.drag_dest_set(Gtk.DestDefaults.ALL, [], Gdk.DragAction.COPY)
        self.drag_dest_set_target_list(targets)
        self.connect('drag-data-received',self.drop_data_cb)
        
        ## main container
        vb = Gtk.VBox(False, 0) 
        self.add(vb)
        
        ## banner box
        l_banner_box = Gtk.EventBox()
        vb.pack_start(l_banner_box,False, False, 0)
        ## banner box color
        # (Gtk.StateType.NORMAL, Gtk.StateType.ACTIVE, 
        # Gtk.StateType.PRELIGHT, Gtk.StateType.SELECTED, 
        # Gtk.StateType.INSENSITIVE)
        for i in range(0,5):
            l_banner_box.modify_bg(Gtk.StateType(i), Gdk.color_parse("#fffff8"))
        l_banner=Gtk.Label()
        l_banner.set_justify(Gtk.Justification.CENTER)
        l_banner.set_markup('''<span face="Simplified Naskh" color="#2040FF" 
                               size="x-large">%(verse)s</span>'''
                               % {'verse':random.choice(banner_list)})
        l_banner_box.add(l_banner)
        
        ## new format 
        self.c_to = comboBox(_('To:'), sorted(formats), self.c_to_cb, cap_width = 0)
        
        # TODO: add axel 
        b_add = Gtk.Button(stock = Gtk.STOCK_ADD)
        b_add.connect('clicked', self.add_files_cb)
        b_rm = Gtk.Button(stock = Gtk.STOCK_REMOVE)
        b_rm.connect('clicked', self.rm_cb)
        b_clear = Gtk.Button(stock = Gtk.STOCK_CLEAR)
        b_clear.connect('clicked', self.clear_cb)
        self.b_convert = Gtk.Button(stock = Gtk.STOCK_CONVERT)
        self.b_convert.connect('clicked', self.convert_cb)
        self.b_stop = Gtk.Button(stock = Gtk.STOCK_STOP)
        self.b_stop.connect('clicked', self.stop_cb)
        b_about = Gtk.Button(stock = Gtk.STOCK_ABOUT)
        b_about.connect("clicked", lambda *args: about_dlg(self))

        self.tools_hb = d_hb = Gtk.HBox(False,0)
        self.ctoools_hb = Gtk.HBox(False,0)
        ## pack toolbar tools
        for i in (b_rm, b_clear, Gtk.VSeparator(), self.c_to):
            self.ctoools_hb.pack_start(i,False, False, 2)
        for i in (b_add, Gtk.VSeparator(),self.ctoools_hb):
            d_hb.pack_start(i,False, False, 2)
            d_hb.set_spacing(4)
        hb = Gtk.HBox(False,0); vb.pack_start(hb,False, False, 0)
        for i in (d_hb,self.b_convert,self.b_stop,b_about):
            hb.pack_start(i,False, False, 2)
            hb.set_spacing(4)

        ## ScrolledWindow
        scroll = Gtk.ScrolledWindow()
        scroll.set_shadow_type(Gtk.ShadowType.IN)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        
        ## files tree
        # fn, os.path.basename, percent, pulse, label
        self.files = Gtk.ListStore(str, str, float, int, str) 
        self.files_list = Gtk.TreeView(self.files)
        self.files_list.set_size_request(-1, 350)
        self.files_list.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)
        scroll.add(self.files_list)
        vb.pack_start(scroll,True, True, 0)
        vb.set_spacing(8)
        
        # setting the list
        cells = []
        cols = []
        cells.append(Gtk.CellRendererText())
        cols.append(Gtk.TreeViewColumn(_('Files'), cells[-1], text = 1))
        cols[-1].set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        cols[-1].set_resizable(True)
        cols[-1].set_expand(True)
        cells.append(Gtk.CellRendererProgress());
        cols.append(Gtk.TreeViewColumn(' \t\t%s\t\t '%_('Status'),
                                        cells[-1], value = 2,
                                        pulse = 3,text = 4))
        cols[-1].set_expand(False)
        self.files_list.set_headers_visible(True)
        self.b_stop.set_sensitive(False)
        self.b_convert.set_sensitive(False)
        for i in cols:
            self.files_list.insert_column(i, -1)
            
        ## new format 
        #self.c_to = comboBox(_('New format: '), sorted(formats), self.c_to_cb)
        #vb.pack_start(self.c_to,False, True, 0)
        
        ## self options
        self.options = options(self)
        if self.options.conf.has_key('src_dir'):
            self.cur_src_dir = self.options.conf['src_dir']
        expander = Gtk.Expander(label = _('Options'))
        expander.add(self.options)
        expander.set_resize_toplevel(True)
        vb.pack_start(expander, False, False,0)
        
        s_hb = Gtk.HBox(False,0); vb.pack_start(s_hb,False, False, 0)
        self.status_bar = s = Gtk.Statusbar()

        s_hb.pack_start(s, True,True,2)
        self.context_id = context_id = self.status_bar.get_context_id("STATUS_D")
        self.status_bar.push(context_id,_('Add files, Then click Convert!'))

        self.popupMenu = Gtk.Menu()
        self.build_popup_Menu()
        self.files_list.connect("button-press-event", self.do_popup)
        
        ## for test proposes
        # sample list for testing
        #ls=[("/usr/share/file1.avi",10.0),("file2",20)]
        #self.files.clear()
        #for j,k in ls: self.files.append([j,os.path.basename(j),k,-1,None])
        #self.files[(1,)] = (self.files[1][0], self.files[1][1], 90,-1,"Done %d %%" % 90)
        #self.options.set_sensitive(False)
        #print self.options
        
        GObject.timeout_add(250, self.progress_cb)
        self.show_all()
        ## to set current quality
        self.c_to_cb(self.c_to)

    def active_controlls(self, v=False):
        self.b_stop.set_sensitive(v)
        self.b_convert.set_sensitive(not v)
        self.tools_hb.set_sensitive(not v)
        self.ctoools_hb.set_sensitive(not v)
        self.popupMenu.get_children()[2].set_sensitive(not v)
        self.popupMenu.get_children()[3].set_sensitive(not v)
        
    def build_popup_Menu(self):
        i = Gtk.MenuItem(_("Open output folder"))
        i.connect("activate", self.open_odir_cb)
        self.popupMenu.add(i)
        self.popupMenu.add(Gtk.SeparatorMenuItem.new())
        i = Gtk.ImageMenuItem.new_from_stock(Gtk.STOCK_REMOVE, None)
        i.connect("activate", self.rm_cb)
        self.popupMenu.add(i)
        i = Gtk.ImageMenuItem.new_from_stock(Gtk.STOCK_CLEAR, None)
        i.connect("activate", self.clear_cb)
        self.popupMenu.add(i)
        
    def do_popup(self, widget, event):
        iters = self.get_Iters()
        if event.button == 3 and len(iters) > 0:
            self.popupMenu.show_all()
            self.popupMenu.popup(None, self, None, None, 3, Gtk.get_current_event_time())
            return True
            
    def get_Iters(self):
        sel_rows = self.files_list.get_selection().get_selected_rows()[1]
        return map(lambda a: self.files.get_iter(a), sel_rows)
        
    def open_odir_cb(self, *args):
        self.fileman._opend={}
        odir=self.options.dst_b.get_filename()
        if self.options.dst_o2.get_active():
            self.fileman.run_file_man(odir)
        else:
            iters = self.get_Iters()
            for i in iters:
                odir = os.path.dirname(self.files[self.files.get_path(i)][0])
                self.fileman.run_file_man(odir)
                
    def clear_cb(self, *args):
        ln=len(self.files)
        self.files.clear()
        self.done_ls=[]
        self.rmstatus(ln)
        
    def rm_cb(self, *args):
        iters = self.get_Iters()
        for i in iters:
            self.files.remove(i)
        self.rmstatus(len(iters))
        
    def rmstatus(self, fc):
        self.status_bar.push(self.context_id, '%i %s' %(fc, _('File/Files removed')))
        
    def progress_cb(self, *args):
        #print "*", len(working_ls)
        if not len(self.files):
            self.b_stop.set_sensitive(False)
            self.b_convert.set_sensitive(False)
            self.tools_hb.set_sensitive(True)
            self.ctoools_hb.set_sensitive(False)
            #self.active_controlls(False)
            return True
        self.active_controlls(len(self.working_ls)>0)
        self.ctoools_hb.get_children()[0].set_sensitive(len(self.get_Iters())>0)
        if len(self.working_ls) <= 0: return True
        self.progressstatus()
        if not self.working_ls[0][0]:
            self.start_subprocess()
            return True
        r = self.working_ls[0][0].poll()
        if r == None:
            self.progress()
            return True
        elif r == 0:
            i=self.files[(self.working_ls[0][2],)]
            i[2]= 100.0
            i[3]= -1
            i[4]=_('Done')
            # add to done items
            done_item = self.working_ls[0][-1]
            if not done_item in self.done_ls: self.done_ls.append(done_item)
        else:
            i=self.files[(self.working_ls[0][2],)]
            i[2]= 100.0
            i[3]= -1
            i[4]='%s %d' % (_('Error'), r)
            # clean on error 
            if os.path.isfile(self.ouput_fn):
                os.unlink(self.ouput_fn)
            if os.path.isfile(self.working_ls[0][4]):
                os.unlink(self.working_ls[0][4])
        self.working_ls.pop(0)
        if len(self.working_ls)>0: stat_str=''
        else: stat_str=_('Finished:')
        self.progressstatus(stat_str)
        return True
        
    def progressstatus(self, txt=''):
        if txt=='': txt=_('Converting:')
        cm=len(self.done_ls)
        tot=len(self.files)
        if cm>tot: cm=tot
        self.status_bar.push(self.context_id,'%s %i %s %i %s!' %(txt,cm,_('file/files of'),tot,_('Compleated')))
        
    def progress(self, *args):
        p, icmd, i, fn, ofn, sn = self.working_ls[0]
        #print self.get_dura_cb()
        #of_dura=self.get_dura_cb_old(ofn)
        #if of_dura < 0: self.pulse_cb(i); return True
        #if_dura=self.get_dura_cb_old(fn)
        #if if_dura < of_dura: self.pulse_cb(i); return True
        if_dura, of_dura = self.get_dura_cb()
        pct = (float(of_dura) / if_dura) * 100.0
        self.files[(i,)][3] = -1
        self.files[(i,)][2] = pct
        i = self.files[(self.working_ls[0][2],)]
        i[4] = '%0.2f%%' % pct
        Gtk.main_iteration()
        return True;

    def pulse_cb(self, i):
        self.files[(i,)][2]=0
        self.files[(i,)][3]=int(abs(self.files[(i,)][3])+1)
        Gtk.main_iteration()

    
    def get_dura_cb(self):
        out = open(self.ouput_fn,'r').read().strip()
        ifd = self.if_dura_re.findall(out)
        ofd = self.of_dura_re.findall(out)
        try: 
            i, o = ifd[-1], ofd[-1]
        except IndexError:
            return 100, 0
        return self.convert_to_sec(map(lambda a: float(a),i)), self.convert_to_sec(map(lambda a: float(a),o))
    
    
    def convert_to_sec(self, dd):
        return timedelta(hours=dd[0], minutes=dd[1], seconds=dd[2]).total_seconds()
    
    def get_dura_cb_old(self, fn):
        if not os.path.isfile(fn): return -1
        c = Popen(['ffmpeg', '-i', fn], stdout=PIPE, stderr=PIPE)
        o, e = c.communicate()
        dd=self.if_dura_re.search(e)
        if not hasattr(dd, 'groups'): return -1
        dd = map(lambda a: float(a), dd.groups())
        return timedelta(hours=dd[0], minutes=dd[1], seconds=dd[2]).total_seconds()
        
    def start_subprocess(self):
        TMP_F=file(self.ouput_fn,'w')
        TMP_F.write('')
        if self.working_ls[0][3]==self.working_ls[0][4]:
            if self.options.x_o3.get_active():
                if not self.rename_cb(): return self.skiped()
            else: 
                return self.skiped()
        if os.path.exists(self.working_ls[0][4]):
            if self.options.x_o3.get_active():
                if not self.rename_cb(): return self.skiped()
            elif self.options.x_o1.get_active():
                return self.skiped()
        cmd = self.working_ls[0][1]
        self.working_ls[0][0] = Popen(cmd, stderr = TMP_F, stdout = PIPE)
        i = self.files[(self.working_ls[0][2],)]
        i[2] = 0.0
        i[3] = -1
        i[4] = _('Converting ...')
        #self.working_ls.append()=[None,icmd,working_on,fn,ofn]

    def drop_data_cb(self, widget, dc, x, y, selection_data, info, t):
        if len(self.working_ls)>0: print 'Sorry, You can not add files while converting ...'; return 
        for i in selection_data.get_uris():
            if i.startswith('file://'):
                f=unquote(i[7:])
                if os.path.isfile(f):
                    self.files.append([f,os.path.basename(f), 0.0, -1,_('Not started')])
                else:
                    print "Can not add folders [%s]" % f
            else:
                print "Protocol not supported in [%s]" % i
        self.addstatus(len(self.files))
        self.options.conf['src_dir']=self.cur_src_dir
        self.options.save_conf()
    
    def add_files_cb(self, *args):
        dlg = add_dlg(self)
        if self.cur_src_dir:
            dlg.set_current_folder(self.cur_src_dir)
        if (dlg.run() == Gtk.ResponseType.ACCEPT):
            for i in dlg.get_filenames():
                self.files.append([i, os.path.basename(i), 0.0, -1, _('Not started')])
            self.addstatus(len(self.files))
            self.cur_src_dir=os.path.dirname(i)
        self.options.conf['src_dir']=self.cur_src_dir
        self.options.save_conf()
        dlg.unselect_all()

    def addstatus(self, fc):
        self.status_bar.push(self.context_id,'%s %i %s' %(
                             _('Click Convert, to start converting'),
                             fc,
                             _('file/files'))
                             )
        
    def c_to_cb(self, c,*args):
        """
            Destination format combo box callback
        """
        frm = formats[self.c_to.get_value()]
        ## Disable/Enable video settings widget
        for i in (self.options.br_v_c,  # Video Bitrates widget
                  self.options.scale_c, # Video Resize widget
                  self.options.q_v_c):  # Video Quality widget
            i.set_active(False)
            i.set_sensitive(frm[1])
        ## set check box activity
        for i,j in ((frm[3],self.options.q_a_c),     # Audio Quality widget
                      (frm[4],self.options.q_v_c),   # Video Quality widget
                      (frm[5],self.options.br_a_c),  # Audio Bitrates widget
                      (frm[6],self.options.br_v_c)): # Video Bitrates widget
            j.set_active(i)
            if not i:
                j.set_active(False)
        ## set Audio Samplerate
        self.options.ar_r_c.set_sensitive(frm[7])
        self.options.ar_r_c.set_active(frm[7])
        self.options.ar_r_c.set_value(str(frm[8]))
        # Audio Quality scal wdget
        adj = (frm[10], frm[11], frm[12], 1)
        self.options.q_a.set_Adjustment(*adj)
        self.options.q_a_c.set_sensitive(int(self.options.q_a.get_value()))
        # Video Quality scal wdget
        adj = (frm[14], frm[15], frm[16], 1)
        self.options.q_v.set_Adjustment(*adj)
        self.options.q_v_c.set_sensitive(int(self.options.q_v.get_value()))
        # Audio Bitrates value
        val = frm[17]/1000
        self.options.br_a_c.set_value('{}k'.format(val))
        # Video Bitrates value
        self.options.br_v_c.set_value(str(frm[20]))

        ## set quality
        q = self.options.quality_l.get_value(True)
        quality = frm[-1][q]
        for i, k in enumerate((self.options.br_a_c,
                              self.options.ar_r_c,
                              self.options.br_v_c,
                              self.options.scale_c)):
            s, b = str(quality[i]), bool(quality[i])
            if b:
                k.set_value(s)
                k.set_active(b)
        
    def convert_cb(self, *args):
        self.active_controlls(True)
        frm = formats[self.c_to.get_value()]
        cmd = self.options.build_cmd(frm, self)
        if not cmd:
            return
        if self.options.dst_o2.get_active(): 
            oodir=self.options.dst_b.get_filename();
        else: 
            oodir=False
        self.working_ls = []
        for working_on,i in enumerate(self.files):
            fn=i[0]
            bfn=os.path.basename(fn)
            if not oodir: odir=os.path.dirname(fn)
            else: odir=oodir
            ofn=os.path.join(odir, bfn.partition('.')[0]+frm[0])
            #if fn==ofn or os.path.exists(ofn): i[4]='Exists; Skiped'; continue
            #i[2]=0; i[3]=-1; i[4]='Converting ...'
            
            icmd=self.cmd_to_list(fn,ofn,cmd)
            
            picmd=map(lambda a:a,icmd)
            picmd[3]='"%s"'%(picmd[3])
            picmd[-1]='"%s"'%(picmd[-1])
            print "***\n", ' '.join(picmd)
            serial=[cmd,fn]
            #print serial, self.done_ls
            # escape done items
            if not serial in self.done_ls:
                self.working_ls.append([None,icmd,working_on,fn,ofn,serial])
            #print icmd
            #working_fn=ofn; working_size=os.stat(fn)
            #r=os.system(icmd)
            #if r: i[2]=100; i[3]=-1; i[4]='Error %d' % r
            #else: i[2]=100; i[3]=-1; i[4]='Done'
            #files[(working_on,)][2]= 100
        working_on=-1 # not needed
        #if len(self.working_ls)>0:
        #    self.status_bar.push(self.context_id,_('Starting operations...'))

    def cmd_to_list(self, fn, ofn, cmd):
        s=["ffmpeg", "-y", "-i", fn]
        s.extend(cmd.split())
        s.append(ofn)
        return s
        
    def stop_cb(self, *args):
        self.progressstatus(_('Stoped:'))
        if os.path.isfile(self.ouput_fn): os.unlink(self.ouput_fn)
        for j in self.working_ls:
            if j[0]:
                try: os.kill(j[0].pid,signal.SIGTERM); os.unlink(j[4])
                except OSError: pass
                i=self.files[(self.working_ls[0][2],)]
                i[4]=_('Canceled')
        self.working_ls=[]
        self.active_controlls(False)
    
    def suffex_gen(self):
        for i in xrange(0,0xFFFF): yield str(i)
        for i in xrange(0,0xFFFF): yield '_'+str(i)
        for i in xrange(0,0xFFFF): yield '_'+str(i)
        for j in xrange(65,91):
            for i in self.suffex_gen(): yield chr(j)+str(i)

    def suggest_name(self, f):
        dn=os.path.dirname(f)
        fn=os.path.basename(f)
        b,d,e=fn.partition('.')
        for i in self.suffex_gen():
            f=os.path.join(dn,''.join((b,'_',i,d,e)))
            if not os.path.exists(f): return f
        return None

    def rename_cb(self):
        ofn=self.working_ls[0][4]=self.suggest_name(self.working_ls[0][4])
        if not ofn:
            i=self.files[(self.working_ls[0][2],)]; i[4]=_('Exists; Skipped');
            self.working_ls.pop(0); return False
        fn=self.working_ls[0][3]
        frm = formats[self.c_to.get_value()]
        cmd=self.options.build_cmd(frm, self)
        self.working_ls[0][1]=self.cmd_to_list(fn,ofn,cmd)
        return True

    def skiped(self):
        i = self.files[(self.working_ls[0][2],)]
        i[4] = _('Exists; Skipped')
        self.working_ls.pop(0)
        return 0

    def quit_cb(self, *w):
        if len(self.working_ls)>0:
            if not sure(_('There are corrently running oprations, Stop it?'), self):return True
        self.stop_cb()
        Gtk.main_quit()
        
class options(Gtk.Notebook):
    """
    """
    def __init__(self, win):
        Gtk.Notebook.__init__(self)
        self.cw_Stop = False
        self.win = win
        self.conf = {}
        self.scale_dict = {}
        for i in filter(lambda a: a != _("custom"),scale_ls):
            a = i.split(' ')
            self.scale_dict[a[1]] = i
            
        ## quality page
        self.quality_l = q = comboBox(_("Quality:"),
                                      [_("Low"), _("Normal"), _("High")],
                                      self.set_options_cb,
                                      cap_width = 100)
        ## create page and pack widgets ( page 1 )
        ##########################################
        self.create_page(_("Quality"), q)
        ##########################################
        
        ## save options page
        # dst widgets
        self.dst_o1 = o1 = Gtk.RadioButton.new_with_label_from_widget(None,_("same as source"))
        self.dst_o2 = o2 = Gtk.RadioButton.new_with_label_from_widget(self.dst_o1, _("fixed"))
        self.dst_b = b = Gtk.FileChooserButton(_("Select destination folder"))
        self.dst_b.set_action(Gtk.FileChooserAction.SELECT_FOLDER)
        dst_l = labeldBox(_("Save destination as:"), [o1, o2, b])
        # ifexist widgets
        self.x_o1 = o1 =Gtk.RadioButton.new_with_label_from_widget(None,_("Skip"))
        self.x_o2 = o2 =Gtk.RadioButton.new_with_label_from_widget(self.x_o1,_("Overwrite"))
        self.x_o3 = o3 =Gtk.RadioButton.new_with_label_from_widget(self.x_o1,_("Rename"))
        self.x_o3.set_active(True)
        x_l = labeldBox(_("If destination exists:"), [o1, o2, o3])
        ## create page and pack widgets ( page 2 )
        ##########################################
        self.create_page(_('Save'), dst_l, x_l)
        ##########################################
        
        ## audio settings page
        # Audio Bitrates widget
        ls = map(lambda i: str(i)+'k', list(range(8,17,8))+list(range(32,257,32)))
        self.br_a_c = comboBox(_("Audio Bitrates:"), ls, chk_box = True)
        
        # Audio Samplerate widget
        ls = map(lambda i: str(i), list(range(11025,48101,11025)+list(range(8000,48001,8000))) )
        self.ar_r_c = comboBox(_("Audio Samplerate:"), ls, chk_box = True)
        
        # Audio Quality widget
        adj = (3, 0, 10, 1)
        self.q_a = hScale(*adj)
        self.q_a_c = labeldBox(_("Audio Quality:"), [self.q_a], True)
        ## create page and pack widgets ( page 3 )
        ##########################################
        self.create_page(_('Audio'), self.br_a_c, self.ar_r_c, self.q_a_c)
        ##########################################
        
        ## video settings page
        # Video Bitrates widget
        ls = map(lambda i: str(i), list(range(200, 10001, 250)))
        self.br_v_c = comboBox(_("Video Bitrates:"), ls, chk_box = True)
        
        # Resize widget
        adj = (0, 0, 10000, 1, 10, 0)
        self.scale_w = spinButton(*adj)
        self.scale_h = spinButton(*adj)
        self.scale_c = comboBox(_("Resize:"),  # caption
                                scale_ls,      # list
                                self.scale_cb, # callback
                                True,          # with check button ?
                                # extra widgets
                                [self.scale_w, Gtk.Label("x"), self.scale_h]
                               )
        # Video Quality widget
        adj = (10, 0, 100,0)
        self.q_v = hScale(*adj)
        self.q_v_c = labeldBox(_("Video Quality:"), [self.q_v], True)
        ## create page and pack widgets ( page 4 )
        ##########################################
        self.create_page(_("Video"), self.br_v_c, self.scale_c, self.q_v_c)
        ##########################################
        
        ## advanced settings page
        # Corp widgets
        adj = (0, 0, 10000, 2, 10, 0)
        crp_ly1 = Gtk.Label(_("Top"))
        self.crp_dy1 = spinButton(*adj)
        
        crp_ly2 = Gtk.Label(_("Bottom"))
        self.crp_dy2 = spinButton(*adj)
        
        crp_lx1 = Gtk.Label(_("Left"))
        self.crp_dx1 = spinButton(*adj)
        
        crp_lx2 = Gtk.Label(_("Right"))
        self.crp_dx2 = spinButton(*adj)
        
        w = [crp_ly1, self.crp_dy1, crp_ly2, self.crp_dy2,
             crp_lx1, self.crp_dx1, crp_lx2, self.crp_dx2]
        self.crp_c = labeldBox(_("Crop"), w, True)

        # Pad widgets
        self.pad_c = Gtk.CheckButton(_("Pad"))

        pad_ly1 = Gtk.Label(_("Top"))
        self.pad_dy1 = spinButton(*adj)
        
        pad_ly2 = Gtk.Label(_("Bottom"))
        self.pad_dy2 = spinButton(*adj)
        
        pad_lx1 = Gtk.Label(_("Left"))
        self.pad_dx1 = spinButton(*adj)
        
        pad_lx2 = Gtk.Label(_("Right"))
        self.pad_dx2 = spinButton(*adj)
        
        w = [pad_ly1, self.pad_dy1, pad_ly2, self.pad_dy2,
             pad_lx1, self.pad_dx1, pad_lx2, self.pad_dx2]
        self.pad_c = labeldBox(_("Pad"), w, True)
        ## create page and pack widgets ( page 5 )
        ##########################################
        self.create_page(_("Advanced"), self.crp_c, self.pad_c)
        ##########################################
        
        self.apply_conf()
        
        ## apply calbacks
        # FIXME: comment out evry line !
        # TODO: set callbaks via classes
         
        self.dst_o2.connect('toggled', self.save_conf)
        self.x_o1.connect('toggled', self.save_conf)
        self.x_o2.connect('toggled', self.save_conf)
        self.dst_b.connect('file-set', self.save_conf)
        #self.dst_b.connect('current-folder-changed', self.save_conf)
        self.scale_w.connect('changed', self.scale_wh_cb,self.scale_w,self.scale_h,self.scale_c)
        self.scale_h.connect('changed', self.scale_wh_cb,self.scale_w,self.scale_h,self.scale_c)
        self.scale_w.connect('activate', self.scale_wh_cb,self.scale_w,self.scale_h,self.scale_c)
        self.scale_h.connect('activate', self.scale_wh_cb,self.scale_w,self.scale_h,self.scale_c)    
        self.scale_w.connect_after('focus-out-event', lambda a,*args: a.activate() and False)
        self.scale_h.connect_after('focus-out-event', lambda a,*args: a.activate() and False)
        self.dst_b.set_sensitive(self.dst_o2.get_active())
        self.scale_c.set_value("qvga 320x240")
        self.quality_l.set_value(1, True)
        
    def set_options_cb(self, c):
        c.cb.connect_object('changed', self.win.c_to_cb, self.win.c_to)
  
    def create_page(self, label, *widgets):
        vb=Gtk.VBox()
        vb.set_border_width(6)
        vb.set_spacing(6)
        self.append_page(vb, Gtk.Label(label))
        if widgets:
            for w in widgets:
                vb.pack_start(w,False, False, 2)
        return vb
        
    def apply_conf(self):
        self.load_conf()
        self.dst_b.set_current_folder(self.conf['dst_b'])
        self.dst_o1.set_active(self.conf['dst_o1'])
        self.dst_o2.set_active(self.conf['dst_o2'])
        self.x_o1.set_active(self.conf['x_o1'])
        self.x_o2.set_active(self.conf['x_o2'])
        self.x_o3.set_active(self.conf['x_o3'])
        
    def load_conf(self):
        s=''
        fn=os.path.expanduser('~/.ojuba-mimic.rc')
        if os.path.exists(fn):
            try: s=open(fn,'rt').read()
            except OSError: pass
        self.parse_conf(s)
        self.conf['dst_o1']=(self.conf['dst_o1']=='True')
        self.conf['dst_o2']=(self.conf['dst_o2']=='True')
        self.conf['x_o1']=(self.conf['x_o1']=='True')
        self.conf['x_o2']=(self.conf['x_o2']=='True')
        self.conf['x_o3']=(self.conf['x_o3']=='True')
        if os.path.ismount(self.conf['dst_b']) or os.path.isdir(self.conf['dst_b']): return
        self.conf['dst_b']=os.path.realpath(os.path.expanduser('~'))
        
    def parse_conf(self, s):
        self.default_conf()
        l1 = map(lambda k: k.split('=',1), filter(lambda j: j,map(lambda i: i.strip(),s.splitlines())) )
        l2 = map(lambda a: (a[0].strip(),a[1].strip()),filter(lambda j: len(j)==2,l1))
        r = dict(l2)
        self.conf.update(dict(l2))
        return len(l1)==len(l2)
        
    def default_conf(self):
        self.conf['dst_o1']=True #self.dst_o1.get_active()
        self.conf['dst_o2']=False #self.dst_o2.get_active()
        self.conf['dst_b']=os.path.realpath(os.path.expanduser('~'))
        self.conf['x_o1']=False #self.x_o1.get_active()
        self.conf['x_o2']=False #self.x_o2.get_active()
        self.conf['x_o3']=True #self.x_o3.get_active()
        
    def save_conf(self, *args):
        self.dst_b.set_sensitive(self.dst_o2.get_active())
        self.conf['dst_o1']=self.dst_o1.get_active()
        self.conf['dst_o2']=self.dst_o2.get_active()
        self.conf['dst_b']=self.dst_b.get_filename()
        self.conf['x_o1']=self.x_o1.get_active()
        self.conf['x_o2']=self.x_o2.get_active()
        self.conf['x_o3']=self.x_o3.get_active()
        print "** saving conf", args,self.conf
        fn=os.path.expanduser('~/.ojuba-mimic.rc')
        s='\n'.join(map(lambda k: "%s=%s" % (k,str(self.conf[k])), self.conf.keys()))
        try: open(fn,'wt').write(s)
        except OSError: pass
        
    def scale_cb(self, c, *args):
        s = self.scale_c.get_value()
        if s == _("custom"):
            return
        n,r = s.split(' ')
        W,H = r.split('x')
        self.cw_Stop = True
        self.scale_w.set_value(float(W))
        self.scale_h.set_value(float(H))
        self.cw_Stop = False
        
        
    def scale_wh_cb(self, m,w,h,l):
        if self.cw_Stop: return
        scale_dict = self.scale_dict
        W = w.get_value()
        H = h.get_value()
        S = '%dx%d' % (W,H)
        if S not in scale_dict: l.set_value(_("custom"))
        elif scale_dict[S] != l.get_value():
            l.set_value(scale_dict[S])

    def build_cmd(self, frm, win=None):
        ext = frm[0] #.split(' ')[0]
        
        opts={}
        # make things even:
        for i in (self.crp_dy1,self.crp_dy2,self.crp_dx1,
                  self.crp_dx2,self.scale_w,self.scale_h,
                  self.pad_dy1,self.pad_dy2,self.pad_dx1,self.pad_dx2):
            a=int(i.get_value())
            i.set_value(a-(a%2))
            #i.set_value(modNfix(int(i.get_value())))
        #
        if self.crp_c.get_active():
            opts['croptop']=('','-croptop %d' % self.crp_dy1.get_value())[bool(self.crp_dy1.get_value())]
            opts['cropbottom']=('','-cropbottom %d' % self.crp_dy2.get_value())[bool(self.crp_dy2.get_value())]
            opts['cropleft']=('','-cropright %d' % self.crp_dx1.get_value())[bool(self.crp_dx1.get_value())]
            opts['cropright']=('','-cropleft %d' % self.crp_dx2.get_value())[bool(self.crp_dx2.get_value())]
            opts['crop']=' '.join((opts['croptop'],opts['cropbottom'],opts['cropright'],opts['cropleft']))
        else:
            opts['crop']=''
            opts['croptop']=''
            opts['cropbottom']=''
            opts['cropleft']=''
            opts['cropright']=''
        if self.pad_c.get_active():
            opts['padtop']=('','-padtop %d' % self.pad_dy1.get_value())[bool(self.pad_dy1.get_value())]
            opts['padbottom']=('','-padbottom %d' % self.pad_dy2.get_value())[bool(self.pad_dy2.get_value())]
            opts['padleft']=('','-padright %d' % self.pad_dx1.get_value())[bool(self.pad_dx1.get_value())]
            opts['padright']=('','-padleft %d' % self.pad_dx2.get_value())[bool(self.pad_dx2.get_value())]
            opts['pad']=' '.join((opts['padtop'],opts['padbottom'],opts['padright'],opts['padleft']))
            #if opts['pad']: opts['pad']+' -padcolor 000000'
        else: opts['pad']=''; opts['padtop']=''; opts['padbottom']=''; opts['padleft']=''; opts['padright']=''

        if self.scale_c.get_active():
            opts['width']=self.scale_w.get_value()
            opts['height']=self.scale_h.get_value()
            opts['size']='-s %dx%d' % (self.scale_w.get_value(),self.scale_h.get_value())
        else:
            opts['width']=''
            opts['height']=''
            opts['size']=''
        if self.q_a_c.get_active():
            opts['audio_quality']=(('-aq %d','-aq %g')[frm[9]==float] ) % frm[9](self.q_a.get_value())
        else: opts['audio_quality']=''
        if self.q_v_c.get_active():
            opts['video_quality']=(('-qscale %d','-qscale %g')[frm[13]==float] ) % frm[13](self.q_v.get_value())
        else: opts['video_quality']=''
        if self.br_a_c.get_active():
            opts['audio_bitrate']=self.br_a_c.get_value()
            opts['br_a']='-ab %s' % self.br_a_c.get_value()
        else: opts['br_a']=opts['audio_bitrate']=''
        if self.br_v_c.get_active():
            opts['video_bitrate']=self.br_v_c.get_value()
            opts['br_v']='-b %dk' % int(self.br_v_c.get_value())
        else: opts['br_v']=opts['video_bitrate']=''
        if self.ar_r_c.get_active():
            opts['audio_samplerate']=int(self.ar_r_c.get_value())
            opts['ar']='-ar %s' % opts['audio_samplerate']
        else: opts['ar']=opts['audio_samplerate']=''
        if not frm[1]:
            opts['size']=''
            opts['br_v']=''
            opts['q_v']=''
        o = frm[24]
        try:
            if not eval(frm[24],opts):
                error(frm[25], win); return None
        except TypeError:
            error(_("Error: Validity python eval check faild") , win); return None
        cmd=' '.join((frm[2] % opts,opts['ar'],opts['br_a'],opts['br_v'],opts['crop'],opts['size'],opts['pad']))
        return cmd
    
    def modNfix(self, i,n=2): return i-(i%n)


class FileManager:
    def __init__(self):
        self._ps=[]
        self._opend={}
        
    def run_in_bg(self, cmd):
        setsid = getattr(os, 'setsid', None)
        if not setsid: setsid = getattr(os, 'setpgrp', None)
        self._ps=filter(lambda x: x.poll()!=None,self._ps) # remove terminated processes from _ps list
        #opend = dict(filter(lambda (k,v): k in self._ps,self._opend.items()))
        #print self._ps
        #print self._opend
        if cmd in self._opend.values(): return False
        cid=Popen(cmd,0,'/bin/sh',shell=True, preexec_fn=setsid)
        self._ps.append(cid)
        self._opend[cid]=cmd

    def get_pids(self, l):
        pids=[]
        for i in l:
            p=Popen(['/sbin/pidof',i], 0, stdout=PIPE)
            l=p.communicate()[0].strip().split()
            r=p.returncode
            if r==0: pids.extend(l)
        pids.sort()
        return pids

    def get_desktop(self):
        """return 1 for kde, 0 for gnome, -1 none of them"""
        l=self.get_pids(('kwin','ksmserver',))
        if l: kde=l[0]
        else: kde=None
        l=self.get_pids(('gnome-session',))
        if l: gnome=l[0]
        else: gnome=None
        if kde:
            if not gnome or kde<gnome: return 1
            else: return 0
        if gnome: return 0
        else: return -1

    def run_file_man(self,mp):
        if self.get_desktop()==0: self.run_in_bg("nautilus '%s'" % mp)
        elif self.get_desktop()==1: self.run_in_bg("konqueror '%s'" % mp)
        elif os.path.exists('/usr/bin/thunar'): self.run_in_bg("thunar '%s'" % mp)
        elif os.path.exists('/usr/bin/pcmanfm'): self.run_in_bg("pcmanfm '%s'" % mp)
        elif os.path.exists('/usr/bin/nautilus'): self.run_in_bg("nautilus --no-desktop '%s'" % mp)
        elif os.path.exists('/usr/bin/konqueror'): self.run_in_bg("konqueror '%s'" % mp)

def main():
    win=MainWindow()
    try: Gtk.main()
    except KeyboardInterrupt: win.stop_cb()
    
if __name__ == "__main__":
    main()
