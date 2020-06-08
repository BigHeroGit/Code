from Model.Civel.rootModel import RootModel
from Model.toolsModel import *
from Model.logErrorModel import LogErrorModelMutlThread
from Model.processoPlataformaModel import ProcessoPlataformaModel
from Model.acompanhamentoModel import AcompanhamentoModel
from Model.processoArquivoModel import ProcessoArquivoModel
from Model.parteModel import ParteModel
from Model.responsavelModel import ResponsavelModel
from Model.audienciaModel import AudienciaModel



class TucujurisModel(RootModel):
    def __init__(self, site, mode_execute, access, platform_id, platform_name, flag,num_thread,grau=1):
        self.grau = 1 if 1 == grau else 2
        self.log_error = None
        self.state = "AP"
        self.platform_name = platform_name
        self.platform_id = platform_id
        self.flag = flag
        self.num_thread = num_thread
        self.log_error = LogErrorModelMutlThread(platform_name=platform_name, state=self.state,
                                                 num_thread=self.num_thread)
        super().__init__(site, mode_execute, access, platform_id, platform_name, self.state, grau)

        # MONTAR PROCESSO-PLATAFORMA

        # MONTAR PROCESSO-PLATAFORMA

    def montar_processo_plataforma(self, prc_id, prc_numero, flag, plp_codigo):

        if flag:

            # PEGA DADOS DO PROCESSO E ATUALIZA TABELA
            segredo, vara, assunto, status = self.pegar_dados_do_prcesso()

            # CRIA O OBJETO PROCESSO-PLATAFORMA QUE SERÁ INSERIDO NO BANCO DE DADOS
            process_platform = ProcessoPlataformaModel(plp_prc_id=prc_id, plp_plt_id=self.platform_id,  plp_grau=1,
                                                       plp_numero=prc_numero, plp_status=status, plp_codigo=plp_codigo,
                                                       plp_segredo=False,plp_assunto=assunto,  plp_localizado=1)
        else:

            process_platform = ProcessoPlataformaModel(plp_prc_id=prc_id, plp_plt_id=self.platform_id,
                                                       plp_numero=prc_numero, plp_segredo=False, plp_localizado=True)

        return process_platform



    # VALIDA A INICIALIZAÇÃO DA VARREDURA NA PLATAFORMA
    def initializer(self, user, password):
        while True:
            # INICIALIZA BROWSER
            try:
                if self.init_browser():
                    self.browser.execute_script('return document.readyState')
                    wait = WebDriverWait(self.browser, 5)
                    wait.until(EC.presence_of_element_located((By.XPATH, '/html/body')))
                    # LOGIN NA PLATAFORMA
                    if self.login(user, password):
                        break
            except (TimeoutException, NoSuchElementException, ElementClickInterceptedException,
                    ElementNotSelectableException, Exception):
                self.browser.quit()
                continue
            self.browser.quit()


    # REALIZA LOGIN
    def login(self, user, password):
        try:
            link_ant = self.browser.current_url
            while True:
                try:

                    sleep(1.5)
                    self.browser.find_element_by_xpath('//*[@id="usuario"]').clear()
                    self.browser.find_element_by_xpath('//*[@id="senha"]').clear()

                    self.browser.find_element_by_xpath('//*[@id="usuario"]').send_keys(user)

                    self.browser.find_element_by_xpath('//*[@id="senha"]').send_keys(password, Keys.RETURN)

                    sleep(1.5)
                    if link_ant != self.browser.current_url:
                        return True
                    else:
                        continue

                except:
                    continue

        except:
            return False

    # BUSCA PROCESSO NO TUCUJURIS
    def find_process(self, prc_numero=None, prc_codigo=None):
        try:

            self.browser.get(
                'http://tucujuris.tjap.jus.br/tucujuris/pages/consultar-processo/consultar-processo.html')

            self.browser.execute_script('return document.readyState')
            wait = WebDriverWait(self.browser, 15)
            wait.until(EC.presence_of_element_located((By.ID, 'form-consulta')))
            try:
                wait = WebDriverWait(self.browser, 15)
                wait.until(EC.element_to_be_clickable(
                    (By.XPATH, '//*[@id="form-consulta"]/div/form/div[5]/div/label[4]/input')))
                self.browser.find_element_by_xpath(
                    '//*[@id="form-consulta"]/div/form/div[5]/div/label[4]/input').click()

            except:
                return True
            wait.until(EC.visibility_of_element_located(
                (By.XPATH, '//*[@id="form-consulta"]/div/form/div[1]/div/div/div/input')))
            self.browser.find_element_by_xpath(
                '//*[@id="form-consulta"]/div/form/div[1]/div/div/div/input').send_keys(prc_numero)

            wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="btnConsultar"]')))
            self.browser.find_element_by_xpath('//*[@id="btnConsultar"]').click()

            wait.until(EC.element_to_be_clickable((By.ID, 'resultado-consulta')))
            self.browser.find_element_by_xpath('//*[@id="resultado-consulta"]/div/div[2]/div/div/a').click()
            wait.until(EC.element_to_be_clickable((By.XPATH,
                                                   '//*[@id="detalhe-processo"]/div/detalhesprocesso/partial/div/div/div[1]/div[1]/cabecalhoprocesso/div/div/div[1]/h3/small[2]/a')))
            link = self.browser.find_element_by_xpath(
                '//*[@id="detalhe-processo"]/div/detalhesprocesso/partial/div/div/div[1]/div[1]/cabecalhoprocesso/div/div/div[1]/h3/small[2]/a').get_attribute(
                "href")
            self.browser.get(str(link))
            self.browser.execute_script('return document.readyState')
            return False
        except:
            return True

    # SITUAÇÃO DO PROCESSO
    def secret_of_justice(self):
        try:
            return (self.browser.find_element_by_xpath(
                '//*[@id="Partes"]/table[2]/tbody/tr[11]/td[2]/div/strong').text != "NÃO")
        except:
            return False

    # PEGA OS ENVOLVIDOS E RETORNA UMA LISTA COM AS PARTES E OS ADVOGADOS/JUIZ
    def envolvidos(self):
        # input('começou a coletar as partes')
        list_partes = []
        list_advogs = []
        # PARTES E RESPONSÁVEIS
        try:
            # PARTE ATIVA & PASSIVA
            self.browser.execute_script('window.scrollTo(0, 0);')
            wait = WebDriverWait(self.browser, 15)
            wait.until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="main-content"]/div/div[2]/detalhesprocesso/partial/div/div/div[2]/div')))
            partes = self.browser.find_elements_by_xpath(
                '//*[@id="main-content"]/div/div[2]/detalhesprocesso/partial/div/div/div[2]/div')
            tipo = None
            for parte_i in partes:

                try:
                    nome_parte = parte_i.find_element_by_xpath('div[1]/div/div[2]/span').text
                    # print(nome_parte)
                    # input('nome da parte')
                    nome_parte = Tools.remove_accents(nome_parte)
                    tipo = parte_i.find_element_by_xpath('div[1]/div/div[1]/label').text
                    tipo = 'Ativo' if "PARTE AUTORA" in tipo else 'Passivo'
                    print('\n',tipo,'parte->',nome_parte)
                    # input()
                    if len(nome_parte):
                        list_partes.append((ParteModel(prt_nome=nome_parte, prt_cpf_cnpj="AP"), str(tipo)))
                except Exception as e:
                    self.log_error.insert_log('coleta de dados da parte {}!'.format(tipo))
                    input(e)
                    raise
                try:
                    nome_responsavel = parte_i.find_element_by_xpath('div[2]/div/div[2]/span').text
                    nome_responsavel = Tools.remove_accents(nome_responsavel)
                    # print('\n', tipo, 'responsável->', nome_responsavel)
                    if len(nome_responsavel):
                        list_advogs.append((ResponsavelModel(rsp_nome=nome_responsavel,rsp_tipo="ADVOGADO(A)", rsp_oab="AP"), str(tipo)))
                except:
                    self.log_error.insert_log('coleta de dados do responsável {}!'.format(tipo))
        except:
            list_partes.clear()
            list_advogs.clear()
            self.log_error.insert_log('coleta de dados dos envolvidos no processo!')

        # print(list_partes, list_advogs)
        # input('terminou de coletar as partes')
        return list_partes, list_advogs

    # PEGA ANDAMENTOS DO PROCESSO, AS AUDIÊNCIAS E REALIZA OS DOWNLOADS POR ACOMPANHAMENTO
    def acomp_down_aud(self, prc_id, ult_mov, bool_2_grau_numero,full=None):
        print('ult_mov',ult_mov)
        file_downloaded = None
        list_name_urls = []
        list_audiences = []
        list_file_path = []
        list_acomp_download = []
        not_refresh = 0
        err = False
        acp_pra_status = None
        primeiro_d=True
        t = 0
        k = 0
        # PERCORRE A TABELA E FAZ O DOWNLOAD REFERENTE A CADA ACOMPANHAMENTO
        try:
            # COLETA DE DADOS PARA CRIAÇÃO DOS ACOMPANHAMENTOS E DOWNLOAD DOS ARQUIVOS
            wait = WebDriverWait(self.browser, 15)
            wait.until(EC.visibility_of_element_located(
                (By.XPATH,
                 '//*[@id="main-content"]/div/div[2]/detalhesprocesso/partial/div/div/div[3]/historicoprocesso/div/div[1]/div')))
            acompanhamentos = self.browser.find_elements_by_xpath(
                '//*[@id="main-content"]/div/div[2]/detalhesprocesso/partial/div/div/div[3]/historicoprocesso/div/div[1]/div')
            #print('len(acompanhamentos)',len(acompanhamentos))
            sleep(1)
            for i in range(len(acompanhamentos)):
                xpath_aux_data = '//*[@id="main-content"]/div/div[2]/detalhesprocesso/partial/div/div/div[3]/' \
                                 'historicoprocesso/div/div[1]/div[{}]/div[1]/span[2]/span'.format(i + 1)
                wait = WebDriverWait(self.browser, 15)

                wait.until(EC.visibility_of_element_located((By.XPATH,xpath_aux_data)))

                aux_data = self.browser.find_element_by_xpath(xpath_aux_data)
                coordinates = aux_data.location_once_scrolled_into_view
                coordinates['x'] += 200
                coordinates['y'] += 200
                # print(coordinates)
                # input()
                self.browser.execute_script('window.scrollTo({}, {});'.format(coordinates['x'], coordinates['y']))
                print(i)
                aux_data = self.browser.find_element_by_xpath(xpath_aux_data).text[:-1]

                print("data->",aux_data)
                aux_data = Tools.treat_date(aux_data)
                if ult_mov is not None:
                    not_refresh += 1
                    if aux_data <= ult_mov:
                        break
                k += 1

                desc_process = acompanhamentos[i].find_element_by_xpath('div[2]').text
                desc_process = Tools.remove_accents(desc_process)
                barralugar = acompanhamentos[i].find_element_by_xpath('div[2]').location_once_scrolled_into_view
                lugar_n_event = acompanhamentos[i].find_element_by_xpath(
                    'div[1]/span[1]').location_once_scrolled_into_view

                self.browser.execute_script(
                    'window.scrollTo({}, {});'.format(lugar_n_event['x'] + 200, lugar_n_event['y'] + 200))
                n_event = acompanhamentos[i].find_element_by_xpath('div[1]/span[1]').text[1:]

                # print(n_event)
                # input('acp_numero')
                # REALIZA O DOWNLOAD DOS ANEXOS DE CADA ACOMPANHAMENTO
                acess_donwload = acompanhamentos[i].find_element_by_xpath('div[3]/a')
                list_file_name = []

                if acess_donwload.text:
                    try:
                        coordinate = acess_donwload.location_once_scrolled_into_view
                        self.browser.execute_script(
                            'window.scrollTo({}, {});'.format(coordinate['x'], coordinate['y']))
                        acess_donwload.click()
                        wait = WebDriverWait(self.browser, 5)
                        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'modal-open')))
                        indentificador = 1

                        wait = WebDriverWait(self.browser, 5)
                        wait.until(EC.element_to_be_clickable((By.XPATH,
                                                               '//*[@id="main-content"]/div/div[2]/detalhesprocesso/partial/div/div/div[3]/historicoprocesso/div/div[2]/div/div/div[2]/div[1]')))
                        list_file=self.browser.find_elements_by_xpath(
                            '//*[@id="main-content"]/div/div[2]/detalhesprocesso/partial/div/div/div[3]/historicoprocesso/div/div[2]/div/div/div[2]/div[1]/div/div')

                        # input('kaio inicio')
                        # ANEXO SUPRIMIDO
                        files_supri = self.browser.find_elements_by_xpath(
                            '//*[@id="main-content"]/div/div[2]/detalhesprocesso/partial/div/div/div[3]/historicoprocesso/div/div[2]/div/div/div[2]/div[1]/p/span')
                        if len(files_supri):
                            files_supri = int(files_supri[0].text)
                            for i in range(files_supri):
                                list_file_name.append(ProcessoArquivoModel(pra_prc_id=prc_id,
                                                                       pra_nome=Tools.convert_base(str(datetime.now())),
                                                                       pra_erro=3))
                        # input('kaio fim')
                        for file in list_file:
                            try:

                                n_files = len(os.listdir(self.path_download_prov))
                                coordinates = file.location_once_scrolled_into_view

                                if list_file.index(file) > 2:
                                    self.browser.execute_script(
                                        'window.scrollTo({}, {});'.format(coordinates['x'], coordinates['y']))


                                try:
                                    # tempo alto por causa do dowload dos audio
                                    wait = WebDriverWait(self.browser, 25)
                                    wait.until(EC.element_to_be_clickable((By.XPATH,
                                                                           '//*[@id="main-content"]/div/div[2]/detalhesprocesso/partial/div/div/div[3]/historicoprocesso/div/div[2]/div/div/div[2]/div[1]/div/div[{}]/a'.format( indentificador))))
                                    file.find_element_by_xpath('a').click()
                                    wait = WebDriverWait(self.browser, 25)
                                    xpath = self.browser.find_element_by_xpath('//*[@id="main-content"]/div/div[2]/detalhesprocesso/partial/div/div/div[3]/historicoprocesso/div/div[2]/div/div/div[2]/div[1]/div/div[{}]/a/div/p'.format(indentificador))
                                    # print(xpath.text)
                                    # input("Certo?")
                                    # IF PARA VERIFICAR SE É AUDIO, AUDIO NAO É NECESSARIO REALIZAR O CLICK DEBAIXO....
                                    if 'INTERESSADO' not in xpath.text:
                                        wait.until(EC.element_to_be_clickable((By.XPATH,
                                                                               '//*[@id="main-content"]/div/div[2]/detalhesprocesso/partial/div/div/div[3]/historicoprocesso/div/div[2]/div/div/div[1]/a')))

                                        self.browser.find_element_by_xpath(
                                            '//*[@id="main-content"]/div/div[2]/detalhesprocesso/partial/div/div/div[3]/historicoprocesso/div/div[2]/div/div/div[1]/a').click()
                                except:
                                    input('erro xpath unfunding')
                                    raise
                                t += 1

                                err_down = self.wait_download(n_files)
                                print('', end='*', flush=True)
                                nome = Tools.convert_base(str(datetime.now()))
                                desc_file = file.text

                                if not err_down:
                                    for arq in os.listdir(self.path_download_prov):
                                        if arq not in list_file_path:
                                            list_file_path.append(arq)
                                            file_downloaded = arq
                                            break
                                    list_name_urls.append((nome, file_downloaded))
                                    # print((nome, file_downloaded))
                                    ext = file_downloaded.split('.')[-1].lower()
                                    nome = nome + '.' + ext

                                    acp_pra_status = True and acp_pra_status

                                list_file_name.append(ProcessoArquivoModel(pra_prc_id=prc_id,
                                                                               pra_nome=nome,
                                                                               pra_descricao=desc_file,pra_erro=int(err_down)))
                            except Exception as e:
                                # input(e)
                                raise
                                self.log_error.insert_log('Download do arquivo: evento {}!'.format(n_event))
                                self.browser.execute_script('return document.readyState')
                                acp_pra_status = False

                            indentificador += 1

                        x_path_button = '/html/body/div[3]/section/div/div[2]/detalhesprocesso/partial/div/div/div[3]' \
                                        '/historicoprocesso/div/div[2]/div/div/div[1]/button'

                        t_ini =  time.time()
                        flag= True
                        while flag:
                            flag=( time.time()-t_ini  ) < 15
                            try:
                                wait = WebDriverWait(self.browser, 5)
                                wait.until(EC.visibility_of_element_located((By.XPATH, x_path_button)))
                                button_close = self.browser.find_element_by_xpath(x_path_button)
                                button_close.click()

                            except:
                                pass
                        if flag :
                            raise


                    except Exception as e:
                        # input(e)
                        raise
                        self.log_error.insert_log('Download  na coleta dos arquivoa: evento {}!'.format(n_event))
                        acp_pra_status = False

                self.browser.execute_script(
                    'window.scrollTo({}, {});'.format(barralugar['x'], barralugar['y']))
                list_desc_proc = desc_process.split('\n')
                if len(list_desc_proc) == 1:
                    list_desc_proc.append('')

                list_acomp_download.append([AcompanhamentoModel(acp_tipo=list_desc_proc[0],
                                                                acp_esp=list_desc_proc[1],
                                                                acp_data_cadastro=aux_data,
                                                                acp_prc_id=prc_id,
                                                                acp_pra_status=acp_pra_status,
                                                                acp_numero=n_event), list_file_name])

                # for i in list_acomp_download[-1][0].__dict__.items():
                #     if i[1] is not None:
                #         print('{} \t:\t {}'.format(i[0],i[1]))
                # a=input('\n\npode continuar\n\n')
                # input('audiencias inicio')
                # BUSCA AS AUDIÊNCIAS PARTE 1

                if (desc_process.find('Audi') == 0):
                    # input(desc_process + '<<<<\n')
                    aux = desc_process.split('\n')
                    # print('kaioooooo')
                    # input(aux)

                    aux[1] = aux[1] if len(aux[1]) > 7 else aux[0]
                    status, tipo = self.tratar_status_tipo(aux[0], aux[1])
                    data = aux[0].split('. ')[-1]
                    data = Tools.treat_date(data)
                    # print('\n' + tipo + '-' + status + '-' + str(data) + '-' + desc_process + '-' + str(aux_data))
                    # input('stop')
                    list_audiences.append((tipo, status, data, desc_process, aux_data))

            # PEGA AS AUDIÊNCIAS APÓS ULTIMA DATA DE MOVIMENTAÇÃO DOS ACOMPANHAMENTOS
            for j in range(k,len(acompanhamentos)):
                desc_process = acompanhamentos[j].find_element_by_xpath('div[2]').text
                desc_process = Tools.remove_accents(desc_process)
                if"AUDIENCIA" not in desc_process[:12]:
                    continue

                xpath_aux_data = '//*[@id="main-content"]/div/div[2]/detalhesprocesso/partial/div/div/div[3]/'\
                                 'historicoprocesso/div/div[1]/div[{}]/div[1]/span[2]/span'.format(j + 1)
                wait = WebDriverWait(self.browser, 10)
                aux_data=wait.until(EC.visibility_of_element_located((By.XPATH, xpath_aux_data)))
                aux = desc_process.split('\n')
                status, tipo = self.tratar_status_tipo(aux[0], aux[1])
                data = aux[0].split('.')[-1]
                # print('data->',data)
                data = Tools.treat_date(data)


                list_audiences.append((tipo, status, data, desc_process, aux_data))
        except:
            # raise
            list_acomp_download.clear()
            list_name_urls.clear()
            list_audiences.clear()
            self.log_error.insert_log('coleta de dados dos acompanhamentos do processo!'.upper())
            err = True
            # input('\n\npode 4 continuar\n\n')
            raise
        # TRATA AS AUDIÊNCIAS
        list_audiences = self.trata_as_audiencias(list_audiences, prc_id)
        # input('audiencia tratada')
        return list_audiences, list_acomp_download, list_name_urls,None,  err, not_refresh

    def validar_numero_plataforma(self, prc_numero):
        try:
            wait = WebDriverWait(self.browser, 5)
            # input("\n\n\n\t\t\tTimeoutException")
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'numcnj')))
            numero_no_site = self.browser.find_element_by_class_name('numcnj').text
            numero_no_site = re.sub('[^0-9]', '', numero_no_site)
            # input('{}={} ->{}'.format(prc_numero,numero_no_site,prc_numero not in numero_no_site))
            return prc_numero not in numero_no_site
        except Exception as e:
            print(e)
        return True

    # TRATAR STATUS E TIPO DAS AUDIENCIAS
    def tratar_status_tipo(self, status, tipo):
        status = normalize('NFKD', status).encode('ASCII', 'ignore').decode('ASCII')
        tipo = normalize('NFKD', tipo).encode('ASCII', 'ignore').decode('ASCII')
        # input('\n\n' + status + '\n\n' + tipo + '\n\n')

        status = status.upper()
        tipo = tipo.upper()
        aux1, aux2 = None, None

        if 'CONCILIACAO' in tipo and 'INSTRUCAO' in tipo and 'JULGAMENTO' in tipo:
            aux1 = 'UNA'

        elif 'INSTRUCAO' in tipo and 'JULGAMENTO' in tipo:
            aux1 = 'INSTRUCAO E  JULGAMENTO'

        elif 'CONCILIACAO' in tipo:
            aux1 = 'CONCILIACAO'

        elif 'INSTRUCAO' in tipo:
            aux1 = 'INSTRUCAO'

        elif 'JULGAMENTO' in tipo:
            aux1 = 'JULGAMENTO'
        else:
            aux1 = None

        # TRATAR STATUS

        if 'NAO REALIZADA' in status:
            aux2 = 'NAO REALIZADA'

        elif 'REALIZADA' in status:
            aux2 = 'REALIZADA'

        elif 'CONCLUIDA' in status:
            aux2 = 'CONCLUIDA'

        elif 'REDESIGNADA' in status:
            aux2 = 'REDESIGNADA'

        elif 'DESIGNADA' in status:
            aux2 = 'DESIGNADA'

        elif 'PENDENTE' in status:
            aux2 = 'JULGAMENTO'
        elif 'CANCELADA' in status:
            aux2 = 'CANCELADA'

        return aux2, aux1

    # TRATA AS AUDIÊNCIAS
    def trata_as_audiencias(self, list_audiences, prc_id):
        dict_audiences = []
        list_audiences.reverse()

        for i_aud in range(len(list_audiences)):
            obj = len(dict_audiences)
            obj -= 1

            while obj >= 0:
                if list_audiences[i_aud][0] == dict_audiences[obj][0]:
                    if list_audiences[i_aud][1] == 'REDESIGNADA' and list_audiences[i_aud][2].date() == \
                            list_audiences[i_aud][4].date():
                        dict_audiences[obj] = ([list_audiences[i_aud][0], "REALIZADA", list_audiences[i_aud][2], list_audiences[i_aud][3],
                             list_audiences[i_aud][4]])
                        break
                    if dict_audiences[obj][1] == "REALIZADA":
                            dict_audiences.append(list_audiences[i_aud])
                    else:
                        if (dict_audiences[obj][2] > list_audiences[i_aud][4]) and \
                                (dict_audiences[obj][4].date() == list_audiences[i_aud][4].date()):
                            dict_audiences.append(dict_audiences[obj])
                            dict_audiences[obj-1] = list_audiences[i_aud]
                        else:
                            dict_audiences[obj] = list_audiences[i_aud]
                    break
                obj -= 1
            if obj < 0:
                dict_audiences.append(list_audiences[i_aud])


        print('-' * 30)
        list_audiences=[]
        for i in range(len(dict_audiences)):
            print(f'\n{dict_audiences[i][0]} type:{type(dict_audiences[i][0])} \n '
                  f'{dict_audiences[i][1] } type:{type(dict_audiences[i][1])}\n'
                  f'{str(dict_audiences[i][2])}  type:{type(dict_audiences[i][2])}\n'
                  f'{ str(dict_audiences[i][4])}  type:{type(dict_audiences[i][4])}')
            aud_obs1 = str(dict_audiences[i][3]).replace("'",'').replace('"','')
            tam = len(aud_obs1)
            tam = 150 if tam > 150 else tam
            aud_obs1 = aud_obs1[:tam]
            list_audiences.append(AudienciaModel(aud_prc_id=int(prc_id),aud_tipo=str(dict_audiences[i][0]),
                                                 aud_status=str(dict_audiences[i][1]),aud_data=dict_audiences[i][2],
                                                 aud_obs=aud_obs1))

        print('-' * 30)

        return list_audiences

    # PEGA DADOS DO PROCESSO
    def pegar_dados_do_prcesso(self):
        # PEGA DADOS DO PROCESSO E ATUALIZA TABELA
        wait = WebDriverWait(self.browser, 10)
        try:
            segredo = self.browser.find_element_by_id('main-content').text
            segredo = True if str(segredo).find('Segredo de justiça -') > -1 else False
        except (Exception, NoSuchElementException):
            segredo = None

        try:
            wait.until(EC.visibility_of_element_located(
                (By.XPATH,
                 '//*[@id="main-content"]/div/div[2]/detalhesprocesso/partial/div/div/div[1]/div[1]/cabecalhoprocesso/div/div/p/span[1]')))
            vara = self.browser.find_element_by_xpath(
                '//*[@id="main-content"]/div/div[2]/detalhesprocesso/partial/div/div/div[1]/div[1]/cabecalhoprocesso/div/div/p/span[1]').text
            vara = Tools.remove_accents(vara)
        except (Exception, NoSuchElementException, ElementClickInterceptedException, TimeoutException):
            vara = None

        try:
            wait.until(EC.visibility_of_element_located(
                (By.XPATH, '//*[@id="main-content"]/div/div[2]/detalhesprocesso/'
                           'partial/div/div/div[1]/div[1]/cabecalhoprocesso/div/div/p/span[3]')))
            assunto = self.browser.find_element_by_xpath('//*[@id="main-content"]/div/div[2]/detalhesprocesso/'
                                                         'partial/div/div/div[1]/div[1]/cabecalhoprocesso/'
                                                         'div/div/p/span[3]').text
            assunto = Tools.remove_accents(assunto)
        except (Exception, NoSuchElementException, ElementClickInterceptedException, TimeoutException):
            assunto = None

        try:
            wait.until(EC.visibility_of_element_located((
                By.XPATH,
                '//*[@id="main-content"]/div/div[2]/detalhesprocesso/partial/div/div/div[1]/div[1]/cabecalhoprocesso/div/div/div[2]/span[1]/')))
            status = self.browser.find_element_by_xpath(
                '//*[@id="main-content"]/div/div[2]/detalhesprocesso/partial/div/div/div[1]/div[1]/cabecalhoprocesso/div/div/div[2]/span[1]').text
            status = Tools.remove_accents(status)
        except (Exception, NoSuchElementException, ElementClickInterceptedException, TimeoutException):
            status = None

        print('\n----')
        print('segredo', segredo)
        print('vara', vara)
        print('assunto', assunto)
        print('status', status)
        print('\n----')
        return segredo, vara, assunto, status
