






# ********* les imports **************   
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

# sleep(240)
connection1 = MC.connect(host='mysql-hinvest.alwaysdata.net',database='hinvest_bbd',user='hinvest',password='HOunha20lide@')

# ********* les parametres commun *****
pairSymbol = 'BNB/USD'
fiatSymbol = 'USD'
cryptoSymbol = 'BNB'
myTruncate = 3

api_key = '4ylY1TRh4R7vxNhW-6lG_Qq3DkZgMa-JHNPF8Tr0'
api_secret = 'OlBlqYozzwJsuOXi2P8IFRBqi4QW107ji02eGgDf'
subaccount_name = 'ErnestTradingFtxBot'
takerFee = 0.0007

pointage_achat = ernest.get(connection1, "pointage", 3)
pointage_vent = ernest.get(connection1, "pointage", 4)
pointage_pas_op = ernest.get(connection1, "pointage", 2)
pointage_bot = ernest.get(connection1, "pointage", 5)


# ********** les fonction commun ******

def truncate(n, decimals=0):
    r = floor(float(n)*10**decimals)/10**decimals
    return str(r)


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

data = client.get_historical_data(
    market_name=pairSymbol, 
    resolution=3600, 
    limit=1000, 
    start_time=float(round(time.time()))-150*3600, 
    end_time=float(round(time.time())))
df = pd.DataFrame(data)



df['EMA90']=ta.trend.ema_indicator(df['close'], 90)
df['STOCH_RSI']=ta.momentum.stochrsi(df['close'])

ST_length = 20
ST_multiplier = 3.0
superTrend = pda.supertrend(df['high'], df['low'], df['close'], length=ST_length, multiplier=ST_multiplier)
df['SUPER_TREND'] = superTrend['SUPERT_'+str(ST_length)+"_"+str(ST_multiplier)]
df['SUPER_TREND_DIRECTION1'] = superTrend['SUPERTd_'+str(ST_length)+"_"+str(ST_multiplier)]

ST_length = 20
ST_multiplier = 4.0
superTrend = pda.supertrend(df['high'], df['low'], df['close'], length=ST_length, multiplier=ST_multiplier)
df['SUPER_TREND'] = superTrend['SUPERT_'+str(ST_length)+"_"+str(ST_multiplier)]
df['SUPER_TREND_DIRECTION2'] = superTrend['SUPERTd_'+str(ST_length)+"_"+str(ST_multiplier)]

ST_length = 40
ST_multiplier = 8.0
superTrend = pda.supertrend(df['high'], df['low'], df['close'], length=ST_length, multiplier=ST_multiplier)
df['SUPER_TREND'] = superTrend['SUPERT_'+str(ST_length)+"_"+str(ST_multiplier)]
df['SUPER_TREND_DIRECTION3'] = superTrend['SUPERTd_'+str(ST_length)+"_"+str(ST_multiplier)]
#print(df)



# ****************************************************************
#      1 debut super trend 
# ****************************************************************


# ******* Recuperation des informations general sur le bot  *****

table = "bot_39"
nom_bot = ernest.get(connection1, table, 1)
nom_crypto = ernest.get(connection1, table, 2)
nombre_crypto = ernest.get(connection1, table, 3)
usdt = ernest.get(connection1, table, 5)

total_trad = ernest.get(connection1, table, 8)
positif_trad = ernest.get(connection1, table, 9)
negatif_trad = ernest.get(connection1, table, 10)
status = ernest.get(connection1, table, 11)
prix_achat 	= ernest.get(connection1, table, 13)
actif 	= ernest.get(connection1, table, 15)

# ****************************************************************

messages = nom_bot
telegram_send.send(messages=[messages])

client = ftx.FtxClient(api_key = api_key,
                   api_secret = api_secret, subaccount_name=subaccount_name)


    
# fiatAmount = getBalance(client, fiatSymbol)
# cryptoAmount = getBalance(client, cryptoSymbol)
fiatAmount = usdt
cryptoAmount = nombre_crypto
actualPrice = df['close'].iloc[-1]
minToken = 5/actualPrice
print('coin price :',actualPrice, 'usd balance', fiatAmount, 'coin balance :',cryptoAmount)

if df['SUPER_TREND_DIRECTION1'].iloc[-2] >= 1 and df['close'].iloc[-2] > df['EMA90'].iloc[-2] and df['STOCH_RSI'].iloc[-2] < 0.8 and actif == 1 and ( status == "Libre" or status == "Achat seul" ) :
    if float(fiatAmount) > 5:
        
        messages = " condition d'achat valider "
        telegram_send.send(messages=[messages])
        
        quantityBuy = truncate(float(fiatAmount)/actualPrice, myTruncate)
        # buyOrder = client.place_order(
        #     market=pairSymbol, 
        #     side="buy", 
        #     price=None, 
        #     size=quantityBuy, 
        #     type='market')
        # print("BUY", buyOrder)

        messages = "Achat de " + str(quantityBuy) + " " + cryptoSymbol + " a " + str(actualPrice)
        telegram_send.send(messages=[messages])
        
        # ernest information pour la base de donner
        nombre_crypto = quantityBuy
        valeur_crypto = quantityBuy * actualPrice
        usdt = 0
        indicateurs1 = df['TRIX_HISTO'].iloc[-1]
        indicatuer2 = df['STOCH_RSI'].iloc[-1]
        total_trad = total_trad
        operation = "Achat"
        prix_achat = actualPrice
        prix_actuel = actualPrice
        
        ernest.insert(connection1, table, nom_bot, nom_crypto, nombre_crypto, valeur_crypto, usdt, indicateurs1, indicatuer2, total_trad, positif_trad, negatif_trad, status, operation, prix_achat, actif, prix_actuel)
        
        tab = "transactions"
        ernest.insertTranscation(connection1, tab, nom_crypto, operation, valeur_crypto, usdt, nom_bot, status)
        
        
        pointage_achat += 1
        pointage_bot += 1

        
    else:
        print("If you  give me more USD I will buy more",cryptoSymbol)
        messages = " Condition d'achat valider, mais il ne faut plus de " + fiatSymbol + " pour acheter des " + cryptoSymbol
        telegram_send.send(messages=[messages])
        pointage_pas_op += 1
        pointage_bot += 1

elif df['SUPER_TREND_DIRECTION1'].iloc[-2] < 1 and df['STOCH_RSI'].iloc[-2] > 0.2 and actif == 1 and ( status == "Libre" or status == "Vente seul" ) :
    if float(cryptoAmount) > minToken:
        
        messages = " condition de vante valider "
        telegram_send.send(messages=[messages])
        
        # sellOrder = client.place_order(
        #     market=pairSymbol, 
        #     side="sell", 
        #     price=None, 
        #     size=truncate(cryptoAmount, myTruncate), 
        #     type='market')
        # print("SELL", sellOrder)

        messages = "Vente de " + str(cryptoAmount) + " " + cryptoSymbol  + " a " + str(actualPrice)
        telegram_send.send(messages=[messages])
        
        # ernest information pour la base de donner
        
        usdt = nombre_crypto * actualPrice 
        frais_transaction = takerFee * usdt
        usdt = usdt - frais_transaction
        
        nombre_crypto = 0
        valeur_crypto = 0 
        
        indicateurs1 = df['TRIX_HISTO'].iloc[-1]
        indicatuer2 = df['STOCH_RSI'].iloc[-1]
        total_trad += 1
        operation = "Vente"
        
        if actualPrice > prix_achat:
            positif_trad += 1
        else:
            negatif_trad += 1
            
        prix_achat = actualPrice
        prix_actuel = actualPrice
        
        ernest.insert(connection1, table, nom_bot, nom_crypto, nombre_crypto, valeur_crypto, usdt, indicateurs1, indicatuer2, total_trad, positif_trad, negatif_trad, status, operation, prix_achat, actif, prix_actuel)
        
        tab = "transactions"
        ernest.insertTranscation(connection1, tab, nom_crypto, operation, valeur_crypto, usdt, nom_bot, status)
        
        
        pointage_vent += 1
        pointage_bot += 1

        
    else:
        print("If you give me more",cryptoSymbol,"I will sell it")
        messages = " Condition de vente valider, mais il ne faut plus de " + cryptoSymbol + " pour vendre " 
        telegram_send.send(messages=[messages])
        pointage_pas_op += 1
        pointage_bot += 1
     
else :
    print("No opportunity to take")
    # messages = "Pas d'opportuniter de trade" 
    # telegram_send.send(messages=[messages])
    pointage_pas_op += 1
    pointage_bot += 1



modifierId = ernest.get(connection1, table, 0)
ernest.updateActuelPrix(connection1,table,actualPrice,modifierId)

sleep(2)
# ****************************************************************
#      1 fin super trend 1
# ****************************************************************









# ****************************************************************
#      1s debut super trend 1s
# ****************************************************************


# ******* Recuperation des informations general sur le bot  *****

table = "bot_40"
nom_bot = ernest.get(connection1, table, 1)
nom_crypto = ernest.get(connection1, table, 2)
nombre_crypto = ernest.get(connection1, table, 3)
usdt = ernest.get(connection1, table, 5)

total_trad = ernest.get(connection1, table, 8)
positif_trad = ernest.get(connection1, table, 9)
negatif_trad = ernest.get(connection1, table, 10)
status = ernest.get(connection1, table, 11)
prix_achat 	= ernest.get(connection1, table, 13)
actif 	= ernest.get(connection1, table, 15)

# ****************************************************************

messages = nom_bot
telegram_send.send(messages=[messages])

client = ftx.FtxClient(api_key = api_key,
                   api_secret = api_secret, subaccount_name=subaccount_name)


    
# fiatAmount = getBalance(client, fiatSymbol)
# cryptoAmount = getBalance(client, cryptoSymbol)
fiatAmount = usdt
cryptoAmount = nombre_crypto
actualPrice = df['close'].iloc[-1]
minToken = 5/actualPrice
print('coin price :',actualPrice, 'usd balance', fiatAmount, 'coin balance :',cryptoAmount)

if df['SUPER_TREND_DIRECTION1'].iloc[-2] >= 1 and df['close'].iloc[-2] > df['EMA90'].iloc[-2] and df['STOCH_RSI'].iloc[-2] < 0.8 and actif == 1 and ( status == "Libre" or status == "Achat seul" ) :
    if float(fiatAmount) > 5:
        
        messages = " condition d'achat valider "
        telegram_send.send(messages=[messages])
        
        quantityBuy = truncate(float(fiatAmount)/actualPrice, myTruncate)
        # buyOrder = client.place_order(
        #     market=pairSymbol, 
        #     side="buy", 
        #     price=None, 
        #     size=quantityBuy, 
        #     type='market')
        # print("BUY", buyOrder)

        messages = "Achat de " + str(quantityBuy) + " " + cryptoSymbol + " a " + str(actualPrice)
        telegram_send.send(messages=[messages])
        
        # ernest information pour la base de donner
        nombre_crypto = quantityBuy
        valeur_crypto = quantityBuy * actualPrice
        usdt = 0
        indicateurs1 = df['TRIX_HISTO'].iloc[-1]
        indicatuer2 = df['STOCH_RSI'].iloc[-1]
        total_trad = total_trad
        operation = "Achat"
        prix_achat = actualPrice
        prix_actuel = actualPrice
        
        ernest.insert(connection1, table, nom_bot, nom_crypto, nombre_crypto, valeur_crypto, usdt, indicateurs1, indicatuer2, total_trad, positif_trad, negatif_trad, status, operation, prix_achat, actif, prix_actuel)
        
        tab = "transactions"
        ernest.insertTranscation(connection1, tab, nom_crypto, operation, valeur_crypto, usdt, nom_bot, status)
        
        
        pointage_achat += 1
        pointage_bot += 1

        
    else:
        print("If you  give me more USD I will buy more",cryptoSymbol)
        messages = " Condition d'achat valider, mais il ne faut plus de " + fiatSymbol + " pour acheter des " + cryptoSymbol
        telegram_send.send(messages=[messages])
        pointage_pas_op += 1
        pointage_bot += 1
    

elif df['SUPER_TREND_DIRECTION1'].iloc[-2] < 1 and df['STOCH_RSI'].iloc[-2] > 0.2 and actif == 1 and ( status == "Libre" or status == "Vente seul" ) :
    if float(cryptoAmount) > minToken and actualPrice > prix_achat:
        
        messages = " condition de vante valider "
        telegram_send.send(messages=[messages])
        
        # sellOrder = client.place_order(
        #     market=pairSymbol, 
        #     side="sell", 
        #     price=None, 
        #     size=truncate(cryptoAmount, myTruncate), 
        #     type='market')
        # print("SELL", sellOrder)
        
        messages = "Vente de " + str(cryptoAmount) + " " + cryptoSymbol  + " a " + str(actualPrice)
        telegram_send.send(messages=[messages])

        # ernest information pour la base de donner
        
        usdt = nombre_crypto * actualPrice 
        frais_transaction = takerFee * usdt
        usdt = usdt - frais_transaction
        
        nombre_crypto = 0
        valeur_crypto = 0 
        
        indicateurs1 = df['TRIX_HISTO'].iloc[-1]
        indicatuer2 = df['STOCH_RSI'].iloc[-1]
        total_trad += 1
        operation = "Vente"
        
        if actualPrice > prix_achat:
            positif_trad += 1
        else:
            negatif_trad += 1
            
        prix_achat = actualPrice
        prix_actuel = actualPrice
        
        ernest.insert(connection1, table, nom_bot, nom_crypto, nombre_crypto, valeur_crypto, usdt, indicateurs1, indicatuer2, total_trad, positif_trad, negatif_trad, status, operation, prix_achat, actif, prix_actuel)
        
        tab = "transactions"
        ernest.insertTranscation(connection1, tab, nom_crypto, operation, valeur_crypto, usdt, nom_bot, status)
        
        
        pointage_vent += 1
        pointage_bot += 1

        
    else:
        print("If you give me more",cryptoSymbol,"I will sell it")
        messages = " Condition de vente valider, mais il ne faut plus de " + cryptoSymbol + " pour vendre " 
        telegram_send.send(messages=[messages])
        pointage_pas_op += 1
        pointage_bot += 1
else :
    print("No opportunity to take")
    # messages = "Pas d'opportuniter de trade" 
    # telegram_send.send(messages=[messages])
    pointage_pas_op += 1
    pointage_bot += 1



modifierId = ernest.get(connection1, table, 0)
ernest.updateActuelPrix(connection1,table,actualPrice,modifierId)

sleep(2)
# ****************************************************************
#      1s fin super trend 1s
# ****************************************************************



# ***************************************************************************************************



# ****************************************************************
#      2 debut super trend 
# ****************************************************************


# ******* Recuperation des informations general sur le bot  *****

table = "bot_41"
nom_bot = ernest.get(connection1, table, 1)
nom_crypto = ernest.get(connection1, table, 2)
nombre_crypto = ernest.get(connection1, table, 3)
usdt = ernest.get(connection1, table, 5)

total_trad = ernest.get(connection1, table, 8)
positif_trad = ernest.get(connection1, table, 9)
negatif_trad = ernest.get(connection1, table, 10)
status = ernest.get(connection1, table, 11)
prix_achat 	= ernest.get(connection1, table, 13)
actif 	= ernest.get(connection1, table, 15)

# ****************************************************************

messages = nom_bot
telegram_send.send(messages=[messages])

client = ftx.FtxClient(api_key = api_key,
                   api_secret = api_secret, subaccount_name=subaccount_name)


    
# fiatAmount = getBalance(client, fiatSymbol)
# cryptoAmount = getBalance(client, cryptoSymbol)
fiatAmount = usdt
cryptoAmount = nombre_crypto
actualPrice = df['close'].iloc[-1]
minToken = 5/actualPrice
print('coin price :',actualPrice, 'usd balance', fiatAmount, 'coin balance :',cryptoAmount)

if df['SUPER_TREND_DIRECTION2'].iloc[-2] >= 1 and df['close'].iloc[-2] > df['EMA90'].iloc[-2] and df['STOCH_RSI'].iloc[-2] < 0.8 and actif == 1 and ( status == "Libre" or status == "Achat seul" ) :
    if float(fiatAmount) > 5:
        
        messages = " condition d'achat valider "
        telegram_send.send(messages=[messages])
        
        quantityBuy = truncate(float(fiatAmount)/actualPrice, myTruncate)
        # buyOrder = client.place_order(
        #     market=pairSymbol, 
        #     side="buy", 
        #     price=None, 
        #     size=quantityBuy, 
        #     type='market')
        # print("BUY", buyOrder)

        messages = "Achat de " + str(quantityBuy) + " " + cryptoSymbol + " a " + str(actualPrice)
        telegram_send.send(messages=[messages])
        
        # ernest information pour la base de donner
        nombre_crypto = quantityBuy
        valeur_crypto = quantityBuy * actualPrice
        usdt = 0
        indicateurs1 = df['TRIX_HISTO'].iloc[-1]
        indicatuer2 = df['STOCH_RSI'].iloc[-1]
        total_trad = total_trad
        operation = "Achat"
        prix_achat = actualPrice
        prix_actuel = actualPrice
        
        ernest.insert(connection1, table, nom_bot, nom_crypto, nombre_crypto, valeur_crypto, usdt, indicateurs1, indicatuer2, total_trad, positif_trad, negatif_trad, status, operation, prix_achat, actif, prix_actuel)
        
        tab = "transactions"
        ernest.insertTranscation(connection1, tab, nom_crypto, operation, valeur_crypto, usdt, nom_bot, status)
        
        
        pointage_achat += 1
        pointage_bot += 1

        
    else:
        print("If you  give me more USD I will buy more",cryptoSymbol)
        messages = " Condition d'achat valider, mais il ne faut plus de " + fiatSymbol + " pour acheter des " + cryptoSymbol
        telegram_send.send(messages=[messages])
        pointage_pas_op += 1
        pointage_bot += 1

elif df['SUPER_TREND_DIRECTION2'].iloc[-2] < 1 and df['STOCH_RSI'].iloc[-2] > 0.2 and actif == 1 and ( status == "Libre" or status == "Vente seul" ) :
    if float(cryptoAmount) > minToken:
        
        messages = " condition de vante valider "
        telegram_send.send(messages=[messages])
        
        # sellOrder = client.place_order(
        #     market=pairSymbol, 
        #     side="sell", 
        #     price=None, 
        #     size=truncate(cryptoAmount, myTruncate), 
        #     type='market')
        # print("SELL", sellOrder)

        messages = "Vente de " + str(cryptoAmount) + " " + cryptoSymbol  + " a " + str(actualPrice)
        telegram_send.send(messages=[messages])
        
        # ernest information pour la base de donner
        
        usdt = nombre_crypto * actualPrice 
        frais_transaction = takerFee * usdt
        usdt = usdt - frais_transaction
        
        nombre_crypto = 0
        valeur_crypto = 0 
        
        indicateurs1 = df['TRIX_HISTO'].iloc[-1]
        indicatuer2 = df['STOCH_RSI'].iloc[-1]
        total_trad += 1
        operation = "Vente"
        
        if actualPrice > prix_achat:
            positif_trad += 1
        else:
            negatif_trad += 1
            
        prix_achat = actualPrice
        prix_actuel = actualPrice
        
        ernest.insert(connection1, table, nom_bot, nom_crypto, nombre_crypto, valeur_crypto, usdt, indicateurs1, indicatuer2, total_trad, positif_trad, negatif_trad, status, operation, prix_achat, actif, prix_actuel)
        
        tab = "transactions"
        ernest.insertTranscation(connection1, tab, nom_crypto, operation, valeur_crypto, usdt, nom_bot, status)
        
        
        pointage_vent += 1
        pointage_bot += 1

        
    else:
        print("If you give me more",cryptoSymbol,"I will sell it")
        messages = " Condition de vente valider, mais il ne faut plus de " + cryptoSymbol + " pour vendre " 
        telegram_send.send(messages=[messages])
        pointage_pas_op += 1
        pointage_bot += 1
     
else :
    print("No opportunity to take")
    # messages = "Pas d'opportuniter de trade" 
    # telegram_send.send(messages=[messages])
    pointage_pas_op += 1
    pointage_bot += 1



modifierId = ernest.get(connection1, table, 0)
ernest.updateActuelPrix(connection1,table,actualPrice,modifierId)

sleep(2)
# ****************************************************************
#      2 fin super trend 2
# ****************************************************************





# ****************************************************************
#      2s debut super trend 2s
# ****************************************************************


# ******* Recuperation des informations general sur le bot  *****

table = "bot_42"
nom_bot = ernest.get(connection1, table, 1)
nom_crypto = ernest.get(connection1, table, 2)
nombre_crypto = ernest.get(connection1, table, 3)
usdt = ernest.get(connection1, table, 5)

total_trad = ernest.get(connection1, table, 8)
positif_trad = ernest.get(connection1, table, 9)
negatif_trad = ernest.get(connection1, table, 10)
status = ernest.get(connection1, table, 11)
prix_achat 	= ernest.get(connection1, table, 13)
actif 	= ernest.get(connection1, table, 15)

# ****************************************************************

messages = nom_bot
telegram_send.send(messages=[messages])

client = ftx.FtxClient(api_key = api_key,
                   api_secret = api_secret, subaccount_name=subaccount_name)


    
# fiatAmount = getBalance(client, fiatSymbol)
# cryptoAmount = getBalance(client, cryptoSymbol)
fiatAmount = usdt
cryptoAmount = nombre_crypto
actualPrice = df['close'].iloc[-1]
minToken = 5/actualPrice
print('coin price :',actualPrice, 'usd balance', fiatAmount, 'coin balance :',cryptoAmount)

if df['SUPER_TREND_DIRECTION2'].iloc[-2] >= 1 and df['close'].iloc[-2] > df['EMA90'].iloc[-2] and df['STOCH_RSI'].iloc[-2] < 0.8 and actif == 1 and ( status == "Libre" or status == "Achat seul" ) :
    if float(fiatAmount) > 5:
        
        messages = " condition d'achat valider "
        telegram_send.send(messages=[messages])
        
        quantityBuy = truncate(float(fiatAmount)/actualPrice, myTruncate)
        # buyOrder = client.place_order(
        #     market=pairSymbol, 
        #     side="buy", 
        #     price=None, 
        #     size=quantityBuy, 
        #     type='market')
        # print("BUY", buyOrder)

        messages = "Achat de " + str(quantityBuy) + " " + cryptoSymbol + " a " + str(actualPrice)
        telegram_send.send(messages=[messages])
        
        # ernest information pour la base de donner
        nombre_crypto = quantityBuy
        valeur_crypto = quantityBuy * actualPrice
        usdt = 0
        indicateurs1 = df['TRIX_HISTO'].iloc[-1]
        indicatuer2 = df['STOCH_RSI'].iloc[-1]
        total_trad = total_trad
        operation = "Achat"
        prix_achat = actualPrice
        prix_actuel = actualPrice
        
        ernest.insert(connection1, table, nom_bot, nom_crypto, nombre_crypto, valeur_crypto, usdt, indicateurs1, indicatuer2, total_trad, positif_trad, negatif_trad, status, operation, prix_achat, actif, prix_actuel)
        
        tab = "transactions"
        ernest.insertTranscation(connection1, tab, nom_crypto, operation, valeur_crypto, usdt, nom_bot, status)
        
        
        pointage_achat += 1
        pointage_bot += 1

        
    else:
        print("If you  give me more USD I will buy more",cryptoSymbol)
        messages = " Condition d'achat valider, mais il ne faut plus de " + fiatSymbol + " pour acheter des " + cryptoSymbol
        telegram_send.send(messages=[messages])
        pointage_pas_op += 1
        pointage_bot += 1
    

elif df['SUPER_TREND_DIRECTION2'].iloc[-2] < 1 and df['STOCH_RSI'].iloc[-2] > 0.2 and actif == 1 and ( status == "Libre" or status == "Vente seul" ) :
    if float(cryptoAmount) > minToken and actualPrice > prix_achat:
        
        messages = " condition de vante valider "
        telegram_send.send(messages=[messages])
        
        # sellOrder = client.place_order(
        #     market=pairSymbol, 
        #     side="sell", 
        #     price=None, 
        #     size=truncate(cryptoAmount, myTruncate), 
        #     type='market')
        # print("SELL", sellOrder)
        
        messages = "Vente de " + str(cryptoAmount) + " " + cryptoSymbol  + " a " + str(actualPrice)
        telegram_send.send(messages=[messages])

        # ernest information pour la base de donner
        
        usdt = nombre_crypto * actualPrice 
        frais_transaction = takerFee * usdt
        usdt = usdt - frais_transaction
        
        nombre_crypto = 0
        valeur_crypto = 0 
        
        indicateurs1 = df['TRIX_HISTO'].iloc[-1]
        indicatuer2 = df['STOCH_RSI'].iloc[-1]
        total_trad += 1
        operation = "Vente"
        
        if actualPrice > prix_achat:
            positif_trad += 1
        else:
            negatif_trad += 1
            
        prix_achat = actualPrice
        prix_actuel = actualPrice
        
        ernest.insert(connection1, table, nom_bot, nom_crypto, nombre_crypto, valeur_crypto, usdt, indicateurs1, indicatuer2, total_trad, positif_trad, negatif_trad, status, operation, prix_achat, actif, prix_actuel)
        
        tab = "transactions"
        ernest.insertTranscation(connection1, tab, nom_crypto, operation, valeur_crypto, usdt, nom_bot, status)
        
        
        pointage_vent += 1
        pointage_bot += 1

        
    else:
        print("If you give me more",cryptoSymbol,"I will sell it")
        messages = " Condition de vente valider, mais il ne faut plus de " + cryptoSymbol + " pour vendre " 
        telegram_send.send(messages=[messages])
        pointage_pas_op += 1
        pointage_bot += 1
else :
    print("No opportunity to take")
    # messages = "Pas d'opportuniter de trade" 
    # telegram_send.send(messages=[messages])
    pointage_pas_op += 1
    pointage_bot += 1



modifierId = ernest.get(connection1, table, 0)
ernest.updateActuelPrix(connection1,table,actualPrice,modifierId)

sleep(2)
# ****************************************************************
#      2s fin super trend 2s
# ****************************************************************


# **********************************************************************************************************************************


# ****************************************************************
#     3 debut super trend 
# ****************************************************************


# ******* Recuperation des informations general sur le bot  *****

table = "bot_43"
nom_bot = ernest.get(connection1, table, 1)
nom_crypto = ernest.get(connection1, table, 2)
nombre_crypto = ernest.get(connection1, table, 3)
usdt = ernest.get(connection1, table, 5)

total_trad = ernest.get(connection1, table, 8)
positif_trad = ernest.get(connection1, table, 9)
negatif_trad = ernest.get(connection1, table, 10)
status = ernest.get(connection1, table, 11)
prix_achat 	= ernest.get(connection1, table, 13)
actif 	= ernest.get(connection1, table, 15)

# ****************************************************************

messages = nom_bot
telegram_send.send(messages=[messages])

client = ftx.FtxClient(api_key = api_key,
                   api_secret = api_secret, subaccount_name=subaccount_name)


    
# fiatAmount = getBalance(client, fiatSymbol)
# cryptoAmount = getBalance(client, cryptoSymbol)
fiatAmount = usdt
cryptoAmount = nombre_crypto
actualPrice = df['close'].iloc[-1]
minToken = 5/actualPrice
print('coin price :',actualPrice, 'usd balance', fiatAmount, 'coin balance :',cryptoAmount)

if df['SUPER_TREND_DIRECTION3'].iloc[-2] >= 1 and df['close'].iloc[-2] > df['EMA90'].iloc[-2] and df['STOCH_RSI'].iloc[-2] < 0.8 and actif == 1 and ( status == "Libre" or status == "Achat seul" ) :
    if float(fiatAmount) > 5:
        
        messages = " condition d'achat valider "
        telegram_send.send(messages=[messages])
        
        quantityBuy = truncate(float(fiatAmount)/actualPrice, myTruncate)
        # buyOrder = client.place_order(
        #     market=pairSymbol, 
        #     side="buy", 
        #     price=None, 
        #     size=quantityBuy, 
        #     type='market')
        # print("BUY", buyOrder)

        messages = "Achat de " + str(quantityBuy) + " " + cryptoSymbol + " a " + str(actualPrice)
        telegram_send.send(messages=[messages])
        
        # ernest information pour la base de donner
        nombre_crypto = quantityBuy
        valeur_crypto = quantityBuy * actualPrice
        usdt = 0
        indicateurs1 = df['TRIX_HISTO'].iloc[-1]
        indicatuer2 = df['STOCH_RSI'].iloc[-1]
        total_trad = total_trad
        operation = "Achat"
        prix_achat = actualPrice
        prix_actuel = actualPrice
        
        ernest.insert(connection1, table, nom_bot, nom_crypto, nombre_crypto, valeur_crypto, usdt, indicateurs1, indicatuer2, total_trad, positif_trad, negatif_trad, status, operation, prix_achat, actif, prix_actuel)
        
        tab = "transactions"
        ernest.insertTranscation(connection1, tab, nom_crypto, operation, valeur_crypto, usdt, nom_bot, status)
        
        
        pointage_achat += 1
        pointage_bot += 1

        
    else:
        print("If you  give me more USD I will buy more",cryptoSymbol)
        messages = " Condition d'achat valider, mais il ne faut plus de " + fiatSymbol + " pour acheter des " + cryptoSymbol
        telegram_send.send(messages=[messages])
        pointage_pas_op += 1
        pointage_bot += 1

elif df['SUPER_TREND_DIRECTION3'].iloc[-2] < 1 and df['STOCH_RSI'].iloc[-2] > 0.2 and actif == 1 and ( status == "Libre" or status == "Vente seul" ) :
    if float(cryptoAmount) > minToken:
        
        messages = " condition de vante valider "
        telegram_send.send(messages=[messages])
        
        # sellOrder = client.place_order(
        #     market=pairSymbol, 
        #     side="sell", 
        #     price=None, 
        #     size=truncate(cryptoAmount, myTruncate), 
        #     type='market')
        # print("SELL", sellOrder)

        messages = "Vente de " + str(cryptoAmount) + " " + cryptoSymbol  + " a " + str(actualPrice)
        telegram_send.send(messages=[messages])
        
        # ernest information pour la base de donner
        
        usdt = nombre_crypto * actualPrice 
        frais_transaction = takerFee * usdt
        usdt = usdt - frais_transaction
        
        nombre_crypto = 0
        valeur_crypto = 0 
        
        indicateurs1 = df['TRIX_HISTO'].iloc[-1]
        indicatuer2 = df['STOCH_RSI'].iloc[-1]
        total_trad += 1
        operation = "Vente"
        
        if actualPrice > prix_achat:
            positif_trad += 1
        else:
            negatif_trad += 1
            
        prix_achat = actualPrice
        prix_actuel = actualPrice
        
        ernest.insert(connection1, table, nom_bot, nom_crypto, nombre_crypto, valeur_crypto, usdt, indicateurs1, indicatuer2, total_trad, positif_trad, negatif_trad, status, operation, prix_achat, actif, prix_actuel)
        
        tab = "transactions"
        ernest.insertTranscation(connection1, tab, nom_crypto, operation, valeur_crypto, usdt, nom_bot, status)
        
        
        pointage_vent += 1
        pointage_bot += 1

        
    else:
        print("If you give me more",cryptoSymbol,"I will sell it")
        messages = " Condition de vente valider, mais il ne faut plus de " + cryptoSymbol + " pour vendre " 
        telegram_send.send(messages=[messages])
        pointage_pas_op += 1
        pointage_bot += 1
     
else :
    print("No opportunity to take")
    # messages = "Pas d'opportuniter de trade" 
    # telegram_send.send(messages=[messages])
    pointage_pas_op += 1
    pointage_bot += 1



modifierId = ernest.get(connection1, table, 0)
ernest.updateActuelPrix(connection1,table,actualPrice,modifierId)

sleep(2)
# ****************************************************************
#      3 fin super trend 3
# ****************************************************************









# ****************************************************************
#      3s debut super trend 3s
# ****************************************************************


# ******* Recuperation des informations general sur le bot  *****

table = "bot_44"
nom_bot = ernest.get(connection1, table, 1)
nom_crypto = ernest.get(connection1, table, 2)
nombre_crypto = ernest.get(connection1, table, 3)
usdt = ernest.get(connection1, table, 5)

total_trad = ernest.get(connection1, table, 8)
positif_trad = ernest.get(connection1, table, 9)
negatif_trad = ernest.get(connection1, table, 10)
status = ernest.get(connection1, table, 11)
prix_achat 	= ernest.get(connection1, table, 13)
actif 	= ernest.get(connection1, table, 15)

# ****************************************************************

messages = nom_bot
telegram_send.send(messages=[messages])

client = ftx.FtxClient(api_key = api_key,
                   api_secret = api_secret, subaccount_name=subaccount_name)


    
# fiatAmount = getBalance(client, fiatSymbol)
# cryptoAmount = getBalance(client, cryptoSymbol)
fiatAmount = usdt
cryptoAmount = nombre_crypto
actualPrice = df['close'].iloc[-1]
minToken = 5/actualPrice
print('coin price :',actualPrice, 'usd balance', fiatAmount, 'coin balance :',cryptoAmount)

if df['SUPER_TREND_DIRECTION3'].iloc[-2] >= 1 and df['close'].iloc[-2] > df['EMA90'].iloc[-2] and df['STOCH_RSI'].iloc[-2] < 0.8 and actif == 1 and ( status == "Libre" or status == "Achat seul" ) :
    if float(fiatAmount) > 5:
        
        messages = " condition d'achat valider "
        telegram_send.send(messages=[messages])
        
        quantityBuy = truncate(float(fiatAmount)/actualPrice, myTruncate)
        # buyOrder = client.place_order(
        #     market=pairSymbol, 
        #     side="buy", 
        #     price=None, 
        #     size=quantityBuy, 
        #     type='market')
        # print("BUY", buyOrder)

        messages = "Achat de " + str(quantityBuy) + " " + cryptoSymbol + " a " + str(actualPrice)
        telegram_send.send(messages=[messages])
        
        # ernest information pour la base de donner
        nombre_crypto = quantityBuy
        valeur_crypto = quantityBuy * actualPrice
        usdt = 0
        indicateurs1 = df['TRIX_HISTO'].iloc[-1]
        indicatuer2 = df['STOCH_RSI'].iloc[-1]
        total_trad = total_trad
        operation = "Achat"
        prix_achat = actualPrice
        prix_actuel = actualPrice
        
        ernest.insert(connection1, table, nom_bot, nom_crypto, nombre_crypto, valeur_crypto, usdt, indicateurs1, indicatuer2, total_trad, positif_trad, negatif_trad, status, operation, prix_achat, actif, prix_actuel)
        
        tab = "transactions"
        ernest.insertTranscation(connection1, tab, nom_crypto, operation, valeur_crypto, usdt, nom_bot, status)
        
        
        pointage_achat += 1
        pointage_bot += 1

        
    else:
        print("If you  give me more USD I will buy more",cryptoSymbol)
        messages = " Condition d'achat valider, mais il ne faut plus de " + fiatSymbol + " pour acheter des " + cryptoSymbol
        telegram_send.send(messages=[messages])
        pointage_pas_op += 1
        pointage_bot += 1
    

elif df['SUPER_TREND_DIRECTION3'].iloc[-2] < 1 and df['STOCH_RSI'].iloc[-2] > 0.2 and actif == 1 and ( status == "Libre" or status == "Vente seul" ) :
    if float(cryptoAmount) > minToken and actualPrice > prix_achat:
        
        messages = " condition de vante valider "
        telegram_send.send(messages=[messages])
        
        # sellOrder = client.place_order(
        #     market=pairSymbol, 
        #     side="sell", 
        #     price=None, 
        #     size=truncate(cryptoAmount, myTruncate), 
        #     type='market')
        # print("SELL", sellOrder)
        
        messages = "Vente de " + str(cryptoAmount) + " " + cryptoSymbol  + " a " + str(actualPrice)
        telegram_send.send(messages=[messages])

        # ernest information pour la base de donner
        
        usdt = nombre_crypto * actualPrice 
        frais_transaction = takerFee * usdt
        usdt = usdt - frais_transaction
        
        nombre_crypto = 0
        valeur_crypto = 0 
        
        indicateurs1 = df['TRIX_HISTO'].iloc[-1]
        indicatuer2 = df['STOCH_RSI'].iloc[-1]
        total_trad += 1
        operation = "Vente"
        
        if actualPrice > prix_achat:
            positif_trad += 1
        else:
            negatif_trad += 1
            
        prix_achat = actualPrice
        prix_actuel = actualPrice
        
        ernest.insert(connection1, table, nom_bot, nom_crypto, nombre_crypto, valeur_crypto, usdt, indicateurs1, indicatuer2, total_trad, positif_trad, negatif_trad, status, operation, prix_achat, actif, prix_actuel)
        
        tab = "transactions"
        ernest.insertTranscation(connection1, tab, nom_crypto, operation, valeur_crypto, usdt, nom_bot, status)
        
        
        pointage_vent += 1
        pointage_bot += 1

        
    else:
        print("If you give me more",cryptoSymbol,"I will sell it")
        messages = " Condition de vente valider, mais il ne faut plus de " + cryptoSymbol + " pour vendre " 
        telegram_send.send(messages=[messages])
        pointage_pas_op += 1
        pointage_bot += 1
else :
    print("No opportunity to take")
    # messages = "Pas d'opportuniter de trade" 
    # telegram_send.send(messages=[messages])
    pointage_pas_op += 1
    pointage_bot += 1



modifierId = ernest.get(connection1, table, 0)
ernest.updateActuelPrix(connection1,table,actualPrice,modifierId)

sleep(2)
# ****************************************************************
#      3s fin super trend 3s
# ****************************************************************


# *************************************************************************************************************************





# ****************************************************************
#      1 2 debut super trend 
# ****************************************************************


# ******* Recuperation des informations general sur le bot  *****

table = "bot_45"
nom_bot = ernest.get(connection1, table, 1)
nom_crypto = ernest.get(connection1, table, 2)
nombre_crypto = ernest.get(connection1, table, 3)
usdt = ernest.get(connection1, table, 5)

total_trad = ernest.get(connection1, table, 8)
positif_trad = ernest.get(connection1, table, 9)
negatif_trad = ernest.get(connection1, table, 10)
status = ernest.get(connection1, table, 11)
prix_achat 	= ernest.get(connection1, table, 13)
actif 	= ernest.get(connection1, table, 15)

# ****************************************************************

messages = nom_bot
telegram_send.send(messages=[messages])

client = ftx.FtxClient(api_key = api_key,
                   api_secret = api_secret, subaccount_name=subaccount_name)


    
# fiatAmount = getBalance(client, fiatSymbol)
# cryptoAmount = getBalance(client, cryptoSymbol)
fiatAmount = usdt
cryptoAmount = nombre_crypto
actualPrice = df['close'].iloc[-1]
minToken = 5/actualPrice
print('coin price :',actualPrice, 'usd balance', fiatAmount, 'coin balance :',cryptoAmount)

if df['SUPER_TREND_DIRECTION1'].iloc[-2]+df['SUPER_TREND_DIRECTION2'].iloc[-2] >= 1 and df['close'].iloc[-2] > df['EMA90'].iloc[-2] and df['STOCH_RSI'].iloc[-2] < 0.8 and actif == 1 and ( status == "Libre" or status == "Achat seul" ) :
    if float(fiatAmount) > 5:
        
        messages = " condition d'achat valider "
        telegram_send.send(messages=[messages])
        
        quantityBuy = truncate(float(fiatAmount)/actualPrice, myTruncate)
        # buyOrder = client.place_order(
        #     market=pairSymbol, 
        #     side="buy", 
        #     price=None, 
        #     size=quantityBuy, 
        #     type='market')
        # print("BUY", buyOrder)

        messages = "Achat de " + str(quantityBuy) + " " + cryptoSymbol + " a " + str(actualPrice)
        telegram_send.send(messages=[messages])
        
        # ernest information pour la base de donner
        nombre_crypto = quantityBuy
        valeur_crypto = quantityBuy * actualPrice
        usdt = 0
        indicateurs1 = df['TRIX_HISTO'].iloc[-1]
        indicatuer2 = df['STOCH_RSI'].iloc[-1]
        total_trad = total_trad
        operation = "Achat"
        prix_achat = actualPrice
        prix_actuel = actualPrice
        
        ernest.insert(connection1, table, nom_bot, nom_crypto, nombre_crypto, valeur_crypto, usdt, indicateurs1, indicatuer2, total_trad, positif_trad, negatif_trad, status, operation, prix_achat, actif, prix_actuel)
        
        tab = "transactions"
        ernest.insertTranscation(connection1, tab, nom_crypto, operation, valeur_crypto, usdt, nom_bot, status)
        
        
        pointage_achat += 1
        pointage_bot += 1

        
    else:
        print("If you  give me more USD I will buy more",cryptoSymbol)
        messages = " Condition d'achat valider, mais il ne faut plus de " + fiatSymbol + " pour acheter des " + cryptoSymbol
        telegram_send.send(messages=[messages])
        pointage_pas_op += 1
        pointage_bot += 1

elif df['SUPER_TREND_DIRECTION1'].iloc[-2]+df['SUPER_TREND_DIRECTION2'].iloc[-2] < 1 and df['STOCH_RSI'].iloc[-2] > 0.2 and actif == 1 and ( status == "Libre" or status == "Vente seul" ) :
    if float(cryptoAmount) > minToken:
        
        messages = " condition de vante valider "
        telegram_send.send(messages=[messages])
        
        # sellOrder = client.place_order(
        #     market=pairSymbol, 
        #     side="sell", 
        #     price=None, 
        #     size=truncate(cryptoAmount, myTruncate), 
        #     type='market')
        # print("SELL", sellOrder)

        messages = "Vente de " + str(cryptoAmount) + " " + cryptoSymbol  + " a " + str(actualPrice)
        telegram_send.send(messages=[messages])
        
        # ernest information pour la base de donner
        
        usdt = nombre_crypto * actualPrice 
        frais_transaction = takerFee * usdt
        usdt = usdt - frais_transaction
        
        nombre_crypto = 0
        valeur_crypto = 0 
        
        indicateurs1 = df['TRIX_HISTO'].iloc[-1]
        indicatuer2 = df['STOCH_RSI'].iloc[-1]
        total_trad += 1
        operation = "Vente"
        
        if actualPrice > prix_achat:
            positif_trad += 1
        else:
            negatif_trad += 1
            
        prix_achat = actualPrice
        prix_actuel = actualPrice
        
        ernest.insert(connection1, table, nom_bot, nom_crypto, nombre_crypto, valeur_crypto, usdt, indicateurs1, indicatuer2, total_trad, positif_trad, negatif_trad, status, operation, prix_achat, actif, prix_actuel)
        
        tab = "transactions"
        ernest.insertTranscation(connection1, tab, nom_crypto, operation, valeur_crypto, usdt, nom_bot, status)
        
        
        pointage_vent += 1
        pointage_bot += 1

        
    else:
        print("If you give me more",cryptoSymbol,"I will sell it")
        messages = " Condition de vente valider, mais il ne faut plus de " + cryptoSymbol + " pour vendre " 
        telegram_send.send(messages=[messages])
        pointage_pas_op += 1
        pointage_bot += 1
     
else :
    print("No opportunity to take")
    messages = "Pas d'opportuniter de trade" 
    telegram_send.send(messages=[messages])
    pointage_pas_op += 1
    pointage_bot += 1



modifierId = ernest.get(connection1, table, 0)
ernest.updateActuelPrix(connection1,table,actualPrice,modifierId)

sleep(2)
# ****************************************************************
#      1 2 fin super trend 1 2
# ****************************************************************






# ****************************************************************
#      1s debut super trend 1s
# ****************************************************************


# ******* Recuperation des informations general sur le bot  *****

table = "bot_46"
nom_bot = ernest.get(connection1, table, 1)
nom_crypto = ernest.get(connection1, table, 2)
nombre_crypto = ernest.get(connection1, table, 3)
usdt = ernest.get(connection1, table, 5)

total_trad = ernest.get(connection1, table, 8)
positif_trad = ernest.get(connection1, table, 9)
negatif_trad = ernest.get(connection1, table, 10)
status = ernest.get(connection1, table, 11)
prix_achat 	= ernest.get(connection1, table, 13)
actif 	= ernest.get(connection1, table, 15)

# ****************************************************************

messages = nom_bot
telegram_send.send(messages=[messages])

client = ftx.FtxClient(api_key = api_key,
                   api_secret = api_secret, subaccount_name=subaccount_name)


    
# fiatAmount = getBalance(client, fiatSymbol)
# cryptoAmount = getBalance(client, cryptoSymbol)
fiatAmount = usdt
cryptoAmount = nombre_crypto
actualPrice = df['close'].iloc[-1]
minToken = 5/actualPrice
print('coin price :',actualPrice, 'usd balance', fiatAmount, 'coin balance :',cryptoAmount)

if df['SUPER_TREND_DIRECTION1'].iloc[-2]+df['SUPER_TREND_DIRECTION2'].iloc[-2] >= 1 and df['close'].iloc[-2] > df['EMA90'].iloc[-2] and df['STOCH_RSI'].iloc[-2] < 0.8 and actif == 1 and ( status == "Libre" or status == "Achat seul" ) :
    if float(fiatAmount) > 5:
        
        messages = " condition d'achat valider "
        telegram_send.send(messages=[messages])
        
        quantityBuy = truncate(float(fiatAmount)/actualPrice, myTruncate)
        # buyOrder = client.place_order(
        #     market=pairSymbol, 
        #     side="buy", 
        #     price=None, 
        #     size=quantityBuy, 
        #     type='market')
        # print("BUY", buyOrder)

        messages = "Achat de " + str(quantityBuy) + " " + cryptoSymbol + " a " + str(actualPrice)
        telegram_send.send(messages=[messages])
        
        # ernest information pour la base de donner
        nombre_crypto = quantityBuy
        valeur_crypto = quantityBuy * actualPrice
        usdt = 0
        indicateurs1 = df['TRIX_HISTO'].iloc[-1]
        indicatuer2 = df['STOCH_RSI'].iloc[-1]
        total_trad = total_trad
        operation = "Achat"
        prix_achat = actualPrice
        prix_actuel = actualPrice
        
        ernest.insert(connection1, table, nom_bot, nom_crypto, nombre_crypto, valeur_crypto, usdt, indicateurs1, indicatuer2, total_trad, positif_trad, negatif_trad, status, operation, prix_achat, actif, prix_actuel)
        
        tab = "transactions"
        ernest.insertTranscation(connection1, tab, nom_crypto, operation, valeur_crypto, usdt, nom_bot, status)
        
        
        pointage_achat += 1
        pointage_bot += 1

        
    else:
        print("If you  give me more USD I will buy more",cryptoSymbol)
        messages = " Condition d'achat valider, mais il ne faut plus de " + fiatSymbol + " pour acheter des " + cryptoSymbol
        telegram_send.send(messages=[messages])
        pointage_pas_op += 1
        pointage_bot += 1
    

elif df['SUPER_TREND_DIRECTION1'].iloc[-2]+df['SUPER_TREND_DIRECTION2'].iloc[-2]< 1 and df['STOCH_RSI'].iloc[-2] > 0.2 and actif == 1 and ( status == "Libre" or status == "Vente seul" ) :
    if float(cryptoAmount) > minToken and actualPrice > prix_achat:
        
        messages = " condition de vante valider "
        telegram_send.send(messages=[messages])
        
        # sellOrder = client.place_order(
        #     market=pairSymbol, 
        #     side="sell", 
        #     price=None, 
        #     size=truncate(cryptoAmount, myTruncate), 
        #     type='market')
        # print("SELL", sellOrder)
        
        messages = "Vente de " + str(cryptoAmount) + " " + cryptoSymbol  + " a " + str(actualPrice)
        telegram_send.send(messages=[messages])

        # ernest information pour la base de donner
        
        usdt = nombre_crypto * actualPrice 
        frais_transaction = takerFee * usdt
        usdt = usdt - frais_transaction
        
        nombre_crypto = 0
        valeur_crypto = 0 
        
        indicateurs1 = df['TRIX_HISTO'].iloc[-1]
        indicatuer2 = df['STOCH_RSI'].iloc[-1]
        total_trad += 1
        operation = "Vente"
        
        if actualPrice > prix_achat:
            positif_trad += 1
        else:
            negatif_trad += 1
            
        prix_achat = actualPrice
        prix_actuel = actualPrice
        
        ernest.insert(connection1, table, nom_bot, nom_crypto, nombre_crypto, valeur_crypto, usdt, indicateurs1, indicatuer2, total_trad, positif_trad, negatif_trad, status, operation, prix_achat, actif, prix_actuel)
        
        tab = "transactions"
        ernest.insertTranscation(connection1, tab, nom_crypto, operation, valeur_crypto, usdt, nom_bot, status)
        
        
        pointage_vent += 1
        pointage_bot += 1

        
    else:
        print("If you give me more",cryptoSymbol,"I will sell it")
        messages = " Condition de vente valider, mais il ne faut plus de " + cryptoSymbol + " pour vendre " 
        telegram_send.send(messages=[messages])
        pointage_pas_op += 1
        pointage_bot += 1
else :
    print("No opportunity to take")
    # messages = "Pas d'opportuniter de trade" 
    # telegram_send.send(messages=[messages])
    pointage_pas_op += 1
    pointage_bot += 1



modifierId = ernest.get(connection1, table, 0)
ernest.updateActuelPrix(connection1,table,actualPrice,modifierId)

sleep(2)
# ****************************************************************
#      1 2s fin super trend 1 2s
# ****************************************************************



# *****************************************************************************************************************************




# ****************************************************************
#      1 debut super trend 
# ****************************************************************


# ******* Recuperation des informations general sur le bot  *****

table = "bot_47"
nom_bot = ernest.get(connection1, table, 1)
nom_crypto = ernest.get(connection1, table, 2)
nombre_crypto = ernest.get(connection1, table, 3)
usdt = ernest.get(connection1, table, 5)

total_trad = ernest.get(connection1, table, 8)
positif_trad = ernest.get(connection1, table, 9)
negatif_trad = ernest.get(connection1, table, 10)
status = ernest.get(connection1, table, 11)
prix_achat 	= ernest.get(connection1, table, 13)
actif 	= ernest.get(connection1, table, 15)

# ****************************************************************

messages = nom_bot
telegram_send.send(messages=[messages])

client = ftx.FtxClient(api_key = api_key,
                   api_secret = api_secret, subaccount_name=subaccount_name)


    
# fiatAmount = getBalance(client, fiatSymbol)
# cryptoAmount = getBalance(client, cryptoSymbol)
fiatAmount = usdt
cryptoAmount = nombre_crypto
actualPrice = df['close'].iloc[-1]
minToken = 5/actualPrice
print('coin price :',actualPrice, 'usd balance', fiatAmount, 'coin balance :',cryptoAmount)

if df['SUPER_TREND_DIRECTION1'].iloc[-2]+df['SUPER_TREND_DIRECTION3'].iloc[-2] >= 1 and df['close'].iloc[-2] > df['EMA90'].iloc[-2] and df['STOCH_RSI'].iloc[-2] < 0.8 and actif == 1 and ( status == "Libre" or status == "Achat seul" ) :
    if float(fiatAmount) > 5:
        
        messages = " condition d'achat valider "
        telegram_send.send(messages=[messages])
        
        quantityBuy = truncate(float(fiatAmount)/actualPrice, myTruncate)
        # buyOrder = client.place_order(
        #     market=pairSymbol, 
        #     side="buy", 
        #     price=None, 
        #     size=quantityBuy, 
        #     type='market')
        # print("BUY", buyOrder)

        messages = "Achat de " + str(quantityBuy) + " " + cryptoSymbol + " a " + str(actualPrice)
        telegram_send.send(messages=[messages])
        
        # ernest information pour la base de donner
        nombre_crypto = quantityBuy
        valeur_crypto = quantityBuy * actualPrice
        usdt = 0
        indicateurs1 = df['TRIX_HISTO'].iloc[-1]
        indicatuer2 = df['STOCH_RSI'].iloc[-1]
        total_trad = total_trad
        operation = "Achat"
        prix_achat = actualPrice
        prix_actuel = actualPrice
        
        ernest.insert(connection1, table, nom_bot, nom_crypto, nombre_crypto, valeur_crypto, usdt, indicateurs1, indicatuer2, total_trad, positif_trad, negatif_trad, status, operation, prix_achat, actif, prix_actuel)
        
        tab = "transactions"
        ernest.insertTranscation(connection1, tab, nom_crypto, operation, valeur_crypto, usdt, nom_bot, status)
        
        
        pointage_achat += 1
        pointage_bot += 1

        
    else:
        print("If you  give me more USD I will buy more",cryptoSymbol)
        messages = " Condition d'achat valider, mais il ne faut plus de " + fiatSymbol + " pour acheter des " + cryptoSymbol
        telegram_send.send(messages=[messages])
        pointage_pas_op += 1
        pointage_bot += 1

elif df['SUPER_TREND_DIRECTION1'].iloc[-2]+df['SUPER_TREND_DIRECTION3'].iloc[-2] < 1 and df['STOCH_RSI'].iloc[-2] > 0.2 and actif == 1 and ( status == "Libre" or status == "Vente seul" ) :
    if float(cryptoAmount) > minToken:
        
        messages = " condition de vante valider "
        telegram_send.send(messages=[messages])
        
        # sellOrder = client.place_order(
        #     market=pairSymbol, 
        #     side="sell", 
        #     price=None, 
        #     size=truncate(cryptoAmount, myTruncate), 
        #     type='market')
        # print("SELL", sellOrder)

        messages = "Vente de " + str(cryptoAmount) + " " + cryptoSymbol  + " a " + str(actualPrice)
        telegram_send.send(messages=[messages])
        
        # ernest information pour la base de donner
        
        usdt = nombre_crypto * actualPrice 
        frais_transaction = takerFee * usdt
        usdt = usdt - frais_transaction
        
        nombre_crypto = 0
        valeur_crypto = 0 
        
        indicateurs1 = df['TRIX_HISTO'].iloc[-1]
        indicatuer2 = df['STOCH_RSI'].iloc[-1]
        total_trad += 1
        operation = "Vente"
        
        if actualPrice > prix_achat:
            positif_trad += 1
        else:
            negatif_trad += 1
            
        prix_achat = actualPrice
        prix_actuel = actualPrice
        
        ernest.insert(connection1, table, nom_bot, nom_crypto, nombre_crypto, valeur_crypto, usdt, indicateurs1, indicatuer2, total_trad, positif_trad, negatif_trad, status, operation, prix_achat, actif, prix_actuel)
        
        tab = "transactions"
        ernest.insertTranscation(connection1, tab, nom_crypto, operation, valeur_crypto, usdt, nom_bot, status)
        
        
        pointage_vent += 1
        pointage_bot += 1

        
    else:
        print("If you give me more",cryptoSymbol,"I will sell it")
        messages = " Condition de vente valider, mais il ne faut plus de " + cryptoSymbol + " pour vendre " 
        telegram_send.send(messages=[messages])
        pointage_pas_op += 1
        pointage_bot += 1
     
else :
    print("No opportunity to take")
    # messages = "Pas d'opportuniter de trade" 
    # telegram_send.send(messages=[messages])
    pointage_pas_op += 1
    pointage_bot += 1



modifierId = ernest.get(connection1, table, 0)
ernest.updateActuelPrix(connection1,table,actualPrice,modifierId)

sleep(2)
# ****************************************************************
#      1 fin super trend 1
# ****************************************************************





# ****************************************************************
#      1s debut super trend 1s
# ****************************************************************


# ******* Recuperation des informations general sur le bot  *****

table = "bot_48"
nom_bot = ernest.get(connection1, table, 1)
nom_crypto = ernest.get(connection1, table, 2)
nombre_crypto = ernest.get(connection1, table, 3)
usdt = ernest.get(connection1, table, 5)

total_trad = ernest.get(connection1, table, 8)
positif_trad = ernest.get(connection1, table, 9)
negatif_trad = ernest.get(connection1, table, 10)
status = ernest.get(connection1, table, 11)
prix_achat 	= ernest.get(connection1, table, 13)
actif 	= ernest.get(connection1, table, 15)

# ****************************************************************

messages = nom_bot
telegram_send.send(messages=[messages])

client = ftx.FtxClient(api_key = api_key,
                   api_secret = api_secret, subaccount_name=subaccount_name)


    
# fiatAmount = getBalance(client, fiatSymbol)
# cryptoAmount = getBalance(client, cryptoSymbol)
fiatAmount = usdt
cryptoAmount = nombre_crypto
actualPrice = df['close'].iloc[-1]
minToken = 5/actualPrice
print('coin price :',actualPrice, 'usd balance', fiatAmount, 'coin balance :',cryptoAmount)

if df['SUPER_TREND_DIRECTION1'].iloc[-2]+df['SUPER_TREND_DIRECTION3'].iloc[-2] >= 1 and df['close'].iloc[-2] > df['EMA90'].iloc[-2] and df['STOCH_RSI'].iloc[-2] < 0.8 and actif == 1 and ( status == "Libre" or status == "Achat seul" ) :
    if float(fiatAmount) > 5:
        
        messages = " condition d'achat valider "
        telegram_send.send(messages=[messages])
        
        quantityBuy = truncate(float(fiatAmount)/actualPrice, myTruncate)
        # buyOrder = client.place_order(
        #     market=pairSymbol, 
        #     side="buy", 
        #     price=None, 
        #     size=quantityBuy, 
        #     type='market')
        # print("BUY", buyOrder)

        messages = "Achat de " + str(quantityBuy) + " " + cryptoSymbol + " a " + str(actualPrice)
        telegram_send.send(messages=[messages])
        
        # ernest information pour la base de donner
        nombre_crypto = quantityBuy
        valeur_crypto = quantityBuy * actualPrice
        usdt = 0
        indicateurs1 = df['TRIX_HISTO'].iloc[-1]
        indicatuer2 = df['STOCH_RSI'].iloc[-1]
        total_trad = total_trad
        operation = "Achat"
        prix_achat = actualPrice
        prix_actuel = actualPrice
        
        ernest.insert(connection1, table, nom_bot, nom_crypto, nombre_crypto, valeur_crypto, usdt, indicateurs1, indicatuer2, total_trad, positif_trad, negatif_trad, status, operation, prix_achat, actif, prix_actuel)
        
        tab = "transactions"
        ernest.insertTranscation(connection1, tab, nom_crypto, operation, valeur_crypto, usdt, nom_bot, status)
        
        
        pointage_achat += 1
        pointage_bot += 1

        
    else:
        print("If you  give me more USD I will buy more",cryptoSymbol)
        messages = " Condition d'achat valider, mais il ne faut plus de " + fiatSymbol + " pour acheter des " + cryptoSymbol
        telegram_send.send(messages=[messages])
        pointage_pas_op += 1
        pointage_bot += 1
    

elif df['SUPER_TREND_DIRECTION1'].iloc[-2]+df['SUPER_TREND_DIRECTION3'].iloc[-2] < 1 and df['STOCH_RSI'].iloc[-2] > 0.2 and actif == 1 and ( status == "Libre" or status == "Vente seul" ) :
    if float(cryptoAmount) > minToken and actualPrice > prix_achat:
        
        messages = " condition de vante valider "
        telegram_send.send(messages=[messages])
        
        # sellOrder = client.place_order(
        #     market=pairSymbol, 
        #     side="sell", 
        #     price=None, 
        #     size=truncate(cryptoAmount, myTruncate), 
        #     type='market')
        # print("SELL", sellOrder)
        
        messages = "Vente de " + str(cryptoAmount) + " " + cryptoSymbol  + " a " + str(actualPrice)
        telegram_send.send(messages=[messages])

        # ernest information pour la base de donner
        
        usdt = nombre_crypto * actualPrice 
        frais_transaction = takerFee * usdt
        usdt = usdt - frais_transaction
        
        nombre_crypto = 0
        valeur_crypto = 0 
        
        indicateurs1 = df['TRIX_HISTO'].iloc[-1]
        indicatuer2 = df['STOCH_RSI'].iloc[-1]
        total_trad += 1
        operation = "Vente"
        
        if actualPrice > prix_achat:
            positif_trad += 1
        else:
            negatif_trad += 1
            
        prix_achat = actualPrice
        prix_actuel = actualPrice
        
        ernest.insert(connection1, table, nom_bot, nom_crypto, nombre_crypto, valeur_crypto, usdt, indicateurs1, indicatuer2, total_trad, positif_trad, negatif_trad, status, operation, prix_achat, actif, prix_actuel)
        
        tab = "transactions"
        ernest.insertTranscation(connection1, tab, nom_crypto, operation, valeur_crypto, usdt, nom_bot, status)
        
        
        pointage_vent += 1
        pointage_bot += 1

        
    else:
        print("If you give me more",cryptoSymbol,"I will sell it")
        messages = " Condition de vente valider, mais il ne faut plus de " + cryptoSymbol + " pour vendre " 
        telegram_send.send(messages=[messages])
        pointage_pas_op += 1
        pointage_bot += 1
else :
    print("No opportunity to take")
    # messages = "Pas d'opportuniter de trade" 
    # telegram_send.send(messages=[messages])
    pointage_pas_op += 1
    pointage_bot += 1



modifierId = ernest.get(connection1, table, 0)
ernest.updateActuelPrix(connection1,table,actualPrice,modifierId)

sleep(2)
# ****************************************************************
#      1s fin super trend 1s
# ****************************************************************



# *******************************************************************************************************************************





# ****************************************************************
#      1 debut super trend 
# ****************************************************************


# ******* Recuperation des informations general sur le bot  *****

table = "bot_49"
nom_bot = ernest.get(connection1, table, 1)
nom_crypto = ernest.get(connection1, table, 2)
nombre_crypto = ernest.get(connection1, table, 3)
usdt = ernest.get(connection1, table, 5)

total_trad = ernest.get(connection1, table, 8)
positif_trad = ernest.get(connection1, table, 9)
negatif_trad = ernest.get(connection1, table, 10)
status = ernest.get(connection1, table, 11)
prix_achat 	= ernest.get(connection1, table, 13)
actif 	= ernest.get(connection1, table, 15)

# ****************************************************************

messages = nom_bot
telegram_send.send(messages=[messages])

client = ftx.FtxClient(api_key = api_key,
                   api_secret = api_secret, subaccount_name=subaccount_name)


    
# fiatAmount = getBalance(client, fiatSymbol)
# cryptoAmount = getBalance(client, cryptoSymbol)
fiatAmount = usdt
cryptoAmount = nombre_crypto
actualPrice = df['close'].iloc[-1]
minToken = 5/actualPrice
print('coin price :',actualPrice, 'usd balance', fiatAmount, 'coin balance :',cryptoAmount)

if df['SUPER_TREND_DIRECTION2'].iloc[-2]+df['SUPER_TREND_DIRECTION3'].iloc[-2] >= 1 and df['close'].iloc[-2] > df['EMA90'].iloc[-2] and df['STOCH_RSI'].iloc[-2] < 0.8 and actif == 1 and ( status == "Libre" or status == "Achat seul" ) :
    if float(fiatAmount) > 5:
        
        messages = " condition d'achat valider "
        telegram_send.send(messages=[messages])
        
        quantityBuy = truncate(float(fiatAmount)/actualPrice, myTruncate)
        # buyOrder = client.place_order(
        #     market=pairSymbol, 
        #     side="buy", 
        #     price=None, 
        #     size=quantityBuy, 
        #     type='market')
        # print("BUY", buyOrder)

        messages = "Achat de " + str(quantityBuy) + " " + cryptoSymbol + " a " + str(actualPrice)
        telegram_send.send(messages=[messages])
        
        # ernest information pour la base de donner
        nombre_crypto = quantityBuy
        valeur_crypto = quantityBuy * actualPrice
        usdt = 0
        indicateurs1 = df['TRIX_HISTO'].iloc[-1]
        indicatuer2 = df['STOCH_RSI'].iloc[-1]
        total_trad = total_trad
        operation = "Achat"
        prix_achat = actualPrice
        prix_actuel = actualPrice
        
        ernest.insert(connection1, table, nom_bot, nom_crypto, nombre_crypto, valeur_crypto, usdt, indicateurs1, indicatuer2, total_trad, positif_trad, negatif_trad, status, operation, prix_achat, actif, prix_actuel)
        
        tab = "transactions"
        ernest.insertTranscation(connection1, tab, nom_crypto, operation, valeur_crypto, usdt, nom_bot, status)
        
        
        pointage_achat += 1
        pointage_bot += 1

        
    else:
        print("If you  give me more USD I will buy more",cryptoSymbol)
        messages = " Condition d'achat valider, mais il ne faut plus de " + fiatSymbol + " pour acheter des " + cryptoSymbol
        telegram_send.send(messages=[messages])
        pointage_pas_op += 1
        pointage_bot += 1

elif df['SUPER_TREND_DIRECTION2'].iloc[-2]+df['SUPER_TREND_DIRECTION3'].iloc[-2] < 1 and df['STOCH_RSI'].iloc[-2] > 0.2 and actif == 1 and ( status == "Libre" or status == "Vente seul" ) :
    if float(cryptoAmount) > minToken:
        
        messages = " condition de vante valider "
        telegram_send.send(messages=[messages])
        
        # sellOrder = client.place_order(
        #     market=pairSymbol, 
        #     side="sell", 
        #     price=None, 
        #     size=truncate(cryptoAmount, myTruncate), 
        #     type='market')
        # print("SELL", sellOrder)

        messages = "Vente de " + str(cryptoAmount) + " " + cryptoSymbol  + " a " + str(actualPrice)
        telegram_send.send(messages=[messages])
        
        # ernest information pour la base de donner
        
        usdt = nombre_crypto * actualPrice 
        frais_transaction = takerFee * usdt
        usdt = usdt - frais_transaction
        
        nombre_crypto = 0
        valeur_crypto = 0 
        
        indicateurs1 = df['TRIX_HISTO'].iloc[-1]
        indicatuer2 = df['STOCH_RSI'].iloc[-1]
        total_trad += 1
        operation = "Vente"
        
        if actualPrice > prix_achat:
            positif_trad += 1
        else:
            negatif_trad += 1
            
        prix_achat = actualPrice
        prix_actuel = actualPrice
        
        ernest.insert(connection1, table, nom_bot, nom_crypto, nombre_crypto, valeur_crypto, usdt, indicateurs1, indicatuer2, total_trad, positif_trad, negatif_trad, status, operation, prix_achat, actif, prix_actuel)
        
        tab = "transactions"
        ernest.insertTranscation(connection1, tab, nom_crypto, operation, valeur_crypto, usdt, nom_bot, status)
        
        
        pointage_vent += 1
        pointage_bot += 1

        
    else:
        print("If you give me more",cryptoSymbol,"I will sell it")
        messages = " Condition de vente valider, mais il ne faut plus de " + cryptoSymbol + " pour vendre " 
        telegram_send.send(messages=[messages])
        pointage_pas_op += 1
        pointage_bot += 1
     
else :
    print("No opportunity to take")
    # messages = "Pas d'opportuniter de trade" 
    # telegram_send.send(messages=[messages])
    pointage_pas_op += 1
    pointage_bot += 1



modifierId = ernest.get(connection1, table, 0)
ernest.updateActuelPrix(connection1,table,actualPrice,modifierId)

sleep(2)
# ****************************************************************
#      1 fin super trend 1
# ****************************************************************









# ****************************************************************
#      1s debut super trend 1s
# ****************************************************************


# ******* Recuperation des informations general sur le bot  *****

table = "bot_50"
nom_bot = ernest.get(connection1, table, 1)
nom_crypto = ernest.get(connection1, table, 2)
nombre_crypto = ernest.get(connection1, table, 3)
usdt = ernest.get(connection1, table, 5)

total_trad = ernest.get(connection1, table, 8)
positif_trad = ernest.get(connection1, table, 9)
negatif_trad = ernest.get(connection1, table, 10)
status = ernest.get(connection1, table, 11)
prix_achat 	= ernest.get(connection1, table, 13)
actif 	= ernest.get(connection1, table, 15)

# ****************************************************************

messages = nom_bot
telegram_send.send(messages=[messages])

client = ftx.FtxClient(api_key = api_key,
                   api_secret = api_secret, subaccount_name=subaccount_name)


    
# fiatAmount = getBalance(client, fiatSymbol)
# cryptoAmount = getBalance(client, cryptoSymbol)
fiatAmount = usdt
cryptoAmount = nombre_crypto
actualPrice = df['close'].iloc[-1]
minToken = 5/actualPrice
print('coin price :',actualPrice, 'usd balance', fiatAmount, 'coin balance :',cryptoAmount)

if df['SUPER_TREND_DIRECTION2'].iloc[-2]+df['SUPER_TREND_DIRECTION3'].iloc[-2] >= 1 and df['close'].iloc[-2] > df['EMA90'].iloc[-2] and df['STOCH_RSI'].iloc[-2] < 0.8 and actif == 1 and ( status == "Libre" or status == "Achat seul" ) :
    if float(fiatAmount) > 5:
        
        messages = " condition d'achat valider "
        telegram_send.send(messages=[messages])
        
        quantityBuy = truncate(float(fiatAmount)/actualPrice, myTruncate)
        # buyOrder = client.place_order(
        #     market=pairSymbol, 
        #     side="buy", 
        #     price=None, 
        #     size=quantityBuy, 
        #     type='market')
        # print("BUY", buyOrder)

        messages = "Achat de " + str(quantityBuy) + " " + cryptoSymbol + " a " + str(actualPrice)
        telegram_send.send(messages=[messages])
        
        # ernest information pour la base de donner
        nombre_crypto = quantityBuy
        valeur_crypto = quantityBuy * actualPrice
        usdt = 0
        indicateurs1 = df['TRIX_HISTO'].iloc[-1]
        indicatuer2 = df['STOCH_RSI'].iloc[-1]
        total_trad = total_trad
        operation = "Achat"
        prix_achat = actualPrice
        prix_actuel = actualPrice
        
        ernest.insert(connection1, table, nom_bot, nom_crypto, nombre_crypto, valeur_crypto, usdt, indicateurs1, indicatuer2, total_trad, positif_trad, negatif_trad, status, operation, prix_achat, actif, prix_actuel)
        
        tab = "transactions"
        ernest.insertTranscation(connection1, tab, nom_crypto, operation, valeur_crypto, usdt, nom_bot, status)
        
        
        pointage_achat += 1
        pointage_bot += 1

        
    else:
        print("If you  give me more USD I will buy more",cryptoSymbol)
        messages = " Condition d'achat valider, mais il ne faut plus de " + fiatSymbol + " pour acheter des " + cryptoSymbol
        telegram_send.send(messages=[messages])
        pointage_pas_op += 1
        pointage_bot += 1
    

elif df['SUPER_TREND_DIRECTION2'].iloc[-2]+df['SUPER_TREND_DIRECTION3'].iloc[-2] < 1 and df['STOCH_RSI'].iloc[-2] > 0.2 and actif == 1 and ( status == "Libre" or status == "Vente seul" ) :
    if float(cryptoAmount) > minToken and actualPrice > prix_achat:
        
        messages = " condition de vante valider "
        telegram_send.send(messages=[messages])
        
        # sellOrder = client.place_order(
        #     market=pairSymbol, 
        #     side="sell", 
        #     price=None, 
        #     size=truncate(cryptoAmount, myTruncate), 
        #     type='market')
        # print("SELL", sellOrder)
        
        messages = "Vente de " + str(cryptoAmount) + " " + cryptoSymbol  + " a " + str(actualPrice)
        telegram_send.send(messages=[messages])

        # ernest information pour la base de donner
        
        usdt = nombre_crypto * actualPrice 
        frais_transaction = takerFee * usdt
        usdt = usdt - frais_transaction
        
        nombre_crypto = 0
        valeur_crypto = 0 
        
        indicateurs1 = df['TRIX_HISTO'].iloc[-1]
        indicatuer2 = df['STOCH_RSI'].iloc[-1]
        total_trad += 1
        operation = "Vente"
        
        if actualPrice > prix_achat:
            positif_trad += 1
        else:
            negatif_trad += 1
            
        prix_achat = actualPrice
        prix_actuel = actualPrice
        
        ernest.insert(connection1, table, nom_bot, nom_crypto, nombre_crypto, valeur_crypto, usdt, indicateurs1, indicatuer2, total_trad, positif_trad, negatif_trad, status, operation, prix_achat, actif, prix_actuel)
        
        tab = "transactions"
        ernest.insertTranscation(connection1, tab, nom_crypto, operation, valeur_crypto, usdt, nom_bot, status)
        
        
        pointage_vent += 1
        pointage_bot += 1

        
    else:
        print("If you give me more",cryptoSymbol,"I will sell it")
        messages = " Condition de vente valider, mais il ne faut plus de " + cryptoSymbol + " pour vendre " 
        telegram_send.send(messages=[messages])
        pointage_pas_op += 1
        pointage_bot += 1
else :
    print("No opportunity to take")
    # messages = "Pas d'opportuniter de trade" 
    # telegram_send.send(messages=[messages])
    pointage_pas_op += 1
    pointage_bot += 1



modifierId = ernest.get(connection1, table, 0)
ernest.updateActuelPrix(connection1,table,actualPrice,modifierId)

sleep(2)
# ****************************************************************
#      1s fin super trend 1s
# ****************************************************************





# pour la vente de tous les cryptos urgent

table = "cryse"
resultat = ernest.get(connection1, table, 1)
if resultat == "vent":
    
    cryptoAmount = getBalance(client, cryptoSymbol)
    if float(cryptoAmount) > minToken:
        sellOrder = client.place_order(
            market=pairSymbol, 
            side="sell", 
            price=None, 
            size=truncate(cryptoAmount, myTruncate), 
            type='market')
        print("SELL", sellOrder)
        
        messages = "Tous les crypto ont ete vendu : ". cryptoSymbol
        telegram_send.send(messages=[messages])









# pause a la fin de 10 execution
sleep(2)

# A la fin de tour les bots
ernest.insertPointage(connection1, pointage_pas_op, pointage_achat, pointage_vent, pointage_bot)

# pause a la fin de 10 execution
sleep(2)

cryptoSymbol = "BNB"
idBNB = 1
BNB_quantiter = getBalance(client, cryptoSymbol)
ernest.updateCrypto(connection1, BNB_quantiter, idBNB)

sleep(2)

cryptoSymbol = "ETH"
idBNB = 2
BNB_quantiter = getBalance(client, cryptoSymbol)
ernest.updateCrypto(connection1, BNB_quantiter, idBNB)

sleep(2)

cryptoSymbol = "BTC"
idBNB = 3
BNB_quantiter = getBalance(client, cryptoSymbol)
ernest.updateCrypto(connection1, BNB_quantiter, idBNB)

sleep(2)

cryptoSymbol = "LINK"
idBNB = 4
BNB_quantiter = getBalance(client, cryptoSymbol)
ernest.updateCrypto(connection1, BNB_quantiter, idBNB)

sleep(2)

cryptoSymbol = "LTC"
idBNB = 5
BNB_quantiter = getBalance(client, cryptoSymbol)
ernest.updateCrypto(connection1, BNB_quantiter, idBNB)


sleep(2)

cryptoSymbol = fiatSymbol
idBNB = 6
BNB_quantiter = getBalance(client, cryptoSymbol)
ernest.updateCrypto(connection1, BNB_quantiter, idBNB)


messages = "Fichier bot 5 BNB2 terminer"
telegram_send.send(messages=[messages]) 

messages = "#*** Fin execution ***#"
telegram_send.send(messages=[messages])    

#fin











