from sqlalchemy import *
from Model.toolsModel import *
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import ArgumentError, InterfaceError, OperationalError

Base = declarative_base()

class ProcessoTable(Base):
    __tablename__ = "processo"
    prc_id = Column(Integer, primary_key=True, autoincrement=True)
    prc_sequencial = Column(VARCHAR(15))
    prc_numero = Column(VARCHAR(30))
    prc_carteira = Column(INTEGER)
    prc_estado = Column(VARCHAR(2))
    prc_parte_ativa = Column(VARCHAR(50))
    prc_parte_passiva = Column(VARCHAR(50))
    prc_objeto1 = Column(VARCHAR(80))
    prc_objeto2 = Column(VARCHAR(80))
    prc_objeto3 = Column(VARCHAR(80))
    prc_objeto4 = Column(VARCHAR(80))
    prc_data_cadastro = Column(DATETIME)
    prc_area = Column(INTEGER)
    prc_apto_pgto = Column(BOOLEAN)
    prc_penhora = Column(BOOLEAN)
    prc_responsavel = Column(INTEGER)


class ProcessoPlataformaTable(Base):
    __tablename__ = "processo_plataforma"

    plp_id = Column(Integer, primary_key=True, autoincrement=True)
    plp_prc_id = Column(INTEGER)
    plp_plt_id = Column(INTEGER)
    plp_numero = Column(VARCHAR(40))
    plp_status = Column(NVARCHAR(30))
    plp_comarca = Column(NVARCHAR(30))
    plp_serventia = Column(NVARCHAR(150))
    plp_juizo = Column(VARCHAR(150))
    plp_fase = Column(NVARCHAR(55))
    plp_diligencia = Column(NVARCHAR(55))
    plp_vara = Column(NVARCHAR(250))
    plp_filtro = Column(BOOLEAN)
    plp_penhora = Column(BOOLEAN)
    plp_valor_causa = Column(NUMERIC)
    plp_valor_condenacao = Column(NUMERIC)
    plp_classe = Column(VARCHAR(100))
    plp_assunto = Column(NVARCHAR(500))
    plp_processo_origem = Column(NVARCHAR(30))
    plp_data_distribuicao = Column(DATETIME)
    plp_data_transito_julgado = Column(DATETIME)
    plp_codigo = Column(VARCHAR(120))
    plp_segredo = Column(BOOLEAN)
    plp_efeito_suspensivo = Column(BOOLEAN)
    plp_prioridade = Column(BOOLEAN)
    plp_localizado = Column(INTEGER)
    plp_migrado = Column(BINARY)
    plp_grau = Column(INTEGER)
    plp_data_update = Column(DATETIME)


class ParteTable(Base):
    __tablename__ = "parte"
    prt_id = Column(INTEGER, primary_key=True, autoincrement=True)
    prt_nome = Column(VARCHAR(100))
    prt_cpf_cnpj = Column(VARCHAR(20))
    prt_busca = Column(BINARY)


class ProcessoParteTable(Base):
    __tablename__ = "processo_parte"
    ppt_id = Column(INTEGER, primary_key=True, autoincrement=True)
    ppt_id = ppt_id
    ppt_prc_id = Column(INTEGER)
    ppt_plp_id = Column(INTEGER)
    ppt_prt_id = Column(INTEGER)
    ppt_tipo = Column(VARCHAR(20))
    ppt_polo = Column(VARCHAR(10))


class ResponsavelTable(Base):
    __tablename__ = "responsavel"
    rsp_id = Column(INTEGER, primary_key=True, autoincrement=True)
    rsp_nome = Column(VARCHAR(255))
    rsp_tipo = Column(VARCHAR(15))
    rsp_oab = Column(VARCHAR(15))


class ProcessoResponsavelTable(Base):
    __tablename__ = "processo_responsavel"
    prr_id = Column(INTEGER, primary_key=True, autoincrement=True)
    prr_prc_id = Column(INTEGER)
    prr_plp_id = Column(INTEGER)
    prr_rsp_id = Column(INTEGER)
    prr_polo = Column(VARCHAR(20))


class AudienciaTable(Base):
    __tablename__ = "audiencia"
    aud_id = Column(INTEGER, primary_key=True, autoincrement=True)
    aud_prc_id = Column(INTEGER)
    aud_plp_id = Column(INTEGER)
    aud_usr_id = Column(INTEGER)
    aud_data = Column(DATETIME)
    aud_tipo = Column(VARCHAR(50))
    aud_status = Column(VARCHAR(50))
    aud_obs = Column(VARCHAR(150))


class AcompanhamentoTable(Base):
    __tablename__ = "acompanhamento"
    acp_id = Column(INTEGER, primary_key=True, autoincrement=True)
    acp_prc_id = Column(INTEGER)
    acp_plp_id = Column(INTEGER)
    acp_tipo = Column(NVARCHAR(200))
    acp_esp = Column(NVARCHAR(1000))
    acp_data_cumprimento = Column(DATETIME)
    acp_data_evento = Column(DATETIME)
    acp_data_prazo = Column(DATETIME)
    acp_data_cadastro = Column(DATETIME)
    acp_data = Column(DATETIME)
    acp_pra_status = Column(BOOLEAN)
    acp_numero = Column(INTEGER, nullable=False)


class ArquivoTable(Base):
    __tablename__ = "processo_arquivo"
    pra_id = Column(INTEGER, primary_key=True, autoincrement=True)
    pra_prc_id = Column(INTEGER)
    pra_acp_id = Column(INTEGER)
    pra_nome = Column(VARCHAR(255))
    pra_descricao = Column(VARCHAR(255))
    pra_url = Column(VARCHAR(100))
    pra_erro = Column(INTEGER)


class CarteiraTable(Base):
    __tablename__ = "carteira"
    crt_id = Column(INTEGER, primary_key=True, nullable=False)
    crt_nome = Column(VARCHAR(50))


class PlataformaEstadoTable(Base):
    __tablename__ = "plataforma_estado"
    ple_id = Column(INTEGER, primary_key=True, autoincrement=True)
    ple_plt_id = Column(INTEGER)
    ple_uf = Column(VARCHAR(2))
    ple_login = Column(VARCHAR(30))
    ple_senha = Column(VARCHAR(30))
    ple_data = Column(DATETIME)


class SQL:

    # CONSTRUTOR DA CLASSE SQL
    def __init__(self, host=None, user=None, password=None):
        """Contrutor recebe os paramentros para conectar com o banco de dados, ao instaciar a classe SQL, conecta-se ao banco de dados, com as informações
        passadas por parametro."""

        # INFORMAÇÕES DO BANCO DE DADOS PARA CONECTAR AO BANCO
        self.host = host
        self.user = user
        self.password = password
        self.cont = 0


        self.conn = create_engine("mssql+pyodbc://" + user + ":" + password + "@titanium_dev",
                                  fast_executemany=False).connect()


        self.metadata = MetaData(bind=self.conn)
        self.session = Session(bind=self.conn)


    # DESTRUTOR DA CLASSE SQL
    def __del__(self):
        """Desconetar do banco de dados"""

        try:
            self.conn.close()
        except

    # PROCURA PELOS PROCESSOS NO BANCO DE DADOS PARA ATUALIZAÇÃO
    def search_process_for_update(self, state, platform, grau=1, area=1):
        """Função para busca do processos para varrer"""

        dict_plp_2_grau = {}

        join = 'left' if int(grau) == 1 else 'inner'

        q = "SELECT prc_numero, prc_id, prc_estado, plp_status, cadastro, plp_codigo, plp_data_update," \
            " plp_id, plp_numero,plp_localizado, CASE WHEN plp_data_update is null THEN 0 ELSE 1 END AS novo FROM processo" \
            " {} join processo_plataforma on plp_prc_id = prc_id and plp_plt_id = {} and plp_grau = {}" \
            " OUTER APPLY (select top 1 acp_plp_id,acp_data_cadastro as cadastro from acompanhamento " \
            " where acp_plp_id=plp_id order by acp_data_cadastro desc) acp" \
            " inner join plataforma_estado on ple_uf = '{}' and ple_plt_id = {} and ple_area = {}" \
            " WHERE (plp_localizado is null or plp_localizado > 0) and (plp_data_update<=ple_data or plp_data_update is null) and prc_estado = '{}' and  (prc_removido is null or prc_removido = 0) " \
            "  and len(prc_numero) > 12 and prc_area = {} order by plp_id".format(join, str(platform), str(grau)
                                                                                  , str(state), str(platform),
                                                                                  str(area), str(state), str(area))

        # EXECULTAR A QUERRY E PEGAR O RETRONO DO BANCO
        dados_busca = self.conn.execute(q).fetchall() # OS DADOS SÃO RETORNADOS EM TUPLAS
        resultado_banco = list(dados_busca) # PASSAR ESSAS TUPLAS PARA LISTA, CADA POSSIÇÃO DA LISTA É UMA TUPLA RETORNADA DO BANCO

        # QUANDO O PROCESSO MESMO PROCESSO ESTÁ NO SEGUNDO GRAU, PEGAR ELE PARA NÃO SER INSERIDO NOVAMENTE
        if grau == 1:
            dict_plp_2_grau = self.procurar_plp_2grau(resultado_banco)

        return resultado_banco, dict_plp_2_grau

    # PROCURA PELOS PROCESSUM NO BANCO DE DADOS PARA ATUALIZAÇÃO
    def procurar_plp_2grau(self, resultado_banco):
        """Função para pegar os numeros dos processos que estão no primeiro e segundo grau, essa função é utilizada quando a busca é do primeiro grau,
        para não adicionar mais de uma vez o processo no seegundo grau"""

        lista_de_prcid = "" # LISTA QUE TERÁ TODOS OS PRC_ID DOS PROCESSOS PARA BUSCA
        dic_plp_2_grau = {} # DICIONÁRIO COM A CHAVE PLP_PRC_ID E CONTEÚDO COMO PLP_NUMERO

        tam_resultado_banco = len(resultado_banco) # TAMANHO PARA VERIFICAR SE PRECISARÁ ADICIONAR VIRGULA OU NÃO
        contador = 1
        for linhas in resultado_banco:
        #LINHAS SÃO AS LINHAS RETORNADAS DO BANCO, NA POSIÇÃO DE NUMERO 1 ESTÁ O PRC_ID, PEGAR ELES PARA FAZER UMA BUSCA NO BANCO

            if linhas[1] != None: # SE EXISTIR PRCID PARA AQUELE PROCESSO
                lista_de_prcid+= str(linhas[1])# ADICIONAR NA LISTA PARA SER BUSCADO
                lista_de_prcid += "," if contador != tam_resultado_banco else ""
            contador+=1


        querry_busca = 'SELECT plp_prc_id,plp_numero FROM processo_plataforma ' \
            'WHERE plp_grau = 2 and plp_prc_id  in ({})'.format(lista_de_prcid)
        list_aux = list(self.conn.execute(querry_busca).fetchall())

       # MONTAR O DICIONARIO A PARTIR DA LISTA AUXILIAR QUE É A BUSCA DO BANCO

        for linhas_banco in list_aux:

            if linhas_banco[0] in dic_plp_2_grau.keys(): # VERIFICAR SE JÁ EXISTE A CHAVE COM PLP_PRC_ID
                dic_plp_2_grau[linhas_banco[0]].append(linhas_banco[-1])
            else: # SE NÃO EXISTIR, CRIAR A CHAVE E INSERIR O DADO NA LISTA
                dic_plp_2_grau[linhas_banco[0]] = []
                dic_plp_2_grau[linhas_banco[0]].append(linhas_banco[-1])


        return dic_plp_2_grau


    def montar_diconario_inserir(self,objeto):
        """funcção para montar um dicionario a partir de um objeto para inserir no banco de dados"""
        dicionario = {}
        campos_objeto = objeto.__dict__
        for atributo in campos_objeto.keys():  # VERIFICAR SE EXISTE CAMPOS NONE, SE NÃO FOR NONE PEGAR OS ATRIBUTOS

            if campos_objeto[atributo] != None:  #TIRAR OS CAMPOS NONE PARA INSERIR NO BANCO
                dicionario[atributo] = campos_objeto[atributo]
        return dicionario

    def inserir_plp_2_grau(self,plp_2_grau):
        """Função para inserir processo no segundo grau, quando é feita a varredura e é identificado que o processo também está no segundo grau,
        inserir o processo no banco indicando que é do segundo grau"""
        if len(plp_2_grau) == 0:
            return
        campos_inserir = []
        for plp in plp_2_grau:
            aux = self.montar_diconario_inserir(plp)
            campos_inserir.append(aux)
        self.session.bulk_insert_mappings(ProcessoPlataformaTable, campos_inserir) # PREPARAR A QUERRY PARA INSERIR NO BANCO DE DADOS
        self.session.commit()

    def insert_process(self, obj, log, list_name_urls, platform, state, root, plp_id=None):
        """Função para inserir ou fazer update de dados coletados na varredura"""

        #SEPARAR OS DADOS PARA INSERIR OU ATUALIZAR
        processo_plataforma = obj[0]
        lista_de_partes = obj[1]
        lista_de_responsavel = obj[2]
        list_de_audiencia = obj[3]
        lista_de_acompanhamentos = obj[4]
        list_plp_2_grau = obj[6]
        prc_id = processo_plataforma.plp_prc_id

        # print("tamanho lista de partes:",len(lista_de_partes))
        # print("tamanho lista de reposavel:", len(lista_de_responsavel))
        # print("tamanho lista de audiencia:", len(list_de_audiencia))
        # print("tamanho lista de acompamnhamentos:", len(lista_de_acompanhamentos))


        ######################INSERT/UPDATE PROCESSE PLATAFORMA##########################################################
        if plp_id == None: # SE O PLP ID É NONE ENTÃO NUNCA FOI VARRIDO ESSE PROCESSO, ENTÃO É UMA INSERÇÃO

            plp_id = self.inserir_atualizar_processo_plat(processo_plataforma) # INSERIR OU ATUALIZAR O PROCESSO PLATAFORMA
        else: # Atualizar o processo plataforma
            processo_plataforma.plp_id = plp_id
            self.inserir_atualizar_processo_plat(processo_plataforma)

        ######################## INSERIR PLP_2_GRAU CASO SEJA############################################################
        #("Plp_inserido:", plp_id)
        plp_aux = plp_id
        self.inserir_plp_2_grau(list_plp_2_grau)

        ####################INSERIR ACOMPANHAMENTOS######################################################################

        self.inserir_acompanhamentos(lista_de_acompanhamentos,prc_id,plp_id,platform,state) # INSERIR OS ACOMPANHAMENTOS
        root.transfer_files(state=state, list_name_urls=list_name_urls, plp_id=plp_id, log=log)# TRANSFERIR OS ARQUIVOS PARA A PASTA

        #################### INSERIR AS AUDIENCIAS#######################################################################

        self.inserir_atualizar_audiencia(list_de_audiencia,plp_aux)

        ################### INSERIR AS PARTES ###########################################################################

        self.inserir_partes_banco(lista_de_partes,prc_id,plp_id)

        ################## INSERIR RESPONSÁVEL###########################################################################
        self.inserir_responsavel_banco(lista_de_responsavel,prc_id,plp_id)
        print("\n\n")
        #input("CONFERIR")




    def inserir_atualizar_processo_plat(self,processo_plataforma):
        """Função para inseriri ou atualizar caso já exista o proesso plataforma na base, é passado os dados do processo plataforma"""

        processo_plataforma.plp_data_update = datetime.now() # ATUALIZAR A DATA
        campos_inserir_plp = [] # PARA INSERIR DEVE CONTER UMA LISTA DE DICIONÁRIO

        dict_processo_plataforma = self.montar_diconario_inserir(processo_plataforma)  # MONTAR O DICONÁRIO PARA INSERIR NO BANCO DE DADOS

        campos_inserir_plp.append(dict_processo_plataforma) # COLOCANDO O OBJETO QUE SERÁ INSERIODO

        if processo_plataforma.plp_id == None: # SE O PLP_ID É NONE ESSE PROCESSO NUNCA FOI VARRIDO, É A PRIMEIRA VEZ, ENTÃO É INSERIDO NO BANCO
            # PASSAR O PROCESSO PLATAFORMA PARA DICONÁRIO, E O QUE FOR NONE EXCLUIR


            # INSERIR O PROCESSO NO BANCO E PEGAR O PLP_ID

            self.session.bulk_insert_mappings(ProcessoPlataformaTable, campos_inserir_plp, return_defaults=True) # RETORNAR A CHAVE QUANDO INSERIR
            #print("Session:", campos_inserir_plp[0])
            self.session.commit()
            # COMO É APENAS UM A SER INSERIDO PEGAR NA PRIMIERA PROSIÇÃO
            plp_id_inserido = campos_inserir_plp[0]['plp_id']
            return plp_id_inserido
        else:
            # FAZER UPDATE DO PROCESSO PLATAFORMA, DATA plp_data_update
            self.session.bulk_update_mappings(ProcessoPlataformaTable,campos_inserir_plp) # FAZ O FILTRO PELO PLP_ID
            self.session.commit()



    def inserir_acompanhamentos(self, lista_de_acompanhamentos,prc_id,plp_id,plataforma,estado):
        """funcao para inserir os acompanhamentos, é passado uma lista de tupla, a primeira posicao é o objeto acompanhamento
        a segunda posicao é a lista de donwloads daquele acompanhamento"""

        lista_de_acompanhamentos.sort(key=lambda a: int(a[0].acp_numero)) # ORDENAR A LISTA DE ACOMPANHAMENTO PARA INSERIR NO BANCO NA ORDEM
        lista_inserir_acomp = [] # LISTA DE DICIONÁRIO, CADA POSIÇÃO DESSA LISTA E UM DICIONÁRIO DO OBJETO ACOMPANHAMENTO PARA INSERI NO BANCO
        lista_arquivo_model = [] # LISTA DE DOWNLOADS DOS ACOMPANHAMENTOS

        lista_acp_id = [] # LISTA DOS ACP_ID QUE FORAM INSERIDOS

        # CADA POSICAO DA LISTA É COMPOSTO POR UMA TUPLA, CADA POSICAO DA TUPLA CONTÉM UM OBJETO ACOMPANHAMENTO E A LISTA DE DOWLOADS
        for acompanhamento in lista_de_acompanhamentos:

            # SETAR AS CHAVES EM CADA ACOMPANHAMENTO
            acompanhamento[0].acp_plp_id = int(plp_id)
            acompanhamento[0].acp_prc_id = int(prc_id)
            #INSERIR A DATA DE INSERÇÃO NO BANCO
            acompanhamento[0].acp_data = datetime.now()

            lista_inserir_acomp.append(self.montar_diconario_inserir(acompanhamento[0])) # MONTA O DICIONÁRIO DO OBJETO PARA INSERIR NO BANCO DE DADOS
            lista_arquivo_model.append(acompanhamento[1]) # COLOCANDO OS PROCESSO ARQUIVO MODEL

        self.session.bulk_insert_mappings(AcompanhamentoTable, lista_inserir_acomp, return_defaults=True) # INSERIR E RETONAR A CHAVE,
        self.session.commit()

        cont = 0
        # PEGAR LISTA DE ACP_ID QUE FORAM INSERIDOS
        for acomp in lista_inserir_acomp:
            lista_acp_id.append(acomp['acp_id'])

            cont+=1

        self.inserir_processo_arquivo(lista_acp_id,lista_arquivo_model,plp_id,prc_id,plataforma,estado)





    def inserir_processo_arquivo(self,lista_acp_id,lista_processo_arquivo,plp_id,prc_id,platform,state):

        # MONTAR PROCESSO ARQUIVO PARA INSERIR NO BANCO
        # UM ACOMPANHAMENTO, ACP_ID, PODE TER VÁRIOS DOWNLOADS, OU SEJA UMA LISTA DE DOWLOADS
        lista_dicionarios = [] # LISTA QUE RECEBERÁ

        for acp_id, lista_donwload in zip(lista_acp_id,lista_processo_arquivo): # PASSAR PELOS ACOMPANHAMENTOS

            for processoArquivo in lista_donwload:

                processoArquivo.pra_prc_id = prc_id # SETANDO AS CHAVES
                processoArquivo.pra_acp_id = acp_id
                processoArquivo.pra_plp_id = plp_id
                # SETAR O CAMINHO DO ARQUIVO

                processoArquivo.pra_url = 'Downloads/{}/{}/{}/{}'.format(state, platform, plp_id, processoArquivo.pra_nome)
                lista_dicionarios.append(processoArquivo.__dict__) # TRANSFORMAR O OBJETO EM DICIONÁRIO PARA A INSERÇÃO

        if len(lista_dicionarios)>0:
            self.session.bulk_insert_mappings(ArquivoTable,lista_dicionarios) # PREPAPRAR PARA INSERIR NO BANCO DE DADOS
            self.session.commit()


    def buscar_audiencia_banco(self,plp_id):
        """Função para selecionar as adiência de um processo que está já está inserida no banco, a busca e feita pelo plp_id,
        a audiencia está relacionada com um processo. A função retorna um vetor, onde cada posição do vetor e uma audiência"""

        querry_busca = "SELECT aud_prc_id,aud_plp_id,aud_usr_id,aud_tipo,aud_data,aud_status,aud_obs,aud_id FROM audiencia WHERE aud_plp_id = {}".format(plp_id) # QUERRY DE BUSCA DE TODAS AS AUDIENCIAS
        resultado_banco = self.conn.execute(querry_busca)

        return  list(resultado_banco.fetchall()) # RESULTADO DO BANCO EM FORMATO DE LISTA

    def compara_audiencia(self, obj_audiencia, tupla_audiencia):
        """Função para comparar as audiencias coletadas e as que estão no banco de dados"""
        aud_tipo = tupla_audiencia[3] # tipo de audiencia
        aud_data = tupla_audiencia[4]
        aud_status= tupla_audiencia[5]
        aud_obs = tupla_audiencia[6]
        #comparar os objetos
        # SE O TIPO E A DATA FOREM IGUAIS ENTÃO É A MESMA AUDIÊNCIA, SE O SATUS ALTERAR MUDAR NO BANCO
        igual = obj_audiencia.aud_tipo == aud_tipo and obj_audiencia.aud_data == aud_data # SE A AUDIÊNCIA É IGUAL QUE ESTÁ NO BANCO
        status_update =  obj_audiencia.aud_status != aud_status  # VERIFICAR SE É DIFERENTE PARA FAZER UPDATE
        return  igual,status_update

    def inserir_atualizar_audiencia(self,lista_audiencias,plp_id):
        """Função para inserir ou atualizar audiência, caso a audiencia esteja no banco, apenas atualizar se necessário, caso não esteja
        inserir no banco. A lista de audiência não deve ser vazia"""

        #print("Plp AUDIÊNCIA", plp_id)
        audiencias_banco = self.buscar_audiencia_banco(plp_id) # BUSCAR AS AUDIENCIAS DESSO PROCESSO
        #print("Audiencias Banco:",audiencias_banco)
        # CADA ELEMENTO DA LISTA RETORNADO DO BANCO É UMA LISTA DE TUPLA, ONDE CADA TUPLA CONTEM:
        # aud_prc_id , aud_plp_id, aud_usr_id, aud_tipo, aud_data, aud_status,aud_obs,aud_id RESPECTIVAMENTE
        lista_inserir_banco = []
        lista_update = [] # LISTA DE AUDIENCIA QUE FARÁ UPDATE

        if len(audiencias_banco) > 0 : # EXISTEM AUDIÊNCIAS DESSE PROCESSO NO BANCO
            #VERIFICAR SE AS AUDIENCIAS JÁ ESTÃO DE ACORDO NO BANCO
            for audiencia in lista_audiencias:

                for tupla_audiencia in audiencias_banco:
                    igual, status_update = self.compara_audiencia(audiencia,tupla_audiencia)
                    if not igual: # SE NÃO ESTIVER NO BANCO COLOCAR NA LISTA DE INSERÇÃO
                        audiencia.aud_plp_id = plp_id # SETAR A CHAVE
                        lista_inserir_banco.append(audiencia.__dict__)
                        break

                    elif status_update: # VERIFICAR SE É PARA FAZER UPDATE, E SE O STATUS MUDOU
                        audiencia.aud_id = tupla_audiencia[-1] # PEGAR O ID DA AUDIENCIA
                        audiencia.aud_plp_id = plp_id
                        lista_update.append(audiencia.__dict__)
                        break

        else: # NÂO POSSUI NEHUMA AUDIENCIA NO BANCO
            for audiencia in lista_audiencias: # SETAR O plp_id
                audiencia.aud_plp_id = plp_id
                lista_inserir_banco.append(audiencia.__dict__)

        if len(lista_inserir_banco) > 0: # TEM AUDIENCIAS PARA INSERIR NO BANCO DE DADOS
                self.session.bulk_insert_mappings(AudienciaTable,lista_inserir_banco,return_defaults=true) # PREPARAR PARA INSERIR
                #print("Lista inserir Adiencia:",lista_inserir_banco)
                self.session.commit()
        if len(lista_update) > 0:
            self.session.bulk_update_mappings(AudienciaTable,lista_update)
            self.session.commit()

    def montar_processo_parte(self,prc_id,prt_id,plp_id,polo):
        """Função para montar um processo parte. O processo parte é um diconário para inserção"""
        polo = 'PASSIVO' if polo == 'Passivo' or 'Passiva' in polo  else 'ATIVO'

        processo_parte = {
                            'ppt_prc_id': prc_id,
                            'ppt_prt_id':prt_id,
                            'ppt_plp_id':plp_id,
                            'ppt_polo':polo
                         }
        return  processo_parte

    def montar_processo_responsavel(self,prc_id,rsp_id,plp_id,polo):
        """Função para montar um processo responsavél """

        processo_responsavel = {
                                    'prr_prc_id':prc_id,
                                    'prr_rsp_id':rsp_id,
                                    'prr_plp_id':plp_id
                               }
        #  SE FOR UM JUIZ ENTÃO ELE NÃO TEM POLO
        if polo != None: #SE NÃO FOR UM JUIZ
            polo = 'PASSIVO' if polo == 'Passivo' or 'Passiva' in polo else 'ATIVO'
            processo_responsavel['prr_polo'] = polo

        return processo_responsavel # OBJETO PARA A INSERÇÃO NO BANCO DE DADOS



    def inserir_partes_banco(self, lista_de_partes,prc_id,plp_id):
        """Função para inserir as partes no banco de dados, verificar se as partes já foram iseridas, se houve alguma alteração,
        e atualizar isso no banco."""

        partes_dicionario = [] # LISTA PARA INSERIR PARTES NO BANCO, CASO NÃO EXISTA NO BANCO

        for parte, polo in lista_de_partes:
            #LISTA DE PARTES É UMA TUPLA, A PRIMEIRA POSIÇÃO TEM UM OBJETO PARTE MODEL, A SEGUNDA SE É ATIVA OU PASSIVA, SE FOR NONE É UM JUÍZ
            prt_id = None
            #VERIFICAR SE JÁ EXISTE NO BANCO
            parte_insert = []
            #prt_id, prt_nome, prt_cpf_cnpj,ppt_prt_id -> ordem dos campos da busca
            busca_banco = self.select_prt_db(prc_id,parte.prt_cpf_cnpj,parte.prt_nome)
            #print("busca banco parte: prc_id: {}, cpf/cpnj: {}, nome:{} \n Resultado: {}".format(prc_id,parte.prt_cpf_cnpj,parte.prt_nome,busca_banco))

            if len(busca_banco) == 0: # SE FOR ZERO NÃO EXISTE NO BANCO
                #INSEIRI NO BANCO E PEGAR A CHAVE PRIMÁRIA
                parte_insert.append(parte.__dict__)
                self.session.bulk_insert_mappings(ParteTable, parte_insert,return_defaults=True)  # INSERIR E RETONAR A CHAVE,
                self.session.commit()
                prt_id = parte_insert[0]['prt_id']
                aux = self.montar_processo_parte(prc_id, prt_id, plp_id, polo)  # MONTAR PARTE PARA INSERIR
                partes_dicionario.append(aux)  # COLOCAR NA LISTA PARA INSERIR

            else: # Já EXITE NO BANCO
                # verificar se já existe o vinculo no banco
                ppt_prt_id = busca_banco[0][-1]
                if ppt_prt_id == None:
                    prt_id = busca_banco[0][0] # PEGA A CHAVE JÁ QUE EXISTE
                    aux = self.montar_processo_parte(prc_id, prt_id, plp_id, polo)  # MONTAR PARTE PARA INSERIR
                    partes_dicionario.append(aux)  # COLOCAR NA LISTA PARA INSERIR




        if len(partes_dicionario) > 0:
            self.session.bulk_insert_mappings(ProcessoParteTable, partes_dicionario)
            self.session.commit()

    def inserir_responsavel_banco(self,lista_reponsavel,prc_id,plp_id):
        """Função para inserir reponsável no banco de dados, se caso não existir no banco de dados"""

        lista_inserir_banco = [] # LISTA DE DICIONÁRIOS PARA INSEIRI RESPONSÁVEL NO BANCO

        for responsavel, polo in lista_reponsavel: # PASSAR SOBRE A LISTA DE RESPONSAVEL E VERIFICAR SE JÁ NÃO EXISTE NO BANCO

            resposavel_insert = [] # LISTA AUXILIAR PARA INSERIR RESPONSÁVEL CASO NÃO EXISTA NO BANCO
            # o select rsp retorna : rsp_id, prr_rsp_id,  respectivamente
            busca_banco = self.select_rsp_db(prc_id,responsavel.rsp_nome,responsavel.rsp_oab)
            #print("Busca banco responsavel: prc_id: {}, nome: {}, oab: {} \n Resultado: {} ".format(prc_id,responsavel.rsp_nome,responsavel.rsp_oab,busca_banco))
            if len(busca_banco) == 0:  # SE FOR ZERO NÃO EXISTE NO BANCO
                # INSERIR RESPONSÁVEL NA TABELA
                resposavel_insert.append(responsavel.__dict__)
                self.session.bulk_insert_mappings(ResponsavelTable,resposavel_insert,return_defaults=True) # PREPARAR PARA INSERIR NO BANCO
                self.session.commit()
                rsp_id = resposavel_insert[0]['rsp_id'] # PEGAR A CHAVE QUE FOI INSERIDA
                aux = self.montar_processo_responsavel(prc_id,rsp_id,plp_id,polo)
                lista_inserir_banco.append(aux) # COLOCAR NA LISTA PARA INSERÇÃO
            else: # CHEGOU AQUI ENTÃO JÁ EXISTE NO BANCO DE DADOS

                # VERIFICAR SE PRR_RSP_ID É NULO
                prr_rsp_id = busca_banco[0][-1]
                if prr_rsp_id == None:
                    rsp_id = busca_banco[0][0] # Pegar a chave da tabela responsavel
                    aux = self.montar_processo_responsavel(prc_id,rsp_id,plp_id,polo) # Montar o processo resposável para
                    lista_inserir_banco.append(aux) # Colocar na lista para inserir

        # Ligar as tabelas
        if len(lista_inserir_banco) > 0:
            self.session.bulk_insert_mappings(ProcessoResponsavelTable,lista_inserir_banco)











                # INSERIR NOVOS PROCESSOS_PLATAFORMA NO BANCO DE DADOS
    # def insert_process(self, obj, log, list_name_urls, platform, state, root, plp_id=None):
    #     plp_id_pk = plp_id
    #
    #     plp = obj[0]
    #     list_prt = obj[1] # LISTA DE PARTES
    #     list_rsp = obj[2] # LISTA DE RESPONSAVEIS
    #     list_aud = obj[3] # LISTA DE AUDIENCIA
    #     list_acp_pra = []
    #     list_plp_2_grau = obj[6]
    #     for acp_files in obj[4]:
    #         list_acp_pra.append(acp_files)
    #
    #     t0 = time.time()
    #
    #
    #     if plp_id is None:  # VERIFICA SE É UM NOVO ELEMENTO NA TABELA
    #
    #         # INSERÇÃO DE DADOS NA TABELA processo_plataforma
    #         plp.plp_data_update = datetime.now()
    #         list_item = {i: j for i, j in plp.__dict__.items() if j is not None}
    #         print("list item ")
    #         print(list_item)
    #         input("Pa")
    #         plp_id_pk = self.conn.execute(ProcessoPlataformaTable.__table__.insert(),
    #                                       [list_item]).inserted_primary_key[0]
    #
    #         print('Inserção na tabela processo_plataforma!')
    #     else:  # SENAO APAGA AS RELAÇÕES ENTRE PARTES E RESPONSÁVEIS PARA ATUALIZÁ-LAS
    #         self.delete_db(plp.plp_prc_id)
    #         # self.delete_db(plp.plp_prc_id)
    #
    #         print('Atualização de elemento no banco de dados!')
    #     # print('plp:', time.time() - t1)
    #     prc_id_pk = plp.plp_prc_id
    #     # PREPARAÇÃO DE DADOS PARA INSERÇÃO NA TABELA processo_plataforma
    #     plp_list_dict = []
    #     for plp_2_grau in list_plp_2_grau:
    #         list_item = {i: j for i, j in plp_2_grau.__dict__.items() if j is not None}
    #         plp_list_dict.append(list_item)
    #
    #     # INSERÇÃO DE DADOS NA TABELA processo_plataforma
    #     if len(list_plp_2_grau):
    #
    #         print("LISTA ")
    #         self.session.bulk_insert_mappings(ProcessoPlataformaTable, plp_list_dict)
    #         self.session.commit()
    #
    #         print('Inserção na tabela "processo_plataforma" !')
    #
    #
    #     # PREPARAÇÃO DE DADOS PARA INSERÇÃO NA TABELA acompanhamento
    #     acp_list_dict = []
    #     list_item_pra = []
    #     tam_pra_list_dict = 0
    #     tam_list_acp_pra = len(list_acp_pra) - 1
    #
    #     for acp_pra in list_acp_pra:
    #         print(f"acp_numero {acp_pra[0].acp_numero} ")
    #
    #     list_acp_pra.sort(key=lambda a: int(a[0].acp_numero))
    #
    #     for acp_pra in list_acp_pra:
    #         acp_pra[0].acp_plp_id = int(plp_id_pk)
    #         acp_pra[0].acp_prc_id = prc_id_pk
    #         acp_pra[0].acp_data = datetime.now()
    #
    #         list_item_acp = {i: j for i, j in acp_pra[0].__dict__.items() if j is not None}
    #         tam_pra_list_dict += len(acp_pra[1])
    #
    #         list_item_pra.append(acp_pra[1])
    #         acp_list_dict.append(list_item_acp)
    #         # INSERÇÃO DE DADOS NA TABELA acompanhamento e processo_arquivo
    #         if len(acp_list_dict) % 100 == 0 or list_acp_pra.index(acp_pra) == tam_list_acp_pra:
    #
    #             self.session.bulk_insert_mappings(AcompanhamentoTable, acp_list_dict,return_defaults=True)
    #
    #             self.session.commit()
    #
    #
    #             print('Inserção na tabela acompanhamento!', acp_list_dict[0]['acp_id'])
    #
    #
    #             # PREPARAÇÃO e INSERÇÃO  DE DADOS PARA INSERÇÃO NA TABELA processo_arquivo
    #             self.insert_process_arquivo(acp_list_dict=acp_list_dict, plp_id_pk=plp_id_pk,
    #                                         list_item_pra=list_item_pra, tam_pra_list_dict=tam_pra_list_dict,
    #                                         state=state, platform=platform)
    #             list_item_acp = []
    #             acp_list_dict = []
    #             tam_pra_list_dict = 0
    #
    #     # TRANSFERE OS ARQUIVOS PARA O DIRETÓRIO FINAL
    #
    #     root.transfer_files(state=state, list_name_urls=list_name_urls, plp_id=plp_id_pk, log=log)
    #
    #     print('Transferência de arquivos concluída!')
    #
    #
    #     t1 = time.time()
    #     # INSERÇÃO DE DADOS NA TABELA audiencia
    #     aud_list_dict = []
    #     # print("Audiencia: ", list_aud)
    #     for aud in list_aud:
    #
    #         aud.aud_plp_id = plp_id_pk
    #         if aud.aud_data is None:
    #             result_select = []
    #         else:
    #             result_select = self.select_aud_db(aud)
    #         if len(result_select) is 0:
    #             aud_list_dict.append(aud.__dict__)
    #         else:
    #             self.update_aud_db(aud)
    #
    #     if len(aud_list_dict):
    #
    #         self.session.bulk_insert_mappings(AudienciaTable, aud_list_dict)
    #         self.session.commit()
    #
    #         print('Inserção na tabela audiencia!')
    #
    #
    #     t1 = time.time()
    #     # INSERÇÃO DE DADOS NA TABELA parte E processo_parte
    #     ppt_list_dict = []
    #     for prt in list_prt:
    #
    #
    #         # VERIFICA SE A PARTE JÁ EXISTE NO BANCO DE DADOS
    #         result_select = self.select_prt_db(plp.plp_prc_id, prt[0].prt_cpf_cnpj, prt[0].prt_nome)
    #
    #         prt_id = self.conn.execute(ParteTable.__table__.insert(), [prt[0].__dict__]
    #                                    ).inserted_primary_key[0] if len(result_select) == 0 else \
    #         result_select[0][0]
    #
    #         ppt_list_dict.append({'ppt_prc_id': plp.plp_prc_id,
    #                               'ppt_prt_id': prt_id,
    #                               'ppt_plp_id': plp_id_pk,
    #                               'ppt_polo': 'PASSIVO' if prt[1] == 'Passivo' or 'Passiva' in prt[
    #                                   1] else 'ATIVO'})
    #
    #     if len(ppt_list_dict):
    #
    #         self.session.bulk_insert_mappings(ProcessoParteTable, ppt_list_dict)
    #         self.session.commit()
    #
    #         print('Inserção na tabela processo_parte!')
    #
    #
    #     t1 = time.time()
    #     # INSERÇÃO DE DADOS NA TABELA responsavel E processo_responsavel
    #     rsp_list_dict = []
    #     for rsp in list_rsp:
    #
    #         result_select = self.select_rsp_db(plp.plp_prc_id, rsp[0].rsp_nome, rsp[0].rsp_oab)
    #         # VERIFICA SE A PARTE JÁ EXISTE NO BANCO DE DADOS
    #         rsp_id = self.conn.execute(ResponsavelTable.__table__.insert(),
    #                                    [rsp[0].__dict__]).inserted_primary_key[0] if len(
    #             result_select) == 0 else result_select[0][0]
    #         if rsp[1] is None:
    #             rsp_list_dict.append({'prr_prc_id': plp.plp_prc_id, 'prr_plp_id': plp_id_pk,
    #                                   'prr_rsp_id': rsp_id},
    #                                  )
    #         else:
    #             rsp_list_dict.append({'prr_prc_id': plp.plp_prc_id,
    #                                   'prr_rsp_id': rsp_id,
    #                                   'prr_plp_id': plp_id_pk,
    #                                   'prr_polo': 'PASSIVO' if rsp[1] == 'Passivo' or rsp[
    #                                       1] == 'Passiva' else 'ATIVO'})
    #
    #
    #
    #     if len(rsp_list_dict):
    #
    #         self.session.bulk_insert_mappings(ProcessoResponsavelTable, rsp_list_dict)
    #         self.session.commit()
    #
    #         print('Inserção na tabela processo_responsavel!')
    #
    #
    #
    #     tend = time.time()
    #     print('\t- Processo ({}) - {} gravado no banco de dados em {} secs'.format(
    #         plp_id_pk, obj[0].plp_numero, (tend - t0)).upper())
    #
    #     print('Inserção no banco de dados!')


    # PREPARAÇÃO e INSERÇÃO  DE DADOS PARA INSERÇÃO NA TABELA processo_arquivo

    def update_process(self, obj, list_name_urls, platform, state, root, log, ):

        plp = obj[0]
        plp.plp_data_update = datetime.now()
        # ATUALIZAÇÃO DE DADOS NA TABELA processo_plataforma
        self.update_plp_db(obj[5], plp)

        # INSERE NOVOS DADOS OBTIDOS NA ATUALIZAÇÃO
        if len(obj[1])>0 and len(obj[2])>0 and len(obj[4])>0:
            self.insert_process(obj=obj, log=log, list_name_urls=list_name_urls, platform=platform,
                                state=state, root=root, plp_id=obj[5])

        print("UPDATE FEITO COM SUCESSO!")


    # ATUALIZAÇÃO DA DATA NA TABELA PLATAFORMA_ESTADO
    def update_ple_data_db(self, ple_plt_id, ple_uf):

        q = "SELECT   COUNT(prc_id)  FROM processo {} join processo_plataforma on plp_prc_id = prc_id and plp_plt_id = {} and plp_grau = {}" \
            " OUTER APPLY (select top 1 acp_plp_id,acp_data_cadastro as cadastro from acompanhamento " \
            " where acp_plp_id=plp_id order by acp_data_cadastro desc) acp inner join plataforma_estado on ple_uf = '{}'" \
            " and ple_plt_id = {} and ple_area = 1" \
            " WHERE (plp_localizado is null or plp_localizado > 0) and " \
            "(plp_data_update<=ple_data or plp_data_update is null) and prc_estado = '{}' and" \
            "  (prc_removido is null or prc_removido = 0) " \
            "  and len(prc_numero) > 12 and prc_area = 1 "

        count_primeiro_grau = q.format('left', str(ple_plt_id), str(1), str(ple_uf), str(ple_plt_id), str(ple_uf))
        count_segundo_grau = q.format('inner', str(ple_plt_id), str(2), str(ple_uf),
                                      str(ple_plt_id), str(ple_uf)).replace('10 and prc_area',
                                                                            "10 and plp_data_update is not null and prc_area")
        print(count_primeiro_grau)
        count_primeiro_grau = self.conn.execute(count_primeiro_grau).fetchall()[0][0]
        count_segundo_grau = self.conn.execute(count_segundo_grau).fetchall()[0][0]

        if count_primeiro_grau == 0 and count_segundo_grau == 0:

            q = "select top 1 plp_data_update, CASE WHEN (convert(char(5), plp_data_update, 108)) >= '18:00' THEN  CONVERT(VARCHAR(10)," \
                " DATEADD(day, 1, plp_data_update), 126)+' 18:00'  ELSE CONVERT(VARCHAR(10), plp_data_update, 126) + ' 18:00' END " \
                " from processo inner join processo_plataforma  on plp_prc_id=prc_id and plp_plt_id = {} and plp_localizado > 0 " \
                " where plp_data_update is not null and prc_estado = '{}' and  (prc_removido is null or prc_removido = 0)  " \
                "order by plp_data_update".format(str(ple_plt_id), str(ple_uf))
            data = self.conn.execute(q).fetchall()[0][0]
            data_atual = datetime.now()
            data = data if data > data_atual else data_atual
            t = PlataformaEstadoTable
            ple_data = {'ple_data': data}
            print('ple_data', data, end='\t')
            print('ple_plt_id', ple_plt_id, end='\t')
            print('ple_uf', ple_uf)
            self.session.query(t).filter(and_(t.ple_plt_id == ple_plt_id, t.ple_uf == ple_uf)).update(ple_data)
            self.session.commit()
        else:
            print("Ainda a {}  para se atualizados sendo ""{} do primerio e {} do segundo !".format(
                (count_primeiro_grau + count_segundo_grau), count_primeiro_grau, count_segundo_grau))

    # ATUALIZAÇÃO DO ELEMENTO PROCESSO_PLATAFORMA NO BANCO DE DADOS
    def update_plp_db(self, plp_id, obj):
        t = ProcessoPlataformaTable
        list_item = {i: j for i, j in obj.__dict__.items() if j is not None}
        # print(list_item)
        print("Tipo plp_id: ", type(plp_id), " Numero plp_id: ", plp_id)
        self.session.query(t).filter(t.plp_id == plp_id).update(list_item)
        self.session.commit()

    # ATUALIZAÇÃO DO ELEMENTO PROCESSO NO BANCO DE DADOS
    def update_prc_db(self, prc_id, obj):
        t = ProcessoTable
        list_item = {i: j for i, j in obj.__dict__.items() if j is not None}
        self.session.query(t).filter(t.prc_id == prc_id).update(list_item)
        self.session.commit()

    # ATUALIZAÇÃO DA AUDIÊNCIA NA TABELA AUDIÊNCIA
    def update_aud_db(self, obj):
        t = AudienciaTable
        list_item = {i: j for i, j in obj.__dict__.items() if j is not None}
        self.session.query(t).filter(and_(t.aud_prc_id == obj.aud_prc_id,
                                          t.aud_tipo == obj.aud_tipo)).update(list_item)
        self.session.commit()

    # ATUALIZAÇÃO DO ELEMENTO ACOMPANHAMENTO NO BANCO DE DADOS
    def update_acp_db(self, acp_id, obj):
        t = AcompanhamentoTable
        list_item = {i: j for i, j in obj.__dict__.items() if j is not None}
        self.session.query(t).filter(t.acp_id == acp_id).update(list_item)
        self.session.commit()

    # BUSCA A AUDIÊNCIA NO BANCO DE DADOS
    def select_aud_db(self, obj):
        query = "SELECT aud_id FROM audiencia " \
                "WHERE aud_prc_id = '{}' and aud_tipo = '{}' and aud_data = '{}' and " \
                "aud_status = '{}';".format(obj.aud_prc_id, obj.aud_tipo, obj.aud_data, obj.aud_status, obj.aud_obs)
        print(query)
        result = self.conn.execute(query)
        return result.fetchall()

    # BUSCA A PARTE NO BANCO DE DADOS
    def select_prt_db(self, prt_prc_id, prt_cpf_cnpj, prt_nome):
        flag = ''
        if prt_cpf_cnpj is None:
            flag = "and prt_cpf_cnpj = '{}'".format(prt_cpf_cnpj)
        query = "SELECT prt_id, prt_nome, prt_cpf_cnpj,ppt_prt_id FROM parte " \
                "LEFT JOIN processo_parte on prt_id=ppt_prt_id and ppt_prc_id='{}' " \
                "WHERE prt_nome = '{}' {} ;".format(prt_prc_id, prt_nome, flag)
        result = self.conn.execute(query)
        return result.fetchall()

    # BUSCA O RESPONSAVEL NO BANCO DE DADOS
    def select_rsp_db(self, prr_prc_id, rsp_nome, rsp_oab):

        query = "SELECT rsp_id, prr_rsp_id FROM responsavel " \
                "LEFT JOIN processo_responsavel on rsp_id=prr_rsp_id and prr_prc_id='{}' " \
                "WHERE (rsp_nome = '{}' and rsp_oab = '{}');".format(prr_prc_id, rsp_nome.replace("'", ' '), rsp_oab)

        result = self.conn.execute(query)
        return result.fetchall()

    # BUSCA OS ACOMPANHAMENTOS NO BANCO DE DADOS
    def select_acp_db(self, plp_id_pk, top):
        query = "SELECT top {} acp_id FROM acompanhamento " \
                "WHERE acp_plp_id = '{}' order by acp_numero desc, acp_data_cadastro desc;".format(top, str(plp_id_pk))
        result = self.conn.execute(query)
        return result.fetchall()

    # DELETA TODOS OS DADOS, PELO ID E PRC_ID, DA TABELA ESCOLHIDA
    def delete_db(self, prc_id):
        t = ProcessoParteTable
        self.session.query(t).filter(t.ppt_prc_id == prc_id).delete()
        self.session.commit()

        t = ProcessoResponsavelTable
        self.session.query(t).filter(t.prr_prc_id == prc_id).delete()
        self.session.commit()

    # PROCURA PELOS PROCESSUM NO BANCO DE DADOS PARA ATUALIZAÇÃO
    def search_process_sequencial_acp_arq(self, result):
        dic_acomp_arq = {}
        aux = ""
        tam = len(result)
        dict_plp_prc_id = {}
        for i in range(tam):
            if result[i][4] is not None:
                aux += str(result[i][4])
                dict_plp_prc_id[result[i][4]] = result[i][3]
                if i < tam - 1:
                    aux += ', '
                else:
                    break

        q = 'SELECT acp_id,acp_plp_id,acp_tipo, acp_esp, acp_data_cumprimento, acp_data_evento, acp_data_prazo,acp_data_cadastro, acp_data, acp_pra_status, acp_numero ' \
            'FROM acompanhamento WHERE acp_plp_id  in ({})'
        q = q.format(aux)
        i = list(self.conn.execute(q).fetchall())
        list_aux = []
        tam = len(i)
        tam1 = 51000
        j = 0
        while j < tam:
            aux = ""
            for k in range(tam1):
                if i[j][0] is not None:
                    aux += str(i[j][0])
                    if j < (tam - 1) and k < (tam1 - 1):
                        aux += ', '
                    else:
                        j += 1
                        break
                j += 1
            q = 'SELECT pra_acp_id,pra_descricao FROM processo_arquivo WHERE pra_acp_id in ({})'
            q = q.format(aux)
            list_aux += list(self.conn.execute(q).fetchall())

        list_arq_acp_plp_id = {}
        for k in list_aux:
            if k[0] in list_arq_acp_plp_id.keys():
                list_arq_acp_plp_id[k[0]].append(k[-1])
            else:
                list_arq_acp_plp_id[k[0]] = [k[-1]]

        for j in i:
            prc_id = dict_plp_prc_id[j[1]]
            list_aux = list_arq_acp_plp_id[j[0]] if j[0] in list_arq_acp_plp_id.keys() else []
            if prc_id in dic_acomp_arq.keys():
                dic_acomp_arq[prc_id][(j[7], j[2], j[3])] = [j, list_aux]
            else:
                dic_acomp_arq[prc_id] = {(j[7], j[2], j[3]): [j, list_aux]}

        return dic_acomp_arq

    # PROCURA PELOS PROCESSUM NO BANCO DE DADOS PARA ATUALIZAÇÃO
    def search_process_sequencial(self, data):

        q = "SELECT  prc_sequencial, plp_status, prc_numero,prc_id ,plp_id, prc_estado, cadastro," \
            "           plp_codigo, plp_data_update,CASE WHEN plp_data_update is null THEN 0 ELSE 1 END AS OrderBy " \
            "           FROM processo " \
            "			left join processo_plataforma on plp_prc_id = prc_id and plp_plt_id=1 and plp_localizado = 1 and plp_data_update<='{}'" \
            "           OUTER APPLY (select top 1 acp_plp_id,acp_data_cadastro as cadastro from acompanhamento " \
            "           where acp_plp_id=plp_id order by acp_data_cadastro desc) acp " \
            "           WHERE  (plp_status is null or  plp_status " \
            "           not in ('Arquivado Definitivamente','ARQUIVADO','Baixado', 'Removido da Base','Trabalhista') " \
            "           or (plp_status in ('Arquivado Definitivamente','ARQUIVADO', 'Baixado') " \
            "           and cadastro>='2014-03-18 18:00' )) " \
            "           and len(prc_numero) > 10 " \
            "           order by OrderBy, newid() "
        q = q.format(str(data))
        result = list(self.conn.execute(q).fetchall())
        dict_acp_arq = self.search_process_sequencial_acp_arq(result)
        # for i in dict_acp_arq.items():
        #     print('*',i[0],'<>',len(i[-1].items()))

        return result, dict_acp_arq
        # INSERIR NOVOS PROCESSOS_PLATAFORMA NO BANCO DE DADOS

    # INSERIR NOVOS PROCESSOS_PLATAFORMA NO BANCO DE DADOS
    def insert_processum(self, obj, list_name_urls, state, log, root, plp_id=None):

        plp_id_pk = plp_id
        prc = obj[0]
        plp = obj[1]
        list_acp_arq = obj[2]
        list_aud = obj[3]
        list_acp_arq_update = obj[4]

        t0 = time.time()
        t1 = time.time()
        if plp_id is None:  # VERIFICA SE É UM NOVO ELEMENTO NA TABELA
            # INSERÇÃO DE DADOS NA TABELA processo_plataforma
            plp_id_pk = self.conn.execute(ProcessoPlataformaTable.__table__.insert(),
                                          [plp.__dict__]).inserted_primary_key[0]

            if log is not None:
                log.insert_info('Objetos inseridos na tabela "processo_plataforma"!')

        t1 = time.time()
        # INSERÇÃO DE DADOS NA TABELA AUDIENCIA
        aud_list_dict = []
        for aud in list_aud:
            aud.aud_plp_id = plp_id_pk
            aud_list_dict.append(aud.__dict__)
        if len(aud_list_dict):

            self.session.bulk_insert_mappings(AudienciaTable, aud_list_dict)
            self.session.commit()

            print('Objetos inseridos na tabela "audiencia"!')


        # print('aud:', time.time() - t1)

        # TRANSFERE OS ARQUIVOS PARA O DIRETÓRIO FINAL

        root.transfer_files(state=state, list_name_urls=list_name_urls, plp_id=plp_id_pk, log=log)

        print('Transferência de arquivos concluída!')


        # PREPARAÇÃO DE DADOS PARA INSERÇÃO NA TABELA acompanhamento
        acp_list_dict = []
        for acp_pra in list_acp_arq:
            acp_pra[0].acp_plp_id = plp_id_pk
            acp_pra[0].acp_prc_id = plp.plp_prc_id
            acp_pra[0].acp_data = datetime(datetime.now().year, datetime.now().month,
                                           datetime.now().day, datetime.now().hour,
                                           datetime.now().minute, datetime.now().second)
            acp_list_dict.append(acp_pra[0].__dict__)
        t1 = time.time()
        # INSERÇÃO DE DADOS NA TABELA acompanhamento
        if len(acp_list_dict):

            self.session.bulk_insert_mappings(AcompanhamentoTable, acp_list_dict)
            self.session.commit()


            print('Objeto inseridos na tabela "acompanhamento"!')

        # print('acp:', time.time() - t1)

        # SELECT PARA RECUPERAR AS CHAVES PRIMARIAS DOS ACOMPANHAMENTOS
        list_acp_id = self.select_acp_db(plp_id_pk, len(acp_list_dict))

        # ATUALIZAR OS ACOMPANHAMENTOS NA TABELA processo_arquivo
        for i in list_acp_arq_update:

            # ATUALIZAÇÃO DE DADOS NA TABELA processo_plataforma
            acp_id = i[0].acp_id
            # print("\n\ni[0]\n\n", i[0].__dict__)
            i[0].acp_id = None
            self.update_acp_db(acp_id=acp_id, obj=i[0])

            print('Objeto atualizados na tabela "acompanhamento"!')


        # PREPARAÇÃO DE DADOS PARA INSERÇÃO NA TABELA processo_arquivo DOS NOVOS ACOMPANHAMENTO
        pra_list_dict = []
        for acp_pra, acp_id in zip(list_acp_arq, list_acp_id):
            for pra in acp_pra[1]:
                pra.pra_acp_id = acp_id[0]
                pra.pra_url = 'Downloads/{}/{}/{}/{}'.format(state, 'Processum', plp_id_pk, pra.pra_nome)
                pra_list_dict.append(pra.__dict__)
        t1 = time.time()

        # PREPARAÇÃO DE DADOS PARA INSERÇÃO NA TABELA processo_arquivo  ACOMPANHAMENTO UPDATE
        for acp_pra in list_acp_arq_update:
            for pra in acp_pra[1]:
                pra.pra_url = 'Downloads/{}/{}/{}/{}'.format('PRO', 'Processum', plp_id_pk, pra.pra_nome)
                pra_list_dict.append(pra.__dict__)
        t1 = time.time()

        # INSERÇÃO DE DADOS NA TABELA processo_arquivo
        if len(pra_list_dict):

            self.session.bulk_insert_mappings(ArquivoTable, pra_list_dict)
            self.session.commit()

            print('Objeto atualizados na tabela "processo_arquivo"!')





    # ATUALIZA PROCESSOS_PLATAFORMA JÁ INSERIDOS NO BANCO DE DADOS
    def update_processum(self, obj, list_name_urls, log, root, state):

        process = obj[0]
        process_platform = obj[1]

        prc_id = obj[-1]
        plp_id = obj[-2]

        # ATUALIZAÇÃO DE DADOS NA TABELA processo
        if prc_id is not None:
            self.update_prc_db(prc_id=prc_id, obj=process)

            print('Objeto atualizado na tabela "processo"!')

        process_platform.plp_prc_id = prc_id
        # ATUALIZAÇÃO DE DADOS NA TABELA processo_plataforma
        if plp_id is not None:
            self.update_plp_db(plp_id=plp_id, obj=process_platform)

            print('Objeto atualizado na tabela "processo_plataforma"!')

        # INSERE NOVOS DADOS OBTIDOS NA ATUALIZAÇÃO
        self.insert_processum(obj=obj[:-2], list_name_urls=list_name_urls, plp_id=plp_id,
                              log=log, root=root, state=state)

            # raise

    # BUSCA O CHAVE NA TABELA CARTEIRA  NO BANCO DE DADOS
    def key_crt(self, crt_name):
        query = "SELECT crt_id FROM carteira WHERE crt_nome = '{}'; ".format(str(crt_name))
        result = list(self.conn.execute(query).fetchall())
        if len(result):
            return result[0][0]
        if crt_name is None:
            return None
        return self.conn.execute(CarteiraTable.__table__.insert(), [{'crt_nome': crt_name}]).inserted_primary_key[0]
