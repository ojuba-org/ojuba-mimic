# -*- coding: UTF-8 -*-
# -*- Mode: Python; py-indent-offset: 4 -*-
"""
    Multi Media Converter that utilize gstreamer and/or ffmpeg
    Copyright © 2008-2015, Ojuba.org <core@ojuba.org>
    Released under terms of Waqf Public License
"""

import gettext, os, sys

exedir = os.path.dirname(sys.argv[0])
ld = os.path.join(exedir,'..','share','locale')
if not os.path.isdir(ld): 
    ld = os.path.join(exedir, 'locale')
gettext.install('ojuba-mimic', ld, unicode=0)


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
# "human readable type"
# .ext,                                                      0
# is_video,                                                  1
# cmd,                                                       2
# q_a, q_v, br_a, br_v, allow_audio_resample, default_ar     3-8
# audio quality float/int, default, from , to,               9-12
# video quality float/int, default, from , to,               13-16
# audio bitrate default , from, to,                          17-19
# video bitrate default , from, to,                          20-22
# [disabled flag that can be turned on],                     23
# validity python eval check,                                24
# fauler msg                                                 25
# 
# NOTE: type 'ffmpeg -formats' and 'ffmpeg -codecs' to get more info
formats = {
"OGG (Ogg/Theora video)":
    ('.ogv',
     True,
     "-f ogg -acodec libvorbis -ac 2 %(audio_quality)s -vcodec libtheora %(video_quality)s",
     1, 1, 0, 0, 1, 44100,
     float, 3, 0, 10,
     float, 10, 1, 100, 
     32000, 8000, 1000000,
     4450, 1000, 10000,
     [],
     'True',
     '',
     #
     ## default values
     # ab, as, vb, vs, vs
     ([0, 0, 0, 0, 0],   # Low quality
      [0, 0, 0, 0, 0],   # Normal quality
      [0, 0, 0, 0, 0])), # High quality
"3GP (3GP)":
    ('.3gp',
     True,
     "-f 3gp -acodec aac -strict experimental -ar 8000 -ac 1 -vcodec h263",
     0, 0, 1, 1, 0, 8000, 
     float, 3, 0, 10,
     float, 10, 1, 100, 
     8000, 1000, 10000,
     4450, 4750, 10000,
     [],
     'size in ("-s 128x96", "-s 176x144", "-s 352x288", "-s 704x576", "-s 1408x1152")', 
               #and audio_bitrate in (4700, 5200, 5950, 6700, 7450, 7950, 9200, 9950)',
     _('choose a valid size and     bitrate (try cif and 4750)'),
     # ab, as, vb, vs, vs
     (['8k', 0, 0, 'sqcif 128x96', 'sqcif 128x96'],   # Low quality
      ['16k', 0, 0, 'cif 352x288', 'cif 352x288'],   # Normal quality
      ['32k', 0, 0, '4cif 704x576', '4cif 704x576'])), # High quality
"FLV (Flash Video)":
    ('.flv',
     True,
     '-f flv -acodec libmp3lame -r 25 -vcodec flv',
     0, 1, 1, 0, 1, 22050, 
     float, 3, 0, 10,
     int, 10, 1, 100,
     32000, 8000, 100000,
     4450, 1000, 10000,
     [],
     'audio_samplerate in (44100, 22050, 11025)',
     _('audio samplerate should be 44100, 22050 or 11025'),
     # ab, as, vb, vs, vs
     ([0, 11025, 700, 0, 0],   # Low quality
      [0, 22050, 1450, 0, 0],   # Normal quality
      [0, 44100, 2450, 0, 0])), # High quality
"AVI (msmpeg4)":
    ('.avi',
     True,
     "-f avi -acodec libmp3lame -vcodec msmpeg4v2",
     0, 0, 1, 1, 1, 44100, 
     int, 0, 0, 0,
     int, 0, 0, 0, 
     32000, 8000, 1000000,
     4450, 1000, 10000,
     [],
     'True',
     '',
     # ab, as, vb, vs, vs
     ([0, 0, 0, 0, 0],   # Low quality
      [0, 0, 0, 0, 0],   # Normal quality
      [0, 0, 0, 0, 0])), # High quality
"WMV (msmpeg4)": 
    ('.wmv',
     True,
     "-f asf -acodec libmp3lame -vcodec msmpeg4",
     0, 0, 1, 1, 1, 44100, 
     int, 0, 0, 0,
     int, 0, 0, 0, 
    32000, 8000, 1000000,
    4450, 1000, 10000,
    [],
    'True',
    '',
    # ab, as, vb, vs, vs
     ([0, 0, 0, 0, 0],   # Low quality
      [0, 0, 0, 0, 0],   # Normal quality
      [0, 0, 0, 0, 0])), # High quality
"WMV (wmv1)": 
    ('.wmv',
     True,
     "-f asf -acodec wmav1 -vcodec wmv1",
     0, 0, 1, 1, 1, 44100, 
     int, 0, 0, 0,
     int, 0, 0, 0, 
     32000, 8000, 1000000,
     4450, 1000, 10000,
     [],
     'True',
     '',
     # ab, as, vb, vs, vs
     ([0, 0, 0, 0, 0],   # Low quality
      [0, 0, 0, 0, 0],   # Normal quality
      [0, 0, 0, 0, 0])), # High quality
"WMV (wmv2)": 
    ('.wmv',
     True,
     "-f asf -acodec wmav2 -vcodec wmv2",
     0, 0, 1, 1, 1, 44100, 
     int, 0, 0, 0,
     int, 0, 0, 0, 
     32000, 8000, 1000000,
     4450, 10000, 10000,
     [],
     'True',
     '',
     # ab, as, vb, vs, vs
     ([0, 0, 0, 0, 0],   # Low quality
      [0, 0, 0, 0, 0],   # Normal quality
      [0, 0, 0, 0, 0])), # High quality
"MPG (VCD)": 
    ('.mpg',
     True,
     "-f mpeg -target ntsc-vcd",
     0, 0, 0, 0, 0, 44100, 
     int, 0, 0, 0,
     int, 0, 0, 0, 
     32000, 8000, 1000000,
     4450, 1000, 10000,
     ['-flags qprd','-flags mv0','-flags skiprd','-g 100'],
     'True',
     '',
     # ab, as, vb, vs, vs
     ([0, 0, 0, 0, 0],   # Low quality
      [0, 0, 0, 0, 0],   # Normal quality
      [0, 0, 0, 0, 0])), # High quality
"MPG (DVD)": 
    ('.mpg',
     True,
     "-f mpeg -target ntsc-dvd",
     0, 0, 0, 0, 0, 44100, 
     int, 0, 0, 0,
     int, 0, 0, 0, 
     32000, 8000, 1000000,
     4450, 1000, 10000,
     ['-flags qprd','-flags mv0','-flags skiprd','-g 100'],
     'True',
     '',
     # ab, as, vb, vs, vs
     ([0, 0, 0, 0, 0],   # Low quality
      [0, 0, 0, 0, 0],   # Normal quality
      [0, 0, 0, 0, 0])), # High quality
"MPG (film)": 
    ('.mpg',
     True,
     "-f mpeg -target ntsc-svcd",
     0, 0, 0, 0, 0, 44100, 
     int, 0, 0, 0,
     int, 0, 0, 0, 
     32000, 8000, 1000000,
     4450, 1000, 10000,
     ['-flags qprd','-flags mv0','-flags skiprd','-g 100'],
     'True',
     '',
     # ab, as, vb, vs, vs
     ([0, 0, 0, 0, 0],   # Low quality
      [0, 0, 0, 0, 0],   # Normal quality
      [0, 0, 0, 0, 0])), # High quality
"MPG (mpeg1)": 
    ('.mpg',
     True,
     "-f mpeg -acodec libmp3lame -vcodec mpeg1video -mbd rd -cmp 2 -subcmp 2 -bf 2",
     0, 0, 1,
     1, 1, 44100, 
     int, 0, 0, 0,
     int, 0, 0, 0, 
     32000, 8000, 1000000,
     4450, 1000, 10000,
     ['-flags qprd','-flags mv0','-flags skiprd','-g 100'],
     'True',
     '',
     # ab, as, vb, vs, vs
     ([0, 0, 0, 0, 0],   # Low quality
      [0, 0, 0, 0, 0],   # Normal quality
      [0, 0, 0, 0, 0])), # High quality
"MPG (mpeg2)": 
    ('.mpg',
     True,
     "-f mpeg -acodec libmp3lame -vcodec mpeg2video -mbd rd -cmp 2 -subcmp 2 -bf 2",
     0, 0, 1,
     1, 1, 44100, 
     int, 0, 0, 0,
     int, 0, 0, 0, 
     32000, 8000, 1000000,
     4450, 1000, 10000,
     [],
     'True',
     '',
     # ab, as, vb, vs, vs
     ([0, 0, 0, 0, 0],   # Low quality
      [0, 0, 0, 0, 0],   # Normal quality
      [0, 0, 0, 0, 0])), # High quality
"MP4 (psp ~30fps)": 
    ('.mp4',
     True,
     "-f psp -acodec aac -strict experimental -vcodec mpeg4 -ar 24000 -r 30000/1001 -bf 2",
     0, 0, 1,
     1, 0, 24000, 
     int, 0, 0, 0,
     int, 0, 0, 0,    
     32000, 8000, 1000000,
     4450, 1000, 10000,
     [],
     'not size and width*height<=76800 and width%16==0 and height%16==0',
     _('Width and Hight must be multibles of 16 or too big resolution'),
     # ab, as, vb, vs, vs
     ([0, 0, 0, 0, 0],   # Low quality
      [0, 0, 0, 0, 0],   # Normal quality
      [0, 0, 0, 0, 0])), # High quality
"MP4 (psp ~15fps)": 
    ('.mp4',
     True,
     "-f psp -acodec aac -strict experimental -vcodec mpeg4 -ar 24000 -r 15000/1001 -bf 2",
     0, 0, 1,
     1, 0, 24000, 
     int, 0, 0, 0,
     int, 0, 0, 0, 
     32000, 8000, 1000000,
     4450, 1000, 10000,
     [],
     'not size or width*height<=76800 and width%16==0 and height%16==0',
     _('Width and Hight must be multibles of 16 or too big resolution'),
     # ab, as, vb, vs, vs
     ([0, 0, 0, 0, 0],   # Low quality
      [0, 0, 0, 0, 0],   # Normal quality
      [0, 0, 0, 0, 0])), # High quality
'MP4 (ipod)': 
    ('.mp4',
     True,
     '-f mp4 -acodec aac -strict experimental -vcodec mpeg4 -mbd 2 -flags +mv4 -ac 2 -cmp 2 -subcmp 2 -bf 2', 
     0, 0, 1,
     1, 1, 22050, 
     int, 0, 0, 0,
     int, 0, 0, 0, 
     32000, 8000, 1000000,
     4450, 1000, 10000,
     [],
     'not size or width<=320 and height<=240',
     _('too big resolution, resize it so that width<=320 and height<=240'),
     # ab, as, vb, vs, vs
     ([0, 0, 0, 0, 0],   # Low quality
      [0, 0, 0, 0, 0],   # Normal quality
      [0, 0, 0, 0, 0])), # High quality
'AVI (MPEG4 like DviX)': 
    ('.avi',
     True,
     '-f avi -mbd rd -flags +mv4+aic -cmp 2 -subcmp 2 -g 300 -acodec aac \
        -strict experimental -vcodec mpeg4 -vtag DIV5 -bf 2',
     0, 0, 1,
     1, 1, 44100, 
     int, 0, 0, 0,
     int, 0, 0, 0, 
     32000, 8000, 1000000,
     4450, 1000, 10000,
     [],
     'True',
     '',
     # ab, as, vb, vs, vs
     ([0, 0, 0, 0, 0],   # Low quality
      [0, 0, 0, 0, 0],   # Normal quality
      [0, 0, 0, 0, 0])), # High quality
'AVI (xvid)': 
    ('.avi',
     True, 
     '-f avi -mbd rd -flags +mv4+aic -cmp 2 -subcmp 2 -g 300 -acodec \
        libmp3lame -vcodec libxvid -vtag xvid -bf 2',
     0, 0, 1,
     1, 1, 44100, 
     int, 0, 0, 0,
     int, 0, 0, 0, 
     32000, 8000, 1000000,
     4450, 1000, 10000,
     [],
     'True',
     '',
     # ab, as, vb, vs, vs
     ([0, 0, 0, 0, 0],   # Low quality
      [0, 0, 0, 0, 0],   # Normal quality
      [0, 0, 0, 0, 0])), # High quality
'MPG (mpeg4)': 
    ('.mpg',
     True,
     '-f mpeg -mbd rd -flags +mv4+aic -cmp 2 -subcmp 2 -g 300 -acodec aac \
        -strict experimental -vcodec mpeg4 -vtag DIV5 -bf 2',
     0, 0, 1,
     1, 1, 44100, 
     int, 0, 0, 0,
     int, 0, 0, 0, 
     32000, 8000, 1000000,
     4450, 1000, 10000,
     [],
     'True',
     '',
     # ab, as, vb, vs, vs
     ([0, 0, 0, 0, 0],   # Low quality
      [0, 0, 0, 0, 0],   # Normal quality
      [0, 0, 0, 0, 0])), # High quality
'MPG (xvid mpeg4)': 
    ('.mpg',
     True,
     '-f mpeg -mbd rd -flags +mv4+aic -cmp 2 -subcmp 2 -g 300 -acodec aac \
        -strict experimental -vcodec libxvid -vtag xvid -bf 2',
     0, 0, 1,
     1, 1, 44100, 
     int, 0, 0, 0,
     int, 0, 0, 0, 
     32000, 8000, 1000000,
     4450, 1000, 10000,
     [],
     'True',
     '',
     # ab, as, vb, vs, vs
     ([0, 0, 0, 0, 0],   # Low quality
      [0, 0, 0, 0, 0],   # Normal quality
      [0, 0, 0, 0, 0])), # High quality
'WMA (wma1)': 
    ('.wma',
     False,
     '-f asf -vn -acodec wmav1',
     0, 0, 1,
     0, 1, 44100, 
     int, 0, 0, 0,
     int, 0, 0, 0, 
     32000, 8000, 1000000,
     0, 0, 0,
     [],
     'True',
     '',
     # ab, as, vb, vs, vs
     ([0, 0, 0, 0, 0],   # Low quality
      [0, 0, 0, 0, 0],   # Normal quality
      [0, 0, 0, 0, 0])), # High quality
'WMA (wma2)': 
    ('.wma',
     False,
     '-f asf -vn -acodec wmav2',
     0, 0, 1, 0, 1, 44100, 
     int, 0, 0, 0,
     int, 0, 0, 0, 
     32000, 8000, 1000000,
     0, 0, 0,
     [],
     'True',
     '',
     # ab, as, vb, vs, vs
     ([0, 0, 0, 0, 0],   # Low quality
      [0, 0, 0, 0, 0],   # Normal quality
      [0, 0, 0, 0, 0])), # High quality
'MP3 (MP3)': 
    ('.mp3',
     False,
     '-f mp3 -vn -acodec libmp3lame',
     0, 0, 1, 1, 1, 44100, 
     int, 0, 0, 0,
     int, 0, 0, 0, 
     32000, 8000, 1000000,
     0, 0, 0,
     [],
     'True',
     '',
     # ab, as, vb, vs, vs
     ([0, 0, 0, 0, 0],   # Low quality
      [0, 0, 0, 0, 0],   # Normal quality
      [0, 0, 0, 0, 0])), # High quality
'WAV (adpcm_ms)': 
    ('.wav',
     False,
     '-f wav -vn -acodec adpcm_ms',
     0, 0, 0, 0, 1, 11025, 
     int, 0, 0, 0,
     int, 0, 0, 0, 
     32000, 8000, 1000000,
     0, 0, 0,
     [],'True',
     '',
     # ab, as, vb, vs, vs
     (['128k', 0, 0, 0, 0],   # Low quality
      ['256k', 0, 0, 0, 0],   # Normal quality
      ['512k', 0, 0, 0, 0])), # High quality
'OGG (Ogg/Vorbis audio)': 
    ('.oga',
     False,
     '-vn -f ogg -acodec libvorbis -ac 2 %(audio_quality)s',
     1, 0, 0, 0, 1, 44100, 
     float, 3, 0, 10,
     int, 0, 0, 0, 
     64000, 8000, 1000000,
     0, 0, 0,
     [],
     'True',
     '',
     # ab, as, vb, vs, vs
     (['16k', 0, 0, 0, 0],   # Low quality
      ['64k', 0, 0, 0, 0],   # Normal quality
      ['128k', 0, 0, 0, 0])), # High quality
}

