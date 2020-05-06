import time
import win32ui
# import pyautogui
# from pywinauto.application import Application
import keyboard
import re
from time import sleep
import abc, os, re, shutil
from base64 import b64encode
from datetime import datetime
from urllib3.exceptions import *
from unicodedata import normalize
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Tools(metaclass=abc.ABCMeta):

    # EXTRAIR DATA ETRANSFORMAR NO FORMATO DO BANCO DE DADOS
    @staticmethod
    def extrair_date_string(string):
        # string= re.sub('[^a-zA-Z0-9-\t \n]', '', normalize('NFKD', string).encode('ASCII', 'ignore').decode('ASCII'))
        # a=input(string)
        data_padrao = r'[0-9][0-9]/[0-9][0-9]/[0-9][0-9][0-9][0-9]'  # Padrão data
        hora_parao_tipo_1 = r'[0-9][0-9]:[0-9][0-9]:[0-9][0-9]'
        hora_parao_tipo_2 = r'[0-9][0-9]:[0-9][0-9]'
        lista_hora_aux_1=re.findall(hora_parao_tipo_1, string)
        lista_hora_aux_2=re.findall(hora_parao_tipo_2, string)
        data = re.findall(data_padrao, string)[0]  # Retorna um vetor com as datas encontradas na string
        data += (' ' + (lista_hora_aux_1[0] if len(lista_hora_aux_1)>0 else lista_hora_aux_2[0]))
        return Tools.treat_date(data)
    # TRANSFORMAR AS DATAS NO FORMATO DO BANCO DE DADOS
    @staticmethod
    def treat_date(data):

        data = normalize('NFKD', data).encode('ASCII', 'ignore').decode('ASCII')
        data = data.lower()

        if data.find('/') >= 0 or data.find('-') >= 0:
            data = data.replace(' as ', ';').replace(' hora ', ';').replace(' ', ';').replace('/', ';').\
                replace('-', ';')
            aux = data.split(';')
            if len(aux) == 3:
                aux.append('0:0:0')
            dia, mes, ano, auxs_hrs = aux
        else:
            meses = {"janeiro": '01',"jan": '01',"january":'01',
                     "fevereiro": '02', "february": '02',"feb": '02',"fev":'02',
                     "marco": '03',"mar": '03',"march":'03',
                     "abril": '04', "april": '04',"abr": '04',"apr":'04',
                     "maio": '05', "mai": '05',"may": '05',
                     "junho": '06',"jun": '06',"june":'06',
                     "julho": '07',"jul": '07',"july":'07',
                     "agosto": '08', "august": '08', "aug": '08',"ago":'08',
                     "setembro": '09', "september": '09',"sep": '09',"set":'09',
                     "outubro": '10', "october": '10', "oct": '10',"out":'10',
                     "novembro": '11', "nov": '11',"november":'11',
                     "dezembro": '12', "december": '12', "dec": '12',"dez":'12'}
            data = data.replace(' de ', ';').replace(' as ', ';').replace(' hora ', ';').replace(' ', ';')\
                .replace('/', ';').replace('\t', ';')
            aux = data.split(';')
            if len(aux) == 3:
                aux.append('0:0:0')
            dia, mes, ano, auxs_hrs = aux
            if mes in meses.keys():
                mes = meses[mes]
            else:
                for i in meses.items():
                    if mes in i[0]:
                        mes = i[-1]
                        break

        if len(auxs_hrs.split(':')) == 3:
            hr, mt, seg = auxs_hrs.split(':')
            data_ = datetime(int(ano), int(mes), int(dia), int(hr), int(mt), int(seg))
            return data_
        elif len(auxs_hrs.split(':')) == 2:
            hr, mt = auxs_hrs.split(':')
            data_ = datetime(int(ano), int(mes), int(dia), int(hr), int(mt))
            return data_
        else:
            hr = auxs_hrs.split(':')
            data_ = datetime(int(ano), int(mes), int(dia), int(hr))

        return data_

    # TRANFORMA STRING EM VALORES DE MOEDA REAL
    @staticmethod
    def treat_value_cause(valor_causa):
        valor_causa =  normalize('NFKD', valor_causa).encode('ASCII', 'ignore').decode('ASCII')
        if valor_causa is None:
            return None
        valor_causa = re.sub('[a-z.A-Z$-/]', '', valor_causa)
        valor_causa = re.sub('[,]', '.', valor_causa)
        if  not len(valor_causa):
            return None
        return float(valor_causa)

    # RETIRAR QUALQUER FORMA DE ACENTUAÇÃO
    @staticmethod
    def remove_accents(txt):
        # return normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII')
        return txt

    # RETIRAR QUALQUER FORMA DE ACENTUAÇÃO E CARACTERE ESPECIAL EXCETO -
    @staticmethod
    def remove_caractere_especial(txt):
        return re.sub('[^a-zA-Z0-9-\t \n]', '', normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII'))

    @staticmethod
    def extrair_datas_da_string(txt):
        # txt= re.sub('[^a-zA-Z0-9-\t \n]', '', normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII'))


        data_padrao = r'[0-9][0-9]/[0-9][0-9]/[0-9][0-9][0-9][0-9]'  # Padrão data
        hora_parao = r'[0-9][0-9]:[0-9][0-9]'
        data = re.findall(data_padrao, txt)  # Retorna um vetor com as datas encontradas na string
        hora = re.findall(hora_parao, txt)  # Retorna um vetor com as horas encontradas na string
        return data,hora

    # CRIA UM DIRETÓRIO
    @staticmethod
    def new_path(folder_nome):
        try:
            os.makedirs(folder_nome, 0o777, False)
            return True
        except Exception:
            return False

    # DELETA UM DIRETÓRIO
    @staticmethod
    def delete_path(folder_nome):
        try:
            shutil.rmtree(folder_nome, ignore_errors=True)
            return True
        except Exception:
            return False
        # DELETA UM DIRETÓRIO

    # DELETA UM FILE
    @staticmethod
    def delete_file(folder_nome):

        dir = os.listdir(folder_nome)
        for file in dir:
            if 'crdownload' in file or 'CRDOWNLOAD'in file:
                # print("remove",file)
                os.remove(os.path.join(folder_nome, file))

    # RECORTA OS ARQUIVOS CONTIDOS EM UM DIRETÓRIO 'de' E COLA EM 'para'
    @staticmethod
    def transfer_and_rename_files(antigo_nome, nome_novo, de, para, log):
        ext = str(antigo_nome).split('.')[-1]
        try:
            nome_novo += "." + ext
            shutil.move(str(de) + "/" + str(antigo_nome), str(para) + "/" + nome_novo)
        except OSError as err:

            log.insert_log(str(err))
            # sleep(60*60)

    # CONVERTE A DATA NUMA STRING BASE64
    @staticmethod
    def convert_base(data):
        data = data.encode()
        data = b64encode(data)
        return data.decode()

    #VERIFICA SE A JANELA name ESTA ATIVA
    @staticmethod
    def WindowExists(class_name,name):
        try:
            win32ui.FindWindow(class_name,name)
        except win32ui.error:
            return False
        else:
            return True


    @property
    def enter_click(self):
        # app = pywinauto.application.Application().connect(title='Autorização')
        # window = app.top_window()
        # window.set_focus()
        # w, h = pyautogui.size()  # obtém o tamanho da tela
        # pyautogui.click((w / 2) - 32, (h / 2))  # Click com botão esquerdo na coordenada informada
        # sleep(60*60)
        # keyboard.press_and_release('\n')
        pass
    #CLICA NA JANELA DO CERTIFICADO
    @staticmethod
    def clicker_certificado_pje(segundos):
        try:
            t0=time.time()
            print(195)
            while time.time() - t0 < segundos and not Tools.WindowExists('SunAwtDialog','Autorização') :
                print(time.time() - t0)
                print(time.time() - t0 >= segundos)
                if time.time() - t0 >= segundos:
                   return False
            # app = Application().connect(title='Autorização')
            # window = app.top_window()
            # window.set_focus()
            # w, h = pyautogui.size()  # obtém o tamanho da tela
            # pyautogui.click((w/2) - 32, (h/2))  # Click com botão esquerdo na coordenada informada
            # sleep(1.5)
            # pyautogui.click((w / 2) - 32, (h / 2))  # Click com botão esquerdo na coordenada informada
            # # sleep(60*60)
            # keyboard.press_and_release('\n')
        except:
            print("Erro")
            return False

        return True
