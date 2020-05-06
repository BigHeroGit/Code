from Model.Civel.rootModel import RootModel
from Model.toolsModel import *
from Model.parteModel import ParteModel
from Model.logErrorModel import LogErrorModelMutlThread
from Model.audienciaModel import AudienciaModel
from Model.responsavelModel import ResponsavelModel
from Model.acompanhamentoModel import AcompanhamentoModel
from Model.processoArquivoModel import ProcessoArquivoModel
from Model.processoPlataformaModel import ProcessoPlataformaModel
from Model.Civel.pjeModel import PjeModel as TratarAudiencia

class EsajModel(RootModel):
    def __init__(self, site, mode_execute, SQL_Long, platform_id, platform_name, state,num_thread,link_consulta,flag,grau='1') :
        self.num_thread = num_thread
        self.platform_name = platform_name
        self.platform_id = platform_id
        self.flag = flag
        self.link_consulta = link_consulta
        self.grau = grau
        self.state = state

        super().__init__(site, mode_execute, SQL_Long, platform_id, platform_name, state, grau)
        self.log_error = LogErrorModelMutlThread(platform_name=platform_name, state=self.state,
                                                 num_thread=self.num_thread, grau=self.grau)

    # MONTAR PROCESSO-PLATAFORMA
    def montar_processo_plataforma(self, prc_id, prc_numero, flag, plp_codigo) :

        if flag :
            classe,  assunto, valor_causa, dt_distribuicao,vara,comarca = self.pegar_dados_do_prcesso()

            # CRIA O OBJETO PROCESSO-PLATAFORMA QUE SERÁ INSERIDO NO BANCO DE DADOS
            process_platform = ProcessoPlataformaModel(plp_prc_id=prc_id, plp_plt_id=self.platform_id,
                                                       plp_numero=prc_numero, plp_status=self.status, plp_codigo=plp_codigo,
                                                       plp_grau=1, plp_valor_causa=valor_causa, plp_classe=classe,
                                                       plp_assunto=assunto, plp_data_distribuicao=dt_distribuicao,
                                                       plp_segredo=False, plp_localizado=1,plp_comarca=comarca)
        else :

            process_platform = ProcessoPlataformaModel(plp_prc_id=prc_id, plp_plt_id=self.platform_id,
                                                       plp_codigo=plp_codigo,plp_localizado=1,
                                                       plp_numero=prc_numero, plp_segredo=False)

        return process_platform
    def check_process(self, n_proc, prc_id, plp_id,plp_localizado,plp_codigo=None):


        localizado,segredo=self.find_process(n_proc,plp_codigo=plp_codigo)

        if not localizado :
            if plp_localizado is None or plp_localizado == -1:
                plp_localizado = 2
            elif 1 < plp_localizado < 5:
                plp_localizado += 1
            elif plp_localizado == 1:
                return True ,-1
            else:
                plp_localizado = 0

            process_platform = ProcessoPlataformaModel(plp_prc_id=prc_id, plp_plt_id=self.platform_id,
                                                       plp_numero=n_proc, plp_segredo=False, plp_grau=self.grau,
                                                       plp_localizado=plp_localizado)

            for i in process_platform.__dict__.items():
                if i[1] is not None:
                    print(i[0], "\t", i[1])

            self.construct_list_obj_insert_bd(process_platform=process_platform, plp_id=plp_id)
            return True ,plp_localizado

            # VERIFICA SE O PROCESSO ESTÁ EM SEGREDO DE JUSTIÇA
        if segredo: # Se o  processo é segredo de justiça

            process_platform = ProcessoPlataformaModel(plp_prc_id=prc_id, plp_plt_id=self.platform_id,
                                                       plp_grau=self.grau,
                                                       plp_numero=n_proc, plp_segredo=True, plp_localizado=1)
            for i in process_platform.__dict__.items():
                if i[1] is not None:
                    print(i[0], "\t", i[1])
            self.construct_list_obj_insert_bd(process_platform=process_platform, plp_id=plp_id)
            return True ,plp_localizado

        return False,plp_localizado
    def login(self, user, password) :

        self.browser.find_element_by_id('usernameForm').send_keys(user)
        self.browser.find_element_by_id('passwordForm').send_keys(password, Keys.RETURN)
        wait = WebDriverWait(self.browser, 4.9)
        wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="identificacao"]/strong')))
        return True
    # ESPERA A BARRA ONDE COLOCA O NUMERO DO PROCESSO APARECER
    def esperar_barra_busca_processo(self):
        wait = WebDriverWait(self.browser,5)
        wait.until(EC.visibility_of_element_located((By.ID,'numeroDigitoAnoUnificado')))
    def colocar_numero_plataforma(self, numero_processo):
        # Primeira pate do número  13 Dígitos
        # Segunda parte os ultimos quatro dígitos
        numero_inserir =  numero_processo[:13] + numero_processo[16:]
        self.browser.find_element_by_id('numeroDigitoAnoUnificado').send_keys(numero_inserir, Keys.RETURN) # Inserir número e pesquisar
        # quando da um enter  ele recarega a página
        WebDriverWait(self.browser, 5).until(EC.presence_of_element_located((By.TAG_NAME, 'body'))) # Esperar a página recaregar
    def remover_mensagem(self):
        element = self.browser.find_elements_by_id('conpass-tag')
        if len(element)>0:
            self.browser.execute_script("""
            var element = arguments[0];
            element.parentNode.removeChild(element);
            """, element[0])
    # ENCONTRAR O PROCESSO NA PLATAFORMA
    def find_process(self, prc_numero, plp_codigo=None) :

        # IR PARA PAGINA DE PESQUISA DO PROCESSO
        self.browser.get(self.link_consulta)
        #ESPERAR A BARRA ONDE COLOCA O NUMERO DO PROCESSO APARECER
        self.esperar_barra_busca_processo()
        self.remover_mensagem() # Remover a mensagem que as vezes aparece
        self.colocar_numero_plataforma(prc_numero) # Coloca o numero na plataforma e pesquisa
        achou = self.browser.find_elements_by_id('mensagemRetorno') # quando não acha aparece uma mensahem: Não existem informações disponíveis para os parâmetros informados.

        if len(achou)> 0: # se for maior que 1 é porque a mensagem que não foi encontrada apareceu
            print("Processo não encontrado")
            return False,False # não achou  e não e segredo de justiça

        segredo = self.browser.find_elements_by_id('popupSenha') # Se aparecer esse popup pedinndo a senha do processo é segredo de justiça
        # 'style="display: none;"' -> não e segredo de justiça
        if len(segredo)>0 and not "NONE" in segredo[0].get_attribute('style').upper(): # se for maior que 0 é por que o pop up existe
            print("Processo em segredo de justiça")
            return True, True # achou e é segredo de justiça
        mensagem = self.browser.find_elements_by_xpath('//*[@id="conpass-tag"]/div/div[2]')
        if len(mensagem) > 0:  # as vezes aparece um tuturial de como usar o site, fecha-lo quando aparacer
            mensagem[0].find_element_by_xpath('div[1]').click()
            print("TEM A MENSAGEM DEPOIS QUE COLOCA O NUMERO")
            a = input("\nTEM A MENSAGEM")
            return self.find_process(prc_numero, plp_codigo)
        return True, False # Achou e não e segredo de justiça
    def pegar_partes(self, parte):

        linha = "1" if 'Ativo' in parte else "2"
        list_advogs = []
        list_partes = []
        xpath = '//*[@id="tablePartesPrincipais"]/tbody/tr[{}]/td[2]'.format(linha)
        tabela_parte = self.browser.find_element_by_xpath(xpath).text
        tabela_parte = tabela_parte.split('\n')
        nome = tabela_parte[0] # pega nome da parte
        print("Nome Parte:", nome, "Parte:", parte)
        list_partes.append((ParteModel(prt_nome=nome), parte))
        for advogados in tabela_parte[1:]: # A primeira posição é sempre a parte
            nome_adv = self.replaces(advogados,['Advogada', 'Advogado', 'Advogado(a)', 'Defensora:'])
            print("Adv : ", nome_adv, " Parte: ", parte)
            list_advogs.append((ResponsavelModel(rsp_nome=nome_adv, rsp_tipo='Advogado(a)', rsp_oab=self.state), parte))

        return list_partes,list_advogs
    # PEGA OS ENVOLVIDOS E RETORNA UMA LISTA COM AS PARTES E OS ADVOGADOS/JUIZ
    @property
    def envolvidos_primeiro_grau(self) :
        list_partes = []
        list_advogs = []

        # JUÍZ(A)

        WebDriverWait(self.browser,5).until(EC.visibility_of_element_located((By.ID,'juizProcesso')))
        nome = self.browser.find_element_by_id('juizProcesso').text
        print("Nome juiz:", nome)
        list_advogs.append((ResponsavelModel(rsp_nome=nome, rsp_tipo='Juíz(a)', rsp_oab=self.state), None))
        self.colocar_elemento_tela()
        for polos in ['Ativo', 'Passivo']: # Pegar essas partes
            partes, advs = self.pegar_partes(polos) # Pegar de acordo com o polo
            list_advogs += advs
            list_partes += partes

        return list_partes, list_advogs
    # PEGA OS ENVOLVIDOS E RETORNA UMA LISTA COM AS PARTES E OS ADVOGADOS/JUIZ
    @property
    def envolvidos_segundo_grau(self) :
        list_partes = []
        list_advogs = []
        try :
            try :
                # JUÍZ(A)
                all_tables = self.browser.find_elements_by_xpath('/html/body/div[2]/div')
                for table in enumerate(all_tables) :
                    try :

                        if 'COMPOSIÇÃO DO' in table[1].find_element_by_xpath('h2').text.upper() :
                            for i in self.browser.find_elements_by_xpath('/html/body/div[2]/table[{}]/'
                                                                         'tbody/tr'.format(table[0] + 1))[1 :] :
                                tipo = i.find_element_by_xpath('td[1]').text
                                nome = i.find_element_by_xpath('td[2]').text
                                nome = Tools.remove_caractere_especial(nome)
                                tipo = Tools.remove_caractere_especial(tipo)

                                list_advogs.append((ResponsavelModel(rsp_nome=nome, rsp_tipo='Juíz(a)', rsp_oab='AM-{}'
                                                                     .format(tipo)), None))
                            break
                    except :
                        pass

                nome = self.browser.find_element_by_xpath('//*[@id="maisDetalhes"]/div/div[1]/div/span').text
                list_advogs.append(
                    (ResponsavelModel(rsp_nome=nome, rsp_tipo='Juíz(a)', rsp_oab='AM-Relator'), None))

            except :
                self.log_error.insert_log('coleta de dados do juíz!')

            td = self.browser.find_elements_by_xpath('//*[@id="tablePartesPrincipais"]/tbody/tr[1]/td')[1 :]
            for i in td :
                # PARTE ATIVA
                try :
                    trs = str(i.text).split('\n')
                    nome = trs[0].upper()
                    list_partes.append((ParteModel(prt_nome=nome), 'Ativo'))
                    # ADVOGADOS ATIVOS
                    for adivs in trs[1 :] :
                        nome = adivs.split(':')[-1]
                        oab = 'AM'
                        nome = Tools.remove_caractere_especial(nome)
                        list_advogs.append(
                            (ResponsavelModel(rsp_nome=nome, rsp_tipo='Advogado(a)', rsp_oab=oab), 'Ativo'))
                except :
                    self.log_error.insert_log('coleta de dados da parte ativa!')
                    self.log_error.insert_log('coleta de dados do responsável ativo!')

            td = self.browser.find_elements_by_xpath('//*[@id="tablePartesPrincipais"]/tbody/tr[2]/td')[1 :]
            for i in td :
                # PARTE PASSIVAS
                try :
                    trs = str(i.text).split('\n')
                    nome = trs[0].upper()
                    list_partes.append((ParteModel(prt_nome=nome), 'Passivo'))
                    # ADVOGADOS PASSIVO
                    for adivs in trs[1 :] :
                        nome = adivs.split(':')[-1].upper()
                        oab = "AM"
                        nome = Tools.remove_caractere_especial(nome)
                        list_advogs.append(
                            (ResponsavelModel(rsp_nome=nome, rsp_tipo='Advogado(a)', rsp_oab=oab), 'Passivo'))
                except :
                    self.log_error.insert_log('coleta de dados da parte passiva!')
                    self.log_error.insert_log('coleta de dados do responsável passivo!')
        except :
            list_partes.clear()
            list_advogs.clear()
            self.log_error.insert_log('coleta de dados dos envolvidos no processo!')

        return list_partes, list_advogs

    @property
    def envolvidos(self):
        list_partes, list_advogs = self.envolvidos_primeiro_grau if self.grau==1 else self.envolvidos_segundo_grau
        return  list_partes, list_advogs
    def tirar_elemento_da_tela(self, xpath): # Tirar o elemento que de lampada que aparece na tela para poder clilcar para abrir  todas as movimentações

        elemento = self.browser.find_element_by_xpath(xpath) # Elemento para ser escondido
        self.browser.execute_script('arguments[0].style.display = "none";',elemento)
    def colocar_elemento_tela(self,xpath = '/html/body/div[1]'):
        elemento = self.browser.find_element_by_xpath(xpath)  # Elemento para ser escondido
        self.browser.execute_script('arguments[0].style.display = "";', elemento)
    def setar_exibicao(self): # Setar para exibir todas movimentações
        todas_movimetacoes = self.browser.find_element_by_id('tabelaTodasMovimentacoes')
        self.browser.execute_script('arguments[0].style.display = "table-row-group";', todas_movimetacoes)
    # Se tier movimentações, exibi todas
    def mostrar_todas_movimentacoes(self):

        #As movimentações não são mostradas todas de uma vez, é preciso clilcar no botão "mais" para abrir todas
        wait = WebDriverWait(self.browser,5)
        wait.until(EC.presence_of_element_located((By.ID,'tabelaTodasMovimentacoes'))) # Esperar a tabela de movimentações pararecer
        botao_mais = self.browser.find_elements_by_id('linkmovimentacoes') # Esse botão aparece quanto tem mais movimentações
        if len(botao_mais)>0: # Existem mais movimentações movimentações
          self.setar_exibicao() # Exibir todas movimentações
          return True  # Se for true é por que tem o botão de mais movimentações
        return False# Apenas movimentações na tabela de ultimas movimentações
    def pegar_linha(self,numero_da_linha):
        return self.browser.find_elements_by_xpath('//*[@id="tabelaTodasMovimentacoes"]/tr')[numero_da_linha]
    def pegar_linha_ultimas(self,numero_da_linha):
        return self.browser.find_elements_by_xpath('//*[@id="tabelaUltimasMovimentacoes"]/tr')[numero_da_linha]
    def verificar_aduio(self,td3):

        return  len(td3.find_elements_by_tag_name('a'))>0 # Eleento é clicavel

    def pegar_dados(self, linha,movimetacoes): # Pegar a descrição do acompanhamento data e verificar se tem donwload
        # '//*[@id="tabelaUltimasMovimentacoes"]' poucas movimentações - //*[@id="tabelaUltimasMovimentacoes"]/tr


        dados_linha = self.pegar_linha(linha) if movimetacoes else self.pegar_linha_ultimas(linha)
        # td[1] fica a data,  td[2] se tiver download tem uma imagem, e td[3] é a descrição do processo

        descricao_movimentacao = dados_linha.find_element_by_xpath('td[3]')
        audio = self.verificar_aduio(descricao_movimentacao)
        descricao_movimentacao = descricao_movimentacao.text

        if audio:  # é um aduio e tem que clilcar para baixar
            input(f'descricao_movimentacao {descricao_movimentacao}')
            data = Tools.extrair_date_string(descricao_movimentacao)
        else:
            data = dados_linha.find_element_by_class_name('dataMovimentacao').text # Pegar data
            data = Tools.treat_date(data)

        donwload = dados_linha.find_elements_by_xpath('td[2]/a/img') # Se o tamanho do download for maior que 0 então tem download
        donwload = True if len(donwload) > 0 or audio else False # Se tiver download a variavel é true



        return  data,descricao_movimentacao,donwload
    # RETORNA FALSE SE NÃO FOR AUDIENCIA, E UMA TUPLA SE FOR AUDIÊNCIA
    def verificar_audiencia(self, descricao_acompanhamento,data):

        # Verificar se tem audiência na descrição da movimentação
        if 'AUDIÊNCIA' in descricao_acompanhamento.upper().split('\n')[0]:
            return self.separar_dados_audiencia(descricao_acompanhamento,data)
        return False
    def esperar_porID(self,wait,id):
        wait.until(EC.element_to_be_clickable((By.ID,id)))
    def clilcar_para_baixar(self):
        wait = WebDriverWait(self.browser,10)
        self.esperar_porID(wait,'esticarButton') # Esperar o botão de selecionar todos os arquivos ser clicavel
        self.browser.find_element_by_id('esticarButton').click() # Abrir a aba de selecionar quais aquivos serão baixados
        self.esperar_porID(wait,'selecionarButton') # Esperar o botão de selecionar todos os documentos ficar clicável
        self.browser.find_element_by_id('selecionarButton').click() # Selecionar para baixar todos os doumentos
        self.browser.find_element_by_id('salvarButton').click() # Clicar para preparar para baixar
        self.esperar_porID(wait,"btnDownloadDocumento") # Esperar o botão download
        wait.until(EC.invisibility_of_element_located((By.XPATH,'//*[@id="popupGerarDocumentoOpcoes"]/p[2]'))) # Esperar a tela de preparação sair da tela, quando ela some o documento está pronto para baixar
        self.browser.find_element_by_id('btnDownloadDocumento').click() # Clicar para baixar
    #verifica se pode realizar o donwload, quando não pode ele não carrega a pagina de donwload corretamente
    def verificar_se_deu_erro_pagina_donwload(self):
        mensagem_erro = self.browser.find_elements_by_xpath('//*[@id="mensagemRetorno"]/li')
        if(len(mensagem_erro))>0: # se for maior que 0 indica que deu erro e apareceu uma mensagem
            #mensagem_site_erro = 'Não foi possível validar o seu acesso a esse recurso. Por favor, acesse os detalhes do processo e tente novamente.'
            return  True
        return False
    def fazer_donwload(self,linha,list_name_url,list_file_name):

        list_name_urls_aux = []
        botao_donwload = self.pegar_linha(linha) # Pegar a linha que tem o donwload

        botao_donwload = botao_donwload.find_elements_by_xpath('td[2]/a') # é onde fica armazenado o link de donwload
        if len(botao_donwload)<1: # Não achou na td[2]
            botao_donwload = self.pegar_linha(linha)  # Pegar a linha que tem o donwload
            botao_donwload = botao_donwload.find_elements_by_xpath('td[3]/div/a') # é onde fica arma
        link = botao_donwload[0].get_attribute('href') # Pegar o link de donwload
        self.browser.execute_script('''window.open("{}","_blank");'''.format(link)) # Abrir nova aba
        self.browser.switch_to_window(self.browser.window_handles[-1])
        WebDriverWait(self.browser, 5).until(EC.presence_of_element_located((By.TAG_NAME, 'body'))) # Esperar a página recaregar
        if self.verificar_se_deu_erro_pagina_donwload():
            a= ("DEU ERRO NA HORA DE CARREGAR A PAGINA!!!!!!")

        nome_arquivos = os.listdir(self.path_download_prov)  # Pegar a quantidade de arquivos antes do download
        self.clilcar_para_baixar()
        self.browser.close() # fechar a guia de donwload que foi aberta
        self.browser.switch_to_window(self.browser.window_handles[0]) # Voltar para a primeira
        status, processoAqruivo = self.verifica(len(nome_arquivos), nome_arquivos, list_name_urls_aux)
        list_name_url += list_name_urls_aux
        list_file_name += processoAqruivo
    #pega a audiencia que está em baixo na tabela audiências
    def pegar_tabela_audiencia(self):
        # as informações estão a partir da tr[3] '/html/body/div[2]/table[6]/tbody/tr[3]'
        list_audiencia = []
        tabela = self.browser.find_elements_by_xpath('/html/body/div[2]/table[6]/tbody/tr')
        if len(tabela)>2: # existe audiências na tabela
            tabela = tabela[2:] # os dois primeiros não são audiencias
            for linha in tabela:
                list_audiencia.append(self.separar_dados_audiencia(linha.text,None))

        return  list_audiencia
    def verifica_segundo_grau(self, descricao_mov):
        descricao_mov = descricao_mov.upper()
        palavras_chaves = ['AUTOS PARA A SEGUNDA INSTÂNICA','REMESSA À TURMA RECURSAL (EM GRAU DE RECURSO)',
                           'SITUAÇÃO: EM GRAU DE RECURSO (MESMO PROCESSO)','REMETIDO RECURSO ELETRÔNICO AO TRIBUNAL DE JUSTIÇA/TURMA DE RECURSOS',
                           'REMETIDOS OS AUTOS PARA A SEGUNDA INSTÂNCIA (RECURSO ELETRÔNICO)', 'REMETIDOS OS AUTOS PARA A TURMA RECURSAL',
                           'REMETIDOS OS AUTOS PARA AO TRIBUNAL DE JUSTIÇA']
        for keys in palavras_chaves:
            if keys in descricao_mov:
                return True
        return False
    # PEGA ANDAMENTOS DO PROCESSO, AS AUDIÊNCIAS E REALIZA OS DOWNLOADS POR ACOMPANHAMENTO
    def acomp_down_aud(self, prc_id, ult_mov,bool_2_grau_numero,full = False) :

        list_acomp_download = []
        list_audiences = []
        list_name_urls = []
        not_refresh = 0
        err = False
        segundo_grau = bool_2_grau_numero
        movimetacoes = self.mostrar_todas_movimentacoes() # Mostrar as movimentações para pegalas

        wait = WebDriverWait(self.browser, 5)
        wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="tabelaTodasMovimentacoes"]/tr')))
        movimentos = self.browser.find_elements_by_xpath('//*[@id="tabelaTodasMovimentacoes"]/tr')
        max_n_events = len(movimentos)
        k=0
        for i in range(max_n_events):

            dados_linha = self.pegar_dados(i,movimetacoes) # Pegar os dados da linha, a função retorna : data, descricao_movimentacao, donwload

            if i==0: # Verificar se a primeira movimentação o processo está ativo ou não
                self.status = self.verificar_arquivado(dados_linha[1]) # verificar o status de acordo com a primeira movimetação
                print("Status:",self.status)
            not_refresh += 1
            if (ult_mov != None and dados_linha[0] <= ult_mov) and not full : # Verificar se é para pegar  a movimentação
               break

            k += 1
            if not segundo_grau:
                segundo_grau = self.verifica_segundo_grau(dados_linha[1])

            audiencia = self.verificar_audiencia(dados_linha[1],dados_linha[0]) # Passando a descrição e a data
            if audiencia != False: # Se for uma audiencia
                list_audiences.append(audiencia)
            list_file_name = [] # Lista de downloads de uma movimentação
            if dados_linha[-1]: # Se for verdadeiro é por que tem donwload
                self.fazer_donwload(i,list_name_urls,list_file_name) # Passar a linha que será feito o download

            list_acomp_download.append((AcompanhamentoModel(acp_esp=dados_linha[1],
                                                            acp_data_cadastro=dados_linha[0],
                                                            acp_prc_id=prc_id), list_file_name))

        if not_refresh > 1: # tem Movimentações novas, então pegar as audiências
            list_audiences += self.pegar_tabela_audiencia()
            list_audiences = TratarAudiencia.treat_audience(list_audiences, prc_id)
        # a = input("Conferir")


        return list_audiences, list_acomp_download, list_name_urls, segundo_grau,err, not_refresh
    # VAlIDANDOS SE NUMERO DO PROCESSO CONTIDO NA PLATAFORMA E O MESMO CONTIDO NO SITE
    def validar_numero_plataforma(self,prc_numero):

        mensagem = self.browser.find_elements_by_xpath('//*[@id="conpass-tag"]/div/div[2]')
        if len(mensagem)>0: # as vezes aparece um tuturial de como usar o site, fecha-lo quando aparacer
            mensagem[0].find_element_by_xpath('div[1]').click()
            a = input("Tem a mensagem !!!!")
        numero_plataforma = self.browser.find_element_by_id('numeroProcesso').text  # Pega o campo onde esta o número do processo
        numero_plataforma = re.sub('[^0-9]', '', numero_plataforma)  # tirar os pontos do numero do processo
        return not (prc_numero == numero_plataforma)  # Se for igual retorna false, se for diferente verdadeiro
        # raise
    # COLETA DO NUMERO DO PROCESSO DO 2 GRAU E CRIAR O PLP COM HAJA NO 2º GRAU!
    def validar_bool_2_grau(self, bool_2_grau, bool_2_grau_numero, prc_numero, prc_id):

        if self.grau != 1 or not bool_2_grau:
            return []
        list_plp_2_grau = []
        list_plp_2_grau.append(ProcessoPlataformaModel(plp_prc_id=prc_id, plp_plt_id=self.platform_id,
                                    plp_numero=prc_numero, plp_grau=2, plp_processo_origem=prc_numero )
                               )

        return list_plp_2_grau
    # PEGA DADOS DO PROCESSO
    def pegar_dados_do_prcesso(self):

        self.browser.execute_script("window.scrollTo(0, 0)") # Subir até o topo da página
        # Mostrar todos os campos
        self.browser.execute_script('document.getElementById("maisDetalhes").className += " show";') # Mostrar todas as informações

        informacoes_processo = {'classeProcesso':"",'assuntoProcesso':"", 'varaProcesso':"",
                                'valorAcaoProcesso':"", 'dataHoraDistribuicaoProcesso':"", 'foroProcesso':""}
        # PEGA DADOS DO PROCESSO E ATUALIZA TABELA


        for campos in informacoes_processo.keys():
            elemento = self.browser.find_elements_by_id(campos)
            informacoes_processo[campos] = elemento[0].text if len(elemento)>0 else None
        data,hora = Tools.extrair_datas_da_string(informacoes_processo['dataHoraDistribuicaoProcesso'])
        data += hora
        data = ' '.join(data)
        informacoes_processo['dataHoraDistribuicaoProcesso'] = Tools.treat_date(data)

        print( informacoes_processo)
        return informacoes_processo['classeProcesso'],\
        informacoes_processo['assuntoProcesso'],Tools.treat_value_cause(informacoes_processo['valorAcaoProcesso']),\
        informacoes_processo['dataHoraDistribuicaoProcesso'], informacoes_processo['varaProcesso'], \
        informacoes_processo['foroProcesso']
        # return classe, status, assunto, valor_causa, dt_distribuicao,vara
    # Buscar plp_codigo
    def request_access(self):
        plp_codigo=''
        link_de_site = self.browser.current_url

        if self.grau == 1:
            plp_codigo = str(self.browser.current_url).split('codigo=')[-1].split('&')[0]
        else:
            link_de_site = self.browser.current_url
            link_de_site = link_de_site.split(
                'search.do?conversationId=&paginaConsulta=0&cbPesquisa=NUMPROC&numeroDigitoAnoUnificado=')[-1]
            print('\n\n\np1',link_de_site.split('&foroNumeroUnificado='))
            aux, link_de_site = link_de_site.split('&foroNumeroUnificado=')
            print('\n\n\np2',link_de_site.split('&dePesquisaNuUnificado='))
            plp_codigo += aux + '|'
            aux, aux2 = link_de_site.split('&dePesquisaNuUnificado=')
            print('\n\n\np4', link_de_site.split('&dePesquisaNuUnificado='))
            plp_codigo += aux + '|' + aux2

        return plp_codigo
