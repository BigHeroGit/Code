from Model.logErrorModel import LogErrorModelMutlThread
from Model.toolsModel import *
from Model.audienciaModel import AudienciaModel
from Model.acompanhamentoModel import AcompanhamentoModel
from Model.processoPlataformaModel import ProcessoPlataformaModel
from Model.processoModel import processoModel
from Model.Civel.processumModel import ProcessumModel
from Model.processoArquivoModel import ProcessoArquivoModel
from time import time


class processumController(ProcessumModel):
    def __init__(self, site, mode_execute, access, platform_id, platform_name, num_thread):
        self.platform_id = platform_id
        self.state = None
        super().__init__(site, mode_execute, access, platform_id, platform_name)
        self.erroo = False
        self.log_error = LogErrorModelMutlThread(platform_name='Processum', num_thread=num_thread)
        # self.log_error.set_Handler('TEST')

    # VALIDA A INICIALIZAÇÃO DA VARREDURA NA PLATAFORMA
    def initializer(self, user, password):

        while True:
            try:
                # INICIALIZA BROWSER
                if self.init_browser():
                    # LOGIN NA PLATAFORMA
                    if self.login(user, password):
                        break
            except:
                self.browser.quit()
                continue


    # SELECIONA PROCESSOS DO BANCO DE DADOS E PROCURA NA PLATAFORMA PARA UPDATE NO BANCO
    def search_process(self, user, password, row_database,dict_acp_arq):

        # row_database=[('24/2019--18', None, '06250172920188040015', 19652, None, 'AM', None, None, None, 0)]
        # dict_acp_arq={19652: {}}

        # print('dict_acp_aud', dict_acp_arq.items())
        # print('conn_database', dict_acp_arq.values())
        # print('row_database', row_database)
        data=datetime(datetime.now().year, datetime.now().month, datetime.now().day, datetime.now().hour)
        # INICIA O BROWSER E A SESSÃO NA PLATAFORMA
        self.initializer(user, password)
        # VERIFICA CADA NUMERO DE PROCESSO DENTRO DA ESTRUTURA FORNECIDA
        i_n = 0
        self.erroo = False
        list_erro = []
        for i_proc in row_database:
            # VERIFICA SE PROCESSO EXISTE
            t0 = time()
            self.log_error.set_Handler(i_proc[5])
            list_objects_process = []
            list_name_urls = []
            dict_urls = {}
            i_n += 1
            n_seq = i_proc[0]

            self.log_error.insert_title(i_proc[0])
            print("\n{}ª: Coleta de dados do processo do sequencial : {}\n".format(i_n, n_seq))
            print('\n i_proc-> ', i_proc)
            print("\nPara atualizar->", len(dict_acp_arq[i_proc[3]]))

            # VERIFICA SE O NAVEGADOR ESTÁ ABERTO
            try:
                if len(self.browser.window_handles) > 1:
                    if self.browser is not None:
                        self.browser.quit()
                        self.log_error.insert_log('Sessão encerrou!')
                        return -1
            except:
                self.log_error.insert_log('navegador fechou!')
                return -1

            bol_find_process = self.find_process(n_seq)
            try:
                wait = WebDriverWait(self.browser, 5)
                wait.until(EC.presence_of_element_located((By.XPATH, '/html/body[2]/form[2]')))
            except:
                try:
                    self.browser.refresh()
                except:
                    self.erroo=True


            # BUSCA PELO PROCESSO NA PLATAFORMA
            if len(i_proc[0]) and bol_find_process and (not self.erroo):
                print('\n', sep=' ', end='1', flush=True)
                prc_carteira, \
                prc_sequencial, \
                prc_numero, \
                prc_parte_ativa, \
                prc_parte_passiva, \
                plp_fase, \
                plp_filtro = self.dados_de_identificacao
                print('', sep=' ', end='2', flush=True)

                prc_data_cadastro, \
                prc_objeto1, \
                prc_objeto2, \
                prc_objeto3, \
                prc_objeto4, \
                plp_localizado, \
                plp_data_distribuicao = self.dados_do_processo

                # contingencia\
                #     ,tipo_de_contingencia\
                #     ,motivo\
                #     ,longo_prazo_provavel\
                #     ,curto_prazo_provavel=self.dados_de_contingencia
                #
                prc_penhora, prc_apto_pgto = self.dados_de_pagamnetosGarantia
                print("prc_penhora",prc_penhora)
                print('', sep=' ', end='3', flush=True)
                data_update = i_proc[6] if None is i_proc[6] or not (type(i_proc[6]) == 'str') else Tools.treat_date(
                    i_proc[6])
                # PEGA MOVIMENTAÇÕES E SALVA NOVAS
                list_acomp_arq, \
                list_audiencias, \
                list_acomp_arq_atualizados, \
                key_list, \
                aux_prc_penhora = self.acompanhamentos(data_update, data, dict_acp_arq[i_proc[3]], i_proc[3])
                print("aux_prc_penhora",aux_prc_penhora)
                if len(key_list) > 0:
                    list_name_urls += key_list
                prc_penhora = prc_penhora or aux_prc_penhora

                # DEFININDO ESTADOS
                print('', sep=' ', end='4', flush=True)
                prc_estado = self.tratar_estado(str(plp_localizado).split('-')[0])
                plp_localizado = True

                # CRIA O OBJETO PROCESSO-PLATAFORMA QUE SERÁ INSERIDO NO BANCO DE DADOS
                process_platform = ProcessoPlataformaModel(plp_prc_id=i_proc[3], plp_plt_id=1,
                                                           plp_numero=prc_numero,
                                                           plp_status=None, plp_comarca=None, plp_serventia=None,
                                                           plp_juizo=None, plp_fase=plp_fase, plp_diligencia=None,
                                                           plp_vara=None, plp_filtro=plp_filtro, plp_penhora=None,
                                                           plp_valor_causa=None, plp_valor_condenacao=None,
                                                           plp_classe=None, plp_assunto=None, plp_processo_origem=None,
                                                           plp_data_distribuicao=plp_data_distribuicao,
                                                           plp_data_transito_julgado=None,
                                                           plp_codigo=None, plp_segredo=None,
                                                           plp_efeito_suspensivo=None,
                                                           plp_prioridade=None, plp_localizado=plp_localizado,
                                                           plp_migrado=None,
                                                           plp_grau=None,
                                                           plp_data_update=data)
                # print('plp_filtro2',plp_filtro)
                # CRIA O OBJETO PROCESSO A QUE SERÁ INSERIDO NO BANCO DE DADOS
                process = processoModel(
                    prc_sequencial=prc_sequencial, prc_numero=prc_numero, prc_carteira=prc_carteira,
                    prc_estado=prc_estado, prc_parte_ativa=prc_parte_ativa, prc_parte_passiva=prc_parte_passiva,
                    prc_objeto1=prc_objeto1,
                    prc_objeto2=prc_objeto2, prc_objeto3=prc_objeto3, prc_objeto4=prc_objeto4,
                    prc_data_cadastro=prc_data_cadastro, prc_penhora=prc_penhora, prc_apto_pgto=prc_apto_pgto
                )
            elif i_proc[4] is not None and (not self.erroo):
                self.log_error.insert_log('Processo - Não localizado')
                process = processoModel()
                process_platform = ProcessoPlataformaModel(plp_localizado=False)
                list_acomp_arq = []
                list_audiencias = []
                list_acomp_arq_atualizados = []

            else:
                self.log_error.insert_info('Procedimento finalizado!')
                print('Procedimento finalizado em: {} secs\n'.format(time() - t0).upper(), "_" * 65)
                continue

            list_objects_process.append((process, process_platform, list_acomp_arq, list_audiencias,
                                         list_acomp_arq_atualizados, i_proc[4], i_proc[3]))
            print('', sep=' ', end='5', flush=True)

            # TRATANDO OS PROCESSO COM ERRO
            if self.erroo:
                self.erroo = False
                if n_seq not in list_erro:
                    list_erro.append(n_seq)
                    row_database.append(i_proc)
                self.log_error.insert_info('Procedimento Inserido na lista de erros')
                print('Procedimento finalizado em: {} secs\n'.format(time() - t0).upper(), "_" * 65)
                continue
            # INSERE A LISTA DE OBJETOS NO BANCO DE DADOS
            print('', sep=' ', end='6\n', flush=True)
            self.export_to_database_processum(objects=list_objects_process,
                                              list_name_urls=list_name_urls, log=self.log_error, root=self,
                                              state=i_proc[5])
            self.log_error.insert_info('Procedimento finalizado!')
            print('Procedimento finalizado em: {} secs\n'.format(time() - t0).upper(), "_" * 65)

            try :
                wait = WebDriverWait(self.browser, 5)
                wait.until(EC.presence_of_element_located((By.XPATH, '/html/body[2]/form[2]')))
            except :
                try :
                    self.browser.refresh()
                except :
                    continue

        self.browser.quit()
        return i_n

    # PEGAR DDADOS DA PARTE IDENTIFICAÇÃO
    @property
    def dados_de_identificacao(self):
        try:
            try:
                wait = WebDriverWait(self.browser, 5)
                wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="fDetalhar:pnlGeraldet"]/tbody')))
            except:
                self.browser.refresh()
                wait = WebDriverWait(self.browser, 5)
                wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="fDetalhar:pnlGeraldet"]/tbody')))

            wait = WebDriverWait(self.browser, 2)
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="fDetalhar:empresa"]')))
            prc_carteira = self.browser.find_element_by_xpath('//*[@id="fDetalhar:empresa"]').text
            prc_carteira = Tools.remove_accents(prc_carteira).upper()

            wait = WebDriverWait(self.browser, 2)
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="fDetalhar:numSequencial"]')))
            prc_sequencial = self.browser.find_element_by_xpath('//*[@id="fDetalhar:numSequencial"]').text
            prc_sequencial = Tools.remove_accents(prc_sequencial).upper()

            wait = WebDriverWait(self.browser, 2)
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="fDetalhar:numero"]')))
            prc_numero = self.browser.find_element_by_xpath('//*[@id="fDetalhar:numero"]').text
            prc_numero = Tools.remove_accents(prc_numero).upper()

            wait = WebDriverWait(self.browser, 5)
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="fDetalhar:dtbPoloAtivo2"]/tbody/tr')))
            prc_parte_ativa = self.browser.find_element_by_xpath('//*[@id="fDetalhar:dtbPoloAtivo2"]/tbody/tr').text
            prc_parte_ativa = Tools.remove_accents(prc_parte_ativa.split(', ')[0]).upper()

            wait = WebDriverWait(self.browser, 2)
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="fDetalhar:dtbPoloPassivo2"]/tbody/tr')))
            prc_parte_passiva = self.browser.find_element_by_xpath('//*[@id="fDetalhar:dtbPoloPassivo2"]/tbody/tr').text
            prc_parte_passiva = Tools.remove_accents(prc_parte_passiva.split(', ')[0]).upper()

            wait = WebDriverWait(self.browser, 2)
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="fDetalhar:faseProcessual"]')))
            plp_fase = self.browser.find_element_by_xpath('//*[@id="fDetalhar:faseProcessual"]').text
            plp_fase = Tools.remove_accents(plp_fase).upper()

            plp_filtro = len(self.browser.find_elements_by_xpath(
                '//*[@id="fDetalhar:pnlAlertaContaFiltro"]/thead/tr/th')) >= 1 and 'Processo com conta(s) em Filtro' in self.browser.find_element_by_xpath(
                '//*[@id="fDetalhar:pnlAlertaContaFiltro"]/thead/tr/th').text
            # print('plp_filtro',plp_filtro)
        except:
            self.browser.refresh()
            self.log_error.insert_log('Erro- ao coletar dados dados_identificacao')
            self.erroo = True
            return None, None, None, None, None, None, None

        return prc_carteira, prc_sequencial, prc_numero, prc_parte_ativa, prc_parte_passiva, plp_fase, plp_filtro

    @property
    def dados_do_processo(self):
        try:
            self.browser.execute_script('arguments[0].style.display = "block";',
                                        self.browser.find_element_by_xpath(
                                            '//*[@id="fDetalhar:lblDadosProcesso_body"]'))
            wait = WebDriverWait(self.browser, 4)
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="fDetalhar:lblDadosProcesso_body"]')))
        except:
            self.browser.refresh()
            self.log_error.insert_log('Erro ao coletar dados dados_identificacao')

            # raise
            return None, None, None, None, None, None, None

        try:
            prc_data_cadastro = self.browser.find_element_by_xpath('//*[@id="fDetalhar:dataCadastro"]').text
            prc_data_cadastro = Tools.treat_date(prc_data_cadastro)
        except:
            prc_data_cadastro = None
            # self.log_error.insert_log('Erro ao coletarprc_data_cadastro')

        try:
            prc_objeto = self.browser.find_element_by_xpath('//*[@id="fDetalhar:objAcao"]').text
            prc_objeto = Tools.remove_accents(prc_objeto).upper()
            prc_objeto = prc_objeto.split('-')[:-1]
            n = len(prc_objeto)
            while n < 4:
                prc_objeto.append(None)
                n += 1
            prc_objeto1, prc_objeto2, prc_objeto3, prc_objeto4 = prc_objeto
        except:
            prc_objeto1, prc_objeto2, prc_objeto3, prc_objeto4 = None, None, None, None
            # self.log_error.insert_log('Erro ao coletar prc_objeto')

        try:

            plp_localizado = self.browser.find_element_by_xpath('//*[@id="fDetalhar:localizacao"]').text
            plp_localizado = Tools.remove_accents(plp_localizado).upper()
        except:
            plp_localizado = None
            self.log_error.insert_log('Erro ao coletar plp_localizado')

        try:
            plp_data_distribuicao = self.browser.find_element_by_xpath('//*[@id="fDetalhar:dataDistribuicao')
            plp_data_distribuicao = Tools.treat_date(plp_data_distribuicao)
        except:
            plp_data_distribuicao = None
            # self.log_error.insert_log('Erro ao coletar plp_data_distribuicao')

        return prc_data_cadastro, prc_objeto1, prc_objeto2, prc_objeto3, prc_objeto4, plp_localizado, plp_data_distribuicao

    @property
    def dados_de_contingencia(self):

        try:
            self.browser.execute_script('arguments[0].style.display = "block";',
                                        self.browser.find_element_by_xpath(
                                            '//*[@id="fDetalhar:pnlContingencia_body"]'))

            wait = WebDriverWait(self.browser, 4)
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="fDetalhar:pnlContingencia_body"]')))

            wait = WebDriverWait(self.browser, 4)
            wait.until(EC.element_to_be_clickable((By.XPATH, ' //*[@id="fDetalhar:expand"]')))
            self.browser.find_element_by_xpath(' //*[@id="fDetalhar:expand"]').click()
        except:
            self.log_error.insert_log('Erro ao coletar contingencia')
            self.erroo = True
            return None, None, None, None, None, None

        try:
            contingencia = self.browser.find_element_by_xpath('//*[@id="fDetalhar:tipoContingencia"]').text
            contingencia = Tools.remove_accents(contingencia).upper()
        except:
            contingencia = None
            # self.log_error.insert_log('Erro ao coletar contingencia')
            # raise

        try:
            tipo_de_contingencia = self.browser.find_element_by_xpath(
                '//*[@id="fDetalhar:especifTipoContingencia"]').text
            tipo_de_contingencia = Tools.remove_accents(tipo_de_contingencia).upper()
        except:
            tipo_de_contingencia = None
            # self.log_error.insert_log('Erro ao coletar tipo_de_contingencia')
            # raise

        try:
            motivo = self.browser.find_element_by_xpath('//*[@id="fDetalhar:especifTipoContingencia"]').text
            motivo = Tools.remove_accents(motivo).upper()
        except:
            motivo = None
            # self.log_error.insert_log('Erro ao coletar motivo')
            # raise

        try:
            curto_prazo_provavel = self.browser.find_element_by_xpath('//*[@id="fDetalhar:valorProvavel"]').text
            curto_prazo_provavel = Tools.remove_accents(curto_prazo_provavel)
            curto_prazo_provavel = Tools.treat_value_cause(curto_prazo_provavel)
        except:
            curto_prazo_provavel = None
            # self.log_error.insert_log('Erro ao coletar curto_prazo_provavel')
            # raise

        try:
            longo_prazo_provavel = self.browser.find_element_by_xpath('//*[@id="fDetalhar:valorLongoPrazo"]').text
            longo_prazo_provavel = Tools.remove_accents(longo_prazo_provavel)
            longo_prazo_provavel = Tools.treat_value_cause(longo_prazo_provavel)
        except:
            longo_prazo_provavel = None
            # self.log_error.insert_log('Erro ao coletar longo_prazo_provavel')
            # raise

        try:
            valor_total_provavel = self.browser.find_element_by_xpath('//*[@id="fDetalhar:valorProvavel2"]').text
            valor_total_provavel = Tools.remove_accents(valor_total_provavel)
            valor_total_provavel = Tools.treat_value_cause(valor_total_provavel)
        except:
            valor_total_provavel = None
            # self.log_error.insert_log('Erro ao coletar valor_total_provavel')
            # raise

        return contingencia, tipo_de_contingencia, motivo, longo_prazo_provavel, curto_prazo_provavel, valor_total_provavel

    @property
    def dados_de_pagamnetosGarantia(self):

        try:
            self.browser.execute_script('arguments[0].style.display = "block";',
                                        self.browser.find_element_by_xpath(
                                            '//*[@id="fDetalhar:dtbValoresPorData"]'))

            wait = WebDriverWait(self.browser, 4)
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="fDetalhar:dtbValoresPorData"]')))

            wait = WebDriverWait(self.browser, 4)
            wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="fDetalhar:_idJsp175_header"]')))
            self.browser.find_element_by_xpath('//*[@id="fDetalhar:_idJsp175_header"]').click()
        except:
            self.log_error.insert_log('ERRO- AO ACESSA OS PAGAMENTOS/GARANTIA ')
            return False, None
        try:
            try:
                wait = WebDriverWait(self.browser, 4)
                wait.until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="fDetalhar:dtbValoresPorData"]/tbody/tr')))
            except:
                self.log_error.insert_info('NÃO A DADOS NA PAGAMENTOS/GARANTIA ')
                return False, None
            dtb = self.browser.find_elements_by_xpath('//*[@id="fDetalhar:dtbValoresPorData"]/tbody/tr')
            tam = len(dtb)
            prc_apto_pgto = True if tam else False
            prc_penhora = False
            for i in range(0, tam, 2):
                tipo = dtb[i].find_element_by_xpath('td[4]').text
                tipo = tipo.upper()
                prc_penhora = prc_penhora or 'GARANTIA JUDICIAL' in tipo or 'PENHORA ON LINE' in tipo
                if len(dtb[i].find_elements_by_xpath('td[1]/a')):

                    dtb[i].find_element_by_xpath('td[1]/a').click()
                    j = i + 1

                    wait = WebDriverWait(self.browser, 4)
                    wait.until(EC.presence_of_element_located((By.XPATH,
                                                               '//*[@id="fDetalhar:dtbValoresPorData"]/tbody/tr[{}]/td/span/table/tfoot/tr/td'.format(
                                                                   str(j + 1)))))

                    wait = WebDriverWait(self.browser, 4)
                    wait.until(EC.visibility_of_all_elements_located(
                        (By.XPATH, '//*[@id="fDetalhar:dtbValoresPorData"]/tbody/tr')))
                    dtb = self.browser.find_elements_by_xpath('//*[@id="fDetalhar:dtbValoresPorData"]/tbody/tr')

                    verde = '0,00' in dtb[j].find_element_by_xpath('td/span/table/tfoot/tr/td').text and len(
                        dtb[j].find_elements_by_xpath('td/span/table/tfoot/tr/td'))

                    wait = WebDriverWait(self.browser, 4)
                    wait.until(
                        EC.presence_of_element_located((By.XPATH,
                                                        '//*[@id="fDetalhar:dtbValoresPorData"]/tbody/tr[{}]/td/span/table/tfoot/tr/td'.format(
                                                            str(j + 1)))))
                    if len(dtb[j].find_elements_by_xpath('td/span/table/tbody/tr')) > 1:
                        for k in dtb[j].find_elements_by_xpath('td/span/table/tbody/tr')[:-1]:
                            verde = verde and len(k.find_elements_by_xpath(
                                'td[6]/img')) == 1 and '/processumweb/images/check.gif' in k.find_element_by_xpath(
                                'td[6]/img').get_attribute('src')
                    else:
                        verde = False
                    prc_apto_pgto = prc_apto_pgto and verde
                    # print('prc_apto_pgto->',prc_apto_pgto)
                else:
                    prc_apto_pgto = False

        except:
            self.erroo = True
            self.log_error.insert_log('ERRO- AO COLETA DOS DADOS NA PAGAMENTOS/GARANTIA ')
            return False, None

        return prc_penhora, prc_apto_pgto

    # REALIZA LOGIN
    def login(self, user, password):
        try:
            link_ant = self.browser.current_url
            while True:
                try:
                    self.browser.find_element_by_xpath('//*[@id="username"]').send_keys(user)
                    # self.browser.execute_script("document.getElementById('usuario').value='"+user+"'")

                    self.browser.find_element_by_xpath('//*[@id="password"]').send_keys(password, Keys.RETURN)
                    # self.browser.execute_script("document.getElementById('senha').value='"+password+"'")
                    # sleep(1.5)
                    if link_ant != self.browser.current_url:
                        return True
                    else:
                        continue
                except:
                    continue
        except:
            # print('deu ruim')
            self.log_error.insert_log('Erro no Login')
            return False

    # BUSCA PROCESSO NO PROJUDI
    def find_process(self, prc_sequencial=None):
        try:

            i = 4
            while i:
                i -= 1

                try:
                    if i == 2:
                        try:
                            wait = WebDriverWait(self.browser, 5)
                            wait.until(EC.presence_of_element_located((By.ID, 'subviewMessages: formHeader :msgErro')))
                            return False
                        except:
                            continue
                    self.browser.execute_script("window.open('{}')".format(
                        'https://ww3.vivo-base.com.br/processumweb/modulo/processo/filtro.jsf'))
                    self.browser.close()
                    self.browser.switch_to_window(self.browser.window_handles[0])
                    wait = WebDriverWait(self.browser, 4)
                    wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="fPesquisa:sequencial"]')))
                    self.browser.find_element_by_xpath('//*[@id="fPesquisa:sequencial"]').clear()
                    self.browser.find_element_by_xpath('//*[@id="fPesquisa:sequencial"]').send_keys(prc_sequencial)

                    wait = WebDriverWait(self.browser, 4)
                    wait.until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="fPesquisa:lblBtnFiltrar"]')))
                    self.browser.find_element_by_xpath('//*[@id="fPesquisa:lblBtnFiltrar"]').click()

                    wait = WebDriverWait(self.browser, 4)
                    wait.until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="fPesquisa:dtbProcesso:0:retornoNumSeq"]')))
                    self.browser.find_element_by_xpath('//*[@id="fPesquisa:dtbProcesso:0:retornoNumSeq"]').click()

                    wait = WebDriverWait(self.browser, 5)
                    wait.until(EC.presence_of_element_located((By.ID, 'fDetalhar')))

                    return True
                except:
                    self.browser.execute_script("window.open('{}')".format(
                        'https://ww3.vivo-base.com.br/processumweb/modulo/processo/filtro.jsf'))
                    self.browser.close()
                    self.browser.switch_to_window(self.browser.window_handles[0])
                    continue
            return False
        except:
            return False

    # SITUAÇÃO DO PROCESSO
    @property
    def secret_of_justice(self):
        try:
            return (self.browser.find_element_by_xpath(
                '//*[@id="Partes"]/table[2]/tbody/tr[11]/td[2]/div/strong').text != "NÃO")
        except:
            return False

    # PEGA ANDAMENTOS DO PROCESSO, AS AUDIÊNCIAS E REALIZA OS DOWNLOADS POR ACOMPANHAMENTO
    def acompanhamentos(self, data_update, data_atual, dict_acp_arq_ant, prc_id):
        list_acp_arq = []
        list_aud = []
        list_acp_arq_ant = []
        list_name_urls = []
        dict_acp_arq_ant = dict_acp_arq_ant
        novos_acp = True
        prc_penhora = False

        try:
            # COLETA DE DADOS PARA CRIAÇÃO DOS ACOMPANHAMENTOS E DOWNLOAD DOS ARQUIVOS
            self.browser.find_element_by_xpath('//*[@id="fDetalhar:btAcompanhamento"]').click()
            try:
                wait = WebDriverWait(self.browser, 10)
                wait.until(EC.presence_of_element_located((By.XPATH, 'html/body[2]/form[2]')))
            except:
                self.browser.refresh()
            parte_do_acomp = self.browser.find_elements_by_class_name('tScroller')
            if len(parte_do_acomp):
                parte_do_acomp = parte_do_acomp[0].find_elements_by_xpath('tbody/tr/td')
                tem = True
                tam = len(parte_do_acomp)
            else:
                tem = False
                tam = 2
            j_flag = 0
            for i in range(1, tam):

                # print('', sep=' ', end='3.{}.0'.format(i), flush=True)
                try:
                    wait = WebDriverWait(self.browser, 4)
                    wait.until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="fAcompanhamento:dtbOcorrencia"]/tbody/tr')))

                except:
                    self.log_error.insert_log('ERRO - NA BUSCA DOS ACOMPANHAMENTOS')
                    self.browser.refresh()
                    wait = WebDriverWait(self.browser, 4)
                    wait.until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="fAcompanhamento:dtbOcorrencia"]/tbody/tr')))

                acompanhamentos = self.browser.find_elements_by_xpath(
                    '//*[@id="fAcompanhamento:dtbOcorrencia"]/tbody/tr')
                tam_acompanhamentos = len(acompanhamentos)

                if novos_acp:
                    # print(' ', sep=' ', end='3.{}.1'.format(i), flush=True)
                    aux = self.acp_aud_arq(acompanhamentos=acompanhamentos,
                                           j_flag=j_flag, tam_acompanhamentos=tam_acompanhamentos,
                                           dict_acp_arq_ant={}, data_atual=data_atual,
                                           data_update=data_update, prc_id=prc_id, novo_acp=novos_acp)

                    list_acp_arq += aux[0]
                    list_aud += aux[1]
                    j_flag = aux[2]
                    prc_penhora = prc_penhora or (aux[4] is not None and aux[4])
                    novos_acp = aux[5]
                    # print(' ', sep=' ', end='3.{}.2'.format(i), flush=True)
                    if j_flag < 0:
                        raise
                    list_name_urls += aux[3]

                if not novos_acp:
                    # print(' ', sep=' ', end='3.{}.1'.format(i), flush=True)
                    aux = self.acp_aud_arq(acompanhamentos=acompanhamentos,
                                           j_flag=j_flag, tam_acompanhamentos=tam_acompanhamentos,
                                           dict_acp_arq_ant=dict_acp_arq_ant, data_atual=data_atual,
                                           data_update=data_update, prc_id=prc_id, novo_acp=novos_acp)

                    list_acp_arq_ant += aux[0]
                    j_flag = aux[2]
                    list_name_urls += aux[3]
                    prc_penhora = prc_penhora or (aux[4] is not None and aux[4])
                    # print(' ', sep=' ', end='3.{}.2'.format(i), flush=True)
                    if j_flag < 0:
                        raise

                if tem and i + 1 < len(parte_do_acomp):
                    try:
                        parte_do_acomp = self.browser.find_element_by_class_name('tScroller').find_elements_by_xpath(
                            'tbody/tr/td')
                        parte_do_acomp[i + 1].find_element_by_xpath('a').click()

                        parte_do_acomp = self.browser.find_element_by_class_name('tScroller').find_elements_by_xpath(
                            'tbody/tr/td')
                    except:
                        self.log_error.insert_log('ERRO -NA  ITERAÇÃO  PÁGINAS  DE ACOMPANHAMENTOS/AUDIENCIAS')
                        # raise
                # print(' ', sep=' ', end='3.{}.3'.format(i), flush=True)
                # print('list_name_urls->', len(list_name_urls))
        except:
            self.log_error.insert_log('-NO ACESSO DOS ACOMPANHAMENTOS, ARQUIVOS E AUDIENCIAS')
            self.erroo = True

            return [], [], [], [], prc_penhora

        if len(list_acp_arq):
            try:
              total = len(list_acp_arq) + len(dict_acp_arq_ant.items())
            except:
                total = len(list_acp_arq)
            for i, j in list_acp_arq:
                i.acp_numero = total
                total -= 1
        return list_acp_arq, list_aud, list_acp_arq_ant, list_name_urls, prc_penhora

    # PEGAR ACOMPANHAMENTOS AUDIENCIAS É ARQUIVO
    def acp_aud_arq(self, acompanhamentos, j_flag, tam_acompanhamentos, dict_acp_arq_ant,
                    data_atual, data_update, prc_id, novo_acp):
        list_aud = []
        list_acp_arq = []
        j_finali = 0
        list_name_urls = []
        prc_penhora = False

        try:
            for j in range(j_flag, tam_acompanhamentos):
                j_finali = j
                data = acompanhamentos[j].find_element_by_xpath('td[6]').text
                data_evento = Tools.treat_date(data) if data else None

                if novo_acp and (
                        (data_evento is not None) and (data_update is not None) and data_evento <= data_update):
                    return list_acp_arq, list_aud, j_finali, list_name_urls, prc_penhora, False

                cadastro = acompanhamentos[j].find_element_by_xpath('td[13]').text
                data_cadastro = Tools.treat_date(cadastro) if cadastro else None

                tipo = acompanhamentos[j].find_element_by_xpath('td[9]').text
                tipo = Tools.remove_accents(tipo).upper()

                esp_tipo = acompanhamentos[j].find_element_by_xpath('td[10]').text
                esp_tipo = Tools.remove_accents(esp_tipo).upper()

                prc_penhora = prc_penhora or 'GARANTIA JUDICIAL' in tipo or 'PENHORA ON LINE' in tipo

                key_dict_acp_arq_ant = (data_cadastro, tipo, esp_tipo) if (data_cadastro, tipo,
                                                                           esp_tipo) in dict_acp_arq_ant.keys() else None

                aux_acomp_list = dict_acp_arq_ant.pop(
                    key_dict_acp_arq_ant) if not novo_acp and key_dict_acp_arq_ant is not None else [[], []]

                aux_acomp, arq_list = aux_acomp_list[0], aux_acomp_list[1]
                altera_acp = False
                if not novo_acp and key_dict_acp_arq_ant is None:
                    # print(2.1)
                    continue

                acomp = AcompanhamentoModel(
                    acp_id=aux_acomp[0], acp_plp_id=aux_acomp[1], acp_tipo=aux_acomp[2], acp_esp=aux_acomp[3],
                    acp_data_cumprimento=aux_acomp[4], acp_data_evento=aux_acomp[5], acp_data_prazo=aux_acomp[6],
                    acp_data_cadastro=aux_acomp[7], acp_data=aux_acomp[8], acp_pra_status=aux_acomp[9],
                    acp_prc_id=prc_id, acp_numero=aux_acomp[10]
                ) if not novo_acp else AcompanhamentoModel(acp_prc_id=prc_id)

                list_arq = []
                try:
                    comentarios = acompanhamentos[j].find_elements_by_xpath(
                        'td[1]/table/tbody/tr/td/label/input')
                except:
                    comentarios = []

                if novo_acp or acomp.acp_tipo != tipo:
                    acomp.acp_tipo = tipo
                    altera_acp = altera_acp or True

                if acomp.acp_data_evento != data_evento or novo_acp:
                    acomp.acp_data_evento = data_evento
                    altera_acp = altera_acp or True

                if novo_acp or acomp.acp_esp != esp_tipo:
                    acomp.acp_esp = esp_tipo
                    altera_acp = altera_acp or True

                prazo = acompanhamentos[j].find_element_by_xpath('td[11]').text
                data_prazo = Tools.treat_date(prazo) if prazo else None
                if novo_acp or acomp.acp_data_prazo != data_prazo:
                    acomp.acp_data_prazo = data_prazo
                    altera_acp = altera_acp or True

                cumprimento = acompanhamentos[j].find_element_by_xpath('td[12]').text
                data_cumprimento = Tools.treat_date(cumprimento) if cumprimento else None
                if novo_acp or acomp.acp_data_cumprimento != data_cumprimento:
                    acomp.acp_data_cumprimento = data_cumprimento
                    altera_acp = altera_acp or True

                if novo_acp or acomp.acp_data_cadastro != data_cadastro:
                    acomp.acp_data_cadastro = data_cadastro
                    altera_acp = altera_acp or True

                # COLETA E TRATAMENDO DAS AUDIENCIAS
                if tipo == 'AUDIENCIA' and novo_acp:
                    aux_aud = AudienciaModel(aud_prc_id=prc_id)
                    aux_aud.aud_tipo = esp_tipo
                    aud_data = acompanhamentos[j].find_element_by_xpath('td[8]').text
                    aud_data = aud_data if aud_data else prazo
                    aux_aud.aud_data = Tools.treat_date(aud_data) if aud_data else None
                    aux_aud.aud_status = "DESIGNADA" if (aux_aud.aud_data is None) or (data_atual is None) or (
                            aux_aud.aud_data >= data_atual) else "REALIZADA"
                    list_aud.append(aux_aud)

                # COLETA E TRATAMENDO DOS DOWNLOADS
                acp_pra_status = None
                if tipo in ' APURACAO ' and (esp_tipo in ['EMISSAO 2A VIA DE FATURA',
                                                          'CONTRATO'] or 'RESGATE DE GRAVACAO'.upper() in esp_tipo):
                    if len(comentarios):
                        comentarios[0].click()
                        comentarios = True
                        wait = WebDriverWait(self.browser, 5)
                        wait.until(EC.presence_of_element_located(
                            (By.XPATH, '//*[@id="fAcompanhamento:dtbOcorrencia"]/tbody/tr')))
                        acompanhamentos = self.browser.find_elements_by_xpath(
                            '//*[@id="fAcompanhamento:dtbOcorrencia"]/tbody/tr')
                        try:
                            wait = WebDriverWait(self.browser, 10)
                            wait.until(EC.presence_of_element_located((By.XPATH, 'html/body[2]/form[2]')))
                        except:
                            self.browser.refresh()
                    else:
                        comentarios = False
                    if comentarios:
                        comentarios = self.browser.find_elements_by_xpath(
                            '//*[@id="fAcompanhamento:dtbComentario:tbody_element"]/tr')
                        comentarios.reverse()
                        for k in comentarios:
                            a = k.find_elements_by_xpath('td[7]/a')
                            if len(a):
                                a[0].click()
                                wait = WebDriverWait(self.browser, 5)
                                wait.until(EC.presence_of_element_located((By.ID, 'popupFrameContainer')))
                                self.browser.switch_to.frame(
                                    self.browser.find_element_by_css_selector(
                                        "iframe[name='__jeniaPopupFrameTarget']"))
                                tr = self.browser.find_elements_by_xpath(
                                    '//*[@id="fAnexo:dtbAnexos:tbody_element"]/tr')

                                acp_pra_status = True if len(tr) else False
                                try:

                                    for l in tr:

                                        tp = l.find_element_by_xpath('td/a').text.split('.')
                                        tp_aux = True
                                        for i in arq_list:
                                            if tp[0] in i:
                                                # print('\n\n', tp[0], '<>', i)
                                                tp_aux = False
                                                break

                                        aux = False
                                        tp[-1]= tp[-1].replace(' ','').replace('\n','').replace('\t','')
                                        if (tp[-1].lower() in ['pdf', 'jpg', 'jpeg', 'mp3','wma', 'zip', 'rar', 'gif', 'xlsx','msg'] and (novo_acp or tp_aux))\
                                                or ('RESGATE DE GRAVACAO'.upper() in esp_tipo and  tp[-1].lower() not in ['docx','png']  and (novo_acp or tp_aux)):
                                            list_file_path = [_ for _ in os.listdir(self.path_download_prov)]
                                            arq_list.append(tp)
                                            try:

                                                n_files = len(os.listdir(self.path_download_prov)) + 1

                                                l.find_element_by_xpath('td/a').click()

                                                err = self.wait_download(n_files, self.browser)
                                                if not err:
                                                    try:
                                                        desc_file = l.find_element_by_xpath('td/a').text
                                                    except:
                                                        desc_file = None

                                                    file_downloaded = str()
                                                    for arq in os.listdir(self.path_download_prov) :
                                                        if arq not in list_file_path :
                                                            list_file_path.append(arq)
                                                            file_downloaded = arq
                                                            break

                                                    nome = Tools.convert_base(str(datetime.now()))
                                                    list_name_urls.append((nome, file_downloaded))

                                                    ext = file_downloaded.split('.')[-1]
                                                    nome = nome + '.' + ext

                                                    list_arq.append(
                                                        ProcessoArquivoModel(pra_prc_id=prc_id,
                                                                             pra_nome=nome,
                                                                             pra_acp_id=acomp.acp_id,
                                                                             pra_descricao=desc_file))
                                                else:
                                                    self.log_error.insert_log(
                                                        'Download do arquivo: evento de data{}!'.format(
                                                            data_cadastro))
                                                aux = True
                                            except:

                                                self.log_error.insert_log(
                                                    'Download do arquivo: evento de data {}!'.format(data_cadastro))
                                                # raise

                                        acp_pra_status = acp_pra_status and aux

                                except:
                                    self.log_error.insert_log('Erro-ACOMPANHAMENTOS-DOWNLOADS')
                                    # raise

                                wait = WebDriverWait(self.browser, 5)
                                self.browser.switch_to.default_content()
                                wait.until(EC.element_to_be_clickable((By.XPATH,
                                                                       '//*[@id="popupFrameContainer"]/tbody/tr[1]/td/table/tbody/tr/td[2]/img')))
                                self.browser.find_element_by_xpath(
                                    '//*[@id="popupFrameContainer"]/tbody/tr[1]/td/table/tbody/tr/td[2]/img').click()
                                try:
                                    wait = WebDriverWait(self.browser, 10)
                                    wait.until(EC.presence_of_element_located((By.XPATH, 'html/body[2]/form[2]')))
                                except:
                                    self.browser.refresh()



                if acomp.acp_pra_status != acp_pra_status:
                    acomp.acp_pra_status = acp_pra_status
                    altera_acp = altera_acp or True

                if altera_acp or len(list_arq):
                    # if not novo_acp and len(list_arq): print('altera_acp->', acomp.__dict__, '\n\n')
                    list_acp_arq.append((acomp, list_arq))

        except:
            self.log_error.insert_log(
                'NA COLETA DOS ACOMPANHAMENTOS, ARQUIVOS E AUDIENCIAS {}'.format('NOVOS' if novo_acp else "ANTIGOS"))
            return [], [], -1, [], False, novo_acp

        # print(list_name_urls)
        return list_acp_arq, list_aud, j_finali, list_name_urls, prc_penhora, novo_acp

    # TRATAR ESTADOS
    @staticmethod
    def tratar_estado(estado):
        estado_sigla = {
            'ACRE': 'AC', 'ALAGOAS': 'AL',
            'AMAPA': 'AP', 'AMAZONAS': 'AM',
            'BAHIA': 'BA', 'DISTRITO FEDERAL': 'DF',
            'CEARÁ': 'CE', 'ESPÍRITO SANTO': 'ES',
            'GOIAS': 'GO', 'MARANHAO': 'MA',
            'MATO GROSSO': 'MT', 'MATO GROSSO DO SUL': 'MS',
            'MINAS GERAIS': 'MG', 'PARAIBA': 'PB',
            'PARANA': 'PR', 'PARA': 'PA',
            'PERNAMBUCO': 'PE', 'PIAUI': 'PI',
            'RIO DE JANEIRO': 'RJ', 'RIO GRANDE DO NORTE': 'RN',
            'RIO GRANDE DO SUL': 'RS', 'RONDONIA': 'RO',
            'RORAIMA': 'RR', 'SANTA CATARINA': 'SC',
            'SAO PAULO': 'SP', 'SERGIPE': 'SE', 'TOCANTINS': 'TO'
        }
        for i in estado_sigla.items():
            if i[0] in estado:
                return i[-1]


