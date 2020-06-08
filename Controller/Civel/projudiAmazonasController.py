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

class projudiAmazonasController(ProjudiModel):
    def __init__(self, site, mode_execute, access, platform_id, platform_name, flag, num_thread, grau=1):
        super().__init__(site=site, mode_execute=mode_execute, SQL_Long=access, platform_id=platform_id,
                         platform_name=platform_name, state='AM', grau=grau)
        self.platform_name = platform_name
        self.platform_id = int(platform_id)
        self.flag = flag
        self.num_thread = num_thread
        self.grau = grau
        self.link_buscar_processo_1_grau = None
        self.log_error = LogErrorModelMutlThread(platform_name=platform_name, state=self.state,
                                                 num_thread=self.num_thread)
        self.montar_dicionario()

    def request_access(self): # FUNCÇÃO PARA ACEITAR O TERMO DE REPONSABILIDADE, QUANDO O PROCESSO ESTÁ EM SEGREDO DE JUSTIÇA
                              # É PRECISSO ACEITAR O TERMO PARA CONSEGUIR ACESSAR OS DOCUMENTOS

        wait = WebDriverWait(self.browser,5)
        wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="processoForm"]/fieldset/table[2]')))
        termo = self.browser.find_elements_by_id('habilitacaoProvisoriaButton')
        if len(termo) > 0: # As  vezes não tem o termo, verificar se existe
            termo[0].click()
            wait.until(EC.presence_of_element_located((By.ID, 'termoAceito')))
            self.browser.find_element_by_id('termoAceito').click()
            self.browser.find_element_by_id('saveButton').click()



    #MONTAR PROCESSO-PLATAFORMA
    def montar_processo_plataforma(self,prc_id,prc_numero,flag,plp_codigo):

        if flag:
            juizo, classe, status, assunto, fase, valor_causa, dt_distribuicao,comarca = self.pegar_dados_do_prcesso()
            print('\n----')
            print('juizo', juizo)
            print('classe', classe)
            print('status', status)
            print('assunto', assunto)
            print('fase', fase)
            print('valor_causa', valor_causa)
            print('dt_distribuicao', dt_distribuicao)
            print('Comarca', comarca)
            print('\n----')
            # CRIA O OBJETO PROCESSO-PLATAFORMA QUE SERÁ INSERIDO NO BANCO DE DADOS
            process_platform = ProcessoPlataformaModel(plp_prc_id=prc_id, plp_plt_id=self.platform_id,
                                                       plp_numero=prc_numero, plp_status=status,plp_codigo=plp_codigo,
                                                       plp_juizo=juizo, plp_fase=fase, plp_grau=self.grau,
                                                       plp_valor_causa=valor_causa, plp_classe=classe,
                                                       plp_assunto=assunto, plp_data_distribuicao=dt_distribuicao,
                                                       plp_segredo=False, plp_localizado=1,plp_comarca=comarca, plp_prioridade=self.verificar_prioridade())
        else:
            process_platform = ProcessoPlataformaModel(plp_prc_id=prc_id, plp_plt_id=self.platform_id,plp_codigo=plp_codigo,
                                                                plp_numero=prc_numero, plp_segredo=False, plp_localizado=1,plp_grau=self.grau)

        return process_platform

    def secret_of_justice(self):
        segredo_xpah = '//*[@id="buscaProcessosQualquerInstanciaForm"]/table[2]/tbody/tr/td[3]/table/tbody/tr/td/ul/li'
        segredo = str(self.browser.find_elements_by_xpath(segredo_xpah).text)
        if "Segredo de Justiça" in segredo:
            return True
        return False

    # REALIZA LOGIN
    def login(self, user, password):

        wait = WebDriverWait(self.browser,5)
        wait.until(EC.presence_of_element_located((By.ID,'login')))
        self.browser.find_element_by_name('login').send_keys(user)
        self.browser.find_element_by_id('senha').send_keys(password, Keys.RETURN)

        wait.until(EC.presence_of_element_located((By.XPATH,'/html/body/div[2]')))

        iframe = self.browser.find_element_by_name('userMainFrame')
        self.browser.switch_to_frame(iframe)
        WebDriverWait(self.browser,5).until(EC.presence_of_element_located((By.XPATH,'//*[@id="mesaAdvogadoForm"]/table/tbody/tr[1]/td')))
        self.browser.switch_to.default_content()
        return True
        #/html/body/div[2]
        #//*[@id="mesaAdvogadoForm"]/h3

    def pegar_link_busca(self):
        if self.link_buscar_processo_1_grau is None:
            wait = WebDriverWait(self.browser, 5)
            xphat_buscar_processo_1_grau = '/html/body/div[9]/table/tbody/tr/td/table/tbody/tr[1]/td/a'
            wait.until(EC.presence_of_element_located((By.XPATH, xphat_buscar_processo_1_grau)))
            self.link_buscar_processo_1_grau = self.browser.find_element_by_xpath(xphat_buscar_processo_1_grau).get_attribute('href')
    def inserir_buscar_processo(self,prc_numero):
        wait = WebDriverWait(self.browser, 5)
        wait.until(EC.presence_of_element_located((By.ID, 'numeroProcesso')))  # Esperar a barra de colocar o número do prcesso aparecer
        self.browser.find_element_by_id('numeroProcesso').send_keys(prc_numero)  # Inserir o número do processo
        self.browser.find_element_by_id('pesquisar').click()                    # Pesquisar

    # BUSCA PROCESSO NO PROJUDI
    def find_process(self, prc_numero,plp_codigo=None):

        self.pegar_link_busca() # Se não existir o link de buscar pega-lo

        self.browser.get(self.link_buscar_processo_1_grau) # ir para pagina de busca

        self.inserir_buscar_processo(prc_numero) # Inserir o nuúmero e buscar o processo

        ##ESPERAR CARREGAR A PAGINA QUANDO BUSCAR E VERIFICAR SE O PRCESSO  EXISTE
        wait = WebDriverWait(self.browser, 5)
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="buscaProcessosQualquerInstanciaForm"]/h3'))) # Esperar o título aparecer
        n_pro = self.browser.find_elements_by_xpath('//*[@id="buscaProcessosQualquerInstanciaForm"]/table[2]/tbody/tr/td[2]') # Busca o processo na tabela se existir

        if len(n_pro) > 0: # Se achou clicar para abrir o processo
            segredo_xpah = '//*[@id="buscaProcessosQualquerInstanciaForm"]/table[2]/tbody/tr/td[3]/table/tbody/tr/td/ul/li'
            segredo = self.browser.find_element_by_xpath(segredo_xpah).text
            if "Segredo de Justiça" in segredo:
                return True
            xpath_abrir_proc = '//*[@id="buscaProcessosQualquerInstanciaForm"]/table[2]/tbody/tr/td[2]/a'
            link = self.browser.find_element_by_xpath(xpath_abrir_proc).get_attribute('href') # Abrir o prcesso
            self.browser.get(link)
            return False

        return True

    # SITUAÇÃO DO PROCESSO
    def secret_of_justice(self):
        try:
            return (self.browser.find_element_by_xpath(
                '//*[@id="Partes"]/table[2]/tbody/tr[11]/td[2]/div/strong').text != "NÃO")
        except:
            return False
    def find_xptah(self,xpath):
       return self.browser.find_element_by_xpath(xpath)

    def finds_xptah(self, xpath):
        return self.browser.find_elements_by_xpath(xpath)
    def pegar_advogados(self,linha,parte):

        advogados = linha.find_elements_by_xpath('td[6]/ul/li') # pegar lista de advogados se existir
        list_adv = []  # Lista que ficará armazenado todos os advogados

        for adv in advogados: # Passar pela lista de advogados e pegar as informações
            dados_adv = adv.text
            nome_adv = dados_adv.split('-')[-1] # OAB 29320N-GO - WILKER BAUHER VIEIRA LOPES, exemplo de dados do advogado
            remover_dados = [nome_adv,'OAB',"-", '(Procurador)', '(Defensor Público)'] # Dados para remver para pegar a OAB
            oab_adv =self.replaces(dados_adv,remover_dados)# Pegar a OAB do advogado, tira primeiro
            list_adv.append((ResponsavelModel(rsp_nome=nome_adv.replace("'",' '),rsp_tipo='Advogado(a)',rsp_oab=oab_adv), parte))

        return list_adv



    def pegar_dados_partes(self, parte): # Pega quanto a parte passiva ou ativa, apenas deve ser infomada no parametro
        id = "1" if 'Ativo' in parte else "2" # Verificar se está na tabela um ou dois
        xpath = '//*[@id="includeContent"]/table[{}]/tbody/tr'.format(id)
        wait = WebDriverWait(self.browser,5)
        wait.until(EC.presence_of_element_located((By.XPATH,xpath)))
        tabela = self.finds_xptah(xpath) # Pegando a linha da tabela que contem as informações da parte
        partes = []
        advogados = []
        passivo = self.browser.find_elements_by_xpath('//*[@id="includeContent"]/h4[2]')
        if not 'Ativo' in parte and len(passivo) == 0:
            return [],[]

        for linha in range(0,len(tabela),2): # Pegar as informações das partes
            nome_parte = tabela[linha].find_element_by_xpath('td[2]').text # Pegar o nome da parte
            cpf_cnpj = tabela[linha].find_element_by_xpath('td[4]').text # Pegar o cpf ou cpnj da parte
            cpf_cnpj = re.sub('[^0-9]','',cpf_cnpj)
            partes.append((ParteModel(prt_nome=nome_parte.replace("'"," "),prt_cpf_cnpj=cpf_cnpj if len(cpf_cnpj)>0 else None),parte)) # colocando os dados da parte no modelo
            ########## PEGAR OS ADVOGADOS ###########
            advogados += self.pegar_advogados(tabela[linha],parte)
        return  partes,advogados

    def pegar_juiz(self): # PEGAR O NOME DO JUIZ QUE FICA EM INFORMAÇÕES GERAIS DO PROCESSO
        self.browser.find_element_by_xpath('//*[@id="tabItemprefix0"]/div[2]/a').click()  # Ir para infomações
        xpath_tab = '//*[@id="includeContent"]/fieldset/table/tbody/tr'  # xpath  da tabela de informações gerais do processo
        WebDriverWait(self.browser, 5).until(EC.presence_of_element_located((By.XPATH, xpath_tab)))  # Esperar a tabela aparecer
        atributos = {"Juiz:":""}

        self.pegar_informacao_geral_processo(atributos,xpath_tab)

        if atributos['Juiz:'] is None or len(atributos['Juiz:']) == 0: # Não achou o juiz
            return False
        return [(ResponsavelModel(rsp_nome=atributos['Juiz:'].replace("'"," "),rsp_tipo='Juíz(a)',rsp_oab=None), None)]

    # PEGA OS ENVOLVIDOS E RETORNA UMA LISTA COM AS PARTES E OS ADVOGADOS/JUIZ

    def envolvidos(self):
        list_partes = []
        list_advogs = []
        xptah_parte = '//*[@id="tabItemprefix2"]/div[2]/a'
        self.find_xptah(xptah_parte).click() # Clicar para ir para as partes

        for i in ['Ativo', 'Passivo']:

            list_aux1, list_aux2 = self.pegar_dados_partes(i)  # Pega as partes e os advogados
            list_partes+= list_aux1
            list_advogs+=list_aux2
        # Pegar o nome do juiz que fica em outra aba
        juiz =  self.pegar_juiz() # pegar o juiz
        if juiz != False:
            list_advogs+= juiz
        return list_partes, list_advogs

    def esperar_movimetacoes(self):
        WebDriverWait(self.browser, 10).until(EC.visibility_of_element_located((By.XPATH,'//*[@id="includeContent"]/table/tbody/tr')))  # esperar as movimentações, linhas da tabela, aparecer

    def ir_para_movimentacoes(self):
        wait = WebDriverWait(self.browser, 10)
        # Esperar o botão de movimentações ficar visível na tela
        wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="tabItemprefix3"]/div[2]/a')))
        self.browser.find_element_by_xpath('//*[@id="tabItemprefix3"]/div[2]/a').click()  # Ir para movimentações
        self.esperar_movimetacoes()

    def tamanho_das_movimentacoes(self):
        tam = self.browser.find_elements_by_xpath('//*[@id="includeContent"]/table/tbody/tr')  # pegar a tabela de movimentações
        return  len(tam) # retornar o tamanho

    def pegar_linha_movimentacao(self,linha):
        tam = self.browser.find_elements_by_xpath('//*[@id="includeContent"]/table/tbody/tr')  # pegar a tabela de movimentações
        return tam[linha]
        pass
    def aceita_renovar_sessao(self):
        try:
            alert = self.browser.switch_to_alert()
            alert.accept()
        except:
            pass

    def buscar_dados(self,linha): # É RETORNADO UMA LISTA COM TODOS OS ELEMENTOS, PRIMEIRO O NUMERO DO EVENTO
                                  # SEGUNDO A DATA DO ACOMPANHAMENTO, TERCEIRO A DESCRIÇÃO DO ACOMPANHAMANETO
                                  #QUARTO SE TEM DONWLOAD

        # n_event - >td[2], aux_data->td[3], desc_process -> td[4], download
        xpath = ['td[2]','td[3]','td[4]']
        dados = []
        for i in xpath:
            dados.append(linha.find_element_by_xpath(i).text) # Buscando os dados na linha da tabela
        dados[1] = Tools.treat_date(dados[1]) # Tratar a data do acompanhamento
        dados.append(len(linha.find_elements_by_xpath('td[1]/a/img'))>0) # Pegar o id para ver se tem download, SEMARQUIVO no id mostra se tem download ou não


        return  dados # Retornar a data tratatda

    def verifica(self, n_files, list_file_path, list_name_urls, nome_donwload=None):

        err_down = self.wait_download(n_files)

        if not err_down:  # not err_down: # se o download concluiu totalmente sem nehum erro
            # print('dentro if')
            arquivo = set(os.listdir(self.path_download_prov)).difference(set(list_file_path))  # difereça de dois conjunts

            # print('hduahdushadhsuadushauhdusauhduau')

            file_downloaded = arquivo.pop() # pega o nome do arquivo que foi baixado
            arquivo = list(arquivo)
            if len(arquivo) > 1:  # Tem multiplos donwloads
                for i in range(0, len(arquivo), 1):
                    nome = Tools.convert_base(str(datetime.now()))
                    # nome = nome + '.' + arquivo[i].split('.')[-1]
                    print("Nome multiplos->", nome)
                    list_name_urls.append((nome, arquivo[i]))
                print("multiplos")
                self.log_error.insert_log("Multiplos donwloads processo, verificar!!")

            print('Nome donload: ', file_downloaded, " Paramentro:", nome_donwload)
            nome = Tools.convert_base(str(datetime.now()))# if nome_donwload == None else nome_donwload
            list_name_urls.append((nome,file_downloaded))  # Primeiro é o nome que quer renomear segundo o original, o primeiro não tem extensão
            # ext = file_downloaded.split('.')[-1].lower()
            nome = nome + '.' + file_downloaded.split('.')[-1]
            # print("Nome donload :", nome, "File: ", file_downloaded)
            # desc_file = file_downloaded.replace("." + ext, '')

            # self.dicionario_acompanhamento[numero_acompanhamento].append(file_downloaded) # ADICIONANDO O NOME DO DONWLOAD, IDEPENDENTE SE TERMINOU DE BAIXAR OU NAO

            return True, ProcessoArquivoModel(pra_nome=nome, pra_descricao=file_downloaded,pra_erro=0)




        else:

            return False, ProcessoArquivoModel(pra_erro=1)
    def tempo(self):
        restricao = self.browser.find_elements_by_id(
            'errorMessages')  # Documento não pode ser baixado :  arquivo: os motivos possíveis são uma determinação judicial ou a sua inclusão no processo de forma equivocada.
        if len(restricao) > 0:
            self.fechar_aba_atual_voltar_para_primeira()  # Quando o docimento não pode ser baixado abre mais uma janela

    def fechar_aba_atual_voltar_para_primeira(self):
        self.browser.switch_to_window(self.browser.window_handles[-1])
        self.browser.close()
        self.browser.switch_to_window(self.browser.window_handles[0])

    def fazer_donwload(self,id,list_name_urls,list_file_name, obs):

        #n_files, list_file_path, list_name_urls, nome_donwload=None
        wait = WebDriverWait(self.browser,12)
        list_name_urls_aux = []
        list_file_name_aux = []
        obs_aux = "" # Varivável para verificar se é segredo de justiça
        tabela = self.browser.find_element_by_id(id) # Pega a tabela inteira


        wait.until(EC.presence_of_all_elements_located((By.XPATH,'//*[@id="{}"]/table/tbody/tr'.format(id) )))  # Esperar os elementos da tabela aparecer
        tabela = self.browser.find_elements_by_xpath('//*[@id="{}"]/table/tbody/tr'.format(id)) # Pegar as linhas da nova tabela de downloads

        for linha in tabela: # Passar pelas linhas da tabela, fazendo os donwloads,
            # O botão para clilcar no donwload está na td[5]
            # Se o nome do download for "Restrição na Visualização" não da para baixar


            nome_donwload_plat = linha.find_element_by_xpath('td[5]')
            valido = nome_donwload_plat.find_elements_by_tag_name('strike')
            if not('Restrição na Visualização' in str(nome_donwload_plat.text)) and len(valido)==0: # Se puder baixar o download
                nome_arquivos = os.listdir(self.path_download_prov) # Pegar a quantidade de arquivos antes do download
                link = linha.find_element_by_xpath('td[5]/a').get_attribute('href') # Link do donwload
                self.browser.execute_script('''window.open("{}","_blank");'''.format(link))  # Abrir nova aba,  e ela faz donwload automaticamente
                #linha.find_element_by_xpath('td[5]/a').click()
                nome_donwload = link.split('=')[-1]  # Pegar o id do arquivo que está no final da url
                # wait.until(EC.number_of_windows_to_be(1)) # Quando clicla para fazer o donwload abre mais uma aba, esperar ela fechar
                status,processoAqruivo = self.verifica(len(nome_arquivos), nome_arquivos,list_name_urls_aux, nome_donwload)
                list_file_name_aux.append(processoAqruivo) # Todos os donwloads estarão aqui

            else: # Se echou aqui o documento não pode ser visualizado
                list_file_name_aux.append(ProcessoArquivoModel(pra_erro=3,pra_nome="Erro"))
                obs_aux = " - Movimentação possui arquivos mas há Restrição na Visualização"
                print("DOCUMENTO SIGILOSO - RESTRIÇÃO NA VISUALIZAÇÃO")



        list_name_urls += list_name_urls_aux
        list_file_name += list_file_name_aux
        obs += obs_aux

    def for_audiencia(self, class_name): # Pegar as todas as audiências e trata-las
        audiencias = self.browser.find_elements_by_class_name(class_name)
        lista_audiencia = []
        #td[4] é a descrição da audiencia  e td[3] é a data de quando ela foi colocada no site
        for linhas_aud in audiencias:

            decricao_audiencia = linhas_aud.find_element_by_xpath('td[4]').text # Pegando toda a descrição da movimentação
            data = linhas_aud.find_element_by_xpath('td[3]').text # pegando a data que ela foi publicada
            data = Tools.treat_date(data)
            decricao_audiencia = self.formatar_data_adiencia(str(decricao_audiencia))
            audiencia_tratada = self.separar_dados_audiencia(decricao_audiencia,data) # retorna uma tupla para tratar as audiencias

            if audiencia_tratada != False:

                lista_audiencia.append(audiencia_tratada)
        return lista_audiencia


    def pegar_as_audiencias(self):
        print("estado>", self.state)
        # Pegar as audiencias nas movimentações
        #verificar se a aa de filtros está aberta
        filtros = self.browser.find_element_by_id('divRealceConteiner').get_attribute('style')
        if 'none'in str(filtros):
            self.browser.execute_script('document.getElementById("divRealceConteiner").style = "";')



        # MARCAR AS AUDIENCIAS, QUANDO MARCAR ELA NO SITE, ELAS FICAM VERMELHA E O nome Mark na classe aparece
        self.browser.find_element_by_id('gruposRealceFiltroAUDIENCIA').click() # Marca as audiencias
        classes_audiencias = ['oddMark','evenMark'] # Nomes das classes quando elas são marcadas

        lista_audiencia = []
        for i in classes_audiencias:
            lista_audiencia += self.for_audiencia(i) # Retorna a audiência tratada

        lista_audiencia.sort(key=lambda a: a[-1], reverse=True) # Ordena pela data 2


        return  lista_audiencia# Retona todas as audiências encntradas tratadas




    # PEGA ANDAMENTOS DO PROCESSO, AS AUDIÊNCIAS E REALIZA OS DOWNLOADS POR ACOMPANHAMENTO
    def acomp_down_aud(self, prc_id, ult_mov,bool_2_grau_numero,full = False):
        print("#####################PEGANDO ANDAMENTOS/AUDIENCIA#####################\n ", end='')
        list_acomp_download = []
        list_audiences = []
        list_name_urls = []
        not_refresh = 0
        bool_2_grau = bool_2_grau_numero
        err = False
        k = 0

        # COLETA DE DADOS PARA CRIAÇÃO DOS ACOMPANHAMENTOS E DOWNLOAD DOS ARQUIVOS
        self.ir_para_movimentacoes() # Ir para as movimentações, e esperar elas aparecerem
        tam = self.tamanho_das_movimentacoes() # Pega o tamanho total das movimentações

        i = 0
        qtd_erro = 0
        while i <tam:
            try:
                k += 1  # Contar quantas vezes ele passou no for, os arquivos tem um id que é divArquivosMovimentacaoProcessomovimentacoes + o número da div, que é o k
                print(' {}'.format(i), end='')
                self.aceita_renovar_sessao() # As vezes aparece o alert para renovar a sessão, aceita-ló quando aparecer
                linha = self.pegar_linha_movimentacao(i) # Pega a linha inteira da movimentação
                n_event,aux_data,desc_process,download = self.buscar_dados(linha) # Pegar os dados já tratada, n_event - >td[2], desc_process -> td[4], aux_data->td[3]

                if (ult_mov is not None and (aux_data <= ult_mov)) and  (not full): # Verifica se é para pegar a movimentação de acordo com a dara
                    break

                if not bool_2_grau: # Verificar se o processo está no segundo grau
                    bool_2_grau= self.keywords_2_degree(string=desc_process)

                list_file_name = []
                acp_pra_status = False

                print('.', end='')
                obs = "" # Obseração, a movimentação pode ter downoad mas pode está em sigilo ou colocado de forma equivocada

                if download: # Se existir donwload
                    # os downloads ficam em uma tabela que tem o id = divArquivosMovimentacaoProcessomovimentacoes + numero da linha
                    documento_valido = linha.find_elements_by_tag_name('strike')  # Quando tem essa tag o documento foi exlcuido

                    if  len(documento_valido)>0:
                        obs = " - Acompanhamento possui arquivo mas não pode ser acessado: os motivos possíveis são uma determinação judicial ou a sua inclusão no processo de forma equivocada."
                    else:
                        print("Numero evento: ", n_event, " ")
                        self.pegar_linha_movimentacao(i).find_element_by_tag_name('img').click() # Clilcar para abrir os donwlads
                        self.fazer_donwload('divArquivosMovimentacaoProcessomovimentacoes' + str(k-1),list_name_urls,list_file_name,obs)
                        print('<>', end='')

                if len(self.browser.window_handles)>1: # Documento ainda não está disponível
                       obs = "Documento ainda não está disponível."
                       self.fechar_aba_atual_voltar_para_primeira()
                       list_file_name.append(ProcessoArquivoModel(pra_erro=4))



                list_acomp_download.append((AcompanhamentoModel(acp_esp=desc_process + obs,
                                                                acp_numero=n_event,
                                                                acp_data_cadastro=aux_data,
                                                                acp_prc_id=prc_id), list_file_name))
                qtd_erro = 0
            except TimeoutException:
                if qtd_erro>2:
                    raise
                self.browser.refresh()
                qtd_erro+=1
            i+=2

        #ARRUMAR DAQUI PARA BAIXO DEPOIS
        print('tam: {} | acompanhamento: {}'.format(len(list_name_urls), len(list_acomp_download)))

        if len(list_acomp_download)>0:
            list_audiences = TratarAudiencia.treat_audience(self.pegar_as_audiencias(),prc_id)


        return list_audiences, list_acomp_download, list_name_urls,bool_2_grau, err, not_refresh
    def pegar_informacao_geral_processo(self,atributos,xpath_tab):

        tabela_informacoes = self.finds_xptah(xpath_tab)  # Pegar as linhas da tabela
        for linhas in tabela_informacoes:
            campos = linhas.find_elements_by_xpath('td')  # pegar os campos
            for i in range(0, len(campos), 1):  # Verificar se o campo é o que procuro
                if str(campos[i].text) in atributos.keys():  # Verfica se o campo é um do dicionário
                    atributos[str(campos[i].text)] = None if len(str(campos[(i + 1)].text))==0 else str(campos[(i + 1)].text)  # pegar a informação se não for nula colocar none

    def verificar_prioridade(self):
        """verificar se o processo é prioridade de justiça"""

        prioridade = self.browser.find_elements_by_xpath('//*[@id="informacoesProcessuais"]/tbody/tr[4]')
        if len(prioridade) > 0 : # se achou algum elemento verificar se é o campo prioridade
            prioridade = str(prioridade[0].text)
            if 'PRIORIDADE:' in prioridade.upper():
                print("PROCESSO PRIORIDADE DE JUSTIÇA")
                return True
        return False



    # PEGA DADOS DO PROCESSO
    def pegar_dados_do_prcesso(self):
        # PEGA DADOS DO PROCESSO E ATUALIZA TABELA

        xpath_tab = '//*[@id="includeContent"]/fieldset/table/tbody/tr' # xpath  da tabela de informações gerais do processo

        atributos = {'Comarca:':"",'Juízo:':"",'Situação:':"", 'Classificação Processual:':"",'Valor da Causa:':"",'Distribuição:':"",
                     'Classe Processual:':"",'Assunto Principal:':""}
                     #comarca   juiz   , status ,       fase,                      valor_causa,   dt_distribuicao


        self.pegar_informacao_geral_processo(atributos,xpath_tab)  # PEGAR DADOS DA PRIMEIRA TABELA
        xpath_tab = '//*[@id="informacoesProcessuais"]/tbody/tr'
        self.pegar_informacao_geral_processo(atributos,xpath_tab) # PEGAR DADOS DA SEGUNDA TABELA

        print(atributos)
        return atributos['Juízo:'],atributos['Classe Processual:'].replace('<<',''),atributos['Situação:'],\
               atributos['Assunto Principal:'],atributos['Classificação Processual:'],\
               Tools.treat_value_cause(atributos['Valor da Causa:']),Tools.treat_date(atributos['Distribuição:'].replace("às	","")) if atributos['Distribuição:'] != None or atributos['Distribuição:'] != "" else None,\
               self.separar_comarca(atributos['Comarca:'])


    # VAlIDANDOS SE NUMERO DO PROCESSO CONTIDO NA PLATAFORMA E O MESMO CONTIDO NO SITE
    def validar_numero_plataforma(self, prc_numero):

        wait = WebDriverWait(self.browser, 5)
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="barraTituloStatusProcessual"]')))
        numero_no_site = self.browser.find_element_by_xpath('//*[@id="barraTituloStatusProcessual"]').text
        numero_no_site = re.sub('[^0-9]', '', numero_no_site)
        # print("numero_no_site",numero_no_site)
        return prc_numero not in numero_no_site
