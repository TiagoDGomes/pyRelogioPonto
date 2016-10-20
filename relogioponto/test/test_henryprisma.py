# -*- coding: utf-8 -*-
from ..henryprisma import HenryPrisma
from _warnings import warn
import unittest
from relogioponto.base import Colaborador, Empregador, RelogioPontoException
from datetime import datetime


RELOGIO_PRISMA_ENDERECO = '10.3.0.10'
TESTAR_INSERCAO_EXCLUSAO = False
TESTAR_ALTERACAO_DATAHORA = False
TESTAR_ALTERACAO_EMPREGADOR = False
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
    
    def test_biometrias(self):
        biometrias = self.colaborador.biometrias
        self.assertGreaterEqual(len(biometrias), 0)


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
        self.assertEqual(len(self.relogio.colaboradores.filter(matricula=112233)), 0)  
          
    def test_colaboradores(self):
        global TESTAR_INSERCAO_EXCLUSAO
        if not TESTAR_INSERCAO_EXCLUSAO:
            warn('\nTestes de insercao e exclusao ignorados. Altere a variavel TESTAR_INSERCAO_EXCLUSAO para executar estes testes.\n')
        else:
            if len(self.relogio.colaboradores.filter(matricula=112233)) > 0:
                self.t_apagarcolaborador()
               
            colaborador = Colaborador(self.relogio)
            colaborador.nome = u"TESTCASE Á"
            colaborador.pis = "5555.55555.55/5" 
            colaborador.matriculas = [112233,445566]
            colaborador.verificar_digital = True
            colaborador.save()
            self.assertNotEqual(colaborador.id, None)
    
            lista = self.relogio.colaboradores.filter(matricula=112233)
            self.assertEqual(len(lista), 1)                
    
            colaborador_salvo = lista[0]
            self.assertNotEqual(colaborador_salvo.id, None)
    
            self.assertEqual(colaborador_salvo.nome, colaborador.nome)
            self.assertEqual(colaborador_salvo.pis, colaborador.pis)
            self.assertEqual(colaborador_salvo.matriculas, colaborador.matriculas)
            self.assertEqual(colaborador_salvo.verificar_digital, colaborador.verificar_digital)
    
            
            lista = self.relogio.colaboradores.all()
            self.assertTrue(len(lista) >= 1)
            self.t_apagarcolaborador()
    
    def test_hora(self):
        if not TESTAR_ALTERACAO_DATAHORA:
            warn('\nTestes de alteracao de data e hora ignorados. Altere a variavel TESTAR_ALTERACAO_DATAHORA para executar estes testes.\n')
            
        else:
            data_relogio = self.relogio.data_hora
            self.assertEqual(type(data_relogio),datetime) 
            agora = datetime.now()
            self.relogio.data_hora = agora
            data_relogio = self.relogio.data_hora        
            delta = data_relogio - agora
            self.assertTrue(delta.seconds >= -10 and delta.seconds <= 10)  
            
    def test_empregador(self):
        empregador = self.relogio.get_empregador()   
        self.assertTrue(type(empregador) == Empregador)  
        if not TESTAR_ALTERACAO_EMPREGADOR:
            warn('\nTestes de alteracao de empregador ignorados. Altere a variavel TESTAR_ALTERACAO_EMPREGADOR para executar estes testes.\n')
        else:    
            alterado_empregador = Empregador()
            alterado_empregador.razao_social = u'Teste'
            alterado_empregador.local = u'Teste local'
            alterado_empregador.documento = u'00.000.000/0000-00'
            alterado_empregador.tipo_documento = 1
            alterado_empregador.cei = u'00.000.00000/00'
            print alterado_empregador
            print empregador
            with self.assertRaises(RelogioPontoException):
                self.relogio.set_empregador(alterado_empregador) 
            
            alterado_empregador.documento = u'26.347.567/0001-22'            
            self.relogio.set_empregador(alterado_empregador) 
            empregador_salvo = self.relogio.get_empregador()  
             
            self.assertEqual(empregador_salvo.razao_social, alterado_empregador.razao_social)  
            self.assertEqual(empregador_salvo.local, alterado_empregador.local)  
            self.assertEqual(empregador_salvo.documento, alterado_empregador.documento)  
            self.assertEqual(empregador_salvo.tipo_documento, alterado_empregador.tipo_documento)  
            self.assertEqual(empregador_salvo.cei, alterado_empregador.cei)  
            
            #self.relogio.set_empregador(empregador)
    
    def test_getafd(self):
        todos = self.relogio.get_afd()
        self.assertEqual(type(todos), str)

    def test_getafd_filtrado(self):
        todos = self.relogio.get_afd()
        filtrado = self.relogio.get_afd(nsr=2)
        self.assertNotEqual(todos, filtrado)

    def test_getafd_datahora(self):
        filtro = self.relogio.get_afd(data_hora=datetime.now())
        self.assertEqual(filtro,'')
    
    
                
                    
                
                
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
    
    
    