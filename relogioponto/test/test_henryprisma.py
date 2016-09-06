# -*- coding: utf-8 -*-
from relogioponto.henryprisma import HenryPrisma
from _warnings import warn
import unittest
from relogioponto.base import Colaborador
from datetime import datetime
import time


RELOGIO_PRISMA_ENDERECO = '10.3.0.10'
TESTAR_INSERCAO_EXCLUSAO = False
COLABORADOR_MATRICULA = 13563

class TestColaboradorHenry(unittest.TestCase):
    
    def setUp(self):
        self.endereco = RELOGIO_PRISMA_ENDERECO
        self.relogio = HenryPrisma(self.endereco)
        self.relogio.conectar() 
        self.colaborador = self.relogio.colaboradores.filter(matricula=COLABORADOR_MATRICULA)[0]
        
    def tearDown(self):
        self.relogio.desconectar()
        del self.relogio   
         
    def test_colaborador(self):        
        self.assertEqual(self.colaborador.relogio, self.relogio)
    
    def test_digitais(self):
        digitais = self.colaborador.digitais
        self.assertTrue(len(digitais) >= 0)


class TestHenryPrisma(unittest.TestCase): 
       
    def setUp(self):
        self.endereco = RELOGIO_PRISMA_ENDERECO
        self.relogio = HenryPrisma(self.endereco)
        self.relogio.conectar() 
           
    def tearDown(self):
        self.relogio.desconectar()
        
    def test_conexao(self):
        self.assertTrue(self.relogio.conectado, u'Não conectado. Verifique o endereco se está correto ou se o dispositivo está conectado.')

    def test_conectar_via_http(self):
        self.relogio.conectar_via_http()
        self.assertTrue(self.relogio.conectado_via_http)
    
    def t_apagarcolaborador(self): 
        colaborador = self.relogio.colaboradores.filter(matricula=112233)[0]
        colaborador.delete()
        self.assertTrue(len(self.relogio.colaboradores.filter(matricula=112233)) == 0)  
          
    def test_colaboradores(self):
        global TESTAR_INSERCAO_EXCLUSAO
        if not TESTAR_INSERCAO_EXCLUSAO:
            warn('Testes de insercao e exclusao ignorados.')
        else:
            if len(self.relogio.colaboradores.filter(matricula=112233)) > 0:
                self.t_apagarcolaborador()
               
            colaborador = Colaborador(self.relogio)
            colaborador.nome = "TESTCASE"
            colaborador.pis = "5555.55555.55/5" 
            colaborador.matriculas = [112233,445566]
            colaborador.verificar_digital = True
            colaborador.save()
            self.assertTrue(colaborador.id != None)
    
            lista = self.relogio.colaboradores.filter(matricula=112233)
            self.assertTrue(len(lista)==1)                
    
            colaborador_salvo = lista[0]
            self.assertTrue(colaborador_salvo.id != None)
    
            self.assertEqual(colaborador_salvo.nome, colaborador.nome)
            self.assertEqual(colaborador_salvo.pis, colaborador.pis)
            self.assertEqual(colaborador_salvo.matriculas, colaborador.matriculas)
            self.assertEqual(colaborador_salvo.verificar_digital, colaborador.verificar_digital)
    
            
            lista = self.relogio.colaboradores.all()
            self.assertTrue(len(lista) >= 1)
            self.t_apagarcolaborador()
    
    def test_hora(self):
        data_relogio = self.relogio.data_hora
        self.assertTrue(type(data_relogio)==datetime) 
        agora = datetime.now()
        self.relogio.data_hora = agora
        data_relogio = self.relogio.data_hora        
        delta = data_relogio - agora
        self.assertTrue(delta.seconds >= -10 and delta.seconds <= 10)        
        
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
    
    
    