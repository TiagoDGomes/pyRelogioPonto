# -*- coding: utf-8 -*-
import socket
from threading import Thread
import time
from relogioponto.util import remover_acentos

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
    
    def __str__(self, *args, **kwargs):
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
        
    def __init__(self, endereco, porta=3000):
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
        except:
            pass
        self.tcp_socket = None
    
    @property    
    def colaboradores(self):
        raise NotImplementedError('Implementacao ausente na classe filha de RelogioPonto (colaboradores)')
    
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


class RelogioPontoException(Exception):
    pass 