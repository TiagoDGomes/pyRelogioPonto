# -*- coding: utf-8 -*-
from .base import RelogioPonto, RelogioPontoException, Colaborador
import pyodbc
from core.util import somente_numeros


class Orion5ODBCMode(RelogioPonto):
    conn = None
    def __init__(self, conn_str=None, *args, **kwargs):
        self.conectado = None
        self.conn_str = conn_str
        self.conectar()

    
    
    def conectar(self):
        if not self.conn_str:
            raise RelogioPontoException(r"String de conexão ODBC vazia")
        try:
            self.conn = pyodbc.connect(self.conn_str)
            self.conectado = True
        except Exception as e:
            print(e)
            self.conectado = False
            
    
    def get_afd(self, nsr=None, data_hora=None):
        cursor = self.conn.cursor()
        sql = '''SELECT HE22_AT_COD, 
                        HE22_DT_REGISTRO, 
                        HE02_ST_PIS 
                 FROM HE22 
                 INNER JOIN HE02 
                    ON HE02_ST_MATRICULA = HE22_ST_MATRICULA 
                 WHERE HE02_ST_PIS <> '000000000000' 
                   AND HE02_ST_PIS <> ''
              '''
        if nsr:
            if data_hora:                
                cursor.execute(sql + 
                    """AND HE22_DT_REGISTRO = ? AND HE22_AT_COD >= ?""" ,
                    data_hora, nsr)
            else:
                cursor.execute(sql + 'AND HE22_AT_COD >= ?' , nsr)
        else:
            if data_hora:                
                cursor.execute(sql + 'AND HE22_DT_REGISTRO = ?' , data_hora)
            else:
                cursor.execute(sql)
                
        rows = cursor.fetchall()
        afd = []
        for row in rows:
            afd.append('{:09d}3{:%d%m%Y%H%M}{:012d}'.format(
                                                row[0],
                                                row[1], 
                                                int(row[2]))
                       )
        return "\r\n".join(afd)
    
    @property
    def quantidade_eventos_registrados(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT MAX(HE22_AT_COD) FROM HE22;")
        row = cursor.fetchone()
        return row[0]
        
    @property    
    def colaboradores(self):
        return ColaboradorOrion5ODBCLista(self) 
            
    def gravar_colaborador(self, colaborador):
        pis = somente_numeros(colaborador.pis)
        matricula = "{:020}".format( colaborador.matriculas[0] )
        cursor = self.conn.cursor()
        param_sql = []
        param_sql.append( matricula ) 
        param_sql.append( colaborador.nome )
        param_sql.append( colaborador.verificar_digital )
        param_sql.append( pis )

        
        cursor.execute("""SELECT HE02_ST_PIS 
                            FROM HE02 
                            WHERE HE02_ST_PIS = ?""", pis)
        
        row = cursor.fetchone()
        if row: # se há um colaborador com PIS... 
            sql = '''UPDATE HE02 SET HE02_ST_MATRICULA = ?, 
                            HE02_ST_NOME = ? , 
                            HE02_BL_VERIFDIG = ? 
                     WHERE HE02_ST_PIS = ?  
                     '''
            
        else: 
            # PIS não encontrado. Procurar por matrícula...
            cursor.execute("""SELECT HE02_ST_MATRICULA 
                              FROM HE02 
                              WHERE HE02_ST_MATRICULA 
                                  LIKE '%{matricula}'
                            """.format(
                                    matricula=colaborador.matriculas[0]
                                    )
                           )
            row = cursor.fetchone()
            if row: # se tem colaborador com uma matrícula especifica...
                sql = '''UPDATE HE02 
                            SET HE02_ST_PIS = ?, 
                            HE02_ST_NOME = ? , 
                            HE02_BL_VERIFDIG = ? 
                            WHERE HE02_ST_MATRICULA = ?  
                            '''
                # inverter parâmetros
                param_sql[0] = pis
                param_sql[3] = matricula  
            else:                
                sql = '''INSERT INTO HE02 (HE02_ST_MATRICULA,
                                            HE02_ST_NOME,
                                            HE02_BL_VERIFDIG,
                                            HE02_ST_PIS) 
                                VALUES (?,?,?,?) '''
                 
        cursor.execute(sql,
                       param_sql[0],
                       param_sql[1],
                       param_sql[2],
                       param_sql[3]) #atualizar dados        
            
        cursor.execute("""
                        SELECT HE02_AT_COD 
                        FROM HE02 WHERE HE02_ST_PIS = ?""",
                        pis
                      )
        row = cursor.fetchone()
        colaborador.id = row[0]   
         
         
class ColaboradorOrion5ODBCLista(object):
    def __init__(self, relogio):
        self.relogio = relogio
        self._list_colaboradores = None        
    
    def all(self):
        return self.filter()
    
    def filter(self, nome=None, pis=None, matricula=None):        
        cursor = self.relogio.conn.cursor()
        lista_colaboradores = []
        sql = '''SELECT HE02_ST_NOME,
                        HE02_BL_VERIFDIG, 
                        HE02_AT_COD, 
                        HE02_ST_MATRICULA,
                        HE02_ST_PIS 
                 FROM HE02 WHERE 1 = 1 '''
        if pis:
            sql += "AND HE02_ST_PIS LIKE '%{pis}' ".format(
                                                     pis=somente_numeros(pis)
                                                    )  
        if matricula:
            sql += "AND HE02_ST_MATRICULA LIKE '%{matricula}' ".format(
                                                     matricula=matricula
                                                    )
        if nome:
            sql += "AND HE02_ST_NOME LIKE '%{nome}%'".format(nome=nome)
            
        cursor.execute(sql)
            
        rows = cursor.fetchall()
        for row in rows: 
            colaborador = Colaborador(relogio=self.relogio)
            colaborador.nome = row[0]
            colaborador.pis = row[4]
            colaborador.verificar_digital = row[1]
            colaborador.id = row[2]
            colaborador.matriculas.append(row[3])
            lista_colaboradores.append(colaborador)        
        return lista_colaboradores
            
        
        
            