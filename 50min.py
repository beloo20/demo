


import ftx
import pandas as pd
import ta
import time
import json
from math import *
import pandas_ta as pda
import telegram_send

import mysql.connector as MC
from time import sleep
import ernest

# pour la connexion au bdd
connection1 = MC.connect(host='mysql-hinvest.alwaysdata.net',database='hinvest_bbd',user='hinvest',password='HOunha20lide@')

#pour la connection au compte ftx
api_key = '4ylY1TRh4R7vxNhW-6lG_Qq3DkZgMa-JHNPF8Tr0'
api_secret = 'OlBlqYozzwJsuOXi2P8IFRBqi4QW107ji02eGgDf'
subaccount_name = 'ErnestTradingFtxBot'


def getBalance(myclient, coin):
    jsonBalance = myclient.get_balances()
    if jsonBalance == []: 
        return 0
    pandaBalance = pd.DataFrame(jsonBalance)
    if pandaBalance.loc[pandaBalance['coin'] == coin].empty: 
        return 0
    else: 
        return float(pandaBalance.loc[pandaBalance['coin'] == coin]['free'])
    

client = ftx.FtxClient(
    api_key = api_key,
    api_secret = api_secret, 
    subaccount_name = subaccount_name
)
result = client.get_balances()
fiatSymbol = 'USD'

solde_compte = getBalance(client, fiatSymbol)
usdt_bot = 0
valeur_demande = 0

nombre_bot = 50
nombre_bot += 1

reste = 0.0
divise = 0
retire = 0

# verifier demande de retrait
if ernest.get(connection1 , "retrait", 3) == "En attente":
    print("demande en cour")
    
    valeur_demande = ernest.get(connection1 , "retrait", 2)
    id = ernest.get(connection1 , "retrait", 0)
    print("valeur_demande: " + str(valeur_demande))
    
    
    # recuperation solde des bots
    for i in range(1,nombre_bot):
        table = "bot_"+str(i)
        usdt_bot += ernest.get(connection1 , table, 5)
        
        if ernest.get(connection1 , table, 5) > 15:
            divise += 1
    print("divise : " + str(divise))
    print("usdt_bot : " +str(usdt_bot))
    
    # si le solde globale peut couvrire le retrait
    if solde_compte > usdt_bot:
        reste = solde_compte - usdt_bot
        print("reste: "+str(reste))
        if reste >= valeur_demande:
            print("retrait possible")
            ernest.update(connection1, id)
            
            
    retire = valeur_demande / divise
    retire2 = 0
    print(retire)
    if solde_compte < usdt_bot:
        # recuperation solde des bots
        for i in range(1,nombre_bot):
            table = "bot_"+str(i)
            if (ernest.get(connection1 , table, 5) - retire) > 14 and retire2 < valeur_demande:
                retire2 += retire
            
    if retire2 >= valeur_demande and retire2 > 0:
        print("retrait possible retraire 2")
        print("id: "+str(id))
        ernest.update(connection1, id)
        retire2 = 0
        for i in range(1,nombre_bot):
            table = "bot_"+str(i)
            if (ernest.get(connection1 , table, 5) - retire) > 14 and retire2 < valeur_demande:
                retire2 += retire
                montant = ernest.get(connection1 , table, 5) - retire
                id = ernest.get(connection1 , table, 0)
                ernest.update2(connection1, table, montant, id)
            
    
else:
    print("pas de demande")
    

messages = " Bibliotheque 50min.py charger sans probleme "
telegram_send.send(messages=[messages])



