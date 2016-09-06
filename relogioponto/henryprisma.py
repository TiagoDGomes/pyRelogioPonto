# -*- coding: utf-8 -*-
from relogioponto.base import RelogioPonto, Colaborador
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
    def colaboradores(self):
        return ColaboradorHenryLista(self) 
    
    def _send(self, data, msg_ok='Sucesso ao salvar'):
        browser = mechanize.Browser() 
        response = browser.open(self.URL, data=data)
        soup = BeautifulSoup(response.read())
        defaultResponse = soup.find("div", id='defaultResponse')
        resposta = defaultResponse.find("font", attrs={'class': 'fonte15'})
        if resposta.text != msg_ok:
            raise Exception(resposta.text)   
         
    def gravar_colaborador(self, colaborador):
        
        registration = ''
        chkVerDig = ''
        if colaborador.verificar_digital:
            chkVerDig = 'chkVerDig=on&'
        for matricula in colaborador.matriculas:
            registration = '{old}registration[]={new}&'.format(old=registration, new=matricula) 
        data = ('option=1&index=0&id=%3Fid%3F&wizard=0&pageIndex=0&x=22&y=24&lblName={nome}&lblPis={pis}&{chkVerDig}{registration}'
                .format(nome=colaborador.nome, pis=colaborador.pis, chkVerDig=chkVerDig, registration=registration))  

        self._send(data)
        colaborador.id = self.colaboradores.filter(pis=colaborador.pis)[0].id
        
    def apagar_colaborador(self, colaborador):
        data = ('option=3&index=0&id={id}&wizard=0&pageIndex=0&x=10&y=6&cbxOrderBy=0&lblFilterName=&lblFilterPis=&lblFilterRegistration='
                .format(id=colaborador.id))  

        self._send(data)

            
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

        
