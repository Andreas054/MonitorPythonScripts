def monitorDiferentaLDI():
    import fdb # apt install libfbclient2
    import time
    import telepot
    import datetime

    from config import telegramid, telegramidNd, telepotBotToken, magNume, dbdir

    bot = telepot.Bot(telepotBotToken)

    diferentaPretMaxim = 1000

    for magSelectat in range(len(magNume)):
        print(magNume[magSelectat])

        try:
            fdbConnection = fdb.connect(dsn = dbdir[magSelectat], user = "sysdba", password = "masterkey") # Firebird
            fdbCursor1 = fdbConnection.cursor()

            dataQueryStart = (datetime.datetime.now() - datetime.timedelta(days = 2)).strftime('%Y-%m-%d') # 2 days ago

            fdbCommandSql = f"SELECT idpv, datapv, SUM(pretnou * stoc) - SUM(pretvechi * stoc) FROM pvmodpret WHERE datapv >= '{dataQueryStart}' GROUP BY idpv, datapv ORDER BY datapv DESC"
            fdbCursor1.execute(fdbCommandSql)
            listaCursor1 = fdbCursor1.fetchall()
            
            messageStr = ""
            ldiFound = False

            for idpv, datapv, valDifPret in listaCursor1:
                idpv = str(idpv)
                datapv = str(datapv)
                valDifPret = round(valDifPret, 2)
                #if valDifPret < 0:
                    #valDifPret = (-1) * valDifPret

                if valDifPret >= diferentaPretMaxim or valDifPret <= -diferentaPretMaxim:
                    ldiFound = True
                    valDifPret = str(valDifPret)
                    messageStr += f"{'Data'.ljust(12)}{'Nr LDI'.ljust(8)}{'Diferenta'}\n"
                    messageStr += f"{datapv.ljust(12)}{idpv.ljust(8)}{valDifPret}\n"

                    fdbCommandSql = f"SELECT FIRST 5 ABS(pretnou * stoc - pretvechi * stoc), pretnou * stoc - pretvechi * stoc, (SELECT descriere FROM catalog WHERE catalog.artnr = pvmodpret.artnr) FROM pvmodpret WHERE idpv = {idpv} ORDER BY 1 DESC"
                    fdbCursor1.execute(fdbCommandSql)
                    listaCursor2 = fdbCursor1.fetchall()

                    messageStr += f"\t{'Diferenta'.ljust(12)}{'Produs'}\n"
                    for _, diferentaPret, numeProdus in listaCursor2:
                        diferentaPret = round(diferentaPret, 2)
                        diferentaPret = str(diferentaPret)
                        messageStr += f"\t{diferentaPret.ljust(12)}{numeProdus}\n"
                    messageStr += '\n'
                    
            if ldiFound:
                messageStr += "```"
                messageStr = f"*{magNume[magSelectat]}*\n```LDI\n" + messageStr
                print(messageStr)
                bot.sendMessage(telegramid, messageStr, parse_mode= 'Markdown')
                bot.sendMessage(telegramidNd, messageStr, parse_mode= 'Markdown')
            
            fdbConnection.close()
            time.sleep(1)
        except Exception as e:
            print(f"Eroare comunicare server\n{e}")

if __name__ == '__main__':
    monitorDiferentaLDI()
