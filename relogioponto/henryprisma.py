# -*- coding: utf-8 -*-
from relogioponto.base import RelogioPonto, Colaborador, Empregador,\
    RelogioPontoException
import urllib2
import urllib
import mechanize
from BeautifulSoup import BeautifulSoup
from datetime import datetime
  
def bin2hextxt(data):
    return " ".join("{:02x}".format(ord(c)) for c in data)
    
def hextxt2bin(text):
    text = text.replace(" ","")
    return text.decode('hex')   
    
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
    def colaboradores(self):
        return ColaboradorHenryLista(self) 
    
    def _send(self, post_raw):
        browser = mechanize.Browser() 
        response = browser.open(self.URL, data=post_raw)
        return (response.read())         
    
    def _sendpost(self, post_raw, msg_ok='Sucesso ao salvar'):
        try:
            # Python 2.6-2.7 
            from HTMLParser import HTMLParser
        except ImportError:
            # Python 3
            from html.parser import HTMLParser
        h = HTMLParser()
        html_text = self._send(post_raw)
        soup = BeautifulSoup(html_text)
        defaultResponse = soup.find("div", id='defaultResponse')
        resposta = defaultResponse.find("font", attrs={'class': 'fonte15'})
        if resposta.text != msg_ok:
            raise RelogioPontoException(h.unescape(resposta.text))
         
    def gravar_colaborador(self, colaborador):
        
        registration = ''
        chkVerDig = ''
        if colaborador.verificar_digital:
            chkVerDig = 'chkVerDig=on&'
        for matricula in colaborador.matriculas:
            registration = '{old}registration[]={new}&'.format(old=registration, new=matricula) 
        data = ('option=1&index=0&id=%3Fid%3F&wizard=0&pageIndex=0&x=22&y=24&lblName={nome}&lblPis={pis}&{chkVerDig}{registration}'
                .format(nome=colaborador.nome, pis=colaborador.pis, chkVerDig=chkVerDig, registration=registration))  

        self._sendpost(data)
        colaborador.id = self.colaboradores.filter(pis=colaborador.pis)[0].id
        
    def apagar_colaborador(self, colaborador):
        data = ('option=3&index=0&id={id}&wizard=0&pageIndex=0&x=10&y=6&cbxOrderBy=0&lblFilterName=&lblFilterPis=&lblFilterRegistration='
                .format(id=colaborador.id))  

        self._sendpost(data)
        
    def get_biometrias(self, colaborador=None):
        data = ('option=16&index=7&id=5&wizard=0&visibleDiv=biometricEnable&visibleDivFooter=default&x=32&y=39')
        biometrias = []
        raw_data = self._send(data)[2:]
        len_binary = 411
        for digital_raw in raw_data.split('\r\n\x33\x2b'):
            if len(digital_raw) > 0:
                matricula = int(digital_raw[2:22])   
                if colaborador is None or matricula in colaborador.matriculas:
                    digital_raw_slice = digital_raw[2:].split('}')
                    posA = digital_raw_slice[2].find('{')
                                 
                    id1 = int(digital_raw_slice[1])
                    id2 = int(digital_raw_slice[2][:posA])
                        
                    biometrias.append(
                                    (
                                     id1, 
                                     id2, 
                                     digital_raw[:len_binary],
                                     )
                                    )
                
    
        return biometrias
             
    @property
    def data_hora(self):
        raw = 'optionMenu=4&indexMenu=3&idMenu=&pageIndexMenu='
        html = self._send(raw)
        soup = BeautifulSoup(html)
        resposta = [value for key, value in soup.find("input", id='edtDateTime').attrs if key == 'value'][0]
        return datetime.strptime(resposta, '%d/%m/%Y %I:%M:%S')

    
    @data_hora.setter
    def data_hora(self, date_value):
        date_formatted = date_value.strftime('%d%%2F%m%%2F%Y+%I%%3A%M%%3A%S')
        raw = 'option=1&index=3&id=-1&wizard=0&edtDateTime={date_formatted}&x=40&y=18'.format(date_formatted=date_formatted)
        self._sendpost(raw)
        
        
    def get_empregador(self):
        empregador = Empregador()
        raw = 'option=2&index=1&id=1&wizard=0&x=42&y=37'
        html = self._send(raw)
        soup = BeautifulSoup(html)
        empregador.razao_social = [value for key, value in soup.find("input", id='lblName').attrs if key == 'value'][0]
        empregador.local = [value for key, value in soup.find("input", id='lblLocal').attrs if key == 'value'][0]
        empregador.documento = [value for key, value in soup.find("input", id='lblDocument').attrs if key == 'value'][0]
        empregador.cei = [value for key, value in soup.find("input", id='lblCei').attrs if key == 'value'][0]        
        empregador.tipo_documento = int( [value for key, value in soup.find("select", id='cbxDocType').find('option', selected="selected").attrs if key == 'value'][0] )
        return empregador
    
    def set_empregador(self, empregador):
        values = {'option': '1',
                  'index': '1',
                  'id' : '1',
                  'wizard': '0',
                  'lblName' : unicode(empregador.razao_social).encode('utf-8'),
                  'lblLocal': unicode(empregador.local).encode('utf-8'),
                  'cbxDocType': unicode(empregador.tipo_documento).encode('utf-8'),
                  'lblDocument': unicode(empregador.documento).encode('utf-8'),
                  'lblCei': unicode(empregador.cei).encode('utf-8'),
                  'x': '22',
                  'y': '32',
                  }    
        post_raw = urllib.urlencode(values)                   
        self._sendpost(post_raw)
            
    
                
class ColaboradorHenryLista(object):
    
    def __init__(self, relogio):
        self.relogio = relogio
        self._list_colaboradores = None        
    
    def all(self):
        return self.filter()
    
    def filter(self, nome=None, pis=None, matricula=None):
        self.relogio.conectar_via_http()
        browser = mechanize.Browser() 
        contiver_paginas = True
        pagina = 0
        lista_colaboradores = []
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
            data = urllib.urlencode(values)                   
            response = browser.open(self.relogio.URL, data=data)
            html = response.read()
            soup = BeautifulSoup(html)
            table = soup.find("table", id='displayTable')            
            for row in table.findAll('tr')[1:]:
                cols = row.findAll('td')
                colaborador = Colaborador(self.relogio)
                matriculas = []
                if not cols[0].find('a'):
                    contiver_paginas = False
                else:                    
                    colaborador.nome = cols[0].find('a').text
                    colaborador.pis = cols[1].string   
                    colaborador.verificar_digital = cols[2].string == 'Sim' 
                    attrs = cols[4].find('input', value='Atualizar').attrs  
                    for key, value in attrs:
                        if key == 'onclick':
                            start = value.find("'") + 1
                            end = value.find("'", start)
                            start = value.find("'", end + 1) + 1
                            end = value.find("'", start + 1)
                            colaborador.id = int(value[start:end])
                            break
                                   
                    matriculas = cols[3].findAll(text=True)
                    for matricula in matriculas:
                        try:
                            matricula_text = int(str(matricula.string).strip())
                        except:
                            matricula_text = None
                        if matricula_text:
                            colaborador.matriculas.append(matricula_text)
                        else:
                            break 
                    lista_colaboradores.append(colaborador)

                    
            pagina = pagina + 1 
        return lista_colaboradores
    
    