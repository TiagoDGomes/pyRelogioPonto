# -*- coding: utf-8 -*-
import socket
from threading import Thread
import time
from .util import remover_acentos
from datetime import datetime
from pprint import pprint


 

def get_rep_suportados():
    from . import henryprisma, henryorion5
    return [
             (1, 'Henry - Prisma', henryprisma.HenryPrisma, [
                                                             ('endereco', str),
                                                             ('porta', int),
                                                             ('login', str),
                                                             ('password', str),                                                                                                                          
                                                            ]),
            (2, 'Henry - Orion V (usando database do programa host)', henryorion5.Orion5ODBCMode, [
                                                             ('conn_str', str),                                                                                                                         
                                                            ]),
            
           ]

def get_class_por_tipo(tipo):
    for rep in get_rep_suportados():
        if tipo == rep[0]:
            return rep[2]
    return None

class Colaborador(object):
    
    def __init__(self, relogio):
        self.relogio = relogio
        self.matriculas = []
        self._nome = None
        self.pis = None
        self.verificar_digital = None
        self.id = None
        
    def save(self):
        self.relogio.gravar_colaborador(self)
        
    @property
    def nome(self):
        return self._nome
    
    @nome.setter
    def nome(self, value):
        self._nome = remover_acentos(value)
        
    def delete(self):
        self.relogio.apagar_colaborador(self)
    
    def __repr__(self, *args, **kwargs):
        return str( {'id': self.id, 'nome': self.nome, 'pis': self.pis, 'matriculas': self.matriculas} )

    @property
    def biometrias(self):
        return self.relogio.get_biometrias(self)
    
class Empregador(object):
    def __init__(self):
        self._razao_social = None
        self._local = None
        self.tipo_documento = None
        self.documento = None
        self.cei = None
        
    def __str__(self, *args, **kwargs):
        return str( {'razao_social': self.razao_social, 
                     'local': self.local, 
                     'tipo_documento': self.tipo_documento,
                     'documento': self.documento,
                     'cei': self.cei,                     
                     } )

    @property
    def razao_social(self):
        return self._razao_social
    
    @razao_social.setter
    def razao_social(self, value):
        self._razao_social = remover_acentos(value)
            
    @property
    def local(self):
        return self._local
    
    @local.setter
    def local(self, value):
        self._local = remover_acentos(value) 
           
    
class RelogioPonto(object):
    
    def __init__(self, endereco, porta=3000, *args, **kwargs):
        self.tcp_socket = None
        self.endereco = endereco
        self.porta = porta
        self.conectado = None
        self.callback_func = []
         
    
    def conectar(self):
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)            
        self.conectado = None
        rpself = self
        def run_thread():
            dest = (self.endereco, self.porta) 
            try:
                result = self.tcp_socket.connect_ex(dest) 
            except:
                result = None
            self.status_conexao = result             
            if result:
                self.conectado = False                                        
            else:              
                self.conectado = True
            while self.conectado:
                try:                    
                    data = rpself.tcp_socket.recv(64000)
                    rpself.receber_comando(data)                
                except:
                    self.conectado = False                    
                    break
                finally:
                    self.desconectar() 
        self.thread_conexao = Thread(target=run_thread)
        self.thread_conexao.start()
              
        while self.conectado is None:             
            time.sleep(0.2)

            
        if not self.conectado:
            raise Exception("Falha na conexao. Codigo de erro %s." % (self.status_conexao))   
        

    
    def __exit__(self, *err):
        self.desconectar()
    
    def __del__(self):
        self.desconectar()
    
    def apagar_colaborador(self, colaborador):
        raise NotImplementedError('Implementacao ausente')
        
    def desconectar(self):
        try:
            self.tcp_socket.shutdown(1)
            self.tcp_socket.close()
            self.conectado = False
        except:
            pass
        self.tcp_socket = None
    
    @property    
    def colaboradores(self):
        raise NotImplementedError('Implementacao ausente na classe filha de RelogioPonto (colaboradores)')
    
    @property    
    def quantidade_eventos_registrados(self):
        raise NotImplementedError('Implementacao ausente na classe filha de RelogioPonto (quantidade_eventos)')
    
    def get_afd(self, nsr=None, data_hora=None):
        raise NotImplementedError('Implementacao ausente na classe filha de RelogioPonto (get_afd)')
    
    def gravar_colaborador(self, colaborador):
        raise NotImplementedError('Implementacao ausente na classe filha de RelogioPonto (gravar_colaborador)')
    
    def get_biometrias(self, colaborador=None):
        raise NotImplementedError('Implementacao ausente na classe filha de RelogioPonto (get_biometrias)')
    
    def enviar_comando(self, data):
        self.tcp_socket.send(data)
        time.sleep(0.5)
    
    def receber_comando(self, data):
        for cmd in self.callback_func:
            cmd(data)
        
    def add_listener(self, callback_func):
        self.callback_func.append(callback_func)   
        
    @property
    def data_hora(self):
        raise NotImplementedError('Implementacao ausente na classe filha de RelogioPonto (data_hora)')
    
    @data_hora.setter
    def data_hora(self, value):
        raise NotImplementedError('Implementacao ausente na classe filha de RelogioPonto (data_hora)')
    
    def get_empregador(self):
        raise NotImplementedError('Implementacao ausente na classe filha de RelogioPonto (get_empregador)')
    
    def set_empregador(self, empregador):
        raise NotImplementedError('Implementacao ausente na classe filha de RelogioPonto (get_empregador)')

    def get_registros(self, nsr=None, data_hora=None):
        afd = self.get_afd(nsr, data_hora)

        registros = []
        for linha in afd.split('\r\n'):   
                   
            if len(linha) > 0:
                registro = {}                
                registro['nsr'] = int(linha[0:9])
                if registro['nsr'] == 999999999:
                    registro['quantidade_tipo_2'] = int(linha[9:18])
                    registro['quantidade_tipo_3'] = int(linha[18:27])
                    registro['quantidade_tipo_4'] = int(linha[27:36])
                    registro['quantidade_tipo_5'] = int(linha[36:45])
                    registro['tipo'] = int(linha[45])  
                else:
                    tipo = int(linha[9:10])
                    registro['tipo'] = tipo
                    if tipo == 1: # Registro tipo "1" - Cabeçalho                     
                        registro['tipo_identificador_empregador'] = int(linha[10:11])
                        registro['documento'] = (linha[11:25])
                        registro['cei'] = int(linha[25:37])
                        registro['razao_social'] = linha[37:187].strip()
                        registro['numero_rep'] = int(linha[187:204])
                        registro['data_inicial'] = datetime.strptime(linha[204:212],"%d%m%Y")
                        registro['data_final'] = datetime.strptime(linha[212:220],"%d%m%Y")
                        registro['data_geracao'] = datetime.strptime(linha[220:232],"%d%m%Y%H%M")
                        
                    
                    elif tipo == 2: # Registro de inclusão ou alteração da identificação da empresa no REP
                        registro['data_gravacao'] = datetime.strptime(linha[10:22],"%d%m%Y%H%M")
                        registro['identificador_empregador'] = int(linha[22])
                        registro['documento'] = (linha[23:37]) or None                      
                        registro['cei'] = int(linha[37:49]) or None 
                        registro['razao_social'] = linha[49:199].strip()
                        registro['local'] = linha[199:299].strip()
                        
                    elif tipo == 3: #Registro de marcação de ponto 
                        registro['data_marcacao'] = datetime.strptime(linha[10:22],"%d%m%Y%H%M")
                        colaborador = self.colaboradores.filter(pis=int(linha[22:34]))
                        if colaborador:                        
                            registro['colaborador'] = colaborador[0]
                        else:
                            colaborador = Colaborador(self)
                            colaborador.pis = linha[22:34] 
                            registro['colaborador'] = colaborador
                                       
                        
                    
                registros.append(registro)
        return (registros)     

    
class RelogioPontoException(Exception):
    pass


