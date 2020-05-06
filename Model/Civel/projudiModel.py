from Model.Civel.rootModel import RootModel
from Model.processoPlataformaModel import ProcessoPlataformaModel
from Model.toolsModel import *



class ProjudiModel(RootModel):
    def __init__(self, site, mode_execute, SQL_Long, platform_id, platform_name, state, grau=1):
        self.grau= grau
        self.log_error=None
        self.flag = None
        self.state=state
        super().__init__(site, mode_execute, SQL_Long, platform_id, platform_name, state, grau)

    # VALIDAÇÂO DE PALAVRAS CHAVE 2º
    def keywords_2_degree(self,string):
        string = string.upper()

        if 'RECURSO SEM EFEITO SUSPENSIVO' in  string:
            return True

        string.replace('\n',' ').replace('\t',' ').replace('-',' ')
        string= set(string.split(' '))


        keyword_base = {'RECURSO','REMESSA','REMETIDO',
                        'RECURSAL', 'TURMA' ,'SEGUNDO','GRAU'
                       }

        return len(keyword_base.intersection(string))>0

    # COLETA DO NUMERO DmO PROCESSO DO 2 GRAU E CRIAR O PLP COM HAJA NO 2º GRAU!
    def validar_bool_2_grau(self, bool_2_grau, bool_2_grau_numero, prc_numero, prc_id):
        list_plp_2_grau = []

        if bool_2_grau and not bool_2_grau_numero:
            list_plp_2_grau = [
                ProcessoPlataformaModel(plp_prc_id=prc_id, plp_plt_id=5,
                                        plp_numero=prc_numero, plp_grau=2, plp_processo_origem=prc_numero)
            ]

        return list_plp_2_grau

    def formatar_data_adiencia(self, descricao):
        # Descrição são as todas as informações em uma string, no caso a linha no acompanhamento
        meses = {"Janeiro":'01',"Fevereiro":'02',"Março":'03',
                 "Abril":'04',"Maio":'05',"Junho":'06',"Julho":'07',
                 "Agosto":'08',"Setembro":'09',"Outubro":'10',
                 "Novembro":'11',"Dezembro":'12'}
        mes = " de {} de " # A data  dos acompanhamentos vem no formato : Agendada para: 10 de Dezembro de 2019 às 10:10

        for i in meses.keys(): # Iterar sobre as chaves do map, os meses


            mes_atual = mes.format(i) # fi



            # cara no tipo " de Janeiro de"
            if mes_atual in descricao: # Trocar pelo mês
                return  descricao.replace(mes_atual,'/'+meses[i]+'/') # Trocará  "10 de Dezembro de 2019" por "10/10/2019"

        return descricao
