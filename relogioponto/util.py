# -*- coding: utf-8 -*-

import sys
import string     
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



def somente_numeros(texto):
    all = string.maketrans('','')
    nodigs = all.translate(all, string.digits)
    return texto.encode('utf-8').translate(all, nodigs)    


def converter_registro_em_texto(self, params=[], matricula=None, pis=None, datahora=None):        
    res = []
    for p in params:
        param_nome = p[0] 
        try:      
            param_valor = p[1]
        except:
            param_valor = None 
              
        valor = ''                 
        if param_nome == 'matricula':         
            valor = str(matricula).zfill(param_valor)                    
        elif param_nome == 'pis':
            pis = somente_numeros(pis)
            valor = str(pis).zfill(param_valor)                    
        elif param_nome == 'datahora':
            valor = datahora.strftime(param_valor)
        elif param_nome == 'personalizado':
            valor = param_valor
            
        res.append(valor)            

    return "".join(res) 
