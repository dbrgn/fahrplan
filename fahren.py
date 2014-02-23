
//Well i think this program need no comment:

import os
import fahrplan
def NunningenOlten():
    Nunningen_Olten = os.system('fahrplan from Nunningen to Olten')


def OltenNunningen():
    Olten_Nunningen = os.system('fahrplan from Olten to Nunningen')


def OltenOensingen():
    Olten_Oensingen = os.system('fahrplan from Olten to Oensingen')


def OensingenOlten():
    Oensingen_Olten = os.system('fahrplan from Oensingen to Olten')
    print Oensingen_Olten

def Eingabe():
    print("Folgende Verbindungen stehen zur Auswahl\n")
    Verbindung1 ="1:Von Nunningen nach Olten"
    Verbindung2 = "2:Von Olten nach Nunningen"
    Verbindung3 = "3:Von Olten nach Oensingen"
    Verbindung4 = "4:von Oensingen nach Olten"
    print(Verbindung1 + "\n")
    print(Verbindung2 + "\n")
    print(Verbindung3 + "\n")
    print(Verbindung4 + "\n")


    Eingabe = input("Geben Sie eine Verbindung ein\n")
    if Eingabe == 1:
        print ("Sie haben die Verbindung von" + " " + Verbindung1 + " " + "gewaehlt")
        NunningenOlten();
    if Eingabe == 2:
        OltenNunningen()
    if Eingabe == 3:
        OltenOensingen()
    if Eingabe == 4:
        OensingenOlten()
        return Eingabe
    if (Eingabe > 4) or (Eingabe <1):
        print "Es wurde die falsche Nummer gewaehlt das Programm startet nochmals"
        os.system('python fahren.py')
Eingabe();


