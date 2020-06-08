from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

from Database.connDatabase import SQL
from socket import gethostbyname, create_connection
from Model.toolsModel import *
from Model.processoPlataformaModel import ProcessoPlataformaModel
from selenium import webdriver
from Model.processoArquivoModel import ProcessoArquivoModel
import smtplib
# Import the email modules we'll need
from email.mime.text import MIMEText

import codecs


class RootModel:
    # virtualização de atributo
    log_error = None
    user = None
    password = None

    def __init__(self, site, mode_execute, SQL_Long, platform_id, platform_name, estado='Default', grau=1):
        self.path_download_prov = os.path.abspath(
            '../../Downloads/' + estado + '/' + platform_name + '/' + str(grau) + 'Grau/Download' + str(hex(id(self))))
        Tools.new_path(str(self.path_download_prov))
        self.site = site
        self.grau = grau
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_experimental_option("prefs",
                                                    {"download.default_directory": r"" + str(self.path_download_prov),
                                                     "download.prompt_for_download": False,
                                                     "download.directory_upgrade": True,
                                                     "safebrowsing.enabled": False,
                                                     "safebrowsing_for_trusted_sources_enabled": False,
                                                     'download.extensions_to_open': 'msg',
                                                     "plugins.always_open_pdf_externally": True,
                                                     "profile.default_content_setting_values.automatic_downloads": 1,
                                                     "profile.content_settings.exceptions.automatic_downloads.*.setting": True
                                                     })
        # self.chrome_options.add_argument("--headless")

        self.visivel = mode_execute
        self.chrome_options.add_argument("--enable-features=NetworkService,NetworkServiceInProcess")
        self.chrome_options.add_argument("--ignore-certificate-errors")
        # ChromeDriver is just AWFUL because every version or two it breaks unless you pass cryptic arguments
        # AGRESSIVE: options.setPageLoadStrategy(PageLoadStrategy.NONE); #https://www.skptricks.com/2018/08/timed-out-receiving-message-from-renderer-selenium.html
        # self.chrome_options.add_argument("start-maximized")  # https://stackoverflow.com/a/26283818/1689770
        # self.chrome_options.add_argument("enable-automation")  # https://stackoverflow.com/a/43840128/1689770
        # self.chrome_options.add_argument("--headless")  ##### only if you are ACTUALLY running headless
        # self.chrome_options.add_argument("--no-sandbox")  # https://stackoverflow.com/a/50725918/1689770
        # self.chrome_options.add_argument("--disable-infobars")  ##https://stackoverflow.com/a/43840128/1689770
        # self.chrome_options.add_argument("--disable-dev-shm-usage")  # https://stackoverflow.com/a/50725918/1689770
        # self.chrome_options.add_argument(
        #     "--disable-browser-side-navigation")  # https://stackoverflow.com/a/49123152/1689770
        # self.chrome_options.add_argument(
        #     "--disable-gpu")  # https://stackoverflow.com/questions/51959986/how-to-solve-selenium-chromedriver-timed-out-receiving-message-from-renderer-exc

        # self.browser = None
        self.Access_AQL = SQL_Long
        self.platform_id = int(platform_id)
        self.platform_name = platform_name
        self.database = SQL(self.Access_AQL[0], self.Access_AQL[1], self.Access_AQL[2])
        self.montar_dicionario()
        self.linha_parou = 0
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

    # MAPEAMENTO DOS TRTS DO PJE TRABALHISTA

    # ABRE O NAVEGADOR PARA INICIAR AS BUSCAS
    def init_browser(self):

        print("INICIANDO BROWSER")
        local = str(os.path.abspath('../../WebDriver/chromedriver.exe'))

        self.browser = webdriver.Chrome(executable_path=local, options=self.chrome_options)
        self.browser.maximize_window()
        self.browser.get(self.site)

        # if self.visivel:
        # self.browser.set_window_position(-10000, 0)
        return True

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
        lista_de_processos = objects  # Lista de processos com todos os dados
        print("Tam list name export", len(list_name_urls))
        print("tam lista de objs:", len(objects))

        print("OBJETO INSERIR: ", objects[0][0].plp_grau)

        for processo in lista_de_processos:
            if processo[5] is None:
                print("Insert")
                self.database.insert_process(obj=processo, log=log, list_name_urls=list_name_urls, platform=platform,
                                             state=state, root=root)
            else:
                print("Update:")
                self.database.update_process(obj=processo, log=log, list_name_urls=list_name_urls,
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

            if (time.time() - temp_inicio) >= 240:  # 4minutos minutos
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

    def verificar_arquivado(self, descricao):

        palavras = ['BAIXA DEFINITIVA', 'ARQUIVADO', 'BAIXADO']
        for chaves in palavras:
            if chaves in descricao.upper():
                return 'ARQUIVADO'
        return 'ATIVO'

    # TRANSFERE OS ARQUIVOS BAIXADOS PARA O PATH
    def transfer_files(self, state, list_name_urls, plp_id, log):
        # CRIA PATH PARA TRANSFERÊNCIA DOS ANEXOS

        if len(list_name_urls) > 0:
            pasta_d = 'D:/titanium/Downloads/' + state + '/' + self.platform_name + '/' + str(plp_id)
            Tools.new_path(pasta_d)
            path_proc = os.path.abspath(pasta_d)
            # VERIFICA SE OS DOWNLOADS FORAM FINALIZADOS
            for new_name, old_name in list_name_urls:
                Tools.transfer_and_rename_files(old_name, new_name, self.path_download_prov, path_proc, log)
        self.clear_path_download()
        print('TRANSFERENCIA DOS ARQUIVOS FINALIZADA')

    # --------GENERALIZAÇÂO DO METODO DE VARREDURA
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

    def verifica(self, n_files, list_file_path, list_name_urls,
                 nome_donwload=None):  # retorna uma lista de processo arquivos

        lista_processoArquivo = []
        err_down = self.wait_download(n_files)

        if not err_down:  # not err_down: # se o download concluiu totalmente sem nehum erro

            arquivo = set(os.listdir(self.path_download_prov)).difference(
                set(list_file_path))  # difereça de dois conjuntos
            file_downloaded = arquivo.pop()  # pega o nome do arquivo que foi baixado
            arquivo = list(arquivo)

            if len(arquivo) > 1:  # Tem multiplos donwloads
                for i in range(0, len(arquivo), 1):
                    nome = Tools.convert_base(str(datetime.now()))

                    list_name_urls.append((nome, arquivo[i]))
                    nome = nome + '.' + arquivo[i].split('.')[-1]
                    lista_processoArquivo.append(
                        ProcessoArquivoModel(pra_nome=nome, pra_descricao=arquivo[i], pra_erro=0))

                print("multiplos")
                self.log_error.insert_log("Multiplos donwloads processo, verificar!!")

            nome = Tools.convert_base(str(datetime.now())) if nome_donwload == None else nome_donwload
            list_name_urls.append((nome,
                                   file_downloaded))  # Primeiro é o nome que quer renomear segundo o original, o primeiro não tem extensão
            nome = nome + '.' + file_downloaded.split('.')[-1]

            lista_processoArquivo.append(ProcessoArquivoModel(pra_nome=nome, pra_descricao=file_downloaded, pra_erro=0))
            return True, lista_processoArquivo

        else:

            return False, [ProcessoArquivoModel(pra_erro=1)]

    def separar_dados_audiencia(self, audiencia, data2):  # descrição da audiência

        # una, conciliação, instrução, julgamente
        # CONCILIAÇÃO
        try:
            tipo = ""
            status = ""
            informacoes = audiencia.upper()
            # PEGAR O TIPO DA AUDIENCIA
            lista_una = ['UNA', 'CONCILIAÇÃO, INSTRUÇÃO E JULGAMENTO', 'CONCILIAÇÃO-INSTRUÇÃO E JULGAMENTO',
                         'INSTRUÇÃO E JULGAMENTO', 'INSTRUÇÃO', 'JULGAMENTO', 'CONCILIAÇÃO', 'COMUM', 'INICIAL',
                         'MEDIAÇÃO']
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
            if type(list()) == type(
                    status):  # Se for uma lista quer dizer que não encontrou nehum status, provalvelmente não e uma audiencia
                status = ""
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
            return (tipo if tipo != "" else None, status, data, None, data2)
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
                                     list_aud=[],
                                     list_acp_pra=[], plp_id=None, list_plp_2_grau=[]):

        # for i in list_acp_pra:
        #     print(f"Date: {i[0].acp_data_cadastro} QtdDowload: {len(i[1])}\n")
        # input('Dowload correto?')
        list_objects_process = [
            (process_platform, list_partes, list_advogs, list_aud, list_acp_pra, plp_id, list_plp_2_grau)]

        aux = ''
        for i in process_platform.__dict__.items():
            aux += '\t\t\t{} = {}\n'.format(i[0], i[1])

        print("\n\n\t\t\t plp_localizado {} \t plp_id {}\n ".format(process_platform.plp_localizado, plp_id))

        # # INSERE A LISTA DE OBJETOS NO BANCO DE DADOS
        print("Tamanho lista õbj", len(list_objects_process))
        self.export_to_database(objects=list_objects_process, log=self.log_error, list_name_urls=list_name_urls,
                                platform=self.platform_name, state=self.state, root=self)

    # COLETA DO NUMERO DmO PROCESSO DO 2 GRAU E CRIAR O PLP COM HAJA NO 2º GRAU!
    def validar_bool_2_grau(self, bool_2_grau, bool_2_grau_numero, prc_numero, prc_id):
        return []

        # SOLICITA PERMIÇÃO DE ACESSO AOS ARQUIVOS

    def request_access(self):
        pass

    # PEGA OS ENVOLVIDOS E RETORNA UMA LISTA COM AS PARTES E OS ADVOGADOS/JUIZ

    def envolvidos(self):
        pass

    # PEGA DADOS DO PROCESSO
    def pegar_dados_do_prcesso(self):
        pass

    # PEGA ANDAMENTOS DO PROCESSO, AS AUDIÊNCIAS E REALIZA OS DOWNLOADS POR ACOMPANHAMENTO
    def acomp_down_aud(self, prc_id, ult_mov, bool_2_grau_numero, full=False):
        pass

    # MONTAR PROCESSO-PLATAFORMA
    def montar_processo_plataforma(self, prc_id, prc_numero, flag, plp_codigo):
        pass

    # VARIFICAR SE O GRAU ALTEROU
    def validar_grau(self):
        pass

    def find_process(self, **kwargs):
        pass

    def new_search(self, tempo):
        return

    def secret_of_justice(self):
        return

    # VAlIDANDOS SE NUMERO DO PROCESSO CONTIDO NA PLATAFORMA E O MESMO CONTIDO NO SITE
    def validar_numero_plataforma(self, prc_numero):
        return

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
        if var_bool:
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
                if i[1] is not None and i[0] == 'plp_localizado':
                    print(i[0], "\t", i[1])

            self.construct_list_obj_insert_bd(process_platform=process_platform, plp_id=plp_id)

            return True, plp_localizado

        # VERIFICA SE O PROCESSO ESTÁ EM SEGREDO DE JUSTIÇA
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
        print("plp_localizado_anterior -> ", plp_localizado)

        if prc_numero is not None:  # PESQUISA PELO NÚMERO DE PROCESSO DA TABELA PROCESSO
            if len(prc_numero) != 20:
                prc_numero = prc_numero.lstrip('0')
                prc_numero = prc_numero.rjust(20, '0')

        # RETORNA False SE TIVER ENCONTRADO PROCESSO E MANTEM O plp_localizado
        # RETORNA True SE NÃO TIVER ENCONTRADO PROCESSO E PASSA O plp_localizado PRA -1
        nao_achou, plp_localizado = self.check_process(n_proc=prc_numero, prc_id=prc_id, plp_id=plp_id,
                                                       plp_localizado=plp_localizado, plp_codigo=plp_codigo)

        if nao_achou:
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

    def replaces(self, text, args):
        for i in args:
            text = text.replace(i, '')
        return text

    def reiniciar_browser(self):
        self.browser.quit()

        # INICIA O BROWSER E A SESSÃO NA PLATAFORMA
        self.initializer(user=self.user, password=self.password)

    def imirmir_acompanhamentos(self, acomps):

        for acmp in acomps:
            print("\n\n##############################################################################")
            print("acp_esp: ", acmp[0].acp_esp)
            print("acp_data_cadastro: ", acmp[0].acp_data_cadastro)
            print("acp_prc_id: ", acmp[0].acp_prc_id)
            print("acp_numero: ", acmp[0].acp_numero)
            print("acp_tipo: ", acmp[0].acp_tipo)
            print("##############################################################################\n\n")

    def pega_data_atual(self):
        dia_atual = datetime.now()
        dia_atual = datetime.strftime(dia_atual, '%Y-%m-%d %H:%M:%S')
        return str(dia_atual)

    # ENVIA O RELATORIO DA VARREDUARA DO TRT PARA O MEU EMAIL
    def enviar_relatorio_email(self, painel_de_erros, img_erro=None):
        """Função para enviar email quando der erro na varredura."""
        print("Enviando erro para o  email!!!!!")
        try:
            # conexão com os servidores do google
            smtp_ssl_host = 'smtp.gmail.com'
            smtp_ssl_port = 465
            # username ou email para logar no servidor
            username = 'relatoriosestagio2020@gmail.com'
            password = 'relatorios123'

            from_addr = 'relatoriosestagio2020@gmail.com'
            to_addrs = ['suporte@i4legal.com.br']

            # a biblioteca email possuí vários templates
            # para diferentes formatos de mensagem
            # neste caso usaremos MIMEText para enviar
            # somente texto
            mensagem = painel_de_erros
            mensagem += "############################################<br>"
            mensagem += "# DATA DO FINAL DA VARREDURA:               #<br>"
            mensagem += "# " + self.pega_data_atual() + " #<br>"
            mensagem += "############################################<br>"
            msg = MIMEMultipart()
            # message = MIMEText(mensagem)
            msg['subject'] = 'RELATORIO VARREDURA'
            msg['from'] = from_addr
            msg['to'] = ', '.join(to_addrs)

            # Anexa a imagem
            # img_erro  # Repare que é diferente do nome do arquivo local!

            f = open(img_erro, 'rb')
            msgImg = MIMEImage(f.read(), name=img_erro)

            msg.attach(msgImg)

            msgText = MIMEText('<b>{}</b><br><img src="cid:{}"><br>'.format(mensagem, img_erro), 'html')
            msg.attach(msgText)

            # conectaremos de forma segura usando SSL
            server = smtplib.SMTP_SSL(smtp_ssl_host, smtp_ssl_port)
            # para interagir com um servidor externo precisaremos
            # fazer login nele
            server.login(username, password)
            server.sendmail(from_addr, to_addrs, msg.as_string())
            server.quit()
            print("EMAIL ENVIADO COM SUCESSO!")
        except Exception as ERRO:
            print('ERRO AO ENVIAR O EMAIL!')
            print("ERRO: ", ERRO)

    def pegar_site_tratado(self, site):
        """função para pegar o site de varredura e deixar so o domínio para verificar a conecção"""
        site = site.replace("https://", "")
        r = site.find(".br")
        r += 3
        return site[:r]

    # Verifica se esta conectado a internet e se é erro 404
    def conectadoInternet(self, site):
        """Fução para verificar se tem acesso a internet ou se é ERRO 404"""

        tentativas = 0
        site = self.pegar_site_tratado(site)
        print("Site: ", site)

        while tentativas < 3:
            try:
                host = gethostbyname(site)
                s = create_connection((host, 80), 2)
                return True
            except:
                tentativas += 1

        return False

    # SELECIONA PROCESSOS DO BANCO DE DADOS E PROCURA NA PLATAFORMA PARA UPDATE NO BANCO
    def search_process_to_update(self, user, password, row_database, dict_plp_2grau):
        # INICIA O BROWSER E A SESSÃO NA PLATAFORMA
        global prc_numero
        flag_inico = True  # flag para verificar se é o primeiro login
        self.user = user
        self.password = password

        tempo_busca = time.time()
        tentativas = 0
        numero_itecao = 0
        # VERIFICA CADA NUMERO DE PROCESSO DENTRO DA ESTRUTURA FORNECIDA
        i_n = 0
        numero_de_processo = len(row_database)
        while numero_itecao < numero_de_processo:

            print(row_database[numero_itecao])
            print(numero_itecao)
            print("Grau: ", self.grau)
            # FRAGMENTAR DADOS DO PROCESSO
            i_n += 1
            try:

                if flag_inico:  # se o site estiver indisponível irá cair na verificação se tem internet ou site fora do ar
                    self.initializer(user=user, password=password)
                    flag_inico = False

                t = time.time()
                prc_numero, prc_id, prc_estado, plp_status, cadastro, plp_codigo, plp_data_update, plp_id, plp_numero, plp_localizado, \
                t0, bool_2_grau_numero, list_plp_2_grau = self.fragimentar_dados_dos_processo(
                    dados_do_prosseco=row_database[numero_itecao],
                    dict_plp_2grau=dict_plp_2grau)
                # prc_numero ='06007867720208010070'
                # VERIFICA SE O NAVEGADOR ESTÁ ABERTO
                if not self.verificar_se_o_navegador_esta_aberto():
                    self.reiniciar_browser()
                    continue

                # VERIFICA SE A SESSÃO ESTÁ ATIVA
                if not self.check_session():
                    self.reiniciar_browser()
                    continue

                # EXIBIÇÃO DE INFORMAÇÕES PREVIAS E TRATAMENTO DO PRC_NUMERO
                prc_numero = self.print_info_previo_e_trata_prc_numero(prc_numero=prc_numero, prc_id=prc_id,
                                                                       plp_id=plp_id, i_n=i_n)
                # prc_numero = '56059173720198090012'
                # BUSCA PELO PROCESSO NA PLATAFORMA

                busca = self.busca_processo_na_plataforma(prc_numero=prc_numero,
                                                          tupla_processo=row_database[numero_itecao],
                                                          t0=t0, row_database=row_database)
                if busca:
                    self.new_search(tempo=t0)
                    numero_itecao += 1

                    continue
                # CAPTURA PLP_CODIGO

                aux = self.request_access()
                plp_codigo = aux if plp_codigo is None or aux is not None else plp_codigo

                # COLETA OS ACOMPANHAMENTOS DO PROCESSO

                list_aud, list_acp_pra, list_name_urls, \
                bool_2_grau, err1, not_refresh = self.acomp_down_aud(prc_id=prc_id, ult_mov=cadastro,
                                                                     bool_2_grau_numero=bool_2_grau_numero, full=False)

                # print("COLETA OS ACOMPANHAMENTOS DO PROCESSO ->>", time.time() - t)

                # VERIFICA SE HOUVE ERRO NA COLETA DOS ACOMPANHAMENTOS
                if not err1:  # Se tiver movimentações

                    list_partes = []
                    list_advogs = []

                    if (False or len(list_acp_pra) > 0):
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
                                                                       plp_codigo=plp_codigo,
                                                                       flag=len(list_acp_pra) > 0)
                    t = time.time()
                    print("plp_id->", plp_id)
                    # CRIANDO LISTA OBJETOS E INSERINDO NO BANCO DE DADOS
                    self.construct_list_obj_insert_bd(process_platform=process_platform, list_partes=list_partes,
                                                      list_advogs=list_advogs, list_aud=list_aud,
                                                      list_acp_pra=list_acp_pra,
                                                      plp_id=plp_id, list_plp_2_grau=list_plp_2_grau,
                                                      list_name_urls=list_name_urls
                                                      )

                    print("# CRIANDO LISTA OBJETOS E INSERINDO NO BANCO DE DADOS", time.time() - t)
                    # LIMPA A PASTA PARA RECEBER OS NOVOS DOWNLOADS
                    self.clear_path_download()
                    print('###Tempo total da coleta de dados do processo: {} SECS'.format(time.time() - t0).upper())
                    print('-' * 65)
                    numero_itecao += 1
                    tentativas = 0
                    continue

                # LIMPA A PASTA PARA RECEBER OS NOVOS DOWNLOADS
                self.clear_path_download()
                self.new_search(tempo=t0)
                print('###Tempo total da coleta de dados do processo: {} SECS'.format(time.time() - t0).upper())
                print('-' * 65)
                tentativas = 0
                numero_itecao += 1


            except Exception as Erro:
                # print(Erro)
                name_img = "erro.png"
                verificar = self.conectadoInternet(self.site)  # Verifica se a página de loguin está fora do ar

                while (not verificar):  # Eseperar o site voltar
                    verificar = self.conectadoInternet(self.site)  # Verifica se a página de loguin está fora do ar
                    print("INTERNET CAIU OU SITE FORA DO AR")

                if tentativas > 1:  # Tenta buscar duas vezes
                    tentativas = 0
                    numero_itecao += 1
                    try:
                        name_img = "ErroProcesso-" + prc_numero + " - " + self.platform_name + ".png"
                        self.browser.save_screenshot(name_img)
                    except:  # Quando o navegador está fechado ele não consegue tirar print
                        pass

                    mensagem = "ERRO NO PROCESSO: {} <br> ESTADO DO PROCESSO : {} <br>" \
                               "<br> PLATAFORMA {}<br>".format(row_database[numero_itecao][0],
                                                               row_database[numero_itecao][2], self.platform_name)
                    if len(str(Erro)) > 0:
                        mensagem += "\t ERRO: " + str(Erro)

                    self.enviar_relatorio_email(mensagem, name_img)
                    if (name_img != "erro.png"):
                        os.remove(name_img)

                self.browser.quit()
                self.initializer(user=user, password=password)

                tentativas += 1

        # VERIFICA SE O NAVEGADOR FECHOU, SENÃO O FECHA
        if self.browser is not None:
            self.browser.quit()

        return i_n
