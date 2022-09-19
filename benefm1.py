


import ftx
import pandas as pd
import time
from math import *
import mysql.connector as MC
from time import sleep
import ernest

connection1 = MC.connect(host='mysql-hinvest.alwaysdata.net',database='hinvest_bbd',user='hinvest',password='HOunha20lide@')

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


    
    
# bnb
cryptoSymbol = "BNB"
pairSymbol = 'BNB/USD'
BNB_quantiter = getBalance(client, cryptoSymbol)

data = client.get_historical_data(
    market_name=pairSymbol, 
    resolution=3600, 
    limit=3, 
    start_time=float(round(time.time()))-150*3600, 
    end_time=float(round(time.time())))
df = pd.DataFrame(data)

actualPriceBNB = df['close'].iloc[-1]
valeurBNB = BNB_quantiter * actualPriceBNB


# eth

cryptoSymbol = "ETH"
pairSymbol = 'ETH/USD'
ETH_quantiter = getBalance(client, cryptoSymbol)

data = client.get_historical_data(
    market_name=pairSymbol, 
    resolution=3600, 
    limit=3, 
    start_time=float(round(time.time()))-150*3600, 
    end_time=float(round(time.time())))
df = pd.DataFrame(data)

actualPriceETH = df['close'].iloc[-1]
valeurETH = ETH_quantiter * actualPriceETH



# BTC

cryptoSymbol = "BTC"
pairSymbol = 'BTC/USD'
BTC_quantiter = getBalance(client, cryptoSymbol)

data = client.get_historical_data(
    market_name=pairSymbol, 
    resolution=3600, 
    limit=3, 
    start_time=float(round(time.time()))-150*3600, 
    end_time=float(round(time.time())))
df = pd.DataFrame(data)

actualPriceBTC = df['close'].iloc[-1]
valeurBTC = BTC_quantiter * actualPriceBTC



# LINK

cryptoSymbol = "LINK"
pairSymbol = 'LINK/USD'
LINK_quantiter = getBalance(client, cryptoSymbol)

data = client.get_historical_data(
    market_name=pairSymbol, 
    resolution=3600, 
    limit=3, 
    start_time=float(round(time.time()))-150*3600, 
    end_time=float(round(time.time())))
df = pd.DataFrame(data)

actualPriceLINK = df['close'].iloc[-1]
valeurLINK = LINK_quantiter * actualPriceLINK


#USD

cryptoSymbol = "USD"
valeurUSD = getBalance(client, cryptoSymbol)


valeurPortefActuel = valeurBNB + valeurBTC + valeurETH + valeurLINK + valeurUSD

valeurPortefHier = ernest.get(connection1, "h24",1)

benef = valeurPortefActuel - float(valeurPortefHier)

pourcentage = (benef / valeurPortefHier) * 100

ernest.insertValeurPortefeuilleM1(connection1, valeurPortefActuel, benef, pourcentage)







