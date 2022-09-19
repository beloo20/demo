








# ********* les imports **************   
import ftx
import pandas as pd
import ta
import time
import json
from math import *
import pandas_ta as pda
import mysql
import mysql.connector as MC
from time import sleep
import ernest
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
    
  
# ****************************************************************
#    1    Debut Trix 1
# ****************************************************************


# ******* Recuperation des informations general sur le bot  *****

table = "bot_1"
nom_bot = ernest.get(connection1, table, 1)
nom_crypto = ernest.get(connection1, table, 2)
nombre_crypto = ernest.get(connection1, table, 3)
usdt = ernest.get(connection1, table, 5)

total_trad = float( ernest.get(connection1, table, 8) ) 
positif_trad = float( ernest.get(connection1, table, 9) ) 
negatif_trad = float( ernest.get(connection1, table, 10) ) 
status = ernest.get(connection1, table, 11)
prix_achat 	= float( ernest.get(connection1, table, 13) ) 
actif 	= ernest.get(connection1, table, 15)

# ****************************************************************



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


        
quantityBuy = truncate(float(fiatAmount)/actualPrice, myTruncate)
       
        
print("Achat de " + str(quantityBuy) + " " + cryptoSymbol + " a " + str(actualPrice) )
        
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
        



