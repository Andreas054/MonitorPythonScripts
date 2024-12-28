def monitorNirAvizeDublu(dataQueryPastDaysAgo):
    import fdb # apt install libfbclient2
    import time
    import telepot

    from config import telegramid, telegramidSm, telepotBotToken, magNume, dbdir

    bot = telepot.Bot(telepotBotToken)

    def checkDuplicates(fdbCommandSql, nirSauAviz):
        dictionarMagNiruriAvize = {
            "P1": [],
            "P2": [],
            "P3": [],
            "P4": [],
            "P5": [],
            "Cob": [],
            "Fet": [],
            "CTp6": [],
            "CTg": []
        }

        dictionarMagHelper = {}

        for magSelectat in range(len(magNume)):
            print(magNume[magSelectat])

            try:
                fdbConnection = fdb.connect(dsn = dbdir[magSelectat], user = "sysdba", password = "masterkey") # Firebird
                fdbCursor1 = fdbConnection.cursor()

                fdbCursor1.execute(fdbCommandSql)
                listaCursor1 = fdbCursor1.fetchall()
                
                for idRec, nrNIR, webFurnizor, nrFactura, dataFactura, valFactura, numeFurnizor in listaCursor1:
                    nrFactura = ''.join(filter(str.isdigit, nrFactura))
                    valFactura = float(valFactura)

                    # remove zeroes from begging of nrFactura string
                    nrFactura = nrFactura.lstrip("0")

                    # dictionarMagNiruriAvize[magNume[magSelectat]].append((idRec, nrNIR, webFurnizor, nrFactura, dataFactura, valFactura, numeFurnizor))
                    dictionarMagNiruriAvize[magNume[magSelectat]].append((webFurnizor, nrFactura, dataFactura))

                    tmpTupluKey = (magNume[magSelectat], webFurnizor, nrFactura, dataFactura)
                    if tmpTupluKey in dictionarMagHelper:
                        dictionarMagHelper[tmpTupluKey].append((idRec, nrNIR, webFurnizor, nrFactura, dataFactura, valFactura, numeFurnizor))
                    else:
                        dictionarMagHelper[tmpTupluKey] = [(idRec, nrNIR, webFurnizor, nrFactura, dataFactura, valFactura, numeFurnizor)]
                
                fdbConnection.close()
                time.sleep(1)
            except Exception as e:
                print(f"Eroare comunicare server\n{e}")
            
        listaTupluriAllValues = [x for xs in dictionarMagNiruriAvize.values() for x in xs]
        
        # check if any duplicate values in list (webFurnizor, nrFactura, dataFactura)
        duplicateValues = [item for item in listaTupluriAllValues if listaTupluriAllValues.count(item) > 1]
        # print(duplicateValues)
        duplicateValues = list(set(duplicateValues))

        # sort duplicateValues by dataFactura desc
        duplicateValues.sort(key = lambda x: x[2], reverse = True)

        messageStr = ""
        for tuplu in duplicateValues:
            print()
            for magazin in dictionarMagNiruriAvize:
                if tuplu in dictionarMagNiruriAvize[magazin]:
                    print(f"{magazin.ljust(4)} Furnizor: {tuplu[0].ljust(5)} DataFactura: {tuplu[2]} NrFactura: {tuplu[1]}")

                    messageStr += f"{magazin.ljust(4)} {tuplu[2]}  {tuplu[1]}\n" # magazin, dataFactura, nrFactura
                    
                    tmpTupluKey = (magazin, tuplu[0], tuplu[1], tuplu[2])
                    listaDetalii = dictionarMagHelper[tmpTupluKey]

                    messageStr += "\t\tNIR/Aviz ValFact Furnizor\n"
                    for idRec, nrNIR, webFurnizor, nrFactura, dataFactura, valFactura, numeFurnizor in listaDetalii:
                        messageStr += f"\t\t{str(nrNIR).ljust(8)} {str(valFactura).ljust(7)} {numeFurnizor[:25]}\n" # nrNIR, valFactura, numeFurnizor
            
            if messageStr != "":
                messageStr += "------------------------------\n"
        
        if messageStr != "":
            messageStr = f"```{nirSauAviz}\nMag  DataFactura NrFactura\n------------------------------\n" + messageStr + "```"
            # bot.sendMessage(telegramid, messageStr, parse_mode= 'Markdown')
            bot.sendMessage(telegramidSm, messageStr, parse_mode= 'Markdown')

    fdbCommandSql = f"SELECT idrec, nir, (SELECT web FROM furnizori WHERE idfurn = rec.idfurn), nrfact, datafact, valfaratvafact + valtvafact, (SELECT nume FROM furnizori WHERE idfurn = rec.idfurn) FROM rec WHERE stare = 1 AND codop = 1 AND nir IS NOT NULL AND datanir >= '{dataQueryPastDaysAgo}'"
    checkDuplicates(fdbCommandSql, 'NIR')

    fdbCommandSql = f"SELECT idout, nrretfurn, (SELECT web FROM furnizori WHERE idfurn = out.idfurn), observatii, dataretfurn, valretfurn, (SELECT nume FROM furnizori WHERE idfurn = out.idfurn) FROM out WHERE inchis = 1 AND codop = 4 AND char_length(observatii) > 0 AND data_event >= '{dataQueryPastDaysAgo}'"
    checkDuplicates(fdbCommandSql, 'Aviz')

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage\tpython3 monitorNirAvizeDublu.py <last N days>\ni.e.\tpython3 monitorNirAvizeDublu.py 0 - today")
        sys.exit(1)
    elif not sys.argv[1].isdigit():
        print("Usage\tpython3 monitorNirAvizeDublu.py <last N days>\ni.e.\tpython3 monitorNirAvizeDublu.py 0 - today")
        sys.exit(1)

    import datetime
    dataQueryPastDaysAgo = (datetime.datetime.now() - datetime.timedelta(days = int(sys.argv[1]))).strftime('%Y-%m-%d')
    
    monitorNirAvizeDublu(dataQueryPastDaysAgo)
