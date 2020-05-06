from selenium import webdriver
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import  By
# from PIL import Image
# import pytesseract
from Model.toolsModel import *
from Model.processoArquivoModel import ProcessoArquivoModel
from Model.audienciaModel import AudienciaModel
from Model.Civel.pjeModel import PjeModel
import webbrowser
import argparse
# import cv2
import os
# import numpy as np
import urllib.request
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
# import pyautogui
from Model.parteModel import ParteModel
from Model.responsavelModel import ResponsavelModel
from Model.acompanhamentoModel import AcompanhamentoModel
from Model.processoPlataformaModel import ProcessoPlataformaModel
from Model.Civel.rootModel import RootModel
import codecs
import random
import re

# https://pje.trt{}.jus.br/primeirograu/login.seam
class PJETabalhistaModel(RootModel):



    def __init__(self,trt,acesso,estado = 'SEM'):


        self.trt = trt
        self.site = 'https://pje.trt{}.jus.br/primeirograu/login.seam'.format(trt)
        self.siteprocesso = 'https://pje.trt{}.jus.br/consultaprocessual/consulta-terceiros'.format(trt)
        self.site_busca_acervo = ' https://pje.trt{}.jus.br/primeirograu/Painel/painel_usuario/advogado.seam'.format(trt)
        self.id_botao = 'loginAplicacaoButton' # botão para apertar loguin
        self.aud_pos = 0
        self.prc_id = None
        self.parou_doc = 1
        self.num = None
        super().__init__( site = self.site, mode_execute=False, SQL_Long=acesso, platform_id = 2, platform_name='Pje',estado=estado)




    # ABRE O NAVEGADOR PARA INICIAR AS BUSCAS
    ########  OBJETIVO DESSA FUNÇÃO É INICIANIZAR O BROWSER E FAZER O LOGUIN###

    def atualizar_info(self):
        try:
            self.browser.get('https://127.0.0.1:9000')
            self.browser.find_element_by_xpath('//*[@id="details-button"]').click()
            wait = WebDriverWait(self.browser,3)
            wait.until(EC.visibility_of_element_located((By.XPATH,'//*[@id="proceed-link"]')))
            self.browser.find_element_by_xpath('//*[@id="proceed-link"]').click()
            wait.until(EC.visibility_of_element_located((By.XPATH,'//*[@id="nav-mobile"]/li[1]/a')))
            self.browser.find_element_by_xpath('//*[@id="nav-mobile"]/li[1]/a').click()
            wait.until(EC.visibility_of_element_located((By.XPATH,'//*[@id="container"]/div/div[1]/div[2]/p[2]/a')))
            self.browser.find_element_by_xpath('//*[@id="container"]/div/div[1]/div[2]/p[2]/a').click()
            sleep(1)
        except Exception as Erro:
            print(Erro)
            pass

    def loguinPJE(self):  # FUNÇÃO PARA ENTRAR NA PAGINA PJE E FICAR NA PAGINA DE BUSCA DE PROCESSOS

        try:  # TENTA LOGAR


            self.init_browser()

            self.atualizar_info()
            self.browser.get(self.site)

            wait = WebDriverWait(self.browser, 8)                                   # esperar  5  segundos até a página carregar
            wait.until(EC.element_to_be_clickable((By.ID, self.id_botao)))          # ATÉ PODER SER CLICADO
            self.browser.find_element_by_id(self.id_botao).click()                  # clicando no botão de loguin


            # sleep(15)
            wait.until(EC.invisibility_of_element((By.ID, self.id_botao)))          # ATÉ PODER SER CLICADO

            return True if not (self.browser.current_url == self.site) else False   # VERIFICAR SE MUDOU DE LINK

        except:  # NÃO CONSEGUIU LOHGAR

            raise
            return False # 'Não foi possivel logar na página'

    def buscaProcessoTerceiros(self, numero_processo, id_botao, id_input_processo):  # modelo versão 2
        try:
            wait = WebDriverWait(self.browser, 5)  # esperar  5  segundos até a página carregar
            wait.until(EC.element_to_be_clickable((By.ID, id_botao)))  # ATÉ PODER SER CLICADO
            self.browser.find_element_by_id(id_input_processo).send_keys(numero_processo)  # coloca o numero do processo
            self.browser.find_element_by_id(id_botao).click()  # clica no botão de pequisar
            return True
        except:
            return False, 'Erro na busca do processo versão 2 !'


    def string_da_iamgem(self):
        pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Public\tesseract\tesseract.exe'

        image = cv2.imread('v.jpg')
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        gray = cv2.medianBlur(gray, 3)
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        filename = "{}.png".format(os.getpid())
        cv2.imwrite(filename, gray)

        text = pytesseract.image_to_string(Image.open(filename),config='--psm 9 --oem 3 -c tessedit_char_whitelist='
                                                                       'abcdefghijklmnoprstuvwxyz0123456789')
        # print(text)
        os.remove(filename)
        #print(Tools.remove_accents(text).replace(' ', '').split('\n')[0])


    #PEGA AS INFORMAÇÕES E FAZ OS DONWLOADS
    def get_list_segredo_ou_sigilo(self,list_documentos,lis_name_urls):


            obj_download = []
            list_aux_url = []

            wait = WebDriverWait(self.browser, 7)  # esperar  5  segundos até a página carregar
            wait.until(EC.invisibility_of_element_located((By.ID, '_viewRoot:status.start')))  # esperar a barra de carregamento

            wait.until(EC.presence_of_element_located((By.CLASS_NAME,'rich-table-row')))

            table = self.browser.find_elements_by_xpath('//*[@id="processoTrfDocumentoMagistradoGridList:tb"]/tr')

            for i in table:



                a = i.find_elements_by_css_selector('a') # pegar a span que a imagem está


                nome_arq = a[0].find_element_by_css_selector('img').get_attribute('title') # pegando o titulo da imagem

                if str(nome_arq) == 'Documento inativado ou aguardando data de publicação':
                    continue
                nome_arquivos = os.listdir(self.path_download_prov)  # quantidade de elementos antes do donwload

                if str(nome_arq) =='Visualizar': # Se for arquivo HTML o titulo é Visualizar
                    a[0].click()
                    pra_nome = self.donwloadAcompanhamento()  # retorna o nome do download
                    obj_download.append(ProcessoArquivoModel(pra_prc_id=None, pra_nome=pra_nome, pra_descricao=i.text))
                    list_aux_url.append((pra_nome.replace('.html',''), pra_nome))  # nome baixado, nome para renomear



                else:  # se for PDF
                    a[0].click()
                    acp_pra_status, download = self.verifica(len(nome_arquivos), nome_arquivos,list_aux_url)  # esperar o download concluir
                    self.browser.switch_to_window(self.browser.window_handles[-1]) # seleciona a ultima janela para continuar os donloads
                    if acp_pra_status:
                        obj_download.append(download)



            # obj_download.append(ProcessoArquivoModel(pra_prc_id=None, pra_nome=pra_nome, pra_descricao=linha))
            list_documentos += obj_download
            lis_name_urls += list_aux_url


    def get_segredo_ou_sigilo(self):

        try:

            list_documentos = []
            list_name_url = []


            self.browser.execute_script("window.scrollTo(0,0)")  # sobe a aba para poder cliclar nas guias
            self.browser.find_element_by_id('permissaoProcessoDocumento_lbl').click() # CLICAR NA ABA DE SEGREDO OU SIGILO

            # Esperar a tabela carregar
            wait = WebDriverWait(self.browser, 7)  # esperar  5  segundos até a página carregar
            wait.until(EC.invisibility_of_element_located((By.ID, '_viewRoot:status.start')))  # esperar a barra de carregamento sumir



            self.get_list_segredo_ou_sigilo(list_documentos,list_name_url)


            self.parou_doc += 1
            # Xpath para verificar se existe a box para passar de pagina
            xpath_box = '//*[@id="processoTrfDocumentoMagistradoGrid"]/div/div[2]/form/table/tbody/tr[1]/td[5]/input'

            box = self.browser.find_elements_by_xpath(xpath_box)

            if len(box) > 0 : # existe a box

               atual = box[0].get_attribute('value')  # pagina atual das tabelas
               fim = self.browser.find_element_by_xpath('//*[@id="processoTrfDocumentoMagistradoGrid"]/div/div[2]/form/table/tbody/tr[1]/td[3]').text # final
               if int(atual) < int(fim):  # AINDA TEM MAIS PARA VARRER

                   xpathBotao = '//*[@id="processoTrfDocumentoMagistradoGrid"]/div/div[2]/form/table/tbody/tr[1]/td[4]/div/div[2]'

                   self.browser.find_element_by_xpath(xpathBotao).click()

                   # Esperar a tabela atualizar
                   wait.until(EC.invisibility_of_element((By.ID,'_viewRoot:status.start')))
                   list_aux, list_name_url_aux = self.get_segredo_ou_sigilo()

                   list_documentos += list_aux
                   list_name_url += list_name_url_aux




            return list_documentos, list_name_url
        except:

            teste = self.try_erro_segredo_ou_sigilo()
            if teste:
                return  self.get_segredo_ou_sigilo()

            print('erro processo ao pegar a lista de documentos')
            return [], []
            print('RUIM ')


    # class PjeModel1Grau(PJETabalhistaModel):
#     def __init__(self, trt):
#
#         super().__init__(trt = trt)
#tipo é a versão da interface do site 1 a mais antiga 2 mais nova

    def fechaAba_e_voltaPrimeira(self):
        try:
            if len(self.browser.window_handles) >= 2:
                self.browser.close() # fecha a atual
                self.browser.switch_to_window(self.browser.window_handles[0]) # volta para a primeira
            return  True
        except:

            return False # 'Erro ao selecionar aba de navegaçao'


    def buscaProcessoTerceiros(self, numero_processo): # modelo versão 2

        try:

            busca = buscaProcesso(numero_processo,'btnPesquisar','mat-input-0') # botão e input da versão 2

            if busca is True:
                wait = WebDriverWait(self.browser, 5)  # esperar  5  segundos até a página carregar
                wait.until(EC.visibility_of_all_elements_located((By.XPATH,
                                                                  '/html/body/pje-root/pje-consulta-'
                                                                  'terceiros/div/mat-card[2]/pje-data-table'
                                                                  '/div[1]/table/tbody[1]/tr'))) # Resultado da busca se existir processo

                listaProcesso = self.browser.find_elements_by_xpath('/html/body/pje-root/'
                                                    'pje-consulta-terceiros/div/mat-card[2]/'
                                                    'pje-data-table/div[1]/table/tbody[1]/tr') # Lista de processo na tabela

                for i in listaProcesso: # procurar na lista de processos o numero do processo do parametro

                    a = i.find_element_by_xpath('td[1]/span/a')
                    num_processo = re.sub('[^0-9]','',a.text)# tira todos os pontos


                    if num_processo  == numero_processo: # se o numero na tabela for igual o da busca


                        link_url = a.get_attribute("href")  # pega o atributo do link
                        self.browser.execute_script('''window.open("{}","_blank");'''.format(link_url))# abre uma nova aba com link

                        self.browser.switch_to_window(self.browser.window_handles[-1])  # vai para última aba

                        wait2 = WebDriverWait(self.browser, 5)  # esperar  5  segundos até a página carregar
                        wait2.until(EC.element_to_be_clickable((By.XPATH,'/html/body/pje-root/pje-detalhe-'
                                                                          'processo/div[2]/button[1]'))) # espera o botão primeiro grau aparecer para clicar


                        self.browser.find_element_by_xpath('/html/body/pje-root/pje-detalhe-'
                                                            'processo/div[2]/button[1]').click() # acha o botão e da um click


                        imagem = self.browser.find_element_by_id('imagemCaptcha').get_attribute('src') # Pega o link da imagem
                        urllib.request.urlretrieve(imagem, "verificacao.jpg") # faz o donwload da imagem
                        # os.remove("verificacao.jpg")

                        break

                return True
            else: # não existe  aquivos para o processo
                return False

        except: # não deu certo a busca ou não existe processo
            raise
            return False


    def procuraProcessoTable(self,numero_processo):

        try:
            listaProcesso = self.browser.find_elements_by_xpath('/html/body/div[5]/div/div/div[2]/div/table/tbody/tr[2]'
                                                                '/td/table/tbody/tr/td/table/tbody/tr/td[2]/div/div[2]/'
                                                                'div/div[2]/div[2]/table/tbody/tr')  # Lista de processo na tabela

            for i in listaProcesso:
                descricao_processo = i.find_element_by_xpath('td[2]/div/div/a/span')
                num = descricao_processo.text.replace(' ','')         # tirar os espaços
                num = re.sub('[^0-9]', '', num)                       # tira todos os pontos e letras e derivados
                if str(num) == str(numero_processo):             # se o numero na tabela for igual o do processo

                    descricao_processo.click() # clica no processo
                    self.browser.switch_to_window(self.browser.window_handles[-1]) # selecionar a página do processo da pessoa

                    # print('quantidade de janelas: ', len(self.browser.window_handles))
                    wait2 = WebDriverWait(self.browser, 5)         # esperar  5  segundos até a página carregar
                    wait2.until(EC.element_to_be_clickable((By.ID,'idEditarModeloDocumento')))

                    self.browser.maximize_window()

                    return True
        except:

            return False

    def verificaBoxAcervo(self, numero_processo):

        # verificar se colocou o número certo na box
        i = 1

        numero = numero_processo[:13] + numero_processo[16:]
        for j in range(4):


            # self.browser.find_element_by_id(
            #     'consultaProcessoAdvogadoForm:numeroProcessoDecoration:numeroProcesso').clear()
            self.browser.find_element_by_id(
                'consultaProcessoAdvogadoForm:numeroProcessoDecoration:numeroProcesso').send_keys(Keys.HOME)
            self.browser.find_element_by_id(
                'consultaProcessoAdvogadoForm:numeroProcessoDecoration:numeroProcesso').send_keys(numero)

            # self.gambiaraColocarNumeroAcervo(numero_processo)  # colocar o numero do processo na box
            # numero_processo = numero_processo[:13] + numero_processo[16:]  # a box já possui alguns número ja colocados
            campo = self.browser.find_element_by_id('consultaProcessoAdvogadoForm:numeroProcessoDecoration:numeroProcesso') # procura por id o campo do processo
            #campo.clear()
            #campo.send_keys(numero_processo)

            # campo.send_keys(numero_processo)



            boxnumero = re.sub('[^0-9]', '', campo.get_attribute('value'))
            # print("box numero ", boxnumero,' tam:', len(boxnumero), "procesos: ", numero_processo,' tam:', len(numero_processo))

            if str(boxnumero) == str(numero_processo):
                break
            i += 1

        # print('i é maior que 4 ? ', i>=4)
        return not (i >= 4)

    def extrair_cpnj_string(self,string_extrair):
        cpnj_padrao = r'[0-9][0-9].[0-9][0-9][0-9].[0-9][0-9][0-9]/[0-9][0-9][0-9][0-9]-[0-9][0-9]' # Padrão a ser buscado
        cpnj = re.findall(cpnj_padrao, string_extrair)  # Retorna um vetor com as datas encontradas na string
        if len(cpnj) > 0:
            return re.sub('[^0-9]', '', cpnj[0])  # Retirar pontos e tracos
        return  False


    def extrair_cpf_string(self, string_extrair):

        cpf_padrao = r'[0-9][0-9][0-9].[0-9][0-9][0-9].[0-9][0-9][0-9]-[0-9][0-9]'  # Padrão CPF
        cpf = re.findall(cpf_padrao, string_extrair)  # Retorna um vetor com as datas encontradas na string

        if len(cpf) > 0:
            return re.sub('[^0-9]', '', cpf[0]) # Retirar pontos e tracos

        return  False
    def extrair_oab_string(self,string_extrair):
        extrair = string_extrair.upper() # deixar maiusculo

        extrair = extrair.split('OAB')[1]  # separar pelo OAB
         # as vezes a oab possui -GO, por exemplo, significa que foi transferida de um estado para outro
        oab = extrair.split('-')[0] # A OAB é  separada por traço
        str_aux = extrair.split('-')
        if len( str_aux)> 3:
            oab += str_aux[1] # Pegar o resto da OAB se existir
        oab = oab.replace(' ','')
        oab = oab.replace(':','')
        return oab


    def get_info_Tabela_polo(self, id, polo):

        list_advogados = []
        list_partes = []
        try:

            wait = WebDriverWait(self.browser, 5)  # esperar  5  segundos até a página carregar
            wait.until(EC.visibility_of_element_located((By.XPATH,'//*[@id="{}:tb"]/tr'.format(id))))  # ATÉ APARECER a tabela


            tabelaAtivo = self.browser.find_elements_by_xpath('//*[@id="{}:tb"]/tr'.format(id)) # pegar a tabela do polo ativo ou passivo

            print('Tamanho da tabela : ',polo, 'Len:',len(tabelaAtivo))
            for linha in tabelaAtivo:
                try:

                    linha.location_once_scrolled_into_view # Colcoar o elemento visível na tela

                    string = linha.find_element_by_xpath('td[1]/span[2]').text # pegando a linha inteira da tabela
                    cpf = self.extrair_cpf_string(string) # Extrair CPF se exitir
                    if cpf == False: # Se não existir cpf
                        cpf = self.extrair_cpnj_string(string) # Extrair cpnj se existir
                    nome = Tools.remove_accents(string.split('-')[0])     # nome é separado por '-'
                    if( 'OAB' in string.upper()): # SE EXISTIR OAB É ADVOGADO

                        oab = self.extrair_oab_string(string)# pegar apenas o numero da OAB
                        list_advogados.append((ResponsavelModel(rsp_nome=nome.upper(),rsp_tipo='ADVOGADO(A)',rsp_oab=oab),polo))
                        # print('>>> ADV:  nome->',nome, ' OAB->', oab ,' CPF->', cpf , '\n' )
                    else:
                        list_partes.append((ParteModel(prt_nome=nome.upper(), prt_cpf_cnpj=cpf), polo))



                    #return False, 'Erro na estruturação da parte Ativa/Passiva'
                except:
                    print('Erro ao pegar na tabela ativo')
                    pass


        except:

            list_advogados = []
            list_partes = []
            return  list_advogados,list_partes

        return  list_advogados,list_partes


# Pegar os envolvidos do processo
    def get_Envolvidos(self):

        wind = self.browser.find_element_by_xpath('//*[@id="informativoProcessoTrf"]/table/tbody/tr/td/div') # Elemento para abaixar o scroll
        self.browser.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', wind)

        list_advogado0, list_partes0 = self.get_info_Tabela_polo('listaPoloAtivo','Ativo')
        list_advogado1, list_partes1 = self.get_info_Tabela_polo('listaPoloPassivo','Passivo')
        print('Lista Partes: ')

        list_advogado0+=list_advogado1
        list_partes0+=list_partes1
        for i in list_advogado0:
            print('nome: ' ,i[0].rsp_nome, 'Tipo:', i[0].rsp_tipo, ' OAB: ', i[0].rsp_oab, 'Polo:', i[1])

        for i in list_partes0:
            print('Nome: ', i[0].prt_nome, 'CPF: ', i[0].prt_cpf_cnpj, 'Polo: ', i[1])







        return list_advogado0, list_partes0

    def donwloadAcompanhamento(self, nome):

        nome =  nome +  '.html' # nome do arquivo que será salvo
        # print('donwload html : ', name)
        self.browser.switch_to_window(self.browser.window_handles[-1])  # vai para última aba
        completeName = os.path.join(self.path_download_prov,nome)
        file_object = codecs.open(completeName, "w", "utf-8")
        html = self.browser.page_source
        file_object.write(html)
        self.browser.close()
        self.browser.switch_to_window(self.browser.window_handles[-1])  # vai para última aba
        return  nome



    def movimentacoes(self,list_name_url, prc_id, data_update):


        try:

            self.parou_doc = 1

            self.browser.execute_script("window.scrollTo(0,0)")  # sobe a aba para poder cliclar nas guias
            self.browser.switch_to_window(self.browser.window_handles[1])  # se estiver na primeira
            self.browser.find_element_by_id('MovimentacoesId_lbl').click()  # IR PARA ABA DE MOVIMENTAÇÕES
            wait = WebDriverWait(self.browser, 10)  # esperar  5  segundos até a página carregar
            wait.until(EC.invisibility_of_element_located((By.ID, '_viewRoot:status.start')))  # esperar a barra de carregamento sum


            ###################################PEGAR TODAS AS MOVIMENTAÇÕES#####################################
            l,r = self.get_movimentacoes(list_name_url = list_name_url,prc_id = prc_id, data_update=data_update) # pega todas as movimentações

        except:
            raise
            print('Deu ruim bdsafybasfydyfdysbfydyfdyfydsbhfd\hfbdufudhfuduhffduhuffdusufhdsufuuçufh')

            try:

                self.try_movimentacoes()
                l,r = self.get_movimentacoes(list_name_url = list_name_url,prc_id = prc_id, data_update=data_update)  # pega todas as movimentações

            except:
                print('Erro em movimentações')
                self.aud_pos = 0  # zera a flag
                raise



        for i in l: # l é s lista de donwloads

            if len(i[-1]) >= 1: # se existe um elemento
                # print("Elemento: ", i[-1])
                if i[-1] == "TEM": # se tem audiencia para pegar
                     i[-1]=[]
                     print('Tem audiências realizadas')
                     try:

                            # print('Tem download')
                            self.browser.find_element_by_id('tabProcessoAudiencia_lbl').click()  # Pass
                            wait = WebDriverWait(self.browser, 10)  # esperar  5  segundos até a página carregar
                            wait.until(EC.invisibility_of_element_located((By.ID, '_viewRoot:status.start')))
                            tabela = self.browser.find_element_by_xpath('//*[@id="processoConsultaAudienciaGridList:tb"]')  # procura a tabela
                            tabela = tabela.find_elements_by_class_name('rich-table-row')


                            try:

                                # print('pos tabela aud: ', self.aud_pos)
                                status = tabela[self.aud_pos].find_element_by_xpath('td[5]/span/div').text
                                # print('stauts: ', status)
                                if str(status) != 'realizada':
                                    self.aud_pos +=1
                                    while str(tabela[self.aud_pos].find_element_by_xpath('td[5]/span/div').text) != 'realizada':
                                        self.aud_pos+=1

                                if self.aud_pos < len((tabela)):

                                    t = tabela[self.aud_pos].find_elements_by_css_selector('a')
                                    # print('len css:', len(t))
                                    if len(t)<=0:
                                        continue
                                    t[0].click()

                                    # print('Passou click')
                                    donwloads = self.donwloadAcompanhamento()
                                    list_name_url.append((donwloads,donwloads+'.html'))  # nome baixado, nome para renomear

                                    # print('ver download: ', donwloads)
                                    novo = ProcessoArquivoModel(pra_prc_id=self.prc_id, pra_nome=donwloads, pra_descricao=donwloads)
                                    i[-1].append(novo)
                                else:
                                    i[-1]=[]


                            except:

                                i[-1]=[]
                            self.aud_pos += 1
                     except:
                         pass


        self.aud_pos = 0 # zera a flag
        return l,r


    def get_movimentacoes(self,list_name_url, prc_id,data_update): # funçao para pegar as movimentações

        lista_acp_download = []
        lista_audiencias =[]

        wait = WebDriverWait(self.browser, 5)  # esperar  5  segundos até a página carregar
        wait.until(EC.invisibility_of_element_located((By.ID, '_viewRoot:status.start')))  # esperar a barra de carre

        try:
            flag = False
            wait.until(EC.presence_of_all_elements_located((By.XPATH,'//*[@id="movimentacaoList:tb"]/tr')))  # ATÉ APARECER as movimentações
            wait.until(EC.invisibility_of_element_located((By.ID, '_viewRoot:status.start')))  # esperar a barra de carregamento sum

            flag = self.get_list_mov(lista_audiencias=lista_audiencias, lista_acp_download=lista_acp_download,
                             prc_id=prc_id, data_update = data_update, list_name_url= list_name_url)  # pega uma pagina da tabela

            self.parou_doc += 1 # onde as movimentações pararam se caso haver algum erro

            wait.until(EC.invisibility_of_element_located((By.ID, '_viewRoot:status.start')))
            xpathBox = '//*[@id="movimentacaoListPanel_body"]/div/form/table/tbody/tr[1]/td[5]/input'
            xpathfinalpagina = '//*[@id="movimentacaoListPanel_body"]/div/form/table/tbody/tr[1]/td[3]'
            xpathPassarPagina = '//*[@id="movimentacaoListPanel_body"]/div/form/table/tbody/tr[1]/td[4]/div/div[2]'
            atual = self.browser.find_elements_by_xpath(xpathBox) # atual é o numeoro da pagina

            if len(atual)>0:  # tem mais de vinte
                atual[0].location_once_scrolled_into_view # Descer o srcoll e colocar elee selemnto visivel
                fim = self.browser.find_elements_by_xpath(xpathfinalpagina)  # final da pagina

                if int(atual[0].get_attribute('value')) < int(fim[0].text) and (not(flag)): # Se ainda tem movimentações a ser pega

                    self.browser.find_element_by_xpath(xpathPassarPagina).click() # Passar de pagina
                    wait.until(EC.invisibility_of_element_located((By.ID, '_viewRoot:status.start')))  # esperar a barra de carre
                    lis_aux_donw, lis_aux_aud = self.get_movimentacoes(list_name_url= list_name_url,prc_id= prc_id,data_update =data_update)
                    lista_acp_download += lis_aux_donw
                    lista_audiencias += lis_aux_aud



            return lista_acp_download, lista_audiencias

        except:
            raise

            try:
                self.try_movimentacoes()
                return   self.get_movimentacoes(list_name_url, prc_id, data_update) # pega todas as movimentações
            except:
                print("deu ruim")
                return  [],[] # se deu bosta retorna

    def donwload_por_id(self,lista_documentos):

        wait = WebDriverWait(self.browser, 8)  # esperar  5  segundos até a página carregar
        list_doc = []
        list_url_t = []
        i = 0
        for obj in lista_documentos:  # FAZER OS DOWNLOAD DE TODOS OS DOCUMENTOS
            # acp_pra_status, downloads, list_url_name =

            acp_pra_status, downloads, list_url_name = self.download_documentos(obj.acp_numero, i)
            obj.acp_pra_staus = acp_pra_status
            list_url_t+= list_url_name # para renomear todos arquivos posteriomente

            #deu certo o download

            list_doc.append((obj, [downloads] if acp_pra_status else [])) # lista do numero da movi e o status

            wait.until(EC.invisibility_of_element_located((By.ID, 'downloadDocumentosModalCDiv')))  # espera a janela fechar
            i += 1


        # print('tamanho lista docdowload', len(list_doc))
        # for i in list_doc:
        #
        #     print('novo nome: ', i[1][0].pra_nome, ' velho:', i[1][0].pra_descricao)

        return  list_doc, list_url_t


    def tempoCarregarTabelaDoc(self, elemento):

        self.browser.execute_script('return document.readyState')  # espera a página carregar

        tabela = self.browser.find_element_by_id('processoDocumentoGridTabList:tb')  # pegar a tabela
        tabela = tabela.find_elements_by_class_name('rich-table-row')  # pegando cada linha pela classe
        while elemento == tabela[0].find_element_by_xpath('td[1]').text:
            continue
        # print(tabela[0].find_element_by_xpath('td[1]').text)

    # RECAREGAR  ATÉ O PROCESSO
    def reload(self):

        if self.browser is not None:
            self.browser.quit()  # FECHAR TUDO E REINICIAR

        status = self.loguinPJE()  # Logar no site

        #################### Loguin####################################################
        i = 0
        while not status and i < 4:  # se não deu para logar  tentat de novo
            if self.browser is not None:
                self.browser.quit()  # FECHAR TUDO E REINICIAR
            status = self.loguinPJE()
        if i >= 4:
            raise Exception('NÃO DEU PARA LOGAR, ERRO AO LOGAR NOVAMENTE')

        ########################### ENTRAR NO PROCESSO NOVAMENTE#########################

        i = 0
        while not self.abrir_box_processo():  # abre a box para a pesquisa do processo
            if i >= 4:
                raise Exception('ABRIR A BOX DO PROCESSO')
            i += 1

        ################ BUSCA O PROCESSO NOVAMENTE E JA DEIXAR PRONTO PARA PEGAR #############
        i = 0
        while not (self.buscarProcessoAcervo(self.num)) and i < 4:  # tentar colocar o numero do processo na box, se tiver o processo já deixa na aba para pegar as informações
            self.fechaAba_e_voltaPrimeira()
            i += 1
        if i >= 4:
            raise Exception('NÃO DEU PARA ENTRAR NOS DADOS DO PROCESSO')

        return True



    ##### Metodos try são muito parecidos, mudam apenas os xpath########
    def try_erro_segredo_ou_sigilo(self):
        print('Erro ao pegar documentos de segredo ou sigilo, tentando recuperar')

        if self.reload(): # relogar na pagina

            wait = WebDriverWait(self.browser, 10)  # esperar  5  segundos até a página carregar
            wait.until(EC.invisibility_of_element_located((By.ID, '_viewRoot:status.start'))) # esperar a tabela carregar

            if self.parou_doc == 1:  # se tiver menos que dez documentos, não precisa buscar a box
                return True

            tam = self.browser.find_elements_by_xpath('//*[@id="processoTrfDocumentoMagistradoGrid"]/div/div[2]/form/table/tbody/tr[1]/td[5]/input')

            if len(tam) > 0:  # Se tem a box de passar de pagina
                tam[0].clear()
                tam[0].send_keys(str(self.parou_doc))  # coloca onde parou
                wait.until(EC.invisibility_of_element_located((By.ID, '_viewRoot:status.start')))
                return True

        return False


    ######################################TENTAR NÃO PARAR NA BUSCA DO PROCESSO, QUANDO DER ERRO TENTÃO RENICIAMOS ONDE PAROU#######
    def try_erro_documento(self):


        print('Erro ao pegar os documentos, tentar recuperar!')

        if self.reload(): # relogar de novo

            wait = WebDriverWait(self.browser, 10)  # esperar  5  segundos até a página carregar
            if self.parou_doc == 1: #  se tiver menos que dez documentos, não precisa buscar a box
                return True

            tam = self.browser.find_elements_by_xpath('//*[@id="processoDocumentoGridTab"]/div/div[2]/form/table/tbody/tr[1]/td[5]/input')
            if len(tam) > 0: # Se tem a box de passar de pagina
                tam[0].clear()
                tam[0].send_keys(str(self.parou_doc)) # coloca onde parou
                # print('colocando número que parou')
                wait.until(EC.invisibility_of_element_located((By.ID, '_viewRoot:status.start')))
                return  True


        return  False

    def vai_para_mov(self):

        self.browser.execute_script("window.scrollTo(0,0)")  # sobe a aba para poder cliclar nas guias
        self.browser.switch_to_window(self.browser.window_handles[1])  # se estiver na primeira
        self.browser.find_element_by_id('MovimentacoesId_lbl').click()  # IR PARA ABA DE MOVIMENTAÇÕES
        wait = WebDriverWait(self.browser, 10)  # esperar  5  segundos até a página carregar
        wait.until(EC.invisibility_of_element_located((By.ID, '_viewRoot:status.start')))  # esperar a barra de carregamento sum

    # DEU ALGUM PROBLEMA NA HORA DE PEGAR AS MOVIMENTAÇÕES ENTÃO ESSE METODO TENTARÁ REPARAR O ERRO
    def try_movimentacoes(self):

        self.reload()
        # IR PARA PAGINA DE MOVIMENTAÇÕES
        try:

           self.vai_para_mov()

        except:

           self.vai_para_mov()

        tam = self.browser.find_elements_by_xpath('//*[@id="movimentacaoListPanel_body"]/div/form/table/tbody/tr[1]/td[5]/input') # botão de input onde será pegado novamente

        if len(tam) > 0:
            tam[0].clear()
            tam[0].send_keys(self.parou_doc)
            wait = WebDriverWait(self.browser, 10)  # esperar  5  segundos até a página carregar
            wait.until(EC.invisibility_of_element_located((By.ID, '_viewRoot:status.start')))  # esperar a barra d



    def set_num_pross(self, num):
        self.num = num

    def get_Documentos(self,data_update, prc_id):

       # print('Data Doc:', data_update)
       list_documentos = []
       list_name_url = []

       try:
            flag = False
            wait = WebDriverWait(self.browser, 20)  # esperar  20  segundos até a página carregar
            wait.until(EC.invisibility_of_element_located((By.ID, 'movimentacaoListPanel'))) # Painel onde está a lista de documentos
            wait.until(EC.visibility_of_element_located((By.ID, 'processoDocumentoGridTabList:tb'))) # esperar lista de documentos apreces
            wait.until(EC.invisibility_of_element_located((By.ID, '_viewRoot:status.start')))



            self.browser.execute_script("window.scrollTo(0,120)") # descer para aparecer o botão para clicar para o proximo

            flag = self.get_list_doc(list_documentos, list_name_url,prc_id,data_update) #  Onde será pego todas as informações dos documentos
            self.parou_doc +=1 # Variavel para que se der erro voltar onde parrou


            # VERIFICAR SE EXISTE MAIS DE DEZ DOCUMENTOS PASSAR PARA PROXIMA PAGINA
            # Xpath do box que indica a quantidade de páginas
            xpathBox = '//*[@id="processoDocumentoGridTab"]/div/div[2]/form/table/tbody/tr[1]/td[5]/input'
            existePaginas = self.browser.find_elements_by_xpath(xpathBox) # pegando a barra se exitir de passagem



            if(len(existePaginas)> 0 ): # EXISTE O CAMPO DE PASSAR DE PAGINA
                existePaginas[0].location_once_scrolled_into_view # Colocar o elemento visível na tela
                pathFim = '//*[@id="processoDocumentoGridTab"]/div/div[2]/form/table/tbody/tr[1]/td[3]' # Mostra a quantidade de páginas de documentos existem
                atual = existePaginas[0].get_attribute('value')  # pagina atual das tabelas
                final = self.browser.find_element_by_xpath(pathFim).text # pagina final das tabelas

                #and (len(list_documentos)>0)
                if (int(atual) < int(final))  and not flag :  # AINDA TEM MAIS PARA VARRER , flag igual a false então não terminou

                      # print("Dentro do passar")
                      # self.browser.execute_script(
                      #     "window.scrollTo(0,185)")  # descer para aparecer o botão para clicar para o proximo
                      existePaginas[0].location_once_scrolled_into_view
                      try: # Tentar passar pela seta
                        xpathBotao =  '//*[@id="processoDocumentoGridTab"]/div/div[2]/form/table/tbody/tr[1]/td[4]' # Seta de passagem da página
                        self.browser.find_elements_by_xpath(xpathBotao)[0].click()
                      except:  # tenta colocar com o numero da box
                          box = self.browser.find_element_by_xpath(xpathBox)
                          box.clear() # Limpar
                          box.send_keys( (int(atual)+1)) # Colocar manualmente já que não não deu para passar
                          wait.until(EC.invisibility_of_element_located((By.ID, '_viewRoot:status.start')))

                      # Esperar a tabela atualizar
                      wait.until(EC.invisibility_of_element_located((By.ID, '_viewRoot:status.start')))
                      list_aux, list_name_url_aux = self.get_Documentos(data_update, prc_id)


                      list_documentos += list_aux
                      list_name_url +=  list_name_url_aux

            return list_documentos, list_name_url




       except: # Tenta voltar

            raise
            teste = self.try_erro_documento() # reloga na página e volta onde começou
            if teste:
                return  self.get_Documentos(data_update,prc_id)

            print('erro processo ao pegar a lista de documentos')
            return  None, None

    def estrair_data_string(self,string, sem_tratar = True):
        import re
        data_padrao = r'[0-9][0-9]/[0-9][0-9]/[0-9][0-9][0-9][0-9]'  # Padrão data
        hora_parao = r'[0-9][0-9]:[0-9][0-9]:[0-9][0-9]'
        data = re.findall(data_padrao, string)[0]  # Retorna um vetor com as datas encontradas na string
        data+=' '+ re.findall(hora_parao,string)[0]

        return Tools.treat_date(data) if sem_tratar==True else data
    def tipo_audiencia(self,type):
        aux1, aux2 = None, None
        if ('CONCILIACAO' in type and 'INSTRUCAO' in type and 'JULGAMENTO' in type) or 'UNA' in type:
            aux1 = 'UNA'

        elif 'INSTRUCAO' in type and 'JULGAMENTO' in type:
            aux1 = 'INSTRUCAO E JULGAMENTO'

        elif 'CONCILIACAO' in type:
            aux1 = 'CONCILIACAO'

        elif 'INSTRUCAO' in type:
            aux1 = 'INSTRUCAO'

        elif 'JULGAMENTO' in type:
            aux1 = 'JULGAMENTO'
        elif 'INICIAL' in type:
            aux1 = 'INICIAL'
        else:
            aux1 = None

        # TRATAR STATUS
        if 'NAO REALIZADA' in type:
            aux2 = 'NAO REALIZADA'

        elif 'CANCELADA' in type:
            aux2 = 'CANCELADA'

        elif 'REALIZADA' in type:
            aux2 = 'REALIZADA'

        elif 'CONCLUIDA' in type:
            aux2 = 'CONCLUIDA'

        elif 'REDESIGNADA' in type:
            aux2 = 'REDESIGNADA'

        elif 'REMARCADA' in type:
            aux2 = 'REMARCADA'

        elif 'DESIGNADA' in type:
            aux2 = 'DESIGNADA'

        elif 'MARCADA' in type:
            aux2 = 'MARCADA'

        elif 'PENDENTE' in type:
            aux2 = 'JULGAMENTO'

        return aux2, aux1

    # def separa_dados_audiencia(self,type): # Audiencia possui duas datas, a da postagem do acompanhamento e a data da audiencia
    #     type = Tools.remove_accents(type).upper()
    #     import re
    #     data_padrao = r'[0-9][0-9]/[0-9][0-9]/[0-9][0-9][0-9][0-9]'  # Padrão data
    #     hora_parao = r'[0-9][0-9]:[0-9][0-9]'
    #     data = re.findall(data_padrao, type) # Vetor de datas que contem na string
    #     hora = re.findall(hora_parao, type) # Vetor com as horas
    #     data1 = data[1] if len(data) > 1 else None  # Retorna um vetor com as datas encontradas na string
    #     if data1 is None:
    #         return False
    #     data1 += ' ' + hora[1]  # Aqui existe uma data para audiencia
    #     data1 = Tools.treat_date(data1) if len(data1)> 0 else None
    #     status,tipo = self.tipo_audiencia(type)
    #     data2 = self.estrair_data_string(type)
    #     if status == None and tipo == None:
    #         return False
    #     return (tipo,status,data1,None,data2)
    def tam_tab(self):
        return  len(self.browser.find_elements_by_xpath('//*[@id="movimentacaoList:tb"]/tr'))
    def get_linha(self,i):
        linha = self.browser.find_elements_by_xpath('//*[@id="movimentacaoList:tb"]/tr')

        return linha[i]
    def get_list_mov(self,lista_acp_download,lista_audiencias,prc_id,list_name_url,data_update):

            list_aux_d = []
            list_aux_a = []
            obj_download = []
            acp_pra_status = None
            flag = False

            wait = WebDriverWait(self.browser, 5)  # esperar  5  segundos até a página carregar
            wait.until(EC.invisibility_of_element_located((By.ID, '_viewRoot:status.start')))  # esperar a barra de carre
            tabela = self.browser.find_elements_by_xpath('//*[@id="movimentacaoList:tb"]/tr') # pegar a tabela# elementos da tabela, cada linha é uma classe
            list_aux_url = []
            print('>>', end="")
            i=0
            while i < self.tam_tab():
                try:

                    obj_download = []
                    linha = self.get_linha(i) # Pegar o elemento da tabela sempre atualizado

                    informacoes = str(linha.text)
                    informacoes = informacoes.split('\n') # As informações, uma linha inteira da tabela, quando faz um splite, contem duas linhas, a primeira é o id e o resto a informação da movimentaçaõ
                    #acp_numero  - Id do acompanhamento, acp_esp - informações da movimentação
                    acp_numero,acp_esp = informacoes
                    data = self.estrair_data_string(acp_esp)  # pega data das movimentações
                    acp_esp = acp_esp.replace(self.estrair_data_string(acp_esp,False),"") # Retirar a data do acompanhamento, que ele foi postado

                    if data_update != None and data <= data_update:
                        flag = True
                        break
                    lista_donwload = []

                    exiteDonw = linha.find_elements_by_tag_name('img') # Se existir Donloads
                    if len(exiteDonw)>0: # Os documentos são todos do tipo HTML
                        exiteDonw[0].click() # Cliclar para baixar
                        pra_nome = self.donwloadAcompanhamento(acp_numero)  # retorna o nome do download
                        obj_download.append(ProcessoArquivoModel(pra_prc_id=prc_id, pra_nome=pra_nome, pra_descricao=acp_esp))
                        acp_pra_status = True
                        list_aux_url.append((pra_nome, pra_nome))  # nome baixado, nome para renomear

                    if 'AUDIÊNCIA' in acp_esp.upper():
                        audiencia_dados = self.separar_dados_audiencia(acp_esp,data)
                        if audiencia_dados != False:
                            list_aux_a.append(audiencia_dados)

                    list_aux_d.append([AcompanhamentoModel(acp_numero=acp_numero, acp_esp=acp_esp
                                                            ,acp_data_cadastro=data, acp_prc_id=prc_id, acp_pra_status=acp_pra_status),obj_download])
                    i+=1
                    print(".",end='')

                except StaleElementReferenceException: # Elemento não esta atualizado
                    pass
                except:
                    raise

            lista_acp_download+= list_aux_d
            lista_audiencias += list_aux_a
            list_name_url += list_aux_url
            return flag


    def verifica(self, n_files, list_file_path, list_name_urls,prc_id, nome = None):

        err_down = self.wait_download(n_files)

        if not err_down:#not err_down: # se o download concluiu totalmente sem nehum erro
            # print('dentro if')
            arquivo  = set(os.listdir(self.path_download_prov)).difference(set(list_file_path))# difereça de dois conjunts
            # print('hduahdushadhsuadushauhdusauhduau')
            file_downloaded = arquivo.pop() # .replace('.pdf','') # pega o nome do arquivo que foi baixado

            # print('Nome donload: ', file_downloaded)
            nome = Tools.convert_base(str(datetime.now())) if nome != None else nome
            list_name_urls.append((nome, file_downloaded)) # Primeiro é o nome que quer renomear segundo o original, o primeiro não tem extensão
            # ext = file_downloaded.split('.')[-1].lower()
            nome = nome + '.pdf'
            #desc_file = file_downloaded.replace("." + ext, '')
            return  True, ProcessoArquivoModel(pra_prc_id=prc_id,pra_nome=nome,pra_descricao=file_downloaded)



        else:

            return  False, None

    def download_documentos(self, id, i):

        try:

            botaodownload = self.browser.find_element_by_xpath('/html/body/div[1]/div/div[1]/form/a/img')
            botaodownload.click()


            wait = WebDriverWait(self.browser, 5)  # esperar  5  segundos até a página carregar
            wait.until(EC.invisibility_of_element_located((By.ID, '_viewRoot:status.start')))# espera a barra de caregamento desaparcer


            boxdesmarca = self.browser.find_element_by_id('tbdownloadDocumentos:downloadDocumentosModal_checkAll')# caixa de desmarcar todos os documentos
            boxdesmarca.click()


            wait.until(EC.visibility_of_element_located((By.XPATH,'//*[@id="tbdownloadDocumentos:tb"]/tr')))

            tabeladonwload = self.browser.find_elements_by_xpath( '//*[@id="tbdownloadDocumentos:tb"]/tr') # pega a tabela listada com todos donwload
            # tabeladonwload = self.browser.find_elements_by_xpath('tr') # pegar todas as linhas da tabela

            # janela = self.browser.find_element_by_id('downloadDocumentosModalCDiv')

            # bot = self.browser.find_elements_by_xpath('//*[@id="resultadoSentencaInner"]/div[1]/div/form/div[2]/table/tbody/tr[2]/td/input[1]')  # botão de download
            # # self.browser.execute_script('arguments[0].onclick = "null"', bot[0])

            lis_name_urls = []

            x = '//*[@id="resultadoSentencaInner"]/div[1]/div/form/div[2]/table/tbody/tr[2]/td/input[1]'

            # j = 0 # começo da lista


            # for i in tabeladonwload:# procurar o elemento na tabela




            idtable = tabeladonwload[i].find_element_by_xpath('td[2]').text  #  id da linha atual

            self.browser.execute_script('document.getElementById("downloadDocumentosModalCDiv").style = "position: absolute; left: 200px; top: -80px; z-index: 9;";') # setar o style da pagina para ficar no centro


            if str(id) == str(idtable): # documento é obrigatório ter id

                tabeladonwload[i].find_element_by_xpath('td[1]').click() # cliclar na caixinha
                bot = self.browser.find_elements_by_xpath(x) # botão de download
                nome_arquivos = os.listdir(self.path_download_prov) # quantidade de elementos antes do donwload

                bot[0].click()  # clica para baixar
                acp_pra_status, obj_download = self.verifica(len(nome_arquivos),nome_arquivos,lis_name_urls)  # esperar o download concluir
                # deu certo o download


                return  acp_pra_status,obj_download,lis_name_urls


            # return False, None, lis_name_urls # não achou na busca
            return True
        except: # deu ruim não baixou

            return  False, None,[]



        #     print('id:', idtable)
        # print('numero de elemetos da tabela:', len(tabeladonwload))



    def new_linha(self, i):
        linha = self.browser.find_elements_by_xpath('//*[@id="processoDocumentoGridTabList:tb"]/tr')
        return linha[i]
    def get_list_doc(self,list_documentos, lis_name_urls,prc_id, data_update):

        try:
            validacao = ""
            grau = ""
            html = False
            wait = WebDriverWait(self.browser, 8)  # esperar  5  segundos até a página carregar
            wait.until(EC.invisibility_of_element_located((By.ID, '_viewRoot:status.start'))) # Esperar carregar os dados
            aux_list=[]
            flag = False

            xpath = '//*[@id="processoDocumentoGridTabList:tb"]/tr' # XPATH Linhas das tabelas dos documentos

            tabela = self.browser.find_elements_by_xpath(xpath)
            if len(tabela) > 0 :
                tabela[0].location_once_scrolled_into_view # Colocar visível na tela
            obj_download = []
            list_aux_url = []
            print(">>", end="")
            for i in  range(0,len(tabela),1):  # tabela com todos os elementos
                html = False
                obj_download = []
                informacoes = self.new_linha(i) # Quando passadas a linha para text cada informação da coluna 'td' são colocadas em uma linha
                linha = str(informacoes.text)

                linha = linha.split('\n') # Separar por queda de linha
                # quando é splitado as informações vem em ordem, de acordo com as tds, td[1], td[2] e assim por diante
                #Quando sliptado vem 5 linhas, o total de tds são 8, os 3 que faltam a td[4] e td[5] vem juntas e as outras duas tds são imagens, icones na tabela
                #validacao = td[8], acp_data_cumprimento = td[3] -date , acp_esp = td[4] + td[5], acp_numero = td[1]
                # td[4] é o nome do documento e td[5] é o tipo do documento
                # validação - Verificar na coluna se o documento está validado
                # acp_data_cumprimento - Data do acompanhamento
                #acp_numero - numero de id do acompanhamento passando para inteiro

                acp_numero,grau,acp_data_cumprimento,acp_esp,validacao = linha # Separando os dados de acordo com as linhas

                if "Excluido" in validacao: # Se o documento estiver sido excluido não pegar
                    continue

                acp_data_cumprimento =Tools.treat_date(acp_data_cumprimento) # Data do acompanhamento em formato data-time


                ############## Verificar se tem que pegar mais movimentações #########################

                if ( data_update != None ) and ( data_update >= acp_data_cumprimento ): # Verificar se ira pegar aquele acompanhamento
                    flag = True # Verificar se precisa pegar mais acompanhamentos
                    break


                if "Documento Sigiloso" in acp_esp: # Documento sigiloso não é possível pegar passar para o proximo
                    continue
                acp_tipo = 'DONWLOAD' # Todos esses documentos possui donwloads


                # Quando é pdf o documento possui um nome, quando é html o nome é 'Visualizar'
                #### Verificar qual tipo de arquivo é
                # XPaph é dos arquivos HTML
                busca_titulo = informacoes.find_elements_by_tag_name('img')

                # Se o titulo da primeira imagem  for visualizar então o documento é HTML
                html =  True if busca_titulo[0].get_attribute('title') == 'Visualizar' else False

                # FAZER UMA FUNÇÃO PARA FAZER ESSA ETAPA DE DOWNLOAD
                if html: # se for html o download
                    busca_titulo[0].click() # onde clica para abrir o documento
                    pra_nome = self.donwloadAcompanhamento(acp_numero)  # retorna o nome do download
                    pra_desc = pra_nome
                    obj_download.append(ProcessoArquivoModel(pra_prc_id=prc_id, pra_nome=pra_nome, pra_descricao=pra_desc))
                    acp_pra_status = True
                    list_aux_url.append((pra_nome, pra_nome))  # nome baixado, nome para renomear

                else:    # se for PDF
                    nome_arquivos = os.listdir(self.path_download_prov)  # quantidade de elementos antes do donwload
                    busca_titulo[0].click()
                    acp_pra_status, download = self.verifica(len(nome_arquivos), nome_arquivos,list_aux_url,prc_id,acp_numero)  # esperar o download concluir

                    obj_download.append(download)

                wait.until(EC.number_of_windows_to_be(2))
                self.browser.switch_to_window(self.browser.window_handles[-1])  # Selecionar a ultima página
                aux_list.append([AcompanhamentoModel(acp_numero=acp_numero, acp_data_cadastro=acp_data_cumprimento,
                                acp_esp=acp_esp, acp_tipo=acp_tipo,acp_pra_status = acp_pra_status), obj_download])
                print(".",end='')


            list_documentos += aux_list
            lis_name_urls   += list_aux_url
            return flag

        except Exception as Erro: # Laça exeção para dar um reload na função que chamou
            print("ERRO: ", Erro)
            sleep(60)
            raise

    def abrir_box_processo(self):

        try:

            self.browser.get(self.site_busca_acervo)  # pagina de busca do processo pelo acervo
            wait = WebDriverWait(self.browser, 8)  # esperar  5  segundos até a página carregar
            wait.until(EC.element_to_be_clickable((By.ID, 'leftAdvPnl_header')))  # ATÉ PODER SER CLICADO

            self.browser.find_element_by_id('leftAdvPnl_header').click()  # clicla para abrir o campo para procurar o processp

            wait.until(EC.visibility_of_element_located((By.XPATH,
                                                         '//*[@id="consultaProcessoAdvogadoForm:'
                                                         'numeroProcessoDecoration:numeroProcesso"]'))
                                                        )  # ATÉ PODER SER CLICADO, BOTÃO DE BUSCA
        # deu tudo certo
            return  True
        except:
            return  False # 'Erro na abertura da box para colocar o processo'




    def buscarProcessoAcervo(self,numero_processo):  # FUNÇÃO PARA BUSCAR O PROCESSO E JA ENTREGAR NA PÁGINA PARA FAZER A VAREDURRA

        try:



            self.num = numero_processo # salavr para tentar reparar erros durante a execução

            if (self.verificaBoxAcervo(numero_processo)): # se Conseguir colocar o numero corretamente no campo


                # print('box okay')
                self.browser.find_element_by_id('consultaProcessoAdvogadoForm:searchButon').click() # clicar em buscar

                wait = WebDriverWait(self.browser, 5)  # esperar  5  segundos até a página carregar
                wait.until(EC.invisibility_of_element_located((By.ID, '_viewRoot:status.start')))  # esperar a barra de carre

                xpathResult ='/html/body/div[5]/div/div/div[2]/div/table/tbody/tr[2]/td/table/' \
                             'tbody/tr/td/table/tbody/tr/td[2]/div/div[2]/div/div[2]/div[2]/span'

                wait.until(EC.visibility_of_element_located((By.XPATH,xpathResult ))) # ATÉ APARECER A MENSAGEM de QUANTOS ELEMENTOS APARECERAM


                resultados = self.browser.find_element_by_xpath(xpathResult).text # numeros de resultados encontrados


                resultados = resultados.replace(' ','') # tira as letras e pontos e deixa apenas numeros
                resultados = int(re.sub('[^0-9]', '', resultados)) # pega os resultados encontrados

                if resultados == 0:
                    return  True

                elif resultados > 0: # verificar se existe mais de uma aba
                    return self.procuraProcessoTable(numero_processo) # retorna com a aba de downloads do processo pronto para baixar
                    #self.get_Envolvidos()


                # return  True # deu algum problema na busca

            else:
                return False #'Preenchimento do campo do porcesso falhou!'

        except:

            return False # 'Erro na página de busca de processos!!'

    def get_audiencias(self):


        lista_audiencias = []
        try:
            #self.browser.find_element_by_id('tabProcessoAudiencia_lbl').click()

            self.browser.find_element_by_id('tabProcessoAudiencia_lbl').click() # para a pagina de audencia
            wait = WebDriverWait(self.browser, 5)  # esperar  5  segundos até a página carregar
            wait.until(EC.invisibility_of_element_located((By.ID, '_viewRoot:status.start')))

            self.browser.execute_script('return document.readyState')  # espera a página carregar
            wait = WebDriverWait(self.browser, 5)  # esperar  5  segundos até a página carregar
            wait.until(EC.visibility_of_element_located((By.ID, 'processoConsultaAudienciaGridList'))) # esperar a tabela aparecer
            i = 0
            while i < 2:      # tenta buscar os elementos da tas tabelas duas veze
                try:
                    lista_audiencias = self.pegaAudiencias()
                    break
                except:
                    i+=1
            if i >= 2: # não consegiu pegar todos elementos
                return  []

            return  lista_audiencias

        except:

            print('erro no metodo get_audiencias')
            return [] # erro

    def pegaAudiencias(self):
        list_adiencia = []

        # print('pasosu ')
        tabela = self.browser.find_element_by_xpath('//*[@id="processoConsultaAudienciaGridList:tb"]')  # procura a tabela
        tabela = tabela.find_elements_by_class_name('rich-table-row')
        #print('tam tabela: ', len(tabela))
        donwloads = []
        try:

            #print('passou dois')
            for i in tabela:

                data = Tools.treat_date(i.find_element_by_xpath('td[1]').text)

                instrucao = i.find_element_by_xpath('td[2]').text


                orgao = i.find_element_by_xpath('td[3]').text

                sala = i.find_element_by_xpath('td[4]').text
                status = i.find_element_by_xpath('td[5]').text

                # exiteDonw = i.find_elements_by_xpath('td[6]/span/div/div/div/form')
                # try:
                #     # print('temmmmmmmmm doonwload')
                #     exiteDonw[0].click()
                #     donwloads = self.donwloadAcompanhamento()
                #
                # except:
                #     donwloads = []

                # print(data, instrucao, orgao, sala, status)
                list_adiencia.append([data,instrucao,orgao,sala,status])

            return  list_adiencia
        except:
            print('erro  no método Pegar audiencias')

            return []

    def esperaID(self, id):

        wait = WebDriverWait(self.browser, 8)  # esperar a tabela aparecer para pegar informações
        wait.until(EC.visibility_of_element_located((By.ID, id)))
    def get_caracteristicas_do_processo(self):

        xpath = '//*[@id="caracteristicaProcessoViewViewView"]/div/div[3]/table/tbody/tr/td[{}]/span/div/span/div/div[2]'
        transitoJugado = None
        segredoJustica = None
        try:  # Tentar pegas as informações referente ao processo, se não der coloca none

            segredoJustica = False if self.browser.find_element_by_id(
                'segredoJusticaCletDecoration:segredoJusticaClet').text.upper() == "NÃO" else True
        except:
            try:
                segredoJustica = False if self.browser.find_element_by_xpath(
                    xpath.format('1')).text.upper() == "NÃO" else True  # pegando se é ou não segredo de justiça
            except:
                segredoJustica = None

        try:
            transitoJugado = \
            self.browser.find_elements_by_id('dataTransitoJulgadoCletDecoration:dataTransitoJulgadoClet')[0].text \
                if len(self.browser.find_elements_by_id(
                'dataTransitoJulgadoCletDecoration:dataTransitoJulgadoClet')) == 1 else None
        except:
            transitoJugado = None
            pass
        return  transitoJugado , segredoJustica
    def get_caracteristicas_proceso(self):


        try:
            wait = WebDriverWait(self.browser, 8)  # esperar a tabela aparecer para pegar informações
            # subir o scroll para aba audiencia aparecer para ser clicada
            aba_caracteristicas = self.browser.find_element_by_id('caracteristicaProcesso_lbl')
            self.browser.execute_script("window.scrollTo(0, 0)") # subir srcoll do mouse
            wait.until(EC.element_to_be_clickable((By.ID,'caracteristicaProcesso_lbl'))) # esperar o elemento ser clicavel

            self.browser.find_element_by_id('caracteristicaProcesso_lbl').click() # Ir para caracteristicas do processo

            wait.until(EC.invisibility_of_element_located((By.ID, '_viewRoot:status.start')))

            transitoJugado, segredoJustica = self.get_caracteristicas_do_processo()
            assunto=  self.get_assunto()

            dados = self.get_dados_processo(assunto) # retorna a classe ProcessoPlataformaModel

            dados.plp_segredo = segredoJustica

            return  dados

        except:

            try:
                self.reload()
                return  self.get_caracteristicas_proceso()
            except:
                return None



    def get_assunto(self):
        try:
            wait = WebDriverWait(self.browser, 5)  # esperar a tabela aparecer para pegar informações
            assuntos_table = self.browser.find_element_by_id('toggleAssuntosProc_header')  # abrir tabela de assuntos
            assuntos_table.location_once_scrolled_into_view  # Ficar visivel na tela
            assuntos_table.click()  # abrir a tabela
            wait.until(EC.invisibility_of_element_located((By.ID, '_viewRoot:status.start')))  # Esperar carregar a tabela

            setAssuntos = set()                                   #set para não colocar elementos repetidos
            self.esperaID('processoAssuntoListAbaProcesso:tb')
            tabela = self.browser.find_elements_by_id('processoAssuntoListAbaProcesso:tb')
            if len(tabela)<=0: # não encontrou a tabela,  não existe
                return  []

            tabela[0].location_once_scrolled_into_view # Ficar visivel na tela

            tabela = tabela[0].find_elements_by_xpath('tr') # pegar as linhas(trs) da tabela
            for i in tabela:
                i.location_once_scrolled_into_view
                principal = i.find_element_by_xpath('td[3]').text # linha
                linha = principal.split('/') # os assuntos são seprarados por barra
                for j in linha:
                    setAssuntos.add(j) # inserindo os assuntos no set

            assuntos = Tools.remove_accents(str(setAssuntos).replace("', '",'/')[2:-3]).upper()

            if len(assuntos)>500: # Adaptação para o banco de dados
                assuntos = assuntos[:500]
            return assuntos
        except:
            print('erro  no método get assuntos')
            return  None

    def get_dados_processo(self,assunto):

        wait = WebDriverWait(self.browser, 5)  # esperar a tabela aparecer para pegar informações
        wait.until(EC.invisibility_of_element_located((By.ID, '_viewRoot:status.start')))

        barra = self.browser.find_element_by_xpath('//*[@id="idAssuntoProcesso"]/div/div[1]/form/div[1]')# abre o campo de dados do processo
        barra.location_once_scrolled_into_view
        barra.click() # Abrir a tabela
        wait.until(EC.invisibility_of_element_located((By.ID, '_viewRoot:status.start')))

        campos_busca = ['numeroProcDecoration', 'dataAutuacaoDecoration','orgaoJulgadorDecoration',
                        'valorCausaDadosProcDecoration','dataDistribuicaoDadosProcDecoration','classeJudDecoration']

        lista_campos = []
        for i in  campos_busca:
            try: # as vezes o elemento não existe
                info_campo = str(self.browser.find_element_by_id(i).text) # Pegando o campo inteiro
                info_campo = info_campo.split('\n')[1:] # Tirando o primeiro elemento
                info_campo = ' '.join(info_campo)
            except:
                info_campo = None
                pass
            lista_campos.append(info_campo)

        print("LISTA: ", lista_campos)

        return ProcessoPlataformaModel(plp_assunto=assunto, plp_classe=lista_campos[5], plp_data_distribuicao=Tools.treat_date(lista_campos[4]),
                                       plp_data_transito_julgado=Tools.treat_date(lista_campos[1]) if lista_campos[1]!= None else None ,
                                       plp_localizado=True, plp_valor_causa=Tools.treat_value_cause(lista_campos[3]),
                                       plp_numero=re.sub('[^0-9]', '',lista_campos[0]), plp_vara=lista_campos[-1])



    def get_info_just_trabalho(self):

        try:

            campos = self.browser.find_elements_by_class_name('rich-stglpanel-marker')
            campos[2].click()  # fecha o campo de assuntos
            wait = WebDriverWait(self.browser, 5)  # esperar a tabela aparecer para pegar informações
            wait.until(EC.invisibility_of_element_located((By.ID, '_viewRoot:status.start')))
            campos[3].click()  # abre o campo de dados do processo

            wait.until(EC.invisibility_of_element_located((By.ID, '_viewRoot:status.start')))



            # self.esperaID('j_id1471:tb')

            xpaht='/html/body/div[3]/div/table/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr/td/div[5]/div/div/div/table/tbody/tr'
            wait = WebDriverWait(self.browser, 5)  # esperar a tabela aparecer para pegar informações
            wait.until(EC.visibility_of_element_located((By.XPATH, xpaht)))

            tabela = self.browser.find_elements_by_xpath(xpaht) #pegar a Tr das tabela
            l = ""

            for i in tabela:   # variando entre as linhas da tabela

               j = i.find_elements_by_xpath('td') # pegando os campos da tablea

               for k in j:
                   l+= Tools.remove_accents(k.text).upper() + '-' # separando por hífen


            return l

        except:
           print('erro  no método get_just_trabalho')


           return ""

    def tratamento_audiencias(self, lista_audiencias):

        lista_audiencias.reverse()
        lista_audiencias_organizadas = self.organizar_audiencias(lista_audiencias)
        lista_final = []
        lista_reserva = [i for i in lista_audiencias_organizadas]
        for audiencia in lista_audiencias_organizadas:
            self.link_audiencia(audiencia, lista_reserva, lista_final)
        for audiencia in lista_reserva:
            audiencia_model = AudienciaModel(aud_status=audiencia[0], aud_tipo=audiencia[1], aud_data=audiencia[3])
            lista_final.append(audiencia_model)

        arquivo = open('audiencia.txt', 'a')
        aux = ''
        for audiencia in lista_final:
            aux += audiencia.aud_status+ ';' + audiencia.aud_tipo + ';' + str(audiencia.aud_data) + '\n'
        arquivo.write(aux)
        arquivo.close()
        return lista_final


    def link_audiencia(self, audiencia, lista_reserva, lista_final):
        for _audiencia in lista_reserva:
            if audiencia[2] != _audiencia[2]:  # Data_prev
                if audiencia[1] == _audiencia[1]:  # Tipo
                    if ((_audiencia[0] == 'REALIZADA') or (_audiencia[0] == 'CANCELADA')) and (
                        audiencia[3].date() == _audiencia[3].date()):
                        audiencia_model = AudienciaModel(aud_status=_audiencia[0], aud_tipo=audiencia[1],
                                                         aud_data=_audiencia[3])
                        lista_final.append(audiencia_model)
                        if audiencia in lista_reserva:
                            lista_reserva.remove(audiencia)
                        if _audiencia in lista_reserva:
                            lista_reserva.remove(_audiencia)
                        return

    def organizar_audiencias(self, lista_audiencias):
        lista_audiencias_organizadas = []
        for audiencia in lista_audiencias:
            lista_audiencias_organizadas.append(
                [self.verifica_status(audiencia[0]), self.verifica_tipo(audiencia[0]), audiencia[1],
                 self.pega_data_prevista(audiencia[0])])
        return lista_audiencias_organizadas

    def pega_data_prevista(self, audiencia):
        # if '16/04/2019 12:53:38 - Audiência de instrução cancelada (07/06/2019 10:20:00 - Sala Principal - 29ª VT - 29ª VARA DO TRABALHO DE BELO HORIZONTE)
        data = audiencia[-16:]

        return Tools.treat_date(data)

    def verifica_tipo(self, audiencia):
        tipos = ('INSTRUCAO E JULGAMENTO', 'ENCERRAMENTO DE INSTRUCAO', 'INSTRUCAO', 'INICIAL', 'UNA')
        audiencia = audiencia.upper()
        audiencia = Tools.remove_accents(audiencia)
        for tipo in tipos:
            if tipo in audiencia:
                return tipo
        return 'Tipo desconhecido'

    def verifica_status(self, audiencia):
        status = ('REDESIGNADA', 'DESIGNADA', 'CANCELADA', 'REALIZADA')
        audiencia = audiencia.upper()
        audiencia = Tools.remove_accents(audiencia)
        for s in status:
            if s in audiencia:
                return s
        return 'Tipo desconhecido'

    def ir_para_documento(self):  # ir para a aba de documentos

        self.browser.execute_script("window.scrollTo(0, 0)")  # subir srcoll do mouse
        self.browser.find_element_by_id('informativoProcessoTrf_lbl').click()  # ir para pagina de documentos
        wait = WebDriverWait(self.browser, 7)  # esperar  5  segundos até a página carregar
        wait.until(EC.invisibility_of_element_located((By.ID, '_viewRoot:status.start')))  # esperar a barra de carregamento sumir
