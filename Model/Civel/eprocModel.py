from Model.Civel.rootModel import RootModel
from Model.processoPlataformaModel import ProcessoPlataformaModel
from Model.toolsModel import *
from Model.parteModel import ParteModel
from Model.logErrorModel import LogErrorModelMutlThread
from Model.audienciaModel import AudienciaModel
from Model.responsavelModel import ResponsavelModel
from Model.acompanhamentoModel import AcompanhamentoModel
from Model.processoArquivoModel import ProcessoArquivoModel
from Model.processoPlataformaModel import ProcessoPlataformaModel
from Model.toolsModel import *
import codecs

class EprocModel(RootModel):

    def __init__(self, site, mode_execute, access, platform_id, platform_name, flag, num_thread, grau='1Grau'):
        self.platform_name = platform_name
        self.platform_id = platform_id
        self.flag = flag
        self.num_thread = num_thread
        self.grau = 1 if '1' in grau else '2'
        self.log_error = None
        self.state = "TO"
        super().__init__(site=site, mode_execute=mode_execute, SQL_Long=access, platform_id=platform_id,
                         platform_name=platform_name, estado=self.state,grau=self.grau)
        self.log_error = LogErrorModelMutlThread(platform_name=platform_name, state=self.state,
                                                 num_thread=self.num_thread, grau=self.grau)

    # MONTAR PROCESSO-PLATAFORMA
    def montar_processo_plataforma(self, prc_id, prc_numero, flag, plp_codigo) :

        process_platform = ProcessoPlataformaModel(plp_prc_id=prc_id, plp_plt_id=self.platform_id,
                                                   plp_codigo=plp_codigo, plp_grau=self.grau,
                                                   plp_numero=prc_numero, plp_segredo=False, plp_localizado=True)

        if flag :
            # PEGA DADOS DO PROCESSO E ATUALIZA TABELA
            juizo,classe,status,valor_causa,plp_serventia,plp_prioridade,\
            dt_distribuicao,plp_assunto = self.pegar_dados_do_prcesso()

            process_platform.plp_status=status
            process_platform.plp_juizo=juizo
            process_platform.plp_assunto=plp_assunto
            process_platform.plp_valor_causa=valor_causa
            process_platform.plp_classe=classe
            process_platform.plp_segredo=False
            process_platform.plp_data_distribuicao=dt_distribuicao
            process_platform.plp_localizado=1
            process_platform.plp_serventia=plp_serventia
            process_platform.plp_prioridade=plp_prioridade

        return process_platform

    # COLETA DO NUMERO DmO PROCESSO DO 2 GRAU E CRIAR O PLP COM HAJA NO 2º GRAU!
    def validar_bool_2_grau(self, bool_2_grau_numero, prc_numero, prc_id,bool_2_grau):

        list_plp_2_grau = []
        list_2_grau_numero = []
        if bool_2_grau_numero is None or bool_2_grau_numero :
            return []

        for i in self.browser.find_elements_by_xpath('//*[@id="tableRelacionado"]/tbody/tr'):

            td1 = i.find_element_by_xpath('td[1]/font/a').text
            td2 = i.find_element_by_xpath('td[3]').text

            if 'Dependente' in td2 and "/TJTO" in td1  :
                number_2_grau = re.sub("[^0-9]", '', td1)
                if number_2_grau not in prc_numero:
                    list_2_grau_numero.append(number_2_grau)
                    print('\n\n\t\tnumber_2_grau ',number_2_grau)

        list_2_grau_numero = set(list_2_grau_numero).difference(set(list_plp_2_grau))
        for i in list_2_grau_numero:
            list_plp_2_grau.append(
                ProcessoPlataformaModel(plp_prc_id=prc_id, plp_plt_id=5,
                                        plp_numero=prc_numero, plp_grau=2, plp_processo_origem=prc_numero)
            )


        return list_plp_2_grau

    def login(self, user, password) :
        try :
            wait = WebDriverWait(self.browser, 5)
            wait.until(EC.presence_of_element_located((By.ID, 'txtUsuario')))
            self.browser.find_element_by_id('txtUsuario').send_keys(user)
            self.browser.find_element_by_id('pwdSenha').send_keys(password, Keys.RETURN)

            wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="main-menu"]/li[4]/a')))
            self.browser.find_element_by_xpath('//*[@id="main-menu"]/li[4]/a').click()

            wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="menu-ul-3"]/li[1]/a')))
            self.browser.find_element_by_xpath('//*[@id="menu-ul-3"]/li[1]/a').click()

            return True
        except :
            raise
            return False

        # BUSCA PROCESSO NO EPROC

    def find_process(self, prc_numero,plp_codigo) :
        try :

            wait = WebDriverWait(self.browser, 4)

            wait.until(EC.presence_of_element_located((By.ID, 'numNrProcesso')))
            self.browser.execute_script('arguments[0].value="{}";'.format(prc_numero),
                                        self.browser.find_element_by_xpath('//*[@id="numNrProcesso"]'))
            self.browser.find_element_by_xpath('//*[@id="numNrProcesso"]').send_keys(Keys.RETURN)

            wait = WebDriverWait(self.browser, 1)
            wait.until(EC.visibility_of_element_located((By.ID, 'spnInfraAviso')))
            wait = WebDriverWait(self.browser, 60)
            wait.until(EC.invisibility_of_element_located((By.ID, 'spnInfraAviso')))
            situacao_da_busca = self.browser.find_elements_by_xpath('//*[@id="divInfraExcecao"]/span')

            return (not situacao_da_busca) or 'Processo não encontrado.' in situacao_da_busca[0].text
        except :

            return None

        # REALIZA NOVA CONSULTA NA PLATAFORMA

    def new_search(self,tempo) :
        if time.time() - tempo < 12 :
            sleep(abs(15-(time.time() - tempo)))
        try:
            self.browser.find_element_by_xpath('//*[@id="main-menu"]/li[4]/a').click()
        except:
            input("\n\n\n\t\t\t132")
        self.browser.find_element_by_xpath('//*[@id="menu-ul-3"]/li[1]/a').click()
        wait = WebDriverWait(self.browser, 5)
        wait.until(EC.presence_of_element_located((By.ID, 'numNrProcesso')))
        self.browser.find_element_by_xpath('//*[@id="numNrProcesso"]').clear()
        # SITUAÇÃO DO PROCESSO

    def secret_of_justice(self) :
        secret = self.browser.find_elements_by_id('divInfraExcecao')
        return len(secret) and 'Processo com segredo de justiça.' in secret[0].text


    # PEGA OS ENVOLVIDOS E RETORNA UMA LISTA COM AS PARTES E OS ADVOGADOS/JUIZ
    def envolvidos(self) :
        list_partes = []
        list_advogs = []

        self.carregar_envolvidos
        tabela_parte=self.browser.find_element_by_id('fldPartes')
        tr = tabela_parte.find_elements_by_class_name('infraTrClara')

        for envolvidos in tr :
            posicao_td=[1,2]
            polo_parte = ['Ativo','Passivo']
            for posi,polo in zip(posicao_td,polo_parte):
                # PARTES ATIVAS & PASSIVAS
                try :
                    if len(list(envolvidos.find_elements_by_xpath('td[{}]/span'.format(posi)))) < 1 or \
                        'Entidade' in envolvidos.find_element_by_xpath('td[{}]'.format(posi)).text :
                        continue
                    nome = envolvidos.find_element_by_xpath('td[{}]/span[1]'.format(posi)).text.split(',')[0]

                    nome = nome.replace("'",'').replace('"','')

                    cpf = envolvidos.find_elements_by_xpath('td[{}]'.format(posi))
                    cpf_cnpj=None
                    if len(cpf):
                        cpf = cpf[0].text

                        pi = cpf[0].find('(') + 1
                        pf = cpf.find(')')
                        cpf_cnpj = (cpf[pi :pf]).replace('.', '').replace('/', '').replace('-', '')
                        cpf_cnpj = re.sub("[^0-9]", '', cpf_cnpj)

                        if len(cpf_cnpj) < 11 or len(cpf_cnpj) > 20 :
                            cpf_cnpj = None
                    list_partes.append((ParteModel(prt_nome=nome.upper(), prt_cpf_cnpj=cpf_cnpj), polo))
                except :
                    # input('coleta de dados do partes {}!'.format(polo))

                    self.log_error.insert_log('coleta de dados da parte {}!'.format(polo))
                    raise

                # ADVOGADOS ATIVAS & PASSIVAS
                try :
                    text =envolvidos.find_element_by_xpath('td[{}]'.format(posi)).text
                    if text.find('\n\n')<0:
                        continue
                    text = text.split('\n\n')[-1]
                    text =  text.split('\n')

                    for j in text:
                        aux = j[10:-4]
                        nome,rsp_oab =  aux.split('  ')[:2]
                        nome = nome.replace("'",'').replace('"','')

                        list_advogs.append((ResponsavelModel(rsp_nome=nome,
                                                             rsp_tipo='Advogado(a)',
                                                             rsp_oab=rsp_oab), polo))
                except :

                    # input('coleta de dados do responsável {}!'.format(polo))


                    self.log_error.insert_log('coleta de dados do responsável {}!'.format(polo))
                    raise


        # JUÍZ(A)
        try :
            nome = self.browser.find_element_by_id('txtMagistrado').text
            list_advogs.append((ResponsavelModel(rsp_nome=nome.upper(),
                                                 rsp_tipo='Juíz(a)'.upper(),
                                                 rsp_oab='TO'), None))
        except :
            self.log_error.insert_log('coleta de dados do juíz!')
            raise


        self.print_if_parte(list_partes=list_partes,list_advogs=list_advogs)
        # input('deseja continuar')
        return list_partes, list_advogs

    def carregar_envolvidos(self):

            tabela_parte = self.browser.find_element_by_id('fldPartes')
            tam_tr = len(tabela_parte.find_elements_by_class_name('infraTrClara'))

            erro = True
            aux_click = self.browser.find_elements_by_xpath('//*[@id="carregarOutrosA"]/a')
            if len(aux_click):
                aux_click[0].click()
                erro = False
            else:
                aux_click = self.browser.find_elements_by_xpath('//*[@id="carregarOutrosR"]/a')
                if len(aux_click):
                    aux_click[0].click()
                    erro =False
            if not erro:
                tempo_inicial = time.time()
                while (time.time() - tempo_inicial) < 3:
                    tabela_parte = self.browser.find_element_by_id('fldPartes')
                    tam_tr_aux = len(tabela_parte.find_elements_by_class_name('infraTrClara'))
                    if tam_tr < tam_tr_aux:
                        break

    # PEGA ANDAMENTOS DO PROCESSO, AS AUDIÊNCIAS E REALIZA OS DOWNLOADS POR ACOMPANHAMENTO
    def acomp_down_aud(self, prc_id, ult_mov,bool_2_grau_numero,full):
        list_acomp_download = []
        file_downloaded = None
        list_file_path = []
        list_audiences = []
        list_name_urls = []
        list_references = []
        list_2_grau_numero = []
        not_refresh = 0
        err = False
        t = 0
        # PERCORRE A TABELA E FAZ O DOWNLOAD REFERENTE A CADA ACOMPANHAMENTO
        try :
            aux_data = self.browser.find_elements_by_xpath('//*[@id="tblEventos"]/tbody/tr[1]/td[2]')
            if len(aux_data) == 0:
                input("\n\n\n\t\t\t\t\t(//*[@id='tblEventos']/tbody/tr[1]/td[2])\n\n\n\n\n")
                raise
            aux_data = Tools.treat_date(aux_data[0].text)

            if ult_mov is not None:
                not_refresh += 1
                if aux_data <= ult_mov:
                    return list_audiences, list_acomp_download, list_name_urls, list_2_grau_numero, err, not_refresh

            aux_click = self.browser.find_elements_by_xpath('//*[@id="infraAjaxCarregarPaginasNormal"]/a[2]')
            if len(aux_click)>0:
                aux_click[0].click()
                wait = WebDriverWait(self.browser, 3)
                wait.until(EC.invisibility_of_element((By.ID,'infraAjaxCarregarPaginasNormal')))

            movimentos = self.browser.find_elements_by_xpath('//*[@id="tblEventos"]/tbody/tr')
            for movimento in movimentos :

                aux_data = Tools.treat_date(movimento.find_element_by_xpath('td[2]').text)
                if ult_mov is not None :
                    not_refresh += 1
                    if aux_data <= ult_mov :
                        break

                desc_process = movimento.find_element_by_xpath('td[3]').text.upper()
                desc_process = Tools.remove_accents(desc_process)
                if "Distribuido Agravo de Instrumento" in desc_process \
                        or "Distribuido Recurso Inominado" in desc_process \
                        or "Distribuido Apelacao / Reexame Necessario" in desc_process :
                    number_2_grau = desc_process.split(":")[-1]
                    number_2_grau = number_2_grau.split('/')[0]
                    number_2_grau = re.sub("[^0-9]", '', number_2_grau)
                    if number_2_grau not in list_2_grau_numero :
                        list_2_grau_numero.append(number_2_grau)

                n_event = int(movimento.find_element_by_xpath('td[1]').text)
                # print("n_event->",n_event)


                # REALIZA O DOWNLOAD DOS ANEXOS DE CADA ACOMPANHAMENTO
                list_files_to_download = movimento.find_elements_by_class_name('infraLinkDocumento')
                list_file_name = []
                acp_pra_status = None
                if len(list_files_to_download) :

                    for file in list_files_to_download :

                        tipo_arq = file.get_attribute("data-mimetype")
                        print(f'tipo_arq = {tipo_arq}')
                        try:

                            coordinate = file.location_once_scrolled_into_view
                            self.browser.execute_script(
                                'window.scrollTo({}, {});'.format(coordinate['x'], coordinate['y']))
                            file.click()

                            n_files = len(os.listdir(self.path_download_prov))
                            t += 1
                            wait = WebDriverWait(self.browser, 2)
                            wait.until(EC.number_of_windows_to_be(2))
                            self.browser.switch_to_window(self.browser.window_handles[-1])
                            if ("mp3" not in tipo_arq) and ("wma" not in tipo_arq):
                                try:
                                    iframe = self.browser.find_elements_by_id("conteudoIframe")
                                except:
                                    input("323")
                                    raise
                                main_content=[]
                                if len(iframe):
                                    self.browser.switch_to.frame(iframe[0])
                                    main_content = self.browser.find_elements_by_xpath('//*[@id="main-content"]/a')

                                if len(main_content):
                                    main_content[0].click()
                                    self.browser.close()
                                    self.browser.switch_to_window(self.browser.window_handles[0])
                                    err_down = self.wait_download(n_files)
                                else:
                                    completeName = os.path.join(self.path_download_prov,
                                                                Tools.convert_base(str(datetime.now())))
                                    file_object = codecs.open(completeName + '.html', "w", "utf-8")
                                    html = self.browser.page_source
                                    file_object.write(html)
                                    self.browser.close()
                                    self.browser.switch_to_window(self.browser.window_handles[0])  # vai para última aba
                                    err_down = False

                        except:
                            self.browser.switch_to_window(self.browser.window_handles[0])
                            self.log_error.insert_log('Download do arquivo: evento {}!'.format(n_event))
                            err_down = True
                            # input("deu erro ")
                            # raise


                        acp_pra_status = acp_pra_status and (not err_down)

                        nome = Tools.convert_base(str(datetime.now()))

                        desc_file = None
                        if not err_down:
                            for arq in os.listdir(self.path_download_prov):
                                if arq not in list_file_path:
                                    list_file_path.append(arq)
                                    file_downloaded = arq
                                    break

                            nome = Tools.convert_base(str(datetime.now()))
                            list_name_urls.append((nome, file_downloaded))
                            ext = file_downloaded.split('.')[-1].lower()
                            nome = nome + '.' + ext
                            desc_file = file_downloaded.split('.')[0]


                        list_file_name.append(ProcessoArquivoModel(pra_prc_id=prc_id, pra_nome=nome,
                                                                   pra_descricao=desc_file, pra_erro=err_down))
                        # VERIFICA SE A SESSÃO FOI ENCERRADA

                        if  ("mp3" not in tipo_arq and "wma"not in tipo_arq )and len(self.browser.window_handles) > 1:
                            self.browser.switch_to_window(self.browser.window_handles[1])
                            input("deseja continuar {}".format(len(self.browser.window_handles)))

                            self.browser.close()
                            acp_pra_status = False
                        self.browser.switch_to_window(self.browser.window_handles[0])

                list_acomp_download.append((AcompanhamentoModel(acp_esp=desc_process,
                                                                acp_numero=n_event,acp_tipo=n_event,
                                                                acp_data_cadastro=aux_data,
                                                                acp_prc_id=prc_id), list_file_name))
                # BUSCA AS AUDIÊNCIAS
                t=time.time()
                self.buscar_as_audiencia(list_audiences=list_audiences,list_references=list_references,
                                         movimentos=movimentos,n_event=n_event)
                # print(' Tempo -> ',time.time()-t)

            list_audiences = self.treat_audience(list_audiences=list_audiences,prc_id=prc_id)

        except :
            list_acomp_download.clear()
            list_name_urls.clear()
            list_audiences.clear()
            list_2_grau_numero.clear()
            self.log_error.insert_log('coleta de dados dos acompanhamentos do processo!'.upper())
            err = True
            raise
        # print(len(list_acomp_download), '->len(list_acomp_download)')
        return list_audiences, list_acomp_download, list_name_urls, list_2_grau_numero, err, not_refresh

    # TRATA AS AUDIÊNCIAS
    def treat_audience(self, list_audiences, prc_id):

        # TRATA AS AUDIÊNCIAS
        dict_audiences = {}
        list_audiences.reverse()
        for i_aud in list_audiences:
            # noinspection PyUnresolvedReferences
            audience = i_aud[1].split(' - ')
            # print(audience)
            audience[-1] = audience[-1] if (audience[-1][0] != ' ') else audience[-1][1:]
            # print(i_aud[0], audience)
            if 'REFER' in audience[-1]:
                data, number_event = audience[-1].split('. REFER. EVENTO')
                number_event = int(number_event)
                data = Tools.treat_date(data) if (data[-1] != ' ') else Tools.treat_date(data[:-1])

                j = 1
                while j < len(audience) and 'LOCAL' not in audience[j]:
                    j += 1
                j = -1 if j >= len(audience) else j
                if 'CANCELADA' in audience[0] or 'NAO REALIZADA' in audience[0] or \
                        'CANCELADA' in audience[2] or 'NAO REALIZADA' in audience[2]:
                    try:
                        dict_audiences[number_event].aud_status = 'CANCELADA/NAO REALIZADA'
                    except KeyError:
                        pass
                        # print(i_aud[0], audience)
                elif 'REALIZADA' in audience[0] or 'REALIZADA' in audience[2]:
                    try:
                        dict_audiences[number_event].aud_status = 'REALIZADA'
                        dict_audiences[number_event].aud_data = data
                        if j > -1:
                            obs = '-'.join(str(e) for e in audience[j:-1]).split('LOCAL ')[-1]
                            dict_audiences[number_event].aud_obs = obs
                    except KeyError:
                        pass
                        # print(i_aud[0], audience)
                elif 'REDESIGNADA' in audience[0] or 'REDESIGNADA' in audience[2]:
                    obs = '-'.join(str(e) for e in audience[3:-1]).split('LOCAL ')[-1]
                    dict_audiences[i_aud[0]] = AudienciaModel(aud_prc_id=prc_id,
                                                              aud_tipo=audience[1],
                                                              aud_status='REDESIGNADA',
                                                              aud_obs=obs,
                                                              aud_data=data)
            else:
                if len(audience) > 2:
                    obs = '-'.join(str(e) for e in audience[3:-1]).split('LOCAL ')[-1]
                    dict_audiences[i_aud[0]] = AudienciaModel(aud_prc_id=prc_id,
                                                              aud_tipo=audience[1],
                                                              aud_status=audience[2],
                                                              aud_obs=obs,
                                                              aud_data=Tools.treat_date(audience[-1]))

        list_audiences.clear()
        list_aux = []
        for i in dict_audiences.values():
            if id(i) not in list_aux:
                list_audiences.append(i)
                list_aux.append(id(i))
                print(f"\n\n\t\t\t Tipo : {i.aud_tipo} \n\t\t\t Status: {i.aud_status} \n\t\t\t data : {i.aud_data} \n\t\t\t obs: {i.aud_obs}")

        return list_audiences

    # BUSCA AS AUDIÊNCIAS
    def buscar_as_audiencia(self,list_audiences,list_references,movimentos,n_event):
        razao =    len(movimentos) - n_event   if n_event >  len(movimentos)  else 0
        # print(f"razao- > {razao}")
        razao = self.validar_n_evento(movimentos=movimentos,n_event=n_event,razao=razao)
        desc_process = Tools.remove_accents(movimentos[-(n_event+razao)].find_element_by_xpath('td[3]').text)
        desc_process = normalize('NFKD', desc_process).encode('ASCII', 'ignore').decode('ASCII')
        desc_process = desc_process.upper()
        while 'AUDIENCIA' in desc_process.split(' - ')[0] and n_event not in list_references:
            list_audiences.append((n_event, desc_process))
            list_references.append(n_event)
            try:
                n_event += int(desc_process.split('REFER. EVENTO')[-1])
                razao = self.validar_n_evento(movimentos=movimentos, n_event=n_event, razao=razao)
                desc_process = Tools.remove_accents(movimentos[-(n_event+razao)].find_element_by_xpath('td[3]').text)
                desc_process = normalize('NFKD', desc_process).encode('ASCII', 'ignore').decode('ASCII')
                desc_process = desc_process.upper()
            except Exception:
                break

    # VALIDAR NUMERO DO EVENTO
    def validar_n_evento(self,movimentos,n_event,razao):
        aux_n_evente = int(movimentos[-(n_event + razao)].find_element_by_xpath('td[1]').text)
        conte= 10
        while conte and aux_n_evente != n_event:
            conte-=1
            razao += n_event - aux_n_evente

            aux_n_evente = int(movimentos[-(n_event + razao)].find_element_by_xpath('td[1]').text)

        return  razao

    # PEGA DADOS DO PROCESSO
    def pegar_dados_do_prcesso(self) :
        # PEGA DADOS DO PROCESSO E ATUALIZA TABELA
            valor_causa = None
            classe = None
            juizo = None
            status = 'ATIVO'
            dt_distribuicao = None
            prc_serventia = None

            imgStatusAssunto = self.browser.find_elements_by_xpath('//*[@id="fldAssuntos"]/legend')
            if len(imgStatusAssunto)>0:
                self.browser.execute_script("infraAbrirFecharElementoHTML('conteudoAssuntos2', 'imgStatusAssunto');")

            imgStatusInfAdicional = self.browser.find_elements_by_xpath('//*[@id="imgStatusInfAdicional"]')
            if len(imgStatusInfAdicional)>0:
                self.browser.execute_script("infraAbrirFecharElementoHTML('conteudoInfAdicional', 'imgStatusInfAdicional');")

            classe = self.browser.find_element_by_id('txtClasse').text.upper()

            juizo = self.browser.find_element_by_id('txtOrgaoJulgador').text.upper()

            status_aux = self.browser.find_element_by_id('txtSituacao').text.upper()
            if 'ARQUIVADO DEFINITIVAMENTE' in status_aux or 'ARQUIVADO' in status_aux or 'BAIXADO' in status_aux :
                status = 'ARQUIVADO'

            dt_distribuicao = self.browser.find_element_by_id('txtAutuacao').text
            dt_distribuicao = Tools.treat_date(dt_distribuicao)

            plp_serventia =  self.browser.find_element_by_id('txtOrgaoJulgador').text



            plp_assunto = self.browser.find_element_by_xpath('//*[@id="conteudoAssuntos2"]/table/tbody/'
                                                             'tr[2]/td[2]').text

            plp_prioridade = self.browser.find_element_by_xpath('//*[@id="conteudoInfAdicional"]/table/tbody/tr[3]/'
                                                        'td[2]').text

            plp_prioridade = "Não" not in plp_prioridade


            valor_causa_text = self.browser.find_elements_by_xpath('/html/body/div[1]/div[2]/div[2]/div/div/form/div[2]/div/div/b/b/fieldset[4]/div/table/tbody/tr[6]/td[6]/label')

            if len(valor_causa_text):
                # print('valor_causa_text[0].text',valor_causa_text[0].text)
                # input("\n\n\n\t\t\t{}\n\n".format(valor_causa_text[0].text))
                valor_causa = Tools.treat_value_cause(valor_causa_text[0].text)




            print('\n----')
            print('\t\tjuizo :', juizo)
            print('\t\tclasse :', classe)
            print('\t\tstatus :', status)
            print('\t\tvalor_causa : ', valor_causa)
            print('\t\tplp_serventia : ', plp_serventia)
            print('\t\tplp_prioridade : ', plp_prioridade)
            print('\t\tdt_distribuicao : ', dt_distribuicao)
            print('\t\tplp_assunto : ', plp_assunto)
            print('\n----')
            # input('deseja continuar')

            return juizo,classe,status,valor_causa,plp_serventia,plp_prioridade,dt_distribuicao,plp_assunto

    # VAlIDANDOS SE NUMERO DO PROCESSO CONTIDO NA PLATAFORMA E O MESMO CONTIDO NO SITE
    def validar_numero_plataforma(self, prc_numero) :
            try:
                wait = WebDriverWait(self.browser, 5)
                # input('Deseja continuar !')
                wait.until(EC.presence_of_element_located((By.ID, 'txtNumProcesso')))
            except:
                return True

            numero_no_site = self.browser.find_element_by_id('txtNumProcesso').text
            numero_no_site = re.sub('[^0-9]', '', numero_no_site)
            prc_numero = re.sub('[^0-9]', '', prc_numero)
            return prc_numero not in numero_no_site
