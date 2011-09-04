#! /usr/bin/python
# -*- coding: UTF-8 -*-
"""
	Multi Media Converter that utilize gstreamer and/or ffmpeg
	Copyright © 2008-2011, Ojuba.org <core@ojuba.org>
	Released under terms of Waqf Public License
"""
import os, commands
import os.path
import random
import signal
import sys
import gobject
import gtk
import pango
import string
import re
import time
import gettext
from urllib import unquote
from os.path import dirname,basename
from subprocess import Popen, PIPE
import time
#".ext (human readable type)", is_video, cmd, q_a,q_v, br_a,br_v, allow_audio_resample, default_ar
# audio quality float/int, default, from , to, 
# video quality float/int, default, from , to,
# audio bitrate default , from, to,
# video bitrate default , from, to,
# [disabled flag that can be turned on],
# validity python eval check, fauler msg

exedir=os.path.dirname(sys.argv[0])
ld=os.path.join(exedir,'..','share','locale')
if not os.path.isdir(ld): ld=os.path.join(exedir, 'locale')
gettext.install('ojuba-mimic', ld, unicode=0)

formats=[
(".ogg _(Ogg/Theora video)", True, "-f ogg -acodec libvorbis -ac 2 %(audio_quality)s -vcodec libtheora %(video_quality)s", 1, 1, 0, 0, 1, 44100, 
 float, 3, 0, 10, float, 10, 1, 100, 
 0, 0, 0, 0, 0, 0, [], 'True',''),
(".3gp (3GP)", True, "-f 3gp -acodec libopencore_amrnb -ar 8000 -ac 1 -vcodec h263", 0, 0, 1, 1, 0, 8000, 
 float, 3, 0, 10, float, 10, 1, 100, 
 4750, 4750, 12200, 4750, 4750, 10000000, [], 'size in ("-s 128x96", "-s 176x144", "-s 352x288", "-s 704x576", "-s 1408x1152") and audio_bitrate in (4750, 5150, 5900, 6700, 7400, 7950, 10200, 12200)',_('choose a valid size and bitrate (try cif and 4750)')),
(".flv _(Flash Video)", True, '-acodec libmp3lame -r 25 -vcodec flv', 0, 1, 1, 0, 1, 22050, 
 float, 3, 0, 10, int, 10, 1, 100,
 32000, 8000, 1000000, 100000, 10000, 10000000, [], 'audio_samplerate in (44100, 22050, 11025)',_('audio samplerate should be 44100, 22050 or 11025')),
(".avi (msmpeg4)", True, "-f avi -acodec libmp3lame -vcodec msmpeg4v2", 0, 0, 1, 1, 1, 44100, 
 int, 0, 0, 0, int, 0, 0, 0, 
32000, 8000, 1000000, 100000, 10000, 10000000, [], 'True',''),
(".wmv (msmpeg4)", True, "-f asf -acodec libmp3lame -vcodec msmpeg4", 0, 0, 1, 1, 1, 44100, 
 int, 0, 0, 0, int, 0, 0, 0, 
32000, 8000, 1000000, 100000, 10000, 10000000, [], 'True',''),
(".wmv (wmv1)", True, "-f asf -acodec wmav1 -vcodec wmv1", 0, 0, 1, 1, 1, 44100, 
 int, 0, 0, 0, int, 0, 0, 0, 
32000, 8000, 1000000, 100000, 10000, 10000000, [], 'True',''),
(".wmv (wmv2)",True,"-f asf -acodec wmav2 -vcodec wmv2", 0, 0, 1, 1, 1, 44100, 
 int, 0, 0, 0, int, 0, 0, 0, 
32000, 8000, 1000000, 100000, 10000, 10000000, [], 'True',''),
(".mpg (VCD)",True, "-f mpeg -target ntsc-vcd", 0, 0, 0, 0, 0, 44100, 
 int, 0, 0, 0, int, 0, 0, 0, 
32000, 8000, 1000000, 100000, 10000, 10000000, ['-flags qprd','-flags mv0','-flags skiprd','-g 100'], 'True',''),
(".mpg (DVD)",True, "-f mpeg -target ntsc-dvd", 0, 0, 0, 0, 0, 44100, 
 int, 0, 0, 0, int, 0, 0, 0, 
32000, 8000, 1000000, 100000, 10000, 10000000, ['-flags qprd','-flags mv0','-flags skiprd','-g 100'], 'True',''),
(".mpg (film)",True, "-f mpeg -target ntsc-svcd", 0, 0, 0, 0, 0, 44100, 
 int, 0, 0, 0, int, 0, 0, 0, 
32000, 8000, 1000000, 100000, 10000, 10000000, ['-flags qprd','-flags mv0','-flags skiprd','-g 100'], 'True',''),
(".mpg (mpeg1)",True, "-f mpeg -acodec libmp3lame -vcodec mpeg1video -mbd rd +trell -cmp 2 -subcmp 2 -bf 2", 0, 0, 1, 1, 1, 44100, 
 int, 0, 0, 0, int, 0, 0, 0, 
32000, 8000, 1000000, 100000, 10000, 10000000, ['-flags qprd','-flags mv0','-flags skiprd','-g 100'], 'True',''),
(".mpg (mpeg2)",True, "-f mpeg -acodec libmp3lame -vcodec mpeg2video -mbd rd  +trell -cmp 2 -subcmp 2 -bf 2", 0, 0, 1, 1, 1, 44100, 
 int, 0, 0, 0, int, 0, 0, 0, 
32000, 8000, 1000000, 100000, 10000, 10000000, [], 'True',''),
(".mp4 (psp ~30fps)",True,"-f psp -acodec libfaac -vcodec mpeg4 -ar 24000 -r 30000/1001 -bf 2", 0, 0, 1, 1, 0, 24000, 
 int, 0, 0, 0, int, 0, 0, 0,  
32000, 8000, 1000000, 100000, 10000, 10000000, [],
 'not size and width*height<=76800 and width%16==0 and height%16==0',_('Width and Hight must be multibles of 16 or too big resolution')),
(".mp4 (psp ~15fps)",True,"-f psp -acodec libfaac -vcodec mpeg4 -ar 24000 -r 15000/1001 -bf 2", 0, 0, 1, 1, 0, 24000, 
 int, 0, 0, 0, int, 0, 0, 0, 
32000, 8000, 1000000, 100000, 10000, 10000000, [],
 'not size or width*height<=76800 and width%16==0 and height%16==0',_('Width and Hight must be multibles of 16 or too big resolution')),
('.mp4 (ipod)',True,'--enable-libfaac -acodec libfaac -vcodec mpeg4 -mbd 2 -flags +mv4 -ac 2 -cmp 2 -subcmp 2 -bf 2', 0, 0, 1, 1, 1, 22050, 
 int, 0, 0, 0, int, 0, 0, 0, 
32000, 8000, 1000000, 100000, 10000, 10000000, [],
 'not size or width<=320 and height<=240',_('too big resolution, resize it so that width<=320 and height<=240')),
('.avi (MPEG4 like DviX)',True,'-f avi -mbd rd -flags +mv4+aic +trell -cmp 2 -subcmp 2 -g 300 -acodec libfaac -vcodec mpeg4 -vtag DIV5 -bf 2', 0, 0, 1, 1, 1, 44100, 
 int, 0, 0, 0, int, 0, 0, 0, 
32000, 8000, 1000000, 100000, 10000, 10000000, [],'True',''),
('.avi (xvid)', True, '-f avi -mbd rd -flags +mv4+aic +trell -cmp 2 -subcmp 2 -g 300 -acodec libmp3lame -vcodec libxvid -vtag xvid -bf 2', 0, 0, 1, 1, 1, 44100, 
 int, 0, 0, 0, int, 0, 0, 0, 
32000, 8000, 1000000, 100000, 10000, 10000000, [],'True',''),
('.mpg (mpeg4)', True, '-f mpeg -mbd rd -flags +mv4+aic +trell -cmp 2 -subcmp 2 -g 300 -acodec libfaac -vcodec mpeg4 -vtag DIV5 -bf 2', 0, 0, 1, 1, 1, 44100, 
 int, 0, 0, 0, int, 0, 0, 0, 
32000, 8000, 1000000, 100000, 10000, 10000000, [],'True',''),
('.mpg (xvid mpeg4)',True,'-f mpeg -mbd rd -flags +mv4+aic +trell -cmp 2 -subcmp 2 -g 300 -acodec libfaac -vcodec libxvid -vtag xvid -bf 2', 0, 0, 1, 1, 1, 44100, 
 int, 0, 0, 0, int, 0, 0, 0, 
32000, 8000, 1000000, 100000, 10000, 10000000, [],'True',''),
('.wma (wma1)', False, '-f asf -vn -acodec wmav1', 0, 0, 1, 0, 1, 44100, 
 int, 0, 0, 0, int, 0, 0, 0, 
32000, 8000, 1000000, 100000, 10000, 10000000, [],'True',''),
('.wma (wma2)', False, '-f asf -vn -acodec wmav2', 0, 0, 1, 0, 1, 44100, 
 int, 0, 0, 0, int, 0, 0, 0, 
32000, 8000, 1000000, 100000, 10000, 10000000, [],'True',''),
('.mp3 (MP3)', False,'-vn -acodec libmp3lame', 0, 0, 1, 1, 1, 44100, 
 int, 0, 0, 0, int, 0, 0, 0, 
32000, 8000, 1000000, 100000, 10000, 10000000, [],'True',''),
('.wav (adpcm_ms)',False, '-vn -acodec adpcm_ms', 0, 0, 0, 0, 1, 11025, 
 int, 0, 0, 0, int, 0, 0, 0, 
32000, 8000, 1000000, 100000, 10000, 10000000, [],'True',''),
('.ogg (Ogg/Vorbis audio)',False,'-vn -f ogg -acodec libvorbis -ac 2 %(audio_quality)s', 1, 0, 0, 0, 1, 44100, 
 float, 3, 0, 10, int, 10, 0, 100, 
 0, 0, 0, 0, 0, 0, [], 'True','')
]

scale_ls=["sqcif 128x96", "qcif 176x144", "cif 352x288", "4cif 704x576",
"qqvga 160x120", "qvga 320x240", "vga 640x480", "svga 800x600",
"xga 1024x768", "uxga 1600x1200", "qxga 2048x1536", "sxga 1280x1024",
"qsxga 2560x2048", "hsxga 5120x4096", "wvga 852x480", "wxga 1366x768",
"wsxga 1600x1024", "wuxga 1920x1200", "woxga 2560x1600", "wqsxga 3200x2048",
"wquxga 3840x2400", "whsxga 6400x4096", "whuxga 7680x4800", "cga 320x200",
"ega 640x350", "hd480 852x480", "hd720 1280x720", "hd1080 1920x1080",_("custom")]

banner_list=[
'وَمِنَ النَّاسِ مَنْ يَشْتَرِي لَهْوَ الْحَدِيثِ لِيُضِلَّ عَنْ سَبِيلِ اللَّهِ\nبِغَيْرِ عِلْمٍ وَيَتَّخِذَهَا هُزُوًا أُولَئِكَ لَهُمْ عَذَابٌ مُهِينٌ'
,'إِنَّ الَّذِينَ يُحِبُّونَ أَنْ تَشِيعَ الْفَاحِشَةُ فِي الَّذِينَ آَمَنُوا لَهُمْ عَذَابٌ أَلِيمٌ\nفِي الدُّنْيَا وَالْآَخِرَةِ وَاللَّهُ يَعْلَمُ وَأَنْتُمْ لَا تَعْلَمُونَ',
'قُلْ لِلْمُؤْمِنِينَ يَغُضُّوا مِنْ أَبْصَارِهِمْ وَيَحْفَظُوا فُرُوجَهُمْ\nذَلِكَ أَزْكَى لَهُمْ إِنَّ اللَّهَ خَبِيرٌ بِمَا يَصْنَعُونَ',
'فَخَلَفَ مِنْ بَعْدِهِمْ خَلْفٌ أَضَاعُوا الصَّلَاةَ وَاتَّبَعُوا الشَّهَوَاتِ فَسَوْفَ يَلْقَوْنَ غَيّاً'
]
formats.sort()
def info(msg,w=None):
	if not w: w=win
	dlg = gtk.MessageDialog (w,
			gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
			gtk.MESSAGE_INFO, gtk.BUTTONS_CLOSE,
			msg)
	dlg.run()
	dlg.destroy()

def bad(msg,w=None):
	if not w: w=win
	dlg = gtk.MessageDialog (w,
			gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
			gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE,
			msg)
	dlg.run()
	dlg.destroy()

def sure(msg,win=None):
  dlg=gtk.MessageDialog(win,gtk.DIALOG_MODAL,gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, msg)
  dlg.connect("response", lambda *args: dlg.hide())
  r=dlg.run()
  dlg.destroy()
  return r==gtk.RESPONSE_YES
  
def update_combo(c,ls):
  c.get_model().clear()
  for i in ls: c.append_text(i)

def create_combo(c, ls, w=1):
  c.set_wrap_width(w)
  for i in ls: c.append_text(i)
  c.set_active(0)
  return c

class MainWindow(gtk.Window):
  def __init__(self):
    gtk.Window.__init__(self)
    gtk.window_set_default_icon_name('ojuba-mimic')
    self.cur_src_dir=None
    self.working_ls=[]
    self.done_ls=[]
    self.fileman=FileManager()
    self.set_title(_('MiMiC :: Multi Media Converter'))
    self.drag_dest_set(gtk.DEST_DEFAULT_ALL,gtk.target_list_add_uri_targets(),(1<<5)-1)
    self.set_size_request(-1, 550)
    self.connect('destroy', self.quit)
    self.connect('delete_event', self.quit)
    self.connect('drag-data-received',self.drop_data_cb)
    self.set_resizable(False)
    self.set_position(gtk.WIN_POS_CENTER_ALWAYS)
    vb=gtk.VBox(False,0) 
    self.add(vb)
    l_banner_box=gtk.EventBox()
    vb.pack_start(l_banner_box,False, False, 0)
    for i in (gtk.STATE_NORMAL,gtk.STATE_ACTIVE,gtk.STATE_PRELIGHT,gtk.STATE_SELECTED,gtk.STATE_INSENSITIVE):
      l_banner_box.modify_bg(i,gtk.gdk.color_parse("#fffff8"))
    l_banner=gtk.Label(); l_banner.set_justify(gtk.JUSTIFY_CENTER)
    l_banner.set_markup('''<span face="Simplified Naskh" color="#204000"  size="x-large">%(verse)s</span>''' % {'verse':random.choice(banner_list)})
    l_banner_box.add(l_banner)
    
    b_add=gtk.Button(stock=gtk.STOCK_ADD)
    b_rm=gtk.Button(stock=gtk.STOCK_REMOVE)
    b_clear=gtk.Button(stock=gtk.STOCK_CLEAR)
    e_to=gtk.Label(_('to: '))
    self.c_to=create_combo(gtk.combo_box_new_text(), map(lambda i:i[0],formats),2)

    self.b_convert=gtk.Button(stock=gtk.STOCK_CONVERT)
    self.b_stop=gtk.Button(stock=gtk.STOCK_STOP)
    b_about=gtk.Button(stock=gtk.STOCK_ABOUT)
    self.files = gtk.ListStore(str,str,float,int,str) # fn, basename, percent, pulse, label
    self.files_list=gtk.TreeView(self.files)
    self.files_list.get_selection().set_mode(gtk.SELECTION_MULTIPLE)

    self.tools_hb=d_hb=gtk.HBox(False,0)
    self.ctoools_hb=gtk.HBox(False,0)
    for i in (b_rm, b_clear, gtk.VSeparator(), e_to, self.c_to):
      self.ctoools_hb.pack_start(i,False, False, 2)
    for i in (b_add, gtk.VSeparator(),self.ctoools_hb):
      d_hb.pack_start(i,False, False, 2)
    hb=gtk.HBox(False,0); vb.pack_start(hb,False, False, 0)
    for i in (d_hb,self.b_convert,self.b_stop,b_about):
      hb.pack_start(i,False, False, 2)
    scroll=gtk.ScrolledWindow()
    scroll.set_policy(gtk.POLICY_NEVER,gtk.POLICY_AUTOMATIC)
    scroll.add(self.files_list)
    vb.pack_start(scroll,True, True, 0)
    self.options=options(self)
    if self.options.conf.has_key('src_dir'):
      self.cur_src_dir=self.options.conf['src_dir']
    vb.pack_start(self.options,False, False, 0)
    
    s_hb=gtk.HBox(False,0); vb.pack_start(s_hb,False, False, 0)
    self.b_options = b = gtk.ToggleButton(_('Options'))
    b.connect('toggled', lambda *a: self.options.set_visible(b.get_active()))
    self.status_bar = s = gtk.Statusbar()
    s_hb.pack_start(b, False,False,2)
    s_hb.pack_start(s, True,True,2)
    self.context_id = context_id = self.status_bar.get_context_id("STATUS_D")
    self.status_bar.push(context_id,_('Add files, Then click Convert!'))
    
    b_add.connect('clicked', self.add_files_cb)
    
    b_clear.connect('clicked', self.clear_cb)
    b_rm.connect('clicked', self.rm_cb)
    self.c_to.connect('changed', self.c_to_cb)
    self.b_convert.connect('clicked', self.convert_cb)
    self.b_stop.connect('clicked', self.stop_cb)
    about_d=about_dlg()
    b_about.connect("clicked", lambda *args: about_d.show())
    
    # setting the list
    cells=[]
    cols=[]
    cells.append(gtk.CellRendererText())
    cols.append(gtk.TreeViewColumn(_('Files'), cells[-1], text=1))
    cols[-1].set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
    cols[-1].set_resizable(True)
    cols[-1].set_expand(True)
    cells.append(gtk.CellRendererProgress());
    cols.append(gtk.TreeViewColumn(' \t\t%s\t\t '%_('Status'), cells[-1], value=2,pulse=3,text=4))
    cols[-1].set_expand(False)
    self.files_list.set_headers_visible(True)
    self.b_stop.set_sensitive(False)
    self.b_convert.set_sensitive(False)
    for i in cols: self.files_list.insert_column(i, -1)

    self.c_to.set_active(len(formats)-1)
    self.c_to.set_active(0)
    
    self.popupMenu = gtk.Menu()
    self.build_popup_Menu()
    self.files_list.connect("button-press-event", self.do_popup)
    
    # sample list for testing
    #ls=[("/usr/share/file1.avi",10.0),("file2",20)]
    #self.files.clear()
    #for j,k in ls: self.files.append([j,basename(j),k,-1,None])
    #self.files[(1,)] = (self.files[1][0], self.files[1][1], 90,-1,"Done %d %%" % 90)
    gobject.timeout_add(250, self.progress_cb)
    self.show_all()
    self.options.set_visible(False)

  def active_controlls(self, v=False):
    self.b_stop.set_sensitive(v)
    self.b_convert.set_sensitive(not v)
    self.tools_hb.set_sensitive(not v)
    self.ctoools_hb.set_sensitive(not v)
    self.b_options.set_sensitive(not v)
    self.popupMenu.get_children()[2].set_sensitive(not v)
    self.popupMenu.get_children()[3].set_sensitive(not v)
    
  def build_popup_Menu(self):
		i = gtk.MenuItem(_("Open output folder"))
		i.connect("activate", self.open_odir_cb)
		self.popupMenu.add(i)
		self.popupMenu.add(gtk.SeparatorMenuItem())
		i = gtk.ImageMenuItem(gtk.STOCK_REMOVE)
		i.connect("activate", self.rm_cb)
		self.popupMenu.add(i)
		i = gtk.ImageMenuItem(gtk.STOCK_CLEAR)
		i.connect("activate", self.clear_cb)
		self.popupMenu.add(i)
		
  def do_popup(self, widget, event):
    iters = self.get_Iters()
    if event.button == 3 and len(iters) > 0:
      self.popupMenu.show_all()
      self.popupMenu.popup(None, self, None, 3, gtk.get_current_event_time())
      return True
      
  def get_Iters(self):
    sel_model, sel_rows = self.files_list.get_selection().get_selected_rows()
    return map(lambda a: self.files.get_iter(a), sel_rows)
    
  def open_odir_cb(self, *args):
    self.fileman._opend={}
    odir=self.options.dst_b.get_filename()
    if self.options.dst_o2.get_active():
      self.fileman.run_file_man(odir)
    else:
      iters = self.get_Iters()
      for i in iters:
        odir = os.path.dirname(self.files[self.files.get_path(i)[0]][0])
        self.fileman.run_file_man(odir)
        
  def clear_cb(self, *args):
    ln=len(self.files)
    self.files.clear()
    self.done_ls=[]
    self.rmstatus(ln)
    
  def rm_cb(self, *args):
    iters = self.get_Iters()
    #print iters
    for i in iters:
      fn = self.files[self.files.get_path(i)[0]][0]
      self.done_ls=filter(lambda a: fn not in a,self.done_ls)
      if i: self.files.remove(i)
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
    if len(self.working_ls)<=0: return True
    self.progressstatus()
    if not self.working_ls[0][0]:
      self.start_subprocess()
      return True
    r=self.working_ls[0][0].poll()
    if r==None:
      self.progress()
      return True
    elif r==0:
      i=self.files[(self.working_ls[0][2],)]
      i[2]=100
      i[3]=-1
      i[4]=_('Done')
    else:
      i=self.files[(self.working_ls[0][2],)]
      i[2]=100
      i[3]=-1
      i[4]='%s %d' % (_('Error'), r)
    done_item = self.working_ls[0][-1]
    self.done_ls.append(done_item)
    self.working_ls.pop(0)
    if len(self.working_ls)>0: stat_str=''
    else: stat_str=_('Finished:')
    self.progressstatus(stat_str)
    return True
    
  def progressstatus(self, txt=''):
    if txt=='': txt=_('Converting:')
    cm=len(self.done_ls)
    tot=len(self.files)
    self.status_bar.push(self.context_id,'%s %i %s %i %s!' %(txt,cm,_('file/files of'),tot,_('Compleated')))
    
  def progress(self, *args):
    p,icmd,i,fn,ofn,sn=self.working_ls[0]
    working_size=0
    try: working_size=os.path.getsize(ofn)
    except OSError, e: self.pulse_cb(i); return True
    if working_size==0: self.pulse_cb(i); return True
    try: s=os.path.getsize(fn)
    except OSError: self.pulse_cb(i); return True
    if working_size==0 or s<working_size: self.pulse_cb(i); return True
    pct=(float(working_size)/s)*100.0
    self.files[(i,)][3]=-1
    self.files[(i,)][2]=pct
    i=self.files[(self.working_ls[0][2],)]; i[4]='%0.2f'%pct
    gtk.main_iteration()
    return True;

  def pulse_cb(self, i):
    self.files[(i,)][2]=0
    self.files[(i,)][3]=int(abs(self.files[(i,)][3])+1)
    gtk.main_iteration()

  def start_subprocess(self):
    if self.working_ls[0][3]==self.working_ls[0][4]:
      if self.options.x_o3.get_active():
        if not self.rename_cb(): return self.skiped()
      else: return self.skiped()
    if os.path.exists(self.working_ls[0][4]):
      if self.options.x_o3.get_active():
        if not self.rename_cb(): return self.skiped()
      elif self.options.x_o1.get_active():
        return self.skiped()
    self.working_ls[0][0]=Popen(self.working_ls[0][1],0,'/bin/sh',shell=True)
    i=self.files[(self.working_ls[0][2],)]; i[2]=0; i[3]=-1; i[4]=_('Converting ...')
    #self.working_ls.append()=[None,icmd,working_on,fn,ofn]

  def drop_data_cb(self, widget, dc, x, y, selection_data, info, t):
    if len(self.working_ls)>0: print 'Sorry, You can not add files while converting ...'; return 
    for i in selection_data.get_uris():
      if i.startswith('file://'):
        f=unquote(i[7:])
        if os.path.isfile(f):
          self.files.append([f,basename(f),0,-1,_('Not started')])
        else:
          print "Can not add folders [%s]" % f
      else:
        print "Protocol not supported in [%s]" % i
    dc.drop_finish (True, t);
    self.addstatus(len(self.files))
    self.options.conf['src_dir']=self.cur_src_dir
    self.options.save_conf()
  
  def add_files_cb(self, *args):
    dlg = add_dlg()
    if self.cur_src_dir:
      dlg.set_current_folder(self.cur_src_dir)
    if (dlg.run()==gtk.RESPONSE_ACCEPT):
      for i in dlg.get_filenames(): self.files.append([i,basename(i),0,-1,_('Not started')])
      self.addstatus(len(self.files))
      self.cur_src_dir=os.path.dirname(i)
    self.options.conf['src_dir']=self.cur_src_dir
    self.options.save_conf()
    dlg.unselect_all()

  def addstatus(self, fc):
    self.status_bar.push(self.context_id,'%s %i %s' %(_('Click Convert, to start converting'),fc,_('file/files')))
    
  def c_to_cb(self, c,*args):
    frm=formats[c.get_active()]
    for i,j,k in ((frm[3],self.options.q_a_c,self.options.q_a),(frm[4],self.options.q_v_c,self.options.q_v),(frm[5],self.options.br_a_c,self.options.br_a),(frm[6],self.options.br_v_c,self.options.br_v)):
      j.set_sensitive(i)
      if not i: k.set_sensitive(False); j.set_active(False)
    self.options.hb_ar.set_sensitive(frm[7]);
    if not frm[7]: self.options.ar_c.set_active(False)
    self.options.ar_r.set_active(map(lambda i: i[0],self.options.ar_r.get_model()).index(str(frm[8])))
    self.options.q_a.get_adjustment().set_all(frm[10], frm[11], frm[12], 10, 1, 0)
    self.options.q_v.get_adjustment().set_all(frm[14], frm[15], frm[16], 10, 1, 0)
    self.options.br_a.get_adjustment().set_all(frm[17],frm[18],frm[19],50, 100, 0)
    self.options.br_v.get_adjustment().set_all(frm[20],frm[21],frm[22],50, 100, 0)

  def convert_cb(self, *args):
    self.b_options.set_active(False)
    self.active_controlls(True)
    frm=formats[self.c_to.get_active()]
    cmd=self.options.build_cmd(formats[self.c_to.get_active()], self)
    if not cmd: return
    if self.options.dst_o2.get_active(): oodir=self.options.dst_b.get_filename();
    else: oodir=False
    self.working_ls=[]
    for working_on,i in enumerate(self.files):
      fn=i[0]
      bfn=basename(fn)
      if not oodir: odir=dirname(fn)
      else: odir=oodir
      ofn=os.path.join(odir, bfn.partition('.')[0]+frm[0][:frm[0].index(' ')])
      #if fn==ofn or os.path.exists(ofn): i[4]='Exists; Skiped'; continue
      #i[2]=0; i[3]=-1; i[4]='Converting ...'
      icmd="ffmpeg -y -i 'file://%s' %s 'file://%s'" % (fn,cmd,ofn)
      print "*** ", icmd
      #print icmd
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
    #  self.status_bar.push(self.context_id,_('Starting operations...'))

  def stop_cb(self, *args):
    self.progressstatus(_('Stoped:'))
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
    dn=dirname(f)
    fn=basename(f)
    b,d,e=fn.partition('.')
    for i in self.suffex_gen():
       f=os.path.join(dn,''.join((b,'_',i,d,e)))
       if not os.path.exists(f): return f
    return None

  def rename_cb(self):
    ofn=self.working_ls[0][4]=self.suggest_name(self.working_ls[0][4])
    if not ofn:
      i=self.files[(self.working_ls[0][2],)]; i[4]=_('Exists; Skiped');
      self.working_ls.pop(0); return False
    fn=self.working_ls[0][3]
    cmd=self.options.build_cmd(formats[self.c_to.get_active()], self)
    self.working_ls[0][1]="ffmpeg -y -i 'file://%s' %s 'file://%s'" % (fn,cmd,ofn)
    return True

  def skiped(self):
    i=self.files[(working_ls[0][2],)]
    i[4]=_('Exists; Skiped')
    self.working_ls.pop(0)
    return 0

  def quit(self, *w):
    if len(self.working_ls)>0:
      if not sure(_('There are corrently running oprations, Stop it?'), self):return True
    self.stop_cb()
    gtk.main_quit()
    
class options(gtk.Frame):
  def __init__(self, win):
    gtk.Frame.__init__(self,_('Options...'))
    self.win=win
    self.conf={}
    m_vb=gtk.VBox(False, 0)
    self.add(m_vb)
    save_fram=gtk.Frame(_('Save Options...'))
    save_fram.set_shadow_type(gtk.SHADOW_OUT)
    s_vb=gtk.VBox(False, 0)
    save_fram.add(s_vb)
    dst_l=gtk.Label(_('Save destination: '))
    self.dst_o1=gtk.RadioButton(None,_("same as source"))
    self.dst_o2=gtk.RadioButton(self.dst_o1,_("fixed"))
    self.dst_b=gtk.FileChooserButton(_("Select destination folder"))
    self.dst_b.set_action(gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER)

    x_l=gtk.Label(_("If exists: "))
    self.x_o1=gtk.RadioButton(None,_("Skip"))
    self.x_o2=gtk.RadioButton(self.x_o1,_("Overwrite"))
    self.x_o3=gtk.RadioButton(self.x_o1,_("Rename"))
    
    hb=gtk.HBox(False,0)
    s_vb.pack_start(hb,False, False, 2)
    for i in (gtk.Label(' '),dst_l,self.dst_o1,self.dst_o2,self.dst_b): hb.pack_start(i,False, False, 2)
    hb=gtk.HBox(False,0)
    s_vb.pack_start(hb,False, False, 2)
    for i in (gtk.Label(' '),x_l,self.x_o1,self.x_o2,self.x_o3): hb.pack_start(i,False, False, 2)
    m_vb.pack_start(save_fram,False, False, 2)
    # temporal
    #x_o2.set_sensitive(False)
    #x_o3.set_sensitive(False)
    
    self.crp_c=gtk.CheckButton(_("Crop"))
    crp_hb=gtk.HBox(False,0);
    
    crp_ly1=gtk.Label(_("Top")); self.crp_dy1=gtk.SpinButton(gtk.Adjustment(0, 0, 10000, 2, 10, 0))
    crp_ly2=gtk.Label(_("Bottom")); self.crp_dy2=gtk.SpinButton(gtk.Adjustment(0, 0, 10000, 2, 10, 0))
    crp_lx1=gtk.Label(_("Left")); self.crp_dx1=gtk.SpinButton(gtk.Adjustment(0, 0, 10000, 2, 10, 0))
    crp_lx2=gtk.Label(_("Right")); self.crp_dx2=gtk.SpinButton(gtk.Adjustment(0, 0, 10000, 2, 10, 0))

    self.pad_c=gtk.CheckButton(_("Pad"))
    pad_hb=gtk.HBox(False,0);
    pad_ly1=gtk.Label(_("Top")); self.pad_dy1=gtk.SpinButton(gtk.Adjustment(0, 0, 10000, 1, 10, 0))
    pad_ly2=gtk.Label(_("Bottom")); self.pad_dy2=gtk.SpinButton(gtk.Adjustment(0, 0, 10000, 1, 10, 0))
    pad_lx1=gtk.Label(_("Left")); self.pad_dx1=gtk.SpinButton(gtk.Adjustment(0, 0, 10000, 1, 10, 0))
    pad_lx2=gtk.Label(_("Right")); self.pad_dx2=gtk.SpinButton(gtk.Adjustment(0, 0, 10000, 1, 10, 0))

    self.br_a_c=gtk.CheckButton(_("Audio Bitrates"))
    self.br_a=gtk.SpinButton(gtk.Adjustment(320000, 8000, 10000000, 50, 100, 0))
    br_a_l=gtk.Label(_("bit/s"));
    self.br_v_c=gtk.CheckButton(_("Video Bitrates"))
    self.br_v=gtk.SpinButton(gtk.Adjustment(100000, 8000, 10000000, 50, 100, 0))
    br_v_l=gtk.Label(_("bit/s"));

    self.q_a_c=gtk.CheckButton(_("Audio Quality"))
    self.q_a=gtk.HScale(gtk.Adjustment(3, 0, 10,0))
    self.q_a.set_property("value-pos",gtk.POS_LEFT)
    self.q_v_c=gtk.CheckButton(_("Video Quality"))
    self.q_v=gtk.HScale(gtk.Adjustment(10, 0, 100,0))
    self.q_v.set_property("value-pos",gtk.POS_LEFT)

    self.ar_c=gtk.CheckButton(_("Audio Samplerate"))
    self.ar_r=create_combo(gtk.combo_box_new_text(), map(lambda i: str(i),list(range(11025,48101,11025)+list(range(8000,48001,8000))) ),2)
    
    self.scale_dict={}
    for i in filter(lambda a: a!=_("custom"),scale_ls): a=i.split(' '); self.scale_dict[a[1]]=i
    self.scale_c=gtk.CheckButton(_("Resize"))
    scale_hb=gtk.HBox(False,0);
    self.scale_l=create_combo(gtk.combo_box_new_text(), scale_ls,2)
    self.scale_w=gtk.SpinButton(gtk.Adjustment(0, 0, 10000, 1, 10, 0))
    self.scale_x=gtk.Label("x");
    self.scale_h=gtk.SpinButton(gtk.Adjustment(0, 0, 10000, 1, 10, 0))

    conv_fram=gtk.Frame(_('Convert Options...'))
    conv_fram.set_shadow_type(gtk.SHADOW_OUT)
    c_vb=gtk.VBox(False, 0)
    c_hb=gtk.HBox(False, 0)
    conv_fram.add(c_vb)
    c_hb.pack_start(conv_fram,False, False, 2)
    m_vb.pack_start(c_hb,False, False, 2)

    #LOGO=gtk.Image()
    #LOGO.set_from_file('./ojuba-mimic.svg')
    #c_hb.pack_start(LOGO,True, False, 2)
    
    hb=gtk.HBox(False,0)
    c_vb.pack_start(hb,False, False, 2)
    hb.pack_start(self.crp_c,False, False, 2)
    hb.pack_start(crp_hb,True, True, 2)
    for i in (crp_ly1,self.crp_dy1,crp_ly2,self.crp_dy2,crp_lx1,self.crp_dx1,crp_lx2,self.crp_dx2): crp_hb.pack_start(i,False, False, 2)

    hb=gtk.HBox(False,0)
    c_vb.pack_start(hb,False, False, 2)
    hb.pack_start(self.scale_c,False, False, 2)
    hb.pack_start(scale_hb,True, True, 2)
    for i in (self.scale_l,self.scale_w,self.scale_x,self.scale_h): scale_hb.pack_start(i,False, False, 2)

    hb=gtk.HBox(False,0)
    c_vb.pack_start(hb,False, False, 2)
    hb.pack_start(self.pad_c,False, False, 2)
    hb.pack_start(pad_hb,True, True, 2)
    for i in (pad_ly1,self.pad_dy1,pad_ly2,self.pad_dy2,pad_lx1,self.pad_dx1,pad_lx2,self.pad_dx2): pad_hb.pack_start(i,False, False, 2)

    hb_br=gtk.HBox(False,0)
    c_vb.pack_start(hb_br,False, False, 2)
    for i in (self.br_a_c,self.br_a,br_a_l, gtk.VSeparator(),self.br_v_c,self.br_v,br_v_l): hb_br.pack_start(i,False, False, 2)

    hb_q=gtk.HBox(False,0)
    c_vb.pack_start(hb_q,False, False, 2)
    for i in (self.q_a_c,self.q_a, gtk.VSeparator(),self.q_v_c,self.q_v): hb_q.pack_start(i,type(i)==gtk.HScale, type(i)==gtk.HScale, 2)


    self.hb_ar=gtk.HBox(False,0)
    c_vb.pack_start(self.hb_ar,False, False, 2)
    for i in (self.ar_c,self.ar_r): self.hb_ar.pack_start(i,False, False, 2)
    
    self.x_o3.set_active(True)
    self.apply_conf()
    
    self.dst_o2.connect('toggled', self.save_conf)
    self.x_o1.connect('toggled', self.save_conf)
    self.x_o2.connect('toggled', self.save_conf)
    self.dst_b.connect('file-set', self.save_conf)
    #self.dst_b.connect('current-folder-changed', self.save_conf)
    for i,j in ((self.crp_c,crp_hb),(self.pad_c,pad_hb),(self.scale_c,scale_hb),(self.br_a_c,self.br_a),(self.br_v_c,self.br_v),(self.q_a_c,self.q_a),(self.q_v_c,self.q_v),(self.ar_c,self.ar_r)):
      i.connect('toggled', lambda i,j: j.set_sensitive(i.get_active()),j)
      i.set_active(False); j.set_sensitive(False)
    self.scale_l.connect('changed', self.scale_cb,self.scale_w,self.scale_h)
    self.scale_w.connect('changed', self.scale_wh_cb,self.scale_w,self.scale_h,self.scale_l)
    self.scale_h.connect('changed', self.scale_wh_cb,self.scale_w,self.scale_h,self.scale_l)
    self.scale_w.connect('activate', self.scale_wh_cb,self.scale_w,self.scale_h,self.scale_l)
    self.scale_h.connect('activate', self.scale_wh_cb,self.scale_w,self.scale_h,self.scale_l)  
    self.scale_w.connect_after('focus-out-event', lambda a,*args: a.activate() and False)
    self.scale_h.connect_after('focus-out-event', lambda a,*args: a.activate() and False)
    self.dst_b.set_sensitive(self.dst_o2.get_active())
    self.scale_l.set_active(scale_ls.index("qvga 320x240"))
    
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
    l1=map(lambda k: k.split('=',1), filter(lambda j: j,map(lambda i: i.strip(),s.splitlines())) )
    l2=map(lambda a: (a[0].strip(),a[1].strip()),filter(lambda j: len(j)==2,l1))
    r=dict(l2)
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
    
  def scale_cb(self, c,w,h):
    s=c.get_model()[c.get_active()][0]
    if s==_("custom"): return
    n,r=s.split(' '); W,H=r.split('x')
    w.set_value(float(W)); h.set_value(float(H));

  def scale_wh_cb(self, m,w,h,l):
    scale_dict=self.scale_dict
    W=w.get_value()
    H=h.get_value()
    S='%dx%d' % (W,H)
    if S not in scale_dict: l.set_active(scale_ls.index(_("custom")))
    elif scale_dict[S]!=l.get_model()[l.get_active()][0]:
      l.set_active(scale_ls.index(scale_dict[S]))

  def build_cmd(self, frm, win=None):
    ext=frm[0].split(' ')[0]
    
    opts={}
    # make things even:
    for i in (self.crp_dy1,self.crp_dy2,self.crp_dx1,self.crp_dx2,self.scale_w,self.scale_h,self.pad_dy1,self.pad_dy2,self.pad_dx1,self.pad_dx2):
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
      opts['audio_bitrate']=self.br_a.get_value()
      opts['br_a']='-ab %d' % self.br_a.get_value()
    else: opts['br_a']=opts['audio_bitrate']=''
    if self.br_v_c.get_active():
      opts['video_bitrate']=self.br_v.get_value()
      opts['br_v']='-b %d' % self.br_v.get_value()
    else: opts['br_v']=opts['video_bitrate']=''
    if self.ar_c.get_active():
      opts['audio_samplerate']=int(self.ar_r.get_model()[self.ar_r.get_active()][0])
      opts['ar']='-ar %d' % opts['audio_samplerate']
    else: opts['ar']=opts['audio_samplerate']=''
    if not frm[1]:
      opts['size']=''
      opts['br_v']=''
      opts['q_v']=''

    if not eval(frm[24],opts): bad(frm[25], win); return None
    cmd=' '.join((frm[2] % opts,opts['ar'],opts['br_a'],opts['br_v'],opts['crop'],opts['size'],opts['pad']))
    return cmd
  
  def modNfix(self, i,n=2): return i-(i%n)
   
class add_dlg(gtk.FileChooserDialog):
  def __init__(self):
    gtk.FileChooserDialog.__init__(self,_("Select files to convert"),buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
    ff=gtk.FileFilter()
    ff.set_name(_('All media files'))
    ff.add_mime_type('video/*')
    ff.add_mime_type('audio/*')
    ff.add_pattern('*.[Rr][AaMm]*')
    self.add_filter(ff)
    ff=gtk.FileFilter()
    ff.set_name(_('All video files'))
    ff.add_mime_type('video/*')
    ff.add_pattern('*.[Rr][AaMm]*')
    self.add_filter(ff)
    ff=gtk.FileFilter()
    ff.set_name(_('All audio files'))
    ff.add_mime_type('audio/*')
    ff.add_pattern('*.[Rr][AaMm]*')
    self.add_filter(ff)  
    ff=gtk.FileFilter()
    ff.set_name(_('All files'))
    ff.add_pattern('*')
    self.add_filter(ff)
    self.set_select_multiple(True)
    self.connect('delete-event', lambda *w: self.hide())
    self.connect('response', lambda *w: self.hide())

class about_dlg(gtk.AboutDialog):
	def __init__(self):
	  gtk.AboutDialog.__init__(self)
	  self.set_default_response(gtk.RESPONSE_CLOSE)
	  self.connect('delete-event', lambda *w: self.hide())
	  self.connect('response', lambda *w: self.hide())
	  try: self.set_program_name(_("MiMiC"))
	  except AttributeError: pass
	  self.set_logo_icon_name('ojuba-mimic')
	  self.set_name(_("MiMiC"))
	  #about_dlg.set_version(version)
	  self.set_copyright(_("Copyright © 2008-2011 Ojuba.org <core@ojuba.org>"))
	  self.set_comments(_("Multi Media Converter"))
	  self.set_license(_("""
      Released under terms of Waqf Public License.
      This program is free software; you can redistribute it and/or modify
      it under the terms of the latest version Waqf Public License as
      published by Ojuba.org.

      This program is distributed in the hope that it will be useful,
      but WITHOUT ANY WARRANTY; without even the implied warranty of
      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

      The Latest version of the license can be found on
      "http://waqf.ojuba.org/license"

  """))
	  self.set_website("http://www.ojuba.org/")
	  self.set_website_label("http://www.ojuba.org")
	  self.set_authors(["Muayyad Saleh Alsadi <alsadi@ojuba.org>", "Ehab El-Gedawy <ehabsas@gmail.com>"])

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
  #win.show_all()
  #gobject.timeout_add(250, progress_cb)
  try: gtk.main()
  except KeyboardInterrupt: win.stop_cb()
  
if __name__ == "__main__":
  main()

