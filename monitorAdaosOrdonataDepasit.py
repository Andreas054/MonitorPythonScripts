def monitorAdaosOrdonataDepasit():
    import fdb # apt install libfbclient2
    import time
    import telepot
    import traceback
    
    from config import telegramid, telegramidNd, telepotBotToken, magNume, dbdir

    bot = telepot.Bot(telepotBotToken)

    adaosReferintaMaxim = 20

    SClasificareMagazine = {
        "P1": "S4",
        "P2": "S4",
        "P3": "S3",
        "P4": "S4",
        "P5": "S2",
        "Cob": "S3",
        "Fet": "S4",
        "CTp6": "S3",
        "CTg": "S3"
    }

    for magSelectat in range(len(magNume)):
        print(magNume[magSelectat])

        try:
            fdbConnection = fdb.connect(dsn = dbdir[magSelectat], user = "sysdba", password = "masterkey") # Firebird
            fdbCursor1 = fdbConnection.cursor()
            fdbCursor2 = fdbConnection.cursor()

            SClasificareMagSelectat = SClasificareMagazine[magNume[magSelectat]]

            fdbCommandSql = f"SELECT ID{SClasificareMagSelectat} FROM {SClasificareMagSelectat} WHERE cod = '1'" # Ordonanta > Adaos Limitat
            fdbCursor1.execute(fdbCommandSql)
            idS = fdbCursor1.fetchone()[0]

            fdbCommandSql = f"SELECT artnr, descriere, pret, (SELECT tva FROM tva WHERE idtva = catalog.idtva), adaos_referinta FROM catalog WHERE {SClasificareMagSelectat} = {idS}"
            fdbCursor1.execute(fdbCommandSql)
            listaCursor1 = fdbCursor1.fetchall()
            
            messageStr = ""
            produsFound = False

            for artNr, descriere, pret, tva, adaosReferinta in listaCursor1:
                pretCuTva = round(pret * (1 + tva / 100), 2)

                # ultimul pret de achizitie
                fdbCommandSql = f"SELECT FIRST 1 pretach FROM recitems WHERE (SELECT idfurn FROM rec WHERE idrec = recitems.idrec) IS NOT NULL AND artnr = {artNr} ORDER BY idrecitem DESC"
                fdbCursor2.execute(fdbCommandSql)
                listaCursor2 = fdbCursor2.fetchall()
                if listaCursor2 != []:
                    pretAchizitie = listaCursor2[0][0]
                else:
                    # fallback, ultimul pret de achizitie fara furnizor
                    fdbCommandSql = f"SELECT FIRST 1 pretach FROM recitems WHERE artnr = {artNr} ORDER BY idrecitem DESC"
                    fdbCursor2.execute(fdbCommandSql)
                    listaCursor2 = fdbCursor2.fetchall()
                    if listaCursor2 != []:
                        pretAchizitie = listaCursor2[0][0]
                    else:
                        # daca nu exista niciun pret de achizitie
                        pretAchizitie = None # ???
                
                if pretAchizitie == None:
                    messageStr += f"{descriere[:20].ljust(24)}{str(pretCuTva).ljust(9)}{str(pretAchizitie).ljust(9)}\n"
                else:
                    pretAchizitie = round(pretAchizitie * (1 + tva / 100), 2)

                    adaosProdus = round((pretCuTva - pretAchizitie) / pretAchizitie * 100, 2)

                    if adaosProdus >= adaosReferintaMaxim:
                        produsFound = True
                        adaosProdus = str(adaosProdus)
                        messageStr += f"{descriere[:20].ljust(24)}{str(pretCuTva).ljust(9)}{str(pretAchizitie).ljust(9)}{adaosProdus}%\n"                    
            
            if produsFound:
                messageStr += "```"
                messageStr = f"*{magNume[magSelectat]}*\n```OrdonantaAdaos-Maxim_{adaosReferintaMaxim}%\n" + "NumeProdus".ljust(24) + "Pret".ljust(9) + "PretAch".ljust(9) + "Adaos\n=================================================\n" + messageStr
                print(messageStr)

                bot.sendMessage(telegramid, messageStr, parse_mode= 'Markdown')
                bot.sendMessage(telegramidNd, messageStr, parse_mode= 'Markdown')
            
            fdbConnection.close()
            time.sleep(1)
        except Exception as e:
            print(f"Eroare comunicare server\n{e}")
            print(traceback.format_exc())

if __name__ == '__main__':
    monitorAdaosOrdonataDepasit()
