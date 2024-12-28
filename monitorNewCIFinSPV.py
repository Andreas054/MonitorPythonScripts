def monitorNewCIFinSPV():
    import MySQLdb # apt install pkg-config default-libmysqlclient-dev && python3 -m pip install mysqlclient
    import telepot

    from config import telegramid, telegramidSm, telepotBotToken, knownCIF_inSPV

    bot = telepot.Bot(telepotBotToken)

    mysqldb = MySQLdb.connect(host = "192.168.60.200", user = "efacturauser_remote_181", passwd = "1234", db = "efactura") # MySQL
    mySqlCursor = mysqldb.cursor()

    def queryMySQL(operationType, query):
        try:
            print(query)
            mySqlCursor.execute(query)

            if (operationType == "CREATE"):
                mysqldb.commit()
            else:
                return mySqlCursor.fetchall()
        except:
            if (operationType == "CREATE"):
                mysqldb.rollback()
            print("eroare mysql")
        
        return []

    listaRaspunsMySQL = queryMySQL("READ", f"SELECT DISTINCT cif_emitent FROM primite WHERE cif_emitent NOT IN {knownCIF_inSPV}")

    if len(listaRaspunsMySQL) != 0:
        listaCIFNoi = [int(x[0]) for x in listaRaspunsMySQL]
        print(listaCIFNoi)
        
        bot.sendMessage(telegramid, f"Exista {len(listaCIFNoi)} CIF-uri noi in SPV: {listaCIFNoi}")
        bot.sendMessage(telegramidSm, f"Exista {len(listaCIFNoi)} CIF-uri noi in SPV: {listaCIFNoi}")

if __name__ == '__main__':
    monitorNewCIFinSPV()
