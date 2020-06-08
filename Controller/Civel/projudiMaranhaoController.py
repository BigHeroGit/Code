from Model.toolsModel import *
from Model.parteModel import ParteModel
from Model.Civel.projudiModel import ProjudiModel
from Model.logErrorModel import LogErrorModelMutlThread
from Model.audienciaModel import AudienciaModel
from Model.responsavelModel import ResponsavelModel
from Model.acompanhamentoModel import AcompanhamentoModel
from Model.processoArquivoModel import ProcessoArquivoModel
from Model.processoPlataformaModel import ProcessoPlataformaModel
from Model.Civel.pjeModel import PjeModel as TratarAudiencia




class projudiMaranhaoController(ProjudiModel):
    def __init__(self, site, mode_execute, access, platform_id, platform_name, flag, num_thread, grau=1):
        super().__init__(site, mode_execute, access, platform_id, platform_name, 'MA', grau)
        self.platform_name = platform_name
        self.platform_id = int(platform_id)
        self.flag = flag
        self.state = 'MA'
        self.num_thread = num_thread
        self.log_error = LogErrorModelMutlThread(platform_name=platform_name, state=self.state,
                                                 num_thread=self.num_thread, grau=grau)

    # MONTAR PROCESSO-PLATAFORMA
    def montar_processo_plataforma(self, prc_id, prc_numero, flag,plp_codigo):

        if flag:

            # PEGA DADOS DO PROCESSO E ATUALIZA TABELA
            juizo, classe, status, assunto, fase, valor_causa, dt_distribuicao = self.pegar_dados_do_prcesso()

            # CRIA O OBJETO PROCESSO-PLATAFORMA QUE SERÁ INSERIDO NO BANCO DE DADOS
            process_platform = ProcessoPlataformaModel(plp_prc_id=prc_id, plp_plt_id=self.platform_id,
                                                       plp_numero=prc_numero, plp_status=status,plp_codigo=plp_codigo,
                                                       plp_juizo=juizo, plp_fase=fase, plp_grau=1,
                                                       plp_valor_causa=valor_causa, plp_classe=classe,
                                                       plp_assunto=assunto, plp_data_distribuicao=dt_distribuicao,
                                                       plp_segredo=False, plp_localizado=1)
        else:

            process_platform = ProcessoPlataformaModel(plp_prc_id=prc_id, plp_plt_id=self.platform_id,
                                                       plp_numero=prc_numero, plp_segredo=False, plp_localizado=True)

        return process_platform

    # VALIDA A INICIALIZAÇÃO DA VARREDURA NA PLATAFORMA
    def initializer(self, user, password):
        i=-1
        while True:
            # INICIALIZA BROWSER
            if self.init_browser():

                # LOGIN NA PLATAFORMA
                if self.login(user, password):

                    if 'projudi.tjma.jus.br/projudi/publico/Logon' in  str(self.browser.current_url):
                        if self.login(user, password):
                            break
                    break
            if self.browser is not None:

                self.browser.quit()

    # MONTAR PROCESSO-PLATAFORMA
    def montar_processo_plataforma(self, prc_id, prc_numero, flag,plp_codigo):

        if flag:

            # PEGA DADOS DO PROCESSO E ATUALIZA TABELA
            juizo, classe, status, assunto, fase, valor_causa, dt_distribuicao = self.pegar_dados_do_prcesso()

            # CRIA O OBJETO PROCESSO-PLATAFORMA QUE SERÁ INSERIDO NO BANCO DE DADOS
            process_platform = ProcessoPlataformaModel(plp_prc_id=prc_id, plp_plt_id=self.platform_id,
                                                       plp_numero=prc_numero, plp_status=status,plp_codigo=plp_codigo,
                                                       plp_juizo=juizo, plp_fase=fase, plp_grau=1,
                                                       plp_valor_causa=valor_causa, plp_classe=classe,
                                                       plp_assunto=assunto, plp_data_distribuicao=dt_distribuicao,
                                                       plp_segredo=False, plp_localizado=1)
        else:

            process_platform = ProcessoPlataformaModel(plp_prc_id=prc_id, plp_plt_id=self.platform_id,
                                                       plp_numero=prc_numero, plp_segredo=False,
                                                       plp_localizado=True)

        return process_platform


    def login(self, user, password):
        try:
            try :
                wait = WebDriverWait(self.browser, 10)
                wait.until(EC.invisibility_of_element((By.ID, 'captchaimg')))
            except :
                text = str(input("\n\n\tDigite as letras da imagem * : "))
                print("Letra Digitadas: \t", text)
                self.browser.find_element_by_xpath('//*[@id="corpo"]/form/table/tbody/tr[2]/td[2]/input').click()
                self.browser.find_element_by_xpath(
                    '//*[@id="corpo"]/form/table/tbody/tr[2]/td[2]/input').send_keys(text)

            self.browser.find_element_by_id('login').send_keys(user)
            self.browser.find_element_by_id('senha').send_keys(password, Keys.RETURN)


            return True
        except:
            return False

    # BUSCA PROCESSO NO PROJUDI
    def find_process(self, prc_numero, prc_codigo=None):
        if prc_codigo is not None:
            try:
                self.browser.get('https://projudi.tjma.jus.br/projudi/listagens/'
                                 'DadosProcesso?numeroProcesso=' + prc_codigo)
                self.browser.find_element_by_xpath('//*[@id="corpo"]/strong')
                return True
            except:
                return False
        else:
            try:
                self.browser.get("https://projudi.tjma.jus.br/projudi/buscas/ProcessosQualquerAdvogado")

                try:
                    wait = WebDriverWait(self.browser, 10)
                    wait.until(EC.invisibility_of_element((By.ID, 'captchaimg')))
                except :
                    text = str(input("\n\n\tDigite as letras da imagem * : "))
                    print("Lestra Digitadas: \t",text)
                    self.browser.find_element_by_xpath('//*[@id="corpo"]/form/table/tbody/tr[2]/td[2]/input').click()
                    self.browser.find_element_by_xpath(
                        '//*[@id="corpo"]/form/table/tbody/tr[2]/td[2]/input').send_keys(text)
                self.browser.find_element_by_id('numeroProcesso').click()
                self.browser.find_element_by_id('numeroProcesso').send_keys(prc_numero, Keys.RETURN)
                if str(self.browser.find_element_by_xpath('//*[@id="corpo"]/div/form[2]/table/tbody/tr[4]/'
                                                          'td').text).find('Nenhum registro foi encontrado', 0) >= 0:
                    return True
                self.browser.find_element_by_xpath('//*[@id="corpo"]/div[1]/form[2]/table/tbody/tr[4]/td[2]/a').click()
            except:
                return True
        return False

    # SITUAÇÃO DO PROCESSO
    @property
    def secret_of_justice(self):
        try:
            return (self.browser.find_element_by_xpath(
                '//*[@id="Partes"]/table[2]/tbody/tr[11]/td[2]/div/strong').text != "NÃO")
        except:
            return False

    # PEGA OS ENVOLVIDOS E RETORNA UMA LISTA COM AS PARTES E OS ADVOGADOS/JUIZ
    @property
    def envolvidos(self):
        list_partes = []
        list_advogs = []
        try:
            # JUÍZ(A)
            try:
                nome_juiz = self.browser.find_element_by_xpath('//*[@id="Partes"]/table/tbody/'
                                                               'tr[7]/td[2]').text.split(': ')[-1].upper()
                nome_juiz = nome_juiz.split('SUBSTITUINDO')[0]
                list_advogs.append((ResponsavelModel(rsp_nome=nome_juiz,
                                                     rsp_tipo='Juíz(a)',
                                                     rsp_oab='PA'), None))
            except:
                self.log_error.insert_log('coleta de dados do juíz!')

            # PARTE ATIVA
            partes_ativas = self.browser.find_elements_by_xpath('//*[@id="Partes"]/table/tbody/tr[2]/td[2]/'
                                                                'table/tbody/tr')[1:]
            for i in range(len(partes_ativas)):
                try:
                    nome_parte_ativa = partes_ativas[i].find_element_by_xpath('td[2]').text
                    cpf_cnpj_ativa = partes_ativas[i].find_element_by_xpath('td[4]').text
                    list_partes.append((ParteModel(prt_nome=nome_parte_ativa.upper(),
                                                   prt_cpf_cnpj=cpf_cnpj_ativa), 'Ativo'))
                    # RESPONSÁVEIS ATIVOS
                    self.browser.find_element_by_xpath('//*[@id="Partes"]/table/tbody/tr[2]/td[2]/table/'
                                                       'tbody/tr[2]/td[5]/a').click()
                    wait = WebDriverWait(self.browser, 10)
                    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'tabelaLista')))
                    aux = self.browser.find_element_by_xpath('//*[@id="Partes"]/table/tbody/tr[2]/td[2]/'
                                                             'table/tbody/tr{}'.format([i + 3]))
                    resp_ativo = aux.find_elements_by_xpath('td/table/tbody/tr[2]/td/table/tbody/tr')[1:]
                    for j in range(len(resp_ativo)):
                        try:
                            nome_responsavel_ativo = resp_ativo[j].find_element_by_xpath('td[1]').text
                            oab_ativo = resp_ativo[j].find_element_by_xpath('td[2]').text
                            list_advogs.append((ResponsavelModel(rsp_nome=nome_responsavel_ativo.upper(),
                                                                 rsp_tipo='Advogado(a)',
                                                                 rsp_oab=oab_ativo), 'Ativo'))
                        except:
                            self.log_error.insert_log('coleta de dados do responsável ativo!')
                    self.browser.find_element_by_xpath('//*[@id="Partes"]/table/tbody/tr[2]/td[2]/table/'
                                                       'tbody/tr[2]/td[5]/a').click()
                except:
                    self.log_error.insert_log('coleta de dados da parte ativa!')

            # PARTE PASSIVA
            partes_passivas = self.browser.find_elements_by_xpath('//*[@id="Partes"]/table/tbody/tr[3]/td[2]/'
                                                                  'table/tbody/tr')[1:]
            for i in range(len(partes_passivas)):
                try:
                    nome_parte_passiva = partes_passivas[i].find_element_by_xpath('td[2]').text
                    cpf_cnpj_passiva = partes_passivas[i].find_element_by_xpath('td[4]').text
                    list_partes.append((ParteModel(prt_nome=nome_parte_passiva.upper(),
                                                   prt_cpf_cnpj=cpf_cnpj_passiva), 'Passivo'))

                    # RESPONSÁVEIS PASSIVOS
                    self.browser.find_element_by_xpath('//*[@id="Partes"]/table/tbody/tr[3]/td[2]/table/'
                                                       'tbody/tr[2]/td[5]/a').click()
                    wait = WebDriverWait(self.browser, 10)
                    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'tabelaLista')))
                    aux = self.browser.find_element_by_xpath('//*[@id="Partes"]/table/tbody/tr[3]/td[2]/'
                                                             'table/tbody/tr{}'.format([i + 3]))
                    resp_passivo = aux.find_elements_by_xpath('td/table/tbody/tr[2]/td/table/tbody/tr')[1:]
                    for j in range(len(resp_passivo)):
                        try:
                            nome_responsavel_passivo = resp_passivo[j].find_element_by_xpath('td[1]').text
                            oab_passivo = resp_passivo[j].find_element_by_xpath('td[2]').text
                            list_advogs.append((ResponsavelModel(rsp_nome=nome_responsavel_passivo.upper(),
                                                                 rsp_tipo='Advogado(a)',
                                                                 rsp_oab=oab_passivo), 'Passivo'))

                        except:
                            self.log_error.insert_log('coleta de dados do responsável Passivo!')
                    self.browser.find_element_by_xpath('//*[@id="Partes"]/table/tbody/tr[3]/td[2]/'
                                                       'table/tbody/tr[2]/td[5]/a').click()
                except:
                    self.log_error.insert_log('coleta de dados da parte Passiva!')
        except:
            list_partes.clear()
            list_advogs.clear()
            self.log_error.insert_log('coleta de dados dos envolvidos no processo!')

        return list_partes, list_advogs

    # PEGA ANDAMENTOS DO PROCESSO, AS AUDIÊNCIAS E REALIZA OS DOWNLOADS POR ACOMPANHAMENTO
    def acomp_down_aud(self, prc_id, ult_mov,bool_2_grau_numero):
        list_acomp_download = []
        file_downloaded = None
        list_file_path = []
        list_audiences = []
        list_name_urls = []
        not_refresh = 0
        bool_2_grau = bool_2_grau_numero
        err = False
        t = 0
        k = 0
        try:
            movimentos = self.browser.find_elements_by_xpath('//*[@id="Arquivos"]/table/tbody/tr')[1:]
            for i in range(len(movimentos)):
                k += 1
                aux_data = movimentos[i].find_element_by_xpath('td/table/tbody/tr/td[5]').text
                aux_data = Tools.treat_date(aux_data)

                if ult_mov is not None:
                    not_refresh += 1
                    if aux_data <= ult_mov:
                        break

                desc_process = movimentos[i].find_element_by_xpath('td/table/tbody/tr/td[4]').text.upper()
                desc_process = Tools.remove_accents(desc_process)

                if not bool_2_grau:
                    aux = desc_process.upper()

                    bool_2_grau = 'RECURSO AUTUADO' in aux
                    if bool_2_grau:
                        print(aux)

                n_event = movimentos[i].find_element_by_xpath('td/table/tbody/tr/td[3]').text

                # PEGAR AS AUDIÊNCIAS
                audiences = desc_process.split(' ')
                if 'AUDIENCIA' in audiences[0]:
                    list_audiences.append(desc_process.split('AUDIENCIA ')[-1])

                # REALIZA O DOWNLOAD
                list_file_name = []
                acp_pra_status = False
                try:
                    movimentos[i].find_element_by_xpath('td/table/tbody/tr/td[8]/div/div/table/tbody/tr/'
                                                        'td[1]/a').click()
                    wait = WebDriverWait(self.browser, 60)
                    wait.until(EC.visibility_of_all_elements_located((By.XPATH, '//*[@id="Arquivos"]/table/tbody/'
                                                                                'tr[{}]/td/span[2]/div/div/table/tbody/'
                                                                                'tr'.format(i + 2))))

                    # BAIXA OS ANEXOS E CRIA ACOMPANHAMENTO ASSOCIANDO OS ANEXOS CONTIDOS NELES
                    ul_files = movimentos[i].find_elements_by_xpath('td/span[2]/div/div/table/tbody/tr')

                    for file in enumerate(ul_files):
                        try:
                            n_files = len(os.listdir(self.path_download_prov))
                            if file[0] != 0:
                                file[1].find_element_by_xpath('td[4]/a').click()
                            else:
                                file[1].find_element_by_xpath('td[5]/a').click()
                            t += 1
                            err_down = self.wait_download(n_files)
                            try:
                                # VERIFICA SE A SESSÃO FOI ENCERRADA
                                if len(self.browser.window_handles) > 1:
                                    if self.browser is not None:
                                        self.browser.switch_to_window(self.browser.window_handles[1])
                                        self.browser.close()
                                        self.browser.switch_to_window(self.browser.window_handles[0])
                                        acp_pra_status = False
                            except:
                                self.log_error.insert_log('Download do arquivo: evento {}!'.format(n_event))
                                acp_pra_status = False
                                err = True
                                break

                            if not err_down:
                                try:
                                    if file[0] != 0:
                                        desc_file = file[1].find_element_by_xpath('td[4]/a').text
                                    else:
                                        desc_file = file[1].find_element_by_xpath('td[5]/a').text
                                except:
                                    desc_file = None

                                for arq in os.listdir(self.path_download_prov):
                                    if arq not in list_file_path:
                                        list_file_path.append(arq)
                                        file_downloaded = arq
                                        break

                                nome = Tools.convert_base(str(datetime.now()))
                                list_name_urls.append((nome, file_downloaded))
                                ext = file_downloaded.split('.')[-1].lower()
                                nome = nome + '.' + ext
                                list_file_name.append(ProcessoArquivoModel(pra_prc_id=prc_id,
                                                                           pra_nome=nome,
                                                                           pra_descricao=desc_file))
                                acp_pra_status = True
                            else:
                                self.log_error.insert_log('Download do arquivo: evento {}!'.format(n_event))
                                acp_pra_status = False
                        except:
                            self.log_error.insert_log('Download do arquivo: evento {}!'.format(n_event))
                            acp_pra_status = False
                except:
                    pass

                list_acomp_download.append([AcompanhamentoModel(acp_esp=desc_process,
                                                                acp_numero=n_event,
                                                                acp_data_cadastro=aux_data,
                                                                acp_prc_id=prc_id), list_file_name])

            print('tam: {} | file: {}'.format(len(list_name_urls), t))

            # PEGA AS AUDIÊNCIAS APÓS ULTIMA DATA DE MOVIMENTAÇÃO DOS ACOMPANHAMENTOS
            for j in range(len(movimentos[k + 1:])):
                desc_process = movimentos[j].find_element_by_xpath('td/table/tbody/tr/td[4]').text.upper()
                desc_process = Tools.remove_accents(desc_process)
                audiences = desc_process.split(' ')
                if 'AUDIENCIA' in audiences[0]:
                    list_audiences.append(desc_process.split('AUDIENCIA ')[-1])

            try:
                # TRATA AS AUDIÊNCIAS
                dict_audiences = {}
                list_audiences.reverse()
                tipo = None
                status = None
                for i in range(len(list_audiences)):
                    aud = list_audiences[i].split('\n')
                    aud_split = aud[0].split(' ')

                    if 'AUDIENCIA' in aud_split[0]:
                        continue
                    if 'CEJUSC' in aud_split:
                        aud_split.remove('CEJUSC')
                    try:
                        if 'DE' in aud_split[0]:
                            del aud_split[0]
                    except IndexError:
                        pass

                    if len(aud_split) > 2 and 'REALIZADA' not in aud_split:
                        tipo = ''
                        for l in aud_split[:-1]:
                            tipo += l
                            if not l == aud_split[-2]:
                                tipo += ' '
                        tipo = tipo.upper()
                        status = aud_split[-1].upper()
                    elif 'REALIZADA' in aud_split:
                        status = 'REALIZADA'
                    elif 'NEGATIVA' in aud_split:
                        status = 'NEGATIVA'
                    elif 'CANCELADA' in aud_split:
                        status = 'CANCELADA'
                    elif len(aud_split) == 2:
                        tipo = aud_split[0].upper()
                        status = aud_split[1].upper()
                    elif len(aud_split) > 0:
                        status = aud_split[0].upper()

                    print('tipo: {} - status: {}'.format(tipo, status))

                    if 'DESIGNADA' == status or 'MARCADA' == status:
                        try:
                            aux_data = aud[1].split('PARA ')[-1].split(' )')[0].split(')')[0].split(', ')[0]
                            aux_data = aux_data.lower()
                            data = Tools.treat_date(aux_data)
                        except:
                            data = None
                        if tipo in dict_audiences.keys() and dict_audiences[tipo].aud_status == status:
                            dict_audiences[tipo].aud_data = data
                        else:
                            dict_audiences[tipo] = AudienciaModel(aud_tipo=tipo,
                                                                  aud_prc_id=prc_id,
                                                                  aud_status=status,
                                                                  aud_data=data)
                    elif 'REDESIGNADA' in status or 'REMARCADA' in status:
                        dict_audiences[tipo].aud_status = status
                        dict_audiences[(tipo, i)] = dict_audiences[tipo]
                    elif 'NEGATIVA' in status or 'CANCELADA' in status:
                        dict_audiences[tipo].aud_status = status
                        dict_audiences[(tipo, i)] = dict_audiences[tipo]
                    elif 'REALIZADA' in status or 'PUBLICADA' in status:
                        dict_audiences[tipo].aud_status = status
                        try:
                            obs = Tools.remove_accents(aud[1]).strip(' (').strip(')')
                        except:
                            obs = None
                        dict_audiences[tipo].aud_obs = obs
                        dict_audiences[(tipo, i)] = dict_audiences[tipo]

                list_audiences.clear()
                list_aux = []
                for i in dict_audiences.values():
                    if id(i) not in list_aux:
                        list_audiences.append(i)
                        list_aux.append(id(i))
                        print('\n', i.aud_tipo, '\n', i.aud_status, '\n', i.aud_data, '\n', i.aud_obs, "\n")
            except:
                list_audiences.clear()
                self.log_error.insert_log('coleta de dados das audiências do processo!'.upper())

        except:
            list_acomp_download.clear()
            list_audiences.clear()
            list_name_urls.clear()
            self.log_error.insert_log('coleta de dados dos acompanhamentos do processo!'.upper())
            err = True
            bool_2_grau = False
            # raise

        return list_audiences, list_acomp_download, list_name_urls, bool_2_grau, err, not_refresh

    # VAlIDANDOS SE NUMERO DO PROCESSO CONTIDO NA PLATAFORMA E O MESMO CONTIDO NO SITE
    def validar_numero_plataforma(self, prc_numero):
        wait = WebDriverWait(self.browser, 10)
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/div/div[3]/form/div[1]/table[2]/tbody/tr[1]/td')))
        numero_no_site = self.browser.find_element_by_xpath('/html/body/div[3]/div/div[3]/form/div[1]/table[2]/tbody/tr[1]/td').text
        numero_no_site = re.sub('[^0-9]', '', numero_no_site)
        print(numero_no_site)
        print(prc_numero)
        print('numeros diferentes')
        # input()
        return prc_numero not in numero_no_site


    # PEGA DADOS DO PROCESSO
    def pegar_dados_do_prcesso(self):
        try:
            juizo = self.browser.find_element_by_xpath('//*[@id="Partes"]/table[2]/tbody/tr[7]/'
                                                       'td[2]').text.split(' Juiz')[0].upper()
            juizo = Tools.remove_accents(juizo)
        except:
            juizo = None
        try:
            classe = self.browser.find_element_by_xpath('//*[@id="Partes"]/table[2]/tbody/tr[9]/td[2]/table/'
                                                        'tbody/tr/td').text.split(' « ')[0]
            classe = Tools.remove_accents(classe)
        except:
            classe = None
        try:
            status = self.browser.find_element_by_xpath('//*[@id="includeContent"]/fieldset/'
                                                        'table/tbody/tr[6]/td[2]').text.upper()
            if 'ARQUIVADO DEFINITIVAMENTE' in status or 'ARQUIVADO' in status or 'BAIXADO' in status:
                status = 'ARQUIVADO'
            else:
                status = 'ATIVO'
        except:
            status = None
        try:
            assunto = self.browser.find_element_by_xpath('//*[@id="Partes"]/table[2]/tbody/tr[8]/'
                                                         'td[2]').text.upper()
            assunto = Tools.remove_accents(assunto)
        except:
            assunto = None
        try:
            fase = self.browser.find_element_by_xpath('//*[@id="Partes"]/table[2]/tbody/'
                                                      'tr[12]/td[2]').text.upper()
            fase = Tools.remove_accents(fase)
        except:
            fase = None
        try:
            valor_causa = self.browser.find_element_by_xpath('//*[@id="Partes"]/table[2]/tbody/'
                                                             'tr[14]/td[2]').text
            valor_causa = Tools.treat_value_cause(valor_causa)
        except:
            valor_causa = None
        try:
            dt_distribuicao = self.browser.find_element_by_xpath('//*[@id="Partes"]/table[2]/tbody/tr[13]/'
                                                                 'td[4]').text.lower()
            dt_distribuicao = Tools.remove_accents(dt_distribuicao)
            dt_distribuicao = Tools.treat_date(dt_distribuicao)
        except:
            dt_distribuicao = None

        print('\n----')
        print('juizo', juizo)
        print('classe', classe)
        print('status', status)
        print('fase', fase)
        print('valor_causa', valor_causa)
        print('dt_distribuicao', dt_distribuicao)
        print('\n----')

        return juizo,classe,status,fase,valor_causa,dt_distribuicao