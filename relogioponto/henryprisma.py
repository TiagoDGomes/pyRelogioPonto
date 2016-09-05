# -*- coding: utf-8 -*-
from relogioponto.base import RelogioPonto, UsuarioPonto
import urllib2
import urllib
import mechanize
from BeautifulSoup import BeautifulSoup


   
    
    
class HenryPrisma(RelogioPonto):
    
    def __init__(self, *args, **kwargs):        
        super(HenryPrisma, self).__init__(*args, **kwargs)
        self.conectado_via_http = None
        self.URL = 'http://{endereco}/prisma.cgi'.format(endereco=self.endereco)
        
    def conectar_via_http(self):
        if not self.conectado_via_http:
            values = {'login': 'prisma', 'password': '123456', 'option': '10', 'x': '0', 'y': '0'}
            data = urllib.urlencode(values)
            req = urllib2.Request(self.URL, data)
            response = urllib2.urlopen(req)
            the_page = response.read()
            senha_incorreta = the_page.find('Dados de login s&atilde;o inv&aacute;lidos') > 0
            if senha_incorreta:
                raise Exception('Senha incorreta')
            self.conectado_via_http = True
        
        
    @property    
    def usuarios(self):
        return UsuarioPontoHenryLista(self) 
        
    def gravar_usuario(self, usuario):
        values = {'option=1&index=0&id=%3Fid%3F&wizard=0&pageIndex=0&lblFilterName=&lblFilterPis=&lblFilterRegistration=13563&lblName=TESte+2&lblPis=6666.66666.66%2F6&chkVerDig=on&registration%5B%5D=5678&registration%5B%5D=1234&x=22&y=24'}



class UsuarioPontoHenryLista(object):
    
    def __init__(self, relogio):
        self.relogio = relogio
        self._list_usuarios = None
    
    def all(self):
        return self.filter()
    
    def filter(self, nome=None, pis=None, matricula=None):
        self.relogio.conectar_via_http()
        browser = mechanize.Browser() 
        contiver_paginas = True
        pagina = 0
        lista_usuarios = []
        values = {
                      'optionMenu': '4', 
                      'indexMenu': str(pagina), 
                      'index': '0',
                      'id': '-1',
                      'pageIndexMenu': str(pagina),
                      'idMenu': '0',                       
                      'x': '0',
                      'y': '0'
        }
        
        if matricula:
            values['lblFilterRegistration'] = matricula
        
        if pis:
            values['lblFilterPis'] = pis
            
        if nome:
            values['lblFilterName'] = nome
        
        while contiver_paginas:   
            values['indexMenu'] = str(pagina)
            values['pageIndexMenu'] = str(pagina) 
            #print values
            data = urllib.urlencode(values)                   
            response = browser.open(self.relogio.URL, data=data)
            html = response.read()
            soup = BeautifulSoup(html)
            #print ('new',html)
            table = soup.find("table", id='displayTable')
            #print table.prettify()
            for row in table.findAll('tr')[1:]:
                cols = row.findAll('td')
                usuario = UsuarioPonto(self.relogio)
                matriculas = []
                if cols[0].find('a'):                    
                    usuario.nome = cols[0].find('a').text
                    usuario.pis = cols[1].string   
                    usuario.verificar_digital = cols[2].string                 
                    matriculas = cols[3].findAll(text=True)
                    for matricula in matriculas:
                        matricula_text = str( matricula.string).strip()
                        if matricula_text:
                            usuario.matriculas.append(matricula_text)
                        else:
                            break 
                    lista_usuarios.append(usuario)
                else:
                    contiver_paginas = False
            pagina = pagina + 1 
        return lista_usuarios
    
    