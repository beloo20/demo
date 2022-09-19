






# ********* les imports **************   
import ftx
import pandas as pd
import ta
import time
import json
from math import *
import pandas_ta as pda
import telegram_send
import mysql
import mysql.connector as MC
from time import sleep
import ernest
connection1 = MC.connect(host='mysql-hinvest.alwaysdata.net',database='hinvest_bbd',user='hinvest',password='HOunha20lide@')


def videTable( con, table ):
    try:
        connection = con

        cursor = connection.cursor()
        
        sql_select_query = """TRUNCATE """+ table
        cursor.execute(sql_select_query)
             
    except mysql.connector.Error as error:
        print("Erreur de connection a MySQL: {}".format(error))
        
        
videTable(connection1, "pointage")




# ********* les parametres commun *****
pairSymbol = 'BNB/USD'
fiatSymbol = 'USD'
cryptoSymbol = 'BNB'
myTruncate = 3

api_key = '4ylY1TRh4R7vxNhW-6lG_Qq3DkZgMa-JHNPF8Tr0'
api_secret = 'OlBlqYozzwJsuOXi2P8IFRBqi4QW107ji02eGgDf'
subaccount_name = 'ErnestTradingFtxBot'
takerFee = 0.0007

pointage_achat = 0
pointage_vent = 0
pointage_pas_op = 0
pointage_bot = 0


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
    

# *********** Debut **************
messages = "#**** Debut ****#"
telegram_send.send(messages=[messages])    


# ****************************************************************
#    1    Debut Trix 1
# ****************************************************************


# ******* Recuperation des informations general sur le bot  *****

table = "bot_1"
nom_bot = ernest.get(connection1, table, 1)
nom_crypto = ernest.get(connection1, table, 2)
nombre_crypto = float( ernest.get(connection1, table, 3) ) 
usdt = float( ernest.get(connection1, table, 5) ) 

total_trad = float( ernest.get(connection1, table, 8) )
positif_trad = float( ernest.get(connection1, table, 9) )
negatif_trad = float( ernest.get(connection1, table, 10) )
status = ernest.get(connection1, table, 11)
prix_achat 	= float( ernest.get(connection1, table, 13) )
actif 	= ernest.get(connection1, table, 15)

# ****************************************************************

messages = nom_bot
telegram_send.send(messages=[messages])


i = 9
j = 21
goOn = True

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


trixLength = 9
trixSignal = 21
df['TRIX'] = ta.trend.ema_indicator(ta.trend.ema_indicator(ta.trend.ema_indicator(close=df['close'], window=trixLength), window=trixLength), window=trixLength)
df['TRIX_PCT'] = df["TRIX"].pct_change()*100
df['TRIX_SIGNAL'] = ta.trend.sma_indicator(df['TRIX_PCT'],trixSignal)
df['TRIX_HISTO'] = df['TRIX_PCT'] - df['TRIX_SIGNAL']
df['STOCH_RSI'] = ta.momentum.stochrsi(close=df['close'], window=14, smooth1=3, smooth2=3)
print(df)


actualPrice = df['close'].iloc[-1]
# ernest 
# fiatAmount = getBalance(client, fiatSymbol)
# cryptoAmount = getBalance(client, cryptoSymbol)
fiatAmount = usdt
cryptoAmount = nombre_crypto
minToken = 5/actualPrice
print('coin price :',actualPrice, 'usd balance', fiatAmount, 'coin balance :',cryptoAmount)

def buyConditionT(row, previousRow):
    if row['TRIX_HISTO'] > 0 and row['STOCH_RSI'] <= 0.82:
        return True
    else:
        return False

def sellConditionT(row, previousRow):
    if row['TRIX_HISTO'] < 0 and row['STOCH_RSI'] >= 0.2:
        return True
    else:
        return False

if buyConditionT(df.iloc[-2], df.iloc[-3]) and actif == 1 and ( status == "Libre" or status == "Achat seul" ) :
    if float(fiatAmount) > 5:
        
        messages = " Condition d'achat valider "
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
        valeur_crypto = float(quantityBuy) * actualPrice
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
        goOn = True
        print("Condition d'achat valider",cryptoSymbol) 
        messages = " Condition d'achat valider, mais il ne faut plus de " + fiatSymbol + " pour acheter des " + cryptoSymbol
        telegram_send.send(messages=[messages])
        
        pointage_pas_op += 1
        pointage_bot += 1

elif sellConditionT(df.iloc[-2], df.iloc[-3]) and actif == 1 and ( status == "Libre" or status == "Vente seul" ):
    if float(cryptoAmount) > minToken:
        
        messages = " condition de vente valider "
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
        goOn = True
        print("If you give me more",cryptoSymbol,"I will sell it")
        messages = " Condition de vente valider, mais il ne faut plus de " + cryptoSymbol + " pour vendre " 
        telegram_send.send(messages=[messages]) 
        pointage_pas_op += 1
        pointage_bot += 1
        
else :
    goOn = True
    print("No opportunity to take")
    
    pointage_pas_op += 1
    pointage_bot += 1

    # messages = "Pas d'opportuniter de trade" 
    # telegram_send.send(messages=[messages])


modifierId = ernest.get(connection1, table, 0)
ernest.updateActuelPrix(connection1,table,actualPrice,modifierId)

sleep(2)
# ****************************************************************
#     1  Fin  Trix 1
# ****************************************************************





# ****************************************************************
#      2 debut super trend 2
# ****************************************************************


# ******* Recuperation des informations general sur le bot  *****

table = "bot_2"
nom_bot = ernest.get(connection1, table, 1)
nom_crypto = ernest.get(connection1, table, 2)
nombre_crypto = float( ernest.get(connection1, table, 3) ) 
usdt = float( ernest.get(connection1, table, 5) ) 

total_trad = float( ernest.get(connection1, table, 8) )
positif_trad = float( ernest.get(connection1, table, 9) )
negatif_trad = float( ernest.get(connection1, table, 10) )
status = ernest.get(connection1, table, 11)
prix_achat 	= float( ernest.get(connection1, table, 13) )
actif 	= ernest.get(connection1, table, 15)

# ****************************************************************

messages = nom_bot
telegram_send.send(messages=[messages])

client = ftx.FtxClient(api_key = api_key,
                   api_secret = api_secret, subaccount_name=subaccount_name)


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



    
# fiatAmount = getBalance(client, fiatSymbol)
# cryptoAmount = getBalance(client, cryptoSymbol)
fiatAmount = usdt
cryptoAmount = nombre_crypto
actualPrice = df['close'].iloc[-1]
minToken = 5/actualPrice
print('coin price :',actualPrice, 'usd balance', fiatAmount, 'coin balance :',cryptoAmount)

if df['SUPER_TREND_DIRECTION1'].iloc[-2]+df['SUPER_TREND_DIRECTION2'].iloc[-2]+df['SUPER_TREND_DIRECTION3'].iloc[-2] >= 1 and df['close'].iloc[-2] > df['EMA90'].iloc[-2] and df['STOCH_RSI'].iloc[-2] < 0.8 and actif == 1 and ( status == "Libre" or status == "Achat seul" ) :
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
        valeur_crypto = float(quantityBuy) * actualPrice
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

elif df['SUPER_TREND_DIRECTION1'].iloc[-2]+df['SUPER_TREND_DIRECTION2'].iloc[-2]+df['SUPER_TREND_DIRECTION3'].iloc[-2] < 1 and df['STOCH_RSI'].iloc[-2] > 0.2 and actif == 1 and ( status == "Libre" or status == "Vente seul" ) :
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
#       3 debut aligator 3
# ****************************************************************

# ******* Recuperation des informations general sur le bot  *****

table = "bot_3"
nom_bot = ernest.get(connection1, table, 1)
nom_crypto = ernest.get(connection1, table, 2)
nombre_crypto = float( ernest.get(connection1, table, 3) ) 
usdt = float( ernest.get(connection1, table, 5) ) 

total_trad = float( ernest.get(connection1, table, 8) )
positif_trad = float( ernest.get(connection1, table, 9) )
negatif_trad = float( ernest.get(connection1, table, 10) )
status = ernest.get(connection1, table, 11)
prix_achat 	= float( ernest.get(connection1, table, 13) )
actif 	= ernest.get(connection1, table, 15)

# ****************************************************************

messages = nom_bot
telegram_send.send(messages=[messages])


client = ftx.FtxClient(api_key=api_key,
                   api_secret=api_secret, subaccount_name=subaccount_name)


df['EMA1']=ta.trend.ema_indicator(close=df['close'], window=7)
df['EMA2']=ta.trend.ema_indicator(close=df['close'], window=30)
df['EMA3']=ta.trend.ema_indicator(close=df['close'], window=50)
df['EMA4']=ta.trend.ema_indicator(close=df['close'], window=100)
df['EMA5']=ta.trend.ema_indicator(close=df['close'], window=121)
df['EMA6']=ta.trend.ema_indicator(close=df['close'], window=200)
df['STOCH_RSI'] = ta.momentum.stochrsi(close=df['close'], window=14, smooth1=3, smooth2=3)
#print(df)


    
# fiatAmount = getBalance(client, fiatSymbol)
# cryptoAmount = getBalance(client, cryptoSymbol)
fiatAmount = usdt
cryptoAmount = nombre_crypto
actualPrice = df['close'].iloc[-1]
minToken = 5/actualPrice
print('coin price :',actualPrice, 'usd balance', fiatAmount, 'coin balance :',cryptoAmount)

def buyConditionA(row, previousRow):
    if row['EMA1'] > row['EMA2'] and row['EMA2'] > row['EMA3'] and row['EMA3'] > row['EMA4'] and row['EMA4'] > row['EMA5'] and row['EMA5'] > row['EMA6'] and row['STOCH_RSI']<0.82:
        return True
    else:
        return False

def sellConditionA(row, previousRow):
    if row['EMA6'] > row['EMA1'] and row['STOCH_RSI']>0.2:
        return True
    else:
        return False

if buyConditionA(df.iloc[-2], df.iloc[-3]) and actif == 1 and ( status == "Libre" or status == "Achat seul" ) :
    if float(fiatAmount) > 5:
        
        messages = " Condition achat valider "
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
        valeur_crypto = float( quantityBuy ) * actualPrice
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
    
elif sellConditionA(df.iloc[-2], df.iloc[-3]) and actif == 1 and ( status == "Libre" or status == "Vente seul" ) :
    if float(cryptoAmount) > minToken:
        
        messages = " condition de vent valider "
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
    # messages = " Pas d'opportuniter de trade "
    # telegram_send.send(messages=[messages])
    pointage_pas_op += 1
    pointage_bot += 1


modifierId = ernest.get(connection1, table, 0)
ernest.updateActuelPrix(connection1,table,actualPrice,modifierId)

sleep(2)
# ****************************************************************
#       3 fin aligator 3
# ****************************************************************




# ****************************************************************
#       4 debut E Mouvine average 4
# ****************************************************************


# ******* Recuperation des informations general sur le bot  *****

table = "bot_4"
nom_bot = ernest.get(connection1, table, 1)
nom_crypto = ernest.get(connection1, table, 2)
nombre_crypto = float( ernest.get(connection1, table, 3) ) 
usdt = float( ernest.get(connection1, table, 5) ) 

total_trad = float( ernest.get(connection1, table, 8) )
positif_trad = float( ernest.get(connection1, table, 9) )
negatif_trad = float( ernest.get(connection1, table, 10) )
status = ernest.get(connection1, table, 11)
prix_achat 	= float( ernest.get(connection1, table, 13) )
actif 	= ernest.get(connection1, table, 15)

# ****************************************************************

messages = nom_bot
telegram_send.send(messages=[messages])


client = ftx.FtxClient(api_key=api_key,
                   api_secret=api_secret, subaccount_name=subaccount_name)


df['EMA28']=ta.trend.ema_indicator(df['close'], 28)
df['EMA48']=ta.trend.ema_indicator(df['close'], 48)
df['STOCH_RSI']=ta.momentum.stochrsi(df['close'])
#print(df)

    
# fiatAmount = getBalance(client, fiatSymbol)
# cryptoAmount = getBalance(client, cryptoSymbol)
fiatAmount = usdt
cryptoAmount = nombre_crypto
actualPrice = df['close'].iloc[-1]
minToken = 5/actualPrice
print('coin price :',actualPrice, 'usd balance', fiatAmount, 'coin balance :',cryptoAmount)

if df['EMA28'].iloc[-2] > df['EMA48'].iloc[-2] and df['STOCH_RSI'].iloc[-2] < 0.8 and actif == 1 and ( status == "Libre" or status == "Achat seul" ) :
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
        valeur_crypto = float( quantityBuy ) * actualPrice
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
    
elif df['EMA28'].iloc[-2] < df['EMA48'].iloc[-2] and df['STOCH_RSI'].iloc[-2] > 0.2 and actif == 1 and ( status == "Libre" or status == "Vente seul" ):
    if float(cryptoAmount) > minToken:
        
        messages = " condition de vent valider "
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
#       4 fin E Mouvine average 4
# ****************************************************************




# ****************************************************************
#       5 debut big 5
# ****************************************************************


# ******* Recuperation des informations general sur le bot  *****

table = "bot_5"
nom_bot = ernest.get(connection1, table, 1)
nom_crypto = ernest.get(connection1, table, 2)
nombre_crypto = float( ernest.get(connection1, table, 3) ) 
usdt = float( ernest.get(connection1, table, 5) ) 

total_trad = float( ernest.get(connection1, table, 8) )
positif_trad = float( ernest.get(connection1, table, 9) )
negatif_trad = float( ernest.get(connection1, table, 10) )
status = ernest.get(connection1, table, 11)
prix_achat 	= float( ernest.get(connection1, table, 13) )
actif 	= ernest.get(connection1, table, 15)

# ****************************************************************

messages = nom_bot
telegram_send.send(messages=[messages])


i = 9
j = 21
goOn = True

client = ftx.FtxClient(
    api_key=api_key,
    api_secret=api_secret, 
    subaccount_name=subaccount_name
)
result = client.get_balances()



trixLength = 9
trixSignal = 21
df['TRIX'] = ta.trend.ema_indicator(ta.trend.ema_indicator(ta.trend.ema_indicator(close=df['close'], window=trixLength), window=trixLength), window=trixLength)
df['TRIX_PCT'] = df["TRIX"].pct_change()*100
df['TRIX_SIGNAL'] = ta.trend.sma_indicator(df['TRIX_PCT'],trixSignal)
df['TRIX_HISTO'] = df['TRIX_PCT'] - df['TRIX_SIGNAL']
df['STOCH_RSI'] = ta.momentum.stochrsi(close=df['close'], window=14, smooth1=3, smooth2=3)
print(df)
messages = ""

actualPrice = df['close'].iloc[-1]
# fiatAmount = getBalance(client, fiatSymbol)
# cryptoAmount = getBalance(client, cryptoSymbol)
fiatAmount = usdt
cryptoAmount = nombre_crypto
minToken = 5/actualPrice
print('coin price :',actualPrice, 'usd balance', fiatAmount, 'coin balance :',cryptoAmount)

def buyConditionT(row, previousRow):
    if row['TRIX_HISTO'] > 0 and row['STOCH_RSI'] <= 0.82:
        return True
    else:
        return False

def sellConditionT(row, previousRow):
    if row['TRIX_HISTO'] < 0 and row['STOCH_RSI'] >= 0.2:
        return True
    else:
        return False
   # trix and  super and aligator and ema
if buyConditionT(df.iloc[-2], df.iloc[-3]) and (df['SUPER_TREND_DIRECTION1'].iloc[-2]+df['SUPER_TREND_DIRECTION2'].iloc[-2]+df['SUPER_TREND_DIRECTION3'].iloc[-2] >= 1 and df['close'].iloc[-2] > df['EMA90'].iloc[-2] and df['STOCH_RSI'].iloc[-2] < 0.8) and buyConditionA(df.iloc[-2], df.iloc[-3]) and (df['EMA28'].iloc[-2] > df['EMA48'].iloc[-2] and df['STOCH_RSI'].iloc[-2] < 0.8) and actif == 1 and ( status == "Libre" or status == "Achat seul" ) :
    if float(fiatAmount) > 5:
        
        
        messages = " codition d'achat valider "
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
        valeur_crypto = float( quantityBuy ) * actualPrice
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
        goOn = True
        print("If you  give me more USD I will buy more",cryptoSymbol) 
        messages = " Condition d'achat valider, mais il ne faut plus de " + fiatSymbol + " pour acheter des " + cryptoSymbol
        telegram_send.send(messages=[messages])
        pointage_pas_op += 1
        pointage_bot += 1
    
# trix and super and aligator
elif sellConditionT(df.iloc[-2], df.iloc[-3]) and ( df['SUPER_TREND_DIRECTION1'].iloc[-2]+df['SUPER_TREND_DIRECTION2'].iloc[-2]+df['SUPER_TREND_DIRECTION3'].iloc[-2] < 1 and df['STOCH_RSI'].iloc[-2] > 0.2 ) and sellConditionA(df.iloc[-2], df.iloc[-3]) and ( df['EMA28'].iloc[-2] < df['EMA48'].iloc[-2] and df['STOCH_RSI'].iloc[-2] > 0.2 ) and actif == 1 and ( status == "Libre" or status == "Vente seul" ):
    if float(cryptoAmount) > minToken:
        
        messages = " condition de vente valider "
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
        goOn = True
        print("If you give me more",cryptoSymbol,"I will sell it")
        messages = " Condition de vente valider, mais il ne faut plus de " + cryptoSymbol + " pour vendre " 
        telegram_send.send(messages=[messages])
        pointage_pas_op += 1
        pointage_bot += 1
    
else :
    goOn = True
    print("No opportunity to take")
    # messages = "Pas d'opportuniter de trade" 
    # telegram_send.send(messages=[messages])
    pointage_pas_op += 1
    pointage_bot += 1


modifierId = ernest.get(connection1, table, 0)
ernest.updateActuelPrix(connection1,table,actualPrice,modifierId)

sleep(2)
# ****************************************************************
#       5 fin big 5
# ****************************************************************





# ****************************************************************
#       6 Debut Trix 2
# ****************************************************************


# ******* Recuperation des informations general sur le bot  *****

table = "bot_6"
nom_bot = ernest.get(connection1, table, 1)
nom_crypto = ernest.get(connection1, table, 2)
nombre_crypto = float( ernest.get(connection1, table, 3) ) 
usdt = float( ernest.get(connection1, table, 5) ) 

total_trad = float( ernest.get(connection1, table, 8) )
positif_trad = float( ernest.get(connection1, table, 9) )
negatif_trad = float( ernest.get(connection1, table, 10) )
status = ernest.get(connection1, table, 11)
prix_achat 	= float( ernest.get(connection1, table, 13) )
actif 	= ernest.get(connection1, table, 15)

# ****************************************************************

messages = nom_bot
telegram_send.send(messages=[messages])


i = 9
j = 21
goOn = True

client = ftx.FtxClient(
    api_key = api_key,
    api_secret = api_secret, 
    subaccount_name = subaccount_name
)
result = client.get_balances()



trixLength = 9
trixSignal = 21
df['TRIX'] = ta.trend.ema_indicator(ta.trend.ema_indicator(ta.trend.ema_indicator(close=df['close'], window=trixLength), window=trixLength), window=trixLength)
df['TRIX_PCT'] = df["TRIX"].pct_change()*100
df['TRIX_SIGNAL'] = ta.trend.sma_indicator(df['TRIX_PCT'],trixSignal)
df['TRIX_HISTO'] = df['TRIX_PCT'] - df['TRIX_SIGNAL']
df['STOCH_RSI'] = ta.momentum.stochrsi(close=df['close'], window=14, smooth1=3, smooth2=3)
print(df)


actualPrice = df['close'].iloc[-1]
# ernest 
# fiatAmount = getBalance(client, fiatSymbol)
# cryptoAmount = getBalance(client, cryptoSymbol)
fiatAmount = usdt
cryptoAmount = nombre_crypto
minToken = 5/actualPrice
print('coin price :',actualPrice, 'usd balance', fiatAmount, 'coin balance :',cryptoAmount)

def buyConditionT(row, previousRow):
    if row['TRIX_HISTO'] > 0 and row['STOCH_RSI'] <= 0.82:
        return True
    else:
        return False

def sellConditionT(row, previousRow):
    if row['TRIX_HISTO'] < 0 and row['STOCH_RSI'] >= 0.2:
        return True
    else:
        return False

if buyConditionT(df.iloc[-2], df.iloc[-3]) and actif == 1 and ( status == "Libre" or status == "Achat seul" ) :
    if float(fiatAmount) > 5:
        
        messages = " Condition d'achat valider "
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
        valeur_crypto = float( quantityBuy ) * actualPrice
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
        goOn = True
        print("If you  give me more USD I will buy more",cryptoSymbol) 
        messages = " Condition d'achat valider, mais il ne faut plus de " + fiatSymbol + " pour acheter des " + cryptoSymbol
        telegram_send.send(messages=[messages])
        pointage_pas_op += 1
        pointage_bot += 1
    

elif sellConditionT(df.iloc[-2], df.iloc[-3]) and actif == 1 and ( status == "Libre" or status == "Vente seul" ):
    if float(cryptoAmount) > minToken and actualPrice > prix_achat:
        
        messages = " condition de vente valider "
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
        goOn = True
        print("If you give me more",cryptoSymbol,"I will sell it")
        messages = " Condition de vente valider, mais il ne faut plus de " + cryptoSymbol + " pour vendre " 
        telegram_send.send(messages=[messages]) 
        pointage_pas_op += 1
        pointage_bot += 1
    
else :
    goOn = True
    print("No opportunity to take")
    # messages = "Pas d'opportuniter de trade" 
    # telegram_send.send(messages=[messages])
    pointage_pas_op += 1
    pointage_bot += 1


modifierId = ernest.get(connection1, table, 0)
ernest.updateActuelPrix(connection1,table,actualPrice,modifierId)

sleep(2)
# ****************************************************************
#      6 Fin  Trix 2
# ****************************************************************





# ****************************************************************
#      7 debut super trend 2 2
# ****************************************************************


# ******* Recuperation des informations general sur le bot  *****

table = "bot_7"
nom_bot = ernest.get(connection1, table, 1)
nom_crypto = ernest.get(connection1, table, 2)
nombre_crypto = float( ernest.get(connection1, table, 3) ) 
usdt = float( ernest.get(connection1, table, 5) ) 

total_trad = float( ernest.get(connection1, table, 8) )
positif_trad = float( ernest.get(connection1, table, 9) )
negatif_trad = float( ernest.get(connection1, table, 10) )
status = ernest.get(connection1, table, 11)
prix_achat 	= float( ernest.get(connection1, table, 13) )
actif 	= ernest.get(connection1, table, 15)

# ****************************************************************

messages = nom_bot
telegram_send.send(messages=[messages])

client = ftx.FtxClient(api_key = api_key,
                   api_secret = api_secret, subaccount_name=subaccount_name)


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



    
# fiatAmount = getBalance(client, fiatSymbol)
# cryptoAmount = getBalance(client, cryptoSymbol)
fiatAmount = usdt
cryptoAmount = nombre_crypto
actualPrice = df['close'].iloc[-1]
minToken = 5/actualPrice
print('coin price :',actualPrice, 'usd balance', fiatAmount, 'coin balance :',cryptoAmount)

if df['SUPER_TREND_DIRECTION1'].iloc[-2]+df['SUPER_TREND_DIRECTION2'].iloc[-2]+df['SUPER_TREND_DIRECTION3'].iloc[-2] >= 1 and df['close'].iloc[-2] > df['EMA90'].iloc[-2] and df['STOCH_RSI'].iloc[-2] < 0.8 and actif == 1 and ( status == "Libre" or status == "Achat seul" ) :
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
        valeur_crypto = float( quantityBuy ) * actualPrice
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
    

elif df['SUPER_TREND_DIRECTION1'].iloc[-2]+df['SUPER_TREND_DIRECTION2'].iloc[-2]+df['SUPER_TREND_DIRECTION3'].iloc[-2] < 1 and df['STOCH_RSI'].iloc[-2] > 0.2 and actif == 1 and ( status == "Libre" or status == "Vente seul" ) :
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
    messages = "Pas d'opportuniter de trade" 
    telegram_send.send(messages=[messages])
    pointage_pas_op += 1
    pointage_bot += 1



modifierId = ernest.get(connection1, table, 0)
ernest.updateActuelPrix(connection1,table,actualPrice,modifierId)

sleep(2)
# ****************************************************************
#      7 fin super trend 2 2
# ****************************************************************





# ****************************************************************
#       8 debut aligator 3 2
# ****************************************************************

# ******* Recuperation des informations general sur le bot  *****

table = "bot_8"
nom_bot = ernest.get(connection1, table, 1)
nom_crypto = ernest.get(connection1, table, 2)
nombre_crypto = float( ernest.get(connection1, table, 3) ) 
usdt = float( ernest.get(connection1, table, 5) ) 

total_trad = float( ernest.get(connection1, table, 8) )
positif_trad = float( ernest.get(connection1, table, 9) )
negatif_trad = float( ernest.get(connection1, table, 10) )
status = ernest.get(connection1, table, 11)
prix_achat 	= float( ernest.get(connection1, table, 13) )
actif 	= ernest.get(connection1, table, 15)

# ****************************************************************

messages = nom_bot
telegram_send.send(messages=[messages])


client = ftx.FtxClient(api_key=api_key,
                   api_secret=api_secret, subaccount_name=subaccount_name)


df['EMA1']=ta.trend.ema_indicator(close=df['close'], window=7)
df['EMA2']=ta.trend.ema_indicator(close=df['close'], window=30)
df['EMA3']=ta.trend.ema_indicator(close=df['close'], window=50)
df['EMA4']=ta.trend.ema_indicator(close=df['close'], window=100)
df['EMA5']=ta.trend.ema_indicator(close=df['close'], window=121)
df['EMA6']=ta.trend.ema_indicator(close=df['close'], window=200)
df['STOCH_RSI'] = ta.momentum.stochrsi(close=df['close'], window=14, smooth1=3, smooth2=3)
#print(df)


    
# fiatAmount = getBalance(client, fiatSymbol)
# cryptoAmount = getBalance(client, cryptoSymbol)
fiatAmount = usdt
cryptoAmount = nombre_crypto
actualPrice = df['close'].iloc[-1]
minToken = 5/actualPrice
print('coin price :',actualPrice, 'usd balance', fiatAmount, 'coin balance :',cryptoAmount)

def buyConditionA(row, previousRow):
    if row['EMA1'] > row['EMA2'] and row['EMA2'] > row['EMA3'] and row['EMA3'] > row['EMA4'] and row['EMA4'] > row['EMA5'] and row['EMA5'] > row['EMA6'] and row['STOCH_RSI']<0.82:
        return True
    else:
        return False

def sellConditionA(row, previousRow):
    if row['EMA6'] > row['EMA1'] and row['STOCH_RSI']>0.2:
        return True
    else:
        return False

if buyConditionA(df.iloc[-2], df.iloc[-3]) and actif == 1 and ( status == "Libre" or status == "Achat seul" ) :
    if float(fiatAmount) > 5:
        
        messages = " Condition achat  valider "
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
        valeur_crypto = float( quantityBuy ) * actualPrice
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
    
elif sellConditionA(df.iloc[-2], df.iloc[-3]) and actif == 1 and ( status == "Libre" or status == "Vente seul" ) :
    if float(cryptoAmount) > minToken and actualPrice > prix_achat:
        
        messages = " condition de vent valider "
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
#       8 fin aligator 3 2
# ****************************************************************




# ****************************************************************
#       9 debut E Mouvine average 4
# ****************************************************************


# ******* Recuperation des informations general sur le bot  *****

table = "bot_9"
nom_bot = ernest.get(connection1, table, 1)
nom_crypto = ernest.get(connection1, table, 2)
nombre_crypto = float( ernest.get(connection1, table, 3) ) 
usdt = float( ernest.get(connection1, table, 5) ) 

total_trad = float( ernest.get(connection1, table, 8) )
positif_trad = float( ernest.get(connection1, table, 9) )
negatif_trad = float( ernest.get(connection1, table, 10) )
status = ernest.get(connection1, table, 11)
prix_achat 	= float( ernest.get(connection1, table, 13) )
actif 	= ernest.get(connection1, table, 15)

# ****************************************************************

messages = nom_bot
telegram_send.send(messages=[messages])


client = ftx.FtxClient(api_key=api_key,
                   api_secret=api_secret, subaccount_name=subaccount_name)


df['EMA28']=ta.trend.ema_indicator(df['close'], 28)
df['EMA48']=ta.trend.ema_indicator(df['close'], 48)
df['STOCH_RSI']=ta.momentum.stochrsi(df['close'])
#print(df)

    
# fiatAmount = getBalance(client, fiatSymbol)
# cryptoAmount = getBalance(client, cryptoSymbol)
fiatAmount = usdt
cryptoAmount = nombre_crypto
actualPrice = df['close'].iloc[-1]
minToken = 5/actualPrice
print('coin price :',actualPrice, 'usd balance', fiatAmount, 'coin balance :',cryptoAmount)

if df['EMA28'].iloc[-2] > df['EMA48'].iloc[-2] and df['STOCH_RSI'].iloc[-2] < 0.8 and actif == 1 and ( status == "Libre" or status == "Achat seul" ) :
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
        valeur_crypto = float( quantityBuy ) * actualPrice
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
    
elif df['EMA28'].iloc[-2] < df['EMA48'].iloc[-2] and df['STOCH_RSI'].iloc[-2] > 0.2 and actif == 1 and ( status == "Libre" or status == "Vente seul" ):
    if float(cryptoAmount) > minToken and actualPrice > prix_achat:
        
        messages = " condition de vent valider "
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
#       9 fin E Mouvine average 4 2
# ****************************************************************




# ****************************************************************
#       10 debut big 5 2
# ****************************************************************


# ******* Recuperation des informations general sur le bot  *****

table = "bot_10"
nom_bot = ernest.get(connection1, table, 1)
nom_crypto = ernest.get(connection1, table, 2)
nombre_crypto = float( ernest.get(connection1, table, 3) ) 
usdt = float( ernest.get(connection1, table, 5) ) 

total_trad = float( ernest.get(connection1, table, 8) )
positif_trad = float( ernest.get(connection1, table, 9) )
negatif_trad = float( ernest.get(connection1, table, 10) )
status = ernest.get(connection1, table, 11)
prix_achat 	= float( ernest.get(connection1, table, 13) )
actif 	= ernest.get(connection1, table, 15)

# ****************************************************************

messages = nom_bot
telegram_send.send(messages=[messages])



i = 9
j = 21
goOn = True

client = ftx.FtxClient(
    api_key=api_key,
    api_secret=api_secret, 
    subaccount_name=subaccount_name
)
result = client.get_balances()



trixLength = 9
trixSignal = 21
df['TRIX'] = ta.trend.ema_indicator(ta.trend.ema_indicator(ta.trend.ema_indicator(close=df['close'], window=trixLength), window=trixLength), window=trixLength)
df['TRIX_PCT'] = df["TRIX"].pct_change()*100
df['TRIX_SIGNAL'] = ta.trend.sma_indicator(df['TRIX_PCT'],trixSignal)
df['TRIX_HISTO'] = df['TRIX_PCT'] - df['TRIX_SIGNAL']
df['STOCH_RSI'] = ta.momentum.stochrsi(close=df['close'], window=14, smooth1=3, smooth2=3)
print(df)
messages = ""

actualPrice = df['close'].iloc[-1]
# fiatAmount = getBalance(client, fiatSymbol)
# cryptoAmount = getBalance(client, cryptoSymbol)
fiatAmount = usdt
cryptoAmount = nombre_crypto
minToken = 5/actualPrice
print('coin price :',actualPrice, 'usd balance', fiatAmount, 'coin balance :',cryptoAmount)

def buyConditionT(row, previousRow):
    if row['TRIX_HISTO'] > 0 and row['STOCH_RSI'] <= 0.82:
        return True
    else:
        return False

def sellConditionT(row, previousRow):
    if row['TRIX_HISTO'] < 0 and row['STOCH_RSI'] >= 0.2:
        return True
    else:
        return False
   # trix and  super and aligator and ema
if buyConditionT(df.iloc[-2], df.iloc[-3]) and (df['SUPER_TREND_DIRECTION1'].iloc[-2]+df['SUPER_TREND_DIRECTION2'].iloc[-2]+df['SUPER_TREND_DIRECTION3'].iloc[-2] >= 1 and df['close'].iloc[-2] > df['EMA90'].iloc[-2] and df['STOCH_RSI'].iloc[-2] < 0.8) and buyConditionA(df.iloc[-2], df.iloc[-3]) and (df['EMA28'].iloc[-2] > df['EMA48'].iloc[-2] and df['STOCH_RSI'].iloc[-2] < 0.8) and actif == 1 and ( status == "Libre" or status == "Achat seul" ) :
    if float(fiatAmount) > 5:
        
        
        messages = " codition d'achat valider "
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
        valeur_crypto = float( quantityBuy ) * actualPrice
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
        goOn = True
        print("If you  give me more USD I will buy more",cryptoSymbol) 
        messages = " Condition d'achat valider, mais il ne faut plus de " + fiatSymbol + " pour acheter des " + cryptoSymbol
        telegram_send.send(messages=[messages])
        pointage_pas_op += 1
        pointage_bot += 1
    
# trix and super and aligator
elif sellConditionT(df.iloc[-2], df.iloc[-3]) and ( df['SUPER_TREND_DIRECTION1'].iloc[-2]+df['SUPER_TREND_DIRECTION2'].iloc[-2]+df['SUPER_TREND_DIRECTION3'].iloc[-2] < 1 and df['STOCH_RSI'].iloc[-2] > 0.2 ) and sellConditionA(df.iloc[-2], df.iloc[-3]) and ( df['EMA28'].iloc[-2] < df['EMA48'].iloc[-2] and df['STOCH_RSI'].iloc[-2] > 0.2 ) and actif == 1 and ( status == "Libre" or status == "Vente seul" ):
    if float(cryptoAmount) > minToken and actualPrice > prix_achat:
        
        messages = " condition de vente valider "
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
        goOn = True
        print("If you give me more",cryptoSymbol,"I will sell it")
        messages = " Condition de vente valider, mais il ne faut plus de " + cryptoSymbol + " pour vendre " 
        telegram_send.send(messages=[messages])  
        pointage_pas_op += 1
        pointage_bot += 1
    
else :
    goOn = True
    print("No opportunity to take")
    # messages = "Pas d'opportuniter de trade" 
    # telegram_send.send(messages=[messages])
    pointage_pas_op += 1
    pointage_bot += 1


modifierId = ernest.get(connection1, table, 0)
ernest.updateActuelPrix(connection1,table,actualPrice,modifierId)
sleep(2)
# ****************************************************************
#       10 fin big 5 2
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


messages = "Fichier bot 1 BNB terminer"
telegram_send.send(messages=[messages])    

#fin











