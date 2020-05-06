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
from Controller.Civel.projudiAmazonasController import projudiAmazonasController

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
