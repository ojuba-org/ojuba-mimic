#! /usr/bin/python
# -*- coding: UTF-8 -*-
"""
	Multi Media Converter that utilize gstreamer and/or ffmpeg
	Copyright © 2008-2012, Ojuba.org <core@ojuba.org>
	Released under terms of Waqf Public License
"""
from gi.repository import Gtk, Gdk, GObject
import os
import random
import signal
import sys
#import gobject
#import Gtk
import re
import gettext
from urllib import unquote
from subprocess import Popen, PIPE
from datetime import timedelta
#import time

#".ext (human readable type)", is_video, cmd, q_a,q_v, br_a,br_v, allow_audio_resample, default_ar
# audio quality float/int, default, from , to, 
# video quality float/int, default, from , to,
# audio bitrate default , from, to,
# video bitrate default , from, to,
# [disabled flag that can be turned on],
# validity python eval check, fauler msg

exedir = os.path.dirname(sys.argv[0])
ld = os.path.join(exedir,'..','share','locale')
if not os.path.isdir(ld): 
	ld = os.path.join(exedir, 'locale')
gettext.install('ojuba-mimic', ld, unicode=0)

# NOTE: type 'ffmpeg -formats' and 'ffmpeg -codecs' to get more info
formats = {
"OGG (Ogg/Theora video)":
	('.ogv', True, "-f ogg -acodec libvorbis -ac 2 %(audio_quality)s -vcodec libtheora %(video_quality)s", 1, 1, 0, 0, 1, 44100, 
	float, 3, 0, 10, float, 10, 1, 100, 
	0, 0, 0, 0, 0, 0, [], 'True',''),
"3GP (3GP)":
	('.3gp', True, "-f 3gp -acodec aac -strict experimental -ar 8000 -ac 1 -vcodec h263", 0, 0, 1, 1, 0, 8000, 
	float, 3, 0, 10, float, 10, 1, 100, 
	4750, 4750, 12200, 4750, 4750, 10000000, [], 'size in ("-s 128x96", "-s 176x144", "-s 352x288", "-s 704x576", "-s	 1408x1152") and audio_bitrate in (4750, 5150, 5900, 6700, 7400, 7950, 10200, 12200)',_('choose a valid size and	 bitrate (try cif and 4750)')),
"FLV (Flash Video)":
 ('.flv', True, '-f flv -acodec libmp3lame -r 25 -vcodec flv', 0, 1, 1, 0, 1, 22050, 
 float, 3, 0, 10, int, 10, 1, 100,
 32000, 8000, 1000000, 100000, 10000, 10000000, [], 'audio_samplerate in (44100, 22050, 11025)',_('audio samplerate should be 44100, 22050 or 11025')),
"AVI (msmpeg4)":
 ('.avi', True, "-f avi -acodec libmp3lame -vcodec msmpeg4v2", 0, 0, 1, 1, 1, 44100, 
 int, 0, 0, 0, int, 0, 0, 0, 
32000, 8000, 1000000, 100000, 10000, 10000000, [], 'True',''),
"WMV (msmpeg4)": 
('.wmv', True, "-f asf -acodec libmp3lame -vcodec msmpeg4", 0, 0, 1, 1, 1, 44100, 
 int, 0, 0, 0, int, 0, 0, 0, 
32000, 8000, 1000000, 100000, 10000, 10000000, [], 'True',''),
"WMV (wmv1)": 
('.wmv', True, "-f asf -acodec wmav1 -vcodec wmv1", 0, 0, 1, 1, 1, 44100, 
 int, 0, 0, 0, int, 0, 0, 0, 
32000, 8000, 1000000, 100000, 10000, 10000000, [], 'True',''),
"WMV (wmv2)": 
('.wmv', True,"-f asf -acodec wmav2 -vcodec wmv2", 0, 0, 1, 1, 1, 44100, 
 int, 0, 0, 0, int, 0, 0, 0, 
32000, 8000, 1000000, 100000, 10000, 10000000, [], 'True',''),
"MPG (VCD)": 
('.mpg', True, "-f mpeg -target ntsc-vcd", 0, 0, 0, 0, 0, 44100, 
 int, 0, 0, 0, int, 0, 0, 0, 
32000, 8000, 1000000, 100000, 10000, 10000000, ['-flags qprd','-flags mv0','-flags skiprd','-g 100'], 'True',''),
"MPG (DVD)": 
('.mpg', True, "-f mpeg -target ntsc-dvd", 0, 0, 0, 0, 0, 44100, 
 int, 0, 0, 0, int, 0, 0, 0, 
32000, 8000, 1000000, 100000, 10000, 10000000, ['-flags qprd','-flags mv0','-flags skiprd','-g 100'], 'True',''),
"MPG (film)": 
('.mpg', True, "-f mpeg -target ntsc-svcd", 0, 0, 0, 0, 0, 44100, 
 int, 0, 0, 0, int, 0, 0, 0, 
32000, 8000, 1000000, 100000, 10000, 10000000, ['-flags qprd','-flags mv0','-flags skiprd','-g 100'], 'True',''),
"MPG (mpeg1)": 
('.mpg', True, "-f mpeg -acodec libmp3lame -vcodec mpeg1video -mbd rd -cmp 2 -subcmp 2 -bf 2", 0, 0, 1, 1, 1, 44100, 
 int, 0, 0, 0, int, 0, 0, 0, 
32000, 8000, 1000000, 100000, 10000, 10000000, ['-flags qprd','-flags mv0','-flags skiprd','-g 100'], 'True',''),
"MPG (mpeg2)": 
('.mpg', True, "-f mpeg -acodec libmp3lame -vcodec mpeg2video -mbd rd -cmp 2 -subcmp 2 -bf 2", 0, 0, 1, 1, 1, 44100, 
 int, 0, 0, 0, int, 0, 0, 0, 
32000, 8000, 1000000, 100000, 10000, 10000000, [], 'True',''),
"MP4 (psp ~30fps)": 
('.mp4', True,"-f psp -acodec aac -strict experimental -vcodec mpeg4 -ar 24000 -r 30000/1001 -bf 2", 0, 0, 1, 1, 0, 24000, 
 int, 0, 0, 0, int, 0, 0, 0,	
32000, 8000, 1000000, 100000, 10000, 10000000, [],
 'not size and width*height<=76800 and width%16==0 and height%16==0',_('Width and Hight must be multibles of 16 or too big resolution')),
"MP4 (psp ~15fps)": 
('.mp4', True,"-f psp -acodec aac -strict experimental -vcodec mpeg4 -ar 24000 -r 15000/1001 -bf 2", 0, 0, 1, 1, 0, 24000, 
 int, 0, 0, 0, int, 0, 0, 0, 
32000, 8000, 1000000, 100000, 10000, 10000000, [],
 'not size or width*height<=76800 and width%16==0 and height%16==0',_('Width and Hight must be multibles of 16 or too big resolution')),
'MP4 (ipod)': 
('.mp4', True,'-f mp4 -acodec aac -strict experimental -vcodec mpeg4 -mbd 2 -flags +mv4 -ac 2 -cmp 2 -subcmp 2 -bf 2', 0, 0, 1, 1, 1, 22050, 
 int, 0, 0, 0, int, 0, 0, 0, 
32000, 8000, 1000000, 100000, 10000, 10000000, [],
 'not size or width<=320 and height<=240',_('too big resolution, resize it so that width<=320 and height<=240')),
'AVI (MPEG4 like DviX)': 
('.avi', True,'-f avi -mbd rd -flags +mv4+aic -cmp 2 -subcmp 2 -g 300 -acodec aac -strict experimental -vcodec mpeg4 -vtag DIV5 -bf 2', 0, 0, 1, 1, 1, 44100, 
 int, 0, 0, 0, int, 0, 0, 0, 
32000, 8000, 1000000, 100000, 10000, 10000000, [],'True',''),
'AVI (xvid)': 
('.avi', True, '-f avi -mbd rd -flags +mv4+aic -cmp 2 -subcmp 2 -g 300 -acodec libmp3lame -vcodec libxvid -vtag xvid -bf 2', 0, 0, 1, 1, 1, 44100, 
 int, 0, 0, 0, int, 0, 0, 0, 
32000, 8000, 1000000, 100000, 10000, 10000000, [],'True',''),
'MPG (mpeg4)': 
('.mpg', True, '-f mpeg -mbd rd -flags +mv4+aic	-cmp 2 -subcmp 2 -g 300 -acodec aac -strict experimental -vcodec mpeg4 -vtag DIV5 -bf 2', 0, 0, 1, 1, 1, 44100, 
 int, 0, 0, 0, int, 0, 0, 0, 
32000, 8000, 1000000, 100000, 10000, 10000000, [],'True',''),
'MPG (xvid mpeg4)': 
('.mpg', True,'-f mpeg -mbd rd -flags +mv4+aic -cmp 2 -subcmp 2 -g 300 -acodec aac -strict experimental -vcodec libxvid -vtag xvid -bf 2', 0, 0, 1, 1, 1, 44100, 
 int, 0, 0, 0, int, 0, 0, 0, 
32000, 8000, 1000000, 100000, 10000, 10000000, [],'True',''),
'WMA (wma1)': 
('.wma', False, '-f asf -vn -acodec wmav1', 0, 0, 1, 0, 1, 44100, 
 int, 0, 0, 0, int, 0, 0, 0, 
32000, 8000, 1000000, 100000, 10000, 10000000, [],'True',''),
'WMA (wma2)': 
('.wma', False, '-f asf -vn -acodec wmav2', 0, 0, 1, 0, 1, 44100, 
 int, 0, 0, 0, int, 0, 0, 0, 
32000, 8000, 1000000, 100000, 10000, 10000000, [],'True',''),
'MP3 (MP3)': 
('.mp3', False,'-f mp3 -vn -acodec libmp3lame', 0, 0, 1, 1, 1, 44100, 
 int, 0, 0, 0, int, 0, 0, 0, 
32000, 8000, 1000000, 100000, 10000, 10000000, [],'True',''),
'WAV (adpcm_ms)': 
('.wav', False, '-f wav -vn -acodec adpcm_ms', 0, 0, 0, 0, 1, 11025, 
 int, 0, 0, 0, int, 0, 0, 0, 
32000, 8000, 1000000, 100000, 10000, 10000000, [],'True',''),
'OGG (Ogg/Vorbis audio)': 
('.oga', False,'-vn -f ogg -acodec libvorbis -ac 2 %(audio_quality)s', 1, 0, 0, 0, 1, 44100, 
 float, 3, 0, 10, int, 10, 0, 100, 
 0, 0, 0, 0, 0, 0, [], 'True','')
}

scale_ls = ["sqcif 128x96", "qcif 176x144", "cif 352x288", "4cif 704x576",
"qqvga 160x120", "qvga 320x240", "vga 640x480", "svga 800x600",
"xga 1024x768", "uxga 1600x1200", "qxga 2048x1536", "sxga 1280x1024",
"qsxga 2560x2048", "hsxga 5120x4096", "wvga 852x480", "wxga 1366x768",
"wsxga 1600x1024", "wuxga 1920x1200", "woxga 2560x1600", "wqsxga 3200x2048",
"wquxga 3840x2400", "whsxga 6400x4096", "whuxga 7680x4800", "cga 320x200",
"ega 640x350", "hd480 852x480", "hd720 1280x720", "hd1080 1920x1080",_("custom")]

banner_list = [
'وَمِنَ النَّاسِ مَنْ يَشْتَرِي لَهْوَ الْحَدِيثِ لِيُضِلَّ عَنْ سَبِيلِ اللَّهِ\nبِغَيْرِ عِلْمٍ وَيَتَّخِذَهَا هُزُوًا أُولَئِكَ لَهُمْ عَذَابٌ مُهِينٌ'
,'إِنَّ الَّذِينَ يُحِبُّونَ أَنْ تَشِيعَ الْفَاحِشَةُ فِي الَّذِينَ آَمَنُوا لَهُمْ عَذَابٌ أَلِيمٌ\nفِي الدُّنْيَا وَالْآَخِرَةِ وَاللَّهُ يَعْلَمُ وَأَنْتُمْ لَا تَعْلَمُونَ',
'قُلْ لِلْمُؤْمِنِينَ يَغُضُّوا مِنْ أَبْصَارِهِمْ وَيَحْفَظُوا فُرُوجَهُمْ\nذَلِكَ أَزْكَى لَهُمْ إِنَّ اللَّهَ خَبِيرٌ بِمَا يَصْنَعُونَ',
'فَخَلَفَ مِنْ بَعْدِهِمْ خَلْفٌ أَضَاعُوا الصَّلَاةَ وَاتَّبَعُوا الشَّهَوَاتِ فَسَوْفَ يَلْقَوْنَ غَيّاً'
]

def info(msg, w = None):
	if not w: 
		w = win
	dlg = Gtk.MessageDialog (w,
			Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
			Gtk.MessageType.INFO, Gtk.ButtonsType.CLOSE,
			msg)
	dlg.run()
	dlg.destroy()

def bad(msg,w = None):
	if not w: 
		w = win
	dlg = Gtk.MessageDialog (w,
			Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
			Gtk.MessageType.ERROR, Gtk.ButtonsType.CLOSE,
			msg)
	dlg.run()
	dlg.destroy()

def sure(msg, win = None):
	dlg=Gtk.MessageDialog(win, Gtk.DialogFlags.MODAL, Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO, msg)
	dlg.connect("response", lambda *args: dlg.hide())
	r=dlg.run()
	dlg.destroy()
	return r == Gtk.ResponseType.YES
	
def update_combo(c, ls):
	c.get_model().clear()
	for i in ls: c.append_text(i)

def create_combo(c, ls, w=1):
	c.set_entry_text_column(0) #
	c.set_wrap_width(w)
	for i in ls: c.append_text(i)
	c.set_active(0)
	return c

class MainWindow(Gtk.Window):
	if_dura_re=re.compile(r'''Duration:\s*(\d+):(\d+):(\d+.?\d*)''')
	of_dura_re=re.compile(r'''time=\s*(\d+):(\d+):(\d+.?\d*)''')
	def __init__(self):
		Gtk.Window.__init__(self)
		self.set_default_icon_name('ojuba-mimic')
		self.set_border_width(4)
		self.set_position(Gtk.WindowPosition.CENTER)
		self.cur_src_dir= None
		self.working_ls = []
		self.ouput_fn = '/tmp/mimic.tmp'
		self.if_dura = 0
		self.done_ls=[]
		self.fileman=FileManager()
		self.set_title(_('MiMiC :: Multi Media Converter'))
		#self.drag_dest_set(Gtk.DestDefaults.ALL, Gtk.TargetList.add_uri_targets(),(1<<5)-1)
		
		self.connect('destroy', self.quit_cb)
		self.connect('delete_event', self.quit_cb)
		self.connect('drag-data-received',self.drop_data_cb)
		
		vb = Gtk.VBox(False, 0) 
		self.add(vb)
		l_banner_box=Gtk.EventBox()
		vb.pack_start(l_banner_box,False, False, 0)
		for i in (Gtk.StateType.NORMAL, Gtk.StateType.ACTIVE, Gtk.StateType.PRELIGHT, Gtk.StateType.SELECTED, Gtk.StateType.INSENSITIVE):
				l_banner_box.modify_bg(i, Gdk.color_parse("#fffff8"))
		l_banner=Gtk.Label(); l_banner.set_justify(Gtk.Justification.CENTER)
		l_banner.set_markup('''<span face="Simplified Naskh" color="#2040FF"	size="x-large">%(verse)s</span>''' % {'verse':random.choice(banner_list)})
		l_banner_box.add(l_banner)
		
		b_add=Gtk.Button(stock=Gtk.STOCK_ADD)
		b_rm=Gtk.Button(stock=Gtk.STOCK_REMOVE)
		b_clear=Gtk.Button(stock=Gtk.STOCK_CLEAR)
		e_to=Gtk.Label(_('to: '))
		self.c_to = create_combo(Gtk.ComboBoxText(has_entry = True), sorted(formats),2)

		self.b_convert=Gtk.Button(stock=Gtk.STOCK_CONVERT)
		self.b_stop = Gtk.Button(stock=Gtk.STOCK_STOP)
		b_about=Gtk.Button(stock=Gtk.STOCK_ABOUT)
		self.files = Gtk.ListStore(str, str, float, int, str) # fn, os.path.basename, percent, pulse, label
		self.files_list = Gtk.TreeView(self.files)
		self.files_list.set_size_request(-1, 350)
		self.files_list.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)

		self.tools_hb = d_hb = Gtk.HBox(False,0)
		self.ctoools_hb=Gtk.HBox(False,0)
		for i in (b_rm, b_clear, Gtk.VSeparator(), e_to, self.c_to):
			self.ctoools_hb.pack_start(i,False, False, 2)
		for i in (b_add, Gtk.VSeparator(),self.ctoools_hb):
			d_hb.pack_start(i,False, False, 2)
			d_hb.set_spacing(4)
		hb = Gtk.HBox(False,0); vb.pack_start(hb,False, False, 0)
		for i in (d_hb,self.b_convert,self.b_stop,b_about):
			hb.pack_start(i,False, False, 2)
			hb.set_spacing(4)
		scroll = Gtk.ScrolledWindow()
		self.set_size_request(-1, 350)
		scroll.set_shadow_type(Gtk.ShadowType.IN)
		scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
		scroll.add(self.files_list)
		vb.pack_start(scroll,True, True, 0)
		vb.set_spacing(8)
		self.options = options(self)
		if self.options.conf.has_key('src_dir'):
			self.cur_src_dir=self.options.conf['src_dir']
		expander = Gtk.Expander(label = _('Options'))
		expander.add(self.options)
		expander.set_resize_toplevel(True)
		vb.pack_start(expander, False, False,0)
		
		s_hb=Gtk.HBox(False,0); vb.pack_start(s_hb,False, False, 0)
		self.status_bar = s = Gtk.Statusbar()

		s_hb.pack_start(s, True,True,2)
		self.context_id = context_id = self.status_bar.get_context_id("STATUS_D")
		self.status_bar.push(context_id,_('Add files, Then click Convert!'))
		
		b_add.connect('clicked', self.add_files_cb)
		
		b_clear.connect('clicked', self.clear_cb)
		b_rm.connect('clicked', self.rm_cb)
		self.c_to.connect('changed', self.c_to_cb)
		self.b_convert.connect('clicked', self.convert_cb)
		self.b_stop.connect('clicked', self.stop_cb)
		about_d = about_dlg()
		b_about.connect("clicked", lambda *args: about_d.show())
		
		# setting the list
		cells=[]
		cols=[]
		cells.append(Gtk.CellRendererText())
		cols.append(Gtk.TreeViewColumn(_('Files'), cells[-1], text=1))
		cols[-1].set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
		cols[-1].set_resizable(True)
		cols[-1].set_expand(True)
		cells.append(Gtk.CellRendererProgress());
		cols.append(Gtk.TreeViewColumn(' \t\t%s\t\t '%_('Status'), cells[-1], value=2,pulse=3,text=4))
		cols[-1].set_expand(False)
		self.files_list.set_headers_visible(True)
		self.b_stop.set_sensitive(False)
		self.b_convert.set_sensitive(False)
		for i in cols: self.files_list.insert_column(i, -1)

		self.c_to.set_active(len(formats)-1)
		self.c_to.set_active(0)
		
		self.popupMenu = Gtk.Menu()
		self.build_popup_Menu()
		self.files_list.connect("button-press-event", self.do_popup)
		
		# sample list for testing
		#ls=[("/usr/share/file1.avi",10.0),("file2",20)]
		#self.files.clear()
		#for j,k in ls: self.files.append([j,os.path.basename(j),k,-1,None])
		#self.files[(1,)] = (self.files[1][0], self.files[1][1], 90,-1,"Done %d %%" % 90)
		GObject.timeout_add(250, self.progress_cb)
		#self.options.set_visible(False)
		#print self.options
		
		self.show_all()

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
		self.popupMenu.add(Gtk.SeparatorMenuItem())
		i = Gtk.ImageMenuItem(Gtk.STOCK_REMOVE)
		i.connect("activate", self.rm_cb)
		self.popupMenu.add(i)
		i = Gtk.ImageMenuItem(Gtk.STOCK_CLEAR)
		i.connect("activate", self.clear_cb)
		self.popupMenu.add(i)
		
	def do_popup(self, widget, event):
		iters = self.get_Iters()
		if event.button == 3 and len(iters) > 0:
			self.popupMenu.show_all()
			self.popupMenu.popup(None, self, None, 3, Gtk.get_current_event_time())
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
		if len(self.working_ls)<=0: return True
		self.progressstatus()
		if not self.working_ls[0][0]:
			self.start_subprocess()
			return True
		r = self.working_ls[0][0].poll()
		if r == None:
			self.progress()
			return True
		elif r==0:
			i=self.files[(self.working_ls[0][2],)]
			i[2]= 100.0
			i[3]= -1
			i[4]=_('Done')
			done_item = self.working_ls[0][-1]
			if not done_item in self.done_ls: self.done_ls.append(done_item)
		else:
			i=self.files[(self.working_ls[0][2],)]
			i[2]= 100.0
			i[3]= -1
			i[4]='%s %d' % (_('Error'), r)
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
					self.files.append([f,os.path.basename(f), 0, -1,_('Not started')])
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
		if (dlg.run() == Gtk.ResponseType.ACCEPT):
			for i in dlg.get_filenames():
				self.files.append([i, os.path.basename(i), 0.0, -1, _('Not started')])
			self.addstatus(len(self.files))
			self.cur_src_dir=os.path.dirname(i)
		self.options.conf['src_dir']=self.cur_src_dir
		self.options.save_conf()
		dlg.unselect_all()

	def addstatus(self, fc):
		self.status_bar.push(self.context_id,'%s %i %s' %(_('Click Convert, to start converting'),fc,_('file/files')))
		
	def c_to_cb(self, c,*args):
		#frm=formats[c.get_active()]
		frm = formats[self.c_to.get_model()[self.c_to.get_active()][0]]
		for i,j,k in ((frm[3],self.options.q_a_c,self.options.q_a),(frm[4],self.options.q_v_c,self.options.q_v),(frm[5],self.options.br_a_c,self.options.br_a),(frm[6],self.options.br_v_c,self.options.br_v)):
			j.set_sensitive(i)
			if not i: k.set_sensitive(False); j.set_active(False)
		self.options.hb_ar.set_sensitive(frm[7]);
		if not frm[7]: self.options.ar_c.set_active(False)
		self.options.ar_r.set_active(map(lambda i: i[0],self.options.ar_r.get_model()).index(str(frm[8])))
		
		adj = Gtk.Adjustment(frm[10], frm[11], frm[12], 10, 1, 0)
		self.options.q_a.set_adjustment(adj)
		
		adj = Gtk.Adjustment(frm[14], frm[15], frm[16], 10, 1, 0)
		self.options.q_v.set_adjustment(adj)
		
		adj = Gtk.Adjustment(frm[17],frm[18],frm[19],50, 100, 0)
		self.options.br_a.set_adjustment(adj)
		adj = Gtk.Adjustment(frm[20],frm[21],frm[22],50, 100, 0)
		self.options.br_v.set_adjustment(adj)

	def convert_cb(self, *args):
		self.active_controlls(True)
		frm = formats[self.c_to.get_model()[self.c_to.get_active()][0]]
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
		#	self.status_bar.push(self.context_id,_('Starting operations...'))

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
			i=self.files[(self.working_ls[0][2],)]; i[4]=_('Exists; Skiped');
			self.working_ls.pop(0); return False
		fn=self.working_ls[0][3]
		frm = formats[self.c_to.get_model()[self.c_to.get_active()][0]]
		cmd=self.options.build_cmd(frm, self)
		self.working_ls[0][1]=self.cmd_to_list(fn,ofn,cmd)
		return True

	def skiped(self):
		i = self.files[(self.working_ls[0][2],)]
		i[4]=_('Exists; Skiped')
		self.working_ls.pop(0)
		return 0

	def quit_cb(self, *w):
		if len(self.working_ls)>0:
			if not sure(_('There are corrently running oprations, Stop it?'), self):return True
		self.stop_cb()
		Gtk.main_quit()
		
class options(Gtk.Frame):
	def __init__(self, win):
		Gtk.Frame.__init__(self, label =_('Options...'))
		self.win=win
		self.conf={}
		m_vb=Gtk.VBox(False, 0)
		self.add(m_vb)
		save_fram=Gtk.Frame(label = _('Save Options...'))
		save_fram.set_border_width(4)
		save_fram.set_shadow_type(Gtk.ShadowType.OUT)
		s_vb = Gtk.VBox(False, 0)
		save_fram.add(s_vb)
		dst_l=Gtk.Label(_('Save destination: '))
		self.dst_o1 = Gtk.RadioButton.new_with_label_from_widget(None,_("same as source"))
		self.dst_o2 = Gtk.RadioButton.new_with_label_from_widget(self.dst_o1, _("fixed"))
		self.dst_b=Gtk.FileChooserButton(_("Select destination folder"))
		self.dst_b.set_action(Gtk.FileChooserAction.SELECT_FOLDER)

		x_l=Gtk.Label(_("If exists: "))
		self.x_o1=Gtk.RadioButton.new_with_label_from_widget(None,_("Skip"))
		self.x_o2=Gtk.RadioButton.new_with_label_from_widget(self.x_o1,_("Overwrite"))
		self.x_o3=Gtk.RadioButton.new_with_label_from_widget(self.x_o1,_("Rename"))
		
		hb=Gtk.HBox(False,0)
		s_vb.pack_start(hb,False, False, 2)
		for i in (Gtk.Label(' '),dst_l,self.dst_o1,self.dst_o2,self.dst_b): hb.pack_start(i,False, False, 2)
		hb=Gtk.HBox(False,0)
		s_vb.pack_start(hb,False, False, 2)
		for i in (Gtk.Label(' '),x_l,self.x_o1,self.x_o2,self.x_o3): hb.pack_start(i,False, False, 2)
		m_vb.pack_start(save_fram,False, False, 2)
		# temporal
		#x_o2.set_sensitive(False)
		#x_o3.set_sensitive(False)
		
		self.crp_c = Gtk.CheckButton(_("Crop"))
		crp_hb = Gtk.HBox(False,0);
		crp_hb.set_spacing(4)
		
		adj = Gtk.Adjustment(0, 0, 10000, 2, 10, 0)
		crp_ly1 = Gtk.Label(_("Top"))
		self.crp_dy1 = Gtk.SpinButton()
		self.crp_dy1.set_adjustment(adj)
		
		adj = Gtk.Adjustment(0, 0, 10000, 2, 10, 0)
		crp_ly2=Gtk.Label(_("Bottom"))
		self.crp_dy2 = Gtk.SpinButton()
		self.crp_dy2.set_adjustment(adj)
		
		adj = Gtk.Adjustment(0, 0, 10000, 2, 10, 0)
		crp_lx1=Gtk.Label(_("Left"))
		self.crp_dx1=Gtk.SpinButton()
		self.crp_dx1.set_adjustment(adj)
		
		adj = Gtk.Adjustment(0, 0, 10000, 2, 10, 0)
		crp_lx2=Gtk.Label(_("Right"))
		self.crp_dx2=Gtk.SpinButton()
		self.crp_dx2.set_adjustment(adj)

		self.pad_c=Gtk.CheckButton(_("Pad"))
		pad_hb=Gtk.HBox(False,0)
		pad_ly1=Gtk.Label(_("Top"))
		adj = Gtk.Adjustment(0, 0, 10000, 1, 10, 0)
		self.pad_dy1=Gtk.SpinButton()
		self.pad_dy1.set_adjustment(adj)
		
		adj = Gtk.Adjustment(0, 0, 10000, 1, 10, 0)
		pad_ly2=Gtk.Label(_("Bottom"))
		self.pad_dy2=Gtk.SpinButton()
		self.pad_dy2.set_adjustment(adj)
		
		adj = Gtk.Adjustment(0, 0, 10000, 1, 10, 0)
		pad_lx1 = Gtk.Label(_("Left"))
		self.pad_dx1 = Gtk.SpinButton()
		self.pad_dx1.set_adjustment(adj)
		
		adj = Gtk.Adjustment(0, 0, 10000, 1, 10, 0)
		pad_lx2=Gtk.Label(_("Right"))
		self.pad_dx2=Gtk.SpinButton()
		self.pad_dx2.set_adjustment(adj)

		self.br_a_c=Gtk.CheckButton(_("Audio Bitrates"))
		adj = Gtk.Adjustment(320000, 8000, 10000000, 50, 100, 0)
		self.br_a=Gtk.SpinButton()
		self.br_a.set_adjustment(adj)
		
		br_a_l=Gtk.Label(_("bit/s"));
		self.br_v_c=Gtk.CheckButton(_("Video Bitrates"))
		adj = Gtk.Adjustment(100000, 8000, 10000000, 50, 100, 0)
		self.br_v=Gtk.SpinButton()
		self.br_v.set_adjustment(adj)
		br_v_l=Gtk.Label(_("bit/s"));

		self.q_a_c=Gtk.CheckButton(_("Audio Quality"))
		adj = Gtk.Adjustment(3, 0, 10,0)
		self.q_a=Gtk.HScale()
		self.q_a.set_adjustment(adj)
		self.q_a.set_property("value-pos", Gtk.PositionType.LEFT)
		self.q_v_c=Gtk.CheckButton(_("Video Quality"))
		adj = Gtk.Adjustment(10, 0, 100,0)
		self.q_v=Gtk.HScale()
		self.q_v.set_adjustment(adj)
		self.q_v.set_property("value-pos",Gtk.PositionType.LEFT)

		self.ar_c=Gtk.CheckButton(_("Audio Samplerate"))
		self.ar_r = create_combo(Gtk.ComboBoxText(), map(lambda i: str(i),list(range(11025,48101,11025)+list(range(8000,48001,8000))) ),2)
		
		self.scale_dict={}
		for i in filter(lambda a: a!=_("custom"),scale_ls):
			a = i.split(' ')
			self.scale_dict[a[1]]=i
		
		self.scale_c=Gtk.CheckButton(_("Resize"))
		scale_hb = Gtk.HBox(False, 0);
		scale_hb.set_spacing(4)
		self.scale_l=create_combo(Gtk.ComboBoxText(), scale_ls,2)
		adj = Gtk.Adjustment(0, 0, 10000, 1, 10, 0)
		self.scale_w=Gtk.SpinButton()
		self.scale_w.set_adjustment(adj)
		self.scale_x=Gtk.Label("x");
		
		adj = Gtk.Adjustment(0, 0, 10000, 1, 10, 0)
		self.scale_h=Gtk.SpinButton()
		self.scale_h.set_adjustment(adj)
		cs_vb=Gtk.VBox(False, 0)
		c_hb = Gtk.HBox(False, 0)
		convs_fram=Gtk.Frame(label = _('Convert Options...'))
		convs_fram.set_border_width(4)
		convs_fram.set_shadow_type(Gtk.ShadowType.OUT)
		convs_fram.add(cs_vb)
		c_hb.pack_start(convs_fram,False, False, 2)
		#m_vb.pack_start(c_hb,False, False, 2)

		c_vb = Gtk.VBox(False, 0)
		c_vb.set_spacing(4)
		c_vb.set_border_width(5)
		conv_fram = Gtk.Frame(label = _('Advanced Options...'))
		conv_fram.set_border_width(4)
		conv_fram.set_shadow_type(Gtk.ShadowType.OUT)
		conv_fram.add(c_vb)
		c_hb.pack_start(conv_fram, True, True, 2)
		m_vb.pack_start(c_hb, False, False, 2)

		hb=Gtk.HBox(False,0)
		cs_vb.pack_start(hb,False, False, 2)
		self.quality_l = q = create_combo(Gtk.ComboBoxText(), ['a','b','c'],1)
		q.connect('changed', self.set_options_cb)
		hb.pack_start(Gtk.Label(_("Quality:")),False, False, 2)
		hb.pack_start(q,True, True, 2)
		
		hb = Gtk.HBox(False,0)
		c_vb.pack_start(hb,False, False, 2)
		hb.pack_start(self.crp_c,False, False, 2)
		hb.pack_start(crp_hb,True, True, 2)
		for i in (crp_ly1,self.crp_dy1,crp_ly2,self.crp_dy2,crp_lx1,self.crp_dx1,crp_lx2,self.crp_dx2):
			crp_hb.pack_start(i, False, False, 2)

		hb = Gtk.HBox(False,0)
		c_vb.pack_start(hb,False, False, 2)
		hb.pack_start(self.scale_c,False, False, 2)
		hb.pack_start(scale_hb,True, True, 2)
		for i in (self.scale_l,self.scale_w,self.scale_x,self.scale_h): scale_hb.pack_start(i,False, False, 2)

		hb=Gtk.HBox(False,0)
		c_vb.pack_start(hb,False, False, 2)
		hb.pack_start(self.pad_c,False, False, 2)
		hb.pack_start(pad_hb,True, True, 2)
		for i in (pad_ly1,self.pad_dy1,pad_ly2,self.pad_dy2,pad_lx1,self.pad_dx1,pad_lx2,self.pad_dx2): pad_hb.pack_start(i,False, False, 2)

		hb_br=Gtk.HBox(False,0)
		c_vb.pack_start(hb_br,False, False, 2)
		for i in (self.br_a_c,self.br_a,br_a_l, Gtk.VSeparator(),self.br_v_c,self.br_v,br_v_l): hb_br.pack_start(i,False, False, 2)

		hb_q=Gtk.HBox(False,0)
		c_vb.pack_start(hb_q,False, False, 2)
		for i in (self.q_a_c,self.q_a, Gtk.VSeparator(),self.q_v_c,self.q_v): hb_q.pack_start(i,type(i)==Gtk.HScale, type(i)==Gtk.HScale, 2)


		self.hb_ar=Gtk.HBox(False,0)
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
		
	def set_options_cb(self, c):
		print c.get_active()
		
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
		
	def scale_cb(self, c,w,h):
		s=c.get_model()[c.get_active()][0]
		if s==_("custom"): return
		n,r = s.split(' ')
		W,H = r.split('x')
		w.set_value(float(W))
		h.set_value(float(H));

	def scale_wh_cb(self, m,w,h,l):
		scale_dict=self.scale_dict
		W=w.get_value()
		H=h.get_value()
		S='%dx%d' % (W,H)
		if S not in scale_dict: l.set_active(scale_ls.index(_("custom")))
		elif scale_dict[S]!=l.get_model()[l.get_active()][0]:
			l.set_active(scale_ls.index(scale_dict[S]))

	def build_cmd(self, frm, win=None):
		ext = frm[0] #.split(' ')[0]
		
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
			opts['br_v']='-b %dK' % self.br_v.get_value()
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
	 
class add_dlg(Gtk.FileChooserDialog):
	def __init__(self):
		Gtk.FileChooserDialog.__init__(self,_("Select files to convert"),
								buttons =(Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT, Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))
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
	def __init__(self):
		Gtk.AboutDialog.__init__(self)
		self.set_default_response(Gtk.ResponseType.CLOSE)
		self.connect('delete-event', lambda *w: self.hide())
		self.connect('response', lambda *w: self.hide())
		try: self.set_program_name(_("MiMiC"))
		except AttributeError: pass
		self.set_logo_icon_name('ojuba-mimic')
		self.set_name(_("MiMiC"))
		self.set_wrap_license(True)
		#about_dlg.set_version(version)
		self.set_copyright(_("Copyright © 2008-2012 Ojuba.org <core@ojuba.org>"))
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
		self.set_authors(["Muayyad Saleh Alsadi <alsadi@ojuba.org>", "Ehab El-Gedawy <ehabsas@gmail.com>", "Fayssal Chamekh <chamfay@gmail.com>"])
		self.connect('delete_event', self.delete)
	
	def delete(self, widget, data):
		return True

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
	try: Gtk.main()
	except KeyboardInterrupt: win.stop_cb()
	
if __name__ == "__main__":
	main()
