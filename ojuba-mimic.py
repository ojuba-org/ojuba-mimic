#! /usr/bin/python
# -*- coding: utf-8 -*-
"""
	Multi Media Converter that utilize gstreamer and/or ffmpeg
	Copyright © 2008, ojuba.org Muayyad Saleh Al-Sadi<alsadi@gmail.com>
	Released under terms of Waqf Public License
"""
import os
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
from subprocess import Popen
win,vb,dlg,files=None,None,None,None
#".ext (human readable type)", is_video, cmd, q_a,q_v, br_a,br_v, allow_audio_resample, default_ar
# audio quality float/int, default, from , to, 
# video quality float/int, default, from , to,
# audio bitrate default , from, to,
# video bitrate default , from, to,
# [disabled flag that can be turned on],
# validity python eval check, fauler msg
formats=[
(".ogg (Ogg/Theora video)", True, "-f ogg -acodec libvorbis -ac 2 %(audio_quality)s -vcodec libtheora %(video_quality)s", 1, 1, 0, 0, 1, 44100, 
 float, 3, 0, 10, float, 10, 1, 100, 
 0, 0, 0, 0, 0, 0, [], 'True',''),
(".3gp (3GP)", True, "-f 3gp -acodec libopencore_amrnb -ar 8000 -ac 1 -vcodec h263", 0, 0, 1, 1, 0, 8000, 
 float, 3, 0, 10, float, 10, 1, 100, 
 4750, 4750, 12200, 4750, 4750, 10000000, [], 'size in ("-s 128x96", "-s 176x144", "-s 352x288", "-s 704x576", "-s 1408x1152") and audio_bitrate in (4750, 5150, 5900, 6700, 7400, 7950, 10200, 12200)','choose a vlid size and bitrate (try cif and 4750)'),
(".flv (Flash Video)", True, '-acodec libmp3lame -r 25 -vcodec flv', 0, 1, 1, 0, 1, 22050, 
 float, 3, 0, 10, int, 10, 1, 100,
 32000, 8000, 1000000, 100000, 10000, 10000000, [], 'audio_samplerate in (44100, 22050, 11025)','audio samplerate should be 44100, 22050 or 11025'),
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
(".mpg (film)",True, "-f mpeg -target ntsc-film", 0, 0, 0, 0, 0, 44100, 
 int, 0, 0, 0, int, 0, 0, 0, 
32000, 8000, 1000000, 100000, 10000, 10000000, ['-flags qprd','-flags mv0','-flags skiprd','-g 100'], 'True',''),

(".mpg (mpeg1)",True, "-f mpeg -acodec libmp3lame -vcodec mpeg1video -mbd rd -flags +trell -cmp 2 -subcmp 2 -bf 2", 0, 0, 1, 1, 1, 44100, 
 int, 0, 0, 0, int, 0, 0, 0, 
32000, 8000, 1000000, 100000, 10000, 10000000, ['-flags qprd','-flags mv0','-flags skiprd','-g 100'], 'True',''),
(".mpg (mpeg2)",True, "-f mpeg -acodec libmp3lame -vcodec mpeg2video -mbd rd -flags +trell -cmp 2 -subcmp 2 -bf 2", 0, 0, 1, 1, 1, 44100, 
 int, 0, 0, 0, int, 0, 0, 0, 
32000, 8000, 1000000, 100000, 10000, 10000000, [], 'True',''),
(".mp4 (psp ~30fps)",True,"-f psp -acodec libfaac -vcodec mpeg4 -ar 24000 -r 30000/1001 -bf 2", 0, 0, 1, 1, 0, 24000, 
 int, 0, 0, 0, int, 0, 0, 0,  
32000, 8000, 1000000, 100000, 10000, 10000000, [],
 'not size and width*height<=76800 and width%16==0 and height%16==0','Width and Hight must be multibles of 16 or too big resolution'),
(".mp4 (psp ~15fps)",True,"-f psp -acodec libfaac -vcodec mpeg4 -ar 24000 -r 15000/1001 -bf 2", 0, 0, 1, 1, 0, 24000, 
 int, 0, 0, 0, int, 0, 0, 0, 
32000, 8000, 1000000, 100000, 10000, 10000000, [],
 'not size or width*height<=76800 and width%16==0 and height%16==0','Width and Hight must be multibles of 16 or too big resolution'),
('.mp4 (ipod)',True,'-acodec libfaac -vcodec mpeg4 -mbd 2 -flags +4mv+trell -aic 2 -cmp 2 -subcmp 2 -bf 2', 0, 0, 1, 1, 1, 22050, 
 int, 0, 0, 0, int, 0, 0, 0, 
32000, 8000, 1000000, 100000, 10000, 10000000, [],
 'not size or width<=320 and height<=240','too big resolution, resize it so that width<=320 and height<=240'),
('.avi (MPEG4 like DviX)',True,'-f avi -mbd rd -flags +4mv+trell+aic -cmp 2 -subcmp 2 -g 300 -acodec libfaac -vcodec mpeg4 -vtag DIV5 -bf 2', 0, 0, 1, 1, 1, 44100, 
 int, 0, 0, 0, int, 0, 0, 0, 
32000, 8000, 1000000, 100000, 10000, 10000000, [],'True',''),
('.avi (xvid)', True, '-f avi -mbd rd -flags +4mv+trell+aic -cmp 2 -subcmp 2 -g 300 -acodec libmp3lame -vcodec libxvid -vtag xvid -bf 2', 0, 0, 1, 1, 1, 44100, 
 int, 0, 0, 0, int, 0, 0, 0, 
32000, 8000, 1000000, 100000, 10000, 10000000, [],'True',''),
('.mpg (mpeg4)', True, '-f mpeg -mbd rd -flags +4mv+trell+aic -cmp 2 -subcmp 2 -g 300 -acodec libfaac -vcodec mpeg4 -vtag DIV5 -bf 2', 0, 0, 1, 1, 1, 44100, 
 int, 0, 0, 0, int, 0, 0, 0, 
32000, 8000, 1000000, 100000, 10000, 10000000, [],'True',''),
('.mpg (xvid mpeg4)',True,'-f mpeg -mbd rd -flags +4mv+trell+aic -cmp 2 -subcmp 2 -g 300 -acodec libfaac -vcodec libxvid -vtag xvid -bf 2', 0, 0, 1, 1, 1, 44100, 
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

working_ls=[]

scale_dict={}
scale_ls=["sqcif 128x96", "qcif 176x144", "cif 352x288", "4cif 704x576",
"qqvga 160x120", "qvga 320x240", "vga 640x480", "svga 800x600",
"xga 1024x768", "uxga 1600x1200", "qxga 2048x1536", "sxga 1280x1024",
"qsxga 2560x2048", "hsxga 5120x4096", "wvga 852x480", "wxga 1366x768",
"wsxga 1600x1024", "wuxga 1920x1200", "woxga 2560x1600", "wqsxga 3200x2048",
"wquxga 3840x2400", "whsxga 6400x4096", "whuxga 7680x4800", "cga 320x200",
"ega 640x350", "hd480 852x480", "hd720 1280x720", "hd1080 1920x1080","custom"]
cells=[]
cols=[]
targets_l=gtk.target_list_add_uri_targets()

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

def main():
  build_gui()
  gobject.timeout_add(250, progress_cb)
  gtk.main()

def quit(*args):
  #stop()
  gtk.main_quit()
def hide_cb(w, *args): w.hide(); return True

def build_about():
	global about_dlg
	about_dlg=gtk.AboutDialog()
	about_dlg.set_default_response(gtk.RESPONSE_CLOSE)
	about_dlg.connect('delete-event', hide_cb)
	about_dlg.connect('response', hide_cb)
	try: about_dlg.set_program_name("MiMiC")
	except: pass
	about_dlg.set_name("MiMiC")
	#about_dlg.set_version(version)
	about_dlg.set_copyright("Copyright (c) 2008 Muayyad Saleh Alsadi <alsadi@ojuba.org>")
	about_dlg.set_comments("Multi Media Converter")
	about_dlg.set_license("""
    Released under terms on Waqf Public License.
    This program is free software; you can redistribute it and/or modify
    it under the terms of the latest version Waqf Public License as
    published by Ojuba.org.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

    The Latest version of the license can be found on
    "http://www.ojuba.org/wiki/doku.php/رخصة وقف العامة"

""")
	about_dlg.set_website("http://www.ojuba.org/")
	about_dlg.set_website_label("http://www.ojuba.org")
	about_dlg.set_authors(["Muayyad Saleh Alsadi <alsadi@ojuba.org>"])

def build_add_dlg():
  global dlg;
  dlg=gtk.FileChooserDialog("Select files to convert",buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
  ff=gtk.FileFilter()
  ff.set_name('All media files')
  ff.add_mime_type('video/*')
  ff.add_mime_type('audio/*')
  ff.add_pattern('*.[Rr][AaMm]*')
  dlg.add_filter(ff)
  ff=gtk.FileFilter()
  ff.set_name('All video files')
  ff.add_mime_type('video/*')
  ff.add_pattern('*.[Rr][AaMm]*')
  dlg.add_filter(ff)
  ff=gtk.FileFilter()
  ff.set_name('All audio files')
  ff.add_mime_type('audio/*')
  ff.add_pattern('*.[Rr][AaMm]*')
  dlg.add_filter(ff)  
  ff=gtk.FileFilter()
  ff.set_name('All files')
  ff.add_pattern('*')
  dlg.add_filter(ff)
  dlg.set_select_multiple(True)
  dlg.connect('delete-event', hide_cb)
  dlg.connect('response', hide_cb)

def create_combo(ls,w=1):
  c = gtk.combo_box_new_text(); c.set_wrap_width(w)
  for i in ls: c.append_text(i)
  c.set_active(0)
  return c

def update_combo(c,ls):
  c.get_model().clear()
  for i in ls: c.append_text(i)

def add_files_cb(*args):
  global dlg,files
  if (dlg.run()==gtk.RESPONSE_ACCEPT):
    for i in dlg.get_filenames(): files.append([i,basename(i),0,-1,"Not started"])
  dlg.unselect_all()

def scale_cb(c,w,h):
  s=c.get_model()[c.get_active()][0]
  if s=='custom': return
  n,r=s.split(' '); W,H=r.split('x')
  w.set_value(float(W)); h.set_value(float(H));
def scale_wh_cb(m,w,h,l):
  global scale_dict
  W=w.get_value()
  H=h.get_value()
  S='%dx%d' % (W,H)
  if S not in scale_dict: l.set_active(scale_ls.index("custom"))
  elif scale_dict[S]!=l.get_model()[l.get_active()][0]:
    l.set_active(scale_ls.index(scale_dict[S]))

def build_options():
  global vb,scale_dict,dst_o2,dst_b,x_o1,x_o2,x_o3
  global crp_c, crp_hb, crp_dy1,crp_dy2,crp_dx1,crp_dx2
  global scale_c, scale_hb, scale_w,scale_h
  global pad_c, pad_hb, pad_dy1,pad_dy2,pad_dx1,pad_dx2
  global hb_br, br_a_c, br_a, br_v_c, br_v
  global hb_q,q_a_c, q_a,q_v_c, q_v
  global hb_ar,ar_c, ar_r

  dst_l=gtk.Label("Save destination: ")
  dst_o1=gtk.RadioButton(None,"same as source")
  dst_o2=gtk.RadioButton(dst_o1,"fixed")
  dst_b=gtk.FileChooserButton("Select destination folder")
  dst_b.set_action(gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER)

  x_l=gtk.Label("If exists: ")
  x_o1=gtk.RadioButton(None,"Skip")
  x_o2=gtk.RadioButton(x_o1,"Overwrite")
  x_o3=gtk.RadioButton(x_o1,"Rename")
  # temporal
  #x_o2.set_sensitive(False)
  #x_o3.set_sensitive(False)
  
  crp_c=gtk.CheckButton("Crop")
  crp_hb=gtk.HBox(False,0);
  
  crp_ly1=gtk.Label("Top"); crp_dy1=gtk.SpinButton(gtk.Adjustment(0, 0, 10000, 2, 10, 0))
  crp_ly2=gtk.Label("Bottom"); crp_dy2=gtk.SpinButton(gtk.Adjustment(0, 0, 10000, 2, 10, 0))
  crp_lx1=gtk.Label("Left"); crp_dx1=gtk.SpinButton(gtk.Adjustment(0, 0, 10000, 2, 10, 0))
  crp_lx2=gtk.Label("Right"); crp_dx2=gtk.SpinButton(gtk.Adjustment(0, 0, 10000, 2, 10, 0))

  pad_c=gtk.CheckButton("Pad")
  pad_hb=gtk.HBox(False,0);
  pad_ly1=gtk.Label("Top"); pad_dy1=gtk.SpinButton(gtk.Adjustment(0, 0, 10000, 1, 10, 0))
  pad_ly2=gtk.Label("Bottom"); pad_dy2=gtk.SpinButton(gtk.Adjustment(0, 0, 10000, 1, 10, 0))
  pad_lx1=gtk.Label("Left"); pad_dx1=gtk.SpinButton(gtk.Adjustment(0, 0, 10000, 1, 10, 0))
  pad_lx2=gtk.Label("Right"); pad_dx2=gtk.SpinButton(gtk.Adjustment(0, 0, 10000, 1, 10, 0))

  br_a_c=gtk.CheckButton("Audio Bitrates")
  br_a=gtk.SpinButton(gtk.Adjustment(320000, 8000, 10000000, 50, 100, 0))
  br_a_l=gtk.Label("bit/s");
  br_v_c=gtk.CheckButton("Video Bitrates")
  br_v=gtk.SpinButton(gtk.Adjustment(100000, 8000, 10000000, 50, 100, 0))
  br_v_l=gtk.Label("bit/s");

  q_a_c=gtk.CheckButton("Audio Quality")
  q_a=gtk.HScale(gtk.Adjustment(3, 0, 10,0))
  q_a.set_property("value-pos",gtk.POS_LEFT)
  q_v_c=gtk.CheckButton("Video Quality")
  q_v=gtk.HScale(gtk.Adjustment(10, 0, 100,0))
  q_v.set_property("value-pos",gtk.POS_LEFT)

  ar_c=gtk.CheckButton("Audio Samplerate")
  ar_r=create_combo(map(lambda i: str(i),list(range(11025,48101,11025)+list(range(8000,48001,8000))) ),2)
  
  scale_dict={}
  for i in filter(lambda a: a!='custom',scale_ls): a=i.split(' '); scale_dict[a[1]]=i
  scale_c=gtk.CheckButton("Resize")
  scale_hb=gtk.HBox(False,0);
  scale_l=create_combo(scale_ls,2)
  scale_w=gtk.SpinButton(gtk.Adjustment(0, 0, 10000, 1, 10, 0))
  scale_x=gtk.Label("x");
  scale_h=gtk.SpinButton(gtk.Adjustment(0, 0, 10000, 1, 10, 0))

  hb=gtk.HBox(False,0); vb.pack_start(hb,False, False, 2)
  for i in (dst_l,dst_o1,dst_o2,dst_b): hb.pack_start(i,False, False, 2)
  hb=gtk.HBox(False,0); vb.pack_start(hb,False, False, 2)
  for i in (x_l,x_o1,x_o2,x_o3): hb.pack_start(i,False, False, 2)
  hb=gtk.HBox(False,0); vb.pack_start(hb,False, False, 2)
  hb.pack_start(crp_c,False, False, 2)
  hb.pack_start(crp_hb,True, True, 2)
  for i in (crp_ly1,crp_dy1,crp_ly2,crp_dy2,crp_lx1,crp_dx1,crp_lx2,crp_dx2): crp_hb.pack_start(i,False, False, 2)

  hb=gtk.HBox(False,0); vb.pack_start(hb,False, False, 2)
  hb.pack_start(scale_c,False, False, 2)
  hb.pack_start(scale_hb,True, True, 2)
  for i in (scale_l,scale_w,scale_x,scale_h): scale_hb.pack_start(i,False, False, 2)

  hb=gtk.HBox(False,0); vb.pack_start(hb,False, False, 2)
  hb.pack_start(pad_c,False, False, 2)
  hb.pack_start(pad_hb,True, True, 2)
  for i in (pad_ly1,pad_dy1,pad_ly2,pad_dy2,pad_lx1,pad_dx1,pad_lx2,pad_dx2): pad_hb.pack_start(i,False, False, 2)

  hb_br=gtk.HBox(False,0); vb.pack_start(hb_br,False, False, 2)
  for i in (br_a_c,br_a,br_a_l, gtk.VSeparator(),br_v_c,br_v,br_v_l): hb_br.pack_start(i,False, False, 2)

  hb_q=gtk.HBox(False,0); vb.pack_start(hb_q,False, False, 2)
  for i in (q_a_c,q_a, gtk.VSeparator(),q_v_c,q_v): hb_q.pack_start(i,type(i)==gtk.HScale, type(i)==gtk.HScale, 2)


  hb_ar=gtk.HBox(False,0); vb.pack_start(hb_ar,False, False, 2)
  for i in (ar_c,ar_r): hb_ar.pack_start(i,False, False, 2)
  
  dst_o2.connect('toggled', lambda *args: dst_b.set_sensitive(dst_o2.get_active()))
  for i,j in ((crp_c,crp_hb),(pad_c,pad_hb),(scale_c,scale_hb),(br_a_c,br_a),(br_v_c,br_v),(q_a_c,q_a),(q_v_c,q_v),(ar_c,ar_r)):
    i.connect('toggled', lambda i,j: j.set_sensitive(i.get_active()),j)
    i.set_active(False); j.set_sensitive(False)
  scale_l.connect('changed', scale_cb,scale_w,scale_h)
  scale_w.connect('changed', scale_wh_cb,scale_w,scale_h,scale_l)
  scale_h.connect('changed', scale_wh_cb,scale_w,scale_h,scale_l)
  scale_w.connect('activate', scale_wh_cb,scale_w,scale_h,scale_l)
  scale_h.connect('activate', scale_wh_cb,scale_w,scale_h,scale_l)  
  scale_w.connect_after('focus-out-event', lambda a,*args: a.activate() and False)
  scale_h.connect_after('focus-out-event', lambda a,*args: a.activate() and False)
  dst_b.set_sensitive(dst_o2.get_active())
  scale_l.set_active(scale_ls.index("qvga 320x240"))
  x_o3.set_active(True)

def c_to_cb(c,*args):
  global formats
  global crp_c, crp_hb, crp_dy1,crp_dy2,crp_dx1,crp_dx2
  global scale_c, scale_hb, scale_w,scale_h
  global pad_c, pad_hb, pad_dy1,pad_dy2,pad_dx1,pad_dx2
  global hb_br, br_a_c, br_a, br_v_c, br_v
  global hb_q,q_a_c, q_a,q_v_c, q_v
  global hb_ar,ar_c, ar_r

  frm=formats[c.get_active()]
  for i,j,k in ((frm[3],q_a_c,q_a),(frm[4],q_v_c,q_v),(frm[5],br_a_c,br_a),(frm[6],br_v_c,br_v)):
    j.set_sensitive(i)
    if not i: k.set_sensitive(False); j.set_active(False)

  hb_ar.set_sensitive(frm[7]);
  if not frm[7]: ar_c.set_active(False)

  ar_r.set_active(map(lambda i: i[0],ar_r.get_model()).index(str(frm[8])))
  q_a.get_adjustment().set_all(frm[10], frm[11], frm[12], 10, 1, 0)
  q_v.get_adjustment().set_all(frm[14], frm[15], frm[16], 10, 1, 0)
  br_a.get_adjustment().set_all(frm[17],frm[18],frm[19],50, 100, 0)
  br_v.get_adjustment().set_all(frm[20],frm[21],frm[22],50, 100, 0)

def modNfix(i,n=2): return i-(i%n)

def build_cmd():
  global crp_c, crp_hb, crp_dy1,crp_dy2,crp_dx1,crp_dx2
  global scale_c, scale_hb, scale_w,scale_h
  global pad_c, pad_hb, pad_dy1,pad_dy2,pad_dx1,pad_dx2
  global hb_br, br_a_c, br_a, br_a_v, br_v
  global hb_q,q_a_c, q_a,q_v_c, q_v
  global hb_ar,ar_c, ar_r

  frm=formats[c_to.get_active()]
  ext=frm[0].split(' ')[0]
  
  opts={}
  # make things even:
  for i in (crp_dy1,crp_dy2,crp_dx1,crp_dx2,scale_w,scale_h,pad_dy1,pad_dy2,pad_dx1,pad_dx2): i.set_value(modNfix(int(i.get_value())))
  #
  if crp_c.get_active():
    opts['croptop']=('','-croptop %d' % crp_dy1.get_value())[bool(crp_dy1.get_value())]
    opts['cropbottom']=('','-cropbottom %d' % crp_dy2.get_value())[bool(crp_dy2.get_value())]
    opts['cropleft']=('','-cropright %d' % crp_dx1.get_value())[bool(crp_dx1.get_value())]
    opts['cropright']=('','-cropleft %d' % crp_dx2.get_value())[bool(crp_dx2.get_value())]
    opts['crop']=' '.join((opts['croptop'],opts['cropbottom'],opts['cropright'],opts['cropleft']))
  else: opts['crop']=''; opts['croptop']=''; opts['cropbottom']=''; opts['cropleft']=''; opts['cropright']=''
  if pad_c.get_active():
    opts['padtop']=('','-padtop %d' % pad_dy1.get_value())[bool(pad_dy1.get_value())]
    opts['padbottom']=('','-padbottom %d' % pad_dy2.get_value())[bool(pad_dy2.get_value())]
    opts['padleft']=('','-padright %d' % pad_dx1.get_value())[bool(pad_dx1.get_value())]
    opts['padright']=('','-padleft %d' % pad_dx2.get_value())[bool(pad_dx2.get_value())]
    opts['pad']=' '.join((opts['padtop'],opts['padbottom'],opts['padright'],opts['padleft']))
    #if opts['pad']: opts['pad']+' -padcolor 000000'
  else: opts['pad']=''; opts['padtop']=''; opts['padbottom']=''; opts['padleft']=''; opts['padright']=''

  if scale_c.get_active():
    opts['width']=scale_w.get_value(); opts['height']=scale_h.get_value()
    opts['size']='-s %dx%d' % (scale_w.get_value(),scale_h.get_value())
  else: opts['width']=''; opts['height']=''; opts['size']='';
  if q_a_c.get_active():
    opts['audio_quality']=(('-aq %d','-aq %g')[frm[9]==float] ) % frm[9](q_a.get_value())
  else: opts['audio_quality']=''
  if q_v_c.get_active():
    opts['video_quality']=(('-qscale %d','-qscale %g')[frm[13]==float] ) % frm[13](q_v.get_value())
  else: opts['video_quality']=''
  if br_a_c.get_active():
    opts['audio_bitrate']=br_a.get_value()
    opts['br_a']='-ab %d' % br_a.get_value()
  else: opts['br_a']=opts['audio_bitrate']=''
  if br_v_c.get_active():
    opts['video_bitrate']=br_v.get_value()
    opts['br_v']='-b %d' % br_v.get_value()
  else: opts['br_v']=opts['video_bitrate']=''
  if ar_c.get_active(): opts['audio_samplerate']=int(ar_r.get_model()[ar_r.get_active()][0]); opts['ar']='-ar %d' % opts['audio_samplerate']
  else: opts['ar']=opts['audio_samplerate']=''
  if not frm[1]: opts['size']=''; opts['br_v']=''; opts['q_v']=''

  if not eval(frm[24],opts): bad(frm[25]); return None
  cmd=' '.join((frm[2] % opts,opts['ar'],opts['br_a'],opts['br_v'],opts['crop'],opts['size'],opts['pad']))
  return cmd
def pulse_cb(i):
  files[(i,)][2]=0
  files[(i,)][3]=int(abs(files[(i,)][3])+1)
  gtk.main_iteration()

def progress(*args):
  global working_ls;
  p,icmd,i,fn,ofn=working_ls[0]
  working_size=os.path.getsize(ofn)
  if working_size==0: pulse_cb(i); return True
  try: s=os.path.getsize(fn)
  except: pulse_cb(i); return True
  if working_size==0 or s<working_size: pulse_cb(i); return True
  files[(i,)][2]=(float(working_size)/s)*100.0
  gtk.main_iteration()
  return True;

def suffex_gen():
  for i in xrange(0,0xFFFF): yield str(i)
  for i in xrange(0,0xFFFF): yield '_'+str(i)
  for i in xrange(0,0xFFFF): yield '_'+str(i)
  for j in xrange(65,91):
    for i in suffex_gen(): yield chr(j)+str(i)

def suggest_name(f):
  dn=dirname(f)
  fn=basename(f)
  b,d,e=fn.partition('.')
  for i in suffex_gen():
     f=os.path.join(dn,''.join((b,'_',i,d,e)))
     if not os.path.exists(f): return f
  return None

def rename_cb():
  ofn=working_ls[0][4]=suggest_name(working_ls[0][4])
  if not ofn:
    i=files[(working_ls[0][2],)]; i[4]='Exists; Skiped';
    working_ls.pop(0); return False
  fn=working_ls[0][3]
  cmd=build_cmd()
  working_ls[0][1]="ffmpeg -y -i 'file://%s' %s 'file://%s'" % (fn,cmd,ofn)
  return True

def skiped():
  i=files[(working_ls[0][2],)]
  i[4]='Exists; Skiped'
  working_ls.pop(0)
  return 0
def start_subprocess():
  global working_ls
  if working_ls[0][3]==working_ls[0][4]:
    if x_o3.get_active():
      if not rename_cb(): return skiped()
    else: return skiped()
  if os.path.exists(working_ls[0][4]):
    if x_o3.get_active():
      if not rename_cb(): return skiped()
    elif x_o1.get_active():
      return skiped()
  working_ls[0][0]=Popen(working_ls[0][1],0,'/bin/sh',shell=True)
  i=files[(working_ls[0][2],)]; i[2]=0; i[3]=-1; i[4]='Converting ...'
  #working_ls.append()=[None,icmd,working_on,fn,ofn]
def progress_cb(*args):
  global working_ls
  #print "*", len(working_ls)
  b_stop.set_sensitive(len(working_ls)>0);
  b_convert.set_sensitive(len(working_ls)<=0)
  if len(working_ls)<=0: return True
  if not working_ls[0][0]: start_subprocess(); return True
  r=working_ls[0][0].poll()
  if r==None: progress(); return True
  elif r==0: i=files[(working_ls[0][2],)]; i[2]=100; i[3]=-1; i[4]='Done'
  else: i=files[(working_ls[0][2],)]; i[2]=100; i[3]=-1; i[4]='Error %d' % r
  working_ls.pop(0)
  return True

def convert_cb(*args):
  global working_ls
  b_convert.set_sensitive(False)
  frm=formats[c_to.get_active()]
  cmd=build_cmd()
  if not cmd: return
  if dst_o2.get_active(): oodir=dst_b.get_filename();
  else: oodir=False
  working_ls=[]
  for working_on,i in enumerate(files):
    fn=i[0]; bfn=basename(fn)
    if not oodir: odir=dirname(fn)
    else: odir=oodir
    ofn=os.path.join(odir, bfn.partition('.')[0]+frm[0][:frm[0].index(' ')])
    #if fn==ofn or os.path.exists(ofn): i[4]='Exists; Skiped'; continue
    #i[2]=0; i[3]=-1; i[4]='Converting ...'
    icmd="ffmpeg -y -i 'file://%s' %s 'file://%s'" % (fn,cmd,ofn)
    print icmd
    working_ls.append([None,icmd,working_on,fn,ofn])
    #print icmd
    #working_fn=ofn; working_size=os.stat(fn)
    #r=os.system(icmd)
    #if r: i[2]=100; i[3]=-1; i[4]='Error %d' % r
    #else: i[2]=100; i[3]=-1; i[4]='Done'
    #files[(working_on,)][2]= 100
  working_on=-1 # not needed
def stop_cb(*args):
  global working_ls
  for j in working_ls:
    if j[0]:
      try: os.kill(j[0].pid,signal.SIGTERM); i=files[(working_ls[0][2],)]; i[4]='Canceled';
      except: pass
  working_ls=[]
  b_convert.set_sensitive(True)

def drop_data_cb(widget, dc, x, y, selection_data, info, t):
  global files
  for i in selection_data.get_uris():
    if i.startswith('file://'): f=unquote(i[7:]); files.append([f,basename(f),0,-1,"Not started"])
    else: print "Protocol not supported in [%s]" % i
  dc.drop_finish (True, t);

def build_gui():
  global win,dlg,files,cells,cols,vb,c_to,b_stop,b_convert
  build_add_dlg()
  build_about()
  win=gtk.Window()
  win.drag_dest_set(gtk.DEST_DEFAULT_ALL,targets_l,(1<<5)-1)
  win.set_title('MiMiC :: Multi Media Converter')
  #win.set_size_request(500, 200)
  win.connect('destroy', quit)
  win.connect('drag-data-received',drop_data_cb)
  
  
  v=['وَمِنَ النَّاسِ مَنْ يَشْتَرِي لَهْوَ الْحَدِيثِ لِيُضِلَّ عَنْ سَبِيلِ اللَّهِ\nبِغَيْرِ عِلْمٍ وَيَتَّخِذَهَا هُزُوًا أُولَئِكَ لَهُمْ عَذَابٌ مُهِينٌ'
  ,'إِنَّ الَّذِينَ يُحِبُّونَ أَنْ تَشِيعَ الْفَاحِشَةُ فِي الَّذِينَ آَمَنُوا لَهُمْ عَذَابٌ أَلِيمٌ\nفِي الدُّنْيَا وَالْآَخِرَةِ وَاللَّهُ يَعْلَمُ وَأَنْتُمْ لَا تَعْلَمُونَ',
  'قُلْ لِلْمُؤْمِنِينَ يَغُضُّوا مِنْ أَبْصَارِهِمْ وَيَحْفَظُوا فُرُوجَهُمْ\nذَلِكَ أَزْكَى لَهُمْ إِنَّ اللَّهَ خَبِيرٌ بِمَا يَصْنَعُونَ',
  'فَخَلَفَ مِنْ بَعْدِهِمْ خَلْفٌ أَضَاعُوا الصَّلَاةَ وَاتَّبَعُوا الشَّهَوَاتِ فَسَوْفَ يَلْقَوْنَ غَيّاً'
]
  
  l_banner_box=gtk.EventBox()
  for i in (gtk.STATE_NORMAL,gtk.STATE_ACTIVE,gtk.STATE_PRELIGHT,gtk.STATE_SELECTED,gtk.STATE_INSENSITIVE):
    l_banner_box.modify_bg(i,gtk.gdk.color_parse("#fffff8"))
  l_banner=gtk.Label(); l_banner.set_justify(gtk.JUSTIFY_CENTER)
  l_banner.set_markup('''<span face="Simplified Naskh" color="#204000"  size="x-large">%(verse)s</span>''' % {'verse':random.choice(v)})
  l_banner_box.add(l_banner)
  b_add=gtk.Button(stock=gtk.STOCK_ADD)
  b_clear=gtk.Button(stock=gtk.STOCK_CLEAR)
  e_to=gtk.Label('to: ')
  c_to=create_combo(map(lambda i:i[0],formats),2)

  b_convert=gtk.Button(stock=gtk.STOCK_CONVERT)
  b_stop=gtk.Button(stock=gtk.STOCK_STOP)
  b_about=gtk.Button(stock=gtk.STOCK_ABOUT)
  files = gtk.ListStore(str,str,float,int,str) # fn, basename, percent, pulse, label
  files_list=gtk.TreeView(files)
  
  vb=gtk.VBox(False,0); win.add(vb)
  vb.pack_start(l_banner_box,False, False, 0)
  hb=gtk.HBox(False,0); vb.pack_start(hb,False, False, 0)
  for i in (b_clear,b_add,e_to,c_to,b_convert,b_stop,b_about): hb.pack_start(i,False, False, 2)
  scroll=gtk.ScrolledWindow()
  scroll.set_policy(gtk.POLICY_NEVER,gtk.POLICY_ALWAYS)
  scroll.add(files_list)
  vb.pack_start(scroll,True, True, 0)
  build_options()
  
  b_add.connect('clicked', add_files_cb)
  b_clear.connect('clicked', lambda *args: files.clear())
  c_to.connect('changed', c_to_cb)
  b_convert.connect('clicked', convert_cb)
  b_stop.connect('clicked', stop_cb)
  b_about.connect("clicked", lambda *args: about_dlg.run())
  win.show_all()


  # setting the list
  cells.append(gtk.CellRendererText())
  cols.append(gtk.TreeViewColumn('Files', cells[-1], text=1))
  cols[-1].set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
  cols[-1].set_resizable(True)
  cols[-1].set_expand(True)
  cells.append(gtk.CellRendererProgress());
  cols.append(gtk.TreeViewColumn('%', cells[-1], value=2,pulse=3,text=4))
  cols[-1].set_expand(False)
  files_list.set_headers_visible(True)
  b_stop.set_sensitive(False)
  for i in cols: files_list.insert_column(i, -1)

  c_to.set_active(len(formats)-1)
  c_to.set_active(0)
  # sample list for testing
  #ls=[("/usr/share/file1.avi",10.0),("file2",20)]
  #files.clear()
  #for j,k in ls: files.append([j,basename(j),k,-1,None])
  #files[(1,)] = (files[1][0], files[1][1], 90,-1,"Done %d %%" % 90)

main()

