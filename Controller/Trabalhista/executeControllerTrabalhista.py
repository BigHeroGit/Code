from Model.Trabalhista.pjeTrabalhistaModel import PJETabalhistaModel
from Model.Civel.rootModel import RootModel
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import  By
from Model.processoPlataformaModel import ProcessoPlataformaModel
from Model.Civel.rootModel import RootModel
from Model.logErrorModel import LogErrorModelMutlThread


from time import  sleep
class ExecutarTrabalhista:
    def __init__(self,trt):
        self.trt = trt
        self.log_error = LogErrorModelMutlThread(platform_name='Pje_trabalhista',num_thread=0,grau='1Grau')


    def check_process(self, n_proc, prc_id, plp_id, plp_data_update, log, state,processo):

                log.insert_info('Processo não encontrado!')

                process_platform = ProcessoPlataformaModel(plp_prc_id=prc_id, plp_plt_id=2,
                                                           plp_numero=n_proc, plp_segredo=False,
                                                           plp_localizado=False) if plp_data_update is None else ProcessoPlataformaModel(
                                                           plp_prc_id=prc_id, plp_plt_id=2,
                                                           plp_numero=n_proc, plp_segredo=False)

                list_objects_process = [(process_platform, [], [], [], [], plp_id, [], [], [])]

                # INSERE A LISTA DE OBJETOS NO BANCO DE DADOS
                # processo.export_to_database(objects=list_objects_process, log=log, list_name_urls=[],
                #                         platform='Pje', state=state, root=processo)
                return True




    def reiniciar_navegador(self,acesso,estado = 'SEM'):
        i = 0

        processo = PJETabalhistaModel(self.trt,acesso,estado)  # Dados para fazer a busca do processo
        status = processo.loguinPJE()
        while not status:  # Se entrat no while não consegiu logar
            if processo !=  None:
                processo.browser.quit()
            processo = PJETabalhistaModel(self.trt,acesso,estado)  # Dados para fazer a busca do processo
            status = processo.loguinPJE()
            if not status: # verifica se deu certo
                return processo
            if i >= 3:  # tentar logar quatro vezes se não lança exeção
                print('Erro, não foi possível abrir o navegador')
                return None
            i += 1
        return processo

    def varredura_processos(self, processosNumeros,acess,estado):



        try:
            list_documentos = []
            list_name_url = []
            print('Varedura processo')

            processo = PJETabalhistaModel(self.trt,acess,estado)  # Dados para fazer a busca do processo


            if not  processo.loguinPJE(): # Se entrat no while não consegiu logar
               try:
                    processo.browser.quit()
               except:
                   raise
                    #pass
               processo = self.reiniciar_navegador(acess,estado)


            if processo == None: # não deu para logar
                return processo


            for num in  processosNumeros: # iterar sobre a lista de processos

                try:
                    self.log_error.set_Handler(state=num[2])
                    # list_banco = (prc_numero, prc_id, prc_estado, plp_status, cadastro, plp_codigo, plp_data_update, plp_id, plp_numero)
                    list_documentos = [] # lista de documentos, que será a mesma da  movimentações
                    list_name_url = []  # lista de renomeios de downloads, é uma tupla (nome, renomeio)


                    #################### Abrir a box para colocar o numero do processo####################

                    i = 0
                    while not processo.abrir_box_processo():  # abre a box para a pesquisa do processo

                        if i >= 3:
                            processo.browser.quit()  # fecha que deu errado
                            processo = self.reiniciar_navegador(acess,estado)  # utilma tentativa

                        print('Erro ao entrar na pagina de busca do processo')
                        if processo is None: # não da mais para abrir
                             return processo
                        i += 1

                    ############################################################################################################

                    ########################### BUSCAR O PROCESSO E JA DEIXAR PRONTO PARA BAIXAR E PEGAR INFORMAÇÕES############
                    i = 0
                    while not(processo.buscarProcessoAcervo(num[0])) and i<=3: # tentar colocar o numero do processo na box, se tiver o processo já deixa na aba para pegar as informações
                        processo.fechaAba_e_voltaPrimeira()
                        i+=1
                    if len(processo.browser.window_handles)==1: # não consegiu colocar o numero na box, não achou o processo passa para o proximo
                        self.check_process(num[0], num[1], num[7], num[6], self.log_error, num[2], processo)
                        # self.log_error.insert_log("Processo não encontrado: {}".format(num[0]))

                        continue
                    if i>=3: # não consegiu cliclar no processo
                        self.log_error.insert_log("Não conseguiu cliclar no processo")
                        continue



                 ################################## PEGAR AS PARTES E OS ADVOGADOS DO PROCESSO##################################

                    list_adv, list_part = processo.get_Envolvidos() #  se não consegiu pegar os dados, as duas listas é vazia

                    i = 0
                    while len(list_part)==0 and i<3: # tentar pegar os envolvidos mais de uma vez

                        list_adv, list_part = processo.get_Envolvidos()  # se não consegiu pegar os dados, as duas listas é vazia
                        i+=1
                        self.log_error.insert_log("ERRO AO PEGAR AS PARTES")

                    if i>=3: # TENTOU VÁRIAS VEZES E NÃO CONSEGIU
                        list_adv = []
                        list_part = []
                        self.log_error.insert_log("ERRO AO PEGAR AS PARTES DEPOIS DE TRÊS TENTATIVAS")
                        continue # passsa para o proximo processo

                    print('List adv:', len(list_adv), ' Part: ', len(list_part))

                ################################# PEGAR AS CACTERISTICAS DO PROCESSO ##########################################
                    i = 0
                    caratreistica = processo.get_caracteristicas_proceso()

                    while caratreistica == None and i < 3:
                        self.log_error.insert_log("erro na primeira vez {}".format(i))
                        caratreistica = processo.get_caracteristicas_proceso()
                        i += 1

                    if i >= 3:
                        self.log_error.insert_log("REINICIAR O NAVEGADOR PARA PEGAR AS PARTES")
                        processo = self.reiniciar_navegador(acess,estado)
                        caratreistica = processo.get_caracteristicas_proceso()
                    if caratreistica == None:  # Não consgiu pegar as caracteristicas

                        self.log_error.insert_log('Não consegiu pegar as caracteristicas do processo: {}'.format( num[0]))
                        caratreistica = ProcessoPlataformaModel(plp_prc_id=num[1])

                    if caratreistica != None:
                        caratreistica.plp_prc_id=num[1]

                    #########################################################################################################

                    processo.ir_para_documento() # Ir para aba de documento para então pegalos

                    #########################################################################################################

                    # pegar a lista de documentos e baixar os arquivos#######################################################
                    i = 0
                    processo.parou_doc = 1
                    list_documentos, list_name_url = processo.get_Documentos(data_update = num[4],prc_id=num[1])   # pegar a lisda de documentos que será feito o download


                    ####################################### PEGAR AS AUDENCIAS E AS MOVIMENTAÇÕES#######################################

                    list_mov,list_aud_mov = processo.movimentacoes(list_name_url= list_name_url, data_update=num[4], prc_id=num[1]) # pegando as movimentaçõeS


                    print(list_aud_mov)
                    # list_documentos_sigilo, list_name_url_sigilo = processo.get_segredo_ou_sigilo()
                    # print('list sigilo: ', len(list_documentos_sigilo))
                    print('tmanho da lista de url: ', len(list_name_url))

                    # list_aud = processo.tratamento_audiencias(list_aud_mov)
                    list_mov += list_documentos
                    print('tam mov: ', len(list_mov),' aud:', len(list_aud_mov))
                    print('Name url - > ', list_name_url)
                    # print('Tam audiencia: ->', len(list_aud))
                    process_platform = []                                                               #i_proc[7]
                    # print('Lis _ mov',list_mov)
                    # Processo plataforma model é as caracteristicas

                ########################################################################## COLOCAR DADOS NO BANCO###########

                    list_objects_process = [(caratreistica, list_part, list_adv,  list_mov,num[7], [], [],[], [])]
                    # INSERE A LISTA DE OBJETOS NO BANCO DE DADOS

                    #processo.export_to_database(objects=list_objects_process, log=self.log_error, list_name_urls=list_name_url,platform='Pje', state=num[2], root=processo)

                    processo.fechaAba_e_voltaPrimeira()

                except:
                    raise
                    self.log_error.insert_log('Erro ao pegar informações do processso {} !'.format(num[0]))
                    processo.fechaAba_e_voltaPrimeira()

            # return processo
        except:


            # self.log_error.insert_log('ERRO DESCONHECIDO NA VARREDURA DO PROCESSO!')
            raise
            pass






        # processo.browser.quit()



