
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
                                                       plp_juizo=juizo, plp_fase=fase, plp_grau=1,
                                                       plp_valor_causa=valor_causa, plp_classe=classe,
                                                       plp_assunto=assunto, plp_data_distribuicao=dt_distribuicao,
                                                       plp_segredo=False, plp_localizado=1,plp_comarca=comarca, plp_prioridade=self.verificar_prioridade())
        else:
            process_platform = ProcessoPlataformaModel(plp_prc_id=prc_id, plp_plt_id=self.platform_id,plp_codigo=plp_codigo,
                                                                plp_numero=prc_numero, plp_segredo=False, plp_localizado=True)

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


class projudiRoraimaController(projudiAmazonasController):
    def __init__(self, site, mode_execute, access, platform_id, platform_name, flag, num_thread, grau='1Grau'):
        super().__init__(site, mode_execute, access, platform_id, platform_name, 'RR', grau)
        self.platform_name = platform_name
        self.platform_id = int(platform_id)
        self.flag = flag
        self.state = 'RR'
        self.num_thread = num_thread
        self.link_buscar_processo_1_grau = None
        self.log_error = LogErrorModelMutlThread(platform_name=platform_name, state=self.state,
                                                 num_thread=self.num_thread, grau=grau)


    # REALIZA LOGIN
    def login(self, user, password):
        # self.browser.switch_to.frame(self.browser.find_element_by_css_selector("frame[name='mainFrame']"))
        wait = WebDriverWait(self.browser, 5)
        wait.until(EC.presence_of_element_located((By.NAME, 'login')))
        self.browser.find_element_by_name('login').send_keys(user)
        self.browser.find_element_by_id('senha').send_keys(password, Keys.RETURN)
        wait = WebDriverWait(self.browser, 5)
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="listaPerfilAtivo"]/div/ul/li[1]/div[1]/a[1]')))
        self.browser.find_element_by_xpath('//*[@id="listaPerfilAtivo"]/div/ul/li[1]/div[1]/a[1]').click()
        return True


class projudiParaController(ProjudiModel):
    def __init__(self, site, mode_execute, access, platform_id, platform_name, flag, num_thread, grau='1Grau'):
        super().__init__(site=site, mode_execute=mode_execute, SQL_Long=access, platform_id=platform_id,
                         platform_name=platform_name, state='PA', grau=grau)

        self.platform_name = platform_name
        self.platform_id = int(platform_id)
        self.flag = flag
        self.num_thread = num_thread
        self.site_busca = 'https://projudi.tjpa.jus.br/projudi/buscas/ProcessosQualquerAdvogado' # Pagina de busca quando não tem o id do processo
        self.base_site_busca_id = 'https://projudi.tjpa.jus.br/projudi/listagens/DadosProcesso?numeroProcesso={}' # Buscar com id do processo

        self.montar_dicionario()
        self.log_error = LogErrorModelMutlThread(platform_name=platform_name, state=self.state,
                                                 num_thread=self.num_thread, grau=grau)

    def login(self, user, password):

            wait = WebDriverWait(self.browser, 5)
            wait.until(EC.presence_of_element_located((By.ID, "login")))
            self.browser.find_element_by_id('login').send_keys(user)
            self.browser.find_element_by_id('senha').send_keys(password, Keys.RETURN)
            wait.until(EC.presence_of_all_elements_located((By.TAG_NAME,'body'))) # Esperar o painel depois do login
            return True

    # MONTAR PROCESSO-PLATAFORMA
    def montar_processo_plataforma(self, prc_id, prc_numero, flag,plp_codigo):

        if flag:

            # PEGA DADOS DO PROCESSO E ATUALIZA TABELA

            juizo, classe, assunto, fase, valor_causa, dt_distribuicao,comarca,prioridade,migrado = self.pegar_dados_do_prcesso()
            # plp_status=status
            # CRIA O OBJETO PROCESSO-PLATAFORMA QUE SERÁ INSERIDO NO BANCO DE DADOS
            process_platform = ProcessoPlataformaModel(plp_prc_id=prc_id, plp_plt_id=self.platform_id,
                                                       plp_numero=prc_numero,plp_codigo=plp_codigo,
                                                       plp_juizo=juizo, plp_fase=fase, plp_grau=1,
                                                       plp_valor_causa=valor_causa, plp_classe=classe,
                                                       plp_assunto=assunto, plp_data_distribuicao=dt_distribuicao,
                                                       plp_segredo=False, plp_localizado=1,plp_comarca=comarca,plp_status=self.status,
                                                       plp_prioridade=prioridade,plp_migrado=migrado)
        else:

            process_platform = ProcessoPlataformaModel(plp_prc_id=prc_id, plp_plt_id=self.platform_id,plp_codigo=plp_codigo,
                                                       plp_numero=prc_numero, plp_segredo=False, plp_localizado=True)

        return process_platform


    # BUSCA PROCESSO NO PROJUDI
    def buscar_processso_platafoma(self, numero_processo):

        self.browser.get(self.site_busca) # ir para o site de busca do processo
        wait = WebDriverWait(self.browser,10)
        wait.until(EC.visibility_of_element_located((By.ID,'numeroProcesso'))) # Esperar o campo do processo aparecer
        campo_nprocesso = self.browser.find_element_by_id('numeroProcesso') # Pegar o campo que coloca o numero do processo
        campo_nprocesso.send_keys(Keys.HOME) # Colocar o curso no comeco para colocar o número do processo
        campo_nprocesso.send_keys(numero_processo) # Colocar o numero do processo e pesquisa-lo
        campo_nprocesso.send_keys(Keys.RETURN) # Pesquisar o processo
        wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, 'body')))  # Esperar a pagina carrear
    def verificar_se_achou_processo(self, numero_processo):

        lista_processo = self.browser.find_elements_by_xpath('/html/body/div[1]/form[2]/table/tbody/tr[4]') # Buscar o primeiro elemento da tabela que retorna
        if len(lista_processo) > 0: # Achou algun processo na tabela
            n_prcesso_site = lista_processo[0].find_element_by_xpath('td[2]').text # Pegar o numero do processo na tabela
            n_prcesso_site = re.sub('[^0-9]','',n_prcesso_site)
            return not(n_prcesso_site in numero_processo)

        return True
    def ir_para_processo(self, id_processo):
        self.browser.get(self.base_site_busca_id.format(id_processo))  # Abrir o processo
        WebDriverWait(self.browser,10).until(EC.visibility_of_element_located((By.XPATH,'//*[@id="Arquivos"]/table/tbody/tr')))

    def abrir_processo(self): # Quando achar o processo abrir o processo

        processo_tabela = self.browser.find_element_by_xpath('/html/body/div[1]/form[2]/table/tbody/tr[4]/td[2]/a') # Pegar o numero do processo para cliclar
        link_processo = str(processo_tabela.get_attribute('href')) # Pegar o link do processo na tabela
        # Exemplo de link : /projudi/listagens/DadosProcesso?numeroProcesso=1020129206529
        id_processo = link_processo.split('=')[-1] # Pegar o id do processo, fica no final do link
        self.ir_para_processo(id_processo) # Abrir o processo



    def find_process(self, prc_numero, plp_codigo=None):

        if plp_codigo is None: # Processo nunca foi buscado, então buscar pelo link padrão
            self.buscar_processso_platafoma(prc_numero)
            nao_achou = self.verificar_se_achou_processo(prc_numero)

            if not nao_achou: # Se achou o processo então cliclar para abri-lo
                self.abrir_processo() # Abrir o processo para pegar as informações
            return  nao_achou # Retornar se achou ou não

        self.ir_para_processo(plp_codigo) # Ir para página do processo
        return False
    # SITUAÇÃO DO PROCESSO



    def secret_of_justice(self):

        xpaths = ['//*[@id="Partes"]/table/tbody/tr[11]/td[2]/div/strong',
                '//*[@id="Partes"]/table/tbody/tr[12]/td[2]/div/strong'] # As vezes o local pode ser diferente
        for  xpath in xpaths:
            segredo = self.browser.find_elements_by_xpath(xpath)
            if len(segredo)>0:
                return segredo[0].text != "NÃO"

    def abrir_lista_advogados(self, parte):

        #'//*[@id="Partes"]/table/tbody/tr[2]/td[2]/table/tbody/tr[2]/td[5]/a' -> ativa
        #'//*[@id="Partes"]/table/tbody/tr[3]/td[2]/table/tbody/tr[2]/td[5]/a' - > passiva

        xpath = '//*[@id="Partes"]/table/tbody/tr[{}]/td[2]/table/tbody/tr[2]/td[5]/a'
        pos = ["2","3"] if 'Ativa' in parte else ["3", "4"] # quando tem a barra de priordade ele possui um xpath diferente
        for i in pos:
            funcao = self.browser.find_elements_by_xpath(xpath.format(i))
            if len(funcao) >0:
                self.browser.execute_script(funcao[0].get_attribute('href') + ";")  # Abrir o painel de advogados
                return


    def request_access(self): # Função para pegar o id do processo
        codido_processo = str(self.browser.current_url) # Pega a url da pagina
        codido_processo = codido_processo.split('=')[-1] # Pega o id do processo
        return codido_processo

    def pegar_respontavel(self,parte,dict_lista):

        # a classe linhaClara e linhaEscura são onde estão os nomes dos advogados e a oab
        lista_partes = []
        links = dict_lista[parte]
        for funcoes in links:
            self.browser.execute_script(funcoes+";") # Abrir a pagina de advogados
            #novotr.id = 'tr' + tipoInfo + idParteProcesso;
            aux_str = self.replaces(funcoes,['javascript: mostraOculta(',"'",')'])

            id_tabela = 'tr'+ aux_str.split(',')[-1] + aux_str.split(',')[0] # id da tabela de advogads

            tabela_advs = self.browser.find_element_by_id(id_tabela)
            tabela_advs = tabela_advs.find_elements_by_tag_name('tbody')[-1]
            tabela_advs = tabela_advs.find_elements_by_tag_name('tr') # linhas da tabela de advs
            print('Tamanho :',len(tabela_advs))
            if len(tabela_advs)>1:
                tabela_advs = tabela_advs[1:] # A primeira linha é as o cabeçalho da tabela
                for adv in tabela_advs: # passar na lista de advs para pegar os ads

                    nome = str(adv.find_element_by_xpath('td[1]').text)
                    oab = str(adv.find_element_by_xpath('td[2]').text)
                    lista_partes.append((ResponsavelModel(rsp_nome=nome.replace("'", " "), rsp_oab=oab, rsp_tipo='Advogado(a)'), parte))

        return lista_partes


    def pegar_partes(self, parte,lista_funcoes):
        lista_partes = []
        lista_funcoes[parte] = [] # dicionarios com as funções para achar o id
        xpath_partes = '//*[@id="Partes"]/table/tbody/tr[{}]/td[2]/table' # 2 é ativa e 3 passiva
        pos = '2' if 'Ativa' in parte else '3'  # Onde estão as tabelas com informações das partes
        tabela_informacoes = self.browser.find_element_by_xpath(xpath_partes.format(pos))
        linhas_tabelas = tabela_informacoes.find_elements_by_class_name('linhaClara')
        linhas_tabelas += tabela_informacoes.find_elements_by_class_name('linhaEscura')
        for linhas in linhas_tabelas:

            nome = str(linhas.find_element_by_xpath('td[2]').text)  # pegando o nome
            cpf = linhas.find_element_by_xpath('td[4]').text
            href = linhas.find_element_by_xpath('td[5]/a')
            lista_funcoes[parte].append(href.get_attribute('href'))
            cpf = re.sub('[^0-9]', '', cpf)
            lista_partes.append((ParteModel(prt_cpf_cnpj=cpf if len(cpf)>0 else None, prt_nome=nome.replace("'",' ')), parte))


        return lista_partes


    # PEGA OS ENVOLVIDOS E RETORNA UMA LISTA COM AS PARTES E OS ADVOGADOS/JUIZ

    def envolvidos(self):

        list_partes = []
        list_advogs = []
        lista_funcoes = {}
        list_partes += self.pegar_partes('Ativa',lista_funcoes)
        list_partes += self.pegar_partes('Passiva',lista_funcoes)
        list_advogs += self.pegar_respontavel('Ativa',lista_funcoes)
        list_advogs += self.pegar_respontavel('Passiva',lista_funcoes)



        return list_partes, list_advogs

    def pegar_dados_linha(self,linha):


        descricao_processo = linha.find_element_by_xpath('td/table/tbody/tr/td[3]').text # Pegar a descricao do processo
        data = linha.find_element_by_xpath('td/table/tbody/tr/td[4]').text
        data = Tools.treat_date(data)
        donwload = linha.find_elements_by_xpath('td/table/tbody/tr/td[6]/div/div/table/tbody/tr/td[1]/a') # elemento que tem donwload
        n_event = linha.find_element_by_xpath('td/table/tbody/tr/td[2]').text # Numero da movimentação
        donwload = True if len(donwload)>0 else False

        return  descricao_processo, data,donwload,n_event


    def verificar_audiencia(self, descricao_acompanhamento,data):

        # Verificar se tem audiência na descrição da movimentação
        if 'AUDIÊNCIA' in descricao_acompanhamento.upper():
            descricao_acompanhamento_aud = self.formatar_data_adiencia(descricao_acompanhamento)
            return self.separar_dados_audiencia(descricao_acompanhamento_aud,data)
        return False

    def fazer_donwload(self, linha,list_name_urls, list_file_name):
        '//*[@id="Arquivos"]/table/tbody/tr[41]/td/table/tbody/tr'
        linhas_donwload = linha.find_elements_by_xpath(
            'td/span[2]/div/div/table/tbody/tr')  # Ir para o local onde está os donwloads
        list_name_urls_aux = []

        for linhas in linhas_donwload:  # Se tiver mais de um donwload pegar a lista e varrer todos

            downlaods = linhas.find_elements_by_tag_name('a')  # Pegar os donwloads que estão com a tag 'a'

            for baixar in downlaods:  # fazer o donwnload em si

                nome_arquivos = os.listdir(self.path_download_prov)  # Pegar a quantidade de arquivos antes do download
                link = baixar.get_attribute('href')  # Pegar o link do donwload

                self.browser.execute_script('''window.open("{}","_blank");'''.format(
                    link))  # Abrir nova aba,  e ela faz donwload automaticamente
                nome_donwload = link.split('=')[-1]  # Pegar o id do arquivo que está no final da url
                status, processoAqruivo = self.verifica(len(nome_arquivos), nome_arquivos, list_name_urls_aux,
                                                        nome_donwload)
                list_name_urls += list_name_urls_aux
                list_file_name += processoAqruivo
    
    def aceitar_alerta(self):
        try:
            alert = self.browser.switch_to_alert()
            alert.accept()
        except:
            pass
    # PEGA ANDAMENTOS DO PROCESSO, AS AUDIÊNCIAS E REALIZA OS DOWNLOADS POR ACOMPANHAMENTO
    def acomp_down_aud(self, prc_id, ult_mov,bool_2_grau_numero,full=False):

        list_acomp_download = []
        list_audiences = []
        list_name_urls = []
        not_refresh = 0
        bool_2_grau = bool_2_grau_numero
        err = False
        i = 0
        linhas_tabela = self.browser.find_elements_by_xpath('//*[@id="Arquivos"]/table/tbody/tr')[1:] # Pegar as linhas com as movimentações
        t= 1
        for linha in linhas_tabela:
            try:
                self.aceitar_alerta()
                descricao_processo, data, donwload,n_event = self.pegar_dados_linha(linha) # Pegar os dados de uma linha
                not_refresh += 1 # não sei para que serve essa variável
                #'005.2012.917.622-7'
                if (ult_mov != None and data <= ult_mov) and not full:  # Verificar se é para pegar  a movimentação
                    break
                if i==0: # Verificar se a primeira movimentação é de arquivado
                    self.status = self.verificar_arquivado(descricao_processo) # verificar o status de acordo com a primeira movimetação
                    i+=1
                if not bool_2_grau: # Verificar se o processo está no segundo grau
                    bool_2_grau= self.keywords_2_degree(string=descricao_processo)

                audiencia = self.verificar_audiencia(descricao_processo, data)  # Passando a descrição e a data

                if audiencia != False:  # Se for uma audiencia
                    list_audiences.append(audiencia)
                list_file_name = []  # Lista de downloads de uma movimentação
                if donwload:  # Se for verdadeiro é por que tem donwload
                    print(" ", n_event, end='')
                    self.fazer_donwload(linha, list_name_urls, list_file_name)  # Passar a linha que será feito o download

                list_acomp_download.append((AcompanhamentoModel(acp_esp=descricao_processo,
                                                                acp_data_cadastro=data,
                                                                acp_prc_id=prc_id,
                                                                acp_numero=n_event
                                                                ), list_file_name))
                t+=1
            except:
                if t>2:
                    raise
                t+=1
                self.browser.refresh()
            # except TimeoutException:
            #     self.browser.refresh()

        if not_refresh > 1:  # tem Movimentações novas, então pegar as audiências

            list_audiences = TratarAudiencia.treat_audience(list_audiences, prc_id)

        return list_audiences, list_acomp_download, list_name_urls, bool_2_grau, err, not_refresh

    # VAlIDANDOS SE NUMERO DO PROCESSO CONTIDO NA PLATAFORMA E O MESMO CONTIDO NO SITE
    def validar_numero_plataforma(self, prc_numero):
        #try:
            #wait = WebDriverWait(self.browser, 10)
            #wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="Partes"]/table/tbody/tr[1]/td')))
        numero_no_site = self.browser.find_element_by_xpath('//*[@id="Partes"]/table/tbody/tr[1]/td').text
        numero_no_site = re.sub('[^0-9]', '', numero_no_site)
        # print("numero_no_site",numero_no_site)
        return prc_numero not in numero_no_site
        # except:
        #     return True

    # PEGA DADOS DO PROCESSO
    def pegar_dados_do_prcesso(self):
        # PEGA DADOS DO PROCESSO E ATUALIZA TABELA

        #quando o processo e prioridade os xpaths mudam, as trs é sempre uma a mais
        prioridade = self.browser.find_elements_by_xpath('//*[@id="Partes"]/table/tbody/tr[2]/td[2]/div/b')
        prioridade = 1 if len(prioridade)>0 else 0 # Verificar se é prioridade

        atributos = {'Juízo':"", 'Assunto':"", 'Classe':"",
                     'Fase Processual':"",'Data de Distribuição':"", 'Valor da Causa':""}

        xpaths = ['//*[@id="Partes"]/table/tbody/tr[{}]/td[2]'.format(7+prioridade),'//*[@id="Partes"]/table/tbody/tr[{}]/td[2]'.format(8+prioridade),
                  '//*[@id="Partes"]/table/tbody/tr[{}]/td[2]'.format(10+prioridade),'//*[@id="Partes"]/table/tbody/tr[{}]/td[2]'.format(12+prioridade),
                  '//*[@id="Partes"]/table/tbody/tr[{}]/td[4]'.format(13+prioridade),'//*[@id="Partes"]/table/tbody/tr[{}]/td[2]/b'.format(14+prioridade)]

        i = 0
        for chaves in atributos.keys():
            campo =  self.browser.find_element_by_xpath(xpaths[i]).text

            atributos[chaves] = campo if len(campo)>0 else None
            if atributos[chaves]!= None and  len(atributos[chaves]) >100:
                atributos[chaves] = atributos[chaves][:atributos[chaves][:100].rfind(' ')]
            i+=1
        atributos['comarca'] = self.separar_comarca(atributos['Juízo'])
        # Verificar se é processo migrado
        migrado = self.browser.find_elements_by_tag_name('img')
        if len(migrado) >0:
            migrado = str(migrado[0].get_attribute('src')).upper()
            migrado = 'PROCESSOMIGRADO' in migrado
        else:
            migrado = False


        return atributos['Juízo'].split('Juiz: ')[0], atributos['Classe'], atributos['Assunto'],atributos['Fase Processual'],\
               Tools.treat_value_cause(atributos['Valor da Causa']),Tools.treat_date(atributos['Data de Distribuição']),\
               atributos['comarca'] if atributos['comarca'] != False else self.state,prioridade,migrado

class projudiMaranhaoController(ProjudiModel):
    def __init__(self, site, mode_execute, access, platform_id, platform_name, flag, num_thread, grau='1Grau'):
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
                list_advogs.append((ResponsavelModel(rsp_nome=nome_juiz.replace("'"," "),
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
        input()
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

class projudiGoiasController(ProjudiModel):
    # CONSTRUTOR DA CLASSE
    def __init__(self, site, mode_execute, access, platform_id, platform_name, flag, num_thread, grau='1Grau'):

        super().__init__(site=site, mode_execute=mode_execute, SQL_Long=access, platform_id=platform_id,
                         platform_name=platform_name, state='GO', grau=grau)
        self.platform_name = platform_name
        self.platform_id = int(platform_id)
        self.flag = flag
        self.num_thread = num_thread

        self.log_error = LogErrorModelMutlThread(platform_name=platform_name, state=self.state,
                                                 num_thread=self.num_thread,grau=grau)

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
        wait = WebDriverWait(self.browser, 10)
        wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="divEditar"]/fieldset/fieldset/label[1]/input[4]')))
        self.browser.find_element_by_xpath('//*[@id="divEditar"]/fieldset/fieldset/label[1]/input[4]').click()

        # INSERE O NUMERO DO PROCESSO NO SEU CAMPO DEVIDO
        self.browser.find_element_by_id('ProcessoNumero').send_keys(prc_numero[:7] + '.' + prc_numero[7:9])

        # CLICA NO BOTÃO 'Buscar'
        self.browser.find_element_by_xpath('//*[@id="divBotoesCentralizados"]/input[1]').click()

        # IF PARA VERIFICAR SE O PROCESSO FOI LOCALIZADO
        if self.browser.find_elements_by_xpath('/html/body/div/h1/img'):
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
            aux_data = self.browser.find_element_by_xpath(xpath_aux_data).text
            aux_data = Tools.treat_date(aux_data)

            # CASO A VARIAVEL ult_mov FOR None QUER DIZER QUE O PROCESSO É A PRIMEIRA VEZ QUE ESTA SENDO PROCURADO
            if ult_mov is not None:
                not_refresh += 1
                if aux_data <= ult_mov and not full:
                    # input('aux_data <= ult_mov and not full')
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
        wait = WebDriverWait(self.browser, 5)
        wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[5]/div[3]/div/button')))
        self.browser.find_element_by_xpath('/html/body/div[5]/div[3]/div/button').click()

        # CAPTURA TABELA DE MOVIMENTAÇÕES
        movimentacoes = self.browser.find_elements_by_xpath('//*[@id="TabelaArquivos"]/tbody/tr')

        # TRATA AS MOVIMENTAÇÕES
        for i in range(1,len(movimentacoes)):

            # APENAS LINHAS IMPARES PODEM SÃO MOVIMENTAÇÕES!
            if i % 2 != 0:
                # CAPTURA A DATA DA MOVIMENTAÇÃO aux_data
                xpath_aux_data = '/html/body/div[2]/form/div[1]/div/div[1]/table/tbody/tr[{}]/td[3]'.format(i)
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
        wait.until(EC.presence_of_element_located((By.XPATH, xpath_aux_docs)))

        ul_files = self.browser.find_elements_by_xpath(xpath_aux_docs)
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

            # AQUI KAIO ACORDA É AQUI QUE VOCE CONTINUA DIA 20/02
            # MANOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO
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

            t += 1
            try:
                wait = WebDriverWait(self.browser, 2)
                wait.until(EC.number_of_windows_to_be(2))
                wait = WebDriverWait(self.browser, 20)
                wait.until(EC.number_of_windows_to_be(1))
            except TimeoutException:
                if len(self.browser.window_handles) > 1:
                    self.browser.switch_to_window(self.browser.window_handles[1])
                    erro = self.browser.find_elements_by_class_name('texto_erro')
                    if len(erro) > 0 and 'Sem Permis' in erro[0].text:
                        self.browser.close()
                        self.browser.switch_to_window(self.browser.window_handles[0])
                        return False

            tipe_err_down = -1
            err_down = self.wait_download(n_files) if not direct else 0

            acp_pra_status = acp_pra_status and (not err_down)

            desc_file = self.browser.find_element_by_xpath(xpath_aux_docs + '['+str(j)+']/div[2]/div[1]/a').text

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

        n = self.browser.find_elements_by_xpath('//*[@id="VisualizaDados"]/fieldset[{}]/span[4]'.format(grau_position))
        if len(n) > 0:
            valor_causa = n[0].text
            valor_causa = Tools.treat_value_cause(valor_causa)

        n = self.browser.find_elements_by_xpath('//*[@id="VisualizaDados"]/fieldset[{}]/span[8]'.format(grau_position))
        if len(n) > 0:
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
