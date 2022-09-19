


import mysql.connector as MC
from time import sleep
import telegram_send
# a supprimer
import mysql
# connection1 = MC.connect(host='mysql-hinvest.alwaysdata.net',database='hinvest_bbd',user='hinvest',password='HOunha20lide@')
# $bdd = connection("mysql-hinvest.alwaysdata.net","hinvest_bbd","hinvest","HOunha20lide@");
def get( con, table, position ):
    try:
        connection = con

        cursor = connection.cursor()
        
        sql_select_query = """select * from """+ table
        cursor.execute(sql_select_query)
        record = cursor.fetchall()
        for row in record:
            recherche = row[position]
        return recherche
                     
    except mysql.connector.Error as error:
        print("Erreur de connection a MySQL: {}".format(error))
        
        

def getBNB( con):
    try:
        connection = con

        cursor = connection.cursor()
        
        sql_select_query = """select * from crypto WHERE id = 1 """
        
        cursor.execute(sql_select_query)
        record = cursor.fetchall()
        for row in record:
            recherche = row[2]
        return recherche
                     
    except mysql.connector.Error as error:
        print("Erreur de connection a MySQL: {}".format(error))




def insert(con, table, nom_bot,  nom_crypto, nombre_crypto, valeur_crypto, usdt, indicateurs1, indicatuer2, total_trad, positif_trad, negatif_trad, status, operation, prix_achat, actif, prix_actuel ):
    try:
        connection = con
        
        cursor = connection.cursor()

        mySql_insert_query = """INSERT INTO """+ table +""" (nom_bot,  nom_crypto, nombre_crypto, valeur_crypto, usdt, indicateurs1, indicatuer2, total_trad, positif_trad, negatif_trad, status, operation, prix_achat, actif, prix_actuel) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) """

        valeur = (nom_bot,  nom_crypto, nombre_crypto, valeur_crypto, usdt, indicateurs1, indicatuer2, total_trad, positif_trad, negatif_trad, status, operation, prix_achat, actif, prix_actuel)
        
        cursor.execute(mySql_insert_query, valeur)
        connection.commit()
        print("insertion des valeurs r")

    except mysql.connector.Error as error:
        print("Failed to insert into MySQL table {}".format(error))
        


def insertTranscation(con, table, crypto,  operation, valeur_crypto, dollar, nom_bot, statuts):
    try:
        connection = con
        
        cursor = connection.cursor()

        mySql_insert_query = """INSERT INTO """+ table +""" ( crypto,  operation, valeur_crypto, dollar, nom_bot, statuts ) VALUES (%s, %s, %s, %s, %s, %s) """

        valeur = ( crypto,  operation, valeur_crypto, dollar, nom_bot, statuts )
        
        cursor.execute(mySql_insert_query, valeur)
        connection.commit()
        print("insertion des valeurs r")

    except mysql.connector.Error as error:
        print("Failed to insert into MySQL table {}".format(error))
        

def insertPointage(con, pas_operation,  achat, vent, point):
    try:
        connection = con
        
        cursor = connection.cursor()

        mySql_insert_query = """INSERT INTO pointage ( pas_operation,  achat, vent, point ) VALUES (%s, %s, %s, %s) """

        valeur = ( pas_operation,  achat, vent, point )
        
        cursor.execute(mySql_insert_query, valeur)
        connection.commit()
        print("insertion des valeurs r")

    except mysql.connector.Error as error:
        print("Failed to insert into MySQL table {}".format(error))
        


def update( con, id ):
    try:
        connection = con

        cursor = connection.cursor()
        
        sql_select_query = """ UPDATE retrait SET status = %s WHERE id = %s """
        valeur = ("Retrait valider par le bot",id)
        cursor.execute(sql_select_query, valeur)
        connection.commit()
                     
    except mysql.connector.Error as error:
        print("Erreur de connection a MySQL: {}".format(error))
        
        
        
def update2( con, table, montant, id ):
    try:
        connection = con

        cursor = connection.cursor()
        
        sql_select_query = """ UPDATE """+table+""" SET usdt = %s WHERE id = %s """
        valeur = (montant,id)
        cursor.execute(sql_select_query, valeur)
        connection.commit()
                     
    except mysql.connector.Error as error:
        print("Erreur de connection a MySQL: {}".format(error))
        
        

def updateCrypto( con, quantiter, id ):
    try:
        connection = con

        cursor = connection.cursor()
        
        sql_select_query = """ UPDATE crypto SET quantiter = %s WHERE id = %s """
        valeur = (quantiter,id)
        cursor.execute(sql_select_query, valeur)
        connection.commit()
                     
    except mysql.connector.Error as error:
        print("Erreur de connection a MySQL: {}".format(error))


def updateActuelPrix( con, table, prix_actuel, id ):
    try:
        connection = con

        cursor = connection.cursor()
        
        sql_select_query = """ UPDATE """+table+""" SET prix_actuel = %s WHERE id = %s """
        valeur = (prix_actuel,id)
        cursor.execute(sql_select_query, valeur)
        connection.commit()
                     
    except mysql.connector.Error as error:
        print("Erreur de connection a MySQL: {}".format(error))



def insertValeurPortefeuilleH24(con, valeurPortefeuille, benefice, pourcentage):
    try:
        connection = con
        
        cursor = connection.cursor()

        mySql_insert_query = """INSERT INTO h24 ( valeurPortefeuille, benefice, pourcentage ) VALUES ( %s, %s, %s ) """

        valeur = ( valeurPortefeuille, benefice, pourcentage)
        
        cursor.execute(mySql_insert_query, valeur)
        connection.commit()
        print("insertion des valeurs r")

    except mysql.connector.Error as error:
        print("Failed to insert into MySQL table {}".format(error))
        

def insertValeurPortefeuilleM1(con, valeurPortefeuille, benefice, pourcentage):
    try:
        connection = con
        
        cursor = connection.cursor()

        mySql_insert_query = """INSERT INTO h24 ( valeurPortefeuille, benefice, pourcentage ) VALUES ( %s, %s, %s ) """

        valeur = ( valeurPortefeuille, benefice, pourcentage)
        
        cursor.execute(mySql_insert_query, valeur)
        connection.commit()
        print("insertion des valeurs r")

    except mysql.connector.Error as error:
        print("Failed to insert into MySQL table {}".format(error))

# messages = " Bibliotheque ernest.py charger sans probleme "
# telegram_send.send(messages=[messages])

# UPDATE visiteur SET visite = ? WHERE jour = ?

# insert(1, 2, 3, 4, 5, 6, 7,8,9,10,11,12,13,14,15)

# get(connection1, "bot_1",0)



