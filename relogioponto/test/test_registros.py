# -*- coding: utf-8 -*-
import unittest
from relogioponto.test.test_henryprisma import RELOGIO_PRISMA_ENDERECO
from relogioponto.henryprisma import HenryPrisma
from datetime import datetime


class TestRegistros(unittest.TestCase):    
       
    def setUp(self):
        self.endereco = RELOGIO_PRISMA_ENDERECO
        self.relogio = HenryPrisma(self.endereco)
        self.relogio.conectar() 
    
    def tearDown(self):
        self.relogio.desconectar()
        del self.relogio 
           
    def test_getregistros(self):
        registros = self.relogio.get_registros()
        self.assertTrue(len(registros)>0)
        quantidade_tipo_2 = 0
        quantidade_tipo_3 = 0
        quantidade_tipo_4 = 0
        quantidade_tipo_5 = 0
        for registro in registros:            
            self.assertEqual(type(registro['nsr']), int)
            self.assertEqual(type(registro['tipo']), int)
            if registro['nsr'] == 999999999:
                self.assertIn('quantidade_tipo_2' , registro)
                self.assertIn('quantidade_tipo_3' , registro)
                self.assertIn('quantidade_tipo_4' , registro)
                self.assertIn('quantidade_tipo_5' , registro)
                self.assertEqual(registro['tipo'], 9)
                self.assertEqual(registro['quantidade_tipo_2'] , quantidade_tipo_2)
                self.assertEqual(registro['quantidade_tipo_3'] , quantidade_tipo_3)
                self.assertEqual(registro['quantidade_tipo_4'] , quantidade_tipo_4)
                self.assertEqual(registro['quantidade_tipo_5'] , quantidade_tipo_5)
                
            else:
                if registro['tipo'] == 1:
                    self.assertIn('tipo_identificador_empregador' , registro)
                    self.assertIn('documento' , registro)
                    self.assertIn('cei' , registro)
                    self.assertIn('razao_social' , registro)
                    self.assertIn('numero_rep' , registro)
                    self.assertIn('data_inicial' , registro)
                    self.assertIn('data_final' , registro)
                    self.assertIn('data_geracao' , registro)
                    self.assertEqual(type(registro['data_inicial']), datetime)
                    self.assertEqual(type(registro['data_final']), datetime)
                    self.assertEqual(type(registro['data_geracao']), datetime)
                    
                elif registro['tipo'] == 2: #  Registro de inclusão ou alteração da identificação da empresa no REP 
                    quantidade_tipo_2 += 1
                    self.assertIn('data_gravacao' , registro)                          
                    self.assertIn('identificador_empregador' , registro)                          
                    self.assertIn('documento' , registro)
                    self.assertIn('cei' , registro)
                    self.assertIn('razao_social' , registro)
                    self.assertIn('local' , registro)
                    self.assertTrue(registro['identificador_empregador'] == 1 or registro['identificador_empregador'] == 2)                          
                    self.assertEqual(type(registro['documento']), str)
                    self.assertTrue(type(registro['cei']) == int or registro['cei'] == None)                                  
                    self.assertEqual(type(registro['data_gravacao']), datetime)
                    
                elif registro['tipo'] == 3:
                    quantidade_tipo_3 += 1
                    self.assertIn('data_marcacao' , registro)
                    self.assertEqual(type(registro['data_marcacao']), datetime)
                    #self.assertIn('empregado' , registro)
                    
                elif registro['tipo'] == 4:
                    quantidade_tipo_4 += 1
                    
                elif registro['tipo'] == 5:
                    quantidade_tipo_5 += 1