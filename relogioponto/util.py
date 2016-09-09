# -*- coding: utf-8 -*-

import sys     
from unicodedata import normalize    

PY2 = ( sys.version_info < (3,0) )

def remover_acentos(str_texto, codificacao_py2='utf-8'):
    if PY2:
        return normalize('NFKD', unicode(str_texto).encode('utf-8').decode(codificacao_py2)).encode('ASCII','ignore')
    else:
        return normalize('NFKD', str_texto).encode('ASCII','ignore').decode('ASCII')


def bin2hextxt(data):
    return " ".join("{:02x}".format(ord(c)) for c in data)
    
def hextxt2bin(text):
    text = text.replace(" ","")
    return text.decode('hex')       