
from Model.Civel.esajModel import *
#from pytesseract import  pytesseract
from Model.toolsModel import *
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
#from PIL import Image
import os
#import cv2
import re

class esajBahiaController(EsajModel):
    def __init__(self, site, mode_execute, access, platform_id, platform_name, flag, num_thread, grau='1Grau'):
        state = 'BA'
        link_consulta = "http://esaj.tjba.jus.br/cpopg/open.do"
        super().__init__(site, mode_execute, access, platform_id, platform_name, state, num_thread, link_consulta, flag,
                         grau)
    # ENCONTRAR O PROCESSO NA PLATAFORMA
    def find_process(self, prc_numero, plp_codigo=None):
        segredo = False
        try:
            if (plp_codigo != None):
                self.browser.get('https://consultasaj.tjam.jus.br/cpopg/show.do?processo.codigo=' + plp_codigo)
                # 'https://esaj.tjac.jus.br/cposg5/search.do?conversationId=&paginaConsulta=0&cbPesquisa=NUMPROC&numeroDigitoAnoUnificado=0708249-28.2019&foroNumeroUnificado=0001&dePesquisaNuUnificado=0708249-28.2019.8.01.0001&dePesquisaNuUnificado=UNIFICADO&dePesquisa=&tipoNuProcesso=UNIFICADO'
                #https://esaj.tjac.jus.br/cpopg/show.do?processo.codigo=020001N240000&processo.foro=2&uuidCaptcha=sajcaptcha_7a49d078c82245ffa5f5473be1475ade
                try:
                    if (self.browser.find_element_by_xpath(
                            '//*[@id="mensagemRetorno"]/li/text()') in '  Não foi possível obter os dados do processo. Por favor tente novamente mais tarde. '):
                        return False
                except:
                    return True
            else:
                self.browser.get(self.link_consulta)
                wait = WebDriverWait(self.browser, 10)
                wait.until(EC.visibility_of_element_located((By.ID, 'numeroDigitoAnoUnificado')))
                self.browser.find_element_by_xpath('//*[@id="numeroDigitoAnoUnificado"]').send_keys(prc_numero[:-7])
                self.browser.find_element_by_xpath('//*[@id="foroNumeroUnificado"]').send_keys(prc_numero[-4:])
                contar = 1
                while contar < 10:
                    contar+=1
                    text =self.recaptcha('//*[@id="defaultCaptchaImage"]')
                    # print("text->",text)
                    if text is None:
                        self.browser.find_element_by_xpath('//*[@id="captchaInfo"]/ul/li[2]').click()
                        continue
                    else:
                        self.browser.find_element_by_xpath('//*[@id="defaultCaptchaCampo"]').send_keys(text,Keys.RETURN)
                        try:
                            wait = WebDriverWait(self.browser, 2)
                            wait.until(EC.visibility_of_element_located((By.ID, 'spwTabelaMensagem')))
                            continue
                        except:
                            break
                try:

                    wait = WebDriverWait(self.browser, 3)
                    wait.until(EC.visibility_of_element_located((By.ID, 'mensagemRetorno')))
                    return False, False
                except:
                    pass

                try:
                    wait = WebDriverWait(self.browser, 3)
                    wait.until(EC.visibility_of_element_located((By.ID, 'tablePartesPrincipais')))
                    # print(1)
                    return True, segredo
                except:
                    # print(2)
                    return False, segredo
        except:

            return False, False

        return True, segredo

    # SELECIONA PROCESSOS DO BANCO DE DADOS E PROCURA NA PLATAFORMA PARA UPDATE NO BANCO
    def search_process_to_update(self, user, password, row_database, dict_plp_2grau):
        # LOGIN NA PLATAFORMA E BUSCA DOS PROCESSOS NO BANCO DE DADOS
        # try:
        #     data = datetime(datetime.now().year - 5, datetime.now().month, datetime.now().day,
        #                     datetime.now().hour, datetime.now().minute, datetime.now().second)
        #     conn_database = SQL(self.Access_AQL[0], self.Access_AQL[1], self.Access_AQL[2])
        #     row_database = conn_database.search_process_for_update(100, 'AM', data, self.platform_id)
        #     conn_database.__del__()
        # except AttributeError:
        #     return -1

        # row_database = [['06154090720188040015', '112224', None, None, None, None, None, None, None, None]]

        # INICIA O BROWSER E A SESSÃO NA PLATAFORMA
        self.initializer(user, password)
        print("controler")
        # VERIFICA CADA NUMERO DE PROCESSO DENTRO DA ESTRUTURA FORNECIDA
        i_n = 0
        for i_proc in row_database:
            t0 = time.time()
            i_n += 1
            list_2_grau = dict_plp_2grau[i_proc[1]]
            list_plp_2_grau = []

            # VERIFICA SE O NAVEGADOR ESTÁ ABERTO

            if len(self.browser.window_handles) > 1:
                if self.browser is not None:
                    self.browser.quit()
                    self.log_error.insert_log('Sessão encerrou!')
                    return -1
            else:

                    wait = WebDriverWait(self.browser, 1)
                    wait.until(EC.alert_is_present())
                    self.browser.quit()
                    self.log_error.insert_log('Sessão encerrou!')
                    return -1



            n_proc = i_proc[0]
            n_proc = re.sub('[^0-9]', '', n_proc)
            self.log_error.insert_title(n_proc)
            print("\t{}ª: Coleta de dados do processo: {}".format(i_n, n_proc).upper())

            # BUSCA PELO PROCESSO NA PLATAFORMA
            t = time.time()
            busca = self.busca_processo_na_plataforma(n_proc, i_proc, t0, self.log_error, self.state)
            t1 = time.time()
            print("TEMPO DE BUSCA", (t1 - t0))
            if busca:
                continue


            # VAlIDANDOS SE NUMERO DO PROCESSO CONTIDO NA PLATAFORMA E O MESMO CONTIDO NO SITE

            num_proc = self.browser.find_element_by_xpath('/html/body/table[4]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/table/tbody/tr/td').text


            num_proc = re.sub('[^0-9]', '', num_proc)
            # print('num_proc->', num_proc)

            if num_proc != n_proc:
                self.log_error.insert_log('numero do processo diferente')
                print('###Tempo total da coleta de dados do processo: {} SECS'.format(time.time() - t0).upper())
                print('-' * 65)

                continue

            # COLETA DO NUMERO DO PROCESSO DO 2 GRAU!
            list_2_grau_numero = []
            # try:
            #     for i in self.browser.find_elements_by_xpath(
            #             '//*[@id="containerDadosPrincipaisProcesso"]/div[1]/div/span'):
            #         text = i.text
            #         print("text->", text)
            #         if 'grau' in text and "recurso" in text:
            #             list_2_grau_numero.append(n_proc)
            #             break
            # except:
            #     list_2_grau_numero.clear()
            #     self.log_error.insert_log('coleta dos numeros do processo do 2 grau!'.upper())
            #     raise
            #
            #
            #
            # a = set(list_2_grau_numero)
            # b = set(list_2_grau)
            # list_2_grau_numero = a.difference(b)
            # for i in list_2_grau_numero:
            #     list_plp_2_grau.append(
            #         ProcessoPlataformaModel(plp_prc_id=i_proc[1], plp_plt_id=self.platform_id,
            #                                 plp_numero=i, plp_grau=2, plp_processo_origem=i_proc[0], )
            #     )
            #  COLETA OS ACOMPANHAMENTOS DO PROCESSO

            list_aud, list_acp_pra, list_name_urls, err1, not_refresh = self.acomp_down_aud(i_proc[1], i_proc[4])


            sleep(60*60)

            if not err1 and (self.flag or not_refresh is not 1):
                # PEGA DADOS DO PROCESSO E ATUALIZA TABELA
                try:
                    codigo = str(self.browser.current_url).split('codigo=')[-1].split('&')[0]
                except:
                    codigo = None
                try:
                    classe = self.browser.find_element_by_xpath('//*[@id="classeProcesso"]').text.upper()
                except:
                    classe = None
                try:
                    vara = self.browser.find_element_by_xpath('//*[@id="varaProcesso"]').text.upper()
                except:
                    vara = None
                try:
                    assunto = self.browser.find_element_by_xpath('//*[@id="assuntoProcesso"]').text.upper()
                except:
                    assunto = None
                try:
                    status = self.browser.find_element_by_xpath('//*[@id="labelSituacaoProcesso"]').text.upper()
                    if 'ARQUIVADO DEFINITIVAMENTE' in status or 'ARQUIVADO' in status or 'BAIXADO' in status:
                        status = 'ARQUIVADO'
                    else:
                        status = 'ATIVO'
                except:
                    status = None
                try:
                    self.browser.find_element_by_xpath('/html/body/div[1]/div[3]/div/div[1]/a').click()
                    wait = WebDriverWait(self.browser, 3)
                    wait.until(EC.visibility_of_element_located((By.ID, 'dataHoraDistribuicaoProcesso')))
                    try:
                        valor_causa = self.browser.find_element_by_xpath('//*[@id="valorAcaoProcesso"]').text
                        valor_causa = Tools.treat_value_cause(valor_causa)
                    except:
                        valor_causa = None
                    try:
                        dt_distribuicao = self.browser.find_element_by_xpath('//*[@id="dataHoraDistribuicao'
                                                                             'Processo"]').text.split(' - ')[0]
                        dt_distribuicao = Tools.treat_date(dt_distribuicao)
                    except:
                        dt_distribuicao = None
                except:
                    valor_causa = None
                    dt_distribuicao = None

                print('\n----')
                print(dt_distribuicao)
                print(valor_causa)
                print(vara)
                print(classe)
                print(codigo)
                print(status)

                # IDENTIFICA OS ENVOLVIDOS E RETORNA UMA LISTA COM AS PARTES, OS ADVOGADOS E O JUIZ
                list_partes, list_advogs = self.envolvidos

                # CRIA O OBJETO PROCESSO-PLATAFORMA QUE SERÁ INSERIDO NO BANCO DE DADOS
                process_platform = ProcessoPlataformaModel(plp_prc_id=i_proc[1], plp_plt_id=self.platform_id,
                                                           plp_numero=n_proc, plp_status=status,
                                                           plp_vara=vara, plp_codigo=codigo, plp_grau=1,
                                                           plp_valor_causa=valor_causa, plp_classe=classe,
                                                           plp_assunto=assunto,
                                                           plp_data_distribuicao=dt_distribuicao,
                                                           plp_segredo=False, plp_localizado=True)

                list_objects_process = [(process_platform, list_partes, list_advogs, list_aud, list_acp_pra,
                                         i_proc[7], list_plp_2_grau)]

                # INSERE A LISTA DE OBJETOS NO BANCO DE DADOS
                # self.export_to_database(objects=list_objects_process, log=self.log_error,
                #                         list_name_urls=list_name_urls,
                #                         platform=self.platform_name, state=self.state, root=self)

                self.log_error.insert_info('Procedimento finalizado!')
            elif not err1:
                # CRIA O OBJETO PROCESSO-PLATAFORMA QUE SERÁ INSERIDO NO BANCO DE DADOS
                process_platform = ProcessoPlataformaModel(plp_prc_id=i_proc[1], plp_plt_id=self.platform_id,
                                                           plp_numero=n_proc, plp_segredo=False,
                                                           plp_localizado=True)

                list_objects_process = [
                    (process_platform, [], [], list_aud, list_acp_pra, i_proc[7], list_plp_2_grau)]

                # INSERE A LISTA DE OBJETOS NO BANCO DE DADOS
                self.export_to_database(objects=list_objects_process, log=self.log_error,
                                        list_name_urls=list_name_urls,
                                        platform=self.platform_name, state=self.state, root=self)

                self.log_error.insert_info('Procedimento finalizado!')
            else:  # SENÃO FAZ UMA NOVA BUSCA
                # LIMPA A PASTA PARA RECEBER OS NOVOS DOWNLOADS
                self.clear_path_download()

            print('###Tempo total da coleta de dados do processo: {} SECS'.format(time.time() - t0).upper())
            print('-' * 65)

        # VERIFICA SE O NAVEGADOR FECHOU, SENÃO O FECHA
        if self.browser is not None:
            self.browser.quit()

        # VERIFICA SE NÃO RETORNOU ALGUM PROCESSO DA BASE, SENÃO ATUALIZA A PLE_DATA
        # self.update_ple_data(ple_plt_id=self.platform_id, ple_uf=self.state)

        return i_n

    def initializer(self, user, password):
        while True:
            # INICIALIZA BROWSER
            if self.init_browser():
                # LOGIN NA PLATAFORMA
                conte = 4
                while conte:
                    conte -= 1
                    if self.login(user, password):
                        conte = -1
                        break
                    if 'http://esaj.tjba.jus.br/esaj/erroDesconhecido.do?layoutIndisponivel=true'  in self.browser.current_url:
                        conte=0

                if conte == -1:
                    break
            if self.browser is not None:
                self.browser.quit()

    # REALIZA LOGIN
    def login(self, user, password):
        try:
            try:
                wait = WebDriverWait(self.browser, 2)
                wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="identificacao"]')))
                texto = self.browser.find_element_by_xpath('//*[@id="identificacao"]').text
                if texto not in "  Identificar-se ":
                    return True
            except:
                pass
            wait = WebDriverWait(self.browser, 4)
            wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="usernameForm"]')))
            self.browser.find_element_by_id('usernameForm').send_keys(user)
            self.browser.find_element_by_id('passwordForm').send_keys(password)
            self.browser.find_element_by_xpath('//*[@id="pbEntrar"]').click()
            wait = WebDriverWait(self.browser, 4)
            wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="identificacao"]')))
            texto=self.browser.find_element_by_xpath('//*[@id="identificacao"]').text
            if texto in "  Identificar-se ":
                self.browser.find_element_by_xpath('//*[@id="identificacao"]/strong/a ').click()
                return False
            return True
        except:
            return False

        # PEGA ANDAMENTOS DO PROCESSO, AS AUDIÊNCIAS E REALIZA OS DOWNLOADS POR ACOMPANHAMENTO

    def acomp_down_aud(self, prc_id, ult_mov):

        print("Arrso ")
        list_acomp_download = []
        file_downloaded = None

        list_file_path = []
        list_audiences = []
        list_name_urls = []
        not_refresh = 0
        err = False
        t = 0
        k = 0
        try:
            try:

                self.browser.execute_script('arguments[0].style.display = "block";',
                                            self.browser.find_element_by_id('tabelaTodasMovimentacoes'))
                self.browser.execute_script('arguments[0].style.display = "none";',
                                            self.browser.find_element_by_id('tabelaUltimasMovimentacoes'))
            except:
                # raise
                list_acomp_download.clear()
                list_audiences.clear()
                list_name_urls.clear()
                self.log_error.insert_info('Não há Movimentações para este processo!'.upper())
                return list_audiences, list_acomp_download, list_name_urls, err, not_refresh

            movimentos = self.browser.find_elements_by_xpath('//*[@id="tabelaTodasMovimentacoes"]/tbody/tr')
            max_n_events = len(movimentos)

            max_n_events = len(movimentos)
            for i in range(len(movimentos)):
                try:
                    k += 1
                    aux_data = movimentos[i].find_element_by_xpath('td[1]').text
                    aux_data = Tools.treat_date(aux_data)
                    print("aux_data",aux_data)

                    if ult_mov is not None:
                        not_refresh += 1
                        if aux_data <= ult_mov:
                            break

                    desc_process = movimentos[i].find_element_by_xpath('td[3]').text[:997].upper()
                    desc_process = Tools.remove_accents(desc_process)
                    n_event = max_n_events - i

                    # PEGAR AS AUDIÊNCIAS
                    if desc_process.find('AUDIENCIA') == 0:
                        j = desc_process.upper().find('SITUACAO:')
                        status = desc_process if j < 0 else desc_process[:j]
                        status, tipo = self.treat_type_and_status(status, desc_process)
                        date_audience = None
                        obs = None
                        if desc_process.find('DATA: ') >= 0:
                            date_audience = desc_process.split(': ')[1].replace(' LOCAL', '').lower()
                            date_audience = Tools.treat_date(date_audience)
                            obs = desc_process.split(': ')[2].replace(' SITUACAO', '')

                        list_audiences.append((tipo, status, date_audience, obs, aux_data))

                    list_file_name = []
                    acp_pra_status = False
                    try:
                        link_url = movimentos[i].find_element_by_xpath('td[2]/a').get_attribute("href")
                        self.browser.execute_script('''window.open("{}","_blank");'''.format(link_url))
                        try:
                            self.browser.switch_to_window(self.browser.window_handles[1])
                            wait = WebDriverWait(self.browser, 10)
                            wait.until(EC.visibility_of_element_located((By.ID, 'esticarButton')))
                            self.browser.find_element_by_xpath('//*[@id="esticarButton"]').click()
                            self.browser.find_element_by_xpath('//*[@id="selecionarButton"]').click()
                            self.browser.find_element_by_xpath('//*[@id="salvarButton"]').click()
                            wait = WebDriverWait(self.browser, 20)
                            wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="btnDownloadDocumento"]')))
                            wait.until(EC.invisibility_of_element_located((By.XPATH, '//*[@id="'
                                                                                     'btnAguardarProcessamento"]')))
                            wait.until(
                                EC.visibility_of_element_located((By.XPATH, '//*[@id="btnDownloadDocumento"]')))
                            n_files = len(os.listdir(self.path_download_prov))
                            self.browser.find_element_by_xpath('//*[@id="btnDownloadDocumento"]').click()
                            t += 1
                            self.browser.close()
                            self.browser.switch_to_window(self.browser.window_handles[0])

                            err_down = self.wait_download(n_files)
                            try:
                                # VERIFICA SE A SESSÃO FOI ENCERRADA
                                if len(self.browser.window_handles) > 1:
                                    if self.browser is not None:
                                        self.browser.switch_to_window(self.browser.window_handles[1])
                                        self.browser.close()
                                        self.browser.switch_to_window(self.browser.window_handles[0])
                                        acp_pra_status = False
                                        err_down = True
                                else:
                                    try:
                                        wait = WebDriverWait(self.browser, 1)
                                        wait.until(EC.alert_is_present())
                                        self.browser.quit()
                                        self.log_error.insert_log('Sessão encerrou!')
                                        return -1
                                    except:
                                        pass
                            except:
                                self.log_error.insert_log('Download do arquivo: evento {}!'.format(n_event))
                                acp_pra_status = False
                                err = True
                                break
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
                                list_file_name.append(ProcessoArquivoModel(pra_prc_id=prc_id,
                                                                           pra_nome=nome,
                                                                           pra_descricao=desc_file))
                                acp_pra_status = True
                            else:
                                self.log_error.insert_log('Download do arquivo: evento {}!'.format(n_event))
                                acp_pra_status = False
                        except:
                            self.browser.close()
                            self.browser.switch_to_window(self.browser.window_handles[0])
                            self.log_error.insert_log('Download do arquivo: evento {}!'.format(n_event))
                            acp_pra_status = False
                    except:
                        pass

                    list_acomp_download.append((AcompanhamentoModel(acp_esp=desc_process,
                                                                    acp_numero=n_event,
                                                                    acp_data_cadastro=aux_data,
                                                                    acp_prc_id=prc_id), list_file_name))
                except:
                    pass

            print('tam: {} | file: {}'.format(len(list_name_urls), t))

            # PEGA AS AUDIÊNCIAS APÓS ULTIMA DATA DE MOVIMENTAÇÃO DOS ACOMPANHAMENTOS
            for j in range(len(movimentos[k:])):
                desc_process = Tools.remove_accents(movimentos[j].find_element_by_xpath('td[3]').text[:997].upper())
                if desc_process.find('AUDIENCIA') == 0:
                    aux_data = movimentos[j].find_element_by_xpath('td[1]').text
                    aux_data = Tools.treat_date(aux_data)
                    j = desc_process.upper().find('SITUACAO:')
                    status = desc_process if j < 0 else desc_process[:j]
                    status, tipo = self.treat_type_and_status(status, desc_process)
                    date_audience = None
                    obs = None
                    if desc_process.find('DATA: ') >= 0:
                        date_audience = desc_process.split(': ')[1].replace(' LOCAL', '').lower()
                        date_audience = Tools.treat_date(date_audience)
                        obs = desc_process.split(': ')[2].replace(' SITUACAO', '')

                    list_audiences.append((tipo, status, date_audience, obs, aux_data))



        except:
            # raise
            list_acomp_download.clear()
            list_audiences.clear()
            list_name_urls.clear()
            self.log_error.insert_log('coleta de dados dos acompanhamentos do processo!'.upper())
            err = True
            # raise

        return list_audiences, list_acomp_download, list_name_urls, err, not_refresh
