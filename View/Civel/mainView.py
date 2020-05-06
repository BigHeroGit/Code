


# coding: utf-8
__autors__ = 'Leonardo Bidó, Aurélio Santos'

import os
import pickle
from sys import argv
from random import random
from Controller.Civel.executeController import *
from Model.toolsModel import *

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

try :

    if argv[1].upper() != 'PROCESSUM':
        ###################################################################################################################
        i = int(argv[3])
        grau = int(argv[4])
        arq_name = str(os.path.abspath('../../Temp/{}/{}/BinaryFiles{}'.format(argv[1].upper(), argv[2].upper(),grau)))
        arq = open(arq_name + "\\row_database_{}_{}.bin".format(i,grau), 'r')
        aux = list(arq.readlines())
        arq.close()
        row_database=aux[0]
        row_database = pickle.loads(eval(row_database))
        dict_plp_2grau = aux[1]
        dict_plp_2grau = pickle.loads(eval(dict_plp_2grau))
        print("Nº",len(row_database))
        row_database1 = row_database[0:int(len(row_database)/2)]
        row_database2 = row_database[int(len(row_database)/2) + 1:len(row_database)]

        print("row1 -> Nº",len(row_database1))
        print("row2 -> Nº", len(row_database2))

        k=0
        for i in row_database1:
            print("ID:{} {}".format(k,i))
            k=k+1
            if k == 10:
                break

        print('\n\n\n\n\n')
        k = 0
        for i in row_database2:
            print("ID:{} {}".format(k, i))
            k = k + 1
            if k == 10:
                break

        #input('mito?')
        ###################################################################################################################
        # raise
        ###################################################################################################################
        platform_id = '7'
        platform_name = 'E-PROC'
        ########################
        if argv[1].upper() == platform_name.upper() and argv[2].upper() == 'TO' :

            print('{}\n{} - TOCANTINS\n{}'.format('#' * 30, platform_name.upper(), '#' * 30))
            eproc_go = eprocThreadController(platform_id=platform_id, platform_name=platform_name, state='TO',
                                             flag=False,
                                             row_database=row_database, dict_plp_2grau=dict_plp_2grau, num_thread=i,
                                             grau=grau)
            eproc_go.start()

        ###################################################################################################################

        ###################################################################################################################
        platform_id = '6'
        platform_name = 'TUCUJURIS'
        ########################
        if argv[1].upper() == platform_name.upper() and argv[2].upper() == 'AP' :
            print('{}\n{} - AMAPA\n{}'.format('#' * 30, platform_name.upper(), '#' * 30))

            tucujuris_ap =  tucujurisThreadController(platform_id=platform_id, platform_name=platform_name, state='AP',
                                             flag=False, row_database=row_database, dict_plp_2grau=dict_plp_2grau, num_thread=i,
                                             grau=1)
            tucujuris_ap.start()
        #####################################################################################

        ###################################################################################################################
        platform_id = '5'
        platform_name = 'ESAJ'
        ########################
        if argv[1].upper() == platform_name.upper() and argv[2].upper() in ['AM', 'MS', 'AC'] :

            estado = {'AM' : 'AMAZONAS', 'MS' : 'MATO GROSSO DO SUL', 'AC' : 'ACRE'}
            print('{}\n{} - {}\n{}'.format('#' * 30, platform_name.upper(), estado[argv[2].upper()], '#' * 30))

            esaj_am = esajThreadController(platform_id=platform_id, platform_name=platform_name, state=argv[2].upper(),
                                           flag=False,
                                           row_database=row_database, dict_plp_2grau=dict_plp_2grau, num_thread=i,
                                           grau=grau)
            esaj_am.start()

        ###################################################################################################################

        ###################################################################################################################
        platform_id = '3'
        platform_name = 'PROJUDI'
        ########################
        if argv[1].upper() == platform_name.upper() and argv[2].upper() in ['MA', 'GO', 'AM', 'RR', 'PA','BA'] :

            estado = {'MA' : 'MARANHÃO', 'GO' : 'GOIAS', 'AM' : 'AMAZONAS', 'RR' : 'RORAIMA', 'PA' : 'PARA', "BA":"BAHIA"}
            print('{}\n{} - {}\n{}'.format('#' * 30, platform_name.upper(), estado[argv[2].upper()], '#' * 30))
            #input('eu')
            projudi_ma = projudiThreadController(platform_id=platform_id, platform_name=platform_name, state=argv[2].upper(),
                                           flag=False,
                                           row_database=row_database, dict_plp_2grau=dict_plp_2grau, num_thread=i,
                                           grau=grau)
            projudi_ma.start()

        ###################################################################################################################

        ###################################################################################################################
        platform_id = '2'
        platform_name = 'PJE'
        ########################
        if argv[1].upper() == platform_name.upper() and argv[2].upper() in ['DF', 'MA', 'PA', 'RO', 'BA', 'RJ'] :

            estado = {'DF' : 'DISTRITO FEDERAL', 'MA' : 'MARANHAO', 'PA' : 'PARA', 'RO' : 'RONDONIA', 'BA':'BAHIA', 'SP': 'SÃO PAULO', 'RJ':'RIO DE JANEIRO'}
            print('{}\n{} - {}\n{}'.format('#' * 30, platform_name.upper(), estado[argv[2].upper()],'#' * 30))
            pje_df = pjeThreadController(platform_id=int(platform_id), platform_name=platform_name, state=argv[2].upper(),
                                           flag=False,
                                           row_database=row_database, dict_plp_2grau=dict_plp_2grau, num_thread=i,
                                           grau=grau,civel_trabalhista = argv[5]) # argv[4] é para identificar se o pje é trabalhista ou cível
            pje_df.start()

    else:

        ###################################################################################################################
        platform_id = '1'
        platform_name = 'PROCESSUM'
        #############################
        i = int(argv[2])
        arq_name = str(os.path.abspath('../../Temp/Processum/BinaryFiles'))
        arq = open(arq_name + "\\row_database.bin", 'r')
        row_database = arq.readlines()[i]
        arq.close()
        row_database = pickle.loads(eval(row_database))
        print('nº', len(row_database))

        arq = open(arq_name + "\\dict_acp_arq.bin", 'r')
        dict_plp_2GRAU = arq.readlines()[i]
        arq.close()
        dict_plp_2GRAU = pickle.loads(eval(dict_plp_2GRAU))

        processum_pro = processumThreadController(platform_id, platform_name, row_database, dict_plp_2GRAU, i)
        processum_pro.start()


except IndexError :
    print("dou ruim")
    # raise
    pass


