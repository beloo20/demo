# bot de ddistribution de prix au autres bots

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


client = ftx.FtxClient(
    api_key = api_key,
    api_secret = api_secret, 
    subaccount_name = subaccount_name
)



def getBalance(myclient, coin):
    jsonBalance = myclient.get_balances()
    if jsonBalance == []: 
        return 0
    pandaBalance = pd.DataFrame(jsonBalance)
    if pandaBalance.loc[pandaBalance['coin'] == coin].empty: 
        return 0
    else: 
        return float(pandaBalance.loc[pandaBalance['coin'] == coin]['free'])
    
    
result = client.get_balances()
fiatSymbol = 'USD'

solde_compte = getBalance(client, fiatSymbol)
usdt_bot = 0

nombre_bot = 50
nombre_bot += 1
bot_actif = 0
a_distribuer = 0.0
valeur_demande = 0

# recuperation solde des bots
for i in range(1,nombre_bot):
    table = "bot_"+str(i)
    usdt_bot += ernest.get(connection1 , table, 5)


# verifier de demande de valider
if ernest.get(connection1 , "retrait", 3) == "Retrait valider par le bot":
    print("Retrait valider par le bot")
    messages = " Retrait Valider par le bot "
    telegram_send.send(messages=[messages])
    
    valeur_demande = ernest.get(connection1 , "retrait", 2)
    print("valeur_demande: " + str(valeur_demande))
    
    messages = "valeur_demande: " + str(valeur_demande)
    telegram_send.send(messages=[messages])

usdt_bot += valeur_demande 
if solde_compte > usdt_bot:
    a_distribuer = solde_compte - usdt_bot 
    # verification de bot actif
    for i in range(1,nombre_bot):
        table = "bot_"+str(i)
        print(table)
        # actif = 1 et usdt < 0.0 et crypto < 0.0
        if ernest.get(connection1 , table, 15) == 1 and ernest.get(connection1 , table, 5) < 0.00000001 and ernest.get(connection1 , table, 3) < 0.00000001:
            bot_actif += 1
            nom_bot = ernest.get(connection1 , table, 1)
            nom_crypto = ernest.get(connection1 , table, 2)
            total_trad = ernest.get(connection1 , table, 8)
            positif_trad = ernest.get(connection1 , table, 9)
            negatif_trad = ernest.get(connection1 , table, 11)
            status = ernest.get(connection1 , table, 11)
            prix_achat = ernest.get(connection1 , table, 13)
            if a_distribuer >= 12.0:
                prix_actuel = ernest.get(connection1 , table, 16)
                ernest.insert( table, nom_bot, nom_crypto, 0, 0, 12.0, 0, 0, total_trad, positif_trad, negatif_trad, status, "achat", prix_achat, 1, prix_achat)
                print("Bot initialiser.....")
                a_distribuer = a_distribuer - 12.0
                
                
                print("a_distribuer: "+str(a_distribuer))
                print("bot_actif: "+str(bot_actif))
                
                
            
print("---------------------------------")
print("usdt_bot: "+str(usdt_bot))
print("a_distribuer: "+str(a_distribuer))
print("solde_compte: "+str(solde_compte))
print("bot_actif: "+str(bot_actif))
         


messages = " Bibliotheque 45min.py charger sans probleme "
telegram_send.send(messages=[messages])

    





