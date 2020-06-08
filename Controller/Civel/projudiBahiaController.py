from Model.Civel.rootModel import RootModel
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


class projudiBahiaController(ProjudiModel):

    def __init__(self, site, mode_execute, SQL_Long, platform_id, platform_name, state, num_thread, link_consulta, flag,
                 grau=1):
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
        self.montar_dicionario()



    def login(self,user,password):

        # XPATHS
        id_bara_login = 'login'
        id_bara_senha = 'senha'
        xpath_btn_entrar = '//*[@id="formLogin"]/table/tbody/tr[6]/td[2]/a'
        name_frame = 'mainFrame'

        self.browser.get(self.site)

        # AGUARDA A BARRA DE LOGIN APARECER
        wait = WebDriverWait(self.browser, 10)
        wait.until(EC.visibility_of_element_located((By.ID, id_bara_login)))

        # INSERE O USUARIO E A SENHA
        self.browser.find_element_by_id(id_bara_login).send_keys(user)
        self.browser.find_element_by_id(id_bara_senha).send_keys(password)

        #QUEBRA O CAPTCHA
        self.captcha()

        input('Continuar?')

        print('inicio sleep')
        self.browser.execute_script("window.stop();")
        print('executou o stop')
        return True;
        # CLICA NO BOTÃO ENTRAR
        # self.navegador.find_element_by_xpath(xpath_btn_entrar).click()

    def find_process(self,num_processo, plp_codigo):
        input('gooo?')
        id_campo_busca = 'numeroProcesso'
        name_btn_submt = 'Buscar'
        xpath_open_process = '/html/body/div[1]/form[2]/table/tbody/tr[4]/td[2]/a'

        # ABRE A BUSCA DE PROCESSO
        self.browser.get(self.link_consulta)
        print('inicio sleep find')
        # self.browser.execute_script("window.stop();")
        print('executou o stop')

        wait = WebDriverWait(self.browser, 10)
        wait.until(EC.visibility_of_element_located((By.ID, id_campo_busca)))
        self.browser.find_element_by_id(id_campo_busca).send_keys(num_processo)

        # CLICA NO BTN SUBMETER PARA BUSCAR O PROCESSO
        wait = WebDriverWait(self.browser, 10)
        wait.until(EC.visibility_of_element_located((By.NAME, name_btn_submt)))
        self.browser.find_element_by_name(name_btn_submt).click()

        # CLICA PARA ABRIR O PROCESSO
        wait = WebDriverWait(self.browser, 10)
        wait.until(EC.visibility_of_element_located((By.XPATH, xpath_open_process)))
        self.browser.find_element_by_xpath(xpath_open_process).click()

        input('cabo')


############################################################################################
    def captcha(self):
        pass
    # VERIFICA SE A SESSÃO DO USUÁRIO ESTÁ ATIVA
    def check_session(self):
        return True

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
    def acomp_down_aud(self, prc_id, ult_mov, bool_2_grau_numero, full=False):
        pass

    # MONTAR PROCESSO-PLATAFORMA
    def montar_processo_plataforma(self, prc_id, prc_numero, flag, plp_codigo):
        pass

    # VARIFICAR SE O GRAU ALTEROU
    def validar_grau(self):
        pass


    def secret_of_justice(self):
        pass

    # VAlIDANDOS SE NUMERO DO PROCESSO CONTIDO NA PLATAFORMA E O MESMO CONTIDO NO SITE
    def validar_numero_plataforma(self, prc_numero):
        pass

