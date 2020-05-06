from Database.connDatabase import SQL
from Model.toolsModel import *


class RootModel:
    def __init__(self, site, mode_execute, SQL_Long, platform_id, platform_name, estado='Default', grau='DefaultGrau'):

        self.path_download_prov = os.path.abspath('../Downloads/' + estado + '/' + platform_name + '/' +str(grau)+'/Download' + str(hex(id(self))))
        Tools.new_path(str(self.path_download_prov))
        self.site = site
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_experimental_option("prefs",
                                                    {"download.default_directory": r"" + str(self.path_download_prov),
                                                     "download.prompt_for_download": False,
                                                     "download.directory_upgrade": True,
                                                     "safebrowsing.enabled": False,
                                                     "safebrowsing_for_trusted_sources_enabled": False,
                                                     'download.extensions_to_open': 'msg',
                                                     "plugins.always_open_pdf_externally": True})

        if not mode_execute:
            self.chrome_options.add_argument("headless")
            self.chrome_options.add_argument("safebrowsing-disable-download-protection")
            self.chrome_options.add_argument("safebrowsing-disable-extension-blacklist")


        self.browser = None
        self.Access_AQL = SQL_Long
        self.platform_id = platform_id
        self.platform_name = platform_name

    def __del__(self):
        Tools.delete_path(self.path_download_prov)

    # ABRE O NAVEGADOR PARA INICIAR AS BUSCAS
    def init_browser(self):
        try:
            self.browser = webdriver.Chrome('../WebDriver/chromedriver.exe', options=self.chrome_options)
            # self.browser = webdriver.Chrome('C:/Users/Administrador.AGECOB049/Desktop/bighero-python/WebDriver/chromedriver.exe', options=self.chrome_options)

            # self.browser.maximize_window()
            # self.browser.minimize_window()
            self.browser.get(self.site)

            return True
        except:
            raise
            return False



    # LIMPA A PASTA DE  DOWNLOAD TEMPORÁRIA
    def clear_path_download(self):
        Tools.delete_path(self.path_download_prov)
        Tools.new_path(self.path_download_prov)

    # ATUALIZAÇÃO DA DATA NA TABELA PLATAFORMA_ESTADO
    def update_ple_data(self, ple_plt_id, ple_uf):
        database = SQL(self.Access_AQL[0], self.Access_AQL[1], self.Access_AQL[2])
        database.update_ple_data_db(ple_plt_id, ple_uf)

    # EXPORTA OS DADOS DO OBJETO DO PROCESSUM PARA O BANCO DE DADOS
    def export_to_database_processum(self, objects, list_name_urls, log, root, state):
        print('###Transferindo arquivos e exportando objetos para o banco de dados...'.upper())
        database = SQL(self.Access_AQL[0], self.Access_AQL[1], self.Access_AQL[2])

        for obj in objects:
            prc_carteira = obj[0].prc_carteira
            prc_carteira = database.key_crt(prc_carteira)
            obj[0].prc_carteira = prc_carteira
            if obj[-1] is None and obj[-2] is None:
                database.insert_processum(obj=obj, list_name_urls=list_name_urls, log=log,
                                          root=root, state=state)


            else:
                database.update_processum(obj=obj, list_name_urls=list_name_urls, log=log,
                                          root=root, state=state)
        database.__del__()

    # EXPORTA OS DADOS DO OBJETO PARA O BANCO DE DADOS
    def export_to_database(self, objects, log, list_name_urls, platform, state, root):
        print('###Transferindo arquivos e exportando objetos para o banco de dados...'.upper())
        database = SQL(self.Access_AQL[0], self.Access_AQL[1], self.Access_AQL[2])
        for obj in objects:
            if obj[5] is None:
                database.insert_process(obj=obj, log=log, list_name_urls=list_name_urls,
                                        platform=platform, state=state, root=root)
            else:
                database.update_process(obj=obj, log=log, list_name_urls=list_name_urls,
                                        platform=platform, state=state, root=root)
        database.__del__()

    # AGUARDA DOWNLOAD DO ARQUIVO BAIXADO
    def wait_download(self, n_files, browser=None):
        print('', sep=' ', end='.', flush=True)
        not_finish = True
        err = False
        val_1 = 0
        val_2 = time.time()
        while not_finish:  # AGUARDA FINALIZAR O DOWNLOAD DO ARQUIVO
            val_1 += 1
            try:
                if len(browser.window_handles) == 0:
                    if browser is not None:
                        browser.quit()
                        err = True
                        break
            except:
                err = True
                break
            try:
                if n_files <= len(os.listdir(self.path_download_prov)):
                    for file in os.listdir(self.path_download_prov):
                        if time.time() - val_2 >= 60:
                            not_finish = False
                            err = True
                            break
                        if file.endswith('.crdownload') or file.endswith('.tmp'):
                            not_finish = True
                            break
                        elif str(file) == str(os.listdir(self.path_download_prov)[-1]):
                            not_finish = False
                        elif val_1 >= 500:
                            not_finish = False
                            err = True
                            break
                elif val_1 >= 500:
                    err = True
                    break
            except FileNotFoundError:
                err = True

                break
        try:
          if err:
              Tools.delete_file(self.path_download_prov)
              print('', sep='', end=':', flush=True)
        except:
          print('', sep='', end=',', flush=True)


        return err

    # TRANSFERE OS ARQUIVOS BAIXADOS PARA O PATH
    def transfer_files(self, state, list_name_urls, plp_id, log):
        # CRIA PATH PARA TRANSFERÊNCIA DOS ANEXOS
        if len(list_name_urls) > 0:
            Tools.new_path('../Downloads/' + state + '/' + self.platform_name + '/' + str(plp_id))
            path_proc = os.path.abspath('../Downloads/' + state + '/' + self.platform_name + '/' + str(plp_id))
            # VERIFICA SE OS DOWNLOADS FORAM FINALIZADOS
            for new_name, old_name in list_name_urls:
                Tools.transfer_and_rename_files(old_name, new_name, self.path_download_prov, path_proc, log)
        self.clear_path_download()
        print('\t- Transferência dos arquivos finalizada'.upper())


class PjeModel1Grau(RootModel):
    def __init__(self, site, mode_execute, SQL_Long, platform_id, platform_name, state,num_thread,link_consulta,flag,grau='1Grau'):
        self.num_thread = num_thread
        self.grau = grau
        self.flag = flag
        self.state = state
        self.link_consulta = link_consulta
        # self.log_error = LogErrorModelMutlThread(platform_name=platform_name, state=self.state,
        #                                          num_thread=self.num_thread, grau=self.grau)
        super().__init__(site, mode_execute, SQL_Long, platform_id, platform_name, state,grau)

    # VALIDA A INICIALIZAÇÃO DA VARREDURA NA PLATAFORMA
    def initializer(self):
        while True:
            # INICIALIZA BROWSER
            if self.init_browser():
                # LOGIN NA PLATAFORMA
                if self.login():
                    break
            if self.browser is not None:
                self.browser.quit()

        # VERIFICA CADA NÚMERO DE PROCESSO RETORNADO DO BANCO DE DADOS NA PLATAFORMA

    def check_process(self, n_proc, prc_id, plp_id, plp_data_update, log, state):
        # if not self.find_process(n_proc):
        #     log.insert_info('Processo não encontrado!')
        #
        #     process_platform = ProcessoPlataformaModel(plp_prc_id=prc_id, plp_plt_id=self.platform_id,
        #                                                plp_numero=n_proc, plp_segredo=False,
        #                                                plp_localizado=False) if plp_data_update is None else ProcessoPlataformaModel(
        #         plp_prc_id=prc_id, plp_plt_id=self.platform_id,
        #         plp_numero=n_proc, plp_segredo=False)
        #
        #     list_objects_process = [(process_platform, [], [], [], [], plp_id,[])]
        #
        #     # INSERE A LISTA DE OBJETOS NO BANCO DE DADOS
        #     self.export_to_database(objects=list_objects_process, log=log, list_name_urls=[],
        #                             platform=self.platform_name, state=state, root=self)
        #     return True
        #
        # # VERIFICA SE O PROCESSO ESTÁ EM SEGREDO DE JUSTIÇA
        # if self.secret_of_justice:
        #     log.insert_info('Processo em segredo de justiça!')
        #
        #     process_platform = ProcessoPlataformaModel(plp_prc_id=prc_id, plp_plt_id=self.platform_id,
        #                                                plp_numero=n_proc, plp_segredo=True, plp_localizado=True)
        #     list_objects_process = [(process_platform, [], [], [], [], plp_id,[])]
        #
        #     # INSERE A LISTA DE OBJETOS NO BANCO DE DADOS
        #     self.export_to_database(objects=list_objects_process, log=log, list_name_urls=[],
        #                             platform=self.platform_name, state=state, root=self)
        #     return True
        pass


        return False

        # BUSCA PELO PROCESSO NA PLATAFORMA

    def busca_processo_na_plataforma(self, n_proc, i_proc, t0, log, state):
        # if i_proc[8] is None:  # PESQUISA PELO NÚMERO DE PROCESSO DA TABELA PROCESSO
        #     if len(n_proc) is 20:
        #         if self.check_process(n_proc=n_proc, prc_id=i_proc[1], plp_id=i_proc[7], plp_data_update=i_proc[6],
        #                               log=log, state=state):
        #             print('###Tempo total da coleta de dados do processo: {} SECS'.format(time.time() - t0).upper())
        #             print('-' * 65)
        #             return True
        #     elif len(n_proc) < 20:
        #         n_proc = '0' * (20 - len(n_proc)) + n_proc
        #         if self.check_process(n_proc=n_proc, prc_id=i_proc[1], plp_id=i_proc[7],
        #                               plp_data_update=i_proc[6], log=log, state=state):
        #             print('###Tempo total da coleta de dados do processo: {} SECS'.format(time.time() - t0).upper())
        #             print('-' * 65)
        #             return True
        #     else:
        #         while int(n_proc[0]) is 0 and len(n_proc) is not 20:
        #             n_proc = n_proc[1:]
        #         if self.check_process(n_proc=n_proc, prc_id=i_proc[1], plp_id=i_proc[7], plp_data_update=i_proc[6],
        #                               log=log, state=state):
        #             print('###Tempo total da coleta de dados do processo: {} SECS'.format(time.time() - t0).upper())
        #             print('-' * 65)
        #             return True
        # else:  # PESQUISA PELO NUMERO DO PROCESSO CONTIDO NA PLATAFORMA
        #     if self.check_process(n_proc=n_proc, prc_id=i_proc[1], plp_id=i_proc[7], plp_data_update=i_proc[6], log=log,
        #                           state=state):
        #         print('###Tempo total da coleta de dados do processo: {} SECS'.format(time.time() - t0).upper())
        #         print('-' * 65)
        #         return True
        # return False
        pass
    # REALIZA LOGIN
    def login(self):
        try:
            wait = WebDriverWait(self.browser, 30)
            self.browser.find_element_by_xpath('//*[@id="loginAplicacaoButton"]').click()
            wait.until(EC.visibility_of_element_located((By.ID, 'home')))
            return True
        except:
            return False

    # BUSCA PROCESSO NO PROJUDI
    def find_process(self, prc_numero):
        # try:
        #     self.browser.get(self.link_consulta)
        #     self.browser.find_element_by_xpath('//*[@id="fPP:numeroProcesso:numeroSequencial"]').send_keys(
        #         prc_numero[:7])
        #     self.browser.find_element_by_xpath('//*[@id="fPP:numeroProcesso:numeroDigitoVerificador"]').send_keys(
        #         prc_numero[7:9])
        #     self.browser.find_element_by_xpath('//*[@id="fPP:numeroProcesso:Ano"]').send_keys(prc_numero[9:13])
        #     self.browser.find_element_by_xpath('//*[@id="fPP:numeroProcesso:labelTribunalRespectivo"]').send_keys(
        #         prc_numero[14:16])
        #     self.browser.find_element_by_xpath('//*[@id="fPP:numeroProcesso:NumeroOrgaoJustica"]').send_keys(
        #         prc_numero[16:], Keys.RETURN)
        #     wait = WebDriverWait(self.browser, 4)
        #     wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="fPP:processosTable:tb"]/tr/td[1]/a')))
        #     self.browser.find_element_by_xpath('//*[@id="fPP:processosTable:tb"]/tr/td[1]/a').click()
        #     try:
        #         wait = WebDriverWait(self.browser, 4)
        #         wait.until(EC.alert_is_present())
        #         alert = self.browser.switch_to_alert()
        #         alert.accept()
        #     except:
        #         pass
        #
        #     try:
        #         self.browse.switch_to_alert().accept()
        #     except:
        #         pass
        #
        #     return True

        # except:
        #     return False
         pass

    # SITUAÇÃO DO PROCESSO
    @property
    def secret_of_justice(self):
        # try:
        #     return (self.browser.find_element_by_xpath(
        #         '//*[@id="Partes"]/table[2]/tbody/tr[11]/td[2]/div/strong').text != "NÃO")
        # except:
        #     return False
        pass

    # PEGA OS ENVOLVIDOS E RETORNA UMA LISTA COM AS PARTES E OS ADVOGADOS/JUIZ
    @property
    def envolvidos(self):
        # list_partes = []
        # list_advogs = []
        # try:
        #     # PARTE ATIVA
        #     partes_ativas = self.browser.find_elements_by_xpath('//*[@id="poloAtivo"]/table/tbody/tr')
        #     for i in range(len(partes_ativas)):
        #         try:
        #
        #             td_split = partes_ativas[i].find_element_by_xpath('td/span').text
        #             td_split = td_split.split(' - ')
        #             nome_parte_ativa = td_split[0]
        #             cpf_cnpj_ativa = re.sub('[^0-9.]', '', td_split[-1])
        #             list_partes.append((ParteModel(prt_nome=nome_parte_ativa,
        #                                            prt_cpf_cnpj=cpf_cnpj_ativa), 'Ativo'))
        #             # print('parte ativa:', nome_parte_ativa, '- cpf:', cpf_cnpj_ativa)
        #
        #             # RESPONSÁVEIS ATIVOS
        #             resp_ativo = partes_ativas[i].find_elements_by_xpath('td/ul/li')
        #             for j in range(len(resp_ativo)):
        #                 try:
        #                     try:
        #                         td_split = resp_ativo[j].find_element_by_xpath('small/span').text.split(' - ')
        #                         nome_responsavel_ativo = td_split[0]
        #                         oab_responsavel_ativo = td_split[1].replace('OAB ', '').upper()
        #
        #                     except:
        #                         nome_responsavel_ativo = resp_ativo[j].find_element_by_xpath('small/span'
        #                                                                                      '').text.split(' - ')[0]
        #                         oab_responsavel_ativo = self.state.upper()
        #
        #                     list_advogs.append((ResponsavelModel(rsp_nome=nome_responsavel_ativo.upper(),
        #                                                          rsp_tipo='Advogado(a)',
        #                                                          rsp_oab=oab_responsavel_ativo,), 'Ativo'))
        #                     # print('responsavel ativo:', nome_responsavel_ativo, 'OAB -', oab_responsavel_ativo)
        #
        #                 except:
        #                     self.log_error.insert_log('coleta de dados do responsável ativo!')
        #         except:
        #             raise
        #             self.log_error.insert_log('coleta de dados da parte ativa!')
        #
        #     # PARTE PASSIVA
        #     partes_passivas = self.browser.find_elements_by_xpath('//*[@id="poloPassivo"]/table/tbody/tr')
        #     for i in range(len(partes_passivas)):
        #         try:
        #             td_split = partes_passivas[i].find_element_by_xpath('td/span').text
        #             td_split = td_split.split(' - ')
        #             nome_parte_passiva = td_split[0]
        #             cpf_cnpj_passiva = re.sub('[^0-9./]', '', td_split[-1])
        #             list_partes.append((ParteModel(prt_nome=nome_parte_passiva,
        #                                            prt_cpf_cnpj=cpf_cnpj_passiva), 'Passivo'))
        #             # print('parte passiva:', nome_parte_passiva, '- cpf:', cpf_cnpj_passiva)
        #
        #             # RESPONSÁVEIS PASSIVOS
        #             resp_passivo = partes_passivas[i].find_elements_by_xpath('td/ul/li')
        #             for j in range(len(resp_passivo)):
        #                 try:
        #                     try:
        #                         td_split = resp_passivo[j].find_element_by_xpath('small/span').text.split(' - ')
        #                         nome_responsavel_passivo = td_split[0]
        #                         oab_responsavel_passivo = td_split[1].replace('OAB ', '').upper()
        #                     except:
        #                         nome_responsavel_passivo = resp_passivo[j].find_element_by_xpath('small/span'
        #                                                                                          '').text.split(' - ')[
        #                             0]
        #                         oab_responsavel_passivo = self.state.upper()
        #
        #                     list_advogs.append((ResponsavelModel(rsp_nome=nome_responsavel_passivo,
        #                                                          rsp_tipo='Advogado(a)',
        #                                                          rsp_oab=oab_responsavel_passivo), 'Passivo'))
        #                     # print('responsavel passiva:', nome_responsavel_passivo, 'OAB -', oab_responsavel_passivo)
        #
        #                 except:
        #                     self.log_error.insert_log('coleta de dados do responsável passivo!')
        #         except:
        #             raise
        #             self.log_error.insert_log('coleta de dados da parte passiva!')
        # except:
        #     list_partes.clear()
        #     list_advogs.clear()
        #     self.log_error.insert_log('coleta de dados dos envolvidos no processo!')
        #     raise
        #
        # return list_partes, list_advogs
        pass

    # SELECIONA PROCESSOS DO BANCO DE DADOS E PROCURA NA PLATAFORMA PARA UPDATE NO BANCO
    def search_process_to_update(self, row_database, dict_plp_2grau):

        # # INICIA O BROWSER E A SESSÃO NA PLATAFORMA
        # self.initializer()
        #
        # # VERIFICA CADA NUMERO DE PROCESSO DENTRO DA ESTRUTURA FORNECIDA
        # i_n = 0
        # for i_proc in row_database:
        #     try:
        #         t0 = time.time()
        #         i_n += 1
        #         list_2_grau = dict_plp_2grau[i_proc[1]]
        #         list_plp_2_grau = []
        #
        #         # VERIFICA SE O NAVEGADOR ESTÁ ABERTO
        #         try:
        #             if len(self.browser.window_handles) > 1:
        #                 if self.browser is not None:
        #                     self.browser.quit()
        #                     self.log_error.insert_log('Sessão encerrou!')
        #                     return -1
        #         except:
        #             self.log_error.insert_log('navegador fechou!')
        #             return -1
        #
        #
        #
        #         n_proc = i_proc[0]
        #         n_proc = re.sub('[^0-9]', '', n_proc)
        #         list_name_urls = []
        #         self.log_error.insert_title(n_proc)
        #         print("\t{}ª: Coleta de dados do processo: {}".format(i_n, n_proc).upper())
        #         try:
        #
        #             wait = WebDriverWait(self.browser, 10)
        #             wait.until(
        #                 EC.presence_of_element_located((By.ID, 'popupAlertaCertificadoProximoDeExpirarContentDiv')))
        #
        #             self.browser.find_element_by_xpath(
        #                 '//*[@id="popupAlertaCertificadoProximoDeExpirarContentDiv"]/div/form/span/i').click()
        #
        #         except:
        #
        #             pass
        #
        #         # BUSCA PELO PROCESSO NA PLATAFORMA
        #         if self.busca_processo_na_plataforma(n_proc, i_proc, t0, self.log_error, self.state):
        #                 continue
        #
        #         # self.browser.switch_to_window(self.browser.window_handles[0])
        #         # sleep(10)
        #         self.browser.switch_to_window(self.browser.window_handles[-1])
        #
        #         # COLETA OS ACOMPANHAMENTOS DO PROCESSO
        #         list_aud, list_acp_pra, list_name_urls, bool_2_grau_numero, err1, not_refresh = self.acomp_down_aud(i_proc[1], i_proc[4], i_proc[0])
        #         try:
        #
        #             if bool_2_grau_numero and i_proc[0] not in list_2_grau:
        #                 list_plp_2_grau = [
        #                     ProcessoPlataformaModel(plp_prc_id=i_proc[1], plp_plt_id=5,
        #                                             plp_numero=i_proc[0], plp_grau=2, plp_processo_origem=i_proc[0])
        #
        #                 ]
        #         except:
        #             self.log_error.insert_log('coleta dos numeros do processo do 2 grau!'.upper())
        #
        #         if not err1 and (self.flag or not_refresh is not 1):
        #             # PEGA DADOS DO PROCESSO E ATUALIZA TABELA
        #             try:
        #                 wait = WebDriverWait(self.browser, 10)
        #                 wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="navbar"]/ul/li/a[1]')))
        #                 self.browser.find_element_by_xpath('//*[@id="navbar"]/ul/li/a[1]').click()
        #                 wait = WebDriverWait(self.browser, 10)
        #                 wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'dl-horizontal')))
        #                 try:
        #                     juizo = self.browser.find_element_by_xpath(
        #                         '//*[@id="maisDetalhes"]/div[1]/dl/dd').text.upper()
        #                     juizo = Tools.remove_accents(juizo)
        #                 except:
        #                     juizo = None
        #                 try:
        #                     classe = self.browser.find_element_by_xpath('//*[@id="maisDetalhes"]/dl/dd[1]').text.upper()
        #                     classe = Tools.remove_accents(classe)
        #                 except:
        #                     classe = None
        #                 try:
        #                     assunto = self.browser.find_element_by_xpath('//*[@id="maisDetalhes"]/dl/dd[2]/ul/'
        #                                                                  'li[1]').text.upper()
        #                     assunto = Tools.remove_accents(assunto)
        #                 except:
        #                     assunto = None
        #                 try:
        #                     status = self.browser.find_element_by_xpath('//*[@id="VisualizaDados"]/fieldset[3]/'
        #                                                                 'span[11]').text.upper()
        #                     if 'ARQUIVADO DEFINITIVAMENTE' in status or 'ARQUIVADO' in status or 'BAIXADO' in status:
        #                         status = 'ARQUIVADO'
        #                     else:
        #                         status = 'ATIVO'
        #                 except:
        #                     status = None
        #                 try:
        #                     valor_causa = self.browser.find_element_by_xpath('//*[@id="maisDetalhes"]/dl/dd[6]').text
        #                     valor_causa = Tools.treat_value_cause(valor_causa)
        #                 except:
        #                     valor_causa = None
        #                 try:
        #                     dt_distribuicao = self.browser.find_element_by_xpath('//*[@id="maisDetalhes"]/dl/'
        #                                                                          'dd[5]').text.lower()
        #                     dt_distribuicao = Tools.remove_accents(dt_distribuicao)
        #                     dt_distribuicao = Tools.treat_date(dt_distribuicao)
        #                 except:
        #                     dt_distribuicao = None
        #             except:
        #                 juizo, classe, assunto, valor_causa, dt_distribuicao, status = None, None, None, None, None, None
        #
        #             # IDENTIFICA OS ENVOLVIDOS E RETORNA UMA LISTA COM AS PARTES E OS ADVOGADOS/JUIZ
        #             wait = WebDriverWait(self.browser, 10)
        #             wait.until(EC.visibility_of_element_located((By.ID, 'poloAtivo')))
        #             wait.until(EC.visibility_of_element_located((By.ID, 'poloPassivo')))
        #             list_partes, list_advogs = self.envolvidos
        #
        #             # CRIA O OBJETO PROCESSO-PLATAFORMA QUE SERÁ INSERIDO NO BANCO DE DADOS
        #             process_platform = ProcessoPlataformaModel(plp_prc_id=i_proc[1], plp_plt_id=self.platform_id,
        #                                                        plp_numero=n_proc, plp_status=status, plp_juizo=juizo,
        #                                                        plp_valor_causa=valor_causa, plp_classe=classe,
        #                                                        plp_grau=2,
        #                                                        plp_assunto=assunto,
        #                                                        plp_data_distribuicao=dt_distribuicao,
        #                                                        plp_segredo=False, plp_localizado=True)
        #             self.browser.close()
        #             self.browser.switch_to_window(self.browser.window_handles[0])
        #             list_objects_process = [(process_platform, list_partes, list_advogs, list_aud, list_acp_pra,
        #                                      i_proc[7], list_plp_2_grau)]
        #
        #             # INSERE A LISTA DE OBJETOS NO BANCO DE DADOS
        #             self.export_to_database(objects=list_objects_process, log=self.log_error,
        #                                     list_name_urls=list_name_urls,
        #                                     platform=self.platform_name, state=self.state, root=self)
        #
        #             self.log_error.insert_info('Procedimento finalizado!')
        #         elif not err1:
        #             # CRIA O OBJETO PROCESSO-PLATAFORMA QUE SERÁ INSERIDO NO BANCO DE DADOS
        #             process_platform = ProcessoPlataformaModel(plp_prc_id=i_proc[1], plp_plt_id=self.platform_id,
        #                                                        plp_numero=n_proc, plp_segredo=False,
        #                                                        plp_localizado=True)
        #
        #             self.browser.close()
        #             self.browser.switch_to_window(self.browser.window_handles[0])
        #             list_objects_process = [
        #                 (process_platform, [], [], list_aud, list_acp_pra, i_proc[7], list_plp_2_grau)]
        #
        #             # INSERE A LISTA DE OBJETOS NO BANCO DE DADOS
        #             self.export_to_database(objects=list_objects_process, log=self.log_error,
        #                                     list_name_urls=list_name_urls,
        #                                     platform=self.platform_name, state=self.state, root=self)
        #
        #             self.log_error.insert_info('Procedimento finalizado!')
        #         else:  # SENÃO FAZ UMA NOVA BUSCA
        #             # LIMPA A PASTA PARA RECEBER OS NOVOS DOWNLOADS
        #             self.browser.close()
        #             self.browser.switch_to_window(self.browser.window_handles[0])
        #             self.clear_path_download()
        #
        #         print('###Tempo total da coleta de dados do processo: {} SECS'.format(time.time() - t0).upper())
        #         print('-' * 65)
        #     except:
        #         raise
        #         return -1
        #
        # # VERIFICA SE O NAVEGADOR FECHOU, SENÃO O FECHA
        # if self.browser is not None:
        #     self.browser.quit()
        #
        # # VERIFICA SE NÃO RETORNOU ALGUM PROCESSO DA BASE, SENÃO ATUALIZA A PLE_DATA
        # self.update_ple_data(ple_plt_id=self.platform_id, ple_uf=self.state)
        #
        # return i_n
        pass

    # REALIZA O DOWNLOAD DO ARQUIVO
    def check_download(self, acp, prc_id, n_event, file_downloaded, list_name_urls, list_file_name, list_file_path):
        # err = False
        # try:
        #     wait = WebDriverWait(self.browser, 60)
        #     wait.until(EC.invisibility_of_element((By.ID, '_viewRoot:status.start')))
        #
        #     n_files = len(os.listdir(self.path_download_prov)) + 1
        #
        #     button_download = acp.find_element_by_xpath('//*[@id="detalheDocumento:download"]')
        #     webdriver.ActionChains(self.browser).move_to_element(button_download).click(button_download).perform()
        #
        #     wait = WebDriverWait(self.browser, 10)
        #     wait.until(EC.alert_is_present())
        #     alert = self.browser.switch_to_alert()
        #     alert.accept()
        #     self.browser.switch_to_default_content()
        #
        #     err_down = self.wait_download(n_files, self.browser)
        #     try:  # VERIFICA SE A SESSÃO FOI ENCERRADA
        #         if len(self.browser.window_handles) > 2:
        #             if self.browser is not None:
        #                 self.browser.quit()
        #     except:
        #         self.log_error.insert_log('Download do arquivo: evento {}!'.format(n_event))
        #         err = True
        #
        #     if not err_down:
        #         for arq in os.listdir(self.path_download_prov):
        #             if arq not in list_file_path:
        #                 list_file_path.append(arq)
        #                 file_downloaded = arq
        #                 break
        #
        #         desc_file = file_downloaded.split('.')[0]
        #         nome = Tools.convert_base(str(datetime.now()))
        #         list_name_urls.append((nome, file_downloaded))
        #         ext = file_downloaded.split('.')[-1].lower()
        #         nome = nome + '.' + ext
        #         list_file_name.append(ProcessoArquivoModel(pra_prc_id=prc_id,
        #                                                    pra_nome=nome,
        #                                                    pra_descricao=desc_file))
        #         acp_pra_status = True
        #     else:
        #         self.log_error.insert_log('Download do arquivo: evento {}!'.format(n_event))
        #         acp_pra_status = False
        # except:
        #     self.log_error.insert_log('Download do arquivo: evento {}!'.format(n_event))
        #     acp_pra_status = False
        #
        # return acp_pra_status, err, list_file_name

        # PEGA ANDAMENTOS DO PROCESSO, AS AUDIÊNCIAS E REALIZA OS DOWNLOADS POR ACOMPANHAMENTO

   # PEGA ANDAMENTOS DO PROCESSO, AS AUDIÊNCIAS E REALIZA OS DOWNLOADS POR ACOMPANHAMENTO
        pass
    def acomp_down_aud(self, prc_id, ult_mov,n_proc):

        # list_acomp_download = []
        # file_downloaded = None
        # desc_process = None
        # aux_data = None
        # bool_2_grau_numero=False
        # list_file_path = []
        # list_audiences = []
        # list_name_urls = []
        # not_refresh = 0
        # err = False
        # t = 0
        # k = 0
        # try:
        #     load = 0
        #     while True:
        #         wait = WebDriverWait(self.browser, 60)
        #         wait.until(EC.invisibility_of_element((By.ID, '_viewRoot:status.start')))
        #
        #         acompanhamentos = self.browser.find_elements_by_xpath('//*[@id="divTimeLine:divEventosTimeLine"]/div')[:-1]
        #
        #         if not load == len(acompanhamentos):
        #             load += 1
        #             eula = self.browser.find_element_by_id('divTimeLine:divEventosTimeLine')
        #             self.browser.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', eula)
        #         else:
        #             eula = self.browser.find_element_by_id('divTimeLine:divEventosTimeLine')
        #             self.browser.execute_script('arguments[0].scrollTop = 0', eula)
        #             break
        #
        #
        #     try:
        #         wait = WebDriverWait(self.browser, 60)
        #         wait.until(
        #             EC.visibility_of_all_elements_located((By.XPATH, '//*[@id="navbar:ajaxPanelAlerts"]/ul/li[3]')))
        #
        #
        #         self.browser.find_element_by_xpath('//*[@id="navbar:ajaxPanelAlerts"]/ul/li[3]/a').click()
        #         wait.until(EC.visibility_of_all_elements_located((By.XPATH, '//*[@id="navbar:ajaxPanelAlerts"]/ul/'
        #                                                                     'li[3]/ul/div/li')))
        #
        #         self.browser.find_element_by_id('navbar:linkAbaAudiencia').click()
        #         wait = WebDriverWait(self.browser, 60)
        #         wait.until(EC.invisibility_of_element((By.ID, '_viewRoot:status.start')))
        #         audiences = self.browser.find_elements_by_xpath('//*[@id="processoConsultaAudienciaGridList:tb"]/tr')
        #         for audience in audiences:
        #             aux = ''
        #             aux += audience.find_element_by_xpath('td[2]').text + ' '
        #             aux += audience.find_element_by_xpath('td[4]').text + ' para '
        #             aux += audience.find_element_by_xpath('td[1]').text
        #             aux = Tools.remove_accents(aux).split(' (')[0]
        #             list_audiences.append(aux.upper())
        #         wait = WebDriverWait(self.browser, 60)
        #         self.browser.find_element_by_xpath('//*[@id="navbar:ajaxPanelAlerts"]/ul/li[3]/a').click()
        #         wait.until(EC.visibility_of_element_located((By.ID, 'navbar:linkAbaAutos')))
        #         self.browser.find_element_by_id('navbar:linkAbaAutos').click()
        #
        #     except (TimeoutException, NoSuchElementException, ElementClickInterceptedException):
        #         self.log_error.insert_log('coleta de audiências!')
        #
        #     wait = WebDriverWait(self.browser, 60)
        #     wait.until(EC.invisibility_of_element((By.ID, '_viewRoot:status.start')))
        #
        #     acompanhamentos = self.browser.find_elements_by_xpath('//*[@id="divTimeLine:divEventosTimeLine"]/div')[:-1]
        #
        #     for i in range(k, len(acompanhamentos)):
        #         n_event = len(acompanhamentos) - i
        #         k += 1
        #         if len(acompanhamentos[i].find_elements_by_xpath('div')) == 1:
        #             try:
        #                 aux_data = acompanhamentos[i].find_element_by_xpath('div/span').text
        #                 aux_data = Tools.treat_date(aux_data)
        #             except ValueError:
        #                 pass
        #
        #         else:
        #             if ult_mov is not None:
        #                 not_refresh += 1
        #                 if aux_data <= ult_mov:
        #                     break
        #
        #             list_file_name = []
        #             acp_pra_status = False
        #
        #             if len(acompanhamentos[i].find_elements_by_xpath('div[2]/div')) == 2:
        #                 try:
        #                     desc_process = acompanhamentos[i].find_element_by_xpath('div[2]/span').text.upper()
        #                     desc_process = Tools.remove_accents(desc_process)
        #
        #                     try:
        #                         if 'REMETIDOS OS AUTOS (EM GRAU DE RECURSO) PARA' in desc_process:
        #                             bool_2_grau_numero = True
        #                             # print("foi meu rei")
        #                     except:
        #                         bool_2_grau_numero = False
        #                         self.log_error.insert_log('coleta dos numeros do processo do 2 grau!'.upper())
        #
        #
        #                     # PEGA AS AUDIÊNCIAS
        #                     audiences = desc_process.split(' ')
        #                     if 'AUDIENCIA' in audiences[0]:
        #                         list_audiences.append(desc_process.split('AUDIENCIA ')[-1])
        #                 except:
        #                     try:
        #                         acompanhamentos[i].find_element_by_xpath('div[2]/div[1]/a').click()
        #                         t += 1
        #                         wait = WebDriverWait(self.browser, 60)
        #                         wait.until(EC.invisibility_of_element((By.ID, '_viewRoot:status.start')))
        #
        #                         acp_pra_status, err, list_file_name = \
        #                             self.check_download(acp=acompanhamentos[i], prc_id=prc_id, n_event=n_event,
        #                                                 file_downloaded=file_downloaded, list_name_urls=list_name_urls,
        #                                                 list_file_name=list_file_name, list_file_path=list_file_path)
        #
        #                         sub_files = acompanhamentos[i].find_elements_by_xpath('div[2]/div[1]/ul/li')
        #                         # print(len(sub_files))
        #                         for file in sub_files:
        #                             file.find_element_by_xpath('a').click()
        #                             t += 1
        #                             wait = WebDriverWait(self.browser, 60)
        #                             wait.until(EC.invisibility_of_element((By.ID, '_viewRoot:status.start')))
        #
        #                             acp_pra_status, err, list_file_name = \
        #                                 self.check_download(acp=acompanhamentos[i], prc_id=prc_id, n_event=n_event,
        #                                                     file_downloaded=file_downloaded,
        #                                                     list_name_urls=list_name_urls,
        #                                                     list_file_name=list_file_name,
        #                                                     list_file_path=list_file_path)
        #
        #                     except (TimeoutException, ElementClickInterceptedException, NoSuchElementException):
        #                         self.log_error.insert_log('Download do arquivo: evento {}!'.format(n_event))
        #                         acp_pra_status = False
        #
        #             elif len(acompanhamentos[i].find_elements_by_xpath('div[2]/div')) > 2:
        #                 l_desc_process = acompanhamentos[i].find_elements_by_xpath('div[2]/div')
        #                 for j in range(len(l_desc_process) - 2):
        #                     desc_process = l_desc_process[j].find_element_by_xpath('span').text.upper()
        #                     desc_process = Tools.remove_accents(desc_process)
        #                     try:
        #                         if 'REMETIDOS OS AUTOS (EM GRAU DE RECURSO) PARA' in desc_process:
        #                            bool_2_grau_numero = True
        #                            # print("foi meu rei")
        #                     except:
        #                         bool_2_grau_numero = False
        #                         self.log_error.insert_log('coleta dos numeros do processo do 2 grau!'.upper())
        #                     # PEGA AS AUDIÊNCIAS
        #                     audiences = desc_process.split(' ')
        #                     if 'AUDIENCIA' in audiences[0]:
        #                         list_audiences.append(desc_process.split('AUDIENCIA ')[-1])
        #
        #                 for j in range(len(l_desc_process) - 2, len(l_desc_process) - 1):
        #                     try:
        #                         l_desc_process[j].find_element_by_xpath('a').click()
        #                         t += 1
        #                         wait = WebDriverWait(self.browser, 60)
        #                         wait.until(EC.invisibility_of_element((By.ID, '_viewRoot:status.start')))
        #
        #                         acp_pra_status, err, list_file_name = \
        #                             self.check_download(acp=acompanhamentos[i], prc_id=prc_id, n_event=n_event,
        #                                                 file_downloaded=file_downloaded, list_name_urls=list_name_urls,
        #                                                 list_file_name=list_file_name, list_file_path=list_file_path)
        #
        #                         sub_files = l_desc_process[j].find_elements_by_xpath('ul/li')
        #                         for file in sub_files:
        #                             file.find_element_by_xpath('a').click()
        #                             t += 1
        #                             wait = WebDriverWait(self.browser, 60)
        #                             wait.until(EC.invisibility_of_element((By.ID, '_viewRoot:status.start')))
        #
        #                             acp_pra_status, err, list_file_name = \
        #                                 self.check_download(acp=acompanhamentos[i], prc_id=prc_id, n_event=n_event,
        #                                                     file_downloaded=file_downloaded,
        #                                                     list_name_urls=list_name_urls,
        #                                                     list_file_name=list_file_name,
        #                                                     list_file_path=list_file_path)
        #
        #                     except (TimeoutException, ElementClickInterceptedException, NoSuchElementException):
        #                         self.log_error.insert_log('Download do arquivo: evento {}!'.format(n_event))
        #                         acp_pra_status = False
        #
        #             list_acomp_download.append((AcompanhamentoModel(acp_esp=desc_process,
        #                                                             acp_numero=n_event,
        #                                                             acp_data_cadastro=aux_data,
        #                                                             acp_prc_id=prc_id), list_file_name))
        #
        #     print('tam: {} | file: {}'.format(len(list_name_urls), t))
        #
        #     # PEGA AS AUDIÊNCIAS APÓS ULTIMA DATA DE MOVIMENTAÇÃO DOS ACOMPANHAMENTOS
        #     for j in range(len(acompanhamentos[k + 1:])):
        #         if len(acompanhamentos[j].find_elements_by_xpath('div')) > 1:
        #             if len(acompanhamentos[j].find_elements_by_xpath('div[2]/div')) == 2:
        #                 try:
        #                     desc_process = acompanhamentos[j].find_element_by_xpath('div[2]/span').text.upper()
        #                     desc_process = Tools.remove_accents(desc_process)
        #                     # PEGA AS AUDIÊNCIAS
        #                     audiences = desc_process.split(' ')
        #                     try:
        #                         if 'REMETIDOS OS AUTOS (EM GRAU DE RECURSO) PARA' in desc_process:
        #                             bool_2_grau_numero = True
        #                             # print("foi meu rei")
        #                     except:
        #                         bool_2_grau_numero = False
        #                         self.log_error.insert_log('coleta dos numeros do processo do 2 grau!'.upper())
        #
        #                     if 'AUDIENCIA' in audiences[0]:
        #                         list_audiences.append(desc_process.split('AUDIENCIA ')[-1])
        #                 except:
        #                     pass
        #
        #             elif len(acompanhamentos[j].find_elements_by_xpath('div[2]/div')) > 2:
        #                 l_desc_process = acompanhamentos[j].find_elements_by_xpath('div[2]/div')[:-2]
        #                 for k in range(len(l_desc_process)):
        #                     desc_process = l_desc_process[k].find_element_by_xpath('span').text.upper()
        #                     desc_process = Tools.remove_accents(desc_process)
        #                     try:
        #                         if 'REMETIDOS OS AUTOS (EM GRAU DE RECURSO) PARA' in desc_process:
        #                             bool_2_grau_numero = True
        #                             # print("foi meu rei")
        #                     except:
        #                         bool_2_grau_numero = False
        #                         self.log_error.insert_log('coleta dos numeros do processo do 2 grau!'.upper())
        #                     # PEGA AS AUDIÊNCIAS
        #                     audiences = desc_process.split(' ')
        #                     if 'AUDIENCIA' in audiences[0]:
        #                         list_audiences.append(desc_process.split('AUDIENCIA ')[-1])
        #
        #     # print('\n audiencias:', list_audiences, '\n')
        #     try:
        #         # TRATA AS AUDIÊNCIAS
        #         dict_audiences = {}
        #         list_audiences.reverse()
        #         for i in range(len(list_audiences)):
        #             aud = list_audiences[i].split(' PARA ')
        #             aud_split = aud[0].split(' ')
        #             try:
        #                 if len(aud_split) > 2:
        #                     tipo = ''
        #                     for i in aud_split[:-1]:
        #                         tipo += i
        #                         if not i == aud_split[-2]:
        #                             tipo += ' '
        #                     tipo = tipo.upper()
        #                     status = aud_split[-1].upper()
        #                 else:
        #                     tipo = aud_split[0].upper()
        #                     status = aud_split[1].upper()
        #             except:
        #                 continue
        #
        #             print('tipo: {} status: {}'.format(tipo, status))
        #
        #             if 'DESIGNADA' == status:
        #                 aux_data = aud[1].split(' PARA ')[-1].strip('.')
        #                 aux_data = str(aux_data.split(' ')[0]) + ' ' + str(aux_data.split(' ')[1])
        #                 data = Tools.treat_date(aux_data)
        #                 if tipo in dict_audiences.keys() and dict_audiences[tipo].aud_status == status:
        #                     dict_audiences[tipo].aud_data = data
        #                 else:
        #                     dict_audiences[tipo] = AudienciaModel(aud_tipo=tipo,
        #                                                           aud_prc_id=prc_id,
        #                                                           aud_status=status,
        #                                                           aud_data=data)
        #             elif 'REDESIGNADA' in status:
        #                 dict_audiences[tipo].aud_status = status
        #                 dict_audiences[(tipo, i)] = dict_audiences[tipo]
        #             elif 'NEGATIVA' in status or 'CANCELADA' in status or 'NAO-REALIZADA' in status:
        #                 dict_audiences[tipo].aud_status = status
        #                 dict_audiences[(tipo, i)] = dict_audiences[tipo]
        #             elif 'REALIZADA' in status:
        #                 dict_audiences[tipo].aud_status = status
        #                 try:
        #                     obs = aud[-1].split(' PARA ')
        #                     obs = Tools.remove_accents(obs)
        #                 except:
        #                     obs = None
        #                 dict_audiences[tipo].aud_obs = obs
        #                 dict_audiences[(tipo, i)] = dict_audiences[tipo]
        #
        #         # SALVA APENAS AS AUDIÊNCIAS COM O ÚLTIMO STATUS
        #         list_audiences.clear()
        #         list_aux = []
        #         for i in dict_audiences.values():
        #             if id(i) not in list_aux:
        #                 list_audiences.append(i)
        #                 list_aux.append(id(i))
        #                 print('\n', i.aud_tipo, '\n', i.aud_status, '\n', i.aud_data, '\n', i.aud_obs, '\n')
        #     except:
        #         list_audiences.clear()
        #         self.log_error.insert_log('coleta de dados das audiências do processo!'.upper())
        # except:
        #     list_acomp_download.clear()
        #     list_name_urls.clear()
        #     list_audiences.clear()
        #     bool_2_grau_numero=False
        #     self.log_error.insert_log('coleta de dados dos acompanhamentos do processo!'.upper())
        #     err = True
        #     # sleep(60*60)
        #     raise
        # return list_audiences, list_acomp_download, list_name_urls, bool_2_grau_numero, err, not_refresh
        pass

class PjeModel2Grau(PjeModel1Grau):
    def __init__(self, site, mode_execute, access, platform_id, platform_name, flag, num_thread, state, link_consulta) :
        super().__init__(site=site, mode_execute=mode_execute, SQL_Long=access, platform_id=platform_id,
                         platform_name=platform_name, flag=flag, num_thread=num_thread, grau='2Grau',state=state,link_consulta=link_consulta)

    # SELECIONA PROCESSOS DO BANCO DE DADOS E PROCURA NA PLATAFORMA PARA UPDATE NO BANCO
    def search_process_to_update(self, row_database):

        # # INICIA O BROWSER E A SESSÃO NA PLATAFORMA
        # self.initializer()
        #
        # # VERIFICA CADA NUMERO DE PROCESSO DENTRO DA ESTRUTURA FORNECIDA
        # i_n = 0
        # for i_proc in row_database:
        #     try:
        #         t0 = time.time()
        #         i_n += 1
        #
        #         # VERIFICA SE O NAVEGADOR ESTÁ ABERTO
        #         try:
        #             if len(self.browser.window_handles) > 1:
        #                 if self.browser is not None:
        #                     self.browser.quit()
        #                     self.log_error.insert_log('Sessão encerrou!')
        #                     return -1
        #         except:
        #             self.log_error.insert_log('navegador fechou!')
        #             return -1
        #
        #         n_proc = i_proc[0]
        #         n_proc = re.sub('[^0-9]', '', n_proc)
        #         list_name_urls = []
        #         self.log_error.insert_title(n_proc)
        #         print("\t{}ª: Coleta de dados do processo: {}".format(i_n, n_proc).upper())
        #         try:
        #             wait = WebDriverWait(self.browser, 10)
        #             wait.until(
        #                 EC.presence_of_element_located((By.ID, 'popupAlertaCertificadoProximoDeExpirarContentTable')))
        #             self.browser.find_element_by_xpath(
        #                 '//*[@id="popupAlertaCertificadoProximoDeExpirarContentDiv"]/div/form/span/i').click()
        #         except:
        #             pass
        #
        #         # BUSCA PELO PROCESSO NA PLATAFORMA
        #         if self.busca_processo_na_plataforma(n_proc, i_proc, t0, self.log_error, self.state):
        #             continue
        #
        #         try:
        #             self.browser.switch_to_window(self.browser.window_handles[1])
        #             wait = WebDriverWait(self.browser, 10)
        #             wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="navbar"]/ul/li/a[1]')))
        #         except:
        #             continue
        #
        #         # COLETA OS ACOMPANHAMENTOS DO PROCESSO
        #         list_aud, list_acp_pra, list_name_urls, err1, not_refresh = self.acomp_down_aud(i_proc[1], i_proc[4] )
        #
        #         # for i in list_acp_pra:
        #         #     print("\n\n")
        #         #     for j in i[0].__dict__.items():
        #         #         if j[-1] is  not None:
        #         #             print(j[0],'->',j[1],'-> tipo->',type(j[1]))
        #
        #         if not err1 and (self.flag or not_refresh is not 1):
        #             # PEGA DADOS DO PROCESSO E ATUALIZA TABELA
        #             try:
        #                 wait = WebDriverWait(self.browser, 10)
        #                 wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="navbar"]/ul/li/a[1]')))
        #                 self.browser.find_element_by_xpath('//*[@id="navbar"]/ul/li/a[1]').click()
        #                 wait = WebDriverWait(self.browser, 10)
        #                 wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'dl-horizontal')))
        #                 try:
        #                     juizo = self.browser.find_element_by_xpath(
        #                         '//*[@id="maisDetalhes"]/div[1]/dl/dd').text.upper()
        #                     juizo = Tools.remove_accents(juizo)
        #                 except:
        #                     juizo = None
        #                 try:
        #                     classe = self.browser.find_element_by_xpath('//*[@id="maisDetalhes"]/dl/dd[1]').text.upper()
        #                     classe = Tools.remove_accents(classe)
        #                 except:
        #                     classe = None
        #                 try:
        #                     assunto = self.browser.find_element_by_xpath('//*[@id="maisDetalhes"]/dl/dd[2]/ul/li[1]').text.upper()
        #                     assunto = Tools.remove_accents(assunto)
        #                 except:
        #                     assunto = None
        #                 try:
        #                     status = self.browser.find_element_by_xpath('//*[@id="VisualizaDados"]/fieldset[3]/'
        #                                                                 'span[11]').text.upper()
        #                     if 'ARQUIVADO DEFINITIVAMENTE' in status or 'ARQUIVADO' in status or 'BAIXADO' in status:
        #                         status = 'ARQUIVADO'
        #                     else:
        #                         status = 'ATIVO'
        #                 except:
        #                     status = None
        #                 try:
        #                     valor_causa = self.browser.find_element_by_xpath('//*[@id="maisDetalhes"]/dl/dd[6]').text
        #                     valor_causa = Tools.treat_value_cause(valor_causa)
        #                 except:
        #                     valor_causa = None
        #                 try:
        #                     dt_distribuicao = self.browser.find_element_by_xpath('//*[@id="maisDetalhes"]/dl/'
        #                                                                          'dd[5]').text.lower()
        #                     dt_distribuicao = Tools.remove_accents(dt_distribuicao)
        #                     dt_distribuicao = Tools.treat_date(dt_distribuicao)
        #                 except:
        #                     dt_distribuicao = None
        #
        #
        #             except:
        #                 juizo, classe, assunto, valor_causa, dt_distribuicao, status = None, None, None, None, None, None
        #
        #             # IDENTIFICA OS ENVOLVIDOS E RETORNA UMA LISTA COM AS PARTES E OS ADVOGADOS/JUIZ
        #             wait = WebDriverWait(self.browser, 10)
        #             wait.until(EC.visibility_of_element_located((By.ID, 'poloAtivo')))
        #             wait.until(EC.visibility_of_element_located((By.ID, 'poloPassivo')))
        #             list_partes, list_advogs = self.envolvidos
        #
        #             # CRIA O OBJETO PROCESSO-PLATAFORMA QUE SERÁ INSERIDO NO BANCO DE DADOS
        #             process_platform = ProcessoPlataformaModel(plp_prc_id=i_proc[1], plp_plt_id=self.platform_id,
        #                                                        plp_numero=n_proc, plp_status=status, plp_juizo=juizo,
        #                                                        plp_valor_causa=valor_causa, plp_classe=classe,
        #                                                        plp_grau=2,
        #                                                        plp_assunto=assunto,
        #                                                        plp_data_distribuicao=dt_distribuicao,
        #                                                        plp_segredo=False, plp_localizado=True)
        #             self.browser.close()
        #             self.browser.switch_to_window(self.browser.window_handles[0])
        #             list_objects_process = [(process_platform, list_partes, list_advogs, list_aud, list_acp_pra,
        #                                      i_proc[7], [])]
        #
        #             # INSERE A LISTA DE OBJETOS NO BANCO DE DADOS
        #             self.export_to_database(objects=list_objects_process, log=self.log_error,
        #                                     list_name_urls=list_name_urls,
        #                                     platform=self.platform_name, state=self.state, root=self)
        #
        #             self.log_error.insert_info('Procedimento finalizado!')
        #         elif not err1:
        #             # CRIA O OBJETO PROCESSO-PLATAFORMA QUE SERÁ INSERIDO NO BANCO DE DADOS
        #             process_platform = ProcessoPlataformaModel(plp_prc_id=i_proc[1], plp_plt_id=self.platform_id,
        #                                                        plp_numero=n_proc, plp_segredo=False,
        #                                                        plp_localizado=True)
        #
        #             self.browser.close()
        #             self.browser.switch_to_window(self.browser.window_handles[0])
        #             list_objects_process = [(process_platform, [], [], list_aud, list_acp_pra, i_proc[7], [])]
        #
        #             # INSERE A LISTA DE OBJETOS NO BANCO DE DADOS
        #             self.export_to_database(objects=list_objects_process, log=self.log_error,
        #                                     list_name_urls=list_name_urls,
        #                                     platform=self.platform_name, state=self.state, root=self)
        #
        #             self.log_error.insert_info('Procedimento finalizado!')
        #         else:  # SENÃO FAZ UMA NOVA BUSCA
        #             # LIMPA A PASTA PARA RECEBER OS NOVOS DOWNLOADS
        #             self.browser.close()
        #             self.browser.switch_to_window(self.browser.window_handles[0])
        #             self.clear_path_download()
        #
        #         print('###Tempo total da coleta de dados do processo: {} SECS'.format(time.time() - t0).upper())
        #         print('-' * 65)
        #     except:
        #         raise
        #         return -1
        #
        # # VERIFICA SE O NAVEGADOR FECHOU, SENÃO O FECHA
        # if self.browser is not None:
        #     self.browser.quit()
        #
        # # VERIFICA SE NÃO RETORNOU ALGUM PROCESSO DA BASE, SENÃO ATUALIZA A PLE_DATA
        # self.update_ple_data(ple_plt_id=self.platform_id, ple_uf=self.state)
        #
        # return i_n
        pass

    # PEGA ANDAMENTOS DO PROCESSO, AS AUDIÊNCIAS E REALIZA OS DOWNLOADS POR ACOMPANHAMENTO
    def acomp_down_aud(self, prc_id, ult_mov):
        # list_acomp_download = []
        # file_downloaded = None
        # desc_process = None
        # aux_data = None
        #
        # list_file_path = []
        # list_audiences = []
        # list_name_urls = []
        # not_refresh = 0
        # err = False
        # t = 0
        # k = 0
        # try:
        #     load = 0
        #     while True:
        #
        #         wait = WebDriverWait(self.browser, 10)
        #         wait.until(EC.invisibility_of_element((By.ID, '_viewRoot:status.start')))
        #
        #
        #         acompanhamentos = self.browser.find_elements_by_xpath('//*[@id="divTimeLine:divEventosTimeLine"]/div')[:-1]
        #
        #         if not load == len(acompanhamentos):
        #             load += 1
        #             eula = self.browser.find_element_by_id('divTimeLine:divEventosTimeLine')
        #             self.browser.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', eula)
        #         else:
        #             eula = self.browser.find_element_by_id('divTimeLine:divEventosTimeLine')
        #             self.browser.execute_script('arguments[0].scrollTop = 0', eula)
        #             break
        #
        #     try:
        #         wait = WebDriverWait(self.browser, 10)
        #         wait.until(
        #             EC.visibility_of_all_elements_located((By.XPATH, '//*[@id="navbar:ajaxPanelAlerts"]/ul/li[3]')))
        #         self.browser.find_element_by_xpath('//*[@id="navbar:ajaxPanelAlerts"]/ul/li[3]/a').click()
        #         wait.until(EC.visibility_of_all_elements_located((By.XPATH, '//*[@id="navbar:ajaxPanelAlerts"]/ul/'
        #                                                                     'li[3]/ul/div/li')))
        #
        #         self.browser.find_element_by_id('navbar:linkAbaAudiencia').click()
        #         wait = WebDriverWait(self.browser, 10)
        #         wait.until(EC.invisibility_of_element((By.ID, '_viewRoot:status.start')))
        #         audiences = self.browser.find_elements_by_xpath('//*[@id="processoConsultaAudienciaGridList:tb"]/tr')
        #         for audience in audiences:
        #             aux = ''
        #             aux += audience.find_element_by_xpath('td[2]').text + ' '
        #             aux += audience.find_element_by_xpath('td[4]').text + ' para '
        #             aux += audience.find_element_by_xpath('td[1]').text
        #             aux = Tools.remove_accents(aux).split(' (')[0]
        #             list_audiences.append(aux.upper())
        #         wait = WebDriverWait(self.browser, 10)
        #         self.browser.find_element_by_xpath('//*[@id="navbar:ajaxPanelAlerts"]/ul/li[3]/a').click()
        #         wait.until(EC.visibility_of_element_located((By.ID, 'navbar:linkAbaAutos')))
        #         self.browser.find_element_by_id('navbar:linkAbaAutos').click()
        #
        #     except (TimeoutException, NoSuchElementException, ElementClickInterceptedException):
        #         list_audiences.clear()
        #         self.log_error.insert_log('coleta de audiências!')
        #
        #     wait = WebDriverWait(self.browser, 10)
        #     wait.until(EC.invisibility_of_element((By.ID, '_viewRoot:status.start')))
        #
        #     acompanhamentos = self.browser.find_elements_by_xpath('//*[@id="divTimeLine:divEventosTimeLine"]/div')
        #
        #     for i in range(k, len(acompanhamentos)):
        #         n_event = len(acompanhamentos) - i
        #         k += 1
        #         if len(acompanhamentos[i].find_elements_by_xpath('div')) == 1:
        #             try:
        #                 aux_data = acompanhamentos[i].find_element_by_xpath('div/span').text
        #                 aux_data = Tools.treat_date(aux_data)
        #             except:
        #                 pass
        #
        #         else:
        #             if ult_mov is not None:
        #                 not_refresh += 1
        #                 if aux_data <= ult_mov:
        #                     break
        #
        #             list_file_name = []
        #             acp_pra_status = False
        #
        #             if len(acompanhamentos[i].find_elements_by_xpath('div[2]/div')) == 2:
        #                 try:
        #                     desc_process = acompanhamentos[i].find_element_by_xpath('div[2]/span').text.upper()
        #                     desc_process = Tools.remove_accents(desc_process)
        #
        #                     # PEGA AS AUDIÊNCIAS
        #                     audiences = desc_process.split(' ')
        #                     if 'AUDIENCIA' in audiences[0]:
        #                         list_audiences.append(desc_process.split('AUDIENCIA ')[-1])
        #                 except:
        #                     try:
        #                         acompanhamentos[i].find_element_by_xpath('div[2]/div[1]/a').click()
        #                         t += 1
        #                         wait = WebDriverWait(self.browser, 60)
        #                         wait.until(EC.invisibility_of_element((By.ID, '_viewRoot:status.start')))
        #
        #                         acp_pra_status, err, list_file_name = \
        #                             self.check_download(acp=acompanhamentos[i], prc_id=prc_id, n_event=n_event,
        #                                                 file_downloaded=file_downloaded, list_name_urls=list_name_urls,
        #                                                 list_file_name=list_file_name, list_file_path=list_file_path)
        #
        #                         sub_files = acompanhamentos[i].find_elements_by_xpath('div[2]/div[1]/ul/li')
        #                         # print(len(sub_files))
        #                         for file in sub_files:
        #                             file.find_element_by_xpath('a').click()
        #                             t += 1
        #                             wait = WebDriverWait(self.browser, 60)
        #                             wait.until(EC.invisibility_of_element((By.ID, '_viewRoot:status.start')))
        #
        #                             acp_pra_status, err, list_file_name = \
        #                                 self.check_download(acp=acompanhamentos[i], prc_id=prc_id, n_event=n_event,
        #                                                     file_downloaded=file_downloaded,
        #                                                     list_name_urls=list_name_urls,
        #                                                     list_file_name=list_file_name,
        #                                                     list_file_path=list_file_path)
        #
        #                     except (TimeoutException, ElementClickInterceptedException, NoSuchElementException):
        #                         self.log_error.insert_log('Download do arquivo: evento {}!'.format(n_event))
        #                         acp_pra_status = False
        #
        #             elif len(acompanhamentos[i].find_elements_by_xpath('div[2]/div')) > 2:
        #                 l_desc_process = acompanhamentos[i].find_elements_by_xpath('div[2]/div')
        #                 for j in range(len(l_desc_process) - 2):
        #                     desc_process = l_desc_process[j].find_element_by_xpath('span').text.upper()
        #                     desc_process = Tools.remove_accents(desc_process)
        #                     try:
        #                         if 'REMETIDOS OS AUTOS (EM GRAU DE RECURSO) PARA' in desc_process:
        #                             bool_2_grau_numero = True
        #                             # print("foi meu rei")
        #                     except:
        #                         bool_2_grau_numero = False
        #                         self.log_error.insert_log('coleta dos numeros do processo do 2 grau!'.upper())
        #                     # PEGA AS AUDIÊNCIAS
        #                     audiences = desc_process.split(' ')
        #                     if 'AUDIENCIA' in audiences[0]:
        #                         list_audiences.append(desc_process.split('AUDIENCIA ')[-1])
        #
        #                 for j in range(len(l_desc_process) - 2, len(l_desc_process) - 1):
        #                     try:
        #                         l_desc_process[j].find_element_by_xpath('a').click()
        #                         t += 1
        #                         wait = WebDriverWait(self.browser, 60)
        #                         wait.until(EC.invisibility_of_element((By.ID, '_viewRoot:status.start')))
        #
        #                         acp_pra_status, err, list_file_name = \
        #                             self.check_download(acp=acompanhamentos[i], prc_id=prc_id, n_event=n_event,
        #                                                 file_downloaded=file_downloaded, list_name_urls=list_name_urls,
        #                                                 list_file_name=list_file_name, list_file_path=list_file_path)
        #
        #                         sub_files = l_desc_process[j].find_elements_by_xpath('ul/li')
        #                         for file in sub_files:
        #                             file.find_element_by_xpath('a').click()
        #                             t += 1
        #                             wait = WebDriverWait(self.browser, 60)
        #                             wait.until(EC.invisibility_of_element((By.ID, '_viewRoot:status.start')))
        #
        #                             acp_pra_status, err, list_file_name = \
        #                                 self.check_download(acp=acompanhamentos[i], prc_id=prc_id, n_event=n_event,
        #                                                     file_downloaded=file_downloaded,
        #                                                     list_name_urls=list_name_urls,
        #                                                     list_file_name=list_file_name,
        #                                                     list_file_path=list_file_path)
        #
        #                     except (TimeoutException, ElementClickInterceptedException, NoSuchElementException):
        #                         self.log_error.insert_log('Download do arquivo: evento {}!'.format(n_event))
        #                         acp_pra_status = False
        #
        #             list_acomp_download.append((AcompanhamentoModel(acp_esp=desc_process,
        #                                                             acp_numero=n_event,
        #                                                             acp_data_cadastro=aux_data,
        #                                                             acp_prc_id=prc_id), list_file_name))
        #
        #     print('tam: {} | file: {}'.format(len(list_name_urls), t))
        #
        #     # PEGA AS AUDIÊNCIAS APÓS ULTIMA DATA DE MOVIMENTAÇÃO DOS ACOMPANHAMENTOS
        #     for j in range(len(acompanhamentos[k + 1:])):
        #         if len(acompanhamentos[j].find_elements_by_xpath('div')) > 1:
        #             if len(acompanhamentos[j].find_elements_by_xpath('div[2]/div')) == 2:
        #                 try:
        #                     desc_process = acompanhamentos[j].find_element_by_xpath('div[2]/span').text.upper()
        #                     desc_process = Tools.remove_accents(desc_process)
        #                     # PEGA AS AUDIÊNCIAS
        #                     audiences = desc_process.split(' ')
        #
        #
        #                     if 'AUDIENCIA' in audiences[0]:
        #                         list_audiences.append(desc_process.split('AUDIENCIA ')[-1])
        #                 except:
        #                     pass
        #
        #             elif len(acompanhamentos[j].find_elements_by_xpath('div[2]/div')) > 2:
        #                 l_desc_process = acompanhamentos[j].find_elements_by_xpath('div[2]/div')[:-2]
        #                 for k in range(len(l_desc_process)):
        #                     desc_process = l_desc_process[k].find_element_by_xpath('span').text.upper()
        #                     desc_process = Tools.remove_accents(desc_process)
        #
        #                     # PEGA AS AUDIÊNCIAS
        #                     audiences = desc_process.split(' ')
        #                     if 'AUDIENCIA' in audiences[0]:
        #                         list_audiences.append(desc_process.split('AUDIENCIA ')[-1])
        #
        #     # print('\n audiencias:', list_audiences, '\n')
        #     try:
        #         # TRATA AS AUDIÊNCIAS
        #         dict_audiences = {}
        #         list_audiences.reverse()
        #         for i in range(len(list_audiences)):
        #             aud = list_audiences[i].split(' PARA ')
        #             aud_split = aud[0].split(' ')
        #             try:
        #                 if len(aud_split) > 2:
        #                     tipo = ''
        #                     for i in aud_split[:-1]:
        #                         tipo += i
        #                         if not i == aud_split[-2]:
        #                             tipo += ' '
        #                     tipo = tipo.upper()
        #                     status = aud_split[-1].upper()
        #                 else:
        #                     tipo = aud_split[0].upper()
        #                     status = aud_split[1].upper()
        #             except:
        #                 continue
        #
        #             print('tipo: {} status: {}'.format(tipo, status))
        #
        #             try:
        #                 if 'DESIGNADA' == status:
        #                     aux_data = aud[1].split(' PARA ')[-1].strip('.')
        #                     aux_data = str(aux_data.split(' ')[0]) + ' ' + str(aux_data.split(' ')[1])
        #                     data = Tools.treat_date(aux_data)
        #                     if tipo in dict_audiences.keys() and dict_audiences[tipo].aud_status == status:
        #                         dict_audiences[tipo].aud_data = data
        #                     else:
        #                         dict_audiences[tipo] = AudienciaModel(aud_tipo=tipo,
        #                                                               aud_prc_id=prc_id,
        #                                                               aud_status=status,
        #                                                               aud_data=data)
        #                 elif 'REDESIGNADA' in status:
        #                     dict_audiences[tipo].aud_status = status
        #                     dict_audiences[(tipo, i)] = dict_audiences[tipo]
        #                 elif 'NEGATIVA' in status or 'CANCELADA' in status or 'NAO-REALIZADA' in status:
        #                     dict_audiences[tipo].aud_status = status
        #                     dict_audiences[(tipo, i)] = dict_audiences[tipo]
        #                 elif 'REALIZADA' in status:
        #                     dict_audiences[tipo].aud_status = status
        #                     try:
        #                         obs = aud[-1].split(' PARA ')
        #                         obs = Tools.remove_accents(obs)
        #                     except:
        #                         obs = None
        #                     dict_audiences[tipo].aud_obs = obs
        #                     dict_audiences[(tipo, i)] = dict_audiences[tipo]
        #             except:
        #                 dict_audiences.clear()
        #
        #
        #         # SALVA APENAS AS AUDIÊNCIAS COM O ÚLTIMO STATUS
        #         list_audiences.clear()
        #         list_aux = []
        #         for i in dict_audiences.values():
        #             if id(i) not in list_aux:
        #                 list_audiences.append(i)
        #                 list_aux.append(id(i))
        #                 print('\n', i.aud_tipo, '\n', i.aud_status, '\n', i.aud_data, '\n', i.aud_obs, '\n')
        #     except:
        #         list_audiences.clear()
        #         self.log_error.insert_log('coleta de dados das audiências do processo!'.upper())
        # except:
        #     list_acomp_download.clear()
        #     list_name_urls.clear()
        #     list_audiences.clear()
        #     bool_2_grau_numero = False
        #     self.log_error.insert_log('coleta de dados dos acompanhamentos do processo!'.upper())
        #     err = True
        #     print('coleta de dados dos acompanhamentos do processo!')
        #
        # return list_audiences, list_acomp_download, list_name_urls, err, not_refresh

    # PEGA OS ENVOLVIDOS E RETORNA UMA LISTA COM AS PARTES E OS ADVOGADOS/JUIZ
        pass
    @property
    def envolvidos(self):
        # list_partes = []
        # list_advogs = []
        # try:
        #     # JUÍZ(A)
        #     try:
        #
        #         tipo = self.browser.find_element_by_xpath('//*[@id="maisDetalhes"]/div[4]/dl/dt').text
        #         nome = self.browser.find_element_by_xpath('//*[@id="maisDetalhes"]/div[4]/dl/dd').text
        #         list_advogs.append((ResponsavelModel(rsp_nome=nome, rsp_tipo='Juíz(a)', rsp_oab='{}-{}'
        #                                              .format(self.state,tipo)), None))
        #         print('Juiaz:', nome, 'OAB -', tipo)
        #
        #     except:
        #         pass
        #
        #     # PARTE ATIVA
        #     partes_ativas = self.browser.find_elements_by_xpath('//*[@id="poloAtivo"]/table/tbody/tr')
        #     for i in range(len(partes_ativas)):
        #         try:
        #
        #             td_split = partes_ativas[i].find_element_by_xpath('td/a/span').text
        #
        #             td_split = td_split.split(' - ')
        #             nome_parte_ativa = td_split[0]
        #             cpf_cnpj_ativa = re.sub('[^0-9.]', '', td_split[-1])
        #             list_partes.append((ParteModel(prt_nome=nome_parte_ativa,
        #                                            prt_cpf_cnpj=cpf_cnpj_ativa), 'Ativo'))
        #             print('parte ativa:', nome_parte_ativa, '- cpf:', cpf_cnpj_ativa)
        #
        #             # RESPONSÁVEIS ATIVOS
        #             resp_ativo = partes_ativas[i].find_elements_by_xpath('td/ul/li')
        #             for j in range(len(resp_ativo)):
        #                 try:
        #                     try:
        #                         td_split = resp_ativo[j].find_element_by_xpath('small/a/span').text.split(' - ')
        #
        #                         nome_responsavel_ativo = td_split[0]
        #                         oab_responsavel_ativo = td_split[1].replace('OAB ', '').upper()
        #
        #                     except:
        #                         nome_responsavel_ativo = resp_ativo[j].find_element_by_xpath('small/a/span'
        #                                                                                      '').text.split(' - ')[0]
        #                         oab_responsavel_ativo = self.state.upper()
        #
        #                     list_advogs.append((ResponsavelModel(rsp_nome=nome_responsavel_ativo.upper(),
        #                                                          rsp_tipo='Advogado(a)',
        #                                                          rsp_oab=oab_responsavel_ativo,), 'Ativo'))
        #                     print('responsavel ativo:', nome_responsavel_ativo, 'OAB -', oab_responsavel_ativo)
        #
        #                 except:
        #                     self.log_error.insert_log('coleta de dados do responsável ativo!')
        #         except:
        #             raise
        #             self.log_error.insert_log('coleta de dados da parte ativa!')
        #
        #     # PARTE PASSIVA
        #     partes_passivas = self.browser.find_elements_by_xpath('//*[@id="poloPassivo"]/table/tbody/tr')
        #     for i in range(len(partes_passivas)):
        #         try:
        #             td_split = partes_passivas[i].find_element_by_xpath('td/a/span').text
        #             td_split = td_split.split(' - ')
        #             nome_parte_passiva = td_split[0]
        #             cpf_cnpj_passiva = re.sub('[^0-9./]', '', td_split[-1])
        #             list_partes.append((ParteModel(prt_nome=nome_parte_passiva,
        #                                            prt_cpf_cnpj=cpf_cnpj_passiva), 'Passivo'))
        #             print('parte passiva:', nome_parte_passiva, '- cpf:', cpf_cnpj_passiva)
        #
        #             # RESPONSÁVEIS PASSIVOS
        #             resp_passivo = partes_passivas[i].find_elements_by_xpath('td/ul/li')
        #             for j in range(len(resp_passivo)):
        #                 try:
        #                     try:
        #                         td_split = resp_passivo[j].find_element_by_xpath('small/a/span').text.split(' - ')
        #                         nome_responsavel_passivo = td_split[0]
        #                         oab_responsavel_passivo = td_split[1].replace('OAB ', '').upper()
        #                     except:
        #                         nome_responsavel_passivo = resp_passivo[j].find_element_by_xpath('small/a/span'
        #                                                                                          '').text.split(' - ')[
        #                             0]
        #                         oab_responsavel_passivo = self.state.upper()
        #
        #                     list_advogs.append((ResponsavelModel(rsp_nome=nome_responsavel_passivo,
        #                                                          rsp_tipo='Advogado(a)',
        #                                                          rsp_oab=oab_responsavel_passivo), 'Passivo'))
        #                     print('responsavel passiva:', nome_responsavel_passivo, 'OAB -', oab_responsavel_passivo)
        #
        #                 except:
        #                     self.log_error.insert_log('coleta de dados do responsável passivo!')
        #         except:
        #             raise
        #             self.log_error.insert_log('coleta de dados da parte passiva!')
        # except:
        #     list_partes.clear()
        #     list_advogs.clear()
        #     self.log_error.insert_log('coleta de dados dos envolvidos no processo!')
        #     raise
        #
        # return list_partes, list_advogs
        pass


class pjeMaranhaoController(PjeModel1Grau):
    def __init__(self, site, mode_execute, access, platform_id, platform_name, flag, num_thread, grau='1Grau'):
        state = 'MA'
        link_consulta='http://pje.tjma.jus.br/pje/Processo/ConsultaProcesso/listView.seam'
        super().__init__(site, mode_execute, access, platform_id, platform_name,state, num_thread, link_consulta,flag,grau)


wait = WebDriverWait(self.browser, 10)
