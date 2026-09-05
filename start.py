print("Walka o Dusze - symulator v2.0 \nAutor: Mariusz Janeczko")

import os
from datetime import datetime
from Silnik.obiekty import Talia
from Silnik.mechanika import *
from Silnik.walka import *

AKCJE_STARTOWE = 5
PRAWDOPODOBIENSTWO_ZARAZY = 0.25
PRAWDOPODOBIENSTWO_LECZENIA = 0.25
STARTOWY_KOSZT_ODNOWY = 2

SCIEZKA_KART="DANE/karty_v1"

os.makedirs("LOGI", exist_ok=True)
czas_startu = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
nazwa_logu = f"LOGI/log_{czas_startu}.txt"
ustaw_log(nazwa_logu)  #przekaż do pliku który uzywa tej funkcji.

statystyki = {
    "runda": 0,
    "zabite_pionki": 0,
    "zabite_klasa5": 0,
    "akcje_biały": AKCJE_STARTOWE,
    "akcje_czarny": AKCJE_STARTOWE,
    "chorzy_poprzednia":0,
    "chorzy_biezaca":0,
    "punkty_arena_biały":0,
    "zwyciezca":None,
    "rzut_akcji_biały": int(1 / PRAWDOPODOBIENSTWO_LECZENIA),
    "rzut_akcji_czarny": int(1 / PRAWDOPODOBIENSTWO_ZARAZY),
    "koszt_odnowy_biały": STARTOWY_KOSZT_ODNOWY,
    "koszt_odnowy_czarny": STARTOWY_KOSZT_ODNOWY,
    "Smierc_zyje": 'TAK',
    "Laska_zyje": 'TAK',
    "zdolnosci": {},
    "wyniki_kart": {},

}

białe_gotowe = Talia()
białe_odpoczywajace = Talia()
białe_stos_smierci = Talia()

czarne_gotowe = Talia()
czarne_odpoczywajace = Talia()
czarne_stos_smierci = Talia()

excel_na_json(SCIEZKA_KART)

białe_gotowe.wczytaj(SCIEZKA_KART, "biały")
czarne_gotowe.wczytaj(SCIEZKA_KART, "czarny")

# Deklaracja struktury liczników zdolności i wyników (None oznacza brak zdolności)
for karta in białe_gotowe.karty + czarne_gotowe.karty:
    klucz = (karta.id, karta.kolor)
    if karta.liczba_zdolnosci_walk == 0:
        statystyki["zdolnosci"][klucz] = {
            "zdolnosc1": None,
            "zdolnosc2": None
        }
    elif karta.liczba_zdolnosci_walk == 1:
        statystyki["zdolnosci"][klucz] = {
            "zdolnosc1": 0,
            "zdolnosc2": None
        }
    elif karta.liczba_zdolnosci_walk == 2:
        statystyki["zdolnosci"][klucz] = {
            "zdolnosc1": 0,
            "zdolnosc2": 0
        }
    statystyki["wyniki_kart"][klucz] = {"liczba_walk": 0,"Z": 0,"W": 0,"R": 0,"P": 0,"U": 0,"wskrzesz": 0}    



BIALE_WYBRANE=[12, 3, 5, 2]
CZARNE_WYBRANE=[19, 4, 7, 2]

symuluj_testowa_arena(
    statystyki,
    białe_gotowe,
    czarne_gotowe,
    BIALE_WYBRANE,
    CZARNE_WYBRANE
)

# białe_gotowe.potasuj()
# czarne_gotowe.potasuj()

# maksymalna_liczba_rund = 100
# runda = 1
# while runda <= maksymalna_liczba_rund:

#     if statystyki["zabite_klasa5"] >= 3:
#         loguj("Koniec gry - biały zrealizował cel")
#         break

#     if statystyki["zabite_pionki"] >= 50:
#         loguj("Koniec gry - Czarny zrealizował cel")
#         break

#     loguj("================")
#     loguj(f"RUNDA {runda}")

#     #odnowa wymuszona
#     if len(białe_gotowe) < LICZBA_SLOTOW_ARENY:
#         odnowa(białe_gotowe,białe_odpoczywajace,statystyki,"biały",runda,STARTOWY_KOSZT_ODNOWY+1)  #kara za wymuszoną odnowe
#     if len(czarne_gotowe) < LICZBA_SLOTOW_ARENY:
#         odnowa(czarne_gotowe,czarne_odpoczywajace,statystyki,"czarny",runda,STARTOWY_KOSZT_ODNOWY+1)  


#     # pobranie ręki
#     białe_na_arenie = białe_gotowe.pobierz_reke(4)
#     czarne_na_arenie = czarne_gotowe.pobierz_reke(4)
    
#     ### WALKA ###
#     ustaw_puste_sloty(białe_na_arenie,czarne_na_arenie)  #przestaw kolejność jeżeli są walkowerowy - najslabsza karta 
#     wynik,białe_zywe,czarne_zywe, białe_aktywne, czarne_aktywne, białe_zabite_runda, czarne_zabite_runda = walka_arena(białe_na_arenie,czarne_na_arenie, statystyki)
#     statystyki['punkty_arena_biały'] = policz_punkty_rundy(wynik)
#     statystyki["zwyciezca"] = ustal_zwyciezce_rundy(statystyki['punkty_arena_biały'],białe_aktywne,czarne_aktywne)
#     loguj_stan_areny(białe_na_arenie,czarne_na_arenie,białe_aktywne,czarne_aktywne)
#     loguj(f"Wynik: {''.join(wynik)} | Punkty Areny białych: {statystyki['punkty_arena_biały']} | Zwycięzca Rundy: {statystyki['zwyciezca']}")

#     białe_aktywne.karty.sort(key=lambda karta: karta.klasa, reverse=True) #zaczynamy od najwyższej klasy
#     czarne_aktywne.karty.sort(key=lambda karta: karta.klasa, reverse=True)

#     kolejnosc_graczy = ["biały", "czarny"]

#     if statystyki["zwyciezca"] == "czarny":
#         kolejnosc_graczy.reverse()

#     ### WYDARZENIA ###


#     ### AKCJE ###
#     for gracz in kolejnosc_graczy:
#         if gracz == "biały":
#             if len(białe_gotowe) < LICZBA_SLOTOW_ARENY:
#                 odnowa(białe_gotowe,białe_odpoczywajace,statystyki,"biały",runda,statystyki["koszt_odnowy_biały"])
#             wykonaj_akcje_kart(białe_aktywne,statystyki,"biały")
#             wykonaj_akcje_pionkow(statystyki,"biały")
#         else:
#             rozlicz_choroby(statystyki) # z poprzedniej rundy
#             if len(czarne_gotowe) < LICZBA_SLOTOW_ARENY:
#                 odnowa(czarne_gotowe,czarne_odpoczywajace,statystyki,"czarny",runda,statystyki["koszt_odnowy_czarny"])
#             wykonaj_akcje_kart(czarne_aktywne,statystyki,"czarny")
#             wykonaj_akcje_pionkow(statystyki,"czarny")

#     ### SPRZATANIE PO WALKACH ###

#     # żywe karty wracają do odpoczynku
#     białe_odpoczywajace.przenies(białe_zywe)
#     czarne_odpoczywajace.przenies(czarne_zywe)

#     # martwe karty idą do stosu śmierci
#     białe_stos_smierci.przenies(białe_zabite_runda)
#     czarne_stos_smierci.przenies(czarne_zabite_runda)

#     loguj(
#         "Podsumowanie Rundy - Białe: ",
#         'Got ', len(białe_gotowe),
#         'Odp ', len(białe_odpoczywajace),
#         'Martwe: ', len(białe_stos_smierci),
#         'Zabite karty Spec: ', statystyki["zabite_klasa5"]
#         )

#     loguj(
#         "Podsumowanie Rundy - Czarne: ",
#         'Got ', len(czarne_gotowe),
#         'Odp ', len(czarne_odpoczywajace),
#         'Martwe: ',len(czarne_stos_smierci),
#         'Zabite pionki ', statystyki["zabite_pionki"]
#         )

#     loguj(
#         "Stan chorych: ",
#         'Poprzednia: ', statystyki["chorzy_poprzednia"],
#         'Aktualna: ', statystyki["chorzy_biezaca"]
#         )

#     runda += 1
#     statystyki["runda"] += 1

#     #reset statystyk rundowych
#     statystyki["akcje_biały"] = AKCJE_STARTOWE
#     statystyki["akcje_czarny"] = AKCJE_STARTOWE
#     statystyki["rzut_akcji_czarny"] = int(1 / PRAWDOPODOBIENSTWO_ZARAZY)
#     statystyki["rzut_akcji_biały"] = int(1 / PRAWDOPODOBIENSTWO_LECZENIA)
#     statystyki["koszt_odnowy_biały"]=STARTOWY_KOSZT_ODNOWY
#     statystyki["koszt_odnowy_czarny"]=STARTOWY_KOSZT_ODNOWY

### KONIEC GRY ###
#Logowanie_koncowe(statystyki,białe_gotowe,czarne_gotowe,białe_odpoczywajace,czarne_odpoczywajace)
zapisz_wyniki_csv(statystyki, białe_gotowe, czarne_gotowe, SCIEZKA_KART)

pokaz_wyniki_csv(SCIEZKA_KART, BIALE_WYBRANE, CZARNE_WYBRANE)