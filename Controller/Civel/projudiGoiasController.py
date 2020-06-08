from selenium.webdriver.common import alert

from Model.toolsModel import *
from Model.parteModel import ParteModel
from Model.Civel.projudiModel import ProjudiModel
from Model.logErrorModel import LogErrorModelMutlThread
from Model.audienciaModel import AudienciaModel
from Model.responsavelModel import ResponsavelModel
from Model.acompanhamentoModel import AcompanhamentoModel
from Model.processoArquivoModel import ProcessoArquivoModel
from Model.processoPlataformaModel import ProcessoPlataformaModel

class projudiGoiasController(ProjudiModel):
    # CONSTRUTOR DA CLASSE
    def __init__(self, site, mode_execute, access, platform_id, platform_name, flag, num_thread, grau=1):

        super().__init__(site=site, mode_execute=mode_execute, SQL_Long=access, platform_id=platform_id,
                         platform_name=platform_name, state='GO', grau=grau)
        self.platform_name = platform_name
        self.platform_id = int(platform_id)
        self.flag = flag
        self.num_thread = num_thread

        self.log_error = LogErrorModelMutlThread(platform_name=platform_name, state=self.state,
                                                 num_thread=self.num_thread, grau=grau)

    # MONTAR PROCESSO-PLATAFORMA  ************* PRONTO *************
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

            process_platform = ProcessoPlataformaModel(plp_prc_id=prc_id, plp_plt_id=self.platform_id,plp_codigo=plp_codigo,
                                                       plp_numero=prc_numero, plp_segredo=False, plp_localizado=True)

        return process_platform

    # REALIZA LOGIN ************* PRONTO *************
    def login(self, user, password):
        try:
            self.browser.find_element_by_id('login').send_keys(user)
            self.browser.find_element_by_id('senha').send_keys(password, Keys.RETURN)

            wait = WebDriverWait(self.browser, 10)
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="divCorpo"]/fieldset[1]/label/a')))
            self.browser.find_element_by_xpath('//*[@id="divCorpo"]/fieldset[1]/label/a').click()


            wait = WebDriverWait(self.browser, 10)
            wait.until(EC.presence_of_element_located((By.ID, 'Principal')))
            iframe = self.browser.find_element_by_id('Principal')


            self.browser.switch_to.frame(iframe)
            wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div[1]/h2')))
            return True
        except Exception as e:
            print('\n********************\nERRO LOGIN REINICIANDO O NAVEGADOR\n********************/\n')
            return False

    # BUSCA PROCESSO NO PROJUDI ************* PRONTO (VERIFICAR ERRO DE PERMISSÃO DO USUARIO) *************
    # DEU 1 ERRO DE LOGADO EM OUTRA MAQUINA
    def find_process(self, prc_numero, plp_codigo):
        # RETORNA TRUE SE TIVER ENCONTRADO
        # IF PARA PROCESSO QUE JÁ FOI BUSCADO PELO MENOS UMA VEZ

        if plp_codigo is not None:
            self.browser.get('https://projudi.tjgo.jus.br/BuscaProcessoUsuarioExterno?PaginaAtual=-1&Id_Processo={}'
                             '&PassoBusca=2'.format(plp_codigo))
            return True

        # EXECUTA 3 TENTATIVAS DE ACESSO A PAGINA DE BUSCA DE PROCESSO
        tentativas = 3
        while tentativas > 0:

            try:
                self.browser.get(
                    'https://projudi.tjgo.jus.br/BuscaProcessoUsuarioExterno?PaginaAtual=2&Proprios=0')
                break
            except:
                tentativas -= 1
                if tentativas == 0:
                    self.reiniciar_browser()


        # VERIFICAR SE DEU ERRO DE USUARIO NA PAGINA ****************************************************************

        # CLICA NO 'X' PARA REMOVER O ATIVO
        wait = WebDriverWait(self.browser, 20)
        wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="divEditar"]/fieldset/fieldset/label[1]/input[4]')))
        self.browser.find_element_by_xpath('//*[@id="divEditar"]/fieldset/fieldset/label[1]/input[4]').click()

        # INSERE O NUMERO DO PROCESSO NO SEU CAMPO DEVIDO
        wait = WebDriverWait(self.browser, 5)
        wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div/form/div/fieldset/input[1]')))
        self.browser.find_element_by_xpath('/html/body/div/form/div/fieldset/input[1]').send_keys(
            "{}.{}".format(prc_numero[:7],prc_numero[7:9]))

        # CLICA NO BOTÃO 'Buscar'
        self.browser.find_element_by_xpath('//*[@id="divBotoesCentralizados"]/input[1]').click()

        # IF PARA VERIFICAR SE O PROCESSO NÃO FOI LOCALIZADO
        if not self.browser.find_elements_by_id('Tabela'):
            return False

        # FOR VARE A TABELA QUE EXIBE LOGO APOS A BUSCA DO PROCESSO E ABRE O PROCESSO
        find = self.browser.find_elements_by_xpath('//*[@id="tabListaProcesso"]/tr')
        for tr in find:
            if len(tr.find_elements_by_xpath('td')) > 1:
                dt_proc = tr.find_element_by_xpath('td[6]').text.split('/')[-1]
                if dt_proc == prc_numero[9:13]:
                    a = tr.find_element_by_xpath('td[4]')

                    att_onClick = a.get_attribute('onclick')
                    self.browser.execute_script(str(att_onClick))
                    break
        return True


    # SOLICITA ACESSO AOS ARQUIVOS DO PROCESSO ************* PRONTO *************
    def request_access(self):
        #COLETA E TRATA O plp_codigo

        plp_codigo = None
        els = self.browser.find_elements_by_tag_name('img')
        for e in els:
            url = e.get_attribute('onclick')

            if url is not None and '&PaginaAtual' in url:
                    plp_codigo = str(url).split('&PaginaAtual')[0]
                    plp_codigo = plp_codigo.split('Processo=')[-1]
                    break

        return plp_codigo


    # VERIFICA SE O PROCESSO ESTA EM SEGREDO DE JUSTICA ************* PRONTO *************
    def secret_of_justice(self):


        secrets = self.browser.find_elements_by_xpath('//*[@id="tabListaProcesso"]/tr[2]/td/div')
        if len(secrets) > 0:
            if 'SEGREDO' in secrets[0].text.upper():
                return True

        return False


    # PEGA OS ENVOLVIDOS E RETORNA UMA LISTA COM AS PARTES E OS ADVOGADOS/JUIZ ************* PRONTO *************
    def envolvidos(self):
        list_partes = []
        list_advogs = []
        try:
            # ABRE A JANELA DOS RESPONSAVEIS PELO PROCESSO
            wait = WebDriverWait(self.browser, 10)
            wait.until(EC.visibility_of_all_elements_located((By.NAME, 'inputResponsaveisProcesso')))
            self.browser.find_element_by_name('inputResponsaveisProcesso').click()


            # COLETA O NOME DOS JUIZES E TRATA CASO OUVE MUDANÇA DE JUIZ NO PROCESSO
            table = self.browser.find_elements_by_xpath('//*[@id="Responsaveis"]/tbody/tr')
            for tr in table:
                nome_juiz = tr.find_element_by_xpath('td[3]').text.upper()
                nome_juiz = nome_juiz.split('SUBSTITUINDO')[0]
                list_advogs.append((ResponsavelModel(rsp_nome=nome_juiz,
                                                     rsp_tipo='Juíz(a)',
                                                     rsp_oab='GO'), None))

            # COLETA DAS PARTES E RESPONSÁVEIS
            # PARTE ATIVA

            # CAPTURA O NOME DA PARTE ATIVA
            nome_parte = self.browser.find_element_by_xpath('//*[@id="divCorpo"]/fieldset/fieldset[1]/span[1]').text

            # COLETA O CPF/CNPF DA PARTE ATIVA
            cpf_cnpj_parte = self.browser.find_element_by_xpath(
                '//*[@id="divCorpo"]/fieldset/fieldset[1]/span[2]').text

            # REMOVE . e - DO CPF/CNPF
            cpf_cnpj_parte = re.sub('[^0-9]', '', cpf_cnpj_parte)
            list_partes.append((ParteModel(prt_nome=nome_parte.upper(),

                                               prt_cpf_cnpj=cpf_cnpj_parte), 'Ativo'))

            # COLETA DA PARTE PASSIVA
            nome_parte = self.browser.find_element_by_xpath('//*[@id="divCorpo"]/fieldset/fieldset[2]/span[1]').text

            # COLETA O CPF/CNPF DA PARTE PASSIVA
            cpf_cnpj_parte = self.browser.find_element_by_xpath(
                '//*[@id="divCorpo"]/fieldset/fieldset[2]/span[2]').text

            # REMOVE . e - DO CPF/CNPF
            cpf_cnpj_parte = re.sub('[^0-9]', '', cpf_cnpj_parte)

            # ADICIONA AS PARTES NA LISTA DE PARTES
            list_partes.append((ParteModel(prt_nome=nome_parte.upper(),
                                           prt_cpf_cnpj=cpf_cnpj_parte), 'Passivo'))

            # COLETA OS ADVOGADOS DAS PARTES ATIVAS E PASSIVAS
            table = self.browser.find_elements_by_xpath('//*[@id="Advogados"]/tbody/tr')

            l_responsavel = []

            # IDENTIFICA  A PARTE REFERENTE A CADA ADVOGADO
            for tr in table:
                # COLETA O NOME DA PARTE
                c_parte = tr.find_element_by_xpath('td[7]').text.split(' - ')

                # IDENTIFICA SE A PARTE É PASSIVA OU ATIVA
                polo = c_parte[-1].split(' ')[-1]

                # COLETA O NOME DO ADVOGADO
                nome_responsavel = tr.find_element_by_xpath('td[1]').text

                # COLETA NUMERO DA MATRICULA DA OAB
                oab = tr.find_element_by_xpath('td[2]').text

                # INSERE OS ADVOGADOS EM SUAS DEVIDAS LISTA SEPARDOS POR ATIVOS E PASSIVOS
                if polo == 'Ativo':
                    if nome_responsavel not in l_responsavel:
                        l_responsavel.append(nome_responsavel)

                        list_advogs.append((ResponsavelModel(rsp_nome=nome_responsavel.upper(),
                                                             rsp_tipo='Advogado(a)',
                                                             rsp_oab=oab), 'Ativo'))

                if polo == 'Passivo':
                    if nome_responsavel not in l_responsavel:
                        l_responsavel.append(nome_responsavel)
                        #l_responsavel= Tools.remove_caractere_especial(l_responsavel)
                        list_advogs.append((ResponsavelModel(rsp_nome=nome_responsavel.upper(),
                                                             rsp_tipo='Advogado(a)',
                                                             rsp_oab=oab), 'Passivo'))

            # RETORNA PARA O PROCESSO E SUAS MOVIMENTAÇÕES
            self.browser.find_element_by_xpath('//*[@id="divCorpo"]/fieldset/span/a').click()
        except:
            list_partes.clear()
            list_advogs.clear()



        # IMPRIME AS PARTES NO PROMPT
        self.print_if_parte(list_partes, list_advogs)
        return list_partes, list_advogs

    # PEGA ANDAMENTOS DO PROCESSO, AS AUDIÊNCIAS E REALIZA OS DOWNLOADS POR ACOMPANHAMENTO
    def acomp_down_aud(self, prc_id, ult_mov, bool_2_grau_numero,full = False):

    # RETORNA LISTAS VAZIAS E A VARIAVEL err COMO True CASO DE ALGUM ERRO

        # INICIALIZA TODAS AS VARIAVEIS
        list_acomp_download = []
        list_file_path = []
        list_audiences = []
        list_name_urls = []
        not_refresh = 0
        err = False

        t0 = time.time()

        # COLETA DE DADOS PARA CRIAÇÃO DOS ACOMPANHAMENTOS E DOWNLOAD DOS ARQUIVOS
        try:
            print("\t\tCONFERINDO SE EXISTE MOVIMENTACAO NOVA", end='')

            # XPATH DA DATA DA ULTIMA MOVIMENTAÇÃO
            xpath_aux_data = '//*[@id="TabelaArquivos"]/tbody/tr[1]/td[3]'

            # AGUARDA AS MOVIMENTAÇÕES APARECEREM
            wait = WebDriverWait(self.browser, 20)
            wait.until(EC.presence_of_all_elements_located((By.XPATH, xpath_aux_data)))

            # COLETA E TRATA A DATA DA ULTIMA MOVIMENTAÇÃO
            aux_data = self.browser.find_element_by_xpath(xpath_aux_data)
            aux_data.location_once_scrolled_into_view
            aux_data = self.browser.find_element_by_xpath(xpath_aux_data).text

            aux_data = Tools.treat_date(aux_data)

            # CASO A VARIAVEL ult_mov FOR None QUER DIZER QUE O PROCESSO É A PRIMEIRA VEZ QUE ESTA SENDO PROCURADO
            if ult_mov is not None:
                not_refresh += 1
                if aux_data <= ult_mov and not full:
                    return list_audiences, list_acomp_download, list_name_urls, None, err, not_refresh
        except TimeoutException:
            print('ERRO  AO PEGA ANDAMENTOS DO PROCESSO E AS AUDIÊNCIAS DO PROCESSO! REINICIANDO O NAVEGADOR...')
            input('timeOut')
            return [],[],[],False ,True, True

        print("\n\tPEGANDO ANDAMENTOS/AUDIENCIA", end='')

        # VERIFICA SE A SESSAO ESTA ATIVA
        t = time.time()

        # É UM BOTÃO QUE TA ESCRITO OUTRAS TAMBEM N
        el = self.browser.find_element_by_id('menu_outras').text

        # VERIFICAÇÃO DE ERRO (NÃO ACHEI NENHUM PROCESSO QUE CAI NESSA CONDIÇÃO, NÃO TIREI POR VIA DAS DUVIDAS....)
        els = self.browser.find_elements_by_xpath('/html/body/div[5]/div[3]/div/button')

        if el.strip() == '' or len(els) > 0:
            return [],[],[],False ,True, True

        print("\tSOLICITACAO DE ACESSO AOS ANEXOS DO PROCESSO ->>", time.time() - t)
        # SOLICITA ACESSO AOS ANEXOS DO PROCESSO

        # GET NO LINK QUE REGISTRA A SOLICITAÇÃO DE ACESSO
        self.browser.get('https://projudi.tjgo.jus.br/DescartarPendenciaProcesso?PaginaAtual=8')

        # FECHA O ALERTE QUE É EXIBIDO QUANDO O GET É EXECUTADO
        btn = self.browser.find_elements_by_xpath('/html/body/div[5]/div[3]/div/button')
        if len(btn):
            btn[0].click()
        # CAPTURA TABELA DE MOVIMENTAÇÕES
        movimentacoes = self.browser.find_elements_by_xpath('//*[@id="TabelaArquivos"]/tbody/tr')

        # TRATA AS MOVIMENTAÇÕES
        for i in range(1,len(movimentacoes)):

            # APENAS LINHAS IMPARES PODEM SÃO MOVIMENTAÇÕES!
            if i % 2 != 0:
                # CAPTURA A DATA DA MOVIMENTAÇÃO aux_data
                xpath_aux_data = '/html/body/div[2]/form/div[1]/div/div[1]/table/tbody/tr[{}]/td[3]'.format(i)
                aux_data = self.browser.find_element_by_xpath(xpath_aux_data)
                aux_data.location_once_scrolled_into_view
                aux_data = self.browser.find_element_by_xpath(xpath_aux_data).text
                # GARANTE QUE A MOVIMENTAÇÃO ESTA VISIVEL PARA O USUARIO E EVITA ERRO DE NÃO POSSIVEL SELECIONAR
                xpath_aux_data_secundario = '/html/body/div[2]/form/div[1]/div/div[1]/table/tbody/tr[{}]/td[3]'.format(i if i-2 <= 0 else i-2)
                roll = self.browser.find_element_by_xpath(xpath_aux_data_secundario)
                roll.location_once_scrolled_into_view

                # TRATA A DATA [aux_data = datetime(int(ano), int(mes), int(dia), int(hr), int(mt), int(seg))]
                aux_data = Tools.treat_date(aux_data)

                # SERVE PARAR QUANDO ESTIVER CHEGADO EM UMA MOVIMENTAÇÃO JÁ ARMAZENADA NO BANCO
                if ult_mov is not None:
                    not_refresh += 1
                    if aux_data <= ult_mov:
                        break

                # PREPARA O XPATH E DIRECIONA A MOVIMANETAÇÃO
                xpath_descri_mov = '/html/body/div[2]/form/div[1]/div/div[1]/table/tbody/tr[{}]/'.format(i)

                # COLETA A DESCRIÇÃO
                desc_process = self.browser.find_element_by_xpath(xpath_descri_mov + 'td[2]').text.upper()

                # COLETA O NUMERO DA MOVIMENTAÇÃO
                n_event = self.browser.find_element_by_xpath(xpath_descri_mov + 'td[1]').text

                # PEGAR AS AUDIÊNCIAS
                if 'AUDIENCIA' in desc_process:
                    list_audiences.append(desc_process)

                list_file_name = []

                # TRATA O XPATH PRA VERIFICAR SE TEM DOWLOAD
                xpath_aux_click = '//*[@id="TabelaArquivos"]/tbody/tr[{}]/td[5]/a'.format(i)

                # NÃO É TODOS QUE TEM ENTÃO FAZ A VERIFICAÇÃO SE ESSA MOVIMENTAÇÃO TEM DOWNLOAD
                els = self.browser.find_elements_by_xpath(xpath_aux_click)
                if len(els) > 0:
                    # ABRE A ABA DE CONTEUDO DA MOVIMENTAÇÃO O MESMO QUE CLICAR NELE POREM MENOS PASSIVO DE ERRO
                    acp_pra_status = None
                    js = els[0].get_attribute('href').split('javascript:')
                    self.browser.execute_script(js[1])

                    # AGUARDA A ABA COM OS ARQUIVOS PARA DOWLOAD
                    # CASO DE ERRO RETORNA UMA TODAS AS LISTAS VAZIAS E A VARRIAVEL err RECEBE True
                    try:
                        wait = WebDriverWait(self.browser, 15)
                        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'serrilhado')))
                    except TimeoutException:
                        return [], [], [], False, True, True

                    # VERIFICA SE TEM ALGUMA CAIXA DE DIALOGO NA TELA
                    if not self.check_file_session():
                        return [], [], [], False, True, True

                    # BAIXA OS ANEXOS
                    if not self.baixar_anexos(i=i,list_name_urls= list_name_urls
                            ,list_file_name=list_file_name,els=els,t=t,acp_pra_status=acp_pra_status,
                            list_file_path=list_file_path,prc_id=prc_id,n_event=n_event,js=js):
                        return [], [], [], False, True, True


                print('### TEMPO DE CAPTURA DO ACOMPANHAMENTO: {} SECS'.format(time.time() - t0).upper())

                list_acomp_download.append((AcompanhamentoModel(acp_esp=desc_process,acp_numero=n_event,acp_tipo=n_event,
                                                                acp_data_cadastro=aux_data,acp_prc_id=prc_id),
                                         list_file_name))

        # PEGA AS AUDIÊNCIAS DA PÁGINA ESPECÍFICA DE AUDIÊNCIAS
        self.browser.get('https://projudi.tjgo.jus.br/BuscaProcessoUsuarioExterno?PaginaAtual=1')

        # PEGA AS AUDIENCIAS EM ABERTO
        auds = self.browser.find_elements_by_xpath('//*[@id="VisualizaDados"]/fieldset[3]/table/tb')

        # TRATA AS AUDIENCIAS E INSERE NA LISTA
        for aud in auds:
            desc_process = aud.find_element_by_xpath('td').text.upper().split(' ')
            if 'AUDIENCIA' in desc_process[0]:
                list_audiences.append(desc_process.split('AUDIENCIA DE ')[-1])

        # RETORNA PARA A PAGINA DO PROCESSO
        self.browser.find_element_by_xpath('//*[@id="divCorpo"]/form/fieldset/span/a').click()

        self.trata_audiencias(list_audiences=list_audiences,prc_id=prc_id)

        return list_audiences, list_acomp_download, list_name_urls, None, err, not_refresh

    # VALIDA SE O NUMERO DO PROCESSO CONTIDO NA PLATAFORMA E O MESMO CONTIDO NA BASE ***************************** PRONTO *************************
    def validar_numero_plataforma(self, prc_numero):
    # RETORNA False SE O NUMERO FOR CORRETO

        # TRATA SEGREDO DE JUSTIÇA
        if self.secret_of_justice():
            self.browser.find_element_by_xpath('/html/body/div/form/div[2]/div[2]/table/tbody/tr[1]/td[7]/input').click()

        # VERIFICA SE O NUMERO DO PROCESSO JÁ APARECEU E CAPTURA O TEXTO
        wait = WebDriverWait(self.browser, 5)
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/form/div[1]/fieldset/span[1]')))

        numero_no_site = self.browser.find_element_by_xpath('/html/body/div[2]/form/div[1]/fieldset/span[1]').text
        # REMOVE OS . E - DO NUMERO DO PROCESSO
        numero_no_site = re.sub('[^0-9]', '', numero_no_site)
        return prc_numero not in numero_no_site

    # BAIXA OS ANEXOS E CRIA ACOMPANHAMENTO ASSOCIANDO OS ANEXOS CONTIDOS NELES
    def baixar_anexos(self,i,list_name_urls,list_file_name,els,t,acp_pra_status,list_file_path,prc_id,n_event,js):
        # BAIXA OS ANEXOS E CRIA ACOMPANHAMENTO ASSOCIANDO OS ANEXOS CONTIDOS NELES
        xpath_aux_docs = '//*[@id="TabelaArquivos"]/tbody/tr[{}]/'.format(i + 1)
        # PEGA A LINHA QUE TA OS DOWNLOAD
        xpath_aux_docs += 'td/ul/li'

        wait = WebDriverWait(self.browser, 10)
        try:
            wait.until(EC.presence_of_element_located((By.XPATH, xpath_aux_docs)))
        except:
            pass

        ul_files = self.browser.find_elements_by_xpath(xpath_aux_docs)
        if len(ul_files) > 0:
            ul_files[0].location_once_scrolled_into_view

        ul_files = self.browser.find_elements_by_xpath(xpath_aux_docs)
        j = 0
        for li in ul_files:
            j +=1
            direct = 0
            n_files = len(os.listdir(self.path_download_prov))

            # COLETA ARQUIVO PARA DOWLOAD
            li_els = li.find_elements_by_xpath('div[2]/div[1]/a')

            # SALVA OS ARQUIVOS
            if len(els) == 0:
                self.browser.execute_script(js[1])
                sleep(1)
                self.browser.execute_script(js[1])
                li_els = li.find_elements_by_xpath('div[2]/div[1]/a')

            # CAPTURA OS DOCUMENTOS
            doc_els = li.find_elements_by_xpath('div[1]/span')

            # VERIFICA SE TEM DOC PRA PEGAR
            if len(doc_els) > 0:
                # VERIFICA SE O DOWNLOAD TA BLOQUEADO
                if 'Bloqueado' in doc_els[0].text:
                    continue

            # PEGA O TITULO DO ARQUIVO
            title = li_els[0].get_attribute('title').lower()

            # VERIFICA SE TEM PDF PARA DOWNLOAD
            pdf = li.find_elements_by_xpath('div[4]/div/a')

            if '.wav' in title:
                arq = open('ProcessoContemAudio.txt', 'r')
                string = arq.read()
                arq.close()

                arq = open('ProcessoContemAudio.txt', 'w')
                string += '\n'

                n_process = self.browser.find_element_by_xpath('/html/body/div[2]/form/div[1]/fieldset/span[1]').text
                string += n_process

                arq.write(string)
                arq.close()

            if not self.check_file_session():
                print("erro o check_file_session")
                return False
            if '.mp3' in title or len(pdf) == 0:
                if '.html' in title:
                    li_els[0].click()
                    arq = title.split('.html')
                    direct = 1
                    self.donwloadAcompanhamento(arq[0])
                else:
                    # document.createElement('div');
                    self.browser.execute_script('arguments[0].setAttribute("download", "");', li_els[0])
                    li_els[0].click()
            else:
                pdf[0].click()

            try:
                alert = self.browser.switchTo().alert();
                alert.accept();
            except:
                pass

            t += 1
            try:
                wait = WebDriverWait(self.browser, 2)
                wait.until(EC.number_of_windows_to_be(2))
                wait = WebDriverWait(self.browser, 20)
                wait.until(EC.number_of_windows_to_be(1))
            except TimeoutException:
                if len(self.browser.window_handles) > 1:
                    self.browser.switch_to_window(self.browser.window_handles[1])
                    time.sleep(4)
                    erro = self.browser.find_elements_by_class_name('texto_erro')
                    if len(erro) > 0 and 'Sem Permis' in erro[0].text:
                        self.browser.close()
                        self.browser.switch_to_window(self.browser.window_handles[0])
                        return False

            tipe_err_down = -1
            err_down = self.wait_download(n_files) if not direct else 0

            acp_pra_status = acp_pra_status and (not err_down)

            xpath_dowload_arquivo = xpath_aux_docs + '[{}]/div[2]/div[1]/a'
            xpath_dowload_arquivo = xpath_dowload_arquivo.format(j)

            wait = WebDriverWait(self.browser, 10)
            wait.until(EC.element_to_be_clickable((By.XPATH, xpath_dowload_arquivo)))
            desc_file = self.browser.find_element_by_xpath(xpath_dowload_arquivo).text

            nome = Tools.convert_base(str(datetime.now()))

            if not err_down:
                for arq in os.listdir(self.path_download_prov):
                    if arq not in list_file_path:
                        list_file_path.append(arq)
                        file_downloaded = arq
                        break

                list_name_urls.append((nome, file_downloaded))
                ext = file_downloaded.split('.')[-1].lower()
                nome = nome + '.' + ext
                print('.', end='')
            else:
                print(':', end='')
                print('title:'+title)
                print('erro download')
            erro = err_down if tipe_err_down is None else False
            list_file_name.append(ProcessoArquivoModel(pra_prc_id=prc_id, pra_nome=nome,
                                                       pra_descricao=desc_file, pra_erro=erro))

            # VERIFICA SE A SESSÃO FOI ENCERRADA

            if len(self.browser.window_handles) > 1:
                self.browser.switch_to_window(self.browser.window_handles[1])
                self.browser.close()
                self.browser.switch_to_window(self.browser.window_handles[0])
                acp_pra_status = False
            print(']', end='')
        return True

    # TRATA AS AUDIENCIAS ********************* PRONTO *************************
    def trata_audiencias(self,list_audiences,prc_id):
        # TRATA AS AUDIÊNCIAS
        dict_audiences = {}
        list_audiences.reverse()
        tipo = None
        status = None
        for i in range(len(list_audiences)):
            aud = list_audiences[i].split('\n')
            aud_split = aud[0].split(' ')

            if 'AUDIENCIA' in aud_split:
                aud_split.remove('AUDIENCIA')
            if 'CEJUSC' in aud_split:
                aud_split.remove('CEJUSC')

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
                # print("STATUS - > ";status)

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

        # SALVA APENAS AS AUDIÊNCIAS COM O ÚLTIMO STATUS
        list_audiences.clear()
        list_aux = []
        for i in dict_audiences.values():
            if id(i) not in list_aux:
                list_audiences.append(i)
                list_aux.append(id(i))
                print("\n", i.aud_tipo, '\n', i.aud_status, '\n', i.aud_data, '\n', i.aud_obs)

    # CHECA SE A SESSÃO AINDA AÉ VALIDA

    def check_session(self):
        els = self.browser.find_elements_by_class_name('texto_erro')
        if len(els)>0 and 'sessão foi invalidada' in els[0].text:
                return False

        return True

    # VERIFICA SE TEM ELEMENTO SENDO CARREGADO NA TELA
    def check_file_session(self):
        try:
            els = self.browser.find_elements_by_id('dialog')
            if len(els) and els[0].is_displayed():
                return False
            return True
        except Exception as e:
            print(e)
            input('Erro check_file_session')


    # PEGA DADOS DO PROCESSO E ATUALIZA TABELA ********************* PRONTO *************************
    def pegar_dados_do_prcesso(self):
        # INICIALIZA AS VARIAVEIS COMO NONE
        juizo, classe, status, assunto, fase, valor_causa, dt_distribuicao = [None] * 7

        grau_position = 2
        print("GRAUUUUUUUUUUUUUUUUUU {}".format(self.grau))
        if self.grau == 1:
            grau_position = 3

        # CAPTURA O JUIZO DO PROCESSO
        n = self.browser.find_elements_by_xpath('//*[@id="VisualizaDados"]/fieldset[{}]/span[1]'.format(grau_position))

        if len(n) > 0:
            juizo = n[0].text.upper()
            juizo = Tools.remove_accents(juizo)

        n = self.browser.find_elements_by_xpath(
            '//*[@id="VisualizaDados"]/fieldset[{}]/span[2]'.format(grau_position))
        if len(n) > 0:
            classe = n[0].text.upper()
            classe = Tools.remove_accents(classe)

        n = self.browser.find_elements_by_xpath('//*[@id="VisualizaDados"]/fieldset[{}]/span[11]'.format(grau_position))
        if len(n) > 0:
            status = n[0].text.upper()
            if 'ARQUIVADO DEFINITIVAMENTE' in status or 'ARQUIVADO' in status or 'BAIXADO' in status:
                status = 'ARQUIVADO'
            else:
                status = 'ATIVO'

        n = self.browser.find_elements_by_xpath('//*[@id="VisualizaDados"]/fieldset[{}]/span[3]/table/tbody/tr/td'.format(grau_position))
        if len(n) > 0:
            assunto = n[0].text.upper()
            assunto = Tools.remove_accents(assunto)

        n = self.browser.find_elements_by_xpath('//*[@id="VisualizaDados"]/fieldset[{}]/span[7]'.format(grau_position))
        if len(n) > 0:
            fase = n[0].text.upper()

        num_span=4
        n = self.browser.find_elements_by_xpath('//*[@id="VisualizaDados"]/fieldset[{}]/div[4]'.format(grau_position))
        if len(n) > 0 and  "Assunto(s)" in n[0].text:
            num_span = 5

        n = self.browser.find_elements_by_xpath('//*[@id="VisualizaDados"]/fieldset[{}]/span[{}]'.format(grau_position,num_span))

        if len(n) > 0:
            valor_causa = n[0].text
            valor_causa = Tools.treat_value_cause(valor_causa)

        n = self.browser.find_elements_by_xpath('//*[@id="VisualizaDados"]/fieldset[{}]/span[8]'.format(grau_position))
        print("Grau_position-> {}".format(grau_position))
        if len(n) > 0:
            print("Datault - >" + n[0].text)

            if "Visualizar" in n[0].text:
                n = self.browser.find_elements_by_xpath(
                    '/html/body/div[2]/form/div[1]/fieldset/fieldset/fieldset[{}]/span[9]'.format(grau_position))

            dt_distribuicao = n[0].text
            dt_distribuicao = Tools.treat_date(dt_distribuicao)

        return juizo,classe,status,assunto,fase,valor_causa,dt_distribuicao

    # VARIFICAR SE O GRAU ALTEROU ********************* PRONTO *************************
    def validar_grau(self):
        if self.grau == 2:
            return None

        segundo_grau = ''
        n = self.browser.find_elements_by_xpath('/html/body/div[2]/form/div[1]/fieldset/fieldset[1]/legend')

        if len(n) > 0:
            segundo_grau = n[0].text

        if 'Dados Recurso' in segundo_grau:
            self.grau = 2
