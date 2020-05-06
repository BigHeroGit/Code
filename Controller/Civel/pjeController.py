from Model.toolsModel import *
from Model.Civel.pjeModel import PjeModel
class pjeController(PjeModel):
    def __init__(self, site, mode_execute, access, platform_id, platform_name, flag, num_thread,state,link_consulta,grau='1Grau'):


        super().__init__(site, mode_execute, access, platform_id, platform_name, state, num_thread, link_consulta, flag,
                         grau)
        if self.state == "RO":
            self.arq_name = str(os.path.abspath('../Temp/{}/{}/ControlerDePrioridade'.format(platform_name.upper(), self.state.upper())))
            Tools.new_path(self.arq_name)
            arq = open(self.arq_name + "\\{}.cdp".format(str(num_thread)), 'w')
            arq.write(str(self.num_thread))
            arq.close()

    # COLETA OS DADOS DO ACOMPANHAMENTOS, AUDIENCIAS E DOWNLOADS
    def acomp_down_aud(self, ult_mov, list_audiences,list_acomp_download, list_name_urls):

    #def acomp_down_aud(self, prc_id, ult_mov,n_proc):

        lista_audiencia = []
        try:
            # self.browser.switch_to_window(self.browser.window_handles[-1])
            # print(f'self.browser.window_handles -> {len(self.browser.window_handles)}')
            wait = WebDriverWait(self.browser,15)
            lista_audiencia = []
            self.tamanho_total_mov = self.tamanho_movimentacoes() # PEGAR O TAMANHO TOTAL DAS MOVIMENTAÇÕES
            # input('self.tamanho_total_mov -> {}'.format(self.tamanho_total_mov))
            list_acomp_download_aux, lista_audiencia_aux, list_name_urls_n_aux,novas_movimentacoes,segundo = self.pegar_lista_de_acompanhamentos(ult_mov) # Pegar os acompanhamentos
            # input('len(list_acomp_download_aux) =  {}'.format(len(list_acomp_download)))

            if novas_movimentacoes == False: # Não teve novas movimentacoes
                print("PROCESSO NÃO TEM NOVAS MOVIMENTAÇÕES!!!!")
                return True, True,segundo
            list_acomp_download+=list_acomp_download_aux
            lista_audiencia+=lista_audiencia_aux
            list_name_urls+=list_name_urls_n_aux
            self.log_error.insert_info("coleta dos acompanhamentos")
            # print(48)
            try:
                list_audiences_aux = self.pegar_audiencias_nova_aba()  # Pegar as audiencias no menu
                lista_audiencia += list_audiences_aux  # Colocar na lista de audiecia
            except Exception as erro:
               print(erro)
               self.log_error.insert_log("Erro audiência")
               raise
            # print(56)
            # self.voltar_para_acompanhamentos()  # Voltar para a aba de acompanhamentos
            self.log_error.insert_info("Coleta de audiencias na aba de audiências")
            list_audiences += lista_audiencia
            print(list_audiences)
            return True, None,segundo
        except Exception as erro:
            print("Erro ::>>>>>>>" + str(erro))
            self.log_error.insert_log("ERRO AO PEGAR AS MOVIMENTAÇÕES!")
            raise
            return False, None
