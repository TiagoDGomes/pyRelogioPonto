# -*- coding: utf-8 -*-
import unittest
from ..henryorion5 import Orion5ODBCMode
import os
from ..base import Colaborador

class TestConexao(unittest.TestCase):  
    def setUp(self):
        unittest.TestCase.setUp(self)  
        self.relogio = Orion5ODBCMode(conn_str=os.environ['TEST_ORION5_CONN_STR'])
    
    def test_conexao(self):
        self.relogio.conectar()
        self.assertTrue(self.relogio.conectado)
    
    def test_colaboradores(self):
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
        
        
        