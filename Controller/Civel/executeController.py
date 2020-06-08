__autors__ = 'Wandersom Moura, Aurélio Santos, Paulo Henrique de Campos'
import threading
from time import time
from Model.Civel.esajModel import EsajModel
from Model.Civel.tucujurisModel import TucujurisModel
from Model.Civel.eprocModel import EprocModel
from Controller.Civel.pjeController import pjeController
from Controller.Civel.projudiMaranhaoController import projudiMaranhaoController
from Controller.Civel.projudiGoiasController import projudiGoiasController
from Controller.Civel.projudiAmazonasController import projudiAmazonasController
from Controller.Civel.projudiRoraimaController import projudiRoraimaController
from Controller.Civel.projudiParaController import projudiParaController
from Controller.Civel.projudiBahiaController import projudiBahiaController
from Controller.Civel.processumController import processumController
from Controller.Trabalhista.executeControllerTrabalhista import ExecutarTrabalhista

from time import  sleep

class PlaformaThreadController(threading.Thread):
    def __init__(self, platform_id, platform_name, state, flag, row_database,dict_plp_2grau, num_thread,grau):
        threading.Thread.__init__(self)
        self.platform_id = platform_id
        self.platform_name = platform_name
        self.state = state
        self.flag = flag
        self.row_database = row_database
        self.num_thread = num_thread
        self.grau=grau
        self.dict_plp_2grau=dict_plp_2grau
        self.obj=None

    def search(self, platform_id, platform_name, row_database,dict_plp_2grau):
        user = 'GO29320'
        password = 'vieiralopes'
        access = ['144.217.126.74', 'sa', 'becadv123']
        platform_id = platform_id
        platform_name = platform_name
        site = 'https://eproc{}.tjto.jus.br/eprocV2_prod_{}grau/'.format(self.grau,self.grau)
        tam = len(row_database)
        print('tam->',tam)
        cont = 0
        t0 = time()
        pi = 0
        pf = 100 if 100 <= tam else tam
        while True:
            obj = EprocModel(site=site, mode_execute=True, access=access,
                             platform_id=platform_id, platform_name=platform_name,
                             flag=self.flag,num_thread=self.num_thread)
            try:
                n_process = obj.search_process_to_update(user=user, password=password, row_database=row_database[pi:pf]
                                                         , dict_plp_2grau=dict_plp_2grau)
            except:
                raise
                n_process=100
                print("ERRO INESPERSA5555DO")
                raise

            cont += n_process
            tam = len(row_database)
            if n_process is not -1 and cont == tam or n_process is 0 or pf == tam:
                obj.__del__()
                break
            pi = pf
            pf = 100 + pf if 100 + pf <= tam else tam
        print('\nE-proc: TO |> processos gravados em: {} secs'.format(time() - t0).upper())

    def run(self):
        if self.state == 'TO':
                self.search_eproc_to(self.platform_id, self.platform_name, self.row_database,self.dict_plp_2grau)

class eprocThreadController(threading.Thread):
    def __init__(self, platform_id, platform_name, state, flag, row_database,dict_plp_2grau, num_thread,grau):
        threading.Thread.__init__(self)
        self.platform_id = platform_id
        self.platform_name = platform_name
        self.state = state
        self.flag = flag
        self.row_database = row_database
        self.num_thread = num_thread
        self.grau=grau
        self.dict_plp_2grau=dict_plp_2grau

    def search_eproc_to(self, platform_id, platform_name, row_database,dict_plp_2grau):
        user = 'GO29320'
        password = 'Vieiralopes52'
        access = ['144.217.126.74', 'sa', 'becadv123']
        platform_id = platform_id
        platform_name = platform_name
        site = 'https://eproc{}.tjto.jus.br/eprocV2_prod_{}grau/'.format(self.grau,self.grau)
        tam = len(row_database)
        print('tam->',tam)
        cont = 0
        t0 = time()
        pi = 0
        pf = 100 if 100 <= tam else tam
        while True:
            obj = EprocModel(site, True, access, platform_id, platform_name, self.flag, self.num_thread)
            try:
                n_process = obj.search_process_to_update(user, password, row_database[pi:pf], dict_plp_2grau)
            except:
                # raise
                n_process=100
                raise
                print("ERRO INESPERSADO")


            cont += n_process
            tam = len(row_database)
            if n_process is not -1 and cont == tam or n_process is 0 or pf == tam:
                obj.__del__()
                break
            pi = pf
            pf = 100 + pf if 100 + pf <= tam else tam
        print('\nE-proc: TO |> processos gravados em: {} secs'.format(time() - t0).upper())

    def run(self):
        if self.state == 'TO':
                self.search_eproc_to(self.platform_id, self.platform_name, self.row_database,self.dict_plp_2grau)

class tucujurisThreadController(threading.Thread):
    def __init__(self, platform_id, platform_name, state, flag, row_database, dict_plp_2grau, num_thread, grau):
        threading.Thread.__init__(self)
        self.platform_id = platform_id
        self.platform_name = platform_name
        self.state = state
        self.flag = flag
        self.row_database = row_database
        self.num_thread = num_thread
        self.grau = grau
        self.dict_plp_2grau = dict_plp_2grau

    def search_tucujuris_ap(self, platform_id, platform_name, row_database,dict_plp_2grau):
        user = '29320go'
        password = 'vieiralopes52'
        access = ['144.217.126.74', 'sa', 'becadv123', 'titanium_dev?charset=utf8']
        platform_id = platform_id
        platform_name = platform_name
        site = 'http://tucujuris.tjap.jus.br/tucujuris/'
        cont = 0
        t0 = time()
        tam = len(row_database)
        pi = 0
        pf = 100 if 100 <= tam else tam

        while True:
            obj = TucujurisModel(site=site,mode_execute= True,access= access,platform_id= platform_id,
                                           platform_name= platform_name,flag=self.flag,num_thread=self.num_thread)
            try:
                n_process = obj.search_process_to_update(user=user, password=password,row_database=row_database[pi:pf],
                                                         dict_plp_2grau=dict_plp_2grau)

            except:
                raise
                n_process=100
                print("ERRO INESPERADO")



            cont += n_process
            tam = len(row_database)
            if n_process is not -1 and cont == tam or n_process is 0 or pf == tam:
                obj.update_ple_data(ple_plt_id=self.platform_id, ple_uf=self.state)
                obj.__del__()
                break
            pi = pf
            pf = 100 + pf if 100 + pf <= tam else tam
        print('\nTucujuris: AP |> processos gravados em: {} secs'.format(time() - t0).upper())

    def run(self):
        if self.state == 'AP':
            self.search_tucujuris_ap(self.platform_id, self.platform_name, self.row_database,self.dict_plp_2grau)

class esajThreadController(threading.Thread):
    def __init__(self, platform_id, platform_name, state, flag, row_database, dict_plp_2grau, num_thread, grau) :
        threading.Thread.__init__(self)
        self.platform_id = platform_id
        self.platform_name = platform_name
        self.user = '965.864.191-15'
        self.password = 'vieiralopes'
        self.access = ['144.217.126.74', 'sa', 'becadv123', 'titanium_dev?charset=utf8']
        self.state = state
        self.flag = flag
        self.row_database = row_database
        self.num_thread = num_thread
        self.grau = grau
        self.dict_plp_2grau = dict_plp_2grau

    def serch_esaj(self,link_consulta,site):
        cont = 0
        t0 = time()
        tam = len(self.row_database)
        pi = 0
        pf = 100 if 100 <= tam else tam
        while True:
            obj = EsajModel(site=site,mode_execute=False, SQL_Long=self.access, platform_id=self.platform_id,
                            platform_name=self.platform_name,state=self.state,flag=self.flag, num_thread=self.num_thread
                            ,link_consulta=link_consulta,grau=self.grau)
            try:
                n_process = obj.search_process_to_update(user=self.user, row_database=self.row_database[pi:pf],
                                                         dict_plp_2grau=self.dict_plp_2grau ,password=self.password)
            except:
                n_process = 100
                print("ERRO INESPERSADO")
                raise


            cont += n_process
            tam = len(self.row_database)
            if n_process is not -1 and cont == tam or n_process is 0 or pf == tam:
                obj.update_ple_data(ple_plt_id=self.platform_id, ple_uf=self.state)
                obj.__del__()
                break
            pi = pf
            pf = 100 + pf if 100 + pf <= tam else tam
        print('\nE-saj: {} |> processos gravados em: {} secs'.format(self.state,time() - t0).upper())

    def run(self):

        link_site ={    ('AM',1):('https://consultasaj.tjam.jus.br/sajcas/login',"https://consultasaj.tjam.jus.br/cpopg/open.do?gateway=true"),
                        ('AM',2):('https://consultasaj.tjam.jus.br/sajcas/login','https://consultasaj.tjam.jus.br/cposgcr//open.do?gateway=true'),
                        ('MS',1):('https://esaj.tjms.jus.br/sajcas/login','https://esaj.tjms.jus.br/cpopg5/open.do?gateway=true'),
                        ('MS',2):('https://esaj.tjms.jus.br/sajcas/login','https://esaj.tjms.jus.br/cposg5//open.do?gateway=true'),
                        ('AC', 1):('https://esaj.tjac.jus.br/sajcas/login','https://esaj.tjac.jus.br/cpopg/open.do?gateway=true'),
                        ('AC', 2):('https://esaj.tjac.jus.br/sajcas/login','https://esaj.tjac.jus.br/cposg5//open.do?gateway=true')
                    }
        print("State->", self.state)
        print("Loguin", link_site[(self.state,self.grau)][0],"  Buca: ", link_site[(self.state,self.grau)][1])

        self.serch_esaj(site=link_site[(self.state,self.grau)][0],link_consulta=link_site[(self.state,self.grau)][1])

class pjeThreadController(threading.Thread):
    def __init__(self, platform_id, platform_name, state, flag, row_database, dict_plp_2grau, num_thread, grau,civel_trabalhista):
        threading.Thread.__init__(self)
        self.platform_id = int(platform_id)
        self.platform_name = platform_name
        self.state = state
        self.flag = flag
        self.row_database = row_database
        self.num_thread = num_thread
        self.grau = 1 if grau == 1 else 2
        self.dict_plp_2grau = dict_plp_2grau

        self.civel_trabalhista = civel_trabalhista
        print('   self.state = state',   self.state, "Cível:", civel_trabalhista)
    def mapeamento_trt(self):

        # estados vinculados com seus respectivos trt
        estados = {'RJ' : 1, 'SP':[2,15],'MG':3, 'RS':4, 'BA':5,'PE':6,'CE':7, 'AP':8,'PA':8,'PR':9, 'DF':10,'TO':10, 'AM':11, 'RR':11,'SC':12,
                   'PB':13,'AC':14,'RO':14,'MA':16,'ES':17, 'GO':18,'AL':19,'SE':20,'RN':21,'PI':22,'MT':23,'MS':24
                  }
        return estados[self.state]


    def search_pje(self,site,link_consulta):
        access = ['144.217.126.74', 'sa', 'becadv123', 'titanium_dev?charset=utf8']
        cont = 0
        t0 = time()
        tam = len(self.row_database)




        print("vivel :", self.civel_trabalhista)

        pi = 0
        pf =tam


        if int(self.civel_trabalhista) <= 1:
            print("Passou")
            #' site, mode_execute, access, platform_id, platform_name, flag, num_thread,state,link_consulta'

            obj = pjeController(site, False, access, self.platform_id, self.platform_name, self.flag,self.num_thread,self.state,link_consulta,
                                self.grau)

            try:
                n_process = obj.search_process_to_update(self.row_database[pi:pf],self.dict_plp_2grau)
            except Exception as Erro:
                raise
                n_process=1
                print(Erro)
                print("ERRO INESPERSADO : ", self.num_thread)


            cont += n_process
            tam = len(self.row_database)

            obj.update_ple_data(ple_plt_id=self.platform_id, ple_uf=self.state)
            obj.__del__()



        else:
            try:
                trt = self.mapeamento_trt()
                ex = ExecutarTrabalhista(trt)
                a = ex.varredura_processos(self.row_database, access,self.state)
            except Exception as Erro:
                print(Erro)


    def run(self):

        grau = 1 if 1 == self.grau else 2
        print("CIVEL TRABALHISTA:", self.civel_trabalhista)
        if int(self.civel_trabalhista) <= 1: # 1 é processos do pje cível
            link_site ={('DF',1):('https://pje.tjdft.jus.br/pje/login.seam','https://pje.tjdft.jus.br/pje/Processo/ConsultaProcesso/listView.seam'),
                        ('DF',2):('https://pje2i.tjdft.jus.br/pje/login.seam','https://pje2i.tjdft.jus.br/pje/Processo/ConsultaProcesso/listView.seam'),
                        ('MA',1):('https://pje.tjma.jus.br/pje/login.seam','http://pje.tjma.jus.br/pje/Processo/ConsultaProcesso/listView.seam'),
                        ('MA',2):('https://pje2.tjma.jus.br/pje2g/login.seam','https://pje2.tjma.jus.br/pje2g/Processo/ConsultaProcesso/listView.seam'),
                        ('PA',1):('http://pje.tjpa.jus.br/pje/login.seam','http://pje.tjpa.jus.br/pje/Processo/ConsultaProcesso/listView.seam'),
                        ('PA',2):('http://pje.tjpa.jus.br/pje-2g/login.seam','http://pje.tjpa.jus.br/pje-2g/Processo/ConsultaProcesso/listView.seam'),
                        ('RO',1):('https://pje.tjro.jus.br/pg/login.seam','https://pjepg.tjro.jus.br/Processo/ConsultaProcesso/listView.seam'),
                        ('RO',2):('https://pje.tjro.jus.br/sg/login.seam','https://pjesg.tjro.jus.br/Processo/ConsultaProcesso/listView.seam'),
                        ('BA',1):('https://pje.tjba.jus.br/pje-web/login.seam','https://pje.tjba.jus.br/pje-web/Processo/CadastroPeticaoAvulsa/peticaoavulsa.seam'),
                        ('BA',2): ('https://pje2g.tjba.jus.br/pje-web/login.seam','https://pje2g.tjba.jus.br/pje-web/Processo/CadastroPeticaoAvulsa/peticaoavulsa.seam')

                        }
            print("State->", self.state)
            print("Loguin", link_site[(self.state,grau)][0],"  Buca: ", link_site[(self.state,grau)][1])
                            # ' platform_id, platform_name, row_database,dict_plp_2grau,site,link_consulta,state'
            self.search_pje(link_site[(self.state,grau)][0],link_site[(self.state,grau)][1])
        else: # aqui é trabalhista

            self.search_pje(None, None)

class projudiThreadController(threading.Thread):
    def __init__(self, platform_id, platform_name, state, flag, row_database, dict_plp_2grau, num_thread, grau):
        threading.Thread.__init__(self)
        self.platform_id = platform_id
        self.platform_name = platform_name
        self.state = state
        self.flag = flag
        self.row_database = row_database
        self.num_thread = num_thread
        self.grau = grau
        self.dict_plp_2grau = dict_plp_2grau

    def search_projudi_ma(self, platform_id, platform_name, row_database,dict_plp_2grau):
        user = 'A29320GO'
        password = 'vieiralopes52'
        access = ['144.217.126.74', 'sa', 'becadv123', 'titanium_dev?charset=utf8']
        platform_id = platform_id
        platform_name = platform_name
        site = 'https://projudi.tjma.jus.br/projudi/'
        cont = 0
        t0 = time()
        tam = len(row_database)
        pi = 0
        pf = 100 if 100 <= tam else tam

        while True:
            obj = projudiMaranhaoController(site, False, access, platform_id, platform_name, self.flag, self.num_thread)
            obj = None
            try:
                n_process = obj.search_process_to_update(user, password, row_database[pi:pf],dict_plp_2grau)
            except:
                n_process = 100
                print("ERRO INESPERSADO")

            cont += n_process
            tam = len(row_database)
            if n_process is not -1 and cont == tam or n_process is 0 or pf == tam:
                obj.update_ple_data(ple_plt_id=self.platform_id, ple_uf=self.state)
                obj.__del__()
                break
            pi = pf
            pf = 100 + pf if 100 + pf <= tam else tam
        print('\nProjudi: MA |> processos gravados em: {} secs'.format(time() - t0).upper())

    def search_projudi_go(self, platform_id, platform_name, row_database,dict_plp_2grau):
        user = '96586419115'
        password = 'megs10'
        access = ['144.217.126.74', 'sa', 'becadv123', 'titanium_dev?charset=utf8']
        platform_id = platform_id
        platform_name = platform_name
        site = 'https://projudi.tjgo.jus.br/'
        cont = 0
        t0 = time()
        tam = len(row_database)
        pi = 0
        # pf É A QUANTIDADE DE PROCESSOS VARIDOS POR LOTE
        pf = 100 if 100 <= tam else tam
        # pf = tam

        while True:
            obj = projudiGoiasController(site=site, mode_execute=True,access= access, platform_id=platform_id,
                                         platform_name= platform_name,flag= self.flag, num_thread=self.num_thread,
                                         grau=self.grau)
            try:
                n_process = obj.search_process_to_update(user=user, password=password, row_database=row_database[pi:pf],
                                                         dict_plp_2grau=dict_plp_2grau)
            except:
                n_process = 100
                print("ERRO INESPERSADO")
                raise


            cont += n_process
            tam = len(row_database)
            if n_process is not -1 and cont == tam or n_process is 0 or pf == tam:
                obj.update_ple_data(ple_plt_id=self.platform_id, ple_uf=self.state)
                obj.__del__()
                break
            pi = pf
            pf = 100 + pf if 100 + pf <= tam else tam
        print('\nProjudi: GO |> processos gravados em: {} secs'.format(time() - t0).upper())

    def search_projudi_am(self, platform_id, platform_name, row_database,dict_plp_2grau):
        user = 'go29320'
        password = 'vieiralopes52'
        access = ['144.217.126.74', 'sa', 'becadv123', 'titanium_dev?charset=utf8']
        platform_id = platform_id
        platform_name = platform_name
        site = 'https://projudi.tjam.jus.br/projudi/usuario/logon.do?actionType=inicio&r='
        cont = 0
        t0 = time()
        tam = len(row_database)
        pi = 0
        pf = 100 if 100 <= tam else tam

        while True:
            obj = projudiAmazonasController(site, True, access, platform_id, platform_name, self.flag, self.num_thread)
            try:
                n_process = obj.search_process_to_update(user, password, row_database[pi:pf],dict_plp_2grau)
            except Exception as Erro:



                raise
                n_process=100
                print("ERRO INESPERSADO")

            obj.update_ple_data(ple_plt_id=self.platform_id, ple_uf=self.state)
            cont += n_process
            tam = len(row_database)
            if n_process is not -1 and cont == tam or n_process is 0 or pf == tam:
                obj.update_ple_data(ple_plt_id=self.platform_id, ple_uf=self.state)
                obj.__del__()
                break
            pi = pf
            pf = 100 + pf if 100 + pf <= tam else tam
        print('\nProjudi: AM |> processos gravados em: {} secs'.format(time() - t0).upper())

    def search_projudi_rr(self, platform_id, platform_name, row_database,dict_plp_2grau):
        user = '96586419115'
        password = 'vieiralopes52'
        access = ['144.217.126.74', 'sa', 'becadv123', 'titanium_dev?charset=utf8']
        platform_id = platform_id
        platform_name = platform_name
        site = 'https://projudi.tjrr.jus.br/projudi/usuario/logon.do?actionType=inicio&r='
        cont = 0
        t0 = time()
        tam = len(row_database)
        pi = 0
        pf = 100 if 100 <= tam else tam
        while True:
            obj = projudiRoraimaController(site, False, access, platform_id, platform_name, self.flag, self.num_thread)
            try:
                n_process = obj.search_process_to_update(user, password, row_database[pi:pf],dict_plp_2grau)
            except:
                raise
                n_process = 100

                print("ERRO INESPERSADO")

            cont += n_process
            tam = len(row_database)
            if n_process is not -1 and cont == tam or n_process is 0 or pf == tam:
                obj.update_ple_data(ple_plt_id=self.platform_id, ple_uf=self.state)
                obj.__del__()
                break
            pi = pf
            pf = 100 + pf if 100 + pf <= tam else tam
        print('\nProjudi: RR |> processos gravados em: {} secs'.format(time() - t0).upper())

    def search_projudi_pa(self, platform_id, platform_name, row_database,dict_plp_2grau):
        user = 'wilker.lopes'
        password = 'vieiralopes52'
        access = ['144.217.126.74', 'sa', 'becadv123', 'titanium_dev?charset=utf8']
        platform_id = platform_id
        platform_name = platform_name
        site = 'https://projudi.tjpa.jus.br/projudi/Logout'
        cont = 0
        t0 = time()
        tam = len(row_database)
        pi = 0
        pf = 100 if 100 <= tam else tam

        while True:
            obj = projudiParaController(site, False, access, platform_id, platform_name, self.flag, self.num_thread)
            try:
                n_process = obj.search_process_to_update(user, password, row_database[pi:pf],dict_plp_2grau)
            except:
                raise
                n_process = 100
                print("ERRO INESPERSADO")

            cont += n_process
            tam = len(row_database)
            if n_process is not -1 and cont == tam or n_process is 0 or pf == tam:
                obj.update_ple_data(ple_plt_id=self.platform_id, ple_uf=self.state)
                obj.__del__()
                break
            pi = pf
            pf = 100 + pf if 100 + pf <= tam else tam
        print('\nProjudi: PA |> processos gravados em: {} secs'.format(time() - t0).upper())

    def search_projudi_ba(self, platform_id, platform_name, row_database,dict_plp_2grau):
        user = '17476BA'
        password = '123456?'
        access = ['144.217.126.74', 'sa', 'becadv123', 'titanium_dev?charset=utf8']
        platform_id = platform_id
        platform_name = platform_name
        site = 'https://projudi.tjba.jus.br/projudi/Logout'
        link_consulta = 'https://projudi.tjba.jus.br/projudi/buscas/ProcessosQualquerAdvogado'
        cont = 0
        t0 = time()
        tam = len(row_database)
        pi = 0
        pf = 100 if 100 <= tam else tam

        while True:
            obj = projudiBahiaController(site=site,mode_execute= False, SQL_Long=access, platform_id=platform_id,
                                         platform_name=platform_name, flag=self.flag, num_thread=self.num_thread,
                                         state= self.state,grau= self.grau,link_consulta=link_consulta)
            try:
                n_process = obj.search_process_to_update(user, password, row_database[pi:pf],dict_plp_2grau)
            except:
                raise
                n_process = 100
                print("ERRO INESPERSADO")

            cont += n_process
            tam = len(row_database)
            if n_process is not -1 and cont == tam or n_process is 0 or pf == tam:
                obj.update_ple_data(ple_plt_id=self.platform_id, ple_uf=self.state)
                obj.__del__()
                break
            pi = pf
            pf = 100 + pf if 100 + pf <= tam else tam
        print('\nProjudi: PA |> processos gravados em: {} secs'.format(time() - t0).upper())


    def run(self):
        if self.state == 'AM':
            if self.grau == 1:
                self.search_projudi_am(self.platform_id, self.platform_name, self.row_database,self.dict_plp_2grau)
            elif self.grau == 2:
                self.search_projudi_am(self.platform_id, self.platform_name, self.row_database)

        elif self.state == 'GO':
                self.search_projudi_go(self.platform_id, self.platform_name, self.row_database,self.dict_plp_2grau)

        elif self.state == 'MA':
            if self.grau == 1:
                self.search_projudi_ma(self.platform_id, self.platform_name, self.row_database,self.dict_plp_2grau)
            elif self.grau == 2:
                self.search_projudi_ma(self.platform_id, self.platform_name, self.row_database)

        elif self.state == 'RR':
            if self.grau == 1:
                self.search_projudi_rr(self.platform_id, self.platform_name, self.row_database,self.dict_plp_2grau)
            elif self.grau == 2:
                self.search_projudi_rr(self.platform_id, self.platform_name, self.row_database)

        elif self.state == 'PA':
            if self.grau == 1:
                self.search_projudi_pa(self.platform_id, self.platform_name, self.row_database,self.dict_plp_2grau)
            elif self.grau == 2:
                self.search_projudi_pa(self.platform_id, self.platform_name, self.row_database)

        elif self.state == 'BA':
                self.search_projudi_ba(self.platform_id, self.platform_name, self.row_database,self.dict_plp_2grau)


class processumThreadController(threading.Thread):
    def __init__(self, platform_id, platform_name, row_database, dict_acp_arq, num_thread):
        threading.Thread.__init__(self)
        self.platform_id = platform_id
        self.platform_name = platform_name
        self.row_database = row_database
        self.dict_acp_arq = dict_acp_arq
        self.num_thread = num_thread

    def search_processum(self, platform_id, platform_name, row_database, dict_acp_arq):
        user = "80227548"
        password = "M@rcelo25#"
        access = ['144.217.126.74', 'sa', 'becadv123', 'titanium_dev?charset=utf8']
        platform_id = platform_id
        platform_name = platform_name
        site = 'https://ww3.vivo-base.com.br/processumweb/principalPadrao.jsf'

        tam = len(row_database)
        cont = 0
        t0 = time()
        pi = 0
        pf = 100 if 100 <= tam else tam
        while True:
            t1 = time()
            obj = processumController(site, True, access, platform_id, platform_name, self.num_thread)
            try:
                n_process = obj.search_process(user, password, row_database[pi:pf], dict_acp_arq)
            except:
                n_process=100
                print("ERRO INESPERSADO")
                # raise


            cont += n_process
            tam = len(row_database)
            if n_process is not -1 and cont == tam or n_process is 0 or pf == tam:
                # obj.update_ple_data(ple_plt_id=self.platform_id, ple_uf=self.state)
                obj.__del__()
                break
            pi = pf
            pf = 100 + pf if 100 + pf <= tam else tam
            print('\n Processum |> {} processos gravados em: {} secs'.format(n_process, time() - t1).upper())

        print('\n Processum |> {} processos gravados em: {} secs'.format(cont, time() - t0).upper())

    def run(self):
        self.search_processum(self.platform_id, self.platform_name, self.row_database, self.dict_acp_arq)
