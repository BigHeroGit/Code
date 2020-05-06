from Database.connDatabase import SQL
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from Model.toolsModel import *
from Model.processoPlataformaModel import ProcessoPlataformaModel
from selenium import  webdriver
from Model.processoArquivoModel import ProcessoArquivoModel

import codecs


class RootModel:

    # virtualização de atributo
    log_error=None
    user = None
    password = None

    def __init__(self, site, mode_execute, SQL_Long, platform_id, platform_name, estado='Default', grau=1):
        self.path_download_prov = os.path.abspath('../../Downloads/' + estado + '/' + platform_name + '/' +str(grau)+'Grau/Download' + str(hex(id(self))))
        Tools.new_path(str(self.path_download_prov))
        self.site = site
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_experimental_option("prefs",
                                                    {"download.default_directory": r"" + str(self.path_download_prov),
                                                     "download.prompt_for_download": False,
                                                     "download.directory_upgrade": True,
                                                     "safebrowsing.enabled": False,
                                                     "profile.default_content_settings.popups": 0,
                                                     "profile.content_settings.pattern_pairs.*.multiple-automatic-downloads":1,
                                                     "safebrowsing_for_trusted_sources_enabled": False,
                                                     "safebrowsing.enabled": False,
                                                     'profile.default_content_settings.multiple-automatic-downloads': 1,
                                                     "safebrowsing_for_trusted_sources_enabled": False,
                                                     'download.extensions_to_open': 'msg',
                                                     "profile.default_content_setting_values.automatic_downloads": 1,
                                                     "plugins.always_open_pdf_externally": True,
                                                     "profile.content_settings.exceptions.automatic_downloads.*.setting":True})


        self.visivel = mode_execute
        self.chrome_options.add_argument("--enable-features=NetworkService,NetworkServiceInProcess")
        self.chrome_options.add_argument("--ignore-certificate-errors")
        self.chrome_options.add_argument("--disable-notifications")

        # self.browser = None
        self.Access_AQL = SQL_Long
        self.platform_id = int(platform_id)
        self.platform_name = platform_name
        self.database = SQL(self.Access_AQL[0], self.Access_AQL[1], self.Access_AQL[2])
        self.montar_dicionario()
        # montar dicionario com o nome de todas as cidades do brasil para pegar a comarca

    def montar_dicionario(self):
        lista = open('dados_cidade.txt', 'r')
        lista = lista.readlines()
        self.dicionario_cidade = dict()
        for i in lista:
            dado = i.split(',')
            chave = dado[-1].replace("\n", "").replace("'", "").replace(" ", "")
            dado = dado[0].replace("\n", "")
            dado = dado[:-1].replace("''", "'")
            dado = dado.replace('-', ' ')
            dado = Tools.remove_accents(dado).upper()
            # print("Estado: ", chave, " Cidade:", dado)

            if chave in self.dicionario_cidade.keys():
                self.dicionario_cidade[chave].append(dado)
            else:
                self.dicionario_cidade[chave] = []
                self.dicionario_cidade[chave].append(dado)

    def separar_comarca(self, comarca):


        comarca = comarca.upper()
        lista = self.dicionario_cidade[self.state.upper().replace(" ", "")]

        for i in lista:
            if i in comarca:
                return i

        chaves = ['COMARCA DE', 'CÍVEL DE', 'CIVEL DE', 'CENTRAL DE', 'ESPECIAL DE', 'CONSUMO DE', 'CÍVEL - ', 'CÍVEL-',
                  'CIVEL-', 'CÍVEL DE',
                  'CENTRAL DE', 'VARA DE', 'MULHER DE', 'CRIMINAL DE', 'CRIMINAL DO', '- '
                  ]

        for i in chaves:
            if i in comarca:  # Verifica se exite a chave, se existe pega tud para frente
                return comarca.split(i)[-1]

        # se não conseguiu achar

        return False
    def __del__(self):
        print(self.path_download_prov)
        Tools.delete_path(self.path_download_prov)
        self.database.__del__()
        # Tools.delete_path('../../WebDriver/' +self.id_chrome)

    #MAPEAMENTO DOS TRTS DO PJE TRABALHISTA


    # ABRE O NAVEGADOR PARA INICIAR AS BUSCAS
    def init_browser(self):
        try:
            print("INICIANDO BROWSER")
            local = str( os.path.abspath('../../WebDriver/chromedriver.exe'))
            self.browser = webdriver.Chrome(local, options=self.chrome_options)
            self.browser.maximize_window()
            self.browser.get(self.site)

            #if self.visivel:
                #self.browser.set_window_position(-10000, 0)
            return True
        except:
            raise
            # print("Ruim")
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

        print("Tam list name export", len(list_name_urls))
        for obj in objects:
            if obj[5] is None:
                print("Insert")
                self.database.insert_process(obj=obj, log=log, list_name_urls=list_name_urls,
                                        platform=platform, state=state, root=root)
            else:
                print("Update:")
                self.database.update_process(obj=obj, log=log, list_name_urls=list_name_urls,
                                        platform=platform, state=state, root=root)

    def donwloadAcompanhamento(self, nome):

        nome = nome + '.html'  # nome do arquivo que será salvo
        # print('donwload html : ', name)
        self.browser.switch_to_window(self.browser.window_handles[-1])  # vai para última aba
        completeName = os.path.join(self.path_download_prov, nome)
        file_object = codecs.open(completeName, "w", "utf-8")
        html = self.browser.page_source
        file_object.write(html)
        self.browser.close()
        self.browser.switch_to_window(self.browser.window_handles[-1])  # vai para última aba

        return nome

    # ESPERAR O DONWLOAD TERMINAR
    def wait_download(self, n_files):
        temp_inicio = time.time()
        baixando = True


        # try:
        temp_inicio = time.time()
        baixando = True


        while baixando:

            if (time.time() - temp_inicio) >= 60:  # passou  um minto
                return True

            dir = os.listdir(self.path_download_prov)
            if n_files < len(dir):  # se tem mais um donwload

                for j in range(0, len(dir)):
                    if dir[j].endswith('.crdownload') or dir[j].endswith('.tmp'):
                        baixando = True
                        break

                    else:
                        baixando = False

        return False
        # except:
        #     return True

    def verificar_arquivado(self,descricao):

        palavras = ['BAIXA DEFINITIVA', 'ARQUIVADO', 'BAIXADO']
        for chaves in palavras:
            if chaves in descricao.upper():
                return  'ARQUIVADO'
        return 'ATIVO'

    # TRANSFERE OS ARQUIVOS BAIXADOS PARA O PATH
    def transfer_files(self, state, list_name_urls, plp_id, log):
        # CRIA PATH PARA TRANSFERÊNCIA DOS ANEXOS
        # print("\n\n\n\t\tlen(list_name_urls) {}".format(len(list_name_urls)))
        if len(list_name_urls) > 0:
            pasta_d='D:/titanium/Downloads/' + state + '/' + self.platform_name + '/' + str(plp_id)
            # pasta_d='../../../titanium/Downloads/' + state + '/' + self.platform_name + '/' + str(plp_id)
            Tools.new_path(pasta_d)
            path_proc = os.path.abspath(pasta_d)
            # VERIFICA SE OS DOWNLOADS FORAM FINALIZADOS
            for new_name, old_name in list_name_urls:
                Tools.transfer_and_rename_files(old_name, new_name, self.path_download_prov, path_proc, log)
        self.clear_path_download()
        print('\t- Transferência dos arquivos finalizada'.upper())
        # input("\n\n\n\t (231)")

    #--------GENERALIZAÇÂO DO METODO DE VARREDURA
    # VALIDA A INICIALIZAÇÃO DA VARREDURA NA PLATAFORMA
    def initializer(self, user, password):
        while True:
            # INICIALIZA BROWSER
            if self.init_browser():
                # LOGIN NA PLATAFORMA
                # input('pode continuar')
                if self.login(user, password):
                    break
            if self.browser is not None:
                self.browser.quit()

        # SEPARA OS DADOS DA AUDIENCIA QUE ESTA NO ACOMPANHAMENTO

    def verifica(self, n_files, list_file_path, list_name_urls,nome_donwload=None):  # retorna uma lista de processo arquivos

        lista_processoArquivo = []
        err_down = self.wait_download(n_files)

        if not err_down:  # not err_down: # se o download concluiu totalmente sem nehum erro

            arquivo = set(os.listdir(self.path_download_prov)).difference(set(list_file_path))  # difereça de dois conjuntos
            file_downloaded = arquivo.pop()  # pega o nome do arquivo que foi baixado
            arquivo = list(arquivo)

            if len(arquivo) > 1:  # Tem multiplos donwloads
                for i in range(0, len(arquivo), 1):

                    nome = Tools.convert_base(str(datetime.now()))

                    list_name_urls.append((nome, arquivo[i]))
                    nome = nome + '.' + arquivo[i].split('.')[-1]
                    lista_processoArquivo.append(ProcessoArquivoModel(pra_nome=nome, pra_descricao=arquivo[i], pra_erro=0))

                print("multiplos")
                self.log_error.insert_log("Multiplos donwloads processo, verificar!!")

            nome = Tools.convert_base(str(datetime.now())) if nome_donwload == None else nome_donwload
            list_name_urls.append((nome,file_downloaded))  # Primeiro é o nome que quer renomear segundo o original, o primeiro não tem extensão
            nome = nome + '.' + file_downloaded.split('.')[-1]

            lista_processoArquivo.append(ProcessoArquivoModel(pra_nome=nome, pra_descricao=file_downloaded, pra_erro=0))
            return True, lista_processoArquivo

        else:
            i = input("Deu erro ")

            return False, [ProcessoArquivoModel(pra_erro=1)]

    def separar_dados_audiencia(self, audiencia, data2):  # descrição da audiência

        # una, conciliação, instrução, julgamente
        # CONCILIAÇÃO
        try:
            tipo = ""
            status = ""
            informacoes = audiencia.upper()
            # PEGAR O TIPO DA AUDIENCIA
            lista_una = ['UNA','CONCILIAÇÃO, INSTRUÇÃO E JULGAMENTO', 'CONCILIAÇÃO-INSTRUÇÃO E JULGAMENTO',
                         'INSTRUÇÃO E JULGAMENTO','INSTRUÇÃO','JULGAMENTO','CONCILIAÇÃO','INICIAL']
            for i in lista_una:
                if i in informacoes:
                    tipo = i
                    break

            # PEGAR O SATUS DA AUDIENCIA
            # TIPOS DE STATUS: 'DESIGNADA', 'REDESIGNADA', 'NEGATIVA', 'CANCELADA', 'NAO-REALIZADA', 'REALIZADA'
            # ['REDESIGNADA', 'REALIZADA', 'CONCLUIDA', 'PENDENTE', 'NÃO REALIZADA']

            status = ['DESIGNADA', 'DESIGNADO', 'REDESIGNADA', 'NEGATIVA', 'CANCELADA', 'NÃO-REALIZADA', 'REALIZADA',
                      'NÃO REALIZADA', 'PENDENTE']
            for i in status:
                if i in informacoes:
                    status = i
                    break
            if type(list()) == type(status): # Se for uma lista quer dizer que não encontrou nehum status, provalvelmente não e uma audiencia
                status=""
            import re
            data_padrao = r'[0-9][0-9]/[0-9][0-9]/[0-9][0-9][0-9][0-9]'  # Padrão data
            hora_parao = r'[0-9][0-9]:[0-9][0-9]'
            data = re.findall(data_padrao, informacoes)  # Retorna um vetor com as datas encontradas na string

            if len(data) > 0:  # Se conter a data da audiencia no acompanhamento

                data = data[0]  # Pegar a data, já que existe
                hora = re.findall(hora_parao, informacoes)
                if len(hora) > 0:
                    data += ' ' + re.findall(hora_parao, informacoes)[0]  # Pegar as horas
                data = Tools.treat_date(data)  # Tratar tada
            else:
                data = None
            print("Tipo:", tipo, "Status", status)
            print("Desc: ", informacoes)
            # print('tipo: ', tipo, 'status: ', status, 'data: ', data)
            if (tipo == "" or status == "") and status != "REALIZADA":
                return False
            return (tipo if tipo!="" else None, status, data, None, data2)
        except:
            raise
            return False

            # pass

    def login(self, user, password):
        pass

    # VERIFICA SE A SESSÃO DO USUÁRIO ESTÁ ATIVA
    def check_session(self):
        return True

    # VERIFICA SE O NAVEGADOR ESTÁ ABERTO
    def verificar_se_o_navegador_esta_aberto(self):
        try:
           self.browser.find_element_by_tag_name('body')
        except NoSuchWindowException:
            self.browser.quit()
            return False

        return True

    # FRAGIMENTAR DADOS DO PROCESSO
    def fragimentar_dados_dos_processo(self, dados_do_prosseco, dict_plp_2grau=None):
        prc_numero, prc_id, prc_estado, plp_status, cadastro, \
        plp_codigo, plp_data_update, plp_id, plp_numero, plp_localizado = dados_do_prosseco[:-1]
        t0 = time.time()
        bool_2_grau_numero = len(dict_plp_2grau[prc_id]) > 0 if dict_plp_2grau is not None else None
        list_plp_2_grau = []
        prc_numero = prc_numero if plp_numero is None else plp_numero

        return prc_numero, prc_id, prc_estado, plp_status, cadastro, \
               plp_codigo, plp_data_update, plp_id, plp_numero, \
               plp_localizado, t0, bool_2_grau_numero, list_plp_2_grau

    # EXIBIÇÃO DE INFORMAÇÕES PREVIAS E TRATAMENTO DO PRC_NUMERO
    def print_info_previo_e_trata_prc_numero(self, prc_numero, prc_id, plp_id, i_n):
        prc_numero = re.sub('[^0-9]', '', prc_numero)
        self.log_error.insert_title(prc_numero)
        print("{}ª: Coleta de dados do processo: <>{}<>".format(i_n, prc_numero).upper())
        print("\tPRC_ID : {}".format(prc_id).upper())
        print("\tPLP_ID : {}\n".format(plp_id).upper())
        # input('dejesa continuar')
        return prc_numero

    # EXIBIÇÃO DE INFORMAÇÕES DAS PARTES
    def print_if_parte(self, list_partes, list_advogs):
        for i in list_partes: print(
            " POLO:{} \t NOME:{} \t CPF_CNPJ:{}".format(i[-1], i[0].prt_nome, i[0].prt_cpf_cnpj))
        print('\n----')
        for i in list_advogs: print(" POLO:{} \t NOME:{} \t TIPO:{}".format(i[-1], i[0].rsp_nome, i[0].rsp_tipo))
        print('\n----')

    # CRIANDO OBJETOS E INSERINDO NO BANCO DE DADOS
    def construct_list_obj_insert_bd(self, process_platform, list_name_urls=[], list_partes=[], list_advogs=[],
                                     list_aud=[],list_acp_pra=[], plp_id=None, list_plp_2_grau=[]):

        print('\n\n\t\t\tlist_plp_2_grau -> ',len(list_plp_2_grau))
        # for i in list_acp_pra:
        #     print(f"Date: {i[0].acp_data_cadastro} QtdDowload: {len(i[1])}\n")
        # input('Dowload correto?')
        list_objects_process = [
            (process_platform, list_partes, list_advogs, list_aud, list_acp_pra, plp_id, list_plp_2_grau)]

        aux = ''
        for i in process_platform.__dict__.items():
            aux += '\t\t\t{} = {}\n'.format(i[0], i[1])

        print("\n\n\t\t\t plp_localizado {} \t plp_id {}\n ".format(process_platform.plp_localizado,plp_id))

        # # INSERE A LISTA DE OBJETOS NO BANCO DE DADOS
        self.export_to_database(objects=list_objects_process, log=self.log_error, list_name_urls=list_name_urls,
                                platform=self.platform_name, state=self.state, root=self)
        # input('Dowload correto?')
        self.log_error.insert_info('Procedimento finalizado!')

    # COLETA DO NUMERO DmO PROCESSO DO 2 GRAU E CRIAR O PLP COM HAJA NO 2º GRAU!
    def validar_bool_2_grau(self, bool_2_grau, bool_2_grau_numero, prc_numero, prc_id):
        return []

    # SOLICITA PERMIÇÃO DE ACESSO AOS ARQUIVOS
    def request_access(self):
        pass

     # PEGA OS ENVOLVIDOS E RETORNA UMA LISTA COM AS PARTES E OS ADVOGADOS/JUIZ
    @property
    def envolvidos(self):
        pass

    # PEGA DADOS DO PROCESSO
    def pegar_dados_do_prcesso(self):
        pass

    # PEGA ANDAMENTOS DO PROCESSO, AS AUDIÊNCIAS E REALIZA OS DOWNLOADS POR ACOMPANHAMENTO
    def acomp_down_aud(self, prc_id, ult_mov, bool_2_grau_numero,full = False):
        pass

    # MONTAR PROCESSO-PLATAFORMA
    def montar_processo_plataforma(self, prc_id, prc_numero, flag, plp_codigo):
        pass

    # VARIFICAR SE O GRAU ALTEROU
    def validar_grau(self):
        pass

    def find_process(self, **kwargs):
        pass

    def new_search(self,tempo) :
        pass

    def secret_of_justice(self):
        pass

    # VAlIDANDOS SE NUMERO DO PROCESSO CONTIDO NA PLATAFORMA E O MESMO CONTIDO NO SITE
    def validar_numero_plataforma(self, prc_numero):
        pass


    # VERIFICA CADA NÚMERO DE PROCESSO RETORNADO DO BANCO DE DADOS NA PLATAFORMA
    def check_process(self, n_proc, prc_id, plp_id, plp_localizado, plp_codigo):
    # RETORNA False SE TIVER ENCONTRADO PROCESSO
    # RETORNA True SE FOR SEGREDO DE JUSTIÇA OU NÃO TIVER ENCONTRADO OU DER ALGUM ERRO

        # BUSCA O PROCESSO NA PLATAFORMA
        #  find_process RETORNA TRUE SE TIVER ENCONTRADO O PROCESSO
        var_bool = self.find_process(n_proc, plp_codigo)

        # ACONTECEU ALGUM ERRO NA BUSCA
        if var_bool is None:
            self.browser.refresh()
            return True, -1

        # PROCESSO NÃO ENCONTRADO
        if not var_bool:
            print('Processo não encontrado!\nplp_localizado{}'.format(plp_localizado))
            if plp_localizado is None:
                plp_localizado = 2
            elif 1 < plp_localizado < 5:
                plp_localizado += 1
            elif plp_localizado == 1:
                plp_localizado = 1
            else:
                plp_localizado = 0

            process_platform = ProcessoPlataformaModel(plp_prc_id=prc_id, plp_plt_id=self.platform_id,
                                                       plp_numero=n_proc, plp_segredo=False, plp_grau=self.grau,

                                                       plp_localizado=plp_localizado)

            for i in process_platform.__dict__.items():
                if i[1] is not None and i[0]=='plp_localizado':
                    print(i[0], "\t", i[1])

            self.construct_list_obj_insert_bd(process_platform=process_platform, plp_id=plp_id)

            self.reiniciar_browser
            return True, plp_localizado

        # VERIFICA SE O PROCESSO ESTÁ EM SEGREDO DE JUSTIÇA
        # input('Processo em segredo de justiça!')
        if self.secret_of_justice():
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
    def busca_processo_na_plataforma(self, prc_numero, tupla_processo, t0, row_database):
        prc_id, prc_estado, plp_status, cadastro, plp_codigo, \
        plp_data_update, plp_id, plp_numero, plp_localizado = tupla_processo[1:-1]
        print("plp_localizado_anterior -> {}".format(plp_localizado))

        if prc_numero is not None:  # PESQUISA PELO NÚMERO DE PROCESSO DA TABELA PROCESSO
            if len(prc_numero) != 20:
                prc_numero = prc_numero.lstrip('0')
                prc_numero = prc_numero.rjust(20, '0')

        # RETORNA False SE TIVER ENCONTRADO PROCESSO E MANTEM O plp_localizado
        # RETORNA True SE NÃO TIVER ENCONTRADO PROCESSO E PASSA O plp_localizado PRA -1
        # input('check??')

        nao_achou, plp_localizado = self.check_process(n_proc=prc_numero, prc_id=prc_id, plp_id=plp_id,
                                                       plp_localizado=plp_localizado, plp_codigo=plp_codigo)


        if nao_achou:
            print(' plp_localizado == {}'.format(plp_localizado))
            if plp_localizado == -1:
                aux_i_prc = tupla_processo
                aux_i_prc[9] = plp_localizado

                if aux_i_prc not in row_database:
                    row_database.append(aux_i_prc)
                    print('### Processo foi reinserido novamente na lista de busca: {} SECS'.format(
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
                self.grau = 1
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

    def replaces(self,text,args):
        for i in args:
            text = text.replace(i,'')
        return text

    def reiniciar_browser(self):
        self.browser.quit()

        # INICIA O BROWSER E A SESSÃO NA PLATAFORMA
        self.initializer(user=self.user, password=self.password)

    # SELECIONA PROCESSOS DO BANCO DE DADOS E PROCURA NA PLATAFORMA PARA UPDATE NO BANCO
    def search_process_to_update(self, user, password, row_database, dict_plp_2grau):
        # INICIA O BROWSER E A SESSÃO NA PLATAFORMA
        self.user=user
        self.password=password
        self.initializer(user=user, password=password)

        # VERIFICA CADA NUMERO DE PROCESSO DENTRO DA ESTRUTURA FORNECIDA
        i_n = 0
        numero_de_processo = len(row_database)
        for i_proc in row_database:

            # FRAGMENTAR DADOS DO PROCESSO
            i_n += 1
            try:
                t = time.time()
                prc_numero, prc_id, prc_estado, plp_status, cadastro, plp_codigo, plp_data_update, plp_id, plp_numero, plp_localizado, \
                t0, bool_2_grau_numero, list_plp_2_grau = self.fragimentar_dados_dos_processo(dados_do_prosseco=i_proc,
                                                                                              dict_plp_2grau=dict_plp_2grau)

                # VERIFICA SE O NAVEGADOR ESTÁ ABERTO OU VERIFICA SE A SESSÃO ESTÁ ATIVA
                if not ( self.verificar_se_o_navegador_esta_aberto() or self.check_session() ):
                    self.reiniciar_browser()
                    continue
                #prc_numero = "00098400420178090134"
                # prc_id = '32014'
                # plp_id = None
                # cadastro = None
                # EXIBIÇÃO DE INFORMAÇÕES PREVIAS E TRATAMENTO DO PRC_NUMERO
                prc_numero = self.print_info_previo_e_trata_prc_numero(prc_numero=prc_numero, prc_id=prc_id,
                                                                       plp_id=plp_id, i_n=i_n)
                #prc_numero = '52943206120188090051'
                # BUSCA PELO PROCESSO NA PLATAFORMA
                busca = self.busca_processo_na_plataforma(prc_numero=prc_numero, tupla_processo=i_proc,
                                                     t0=t0, row_database=row_database)

                #input('kaio lindo')
                if busca:
                    # input('CAPTURA PLP_CODIGO')
                    self.new_search(tempo=t0)
                    continue
                # CAPTURA PLP_CODIGO

                aux = self.request_access()
                plp_codigo = aux if plp_codigo is None or aux is not None else plp_codigo


                # COLETA OS ACOMPANHAMENTOS DO PROCESSO
                t = time.time()

                list_aud, list_acp_pra, list_name_urls,\
                bool_2_grau, err1, not_refresh = self.acomp_down_aud(prc_id=prc_id, ult_mov=cadastro,
                                                                     bool_2_grau_numero=bool_2_grau_numero, full=self.flag)

                print("COLETA OS ACOMPANHAMENTOS DO PROCESSO ->>", time.time() - t)

                t = time.time()

                # VERIFICA SE HOUVE ERRO NA COLETA DOS ACOMPANHAMENTOS

                print(f"ERRO COLETA DE DOWLOAD? {err1}")
                if not err1:
                    list_partes = []
                    list_advogs = []

                    if(self.flag or len(list_acp_pra)):
                        # COLETA DO NUMERO DO PROCESSO DO 2 GRAU E CRIAR O PLP CASO HAJA NO 2º GRAU!
                        list_plp_2_grau = self.validar_bool_2_grau(bool_2_grau=bool_2_grau,
                                                                   bool_2_grau_numero=bool_2_grau_numero,
                                                                   prc_numero=prc_numero, prc_id=prc_id)

                        # VARIFICAR SE O GRAU ALTEROU
                        self.validar_grau()

                        # IDENTIFICA OS ENVOLVIDOS E RETORNA UMA LISTA COM AS PARTES, OS ADVOGADOS E O JUIZ


                        list_partes, list_advogs = self.envolvidos()

                        print("\n#IDENTIFICA OS ENVOLVIDOS E RETORNA UMA LISTA COM AS PARTES, OS ADVOGADOS E O JUIZ\n")

                        print("\n#IDENTIFICA OS ENVOLVIDOS E RETORNA UMA LISTA COM AS PARTES, OS ADVOGADOS E O JUIZ\n")

                        # EXIBIÇÃO DE INFORMAÇÕES DAS PARTES
                        self.print_if_parte(list_partes, list_advogs)


                    # CRIA O OBJETO PROCESSO-PLATAFORMA QUE SERÁ INSERIDO NO BANCO DE DADOS
                    process_platform = self.montar_processo_plataforma(prc_id=prc_id, prc_numero=prc_numero,
                                                                       plp_codigo=plp_codigo, flag=self.flag or len(list_acp_pra))

                    # CRIANDO LISTA OBJETOS E INSERINDO NO BANCO DE DADOS
                    self.construct_list_obj_insert_bd(process_platform=process_platform, list_partes=list_partes,
                                                       list_advogs=list_advogs, list_aud=list_aud,
                                                       list_acp_pra=list_acp_pra,
                                                       plp_id=plp_id, list_plp_2_grau=list_plp_2_grau,
                                                       list_name_urls=list_name_urls
                                                       )

                    print("# CRIANDO LISTA OBJETOS E INSERINDO NO BANCO DE DADOS",time.time() - t)
                    # LIMPA A PASTA PARA RECEBER OS NOVOS DOWNLOADS
                    self.clear_path_download()
                    print('###Tempo total da coleta de dados do processo: {} SECS'.format(time.time() - t0).upper())
                    print('-' * 65)
                    # input('CAPTURA PLP_CODIGO')
                    self.new_search(tempo=t0)
                    continue

                if not_refresh:
                    self.reiniciar_browser()
                aux_i_prc = [i for i in i_proc]
                row_database.append(aux_i_prc)


                # LIMPA A PASTA PARA RECEBER OS NOVOS DOWNLOADS
                self.clear_path_download()
                print('###Tempo total da coleta de dados do processo: {} SECS'.format(time.time() - t0).upper())
                print('-' * 65)


            except Exception as Erro:

                print(Erro)
                # raise

                aux_i_prc = [i for i in i_proc]
                row_database.append(aux_i_prc)
                print("ERRO INESPERADO NO PROCESSO {}".format(i_n))
                raise


            # input('dejejas continiar')
            # input('deseja continuar==============')
            self.new_search(tempo=t0)

        # VERIFICA SE O NAVEGADOR FECHOU, SENÃO O FECHA
        if self.browser is not None:
            self.browser.quit()

        return i_n
