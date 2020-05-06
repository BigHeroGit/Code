from Model.Civel.rootModel import RootModel
from Model.toolsModel import *
from Model.parteModel import ParteModel
from Model.logErrorModel import LogErrorModelMutlThread
from Model.responsavelModel import ResponsavelModel
from Model.processoArquivoModel import ProcessoArquivoModel
from Model.processoPlataformaModel import ProcessoPlataformaModel
from Model.acompanhamentoModel import AcompanhamentoModel
from Model.audienciaModel import AudienciaModel
from selenium import webdriver
# selenium.webdriver.common.action_chains
# import keyboard
from time import sleep

class PjeModel(RootModel):
    def __init__(self, site, mode_execute, SQL_Long, platform_id, platform_name, state,num_thread,link_consulta,flag,grau='1Grau'):
        self.num_thread = num_thread
        self.grau = grau
        self.flag = flag
        self.state = state
        self.link_consulta = link_consulta
        self.grau = 1 if '1' in grau else 2
        self.log_error = LogErrorModelMutlThread(platform_name=platform_name, state=self.state,
                                                 num_thread=self.num_thread, grau=self.grau)


        self.verifica_segredo = 'pje/Processo/CadastroPeticaoAvulsa/peticaoavulsa.seam' # Campo verifica se o processo está em segredo de justiça

        self.montar_dicionario()


        super().__init__(site, mode_execute, SQL_Long, platform_id, platform_name, state,grau)


    # VALIDA A INICIALIZAÇÃO DA VARREDURA NA PLATAFORMA
    def initializer(self):

        while True:
            # INICIALIZA BROWSER
            if self.init_browser():
                # self.browser.set_window_position(-10000, 0)

                # LOGIN NA PLATAFORMA
                login = self.login()
                if login:
                    print("Loguin: ", login)
                    break
                else:
                    if self.state == "RO":
                        keyboard.press_and_release('\n')
            if self.browser is not None :
                self.browser.quit()

        # VERIFICA CADA NÚMERO DE PROCESSO RETORNADO DO BANCO DE DADOS NA PLATAFORMA

    def check_process(self, n_proc, prc_id, plp_id,log,plp_localizado):
        if self.find_process(n_proc):
            log.insert_info('Processo não encontrado!')
            print('Processo não encontrado!\nplp_localizado{}'.format(plp_localizado))
            if (plp_localizado is None):
                plp_localizado = 2
            elif 1 < plp_localizado < 5:
                plp_localizado += 1
            elif abs(plp_localizado) == 1:
                return True, -1
            else:
                plp_localizado = 0

            process_platform = ProcessoPlataformaModel(plp_prc_id=prc_id, plp_plt_id=self.platform_id,
                                                       plp_numero=n_proc, plp_segredo=False, plp_grau=self.grau,

                                                       plp_localizado=plp_localizado)

            for i in process_platform.__dict__.items():
                if i[1] is not None:
                    print(i[0], "\t", i[1])

            self.construct_list_obj_insert_bd(process_platform=process_platform, plp_id=plp_id)
            return True, plp_localizado

            # VERIFICA SE O PROCESSO ESTÁ EM SEGREDO DE JUSTIÇA
        if self.secret_of_justice:
            log.insert_info('Processo em segredo de justiça!')
            print('Processo em segredo de justiça!')
            process_platform = ProcessoPlataformaModel(plp_prc_id=prc_id, plp_plt_id=self.platform_id,
                                                       plp_grau=self.grau,
                                                       plp_numero=n_proc, plp_segredo=True, plp_localizado=1)
            for i in process_platform.__dict__.items():
                if i[1] is not None:
                    print(i[0], "\t", i[1])
            self.construct_list_obj_insert_bd(process_platform=process_platform, plp_id=plp_id)
            return True, plp_localizado

        return False, plp_localizado

        # BUSCA PELO PROCESSO NA PLATAFORMA

    def busca_processo_na_plataforma(self,prc_numero,tupla_processo,t0,log,row_database):
        prc_id, prc_estado, plp_status, cadastro, plp_codigo, \
        plp_data_update, plp_id, plp_numero, plp_localizado = tupla_processo[1:-1]
        print("plp_localizado_anterior -> ", plp_localizado)
        if len(prc_numero) != 20:
            prc_numero = prc_numero.lstrip('0')
            prc_numero = prc_numero.rjust(20, '0')

        nao_achou, plp_localizado = self.check_process(n_proc=prc_numero, prc_id=prc_id, plp_id=plp_id,
                                                       log=log, plp_localizado=plp_localizado)
        if nao_achou:
            print(' plp_localizado == {}'.format(plp_localizado))
            if plp_localizado == -1:
                aux_i_prc = tupla_processo
                aux_i_prc[9] = plp_localizado
                row_database.append(aux_i_prc)
                print('### Processo foi processo foi reinserido novamente no lista de busca: {} SECS'.format(
                    time.time() - t0).upper())
                print('-' * 65)
            else:
                print('###Tempo total da coleta de dados do processo: {} SECS'.format(time.time() - t0).upper())
                print('-' * 65)

            return True
        if self.validar_numero_plataforma(prc_numero):
            print("Os numeros divergem")
            if plp_localizado == 1:
                self.log_error.insert_log('Os numeros divergem!'.upper())

                aux_i_prc = tupla_processo
                aux_i_prc[9] = -1
                row_database.append(aux_i_prc)
                print('### Processo foi reinserido novamente no lista de busca: {} SECS'.format(
                    time.time() - t0).upper())
                print('-' * 65)
            elif plp_localizado == -1:
                plp_localizado = 1
            else:
                prc_id, prc_estado, plp_status, cadastro, plp_codigo, \
                plp_data_update, plp_id, plp_numero, plp_localizado1 = tupla_processo[1:-1]
                if plp_localizado is None:
                    plp_localizado = 2
                elif plp_localizado == 1:
                    plp_localizado = 1
                elif 1 < plp_localizado < 5:
                    plp_localizado += 1
                else:
                    plp_localizado = 0

                process_platform = ProcessoPlataformaModel(plp_prc_id=prc_id, plp_plt_id=self.platform_id,
                                                           plp_segredo=False, plp_grau=self.grau,
                                                           plp_localizado=plp_localizado)

                for i in process_platform.__dict__.items():
                    if i[1] is not None:
                        print(i[0], "\t", i[1])

                self.construct_list_obj_insert_bd(process_platform=process_platform, plp_id=plp_id)
                print('###Tempo total da coleta de dados do processo: {} SECS'.format(time.time() - t0).upper())
                print('-' * 65)
            return True

        return False

    # REALIZA LOGIN
    def login(self):
        try:
            wait = WebDriverWait(self.browser, 30)
            if self.state == "RO": # O RO é necessário cliclar em sim para logar
                if self.num_thread > 0:
                    dir = os.listdir(self.arq_name) # Esse atributo está na classe filho, é o caminho da pasta de prioridade
                    nome_arq_ant = "{}.cdp".format(str(self.num_thread - 1)) # identificação do robo
                    # Verificar se o robo anterior já realizou o loguin
                    while True: # Eseprar até que o robo anterior faça o loguin
                        if nome_arq_ant not in dir:
                            break
                        dir = os.listdir(self.arq_name)

                #Clicar para lohgar
                wait = WebDriverWait(self.browser, 10)
                wait.until(
                    EC.visibility_of_element_located((By.ID, 'loginAplicacaoButton')))
                self.browser.find_element_by_xpath('//*[@id="loginAplicacaoButton"]').click()
                if not Tools.clicker_certificado_pje(25): # Clilcar no OK para logar

                    print("Não conseguiu logar")
                    #os.system("TASKKILL /F /IM jp2launcher.exe") #  Se der errado fechar o aplicativo
                    if not Tools.WindowExists('SunAwtDialog','Autorização'):
                        print("Deu eror")
                        keyboard.press_and_release('\n')

                    sleep(0.5)
                    return  not Tools.WindowExists('SunAwtDialog','Autorização')
                else: # Se deu certo apagar o aquivo que identifica o click
                    wait.until(EC.visibility_of_element_located((By.ID, 'tabExpedientes_lbl')))
                    #wait.until(EC.visibility_of_element_located((By.ID, 'home')))
                    nome_arq = "{}.cdp".format(str(self.num_thread))
                    dir = os.listdir(self.arq_name)
                    for file in dir:
                        if nome_arq in file:
                            os.remove(os.path.join(self.arq_name, file))

                    return True

            else:

                wait = WebDriverWait(self.browser, 40)
                if self.state=="BA":
                    try:
                        wait.until(EC.visibility_of_element_located((By.XPATH,  '//*[@id="mpModoOperacaoContentTable"]/tbody/tr'))) # esperar a tela do como deseja logar no pje BA aparecer
                        self.browser.find_element_by_xpath('//*[@id="mpModoOperacaoContentDiv"]/div/span/i').click() # Fechar a janela de como deseja logar no pje
                    except:
                        print("\n\n\n\t\t\t\tERRO\n\n\n")

                        pass

                wait.until(EC.visibility_of_element_located((By.ID, 'loginAplicacaoButton')))
                self.browser.find_element_by_xpath('//*[@id="loginAplicacaoButton"]').click()

                # Esperar a mensagem de validação de certificação desaparecer
                wait.until(EC.invisibility_of_element((By.ID,'mp_formValidarContentTable')))

                wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'botao-menu')))
                teste = self.browser.find_elements_by_id('tabExpedientes_lbl')
                # print("Passou....", len(teste))

                #olha aqui
                # wait.until(EC.visibility_of_element_located((By.ID, ''
                #                                                     '')))

            return True
        except Exception as Erro:
            # input("Deu ruim no loguin, Errp: {}".format(Erro) )
            print("\n\n\n\t\t\t\t 231 ERRO\n\n\n")
            return False

    # BUSCA PROCESSO NO PROJUDI
    def find_process(self, prc_numero):
        try:

            self.browser.get(self.link_consulta)
            wait = WebDriverWait(self.browser, 7)
            teste_tela_loguin = self.browser.find_elements_by_id('loginAplicacaoButton') # Esse botão é da pagina inicial de loguin, se ele achar está nela
            nao_carregou = self.browser.find_elements_by_xpath('//*[@id="reload-button"]')
            if len(nao_carregou) > 0:
                print("NÃO CARREGOU A PAGINA!")
                sleep(60*60)
            if len(teste_tela_loguin) > 0:
                print("NÃO ESTA NA PAGINA DE BUSCA, ESTÁ NA DE LOGUIN!!")
                sleep(60*60)

            wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="fPP:numeroProcesso:numeroSequencial"]')))
            self.browser.find_element_by_xpath('//*[@id="fPP:numeroProcesso:numeroSequencial"]').send_keys(
                prc_numero[:7])
            self.browser.find_element_by_xpath('//*[@id="fPP:numeroProcesso:numeroDigitoVerificador"]').send_keys(
                prc_numero[7:9])
            print('digito')
            self.browser.find_element_by_xpath('//*[@id="fPP:numeroProcesso:Ano"]').send_keys(prc_numero[9:13])
            print('ano')
            self.browser.find_element_by_xpath('//*[@id="fPP:numeroProcesso:labelTribunalRespectivo"]').send_keys(
                prc_numero[14:16])
            print('tribunal')
            self.browser.find_element_by_xpath('//*[@id="fPP:numeroProcesso:NumeroOrgaoJustica"]').send_keys(
                prc_numero[16:], Keys.RETURN)
            print('orgao')

            wait.until(EC.invisibility_of_element((By.ID, '_viewRoot:status.start')))  # Esperar o site carregar

            #wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="fPP:processosTable:tb"]/tr/td[1]/a')))
            # input("deseja contnura")
            processos =self.browser.find_elements_by_xpath('//*[@id="fPP:processosTable:tb"]/tr')
            if len(processos)>0:# Veroficar se existe apareceu, se apareceu processo então ele existe
                self.browser.find_element_by_xpath('//*[@id="fPP:processosTable:tb"]/tr/td[1]/a').click()
                try: # As vezes aparece alerta, as vezes não se aparecer aceitar
                    # WebDriverWait(self.browser,2).until(EC.alert_is_present())
                    alert = self.browser.switch_to_alert()
                    alert.accept()
                except:
                    print("\n\n\n\t\t\t\tERRO\n\n\n")

                    pass

                # sleep(60*60)
                return  False

            return True
        # except TimeoutException:

        except Exception as erro:
            print("Erro na busca do processo: ", erro)
            print("\n\n\n\t\t\t\tERRO\n\n\n")
            self.log_error.insert_log("Erro ao colocar o numero do processo na plataforma!")
            return True

    # SITUAÇÃO DO PROCESSO
    @property
    def secret_of_justice(self):
        try:
            return (self.browser.find_element_by_xpath(
                '//*[@id="Partes"]/table[2]/tbody/tr[11]/td[2]/div/strong').text != "NÃO")
        except:
            print("\n\n\n\t\t\t\tERRO\n\n\n")

            return False

    def acomp_down_aud(self, ult_mov, list_audiences,list_acomp_download, list_name_urls):
        pass

    # PEGA OS ENVOLVIDOS E RETORNA UMA LISTA COM AS PARTES E OS ADVOGADOS/JUIZ
    def extrair_cpnj_string(self, string_extrair):
        cpnj_padrao = r'[0-9][0-9].[0-9][0-9][0-9].[0-9][0-9][0-9]/[0-9][0-9][0-9][0-9]-[0-9][0-9]'  # Padrão a ser buscado
        cpnj = re.findall(cpnj_padrao, string_extrair)  # Retorna um vetor com as datas encontradas na string
        if len(cpnj) > 0:
            return re.sub('[^0-9]', '', cpnj[0])  # Retirar pontos e tracos
        return False

    def extrair_cpf_string(self, string_extrair):

        cpf_padrao = r'[0-9][0-9][0-9].[0-9][0-9][0-9].[0-9][0-9][0-9]-[0-9][0-9]'  # Padrão CPF
        cpf = re.findall(cpf_padrao, string_extrair)  # Retorna um vetor com as datas encontradas na string

        if len(cpf) > 0:
            return re.sub('[^0-9]', '', cpf[0])  # Retirar pontos e tracos

        return False

    def get_informacoes_partes(self,polo):
        list_partes = []
        list_advogs = []
        nome_adv = None
        oab = self.state
        # polo = 'poloAtivo'
        # polo = 'poloPassivo'
        tabela_polo_ativo = self.browser.find_elements_by_xpath('//*[@id="{}"]/table/tbody/tr'.format(polo)) # Todas informações da parte ativo

        for linha in tabela_polo_ativo: #
            nome =  linha.find_elements_by_xpath('td/span')
            if len(nome) > 0:

                cpf = self.extrair_cpf_string(nome[0].text) # Se não achou cpf retorna false
                if cpf == False:
                    cpf = self.extrair_cpnj_string(nome[0].text) # Tentar buscar por CPNJ
                if cpf == False: # Não achou o Cpf nem o CPNJ
                    cpf = None
                nomePart = nome[0].text
                nomePart = nomePart.split('-')[0]#.upper().repalce('(ADVOGADO)', '') # Pegar o nome

                print("Part:",nomePart)
                list_partes.append((ParteModel(prt_nome=nomePart,prt_cpf_cnpj=cpf), 'Ativo' if 'Ativo' in polo else 'Passivo'))
                print("Nome:", nomePart, "CPF:", cpf)

            responsaveis_ativo = linha.find_elements_by_class_name('tree')
            if len(responsaveis_ativo)> 0: # Quer dizer que possui
                responsaveis_ativo = responsaveis_ativo[0].find_elements_by_xpath('li') # linhas que contem as informações
                for i in responsaveis_ativo:
                    cpf = self.extrair_cpf_string(i.text)
                    if cpf == False:
                        cpf = self.extrair_cpnj_string(i.text)
                    if cpf == False: # Se não achar o cpf nem o CPNJ
                        cpf = None
                    nome = i.text.upper()
                    nome = nome.split('-') if  len(nome) >0 else None
                    if nome != None:
                        nome_adv = nome[0].upper()
                        nome_adv = nome_adv.replace("(ADVOGADO)",'')
                        # Verificar se tem OAB no texto, e então pegar o numero da OAB
                        oab = nome[1].replace('OAB', '') if len(nome)>1 and "OAB" in nome[1] else self.state

                    list_advogs.append((ResponsavelModel(rsp_nome=nome_adv,
                                                         rsp_tipo='Advogado(a)',
                                                         rsp_oab=oab), 'Ativo' if 'Ativo' in polo else 'Passivo'))
                    print("Nome ADV:", nome_adv, "OAB", oab, "CPF:", cpf)

        return list_partes, list_advogs


    def get_dados_processo(self): # Pegar os dados so processo como status, juiz etc.

         tentativas = 0
         while tentativas < 3:
            try:
                #juizo, classe, assuntos_text, valor_causa, dt_distribuicao, self.status,comarca

                wait = WebDriverWait(self.browser, 4)
                wait.until(EC.visibility_of_element_located((By.ID,"maisDetalhes")))
                retorno_dados = []
                tam_informacoes = self.browser.find_elements_by_xpath('//*[@id="maisDetalhes"]/dl/dd') # Se tiver mais de 10 então possui campos a mais

                list_campos = ["Classe judicial", "Assunto","Jurisdição", "Última distribuição","Valor da causa","Segredo de justiça?", "Prioridade?","Órgão julgador"]


                teste = self.browser.find_elements_by_class_name("dl-horizontal") # Existem quatro classes com esse nome, nelas estão as infoormações como orgão jugador, comarca etc
                # Pegar as informações do processo

                # for campos in teste: # Pega os campos que contém as informações, estão todos em dd
                campos = teste[0]
                j=0
                dados = campos.find_elements_by_tag_name('dt')  # Nome do campos , como orgão jugador
                info_dados = campos.find_elements_by_tag_name('dd') # informações sobre os campos , como: comarca de são
                for i in range(len(dados)): # Pegar as
                    if ( list_campos[j] in dados[i].text) and j<len(list_campos):
                        retorno_dados.append(info_dados[i].text)
                        j+=1
                comarca = teste[1].find_element_by_tag_name('dd').text
                retorno_dados.append(comarca)
                comarca = self.separar_comarca(comarca)
                if not comarca:
                    comarca =self.separar_comarca(retorno_dados[2])
                plp_codigo=str(self.browser.current_url)
                plp_codigo=plp_codigo.split('?id=')[-1]
                plp_codigo=plp_codigo.split('&ca')[0]


                print("comarca:", comarca)
                print("List retorno:" , retorno_dados)
                # return juizo, classe, assuntos_text, valor_causa, dt_distribuicao, self.status,comarca, Segredo de justiça?, Prioridade?
                return retorno_dados[2],retorno_dados[0],retorno_dados[1],Tools.treat_value_cause(retorno_dados[4]),\
                       Tools.treat_date(retorno_dados[3]), self.status,comarca, \
                       "NÃO" in retorno_dados[5],"NÃO" in  retorno_dados[6],plp_codigo


            except Exception as Erro :
                tentativas +=1
                print(Erro)
                print("\n\n\n\t\t\t\tERRO\n\n\n")
                self.browser.refresh()
                self.log_error.insert_log("erro ao pegar dados do processo!")
                titulo = self.browser.find_elements_by_class_name("titulo-topo")  # Onde será clilcado para abrir
                titulo[0].click()
                WebDriverWait(self.browser,5).until(EC.visibility_of_element_located((By.ID, 'divTimeLine:txtPesquisa'))) # Esperar a pagina carregar


            # raise
            return None, None, None, None, None, None, None, None, None, None

    def get_caracteristicas(self, prc_id,n_proc):
        tentar = 0

        juizo, classe, assunto, valor_causa, dt_distribuicao, status, comarca, segredo, prioridade = [None for i in range(9)]

        while tentar < 2:
            try:
                juizo, classe, assunto, valor_causa, dt_distribuicao, status,comarca, segredo,prioridade,plp_codigo= self.get_dados_processo()
                self.browser.switch_to_window(self.browser.window_handles[-1])  # Status está na pagina de busca
                break
            except Exception as erro:

                tentar+=1
                print("Erro : " + str(erro))
                self.recuperar_pag_envolvidos(numero_processo=n_proc)  # Recarega a pagina
                print("\n\n\n\t\t\t\tERRO\n\n\n")


                self.log_error.insert_log("AO PERGAR AS PARTES : " + str(erro))

        return ProcessoPlataformaModel( plp_prc_id=prc_id, plp_plt_id=self.platform_id,
                                        plp_numero=n_proc, plp_status=status, plp_juizo=juizo,
                                        plp_valor_causa=valor_causa, plp_classe=classe,plp_codigo= plp_codigo,
                                        plp_grau= self.grau,plp_assunto=assunto,plp_localizado=1,
                                        plp_data_distribuicao=dt_distribuicao,plp_segredo=segredo,
                                        plp_comarca= comarca, plp_prioridade=prioridade )

    # SELECIONA PROCESSOS DO BANCO DE DADOS E PROCURA NA PLATAFORMA PARA UPDATE NO BANCO

    def realizar_loguin(self):

        # Inicialzar o browser
        try:
            inicializacao = self.init_browser()
        except:
            raise
        if inicializacao: # Se for falso deu algo de errado
            loguin = self.login() # Realiza o loguin na plataforma
            if not loguin: #  Se não conseguiu logar
                return False
            return  True
        return  False

    def prefixos_pje_civel(self, state):
        map = {'MA': '810','DF':'807','PA':'814', 'RO':'822', 'BA':'805' }

        for i in map.keys():
            if i == state:
                return map[state]
        return  False


    def coloca_numero_campos(self, numero_processo, xpath ='//*[@id="fPP:numProcessoDiv"]/div/div/div[2]/input' ):

        # buscar campo inteiro
        print("Numero_processo:", numero_processo)
        campo = self.browser.find_elements_by_xpath(xpath)
        # Intervalos para setar o campo

        tam_campos = [0,7,9,13,14,16,21]
        i = 0
        # print("Tamanho dos compos:", len(campo))
        # sleep(60*60)
        for preencher in campo:

            preencher.clear()
            preencher.send_keys(numero_processo[tam_campos[i]:tam_campos[i+1]])
            i+=1
        #Buscar o processo na plataforma
        campo[-1].send_keys(Keys.RETURN)
        WebDriverWait(self.browser,20).until(EC.invisibility_of_element((By.ID, '_viewRoot:status.start')))  # Esperar o site carregar


    def clicar_ir_acompanhamento(self, numero_procurar, ba = None ):

        tabela = self.browser.find_elements_by_xpath('//*[@id="fPP:processosTable:tb"]/tr')  # Tabela de resultados

        for processo in tabela:  # Procurar o processo correto na tabela
            teste = processo.find_element_by_xpath('td[1]' if ba == None else 'td[2]').text  # Pega o numero do processo que esta na tabela
            numero = self.tratar_numero_processo(teste)  # Deixa apenas numeros
            if numero_procurar == numero:  # Achou então clilcar nele para abrir
                processo.find_element_by_xpath('td[1]/a' if ba == None else 'td[1]/a[1]').click()
                break
        # As vezes o alerta aparece as vezes não
        try:  # Gambirar para ver se existe alerta
            # input('As vezes o alerta aparece as vezes não')
            WebDriverWait(self.browser, 0.8).until(EC.alert_is_present())
            alert = self.browser.switch_to.alert
            alert.accept()
        except:
            pass
        # Espera abrir as duas janelas
        wait = WebDriverWait(self.browser,20)
        wait.until(EC.number_of_windows_to_be(2))
        self.browser.switch_to_window(self.browser.window_handles[-1])
        self.browser.maximize_window()
        wait.until(EC.visibility_of_element_located((By.ID, 'divTimeLine:txtPesquisa')))

        return 1

    def segredo_de_justica(self, numero):
        # O NUMERO DO PROCESSO JÁ E TRATADO
        # RETORNA TRUE SE É SEGREDO DE JUSTIÇA E FALSE CASO CONRTARIO
        # VERIFICA EM PETICIONAR SE E SEGREDO DE JUSTIÇA
        # 1 SE FOR BAHIA E TIVER ACHADO O PROCESSO

        try:
            wait = WebDriverWait(self.browser,3)
            link_peticionar = self.link_consulta.replace('pje/Processo/ConsultaProcesso/listView.seam', 'pje/Processo/CadastroPeticaoAvulsa/peticaoavulsa.seam')
            self.browser.get(link_peticionar)

            #xpath campo onde serão colocados o numero do processo
            xpath = '//*[@id="fPP:consultaPeticaoSearchForm"]/div/div/div[2]/input'
            wait.until(EC.visibility_of_element_located((By.XPATH,xpath+'[1]'))) # Esperar o campo aparecer

            self.coloca_numero_campos(numero,xpath)

            wait = WebDriverWait(self.browser, 2)
            wait.until(EC.invisibility_of_element_located((By.ID,'modalStatusContainer')))

            aux=self.browser.find_elements_by_xpath('/html/body/div[6]/div/div/div/div[2]/form/div[2]/div[2]/dl/dt/span')
            if not len(aux):
                wait.until(EC.visibility_of_element_located((By.XPATH,'//*[@id="fPP:processosTable:tb"]/tr/td[1]/a[1]')))
                prc_em_segredo =  self.browser.find_elements_by_xpath('//*[@id="fPP:processosPeticaoGridPanel_body"]/dl/dt/span')
                if len(prc_em_segredo)> 0: # Chegou aqui, achou o processo e apreceu uma mensagem cima dele, então é segredo de justiça !
                    return True # é segredo de justiça
                # if self.state == "BA":
                self.clicar_ir_acompanhamento(numero,True) # Clilcar para abrir o processo
                return 2

            if aux[0].text == 'Não foi encontrado o processo pesquisado. Por favor, verifique o número inserido.':
                return False
            if 'sigiloso' in  aux[0].text :
                return True


        except Exception as erro:
            self.log_error.insert_log(str(erro))
            print("\n\n\n\t\t\t\tERRO\n\n\n")

            return False

            #SE PASSAR AQUI ENTÃO ESTÁ EM SEGREDO
            # print("fdfjidf")


    def tirar_caractere_string(self, str):
        filtro = re.compile('([0-9]+)') # Pegar apenas numeros
        teste = filtro.findall(str) # Lista dos numeros
        str_final = ""
        for i in teste:
            str_final+= i
        return str_final

    def tratar_numero_processo(self,numero):
        num_tratado =  self.tirar_caractere_string(numero) # Deixa apenas numeros
        if len(num_tratado) < 20:
            num_tratado = (20- len(num_tratado))*"0" + num_tratado
        return  num_tratado


    def buscar_processo_plataforma(self,numero_processo):
        # SE ACHOU O PROCESSO RETORNA 2, SE NÃO ACHOU 0, SEGREDO DE JUSTIÇA -1
        if len(numero_processo) != 20:
            numero_processo = numero_processo.lstrip('0')
            numero_processo = numero_processo.rjust(20, '0')

        tentar = 0
        print("Stado:", self.state)

        #

        try:
            if len(self.browser.find_elements_by_xpath('//*[@id="j_id118"]/span')):
                self.browser.execute_script('fecharPopupAlertaCertificadoProximoDeExpirar();')
        except Exception as erro:
            print("\n\n\n\t\t\t\tERRO\n\n\n")
            # input(str(erro))        # input('599')


        while tentar < 2:
            tentar+=1
            try:
                wait = WebDriverWait(self.browser, 3)
                link_peticionar = self.link_consulta.replace('/Processo/ConsultaProcesso/listView.seam',
                                                             '/Processo/CadastroPeticaoAvulsa/peticaoavulsa.seam')
                self.browser.get(link_peticionar)

                # xpath campo onde serão colocados o numero do processo
                xpath = '//*[@id="fPP:consultaPeticaoSearchForm"]/div/div/div[2]/input'
                wait.until(EC.visibility_of_element_located((By.XPATH, xpath + '[1]')))  # Esperar o campo aparecer

                self.coloca_numero_campos(numero_processo, xpath)
                try:
                    alert = self.browser.switch_to_alert()
                    alert.accept()
                except Exception as erro:
                    print("\n\n\n\t\t\t",erro,'\n\n\n\n')

                wait = WebDriverWait(self.browser, 2)
                # input("desejas continuar")
                wait.until(EC.invisibility_of_element_located((By.ID, 'modalStatusContainer')))

                aux = self.browser.find_elements_by_xpath('/html/body/div[6]/div/div/div/div[2]/form/div[2]/div[2]/dl/dt/span')
                # input("deseja continuar -> {}".format(len(aux)))
                if not len(aux):
                    self.clicar_ir_acompanhamento(numero_processo, True)  # Clilcar para abrir o processo
                    return 2

                sigilo=0
                if'sigiloso' in aux[0].text:
                    sigilo=1

                return sigilo


                return sigilo


            except Exception as erro:
                self.log_error.insert_log(str(erro))


                return 0

    def montar_objeto_nao_encontrado(self,plp_localizado,prc_id,n_proc,segredo):

        self.log_error.insert_info('Processo não encontrado!')
        print('Processo não encontrado!\nplp_localizado{}'.format(plp_localizado))
        if (plp_localizado == None):
            plp_localizado = 2
        elif 1 < plp_localizado < 5:
            plp_localizado += 1
        elif plp_localizado == 1:
            plp_localizado = 1
        else:
            plp_localizado = 0

        process_platform = ProcessoPlataformaModel(plp_prc_id=prc_id, plp_plt_id=self.platform_id,
                                                   plp_numero=n_proc, plp_segredo= segredo == 1, plp_grau=self.grau,

                                                   plp_localizado=plp_localizado if segredo ==0 else 1)



        return  process_platform

    def tamanho_movimentacoes(self):
        # FUNÇÃO PARA PEGAR O TAMANHO DAS MOVIMENTAÇÕES
        xpath_movimentos = '//*[@id="divTimeLine:divEventosTimeLine"]/div'
        if self.state == "PA":
            # xpath_lista_movimentacoes = '//*[@id="divTimeLine:eventosTimeLineElement"]/div'.format('divEventosTimeLine') # Lista de movimentações
            xpath_movimentos = xpath_movimentos.replace('divEventosTimeLine','eventosTimeLineElement')  # Lista de movimentações
        tam = len(self.browser.find_elements_by_xpath(xpath_movimentos)) # PEGAR O TAMANHO DAS MOVIMENTAÇÕES
        k = 0
        while k < tam:
            try:
                self.espera_view()
                coordenadas = self.new_linha((tam - 1)).location_once_scrolled_into_view # COLOCA O ELEMENTO VISIVEL NA TELA
                self.browser.execute_script('window.scrollTo({}, {});'.format(coordenadas['x'], coordenadas['y']))
                self.espera_view()
            except:
                print("\n\n\n\t\t\t\tERRO\n\n\n")

                pass
            self.espera_view()
            k = tam
            print("MOV ATUAL:", tam)
            tam = len(self.browser.find_elements_by_xpath(xpath_movimentos)) # ATUALIZAR O TAMANHO, AS VEZES A PAGINA PODE RECARREGAR
        self.browser.refresh()
        self.espera_view()
        return tam

    def reposicionar_movimentacoes(self,i):
        # FUNÇÃO PARA PEGAR O TAMANHO DAS MOVIMENTAÇÕES
        xpath_movimentos = '//*[@id="divTimeLine:divEventosTimeLine"]/div'
        if self.state == "PA":
            # xpath_lista_movimentacoes = '//*[@id="divTimeLine:eventosTimeLineElement"]/div'.format('divEventosTimeLine') # Lista de movimentações
            xpath_movimentos = xpath_movimentos.replace('divEventosTimeLine',
                                                        'eventosTimeLineElement')  # Lista de movimentações
        tam = len(self.browser.find_elements_by_xpath(xpath_movimentos))  # PEGAR O TAMANHO DAS MOVIMENTAÇÕES
        k = 0
        while k < tam:
            try:
                self.espera_view()
                coordenadas = self.new_linha(
                    (tam - 1)).location_once_scrolled_into_view  # COLOCA O ELEMENTO VISIVEL NA TELA
                self.browser.execute_script('window.scrollTo({}, {});'.format(coordenadas['x'], coordenadas['y']))
                self.espera_view()
            except:
                pass
            self.espera_view()
            k = tam
            if i <= k:
                self.espera_view()
                coordenadas = self.new_linha(
                    (i - 1)).location_once_scrolled_into_view  # COLOCA O ELEMENTO VISIVEL NA TELA
                self.browser.execute_script('window.scrollTo({}, {});'.format(coordenadas['x'], coordenadas['y']))
                self.espera_view()
                return True
            print("MOV ATUAL:", tam)
            tam = len(self.browser.find_elements_by_xpath(
                xpath_movimentos))  # ATUALIZAR O TAMANHO, AS VEZES A PAGINA PODE RECARREGAR

        return False

    def espera_view(self):
        try:
            WebDriverWait(self.browser, 10).until(EC.invisibility_of_element(
               (By.ID, '_viewRoot:status.start')))  # Esperar o site carregar
            return  True
        except:
            print("\n\n\n\t\t\t\tERRO\n\n\n")
            return  False

    def numero_processo(self,numero_processo):
        if len(numero_processo) != 20:
            numero_processo = numero_processo.lstrip('0')
            numero_processo = numero_processo.rjust(20, '0')
        prefixo = list(self.prefixos_pje_civel(self.state))
        novo = list(numero_processo)
        # print("prefixo",prefixo)
        # print('novo',novo)
        i = 0
        while i < 3:
            novo[13+i] = prefixo[i]
            i+=1
        return  ''.join(novo)

    def search_process_to_update(self, row_database, dict_plp_2grau):
        self.tamanho_total_mov = 0
        # INICIA O BROWSER E A SESSÃO NA PLATAFORMA
        # logou = self.initializer()
        loguin = False
        cont = 0

        while(not loguin) and cont < 3:

            loguin = self.realizar_loguin()
            if not loguin:
                print("NÃO LOGOU, TENTANDO DE NOVO....")
                try:
                    self.browser.quit()
                except:
                    print("\n\n\n\t\t\t\tERRO\n\n\n")


                    pass
            cont+=1
        if cont >= 3:
            print("NÃO CONSEGUIU LOGAR, TENTAR RODAR DE NOVO OS PROCESSOS")
            return -1
        print("Logou ? ", loguin)
        #sleep(60*60)
        list_partes = []
        list_advogs = []

        # VERIFICA CADA NUMERO DE PROCESSO DENTRO DA ESTRUTURA FORNECIDA
        i_n = 0
        #self.browser.set_window_position(-10000,0)

        for i_proc in row_database:
            try:
                list_aud = []
                list_acp_pra = []
                list_name_urls = []
                list_partes = []
                list_advogs = []

                i_n+=1
                prc_numero, prc_id, prc_estado, plp_status, cadastro, plp_codigo, plp_data_update, plp_id, plp_numero, \
                plp_localizado, t0, list_2_grau, list_plp_2_grau = self.fragimentar_dados_dos_processo(
                    dados_do_prosseco=i_proc,dict_plp_2grau=dict_plp_2grau)
                # prc_numero = "07042319320198070001"
                # prc_numero = "00020566320108140010"
                prc_numero = self.numero_processo(prc_numero)

                prc_numero = self.numero_processo(prc_numero)

                print("VERREDURA NUMERO :",i_n, " NUMERO DO PROCESSO: ",prc_numero)

                self.log_error.insert_title(prc_numero)
                # prc_numero='00027591520138140066'#Segredo

                #Busca processo na plataforma
                situacao_processo  = self.buscar_processo_plataforma(prc_numero)

                print("Busca: ", "Achou" if situacao_processo == 2 else "Não Achou")
                # print(f'situacao_processo  {situacao_processo}')
                if situacao_processo == 2: # Achou o processo,  pegar as informações

                    # COLETA OS ACOMPANHAMENTOS DO PROCESSO
                    status, novas_movimentacoes,bool_2_grau_numero = \
                        self.acomp_down_aud(None if "2" in str(self.grau) else cadastro,list_aud, list_acp_pra, list_name_urls)
                    print("PROCESSO ", "É DO" if bool_2_grau_numero else "NÃO E DO", "SEGUNDO GRAU!")
                    process_platform = ProcessoPlataformaModel()

                    if novas_movimentacoes == None:
                        lista_aud_aux = self.treat_audience(list_aud,prc_id)
                        list_aud = lista_aud_aux

                        # COLETA DO NUMERO DO PROCESSO DO 2 GRAU E CRIAR O PLP COM HAJA NO 2º GRAU!
                        list_plp_2_grau = []
                        if "1" in str(self.grau) :
                            self.validar_bool_2_grau(list_2_grau=list_2_grau, bool_2_grau_numero=bool_2_grau_numero,
                                                        prc_numero=prc_numero, prc_id=prc_id
                                                     )
                        print("LISTA DE SEGUNDO GRAU : ", list_2_grau)
                           #ENVOLVIDOS E RETORNA UMA LISTA COM AS PARTES, OS ADVOGADOS E O JUIZ
                        list_partes, list_advogs = self.envolvidos(prc_numero)

                        # CRIA O OBJETO PROCESSO-PLATAFORMA QUE SERÁ INSERIDO NO BANCO DE DADOS
                        process_platform = self.get_caracteristicas(prc_id,prc_numero)

                    self.log_error.insert_info('Procedimento finalizado!')
                    # self.browser.switch_to_window(self.browser.window_handles[-1])
                    # self.browser.close()
                    # self.browser.switch_to_window(self.browser.window_handles[0])

                elif(str(self.grau) in "2" and 0<=situacao_processo <= 1) or "1" in str(self.grau) : # Chegou aqui é segredo de justica ou não localizado
                    process_platform = self.montar_objeto_nao_encontrado(plp_localizado,prc_id,prc_numero,situacao_processo)


                # CRIANDO  LISTA OBJETOS E INSERINDO NO BANCO DE DADOS
                if (str(self.grau) in "2" and situacao_processo == 2) or "1" in str(self.grau):
                    self.construct_list_obj_insert_bd(process_platform=process_platform, list_partes=list_partes,
                                                  list_advogs=list_advogs, list_aud=list_aud, list_acp_pra=list_acp_pra,
                                                  plp_id=plp_id, list_plp_2_grau=list_plp_2_grau,
                                                  list_name_urls=list_name_urls
                                                  )

                print('###Tempo total da coleta de dados do processo: {} SECS'.format(time.time() - t0).upper())
                print('-' * 65)
            except Exception as ERRO:
                print("\n\n\n\t\t\t\tERRO\n\n\n")

                print(ERRO)
                self.log_error.insert_log(str(ERRO))
                continue
            i_n+=1


        # VERIFICA SE O NAVEGADOR FECHOU, SENÃO O FECHA
        if self.browser is not None:
            self.browser.quit()

        # VERIFICA SE NÃO RETORNOU ALGUM PROCESSO DA BASE, SENÃO ATUALIZA A PLE_DATA
        # self.update_ple_data(ple_plt_id=self.platform_id, ple_uf=self.state)

        return i_n

    # REALIZA O DOWNLOAD DO ARQUIVO
    def check_download(self, acp, prc_id, n_event, file_downloaded, list_name_urls, list_file_name, list_file_path):
        err = False
        try:
            bara = self.browser.find_element_by_xpath('//*[@id="divTimeLine:divEventosTimeLine"]/div[1]')  # Data fica na frete do click ocutar ele
            self.browser.execute_script('arguments[0].style.display = "none";', bara)  # ocutar a data
            wait = WebDriverWait(self.browser, 60)
            wait.until(EC.invisibility_of_element((By.ID, '_viewRoot:status.start')))

            n_files = len(os.listdir(self.path_download_prov)) #+ 1
            bara = self.browser.find_element_by_xpath('//*[@id="divTimeLine:divEventosTimeLine"]/div[1]')  # Data fica na frete do click ocutar ele
            self.browser.execute_script('arguments[0].style.display = "none";', bara)  # ocutar a data
            button_download = acp.find_element_by_xpath('//*[@id="detalheDocumento:download"]')
            webdriver.ActionChains(self.browser).move_to_element(button_download).click(button_download).perform()
            # button_download.click()
            wait = WebDriverWait(self.browser, 10)
            wait.until(EC.alert_is_present())
            alert = self.browser.switch_to_alert()
            alert.accept()
            self.browser.switch_to_default_content()
            bara = self.browser.find_element_by_xpath('//*[@id="divTimeLine:divEventosTimeLine"]/div[1]')  # Data fica na frete do click ocutar ele
            self.browser.execute_script('arguments[0].style.display = "none";', bara)  # ocutar a data

            err_down = self.wait_download(n_files)
            try:  # VERIFICA SE A SESSÃO FOI ENCERRADA
                if len(self.browser.window_handles) > 2:
                    if self.browser is not None:
                        self.browser.quit()
            except:
                self.log_error.insert_log('Download do arquivo: evento {}!'.format(n_event))
                err = True
                print("\n\n\n\t\t\t\tERRO\n\n\n")


            if not err_down:
                for arq in os.listdir(self.path_download_prov):
                    if arq not in list_file_path:
                        list_file_path.append(arq)
                        file_downloaded = arq
                        break

                desc_file = file_downloaded.split('.')[0]
                nome = Tools.convert_base(str(datetime.now()))
                list_name_urls.append((nome, file_downloaded))
                ext = file_downloaded.split('.')[-1].lower()
                nome = nome + '.' + ext
                list_file_name.append(ProcessoArquivoModel(pra_prc_id=prc_id,
                                                           pra_nome=nome,
                                                           pra_descricao=desc_file))
                acp_pra_status = True
            else:
                # print("VARIAVEL CHECK TRUE pjemodel 466")
                self.log_error.insert_log('Download do arquivo: evento {}!'.format(n_event))
                acp_pra_status = False
        except:
            print("\n\n\n\t\t\t\tERRO\n\n\n")

            self.log_error.insert_log('Download do arquivo: evento {}!'.format(n_event))
            acp_pra_status = False

        # print("Saiu da função check!")
        return acp_pra_status, err, list_file_name

        # PEGA ANDAMENTOS DO PROCESSO, AS AUDIÊNCIAS E REALIZA OS DOWNLOADS POR ACOMPANHAMENTO

    # PEGA ANDAMENTOS DO PROCESSO, AS AUDIÊNCIAS E REALIZA OS DOWNLOADS POR ACOMPANHAMENTO

    # ir na aba de audiencias e pegar as audiencias
    def pegar_audiencias_nova_aba(self):

            id_opcao_audiencia = 'navbar:linkAbaAudiencia'  # opçao que deve ser cliclado para ir para aba de audienci
            xpath_tabela_audiencia = '//*[@id="processoConsultaAudienciaGridList:tb"]/tr'
            # input('id_opcao_audiencia = '.format(id_opcao_audiencia))

            lista_de_audiencia = []
            if  len( self.browser.find_elements_by_id(id_opcao_audiencia))==0:
                return lista_de_audiencia


            wait = WebDriverWait(self.browser, 60)  # Objeto para espera
            wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME,'btn-menu-abas')))  # Esperar a bara do menu apararecer
            menu = self.browser.find_elements_by_class_name('btn-menu-abas') # Botão superior do menu
            menu[-1].click() # Cliclar para abrir o menu

            # Esperar todas as opções do menu aparecer
            # input(" \n\n\n\t\t951")
            wait.until(EC.visibility_of_element_located((By.ID,id_opcao_audiencia))) # Esperar A opção de audiencia aparecer

            self.browser.find_elements_by_id(id_opcao_audiencia)[0].click() # Abrir as audiencias

            wait.until(EC.invisibility_of_element((By.ID, '_viewRoot:status.start')))  # Esperar o site carregar

            # CHEGOU AQUI JÁ ESTA NA PAGINA DE AUDIENCIAS, A TABELA DEVERÁ APARECER
            tabela_audiencia = self.browser.find_elements_by_xpath(xpath_tabela_audiencia)  # Pegar a tabela de audiencias, todas as linhas (tr)
            for i in tabela_audiencia:  # Varrer a tabela de audiencias para pegar as informações, linha por linha

                aux = ''

                tipo = i.find_element_by_xpath('td[2]').text.upper()  # Tipo de audiencia

                status = i.find_element_by_xpath('td[4]').text.upper()  # Status da audiencia

                data = Tools.treat_date(i.find_element_by_xpath('td[1]').text)  # Data prevista

                obs = i.find_element_by_xpath('td[3]').text.upper()  # Obs
                # aux = aux.upper() # Passar para maiúscula


                lista_de_audiencia.append((tipo, status, data, obs, None))

            # sleep(60 * 60)
            return lista_de_audiencia

    def voltar_para_acompanhamentos(self):


        id_acompanhamentos = 'navbar:linkAbaAutos'

        wait = WebDriverWait(self.browser, 60) # Objeto para espera dos elementos aparecerem
        wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'btn-menu-abas')))  # Esperar a bara do menu apararecer
        menu = self.browser.find_elements_by_class_name('btn-menu-abas')  # Botão superior do menu
        menu[-1].click()  # Cliclar para abrir o menu # Clicar para abrir as opções

        wait.until(EC.visibility_of_element_located((By.ID, id_acompanhamentos))) # Espera a opção para ir para os acompanhamentos aparecer
        self.browser.find_element_by_id(id_acompanhamentos).click() # clicar para ir para os acompanhamentos

        wait.until(EC.invisibility_of_element((By.ID, '_viewRoot:status.start')))  # Esperar o site carregar

        # TIRAR A DATA DOS ACOMPANHAMENTOS VISIVÉIS NA TELA

        # VERIFICA SE FEZ O DONWLOAD DO ARQUIVO CORRETAMETE

    def verifica(self, n_files, list_file_path, list_name_urls, nome_donwload = None):

        err_down = self.wait_download(n_files)
        print(f"err_dow -> {err_down}")
        if not err_down:  # not err_down: # se o download concluiu totalmente sem nehum erro
            # print('dentro if')
            arquivo = set(os.listdir(self.path_download_prov)).difference(set(list_file_path))  # difereça de dois conjunts

            # print('hduahdushadhsuadushauhdusauhduau')

            file_downloaded = arquivo.pop()  # .replace('.pdf','') # pega o nome do arquivo que foi baixado
            arquivo = list(arquivo)
            if len(arquivo) > 1:  # Tem multiplos donwloads
                for i in range(0, len(arquivo), 1):
                    nome = Tools.convert_base(str(datetime.now()))
                    # nome = nome + '.' + arquivo[i].split('.')[-1]
                    print("Nome multiplos->", nome)
                    list_name_urls.append((nome, arquivo[i]))
                print("multiplos")
                self.log_error.insert_log("Multiplos donwloads processo, verificar!!")

            # print('Nome donload: ', file_downloaded)
            nome = Tools.convert_base(str(datetime.now())) if nome_donwload == None else nome_donwload
            list_name_urls.append((nome,file_downloaded))  # Primeiro é o nome que quer renomear segundo o original, o primeiro não tem extensão
            # ext = file_downloaded.split('.')[-1].lower()
            nome = nome + '.' + file_downloaded.split('.')[-1]
            # print("Nome donload :", nome, "File: ", file_downloaded)
            # desc_file = file_downloaded.replace("." + ext, '')

            # self.dicionario_acompanhamento[numero_acompanhamento].append(file_downloaded) # ADICIONANDO O NOME DO DONWLOAD, IDEPENDENTE SE TERMINOU DE BAIXAR OU NAO

            return True, ProcessoArquivoModel(pra_nome=nome, pra_descricao=file_downloaded)

        return False, None

    @staticmethod
    def treat_audience(list_audiences, prc_id) :
        # print(">>>>>>>>>Lista de audiência>>>",list_audiences)
        try :
            dict_audiences = {}
            list_audiences.reverse()
            for i_aud in list_audiences :

                tipo, status, data1, obs, data2 = i_aud
                # print(tipo, status, data1, obs, data2 )
            for i_aud in list_audiences :

                tipo, status, data1, obs, data2 = i_aud
                # print(f"tipo {tipo}, status{status}\n data1 {data1},  data2 {data2} \nobs {obs},")

                if data1 is not None :
                    key = data1.timetuple()[:3]
                    data = data1

                    str_data = str(data)
                    if str_data[0] == "0":
                        str_data = "2" + str_data[1:]
                        g = str_data.split(' ')
                        str_data = g[0].split('-')[-1] +"/" + g[0].split('-')[-2]+"/" + g[0].split('-')[-3] +" "+ g[-1]

                        data = Tools.treat_date(str_data)
                        key = data.timetuple()[:3]
                else :

                    key = data2.timetuple()[:3]

                    data = data2
                    list_aux = list(dict_audiences.keys())
                    list_aux.append(key)
                    list_aux.sort()
                    i = list_aux.index(key) - 1
                    if i < 0 :
                        continue
                    key = list_aux[i]

                print("key",key)

                # print("Data: testetettetet : ", (data))




                if status == 'DESIGNADA' and key not in dict_audiences.keys() :


                    dict_audiences[key] = AudienciaModel(aud_tipo=tipo,
                                                         aud_status=status,
                                                         aud_data=data,
                                                         aud_obs=obs,
                                                        aud_prc_id=prc_id
                                                         )

                elif status in [ 'CONCLUÍDA','DESIGNADA', 'REDESIGNADA', 'NEGATIVA', 'CANCELADA', 'NÃO-REALIZADA', 'REALIZADA','NÃO REALIZADA', 'PENDENTE'] :
                    # print("Data: testetettetet : ", data[0])
                    if  key not in dict_audiences.keys(): # Se não existir a chave então cria
                        dict_audiences[key] = AudienciaModel(aud_tipo=tipo,
                                                             aud_status=status,
                                                             aud_data=data,
                                                             aud_obs=obs,
                                                             aud_prc_id= prc_id
                                                             )

                    dict_audiences[key].aud_status = status if status is not None else dict_audiences[
                        key].aud_status
                    dict_audiences[key].aud_data = data if data is not None else dict_audiences[key].aud_data
                    dict_audiences[key].aud_tipo = tipo if tipo is not None else dict_audiences[key].aud_tipo

            list_audiences.clear()
            list_aux = []
            for i in dict_audiences.values() :
                if id(i) not in list_aux :
                    list_audiences.append(i)
                    print("\n", i.aud_tipo, '\n', i.aud_status, '\n', i.aud_data, '\n', i.aud_obs, '\n',i.aud_plp_id,'\n',i.aud_prc_id)
                    list_aux.append(id(i))
        except :
            print("\n\n\n\t\t\t\tERRO\n\n\n")
            list_audiences.clear()
            self.log_error.insert_log('coleta de dados das audiências do processo!'.upper())
            print('ERRO coleta de dados das audiências do processo!'.upper())
            # sleep(60*60)

            # raise

        return list_audiences

    def ocutar_data_pje(self):
        bara = self.browser.find_elements_by_class_name('data-interna')  # Data fica na frete do click ocutar ele
        data2_xpat='/html/body/div/div[2]/div[2]/table/tbody/tr[2]/td/table/tbody/tr/td/form[1]/div[2]/div[1]/div'
        # print(f"len({len(bara)})->{bara[0].text}",end='\t')
        if self.state == "PA":
            data2_xpat='/html/body/div/div[2]/div[2]/table/tbody/tr[2]/td/table/tbody/tr/td/form[1]/div[2]/div[1]/div[1]/div'

        data2_elemento= self.browser.find_elements_by_xpath(data2_xpat)

        self.browser.execute_script('arguments[0].style.display = "none";', data2_elemento[0])  # ocutar a data


        # Lista de movimentações
        self.browser.execute_script('arguments[0].style.display = "none";', bara[0])  # ocutar a data
        # input("dc")

    def new_linha(self,i):
        xpath_eventos='//*[@id="divTimeLine:divEventosTimeLine"]/div'
        if self.state == "PA":
            xpath_eventos = xpath_eventos.replace('divEventosTimeLine','eventosTimeLineElement')  # Lista de movimentações
        lista_de_movimentacoes = self.browser.find_elements_by_xpath(xpath_eventos) # Lista de movimentações)  # Pega todas as movimentações
        return lista_de_movimentacoes[i]

    def atualizar(self, caminho):
        aquivos_abaixo = self.browser.find_elements_by_xpath(caminho + '/ul')  # SE POSSUIR ESSA CLASSE (TREE), ENTÃO EXISTE MAIS ARQUIVOS PARA SEREM BAIXADOS
        arquivos_baixar = aquivos_abaixo[0].find_elements_by_xpath('li')
        return  arquivos_baixar

        # FAZ TODOS OS DONWLOADS DE UM ACOMPANHAMENTO

    def fazer_download(self, caminho, list_name_urls, lista_donwload,url_prov = None):

        # o primeiro donwload fica localizado na tag 'a'
        # lista_donwload é a lista de donwloads
        self.ocutar_data_pje()  # Tirar a data porque ela pode ficar na frente

        tentativas = 0
        wait = WebDriverWait(self.browser, 20)

        verificar = self.browser.find_elements_by_xpath(caminho+'/a')
        if len(verificar)==0: # Verificar se foi cancelado
            print("Cancelado")
            return True

        nome_arquivos = os.listdir(self.path_download_prov)  # quantidade de elementos antes do donwload
        # print("Tamanho dos donload : ", len(nome_arquivos))
        div_anexos = self.browser.find_element_by_xpath(caminho)  # Caminho onde estão os donwloads
        nome =[] # Lista de nomes dos downloads
        indice_id = 0
        nomes_span = div_anexos.find_elements_by_tag_name('span') # nomes dos dowloads que está na pagina(cada nome tem um id) estão na span
        for i in nomes_span:
            aux = str(i.text)
            aux = aux.split("-")[0]
            nome.append(aux)

        wait.until(EC.element_to_be_clickable((By.XPATH, caminho + '/a')))
        self.browser.execute_script("arguments[0].click();", div_anexos)
        # div_anexos.find_element_by_xpath('a').click() # cliclar na linha que tem do donwload e o documento aparecera no lado

        wait.until(EC.invisibility_of_element((By.ID, '_viewRoot:status.start')))  # Esperar o documento aparecer

        self.ocutar_data_pje()


        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="detalheDocumento:download"]')))

        button_download = self.browser.find_element_by_xpath('//*[@id="detalheDocumento:download"]')  # Icone do botão

        button_download.click()  # CLICLAR PARA BAIXAR


        WebDriverWait(self.browser, 5).until(EC.alert_is_present())
        alerta = self.browser.switch_to_alert()
        alerta.accept()  # Aceitar, ou clicar em "OK"

        self.ocutar_data_pje()
        # DONWLOAD É UM OBJETO PROCESSO ARQUIVO MODEL
        # print("Antes verifiva")
        # print("Tamanho dos donload depois do click: ", len(os.listdir(self.path_download_prov)))

        # self.dicionario_acompanhamento[numero_movimentacao] = [] # map de nomes de download

        # CHEGOU AQUI ESTA FAZENDO DONWLOAD
        acp_pra_status, download = self.verifica(len(nome_arquivos), nome_arquivos,
                                                 list_name_urls,nome[indice_id])  # esperar o download concluir
        indice_id+=1
        # print("Depis verifica")
        if download  is not None:
            lista_donwload.append(download)  # TODOS DOWNLOADS DESSE ACOMPANHAMENTO ESTARÁ AQUI


        while(len(self.browser.window_handles)>2): # esperar a aba fechar
            sleep(0.2) #
            print("Passou")
            pass

        aquivos_abaixo = self.browser.find_elements_by_xpath(
            caminho + '/ul')  # SE POSSUIR ESSA CLASSE (TREE), ENTÃO EXISTE MAIS ARQUIVOS PARA SEREM BAIXADOS
        posicao_movimentacao=int(caminho.split(']/div[')[1])# NUMERO CORRESPONDENETE A MOVIMENTAÇÃO

        if len(aquivos_abaixo) == 0:
            return True
        coordenadas = aquivos_abaixo[0].location_once_scrolled_into_view  # Colocar visivel
        self.browser.execute_script('window.scrollTo({}, {});'.format(coordenadas['x'], coordenadas['y']))
        arquivos_baixar = aquivos_abaixo[0].find_elements_by_xpath('li')  # nas LI está todos os sub aquivos para serem baixado

        tam_aquivos = len(arquivos_baixar)
        sub_aquivos = 0
        acp_st = acp_pra_status
        while sub_aquivos < tam_aquivos:  # interar na lista de sub arquivos
            # sleep(1)
            try:
                text=arquivos_baixar[sub_aquivos].find_element_by_xpath('a').text

                self.ocutar_data_pje()  # Tirar data ela pode ficar na frente
                arquivos_baixar = self.atualizar(caminho)
                self.ocutar_data_pje()  # Tirar data ela pode ficar na frente
                coordenadas = arquivos_baixar[sub_aquivos].location_once_scrolled_into_view  # Colocar visivel
                self.browser.execute_script('window.scrollTo({}, {});'.format(coordenadas['x'], coordenadas['y']))
                nome_arquivos = os.listdir(self.path_download_prov)  # quantidade de elementos antes do donwload

                arquivos_baixar[sub_aquivos].find_element_by_xpath('a').click()
                # print(1189)
                wait.until(EC.invisibility_of_element((By.ID, '_viewRoot:status.start')))  # Esperar o documento aparecer
                while (len(self.browser.window_handles) > 2):  # esperar a aba fechar
                    print("While subfiles")
                    pass

                self.ocutar_data_pje()


                if 'fa fa-file-pdf-o mr-10' in  arquivos_baixar[sub_aquivos].find_element_by_xpath('a/i').get_attribute("class"):
                    WebDriverWait(self.browser, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="detalheDocumento:download"]')))
                    div_anexos = self.browser.find_element_by_xpath(caminho)  # Caminho onde estão os donwloads
                    button_download = div_anexos.find_element_by_xpath('//*[@id="detalheDocumento:download"]')  # Icone do botão

                    button_download.click()

                    WebDriverWait(self.browser, 5).until(EC.alert_is_present())

                    # sleep(0.5)
                    alerta = self.browser.switch_to_alert()
                    alerta.accept()  # Aceitar, ou clicar em "OK"

                acp_st = acp_pra_status

                acp_pra_status, download = self.verifica(len(nome_arquivos), nome_arquivos,
                                                         list_name_urls,nome[indice_id])  # esperar o download concluir

                acp_st = acp_st and acp_pra_status

                if download  is not None :
                    lista_donwload.append(download)
                sub_aquivos += 1
                while (len(self.browser.window_handles) > 2):  # esperar a aba fechar
                    pass

                indice_id+=1
            except ElementClickInterceptedException:  # Elemento esta obistruido, não da para cliclar
                self.log_error.insert_log("SubFiles acompanhamentos")
                print("Interceptado")

                tentativas += 1
                if tentativas > 4:
                    return False
            except Exception as erro:
                print("\n\n\n\t\t\t\tERRO\n\n\n")
                self.log_error.insert_log("SubFiles acompanhamentos")
                if self.browser.current_url != url_prov:
                    self.browser.get(url_prov)
                tentativas += 1
                if tentativas > 6:
                    return False

                #QUANDO O scroll DA MOVIMENTÇAÕ VOLTA PARA O TOPO

                if self.reposicionar_movimentacoes(posicao_movimentacao):
                    aquivos_abaixo = self.browser.find_elements_by_xpath(caminho + '/ul')
                    arquivos_baixar = aquivos_abaixo[0].find_elements_by_xpath('li')  # nas LI está todos os sub aquivos para serem baixado
                    self.ocutar_data_pje()



                # raise

        return acp_st

    def carregar(self):

        for i in range(len(self.browser.find_elements_by_xpath('//*[@id="divTimeLine:divEventosTimeLine"]/div'))):
            try:
                wait = WebDriverWait(self.browser, 10)
                wait.until(EC.invisibility_of_element((By.ID, '_viewRoot:status.start')))
                acompanhamentos = self.browser.find_elements_by_xpath('//*[@id="divTimeLine:divEventosTimeLine"]/div')
                acompanhamentos[i].location_once_scrolled_into_view
            except:
                raise
                pass

    def tam_movimentacoes(self):
        xpath_movimentos = '//*[@id="divTimeLine:divEventosTimeLine"]/div'
        if self.state == "PA":
            xpath_movimentos = xpath_movimentos.replace('divEventosTimeLine',
                                                        'eventosTimeLineElement')  # Lista de movimentações

        lista_de_movimentacoes = self.browser.find_elements_by_xpath(xpath_movimentos) # Pega todas as movimentações
        return len(lista_de_movimentacoes)
    # Ira retornar uma lista contendo todos os acompanhamentos que deverão ser inseridos no banco de dados

    def verifica_segundo_grau(self,keyword_segundograu,descricao_acompanhamento):
         # Se ele foi para o segundo grau
            for keys in keyword_segundograu:
                if keys in descricao_acompanhamento:  # palavras chaves para o segundo grau
                    return True  # Se for segundo grau
            return False

    def pegar_lista_de_acompanhamentos(self, data_ultima_movimentacao):
        # self.browser.switch_to_window(self.browser.window_handles[-1])
        xpath_lista_movimentacoes = '//*[@id="divTimeLine:divEventosTimeLine"]/div' # Lista de movimentações
        if self.state == "PA":
            # xpath_lista_movimentacoes = '//*[@id="divTimeLine:eventosTimeLineElement"]/div'.format('divEventosTimeLine') # Lista de movimentações
            xpath_lista_movimentacoes = xpath_lista_movimentacoes.replace('divEventosTimeLine','eventosTimeLineElement') # Lista de movimentações
        # input(xpath_lista_movimentacoes)
            wait = WebDriverWait(self.browser, 35)
            wait.until(EC.presence_of_element_located((By.XPATH,xpath_lista_movimentacoes)))

        self.status = "ATIVO"
        caminho = xpath_lista_movimentacoes+'[{}]/div[2]/div[{}]'
        lista_de_movimentacoes = self.browser.find_elements_by_xpath(xpath_lista_movimentacoes) # Pega todas as movimentações
        keyword_segundograu = ['CONHECIDO O RECURSO DE', 'REMETIDOS OS AUTOS (EM GRAU DE RECURSO) PARA', 'INSTÂNCIA SUPERIOR']
        # input(xpath_lista_movimentacoes)
        segundo_grau = False
        list_name_urls_aux = []
        list_name_urls = []
        lista_audiencia = []
        lista_acompanhamentos =[]
        lista_donwload_acp =[]
        data_acompanhamento = ""
        file_downloaded = None
        list_file_path = []
        flag_pegar_acompanhamentos = True
        # Ultima div não e uma movimentação!!
        tamanho_movimentacoes = len(lista_de_movimentacoes)
        cont = 0
        k =0
        tentativas = 0
        i = 0
        url_prov = self.browser.current_url # Url dos acompanhamentos atuais
        # print(f" tamanho_movimentacoes -> {tamanho_movimentacoes}")
        # input()
        while i < (tamanho_movimentacoes): # Passar por todos os acompanhamentos para pegar as informações

            try:
                k+=1
                wait = WebDriverWait(self.browser, 10)

                wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="navbar"]')))
                print(f'i -> {i + 1}')
                linha = self.new_linha(i)# Pega todas as movimentações

                # Quando o nome da classe é 'media data' ou 'media data div-data-rolagem' é onde esta a data dos acompanhamentos
                # Quando o nome da classe é 'media interno tipo-D' é um acompanhamento e tem download
                # Quando o nome da classe é 'media interno tipo-M' é um acompanhamento mas não possui donwload

                wait.until(EC.invisibility_of_element((By.ID, '_viewRoot:status.start')))  # Esperar o documento aparecer

                wait.until(EC.presence_of_element_located((By.XPATH, xpath_lista_movimentacoes)))  # Esperar o documento aparecer

                nome_da_class_div = linha.get_attribute('class') # Pegar o nome da classe

                if 'media data div-data-rolagem' in nome_da_class_div: # Não possui infomação então passa para a proxima
                    i+=1
                    continue
                if 'media data' in nome_da_class_div  : # Se o nome da class é 'media data' então pegamos a data
                    data_acompanhamento = linha.text # Pegando a data
                    i+=1
                    continue # Não tem mais infomrações a serem pegas, então passa para o proximo

                self.ocutar_data_pje()
                wait.until(EC.invisibility_of_element((By.ID, '_viewRoot:status.start')))  # Esperar o documento aparecer

                coordenadas = linha.location_once_scrolled_into_view  # Ficar visivel na tela
                self.browser.execute_script('window.scrollTo({}, {});'.format(coordenadas['x'], coordenadas['y']))

                wait.until(EC.invisibility_of_element((By.ID, '_viewRoot:status.start')))  # Esperar o documento aparecer


                wait.until(EC.invisibility_of_element((By.ID, '_viewRoot:status.start')))  # Esperar o documento aparecer
                # input(' \n\n\t\t{}\n\n'.format(data_acompanhamento))
                data_atual =Tools.treat_date( data_acompanhamento)

                if  data_ultima_movimentacao != None and data_atual <= data_ultima_movimentacao:
                    flag_pegar_acompanhamentos = False
                    return lista_acompanhamentos,lista_audiencia, list_name_urls, False if i==2 else None,segundo_grau


                cont += 1

                if nome_da_class_div == 'media interno tipo-M': # é um acompanhamento mas não tem donwload pegar a descrição
                    self.ocutar_data_pje()
                    linha = self.new_linha(i)  # Pega todas as movimentações

                    coordenadas = linha.location_once_scrolled_into_view # Ficar visivel na tela
                    self.browser.execute_script( 'window.scrollTo({}, {});'.format(coordenadas['x'], coordenadas['y']))

                    self.ocutar_data_pje()
                    #text-muted pull-right
                    hora_teste = linha.find_elements_by_class_name('text-muted') # Pegar a hora do acompanhamento

                    hora_acompanhamento = hora_teste[0].text #if len(hora_teste)>0 and tentativas > 1 else ""
                    data_atual =data_acompanhamento+ ' '+hora_acompanhamento

                    data_atual = Tools.treat_date(data_atual)
                    # '/html/body/div/div[2]/div[2]/table/tbody/tr[2]/td/table/tbody/tr/td/form[1]/div[2]/div[1]/div[3]/div[2]/div[1]/span'
                    descricao_acompanhamento = linha.find_elements_by_xpath('div[2]') # xpath_lista de movimentacoes + 'div[2]/span' onde está a descrição do processo, se exixtir
                    if len(descricao_acompanhamento)==0: # não achou os dados do acompanhamento, no RO ele esta dentro de outra div
                        descricao_acompanhamento = linha.find_elements_by_xpath('div[2]/div[1]/span')


                    descricao_acompanhamento = descricao_acompanhamento[0].text# Passando para texto
                    descricao_acompanhamento = descricao_acompanhamento.upper()

                    segundo_grau = self.verifica_segundo_grau(keyword_segundograu,descricao_acompanhamento)
                    # Verificar se é audiencia e se não e um processo migrado do Projudi para o pje
                    if 'AUDIÊNCIA' in descricao_acompanhamento and not 'EVENTO PROJUDI:' in descricao_acompanhamento: # Se for uma audiencia
                       print(";", end=" ")
                       dados_adiencia =  self.separar_dados_audiencia(descricao_acompanhamento,Tools.treat_date(data_acompanhamento)) # Tratar as audiencias
                       if dados_adiencia != False: # Se retornar falso é porque não e uma audiencia, pode ser por exemplo: "PUBLICADO ATA DA AUDIÊNCIA EM 07/02/2019."
                          lista_audiencia.append(dados_adiencia)
                    if  i<3 and ('ARQUIVADO DEFINITIVAMENTE' in descricao_acompanhamento or 'ARQUIVADO' in descricao_acompanhamento):
                        self.status = "ARQUIVADO"


                    # Insere na lista, ja que não tem donwload
                    if flag_pegar_acompanhamentos: # Verificar se é para pegar o acompanhamento # + ' '+hora_acompanhamento
                        lista_acompanhamentos.append((AcompanhamentoModel(acp_esp=descricao_acompanhamento,acp_data_cadastro=data_atual, acp_numero= str(tamanho_movimentacoes - i)),lista_donwload_acp))
                elif nome_da_class_div =='media interno tipo-D' and flag_pegar_acompanhamentos: # Entrou aqui é porque possui donwload,  é a classe 'media interno tipo-D'
                     self.ocutar_data_pje()
                     linha = self.new_linha(i)  # Pega todas as movimentações
                     dados_acompanhamento = linha.find_elements_by_xpath('div[2]/div') # As informações e donloads estão na div2
                     lista_donwload_acp = [] # limpar a lista para cada acompanhamento
                     posicao_anexo_div = 0 # posiçao da div que estará os anexos
                     # Se tiver descrição nos downloads, pegar as decriçoes, elas ficam armazenadas na classe 'text-upper texto-movimento'
                     descricao_acompanhamento = ""
                     # Se a posição do anexo é 0, então esse anexo não tem descrição
                     # Se é diferente de 0, então existe descrição de anexos, por exemplo se é 2, então as duas divis acima é descrição
                     wait.until(EC.presence_of_element_located((By.CLASS_NAME,'text-muted')))
                     hora_teste = linha.find_elements_by_class_name('text-muted')  # Pegar a hora do acompanhamento


                     hora_acompanhamento = hora_teste[0].text #if len(hora_teste) > 0 and tentativas > 1 else "" # Pegar a hora do acompanhamento nas movimentações
                     data_atual = data_acompanhamento+' '+hora_acompanhamento # juntar com a hora que esta na parte superior dos acompaanhamentos
                     data_atual = Tools.treat_date(data_atual) # tratar a data

                     for divis in dados_acompanhamento: # Procurar a div que está os anexos a serem baixados!
                         if divis.get_attribute('class') == 'anexos': # Se achar a div que esta com os anexos então para

                             break

                         descricao_acompanhamento+= divis.text # enquanto não achar o anexo pega as descrições

                         posicao_anexo_div+=1
                     segundo_grau = self.verifica_segundo_grau(keyword_segundograu, descricao_acompanhamento)
                     # Caminho para fazer os donwloads, esse caminho é para pegar o elemento na função atualizado!!!
                     # caminho = '//*[@id="divTimeLine:divEventosTimeLine"]/div[{}]/div[2]/div[{}]'.format(i+1,posicao_anexo_div+1)
                     caminho = xpath_lista_movimentacoes + '[{}]/div[2]/div[{}]'.format(i+1,posicao_anexo_div+1)
                     tryin = 0
                     acp_pra_status = True
                     lista_donwload_acp_aux = []

                     list_name_urls_aux = []
                     lista_donwload_acp_aux = []
                     print("descricao_acompanhamento {}".format(descricao_acompanhamento))
                     acp_pra_status = self.fazer_download(caminho,list_name_urls_aux,lista_donwload_acp_aux,url_prov) # Retorna uma lista de donwloads e lista de urls

                     # raise
                     # pegar o id do primeiro donwload
                     # print(1437)
                     div_anexos = self.browser.find_element_by_xpath(caminho)  # Caminho onde estão os donwloads



                     nomes_span = str(div_anexos.find_elements_by_tag_name('span')[0].text)  # nomes dos dowloads que está na pagina(cada nome tem um id) estão na span
                     nomes_span = nomes_span.split("-")[0] # o id e separado por um traco

                     #print("Nomes_ acp numero: ", nomes_span)

                     lista_donwload_acp = lista_donwload_acp_aux
                     list_name_urls += list_name_urls_aux
                     # input('descricao_acompanhamento -> {} \n  acp_numero -> {} \n acp_data_cadastro -> {} \n acp_pra_status -> {} '.format(descricao_acompanhamento,nomes_span,data_atual,acp_pra_status))
                     lista_acompanhamentos.append((AcompanhamentoModel(acp_esp=descricao_acompanhamento,
                                                                     acp_numero=nomes_span,
                                                                     acp_data_cadastro=data_atual,
                                                                     acp_pra_status=acp_pra_status)
                                                                     ,lista_donwload_acp))

                     # Verificar se é audiencia e se não e um processo migrado do Projudi para o pje
                     if 'AUDIÊNCIA' in descricao_acompanhamento and not 'EVENTO PROJUDI:' in descricao_acompanhamento:  # Se for uma audiencia
                         print(";", end="")
                         dados_adiencia = self.separar_dados_audiencia(descricao_acompanhamento, Tools.treat_date(
                             data_acompanhamento))  # Tratar as audiencias
                         if dados_adiencia != False:  # Se retornar falso é porque não e uma audiencia, pode ser por exemplo: "PUBLICADO ATA DA AUDIÊNCIA EM 07/02/2019."
                             lista_audiencia.append(dados_adiencia)
                data_atual =""
                i+=1
                tamanho_movimentacoes = self.tam_movimentacoes()
                print(".",end="")
                tentativas = 0

            except Exception as erro:

                print("\n\n\n\t\t\t\tERRO\n\n\n")
                print("()",end="")

                tentativas+=1
                if tentativas>3:
                    self.log_error.insert_log("ERRO AO PEGAR LISTA DE ACOMPANHAMENTOS")
                    raise

                self.browser.get(url_prov) # atualiazar a apagina
                print("Erro nos acompanhamentos: ")

                wait.until(EC.invisibility_of_element((By.ID, '_viewRoot:status.start')))  # Esperar o documento aparecer
                # wait.until(EC.visibility_of_element_located((By.CLASS_NAME,'dropdown drop-menu mais-detalhes')))
                tamanho_movimentacoes = self.tam_movimentacoes() # atualizar o tamnho da tabela

                # raise

        # print("Tamanho lista URL : ", len(list_name_urls))

        return lista_acompanhamentos, lista_audiencia, list_name_urls, None,segundo_grau



        # SEPARA OS DADOS DA AUDIENCIA QUE ESTA NO ACOMPANHAMENTO

    def separar_dados_audiencia(self, audiencia, data2):  # descrição da audiência

        # una, conciliação, instrução, julgamente
        # CONCILIAÇÃO
        try:
            tipo = ""
            status = ""
            informacoes = audiencia.upper()
            # PEGAR O TIPO DA AUDIENCIA
            if 'UNA' in informacoes:
                tipo = 'UNA'
            elif 'CONCILIAÇÃO' in informacoes:
                tipo = 'CONCILIAÇÃO'
            elif 'INSTRUÇÃO' in informacoes:
                tipo = 'INSTRUÇÃO E JULGAMENTO' if 'JULGAMENTO' in informacoes else 'INSTRUÇÃO'

            # PEGAR O SATUS DA AUDIENCIA
            # TIPOS DE STATUS: 'DESIGNADA', 'REDESIGNADA', 'NEGATIVA', 'CANCELADA', 'NAO-REALIZADA', 'REALIZADA'
            #['REDESIGNADA', 'REALIZADA', 'CONCLUIDA', 'PENDENTE', 'NÃO REALIZADA']

            status = [ 'DESIGNADA', 'REDESIGNADA', 'NEGATIVA', 'CANCELADA', 'NÃO-REALIZADA', 'REALIZADA','NÃO REALIZADA', 'PENDENTE']
            for i in status:
                if i in informacoes:
                    status = i
                    break
            import re
            data_padrao = r'[0-9][0-9]/[0-9][0-9]/[0-9][0-9][0-9][0-9]'  # Padrão data
            hora_parao = r'[0-9][0-9]:[0-9][0-9]'
            data = re.findall(data_padrao, informacoes)  # Retorna um vetor com as datas encontradas na string

            if len(data) > 0:  # Se conter a data da audiencia no acompanhamento

                data = data[0]  # Pegar a data, já que existe
                hora = re.findall(hora_parao, informacoes)
                if len(hora)>0:
                    data += ' ' + re.findall(hora_parao, informacoes)[0]  # Pegar as horas
                data = Tools.treat_date(data)  # Tratar tada
            else:
                data = None


            # print('tipo: ', tipo, 'status: ', status, 'data: ', data)
            if tipo == "" or status == "":
                return False
            return (tipo, status, data, None, data2)
        except:
            print("\n\n\n\t\t\t\tERRO\n\n\n")

            return False

            # pass

    # FRAGIMENTAR DADOS DO PROCESSO
    def fragimentar_dados_dos_processo(self, dados_do_prosseco, dict_plp_2grau=None):

        print(dados_do_prosseco, "\n tam:",len(dados_do_prosseco))

        prc_numero, prc_id, prc_estado, plp_status, cadastro, \
        plp_codigo, plp_data_update, plp_id, plp_numero, plp_localizado = dados_do_prosseco[:-1]
        t0 = time.time()
        list_2_grau = dict_plp_2grau[prc_id] if dict_plp_2grau is not None else None
        list_plp_2_grau = []
        # sleep(60*60)
        return prc_numero, prc_id, prc_estado, plp_status, cadastro, \
               plp_codigo, plp_data_update, plp_id, plp_numero, \
               plp_localizado, t0, list_2_grau, list_plp_2_grau

    # VERIFICA SE O NAVEGADOR ESTÁ ABERTO
    # def verificar_se_o_navegador_esta_aberto(self):
    #     try:
    #
    #     except:
    #         self.log_error.insert_log('navegador fechou!')
    #         return False
    #     return True

    # EXIBIÇÃO DE INFORMAÇÕES PREVIAS E TRATAMENTO DO PRC_NUMERO
    def print_info_previo_e_trata_prc_numero(self, prc_numero, prc_id, plp_id, i_n):
        prc_numero = re.sub('[^0-9]', '', prc_numero)
        self.log_error.insert_title(prc_numero)
        print("\t{}ª: Coleta de dados do processo: {}".format(i_n, prc_numero).upper())
        print("\tPRC_ID : {}".format(prc_id).upper())
        print("\tPLP_ID : {}".format(plp_id).upper())
        return prc_numero

    # COLETA DO NUMERO DmO PROCESSO DO 2 GRAU E CRIAR O PLP COM HAJA NO 2º GRAU!
    def validar_bool_2_grau(self, list_2_grau, bool_2_grau_numero, prc_numero, prc_id):
        list_plp_2_grau = []
        try:
            if len(list_2_grau) == 0 and  bool_2_grau_numero:
                list_plp_2_grau = [
                    ProcessoPlataformaModel(plp_prc_id=prc_id, plp_plt_id=5,
                                            plp_numero=prc_numero, plp_grau=2, plp_processo_origem=prc_numero)

                ]
        except:
            list_plp_2_grau = []
            self.log_error.insert_log('coleta dos numeros do processo do 2 grau!'.upper())
            print("\n\n\n\t\t\t\tERRO\n\n\n")

        return list_plp_2_grau

    def recuperar_pag_envolvidos(self,numero_processo):

        if(len(self.browser.window_handles) == 2 ):# A pagina das movimentações estão abertas
            self.browser.switch_to_window(self.browser.window_handles[-1]) # Ecolhe a ultima pagina
            self.browser.close() # Fecha a pagina do processo
            self.browser.switch_to_window(self.browser.window_handles[0])  # Ecolhe a primeira aba
            self.buscar_processo_plataforma(numero_processo)
        else: # Navegador esta fechado ou so tem uma aberta
            self.browser.quit()
            loguin = self.realizar_loguin()
            i = 0
            while not loguin and i < 3:
                try:
                    self.browser.quit()
                except:
                    print("\n\n\n\t\t\t\tERRO\n\n\n")

                    pass
                i+=1
                loguin = self.realizar_loguin()

            self.buscar_processo_plataforma(numero_processo)

    # PEGA OS ENVOLVIDOS E RETORNA UMA LISTA COM AS PARTES E OS ADVOGADOS/JUIZ
    def envolvidos(self, prc_num = None):
       wait = WebDriverWait(self.browser, 10)
       qtd_erro = 0
       list_partes =[]
       list_advogs = []
       while qtd_erro < 2:
            try:

                if(len(self.browser.window_handles) > 2):
                    self.browser.switch_to_window(self.browser.window_handles[-1])
                    self.browser.close()
                    self.browser.switch_to_window(self.browser.window_handles[-1])

                titulo = self.browser.find_elements_by_class_name("titulo-topo") # Onde será clilcado para abrir
                titulo[0].click()
                wait.until(EC.visibility_of_element_located((By.ID, 'poloAtivo')))
                wait.until(EC.visibility_of_element_located((By.ID, 'poloPassivo')))
                list_partes1, list_advogs1 = self.get_informacoes_partes('poloAtivo')
                list_partes, list_advogs = self.get_informacoes_partes('poloPassivo')
                list_partes += list_partes1
                list_advogs += list_advogs1
                break

            except Exception as Erro:
                self.recuperar_pag_envolvidos(numero_processo=prc_num) # Recarega a pagina
                qtd_erro +=1
                print(Erro)
                print("\n\n\n\t\t\t\tERRO\n\n\n")

                list_partes = []
                list_advogs = []
                self.log_error.insert_log("AO PERGAR AS PARTES : "+str(Erro))
                raise


       return list_partes,list_advogs

    # VAlIDANDOS SE NUMERO DO PROCESSO CONTIDO NA PLATAFORMA E O MESMO CONTIDO NO SITE
    def validar_numero_plataforma(self, prc_numero):
        # try:
            self.browser.switch_to_window(self.browser.window_handles[-1]) # Status está na pagina de busca
            wait = WebDriverWait(self.browser, 5)
            wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="navbar"]/ul/li/a[1]')))
            numero_no_site = self.browser.find_element_by_xpath('//*[@id="navbar"]/ul/li/a[1]').text
            numero_no_site = re.sub('[^0-9]', '', numero_no_site)
            prc_numero = re.sub('[^0-9]', '', prc_numero)
            print("numero_no_site",numero_no_site)
            print("prc_numero",prc_numero)
            return prc_numero not in numero_no_site
        # except:
        #     # a=input("Erro validar_numero_plataforma")
        #     # raise
        #     return True

    # CRIANDO OBJETOS E INSERINDO NO BANCO DE DADOS
    def construct_list_obj_insert_bd(self, process_platform, list_name_urls=[], list_partes=[], list_advogs=[], list_aud=[],
                                     list_acp_pra=[], plp_id=None, list_plp_2_grau=[]):

        # print("Tamanho lista url construct: ", len(list_name_urls))
        list_objects_process = [
            (process_platform, list_partes, list_advogs, list_aud, list_acp_pra, plp_id, list_plp_2_grau)]

        # for i in list_acp_pra:
        #     print("len ->",len(i[-1]))
        # print('process_platform ')
        # for key,value in process_platform.__dict__.items():
        #     if value  is not  None:
        #         print(f"{key} = {value}")
        #
        # print(' list_partes')
        # for i,j in list_partes:
        #     print(f"Polo {j}")
        #     for key, value in i.__dict__.items():
        #         if value is not None:
        #             print(f"{key} = {value}")
        #     print('\n')
        #
        #
        # print(' list_advogs')
        # for i,j in list_advogs:
        #     print(f"Polo {j}")
        #     for key, value in i.__dict__.items():
        #         if value is not None:
        #             print(f"{key} = {value}")
        #     print('\n')
        #
        #
        # print(' list_acp_pra')
        # for i,j in list_acp_pra:
        #     for key, value in i.__dict__.items():
        #         if value is not None:
        #             print(f"{key} = {value}")
        #     print('\n')
        #
        # input('pode continuar')


        #INSERE A LISTA DE OBJETOS NO BANCO DE DADOS
        self.export_to_database(objects=list_objects_process, log=self.log_error, list_name_urls=list_name_urls,
                                platform=self.platform_name, state=self.state, root=self)

        self.log_error.insert_info('Procedimento finalizado!')
