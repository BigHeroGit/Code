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
    @property
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

    def pegar_respontavel(self,parte):
        # QUANDO  CLICADO NO BOTÃO DE MOSTRAR TODOS OS ADVOGADOS
        # classe tabelaLista -> existem 9, a primeira é toda a tabela das informações das parte ativa
        # a segunda é onde fica os advogados da parte ativa
        # A  terceira é onde fica todas as infrmações da parte passiva
        # A quinta é onde fica todas os adivogados da parte passiva
        # a classe linhaClara e linhaEscura são onde estão os nomes dos advogados e a oab
        self.abrir_lista_advogados(parte)
        partes = 1 if 'Ativa' in parte else 4  # pegar a qual tabela ira pegar as informações
        lista_partes = []

        tabela = self.browser.find_elements_by_class_name('tabelaLista') # Pegando todas as tabelas que são 9
        tabela_informacoes = tabela[partes] # Pegar a tabela de advogados

        # pegando todas as linhas da tabela que contém os advogados
        linhas_tabelas = tabela_informacoes.find_elements_by_class_name('linhaClara')
        linhas_tabelas+=tabela_informacoes.find_elements_by_class_name('linhaEscura')

        # Pegar as informações dos advogados
        for linhas in linhas_tabelas:

            nome = linhas.find_element_by_xpath('td[1]').text
            oab =  linhas.find_element_by_xpath('td[2]').text
            lista_partes.append((ResponsavelModel(rsp_nome=nome, rsp_oab=oab, rsp_tipo='Advogado(a)'), parte))

        return lista_partes


    def pegar_partes(self, parte):
        lista_partes = []
        tabela = self.browser.find_elements_by_class_name('tabelaLista')  # Pegando todas as tabelas que são 9, a primeira é

        pos = 0 if 'Ativa' in parte else 2  # Onde estão as tabelas com informações das partes
        tabela_informacoes = tabela[pos]

        linhas_tabelas = tabela_informacoes.find_elements_by_class_name('linhaClara')
        linhas_tabelas += tabela_informacoes.find_elements_by_class_name('linhaEscura')
        for linhas in linhas_tabelas:
            nome = linhas.find_element_by_xpath('td[2]').text  # pegando o nome
            cpf = linhas.find_element_by_xpath('td[4]').text
            cpf = re.sub('[^0-9]', '', cpf)
            lista_partes.append((ParteModel(prt_cpf_cnpj=cpf if len(cpf)>0 else None, prt_nome=nome), parte))


        return lista_partes


    # PEGA OS ENVOLVIDOS E RETORNA UMA LISTA COM AS PARTES E OS ADVOGADOS/JUIZ
    @property
    def envolvidos(self):

        list_partes = []
        list_advogs = []
        list_partes += self.pegar_partes('Ativa')
        list_partes += self.pegar_partes('Passiva')
        list_advogs += self.pegar_respontavel('Ativa')
        list_advogs += self.pegar_respontavel('Passiva')



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
        linhas_donwload = linha.find_elements_by_xpath('td/span[2]/div/div/table/tbody/tr') # Ir para o local onde está os donwloads
        list_name_urls_aux = []

        for linhas in linhas_donwload: # Se tiver mais de um donwload pegar a lista e varrer todos

            downlaods = linhas.find_elements_by_tag_name('a') # Pegar os donwloads que estão com a tag 'a'

            for baixar in downlaods: # fazer o donwnload em si

                nome_arquivos = os.listdir(self.path_download_prov)  # Pegar a quantidade de arquivos antes do download
                link = baixar.get_attribute('href') # Pegar o link do donwload

                self.browser.execute_script('''window.open("{}","_blank");'''.format(link))  # Abrir nova aba,  e ela faz donwload automaticamente
                nome_donwload = link.split('=')[-1] # Pegar o id do arquivo que está no final da url
                status, processoAqruivo = self.verifica(len(nome_arquivos), nome_arquivos, list_name_urls_aux,nome_donwload)
                list_name_urls += list_name_urls_aux
                list_file_name += processoAqruivo

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

        for linha in linhas_tabela:

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
