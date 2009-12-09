#!/usr/bin/env python
# encoding: utf-8
"""
transform.py

Created by Manabu Terada on 2009-12-02.
Copyright (c) 2009 CMScom. All rights reserved.
"""
import os
import time
import subprocess, select
from cStringIO import StringIO
import mimetypes
from Products.PortalTransforms.interfaces import itransform
from config import SITE_CHARSET, TRANSFORM_NAME
from c2.transform.msoffice import logger

path = os.path.join(os.path.dirname(__file__))

def msdoc2txt(data, timeout=60): #default 60 sec
    assert isinstance(data, str)
    p = subprocess.Popen(("java", '-cp', '/home/terada/poi-3.5-FINAL/ooxml-lib/*:/home/terada/poi-3.5-FINAL/lib/*:/home/terada/poi-3.5-FINAL/*:'+ path, 'msdoc2txt'),
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         stdin=subprocess.PIPE)
    p.stdin.write(data)
    p.stdin.close()
    outs = select.select([p.stdout],(),(),timeout)[0]
    errs = select.select([p.stderr],(),(),0)[0]
    if errs:
        err = errs[0]
        return False, err.read() # 失敗したら(False, エラーメッセージ)
    elif outs:
        out = outs[0]
        return True, out.read() # 成功したら(True, 抽出文字列)
    else:
        return None, "timeout" # タイムアウトしたら(None, "timeout")

class msoffice_to_text:
    __implements__ = itransform
    __name__ = TRANSFORM_NAME

    inputs = (
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
#         # Wordprocessing formats
#         ct.CT_WORDPROC_DOCX_PUBLIC,
#         ct.CT_WORDPROC_DOCM_PUBLIC,
#         ct.CT_WORDPROC_DOTX_PUBLIC,
#         ct.CT_WORDPROC_DOTM_PUBLIC,
# 
#         # Spreadsheet formats
#         ct.CT_SPREADSHEET_XLSX_PUBLIC,
#         ct.CT_SPREADSHEET_XLSM_PUBLIC,
#         ct.CT_SPREADSHEET_XLTX_PUBLIC,
#         ct.CT_SPREADSHEET_XLTM_PUBLIC,
#         # FIXME: note sure we can honour below types...
# #        '*.xlam': ct.CT_SPREADSHEET_XLAM_PUBLIC,
# #        '*.xlsb': ct.CT_SPREADSHEET_XLSB_PUBLIC
# 
#         # Presentation formats
#         ct.CT_PRESENTATION_PPTX_PUBLIC,
#         ct.CT_PRESENTATION_PPTM_PUBLIC,
#         ct.CT_PRESENTATION_POTX_PUBLIC,
#         ct.CT_PRESENTATION_POTM_PUBLIC,
#         ct.CT_PRESENTATION_PPSX_PUBLIC,
#         ct.CT_PRESENTATION_PPSM_PUBLIC,
#         # FIXME: Not sure we can honour below types
# #        '*.ppam': ct.CT_PRESENTATION_PPAM_PUBLIC
        )

    output = 'text/plain'

    output_encoding = SITE_CHARSET

    def __init__(self,name=None):
        if name:
            self.__name__=name
        return

    def name(self):
        return self.__name__

    def convert(self, orig, data, **kwargs):

        #orig_file = kwargs.get('filename') or 'unknown.xxx'
        mimetype = kwargs.get('mimetype')
        filename = kwargs.get('filename') or 'unknown.xxx'
        if mimetype is None:
            mimetype = mimetypes.guess_type(filename)[0]
        print "MS Office test"
        try:
            status, text = msdoc2txt(orig)
        except Exception, e:
            logger.error(e, exc_info=True)
        print 'text output', status, text
        if status:
            data.setData(text)
        else:
            logger.error(text, exc_info=True)
            data.setData('')
        return data

def register():
    return msoffice_to_text()
