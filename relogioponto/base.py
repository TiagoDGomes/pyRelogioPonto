# -*- coding: utf-8 -*-
import socket
from threading import Thread
import time
import json

class UsuarioPonto(object):
    
    def __init__(self, relogio):
        self.relogio = relogio
        self.matriculas = []
        
    def salvar(self):
        self.relogio.gravar_usuario(self)
    
    def __str__(self, *args, **kwargs):
        return json.dumps( {'nome': self.nome, 'pis': self.pis, 'matriculas': self.matriculas} )


    
    
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
    
    
        
    def desconectar(self):
        try:
            self.tcp_socket.shutdown(1)
            self.tcp_socket.close()
        except:
            pass
        self.tcp_socket = None
    
    @property    
    def usuarios(self):
        raise NotImplementedError('Implementacao ausente')
    
    def gravar_usuario(self, usuario):
        raise NotImplementedError('Implementacao ausente')
    
    def enviar_comando(self, data):
        self.tcp_socket.send(data)
        time.sleep(0.5)
    
    def receber_comando(self, data):
        for cmd in self.callback_func:
            cmd(data)
        
    def add_listener(self, callback_func):
        self.callback_func.append(callback_func)   
        
