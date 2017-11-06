import os
from tqdm import tqdm
import json
import time
from datetime import date as DT

FORMAT_LOADED = False
FORMAT_IS_META = False
zero_fill = "00000"

META_DICT = {}

dict_formato_non_meta = {"formato": "",
                         "sample": "",
                         "id_term_start": "", "id_term_end": "", "verso": "",
                         "badge_start": "", "badge_end": "", "badge_pos": "",
                         "data_start": "", "data_end": "", "data_pos": "",
                         "time_start": "", "time_end": "", "separator": ""}

dict_formato_caricato = {}

dict_formato = {"formato": "konnect",
                 "sample": "0001 A 0000000000 12/10/2017 05:35 000000",
                 "id_term_start": 0, "id_term_end": 3, "verso": 5,
                 "badge_start": 7, "badge_end": 16, "badge_pos": 2,
                 "data_start": 18, "data_end": 27, "data_pos": 3,
                 "time_start": 29, "time_end": 33, "separator": " "}


def menuformati(config):
    choice = ""
    while choice != "q":
        print("Scegliere una opzione:")
        print("0 - Elenco Formati")
        print("1 - Nuovo Formato")
        print("2 - Nuovo META-FORMATO")
        print("3 - Carica Formato")
        print("q - Menu Precedente")
        choice = input()
        if choice == "0":
            elencoformati(config)
        elif choice == "1":
            nuovoformato(config)
        elif choice == "2":
            nuovometaformato(config)
        elif choice == "3":
            caricaformato(config)


def elencoformati(config):
    with open(config) as config_file:
        cfg = json.load(config_file)
        for item in cfg['formati']:
            print(item['formato'])


def nuovoformato(config):
    print("Definizione nuovo formato")
    print("Contate le cifre partendo da ZERO")
    print("Se il formato ha un separatore per i vari campi ad esempio uno spazio, \n" +
           "allora i valori *_pos devono essere assegnati dando al primo campo il valore 0")
    print("Se il formato non ha separatori, allora il valore separatore e i *_pos non vanno attribuiti")
    for k in dict_formato.keys():
        print("Valore per: " + k)
        dict_formato[k] = input()
    print(dict_formato)
    with open(config, 'r') as config_file:
        formati = json.load(config_file)
    with open(config, 'w') as config_file:
        formati['formati'].append(dict_formato)
        json.dump(formati, config_file)


def nuovometaformato(config):
    end = True
    choice = ""
    global META_DICT
    META_DICT = {}

    META_DICT["formato"] = ""
    META_DICT["META"] = True
    print("Definiziione META formato")
    print("Questa funzione permette di definire un dizionario chiave - valore, \n" +
          "ad ogni chiave corrisponde un campo da estrarre" +
          "i valori di ogni chiave sono la posizione del carattere iniziale e di quello finale che compongono il campo")

    while META_DICT["formato"] == "":
        print("Inserire Nome Del formato:")
        META_DICT["formato"] = input()

    while end:
        print("Nome del campo (chiave)?")
        chiave = input()
        print("Poisizione Carattere iniziale")
        cstart = input()
        cend = input("Posizone Carattere Finale")
        META_DICT[chiave] = [cstart, cend]
        while choice != "S" and choice != "s" and choice != "N" and choice != "n":
            print("Vuoi inseirere altre chiavi? S/N")
            choice = input()
            if choice == "N" or choice == "n":
                end = False
            elif choice != "S" and choice != "s" and choice != "N" and choice != "n":
                print("Scelta non valida: S - s / N - n")

    with open(config, 'r') as config_file:
        formati = json.load(config_file)
    with open(config, 'w') as config_file:
        formati['formati'].append(META_DICT)
        json.dump(formati, config_file)


def caricaformato(config):
    global FORMAT_LOADED
    global FORMAT_IS_META
    global dict_formato_caricato
    formato_found = False
    quit = False
    dict_to_load = {}
    while formato_found == False and quit == False:
        print("Nome Formato Da caricare:")
        nome_formato = input()
        with open(config, 'r') as config_file:
            cfg = json.load(config_file)
            for item in cfg['formati']:
                if item['formato'] == nome_formato:
                    print("Formato Trovato, caricamento...")
                    formato_found = True
                    dict_to_load = item
                    quit = True
                    break
            if formato_found != True:
                print("Formato Non Presente, premere invio per altro formato...")
                print("Oppure premere q per menu precendente")
                quit = input()
                if quit == "q":
                    quit = True
            else:
                dict_formato_caricato = dict_to_load
                print(dict_formato_caricato)
                if "META" in dict_formato_caricato.keys():
                    FORMAT_IS_META = True
                    print("Questo Formato e un META-FORMATO")

                else:
                    """for k in dict_formato_caricato.keys():
                        dict_formato_caricato[k] = dict_to_load[k]"""
                    print("Formato Standard Caricato")
                FORMAT_LOADED = True



def encodeNumberInLine(file, param_number):
    output_file = file + "out" + ".txt"
    SEP = False
    if dict_formato_caricato['separator'] != "":
        SEP = True
    with open(output_file, 'w') as out:
        with open(file+".txt") as filetxt:
            for line_number, line in tqdm(enumerate(filetxt, 1)):
                try:
                    encoded_number_str = zero_fill
                    if SEP:
                        params = line.split(dict_formato_caricato['separator'])
                        number = params[param_number]
                    else:
                        number = line[int(dict_formato_caricato['badge_start']):int(dict_formato_caricato['badge_end'])]
                    number_split = []
                    for i in range(0, len(number), 2):
                        number_split.append(number[i:i+2])
                    for i in range(0, len(number_split)):
                        if number_split[i] == "00":
                            number_split[i] = "0"
                        else:
                            number_split[i] = str(hex(int(number_split[i])))[2:]
                        encoded_number_str += (number_split[i])
                    # print(encoded_number_str)
                    if SEP:
                        params[2] = encoded_number_str
                        new_line = ""
                        for i in range(0,len(params)-1):
                            new_line = new_line + params[i] + " "
                        new_line = new_line + params[len(params)-1]
                        out.write(new_line)
                    else:
                        line.replace(line[int(dict_formato_caricato['badge_start']):int(dict_formato_caricato['badge_end'])+1], encoded_number_str)
                except IndexError:
                    print("\nErrore Linea non conforme")
                    print("errore @: " + str(line_number))
                    print(line)
    return


def extractByBadge(file, badge_number):
    output_file = file + "out" + ".txt"
    if dict_formato_caricato['separator'] != "":
        print("Con Separatore...")
        with open(output_file, 'w') as out:
            with open(file+".txt") as filetxt:
                for line_number, line in tqdm(enumerate(filetxt, 1)):
                    try:
                        params = line.split(" ")
                        badge = params[int(dict_formato_caricato['badge_pos'])]
                        if badge == badge_number:
                            out.write(line)
                    except IndexError:
                        print("\n Errore Linea non conforme")
                        print("errore @: " + str(line_number))
                        print(line)
                print("job done: " + output_file + " per risultati")
    else:
        print("Senza Separatore... " + badge_number)
        with open(output_file, 'w') as out:
            with open(file+".txt") as filetxt:
                for line_number, line in tqdm(enumerate(filetxt, 1)):
                    try:
                        badge = line[int(dict_formato_caricato['badge_start']): int(dict_formato_caricato['badge_end'])+1]
                        if badge == badge_number:
                            out.write(line)
                    except IndexError:
                        print("\n Errore Linea non conforme")
                        print("errore @: " + str(line_number))
                        print(line)
                print("job done: " + output_file + " per risultati")


def extractByDate(file, date):
    output_file = file + "out" + ".txt"
    if dict_formato_caricato['separator'] != "":
        with open(output_file, 'w') as out:
            with open(file+".txt") as filetxt:
                for line_number, line in tqdm(enumerate(filetxt, 1)):
                    try:
                        params = line.split(" ")
                        dt = params[int(dict_formato_caricato['data_pos'])]
                        if date == dt:
                            out.write(line)
                    except IndexError:
                        print("\n Errore Linea non conforme")
                        print("errore @: " + str(line_number))
                        print(line)
        print("job done: " + output_file + " per risultati")
    else:
        with open(output_file, 'w') as out:
            with open(file+".txt") as filetxt:
                for line_number, line in tqdm(enumerate(filetxt, 1)):
                    try:
                        dt = line[int(dict_formato_caricato['data_start']):int(dict_formato_caricato['data_end'])+1]
                        if date == dt:
                            out.write(line)
                    except IndexError:
                        print("\n Errore Linea non conforme")
                        print("errore @: " + str(line_number))
                        print(line)
        print("job done: " + output_file + " per risultati")


def splitfromdate(file, dal):
    output_file = file + "out" + ".txt"
    if dict_formato_caricato['separator'] != "":
        with open(output_file, 'w') as out:
            with open(file+".txt") as filetxt:
                for line_number, line in tqdm(enumerate(filetxt, 1)):
                    try:
                        params = line.split(" ")
                        dt = params[int(dict_formato_caricato['data_pos'])]
                        fromdate = time.strptime(dal, "%d/%m/%Y")
                        linedate = time.strptime(dt, "%d/%m/%Y")
                        if linedate >= fromdate:
                            out.write(line)
                    except IndexError:
                        print("\n Errore Linea non conforme")
                        print("errore @: " + str(line_number))
                        print(line)
        print("job done: " + output_file + " per risultati")
    else:
        if len(dal) != 8 and len(dal) != 6:
            print("Questo Formato di data non e supportato")
            return
        else:
            with open(output_file, 'w') as out:
                with open(file+".txt") as filetxt:
                    for line_number, line in tqdm(enumerate(filetxt, 1)):
                        try:
                            dt = line[int(dict_formato_caricato['data_start']):int(dict_formato_caricato['data_end'])+1]
                            if len(dt) == 8:
                                linedate = DT(int(dt[4:8]), int(dt[2:4]), int(dt[0:2]))
                                fromdate = DT(int(dal[4:8]), int(dal[2:4]), int(dal[0:2]))
                            elif len(dt) == 6:
                                linedate = DT(int(dt[4:6]), int(dt[2:4]), int(dt[0:2]))
                                fromdate = DT(int(dal[4:6]), int(dal[2:4]), int(dal[0:2]))
                            if linedate >= fromdate:
                                out.write(line)
                        except IndexError:
                            print("\n Errore Linea non conforme")
                            print("errore @: " + str(line_number))
                            print(line)
        print("job done: " + output_file + " per risultati")


def metaestrai(file):
    campo = ""
    output_file = file + "out" + ".txt"
    print(dict_formato_caricato)
    print("Campi presenti nel meta-formato")
    for key in dict_formato_caricato.keys():
        if key != "META" and key != "formato":
            print(key + " : " + str(dict_formato_caricato[key]))
    while campo not in dict_formato_caricato.keys():
        print("Nome del campo: ")
        campo = input()

    print("Valore da ricercare:")
    value = input()

    with open(output_file, 'w') as out:
        with open(file + ".txt") as filetxt:
            for line_number, line in tqdm(enumerate(filetxt, 1)):
                try:
                    subline = line[int(dict_formato_caricato[campo][0]): int(dict_formato_caricato[campo][1]) + 1]
                    if subline == value:
                        out.write(line)
                except IndexError:
                    print("\n Errore Linea non conforme")
                    print("errore @: " + str(line_number))
                    print(line)

if __name__ == "__main__":
    choice = ""
    file = ""

    while choice != "q":
        print("Scegliere un opzione:")
        print("q - QUIT")
        print("0 - Menu Formati")
        if FORMAT_LOADED:
            print("1 - Converti badge dec -> hex")
            print("2 - Estrai solo badge")
            print("3 - Estrai solo data")
            print("4 - Estrai da data")
            print("5 - META-Estrai")
        choice = input()
        if choice == "0":
            menuformati('estrai.json')
        elif choice == "1" and FORMAT_LOADED:
            print("Nome del file .txt?")
            file = input()
            encodeNumberInLine(file, int(dict_formato_caricato['badge_pos']))
        elif choice == "2" and FORMAT_LOADED:
            print("Nome del file .txt?")
            file = input()
            print("Numero di badge:")
            bn = input()
            extractByBadge(file, bn)
        elif choice == "3" and FORMAT_LOADED:
            print("Nome del file .txt?")
            file = input()
            print("Indicare la data nel formato appropriato")
            date = input()
            extractByDate(file, date)
        elif choice == "4" and FORMAT_LOADED:
            print("Nome del file .txt?")
            file = input()
            print("Indicare la data nel formato appropriato")
            date = input()
            splitfromdate(file, date)
        elif choice == "5" and FORMAT_LOADED and FORMAT_IS_META:
            print("Nome del file .txt?")
            file = input()
            metaestrai(file)
