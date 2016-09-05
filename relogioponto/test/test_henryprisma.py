# -*- coding: utf-8 -*-
from relogioponto.henryprisma import HenryPrisma
from _warnings import warn
import unittest
from relogioponto.base import UsuarioPonto


RELOGIO_PRISMA_ENDERECO = '10.3.0.10'
RELOGIO_PRISMA_TOTAL_USUARIOS = 4

class TestUsuarioPontoHenry(unittest.TestCase):
    
    def setUp(self):
        self.endereco = RELOGIO_PRISMA_ENDERECO
        self.relogio = HenryPrisma(self.endereco)
        self.relogio.conectar() 
        self.usuario = UsuarioPonto(self.relogio)
        
    def tearDown(self):
        self.relogio.desconectar()
        del self.relogio   
         
    def test_usuario(self):        
        self.assertEqual(self.usuario.relogio, self.relogio)
    
    def test_salvar(self):
        self.usuario.salvar()


class TestHenryPrisma(unittest.TestCase):    
    def setUp(self):
        self.endereco = RELOGIO_PRISMA_ENDERECO
        self.totalusuarios = RELOGIO_PRISMA_TOTAL_USUARIOS
        self.relogio = HenryPrisma(self.endereco)
        self.relogio.conectar() 
           
    def tearDown(self):
        self.relogio.desconectar()
        
    def test_conexao(self):
        self.assertTrue(self.relogio.conectado, u'Não conectado. Verifique o endereco se está correto ou se o dispositivo está conectado.')

    def test_conectar_via_http(self):
        self.relogio.conectar_via_http()
        self.assertTrue(self.relogio.conectado_via_http)
        
    def test_listarusuarios(self):
        lista = self.relogio.usuarios.all()
        self.assertEqual(self.totalusuarios, len(lista))
    
    def test_listarusuariosfilter(self):
        lista = self.relogio.usuarios.filter(matricula='1002')
        self.assertEqual(1, len(lista))
    
        
    def test_gravarusuario(self):
        usuario = UsuarioPonto(self.relogio)
        usuario.nome = "TESTE 3"
        usuario.pis = "5555.55555.55/5" 
        usuario.matriculas = ['112233','445566']
        usuario.salvar()
        lista = self.relogio.usuarios.filter(matricula='112233')
        usuario_salvo = lista[0]
        self.assertEqual(usuario_salvo.pis, usuario.pis)
        
        
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()