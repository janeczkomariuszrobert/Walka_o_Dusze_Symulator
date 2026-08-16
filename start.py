print("Walka o Dusze - symulator v1.6 \nAutor: Mariusz Janeczko")

import os
from datetime import datetime
from Silnik.obiekty import Talia
from Silnik.mechanika import *
from Silnik.walka import *

AKCJE_STARTOWE = 5
PRAWDOPODOBIENSTWO_ZARAZY = 0.25
PRAWDOPODOBIENSTWO_LECZENIA = 0.25
STARTOWY_KOSZT_ODNOWY = 2


os.makedirs("LOGI", exist_ok=True)
czas_startu = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
nazwa_logu = f"LOGI/log_{czas_startu}.txt"
ustaw_log(nazwa_logu)  #przekaż do pliku który uzywa tej funkcji.

statystyki = {
    "runda": 0,
    "zabite_pionki": 0,
    "zabite_klasa5": 0,
    "akcje_bialy": AKCJE_STARTOWE,
    "akcje_czarny": AKCJE_STARTOWE,
    "chorzy_poprzednia":0,
    "chorzy_biezaca":0,
    "punkty_arena_bialy":0,
    "zwyciezca":None,
    "rzut_akcji_bialy": int(1 / PRAWDOPODOBIENSTWO_LECZENIA),
    "rzut_akcji_czarny": int(1 / PRAWDOPODOBIENSTWO_ZARAZY),
    "koszt_odnowy_bialy": STARTOWY_KOSZT_ODNOWY,
    "koszt_odnowy_czarny": STARTOWY_KOSZT_ODNOWY,
    "Smierc_zyje": 'TAK',
    "Laska_zyje": 'TAK'
}

biale_gotowe = Talia()
biale_odpoczywajace = Talia()
biale_stos_smierci = Talia()

czarne_gotowe = Talia()
czarne_odpoczywajace = Talia()
czarne_stos_smierci = Talia()


excel_na_json("DANE/karty_v1.xlsx","DANE/karty_v1.json")

biale_gotowe.wczytaj("DANE/karty_v1.json", "biały")
czarne_gotowe.wczytaj("DANE/karty_v1.json", "czarny")

biale_gotowe.potasuj()
czarne_gotowe.potasuj()


maksymalna_liczba_rund = 100
runda = 1
while runda <= maksymalna_liczba_rund:

    if statystyki["zabite_klasa5"] >= 3:
        loguj("Koniec gry - Biały zrealizował cel")
        break

    if statystyki["zabite_pionki"] >= 50:
        loguj("Koniec gry - Czarny zrealizował cel")
        break

    loguj("================")
    loguj(f"RUNDA {runda}")

    #odnowa wymuszona
    if len(biale_gotowe) < LICZBA_SLOTOW_ARENY:
        odnowa(biale_gotowe,biale_odpoczywajace,statystyki,"bialy",runda,STARTOWY_KOSZT_ODNOWY+1)  #kara za wymuszoną odnowe
    if len(czarne_gotowe) < LICZBA_SLOTOW_ARENY:
        odnowa(czarne_gotowe,czarne_odpoczywajace,statystyki,"czarny",runda,STARTOWY_KOSZT_ODNOWY+1)  


    # pobranie ręki
    biale_na_arenie = biale_gotowe.pobierz_reke(4)
    czarne_na_arenie = czarne_gotowe.pobierz_reke(4)
    
    ### WALKA ###
    ustaw_puste_sloty(biale_na_arenie,czarne_na_arenie)  #przestaw kolejność jeżeli są walkowerowy - najslabsza karta 
    wynik,biale_zywe,czarne_zywe, biale_aktywne, czarne_aktywne, biale_zabite_runda, czarne_zabite_runda = walka_arena(biale_na_arenie,czarne_na_arenie, statystyki)
    statystyki['punkty_arena_bialy'] = policz_punkty_rundy(wynik)
    statystyki["zwyciezca"] = ustal_zwyciezce_rundy(statystyki['punkty_arena_bialy'],biale_aktywne,czarne_aktywne)
    loguj_stan_areny(biale_na_arenie,czarne_na_arenie,biale_aktywne,czarne_aktywne)
    loguj(f"Wynik: {''.join(wynik)} | Punkty Areny Białych: {statystyki['punkty_arena_bialy']} | Zwycięzca Rundy: {statystyki['zwyciezca']}")

    biale_aktywne.karty.sort(key=lambda karta: karta.klasa, reverse=True) #zaczynamy od najwyższej klasy
    czarne_aktywne.karty.sort(key=lambda karta: karta.klasa, reverse=True)

    kolejnosc_graczy = ["bialy", "czarny"]

    if statystyki["zwyciezca"] == "czarny":
        kolejnosc_graczy.reverse()

    ### WYDARZENIA ###


    ### AKCJE ###
    for gracz in kolejnosc_graczy:
        if gracz == "bialy":
            if len(biale_gotowe) < LICZBA_SLOTOW_ARENY:
                odnowa(biale_gotowe,biale_odpoczywajace,statystyki,"bialy",runda,statystyki["koszt_odnowy_bialy"])
            wykonaj_akcje_kart(biale_aktywne,statystyki,"bialy")
            wykonaj_akcje_pionkow(statystyki,"bialy")
        else:
            rozlicz_choroby(statystyki) # z poprzedniej rundy
            if len(czarne_gotowe) < LICZBA_SLOTOW_ARENY:
                odnowa(czarne_gotowe,czarne_odpoczywajace,statystyki,"czarny",runda,statystyki["koszt_odnowy_czarny"])
            wykonaj_akcje_kart(czarne_aktywne,statystyki,"czarny")
            wykonaj_akcje_pionkow(statystyki,"czarny")

    ### SPRZATANIE PO WALKACH ###

    # żywe karty wracają do odpoczynku
    biale_odpoczywajace.przenies(biale_zywe)
    czarne_odpoczywajace.przenies(czarne_zywe)

    # martwe karty idą do stosu śmierci
    biale_stos_smierci.przenies(biale_zabite_runda)
    czarne_stos_smierci.przenies(czarne_zabite_runda)

    loguj(
        "Podsumowanie Rundy - Białe: ",
        'Got ', len(biale_gotowe),
        'Odp ', len(biale_odpoczywajace),
        'Martwe: ', len(biale_stos_smierci),
        'Zabite karty Spec: ', statystyki["zabite_klasa5"]
        )

    loguj(
        "Podsumowanie Rundy - Czarne: ",
        'Got ', len(czarne_gotowe),
        'Odp ', len(czarne_odpoczywajace),
        'Martwe: ',len(czarne_stos_smierci),
        'Zabite pionki ', statystyki["zabite_pionki"]
        )

    loguj(
        "Stan chorych: ",
        'Poprzednia: ', statystyki["chorzy_poprzednia"],
        'Aktualna: ', statystyki["chorzy_biezaca"]
        )

    runda += 1
    statystyki["runda"] += 1

    #reset statystyk rundowych
    statystyki["akcje_bialy"] = AKCJE_STARTOWE
    statystyki["akcje_czarny"] = AKCJE_STARTOWE
    statystyki["rzut_akcji_czarny"] = int(1 / PRAWDOPODOBIENSTWO_ZARAZY)
    statystyki["rzut_akcji_bialy"] = int(1 / PRAWDOPODOBIENSTWO_LECZENIA)
    statystyki["koszt_odnowy_bialy"]=STARTOWY_KOSZT_ODNOWY
    statystyki["koszt_odnowy_czarny"]=STARTOWY_KOSZT_ODNOWY

### KONIEC GRY ###

loguj("\nKarty Specjalne:")
loguj("ŚMIERĆ żyje:",statystyki["Smierc_zyje"])
loguj("ŁASKA żyje:",statystyki["Laska_zyje"])

loguj("\nBiałe karty które przeżyły:")
for karta in biale_gotowe.karty + biale_odpoczywajace.karty:
    loguj(karta.id, karta.imie, karta.sila)

loguj("\nCzarne karty które przeżyły:")
for karta in czarne_gotowe.karty + czarne_odpoczywajace.karty:
    loguj(karta.id, karta.imie, karta.sila)