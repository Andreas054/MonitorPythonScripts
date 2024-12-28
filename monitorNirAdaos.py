def monitorNirAdaos():
    import fdb # apt install libfbclient2
    import time
    import telepot
    import datetime

    from config import telegramid, telegramidNd, telepotBotToken, magNume, dbdir

    bot = telepot.Bot(telepotBotToken)

    diferentaPretMaxim = 2500

    for magSelectat in range(len(magNume)):
        print(magNume[magSelectat])

        try:
            fdbConnection = fdb.connect(dsn = dbdir[magSelectat], user = "sysdba", password = "masterkey") # Firebird
            fdbCursor1 = fdbConnection.cursor()

            dataQueryStart = (datetime.datetime.now() - datetime.timedelta(days = 2)).strftime('%Y-%m-%d') # 2 days ago

            fdbCommandSql = f"SELECT idrec, nir, datanir, valfaratva - valfaratvafact FROM rec WHERE codop = 1 AND nir is not null AND datanir >= '{dataQueryStart}' ORDER BY datanir DESC"
            fdbCursor1.execute(fdbCommandSql)
            listaCursor1 = fdbCursor1.fetchall()
            
            messageStr = ""
            nirFound = False

            for idrec, nir, datanir, valDifPret in listaCursor1:
                nir = str(nir)
                datanir = str(datanir)
                valDifPret = round(valDifPret, 2)
                #if valDifPret < 0:
                    #valDifPret = (-1) * valDifPret

                if valDifPret >= diferentaPretMaxim or valDifPret <= -diferentaPretMaxim:
                    nirFound = True
                    valDifPret = str(valDifPret)
                    messageStr += f"{'Data'.ljust(12)}{'Nr NIR'.ljust(8)}{'Diferenta'}\n"
                    messageStr += f"{datanir.ljust(12)}{nir.ljust(8)}{valDifPret}\n"

                    fdbCommandSql = f"SELECT FIRST 5 ABS(cantfiz * pretvanzare - cantfiz * pretach), cantfiz * pretvanzare - cantfiz * pretach, denumire FROM recitems WHERE idrec = {idrec} ORDER BY 1 DESC"
                    fdbCursor1.execute(fdbCommandSql)
                    listaCursor2 = fdbCursor1.fetchall()

                    messageStr += f"\t{'Diferenta'.ljust(12)}{'Produs'}\n"
                    for _, diferentaPret, numeProdus in listaCursor2:
                        diferentaPret = round(diferentaPret, 2)
                        diferentaPret = str(diferentaPret)
                        messageStr += f"\t{diferentaPret.ljust(12)}{numeProdus}\n"
                    messageStr += '\n'
            
            if nirFound:
                messageStr += "```"
                messageStr = f"*{magNume[magSelectat]}*\n```NIR\n" + messageStr
                print(messageStr)
                bot.sendMessage(telegramid, messageStr, parse_mode= 'Markdown')
                bot.sendMessage(telegramidNd, messageStr, parse_mode= 'Markdown')
            
            fdbConnection.close()
            time.sleep(1)
        except Exception as e:
            print(f"Eroare comunicare server\n{e}")

if __name__ == '__main__':
    monitorNirAdaos()
