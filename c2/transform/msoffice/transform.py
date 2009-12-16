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

scpath = os.path.join(os.path.dirname(__file__), 'msdoc2txt.jar')

def msdoc2txt(data, timeout=60): #default 60 sec
    assert isinstance(data, str)
    p = subprocess.Popen(("java", '-jar', scpath),
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
        # MS-Word formats
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.ms-word.document.macroEnabled.12',
        # MS-Excle formats
        'application/vnd.ms-excel',
        'application/msexcel',
        'application/x-msexcel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.ms-excel.sheet.binary.macroEnabled.12',
        'application/vnd.ms-excel.sheet.macroEnabled.12',
        # MS-PowerPoint formats
        'application/powerpoint',
        'application/mspowerpoint',
        'application/x-mspowerpoint',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'application/vnd.ms-powerpoint.presentation.macroEnabled.12',
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
        try:
            status, text = msdoc2txt(orig)
        except Exception, e:
            logger.error(e, exc_info=True)
        if status:
            data.setData(text)
        else:
            logger.error(text, exc_info=True)
            data.setData('')
        return data

def register():
    return msoffice_to_text()
