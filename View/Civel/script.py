
from Database.connDatabase import SQL
from Model.toolsModel import *
from random import shuffle
import pickle
import os

def Processum_mult_thread(num_tread, num_processo):

    try:
        access = ['144.217.126.74', 'sa', 'becadv123', 'titanium_dev?charset=utf8']
        # LOGIN NA PLATAFORMA E BUSCA DOS PROCESSOS NO BANCO DE DADOS
        data = datetime(datetime.now().year , datetime.now().month, datetime.now().day,
                        datetime.now().hour, datetime.now().minute, datetime.now().second)
        conn_database = SQL(access[0], access[1], access[2])
        row_database,dict_acp_arq = conn_database.search_process_sequencial(data)

        # "row_database=[prc_sequencial, plp_status, prc_numero, prc_id,plp_id, prc_estado, cadastro, plp_codigo,
        # plp_data_update,list_acompanmento]"
        conn_database.__del__()
    except AttributeError:
        return False
    try:
        num_Bot = num_tread-1
        num_proc_Bot = len(row_database) // num_Bot
        print('num_proc_Bot',num_proc_Bot)


        arq_name = str(os.path.abspath('../Temp/Processum/BinaryFiles'))
        Tools.new_path(arq_name)

        arq_row_database= open(arq_name + "\\row_database.bin", 'w')
        texto_row_database = []

        arq_acp_arq= open(arq_name + "\\dict_acp_arq.bin", 'w')
        texto_acp_arq = []

        list_row = [list(i) for i in row_database]
        shuffle(list_row)
        tam = len(list_row)
        pi = 0
        pf = num_proc_Bot if num_proc_Bot <= tam else tam

        while True:
            texto_row_database.append(str(pickle.dumps(list_row[pi:pf])) + '\n')
            dict_aux={}
            for i in list_row[pi:pf]:
                dict_aux[i[3]]=dict_acp_arq[i[3]] if i[3] in dict_acp_arq.keys() else [None]
            texto_acp_arq.append(str(pickle.dumps(dict_aux)) + '\n')
            print("list_row[{}:{}]".format(pi,pf),len(list_row[pi:pf]))
            print("dict_aux",len(dict_aux))

            if pf == tam:
                break
            pi = pf
            pf = num_proc_Bot + pf if num_proc_Bot + pf <= tam else tam

        arq_row_database.writelines(texto_row_database)
        arq_row_database.close()

        arq_acp_arq.writelines(texto_acp_arq)
        arq_acp_arq.close()

        for i in range(len(texto_row_database)):
            os.system("start /B start cmd.exe @cmd /k python mainView.py Processum {}".format(str(i)))
    except:
        return False
    return True

def Platform_mult_thread(num_tread,platform_name, platform_id ,state,grau,civel_trabalhista):
    # LOGIN NA PLATAFORMA E BUSCA DOS PROCESSOS NO BANCO DE DADOS
    try:
        conn_database = SQL('144.217.126.74', 'sa','becadv123')
        row_database, dict_plp_2_grau = conn_database.search_process_for_update(state=state.upper(),platform=platform_id
                                                                                ,grau=1,area=civel_trabalhista)

        if len(row_database) == 0:
            print("Não a processos para {} {}".format(str(platform_name), str(state)))
            conn_database.update_ple_data_db(str(platform_id), str(state).upper())
            return False

        print("NUMERO DE PROCESSOS BUSCADOS:", len(row_database))

        conn_database.__del__()
    except AttributeError:
        return False

    try:
        num_Bot = num_tread
        #AJUSTANDOS NUMERO DE THREAD
        num_proc_Bot = len(row_database) // num_Bot
        while num_proc_Bot==0 and num_Bot>0:
            num_Bot-=1
            num_proc_Bot = len(row_database) // num_Bot

        print(' {} {} num_proc_Bot'.format(str(platform_name),str(state)), num_proc_Bot)

        arq_name = str(os.path.abspath('../../Temp/{}/{}/BinaryFiles{}'.format(platform_name.upper(),state.upper(),str(grau))))
        Tools.delete_path(arq_name)
        Tools.new_path(arq_name)

        texto_row_database,texto_plp_2_grau = [],[]

        list_row_bots =[[] for i in range(0,num_Bot)]

        for i in range(len(row_database)):
            p= i % num_Bot
            list_row_bots[p].append(list(row_database[i]))


        for i in list_row_bots:
            texto_row_database.append(str(pickle.dumps(i)) + '\n')
            dict_aux = {}
            count_i=0
            for j in i:
                dict_aux[j[1]] = []
                if j[1] in dict_plp_2_grau.keys() :
                   dict_aux[j[1]] = dict_plp_2_grau[j[1]]
                   count_i+=1

            texto_plp_2_grau.append(str(pickle.dumps(dict_aux)) + '\n')
            print(f"list_row[{list_row_bots.index(i)}] --> tam ={len(i)} --> dict_aux {count_i}")

        print("\n\ntexto_row_database \t\t{}\n\n".format(len(texto_row_database)))


        for i in range(len(texto_row_database)):
            print(arq_name +"\\row_database_{}_{}.bin".format(i,grau))
            arq_row_database = open(arq_name + "\\row_database_{}_{}.bin".format(i,grau), 'a')
            arq_row_database.write(texto_row_database[i])
            arq_row_database.write(texto_plp_2_grau[i])
            arq_row_database.close()

            os.system("start /B start cmd.exe @cmd /k python mainView.py {} {} {} {} {}".format(platform_name,state,str(i),str(grau), str(civel_trabalhista)))
    except:
        raise
        return False
    return [num_tread,platform_name.upper(),state.upper(),platform_id,grau,0]
'''
1	Processum
2	Pje
3	Projudi
4	Físico
5	Esaj
6	Tucujuris
7	E-proc
8	Procon
'''

# Processum_mult_thread(num_tread=1,num_processo=40000)  #ok

 #LISTA PLATAFORMA ESTADO

 # escolher se e cível ou trabalhista no caso do pje

civel_trabalhista = 1# 1 se for cível e 2 caso seja trabahista

lista_ple=[
            #--------5      Esaj-------------------------------------
                # (1,"esaj",5,'am',1),
                # (1,"esaj",5,'am',2),
                # (1,"esaj",5,'ms',1),
                #(1,"esaj",5,'ms',2),
                # (7,"esaj",5,'ac',1),
                # (5,"esaj",5,'ac',2),

            #------3    Projudi----------------------------------------
                 #(1,"projudi",3,'ma',1),
                #(1,"projudi",3,'ma',2),
                (4,"projudi",3,'go',1),
                #(1,"projudi",3,'go',1),
                # (3,"projudi",3,'am',1),
                # (1,"projudi",3,'am',2),
                # (1,"projudi",3,'rr',1),
                # (1,"projudi",3,'rr',2),
                # (1,"projudi",3,'pa',1),
                # (1,"projudi",3,'ba',1),


            #-------2      Pje  Cível ---------------------------------------
               #(1,"pje",2,'sp',1),
               #(1,"pje",2,'ma',1),
               # (1,"pje",2,'rj',1),
               #(1,"pje",2,'ma',1),
               #(1,"pje",2,'df',1),
               # (2,"pje",2,'df',2),
               #(1,"pje",2,'pa',1),
               #(1,"pje",2,'ro',1),
               #(1,"pje",2,'pa',1),
               # (1,"pje",2,'ba',1),
               # (1,"pje",2,'ba',2),

            #----7      EPROC---------------------------------------
                #(1,"e-proc",7,'to',1),

            # ----6      Tucujuris-------------------------------------
                  #(1,"tucujuris",6,'ap',1),


            (-1,-1,-1,-1)
    ]

for i in lista_ple[:-1]:
    Platform_mult_thread(num_tread=i[0], platform_name=i[1], platform_id=i[2], state=i[3],grau=i[4],civel_trabalhista=civel_trabalhista)
"/html/body/center[1]/h1 - bad gatway"
"06105993720198040020"
''
