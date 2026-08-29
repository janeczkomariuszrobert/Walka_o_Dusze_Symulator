import pandas as pd
import random
import os
from Silnik.obiekty import *

LOGOWANIE = 1
LICZBA_SLOTOW_ARENY = 4

PUNKTY = {
    "U": 0,
    "P": 1,
    "R": 2,
    "W": 3,
    "Z": 4
}

nazwa_logu = None

def ustaw_log(nowy_log):  #przeniesienie zmiennej globalnej z pliku START.py
    global nazwa_logu
    nazwa_logu = nowy_log


def excel_na_json(plik_excel,plik_json):
    if os.path.exists(plik_json):
        czas_excel = os.path.getmtime(plik_excel)
        czas_json = os.path.getmtime(plik_json)
        if czas_json >= czas_excel:
            return
    print(f"Aktualizuje: {plik_json}")    
    dane = pd.read_excel(plik_excel)
    dane.to_json(plik_json,orient="records",force_ascii=False,indent=4)
    print(f"Zaktualizowano: {plik_json}")

def loguj(*teksty):  #przyjmuje dowolną liczbe argumentów
    tekst = " ".join(str(x) for x in teksty)
    if LOGOWANIE:
        print(tekst)

    with open(nazwa_logu,"a",encoding="utf-8") as plik:
        plik.write(tekst + "\n")

def uzupelnij_gotowe(gotowe, odpoczywajace, kolor,runda):
    if len(odpoczywajace.karty) == 0:
        return
    loguj(f"Runda {runda}: uzupełnienie stosu GOTOWYCH ({kolor})")
    gotowe.przenies(odpoczywajace)
    gotowe.potasuj()


def rzut_k(wartosc):
    return random.randint(1, wartosc)

def interpretuj_parametr(wartosc):
    if wartosc is None:
        return 0, False

    if isinstance(wartosc, float) and wartosc.is_integer():
        wartosc = int(wartosc)

    if isinstance(wartosc, int):
        return wartosc, False

    wartosc = str(wartosc)

    if wartosc.endswith("p"):
        return int(wartosc[:-1]), True

    if wartosc == "+K4":
        return rzut_k(4), False

    if wartosc == "+K2":
        return rzut_k(2), False

    if wartosc == "-K4":
        return -1*rzut_k(4), False

    if wartosc == "-K2":
        return -1*rzut_k(2), False

    if "-" in wartosc[1:]:
        poczatek, koniec = map(int, wartosc.split("-"))
        return random.randint(poczatek, koniec), False

    if "," in wartosc:
        wartosci = [int(x) for x in wartosc.split(",")]
        return wartosci, False

    return int(wartosc), False


def wybierz_karte_na_walkower(karty, liczba_pustych, gracz):
    wybrane = []
    if gracz == "czarny":
        # Najpierw wybieramy karty klasy 5
        klasy5 = [
            karta for karta in karty.karty
            if karta.klasa == 5
        ]
        wybrane = klasy5[:liczba_pustych]
        # Jeżeli brakuje kart klasy 5, dobieramy najsłabsze z pozostałych
        if len(wybrane) < liczba_pustych:
            pozostale = [
                karta for karta in karty.karty
                if karta not in wybrane
            ]

            pozostale.sort(
                key=lambda karta: interpretuj_parametr(karta.sila)[0]
            )

            brakujace = liczba_pustych - len(wybrane)
            wybrane += pozostale[:brakujace]
    else:
        # Biały zawsze wybiera najsłabsze karty
        wybrane = sorted(
            karty.karty,
            key=lambda karta: interpretuj_parametr(karta.sila)[0]
        )[:liczba_pustych]
    # for karta in wybrane:
    #     loguj(
    #         f"WALKOWER {gracz}: {karta.id} {karta.imie} "
    #         f"(klasa {karta.klasa}, siła {karta.sila})"
    #     )
    return wybrane

def ustaw_puste_sloty(biale_na_arenie, czarne_na_arenie):
    if len(biale_na_arenie.karty) > len(czarne_na_arenie.karty):
        liczba_pustych = len(biale_na_arenie.karty) - len(czarne_na_arenie.karty)
        wybrane = wybierz_karte_na_walkower(
            biale_na_arenie,
            liczba_pustych,
            "bialy"
        )
        pozostale = [
            karta for karta in biale_na_arenie.karty
            if karta not in wybrane
        ]
        biale_na_arenie.karty = pozostale + wybrane
    elif len(czarne_na_arenie.karty) > len(biale_na_arenie.karty):
        liczba_pustych = len(czarne_na_arenie.karty) - len(biale_na_arenie.karty)
        wybrane = wybierz_karte_na_walkower(
            czarne_na_arenie,
            liczba_pustych,
            "czarny"
        )
        pozostale = [
            karta for karta in czarne_na_arenie.karty
            if karta not in wybrane
        ]
        czarne_na_arenie.karty = pozostale + wybrane

def policz_punkty_rundy(wyniki):
    return sum(PUNKTY[w] for w in wyniki)


def czy_stac_na_akcje(statystyki, gracz, koszt):
    return statystyki[f"akcje_{gracz}"] >= koszt

def czy_darmowa_odnowa(gotowe, odpoczywajace, limit=4):
    liczba_kart = (
        len(gotowe.karty)
        +
        len(odpoczywajace.karty)
    )
    return liczba_kart < limit

def odnowa(gotowe,odpoczywajace,statystyki,gracz,runda,koszt_odnowy):
    koszt = 0
    if not czy_darmowa_odnowa(gotowe, odpoczywajace):
        koszt = koszt_odnowy
    statystyki[f"akcje_{gracz}"] -= koszt
    uzupelnij_gotowe(gotowe,odpoczywajace,runda,gracz)


def wykonaj_akcje_pionkow(statystyki,gracz):
    akcje = statystyki[f"akcje_{gracz}"]
    if akcje == 0:
        return
    akcje -= 1  # RUCH
    if gracz == "czarny" and akcje > 0:
        statystyki["zabite_pionki"] += 1 # MORD
        # print('DEBUG Akcje pionków: Zabijam 1')
        akcje -= 1
    while akcje > 0:  # EWANGELIZACJA / KUSZENIE
        if rzut_k(4) == 4:  # 25% szansy na sukces
            if gracz == "bialy":
                ulecz_chorych(statystyki,1)
            else:
                statystyki["chorzy_biezaca"] += 1
        akcje -= 1
    statystyki[f"akcje_{gracz}"] = akcje


def wykonaj_akcje_kart(karty,statystyki,gracz):

    for karta in karty.karty:
        karta.wykonana = False  #reset wykonania
        if karta.id == 4 and karta.kolor == "czarny":   #zły duch Trucizna Kłamstw
            statystyki["kosci_zarazy_czarny"] = 2
        if karta.id == 10 and karta.kolor == "czarny":  #władza samobójstwo
            karty.karty.sort(key=lambda karta: karta.id == 10)  #ustaw na koniec

    for karta in karty.karty:
        if not karta.wykonana and karta.zabija == 0 and karta.zaraza == 0:
            wykonaj_akcje_karty(karta,karty,statystyki,gracz)
            karta.wykonana = True

    for karta in karty.karty:
        if not karta.wykonana and karta.zabija != 0 and karta.zaraza == 0:
            wykonaj_akcje_karty(karta,karty,statystyki,gracz)
            karta.wykonana = True

    for karta in karty.karty:
        if not karta.wykonana and karta.zaraza != 0:
            wykonaj_akcje_karty(karta,karty,statystyki,gracz)
            karta.wykonana = True


def wykonaj_akcje_karty(karta,karty,statystyki,gracz):
    if karta.id == 10 and karta.kolor == "czarny":
        wykonaj_akcje_albo(karta,karty,statystyki,gracz)
        return
    koszt, _ = interpretuj_parametr(karta.koszt)
    limit, _ = interpretuj_parametr(karta.limit)
    # print('DEBUG wykonaj_akcje_karty: ',koszt, limit, karta.imie)

    wykonania = 0
    while (limit is None or wykonania < limit) and czy_stac_na_akcje(statystyki,gracz,koszt):
        statystyki[f"akcje_{gracz}"] -= koszt
        wykonaj_efekt_karty(karta,statystyki)
        wykonania += 1

def wykonaj_efekt_karty(karta,statystyki):
    if karta.id == 14 and karta.kolor == "biały": #życie
        statystyki["chorzy_poprzednia"] = 0
        statystyki["chorzy_biezaca"] = 0
        return

    zabija, _ = interpretuj_parametr(karta.zabija)
    zaraza, czy_test_zaraza = interpretuj_parametr(karta.zaraza)

    #na razie brak jest przypadku, aby zabicie miało szanse mniejsza niz 100%
    if zabija != 0:
        # print('DEBUG wykonaj_efekt_karty: Zabijam ',zabija, karta.imie)
        statystyki["zabite_pionki"] += zabija
    if zaraza > 0:
        if czy_test_zaraza:  #test na zarazę
            if wykonaj_test(statystyki, "czarny"):  #prwdopodobienstwo 25% na zarazenie
                statystyki["chorzy_biezaca"] += zaraza
        else:
            statystyki["chorzy_biezaca"] += zaraza
    if zaraza < 0:
        if czy_test_zaraza:
            if wykonaj_test(statystyki, "bialy"):  #test na leczenie:
                ulecz_chorych(statystyki, -zaraza)
        else:
            ulecz_chorych(statystyki, -zaraza)


def wykonaj_akcje_albo(karta,karty,statystyki,gracz):
    koszty = karta.koszt.split(",")
    efekty = karta.zabija.split(",")

    koszt = int(koszty[0])
    efekt = int(efekty[0])
    limit = oblicz_limit_akcji(karta,karty,gracz,0) #limit akcji płatnej

    wykonane = 0

    while wykonane < limit and czy_stac_na_akcje(statystyki,gracz,koszt):
        statystyki[f"akcje_{gracz}"] -= koszt
        statystyki["zabite_pionki"] += efekt
        wykonane += 1

    if wykonane == 0:
        koszt = int(koszty[1])
        efekt = int(efekty[1])
        limit = oblicz_limit_akcji(karta,karty,gracz,1)  #limit akcji bezplatnej (drugiej w zestawie ALBO)

        while wykonane < limit and czy_stac_na_akcje(statystyki,gracz,koszt):
            statystyki[f"akcje_{gracz}"] -= koszt
            statystyki["zabite_pionki"] += efekt
            wykonane += 1

def ustal_zwyciezce_rundy(punkty,biale_aktywne,czarne_aktywne):
    if punkty > 8:
        return "biały"
    if punkty < 8:
        return "czarny"

    # remis punktowy areny
    suma_bialych = sum(karta.klasa for karta in biale_aktywne.karty)
    suma_czarnych = sum(karta.klasa for karta in czarne_aktywne.karty)

    if suma_bialych > suma_czarnych:
        return "biały"
    if suma_czarnych > suma_bialych:
        return "czarny"

    # absolutny remis
    loguj("Zwycięzca rundy ustalony kością")
    if rzut_k(2) == 1:
        return "biały"
    else:
        return "czarny"


def rozlicz_choroby(statystyki):
    statystyki["zabite_pionki"] += statystyki["chorzy_poprzednia"]
    # print('DEBUG choroba zabija: ',statystyki["chorzy_poprzednia"])
    statystyki["chorzy_poprzednia"]= statystyki["chorzy_biezaca"]
    statystyki["chorzy_biezaca"] = 0

def ulecz_chorych(statystyki, liczba):
    leczenie = liczba
    if statystyki["chorzy_poprzednia"] >= leczenie:
        statystyki["chorzy_poprzednia"] -= leczenie
    else:
        pozostalo = leczenie - statystyki["chorzy_poprzednia"]
        statystyki["chorzy_poprzednia"] = 0
        statystyki["chorzy_biezaca"] = max(0, statystyki["chorzy_biezaca"] - pozostalo)

def wykonaj_test(statystyki,gracz):
    kosci = int(statystyki[f"rzut_akcji_{gracz}"])
    return rzut_k(kosci) == kosci


def oblicz_limit_akcji(karta,aktywne,gracz,opcja=0):
    limit, _ = interpretuj_parametr(karta.limit)
    koszt, _ = interpretuj_parametr(karta.koszt)

    if isinstance(limit,list):
        limit = limit[opcja]
    if isinstance(koszt,list):
        koszt = koszt[opcja]

    if gracz == "czarny" and koszt > 0:
        for aktywna in aktywne.karty:
            if aktywna.id == 13 and aktywna.kolor == "czarny":
                limit = None
                break

    return limit

def loguj_stan_areny(biale_na_arenie,czarne_na_arenie,biale_aktywne,czarne_aktywne):
    loguj("Stan areny:")

    for i in range(4):
        if i < len(biale_na_arenie.karty):
            karta = biale_na_arenie.karty[i]
            flaga = "(F)" if karta.flaga=='tak' else ""
            biala = f"{karta.imie}{flaga} {karta.sila} "
            if biale_aktywne is not None and karta in biale_aktywne.karty:
                biala = f"{biala} WIN"
        else:
            biala = "---"

        if i < len(czarne_na_arenie.karty):
            karta = czarne_na_arenie.karty[i]
            flaga = "(F)" if karta.flaga=='tak' else ""
            czarna = f"{karta.imie}{flaga} {karta.sila} "
            if czarne_aktywne is not None and karta in czarne_aktywne.karty:
                            czarna = f"{czarna} WIN"
        else:
            czarna = "---"

        loguj(f"Walka {i + 1}: {biala:<20} vs   {czarna}")


#pobiera wszystkie aktualnie aktywne bonusy współpracy dla danego koloru, sumuje ich siłę i jednocześnie zmniejsza ich pozostały czas działania.
def pobierz_bonusy_wspolpracy(stan_areny, kolor):
    if kolor == "bialy":
        bonusy = stan_areny.bonusy_bialy  #to jest lista
    else:
        bonusy = stan_areny.bonusy_czarny

    suma = sum(bonus["sila"] for bonus in bonusy)
    pozostale = []
    for bonus in bonusy:
        if bonus["pozostalo"] is None:
            pozostale.append(bonus)
        else:
            bonus["pozostalo"] -= 1

            if bonus["pozostalo"] > 0:
                pozostale.append(bonus)
    if kolor == "bialy":
        stan_areny.bonusy_bialy = pozostale
    else:
        stan_areny.bonusy_czarny = pozostale
    return suma


def sprawdz_warunek(
    warunek,
    karta,
    przeciwnik,
    sojusznicy,
    wynik,
    byla_smierc_wroga
):
    if not warunek: #musi byc podany warunek
        return True
    
    if warunek == "win":
        if karta.kolor == "biały":
            return wynik in ("W", "Z")
        else:
            return wynik in ("P", "U")
        
    if warunek == "winZ":
        if karta.kolor == "biały":
            return wynik == "Z"
        else:
            return wynik == "U"
        
    if warunek == "zab_ta":
        return byla_smierc_wroga
    
    if warunek == "klasa_soj=":
        return sum(
            sojusznik.klasa == karta.klasa
            for sojusznik in sojusznicy
        )
    
    if warunek == "klasa_soj<=":
        return sum(
            sojusznik.klasa <= karta.klasa
            for sojusznik in sojusznicy
        )
    
    if warunek == "klasa_soj>":
        return sum(
            sojusznik.klasa > karta.klasa
            for sojusznik in sojusznicy
        )
    
    if warunek == "klasa_wroga=":
        return przeciwnik.klasa == karta.klasa
    if warunek == "klasa_wroga>":
        return przeciwnik.klasa > karta.klasa
    if warunek == "klasa_wroga<":
        return przeciwnik.klasa < karta.klasa

    loguj('DEBUG: Nie znalazlem warunku zdolnosci wlasnej')
    return False


def pobierz_zdolnosc_wlasna(statystyki, karta, przeciwnik, sojusznicy):
    wynik_warunku = sprawdz_warunek(
        karta.warunek_wlasny,
        karta,
        przeciwnik,
        sojusznicy,
        None,
        None
    )

    if not wynik_warunku:
        return 0, False

    zarejestruj_uzycie_zdolnosci(statystyki, karta.id, karta.kolor, 1)

    bonus, _ = interpretuj_parametr(karta.walka_sila_bonus)
    zdolnosc = karta.walka_zdolnosc

    if isinstance(wynik_warunku, int) and not isinstance(wynik_warunku, bool):
        bonus *= wynik_warunku

    return bonus, zdolnosc


def wykonaj_zdolnosc_po_walce(wynik, karta, stan_areny, statystyki):

    if not sprawdz_warunek(karta.warunek_wspolpracy, karta, None, None, wynik, None):
        return

    zarejestruj_uzycie_zdolnosci(statystyki, karta.id, karta.kolor, 1)
    sila, specjalna = interpretuj_parametr(karta.wspolpraca_sila)

    if karta.typ_wspolpracy in ("1", "3"):
        bonus = {"sila": sila, "pozostalo": int(karta.typ_wspolpracy)}
        if karta.kolor == "biały":
            stan_areny.bonusy_bialy.append(bonus)
        else:
            stan_areny.bonusy_czarny.append(bonus)
    elif karta.typ_wspolpracy == "R":
        if karta.kolor == "biały":
            stan_areny.remis_wygrywa_bialy = True
        else:
            stan_areny.remis_wygrywa_czarny = True

def policz_bonus_flag( karty_aktyw ):  #karty_aktyw jest listą kart aktywnych na arenie
    bonus = 0
    for karta in karty_aktyw:
        if karta.czy_flaga == "tak":
            bonus += interpretuj_parametr(karta.flaga_sila)[0]
    return bonus


def wykonaj_zdolnosc_przed_walka(statystyki,karta, przeciwnik, sojusznicy):  #tylko te które dają wpływ dla mnie (od JA)
    if karta.typ_wspolpracy != "J":
        return 0

    wynik_warunku = sprawdz_warunek(
        karta.warunek_wspolpraca,
        karta,
        przeciwnik,
        sojusznicy,
        None,
        None
    )

    if wynik_warunku:
        zarejestruj_uzycie_zdolnosci(statystyki, karta.id, karta.kolor, 1)
        sila, _ = interpretuj_parametr(karta.wspolpraca_sila)
        return sila

    return 0



def znajdz_kandydata_atak(
    przeciwnik,
    sojusznicy_sr,
    sojusznicy_przeciwnika,
    bonus_sr,
    bonus_przeciwnika
):
    klasa_przeciwnika = przeciwnik.klasa

    if klasa_przeciwnika == 5:
        for i in range(len(sojusznicy_sr)):
            kandydat = sojusznicy_sr[i]
            przeciwnik_kandydata = sojusznicy_przeciwnika[i]

            sila_kandydata = policz_sile_walki(kandydat,bonus_sr,False)
            sila_przeciwnika_kandydata = policz_sile_walki(przeciwnik_kandydata,bonus_przeciwnika,False)

            if sila_kandydata - sila_przeciwnika_kandydata >= 2:
                return kandydat

    elif klasa_przeciwnika == 4:
        for i in range(len(sojusznicy_sr)):
            kandydat = sojusznicy_sr[i]
            przeciwnik_kandydata = sojusznicy_przeciwnika[i]

            sila_kandydata = policz_sile_walki(kandydat, bonus_sr, False)
            sila_przeciwnika_kandydata = policz_sile_walki(przeciwnik_kandydata, bonus_przeciwnika, False)

            if sila_kandydata - sila_przeciwnika_kandydata < 2 or przeciwnik_kandydata.klasa in (4,5):
                continue
            return kandydat

    elif klasa_przeciwnika == 3:
        for i in range(len(sojusznicy_sr)):
            kandydat = sojusznicy_sr[i]
            przeciwnik_kandydata = sojusznicy_przeciwnika[i]

            sila_kandydata = policz_sile_walki(kandydat, bonus_sr, False)
            sila_przeciwnika_kandydata = policz_sile_walki(przeciwnik_kandydata, bonus_przeciwnika, False)

            if sila_kandydata - sila_przeciwnika_kandydata < 2 or przeciwnik_kandydata.klasa in (3,4,5):
                continue
            return kandydat

    return False    

def znajdz_kandydata_ratunek(
    sojusznicy_sr,
    sojusznicy_przeciwnika,
    bonus_sr,
    bonus_przeciwnika
):
    najlepszy_kandydat = None
    najlepsza_klasa = 0

    for i in range(len(sojusznicy_sr)):
        kandydat = sojusznicy_sr[i]
        przeciwnik_kandydata = sojusznicy_przeciwnika[i]

        if przeciwnik_kandydata.klasa < 3:
            continue

        sila_kandydata = policz_sile_walki(
            kandydat,
            bonus_sr,
            False
        )

        sila_przeciwnika_kandydata = policz_sile_walki(
            przeciwnik_kandydata,
            bonus_przeciwnika,
            False
        )

        if sila_kandydata - sila_przeciwnika_kandydata >= 2:
            continue

        if przeciwnik_kandydata.klasa > najlepsza_klasa:
            najlepszy_kandydat = kandydat
            najlepsza_klasa = przeciwnik_kandydata.klasa

    return najlepszy_kandydat


def Znajdz_Kandydata_do_zamiany(
    karta_sr,
    przeciwnik,
    sojusznicy_sr,
    sojusznicy_przeciwnika,
    bonus_sr,
    bonus_przeciwnika   
):        
    kandydat_atak = znajdz_kandydata_atak(
        przeciwnik,
        sojusznicy_sr,  #tu musi wejść lista, a nie krotka
        sojusznicy_przeciwnika,
        bonus_sr,
        bonus_przeciwnika
    )

    kandydat_ratunek = znajdz_kandydata_ratunek(
        sojusznicy_sr,
        sojusznicy_przeciwnika,
        bonus_sr,
        bonus_przeciwnika
    )

    # 1. Ten sam kandydat realizuje oba cele
    if kandydat_atak is not None and kandydat_atak is kandydat_ratunek:
        return kandydat_atak, "ATAK"

    # 2. Jest tylko kandydat do ataku
    if kandydat_atak is not None and kandydat_ratunek is None:
        return kandydat_atak, "ATAK"

    # 3. Jest tylko kandydat do ratunku
    if kandydat_atak is None and kandydat_ratunek is not None:
        return kandydat_ratunek, "RATUNEK"

    # 4. Są obaj - porównujemy ich ważność
    if kandydat_atak is not None and kandydat_ratunek is not None:

        # znajdujemy przeciwnika kandydata_atak
        for i in range(len(sojusznicy_sr)):
            if sojusznicy_sr[i] is kandydat_atak:
                przeciwnik_kandydata_atak = sojusznicy_przeciwnika[i]
                break

        if karta_sr.kolor == "biały":
            # Dla białego zabicie klasy 5 ma bezwzględne pierwszeństwo
            if przeciwnik_kandydata_atak.klasa == 5:
                return kandydat_atak, "ATAK"
        else:
            # Dla czarnego uratowanie klasy 5 ma bezwzględne pierwszeństwo
            if kandydat_ratunek.klasa == 5:
                return kandydat_ratunek, "RATUNEK"

        # W pozostałych przypadkach porównujemy klasy
        if przeciwnik.klasa >= kandydat_ratunek.klasa:
            return kandydat_atak, "ATAK"
        else:
            return kandydat_ratunek, "RATUNEK"

    return None


def znajdz_s(talia,arg):
    for karta in talia.karty:
        if karta.typ_wspolpracy == arg:
            return karta

    return None

def wykonaj_zdolnosci_SR(statystyki,biale_karty,czarne_karty,pozycja_karty_sr):

    if pozycja_karty_sr == 0:  #wywolanie przed walką czyli zwykly SR
        # Szukamy kart SR
        sr_bialy = znajdz_s(biale_karty,"SR")
        sr_czarny = znajdz_s(czarne_karty,"SR")

        # Jeżeli nie ma żadnego SR, nic nie robimy
        if sr_bialy is None and sr_czarny is None:
            return

        #Jezeli jest to obliczamy jego sojuszników bo w argumenci przyszło NONE
        if sr_bialy is not None:
            print("znalazlem bialego SR'a")
        elif sr_czarny is not None:
            print("znalazlem czarnego SR'a")

        sojusznicy_bialego = [
            karta for karta in biale_karty.karty
            if karta is not sr_bialy
        ]
        sojusznicy_czarnego = [
            karta for karta in czarne_karty.karty
            if karta is not sr_czarny
        ]

    else:
        # Szukamy kart SR+
        sr_bialy = znajdz_s(biale_karty,"SR+")
        sr_czarny = znajdz_s(czarne_karty,"SR+")

        # Jeżeli nie ma żadnego SR+, nic nie robimy
        if sr_bialy is None and sr_czarny is None:
            return

        #Jezeli jest to sojusznicy przyszli z argumentu
        if sr_bialy is not None:
            print("znalazlem bialego SR+'a")
        elif sr_czarny is not None:
            print("znalazlem czarnego SR+'a")

        limit_klasy_bialy, _ = interpretuj_parametr(sr_bialy.warunek_wspolpraca)
        limit_klasy_czarny, _ = interpretuj_parametr(sr_bialy.warunek_wspolpraca)
        
        #sojusznicy którzy jeszcze nie walczyli
        sojusznicy_bialego = [karta for j,karta in enumerate(biale_karty.karty,1) if karta is not sr_bialy and j > pozycja_karty_sr and karta.klasa <= limit_klasy_bialy]
        sojusznicy_czarnego = [karta for j,karta in enumerate(czarne_karty.karty,1) if karta is not sr_czarny and j > pozycja_karty_sr and karta.klasa <= limit_klasy_czarny]



    bonus_flagi_bialy = policz_bonus_flag(biale_karty.karty)
    bonus_flagi_czarny = policz_bonus_flag(czarne_karty.karty)

    # Ustalenie kolejności wykonywania SR
    if sr_bialy is not None and sr_czarny is not None:

        if rzut_k(2) == 1:
            kolejnosc = ("bialy", "czarny")
        else:
            kolejnosc = ("czarny", "bialy")

    elif sr_bialy is not None:
        kolejnosc = ("bialy",)

    else:
        kolejnosc = ("czarny",)

    # Wykonanie SR w ustalonej kolejności
    for kolor in kolejnosc:

        if kolor == "bialy":

            pozycja_sr = biale_karty.karty.index(sr_bialy)
            przeciwnik = czarne_karty.karty[pozycja_sr]

            kandydat,powod = Znajdz_Kandydata_do_zamiany(
                sr_bialy,
                przeciwnik,
                sojusznicy_bialego,
                sojusznicy_czarnego,
                bonus_flagi_bialy,
                bonus_flagi_czarny
            )

            if kandydat is not None:
                pozycja_kandydata = biale_karty.karty.index(kandydat)
                #ZAMIANA
                biale_karty.karty[pozycja_sr], biale_karty.karty[pozycja_kandydata] = (
                    biale_karty.karty[pozycja_kandydata],
                    biale_karty.karty[pozycja_sr]
                )
                zarejestruj_uzycie_zdolnosci(statystyki, sr_bialy.id, sr_bialy.kolor)
                loguj("DEBUG SR: ZMIANA",powod," pozycja ", pozycja_sr + 1,"->", pozycja_kandydata + 1)

        else:

            pozycja_sr = czarne_karty.karty.index(sr_czarny)
            przeciwnik = biale_karty.karty[pozycja_sr]

            kandydat,powod = Znajdz_Kandydata_do_zamiany(
                sr_czarny,
                przeciwnik,
                sojusznicy_czarnego,
                sojusznicy_bialego,
                bonus_flagi_czarny,
                bonus_flagi_bialy
            )

            if kandydat is not None:
                pozycja_kandydata = czarne_karty.karty.index(kandydat)
                czarne_karty.karty[pozycja_sr], czarne_karty.karty[pozycja_kandydata] = (
                    czarne_karty.karty[pozycja_kandydata],
                    czarne_karty.karty[pozycja_sr]
                )
                zarejestruj_uzycie_zdolnosci(statystyki, sr_czarny.id, sr_czarny.kolor)
                loguj("DEBUG SR: ZMIANA",powod," pozycja ", pozycja_sr + 1,"->", pozycja_kandydata + 1)

def wykonaj_zdolnosc_SP(
    statystyki,
    biale_karty,
    czarne_karty,
    biale_zabite,
    czarne_zabite,
    biale_zywe,
    czarne_zywe,
    biale_aktywne,
    czarne_aktywne
):

    sp_bialy = znajdz_s(biale_karty,"SP")
    sp_czarny = znajdz_s(czarne_karty,"SP")

    if sp_bialy is None and sp_czarny is None: # Jeżeli nie ma żadnego SP, nic nie robimy
        return 0,0

    decyzja_bialy, decyzja_czarny,wrog_bialego_ginie,wrog_czarnego_ginie,korzysc_biala,korzysc_czarna = Czy_wykonac_zdolnosc_SP(sp_bialy,sp_czarny,biale_karty,czarne_karty)

    if decyzja_bialy:
        zarejestruj_uzycie_zdolnosci(statystyki, sp_bialy.id, sp_bialy.kolor)
        if wrog_bialego_ginie:
            pozycja_sp = biale_karty.karty.index(sp_bialy)
            przeciwnik_sp = czarne_karty.karty[pozycja_sp]
            czarne_zabite.karty.append(przeciwnik_sp)
            czarne_karty.karty.remove(przeciwnik_sp)
            loguj("DEBUG SP: MIŁOŚĆ się poświęca. Przeciwnik ginie. Kożyść=",korzysc_biala)
        else:
            czarne_zywe.dodaj(przeciwnik_sp)   #czarne dostają walkowera
            czarne_aktywne.dodaj(przeciwnik_sp)
            loguj("DEBUG SP: MIŁOŚĆ się poświęca. Przeciwnik przezył. Kożyść=",korzysc_biala)

        bonus_bialy, _ = interpretuj_parametr(sp_bialy.wspolpraca_sila)
        biale_zabite.karty.append(sp_bialy)
        biale_karty.karty.remove(sp_bialy)
    else:     
        loguj("DEBUG SP: MIŁOŚĆ rezygnuje z poświęcenia. Kożyść=",korzysc_biala)
        bonus_bialy=0
        
    if decyzja_czarny:
        zarejestruj_uzycie_zdolnosci(statystyki, sp_czarny.id, sp_czarny.kolor)
        if wrog_czarnego_ginie:
            pozycja_sp = czarne_karty.karty.index(sp_czarny)
            przeciwnik_sp = biale_karty.karty[pozycja_sp]
            biale_zabite.karty.append(przeciwnik_sp)
            biale_karty.karty.remove(przeciwnik_sp)
            loguj("DEBUG SP: WŁADZA8 się poświęca. Przeciwnik ginie. Kożyść=",korzysc_czarna)
        else:
            biale_zywe.dodaj(przeciwnik_sp)   #biale dostają walkowera
            biale_aktywne.dodaj(przeciwnik_sp)
            loguj("DEBUG SP: WŁADZA8 się poświęca. Przeciwnik przezył. Kożyść=",korzysc_czarna)
        bonus_czarny, _ = interpretuj_parametr(sp_czarny.wspolpraca_sila)
        czarne_zabite.karty.append(sp_czarny)
        czarne_karty.karty.remove(sp_czarny)
    else:     
        loguj("DEBUG SP: WLADZA8 rezygnuje z poświęcenia. Kożyść=",korzysc_czarna)
        bonus_czarny=0

    return bonus_bialy,bonus_czarny

def Czy_wykonac_zdolnosc_SP(sp_bialy,sp_czarny,biale_karty, czarne_karty):

    decyzja_bialy=False
    decyzja_czarny=False
    wrog_bialego_ginie=False
    wrog_czarnego_ginie=False

    bonus_flagi_bialy = policz_bonus_flag(biale_karty.karty)
    bonus_flagi_czarny = policz_bonus_flag(czarne_karty.karty)

    # Sojusznicy nie zmienią się w wyniku zamiany
    sojusznicy_bialego = [
        karta for karta in biale_karty.karty
        if karta is not sp_bialy
    ]

    sojusznicy_czarnego = [
        karta for karta in czarne_karty.karty
        if karta is not sp_czarny
    ]

    kolejnosc_wynikow = {
            "U": 0,
            "P": 1,
            "R": 2,
            "W": 3,
            "Z": 4
        }

    # Ustalenie kolejności wykonywania SP
    if sp_bialy is not None and sp_czarny is not None:

        pozycja_bialy = biale_karty.karty.index(sp_bialy)
        pozycja_czarny = czarne_karty.karty.index(sp_czarny)

        if pozycja_bialy < pozycja_czarny:
            kolejnosc = ("bialy", "czarny")

        elif pozycja_czarny < pozycja_bialy:
            kolejnosc = ("czarny", "bialy")

        else:
            if rzut_k(2) == 1:
                kolejnosc = ("bialy", "czarny")
            else:
                kolejnosc = ("czarny", "bialy")

    elif sp_bialy is not None:
        kolejnosc = ("bialy",)

    else:
        kolejnosc = ("czarny",)

    # Wykonanie SP w ustalonej kolejności
    for kolor in kolejnosc:

        if kolor == "bialy":

            X, Y = interpretuj_parametr(sp_bialy.wspolpraca_sila)
            pozycja_sp = biale_karty.karty.index(sp_bialy)
            przeciwnik_sp = czarne_karty.karty[pozycja_sp]
            prog = sp_bialy.klasa + 2
            korzysc_biala = 0

            if przeciwnik_sp.klasa <= Y: # Bezpośredni przeciwnik
                korzysc_biala += 2
                wrog_bialego_ginie=True

            for i in range(len(sojusznicy_bialego)):  #  (zbior 1,2,3,4 bez pozycja_sp)  #petla po sojusznikach bialego

                sojusznik=sojusznicy_bialego[i]
                wrog=czarne_karty.karty[sojusznik.index]
                
                wynik_bez_X=oszacuj_wynik_walki_SP(sojusznik,wrog,bonus_flagi_bialy, bonus_flagi_czarny)
                wynik_z_X  =oszacuj_wynik_walki_SP(sojusznik,wrog,bonus_flagi_bialy, bonus_flagi_czarny-X)

                przesuniecie = kolejnosc_wynikow[wynik_z_X] - kolejnosc_wynikow[wynik_bez_X]
        
                if przesuniecie > 0:
                    korzysc_biala += przesuniecie

                if wrog.klasa == 5 and wynik_bez_X != "Z" and wynik_z_X == "Z":  #zabicie klasy 5
                    korzysc_biala += 4

            if korzysc_biala > prog:  #decyzja o poswieceniu
                decyzja_bialy=True

        else:

            # SP mogło zostać zabite przez wcześniejszą decyzję białego
            if sp_czarny not in czarne_karty.karty:
                continue

            X, Y = interpretuj_parametr(sp_czarny.wspolpraca_sila)
            pozycja_sp = czarne_karty.karty.index(sp_czarny)
            przeciwnik_sp = biale_karty.karty[pozycja_sp]
            prog = sp_czarny.klasa + 2
            korzysc_czarna = 0

            if przeciwnik_sp.klasa <= Y: # Bezpośredni przeciwnik
                korzysc_czarna += 2
                wrog_czarnego_ginie=True

            for i in range(len(sojusznicy_czarnego)):  #(zbior 1,2,3,4 bez pozycja_sp)  #petla po sojusznikach czarnego

                sojusznik=sojusznicy_czarnego[i]
                wrog=biale_karty.karty[sojusznik.index]

                wynik_bez_X=oszacuj_wynik_walki_SP(sojusznik,wrog,bonus_flagi_czarny, bonus_flagi_bialy)
                wynik_z_X  =oszacuj_wynik_walki_SP(sojusznik,wrog,bonus_flagi_czarny, bonus_flagi_bialy-X)

                przesuniecie = kolejnosc_wynikow[wynik_z_X] - kolejnosc_wynikow[wynik_bez_X]
        
                if przesuniecie > 0:
                    korzysc_czarna += przesuniecie

                if sojusznik.klasa == 5 and wynik_bez_X == "Z" and wynik_z_X != "Z":  #uratowanie klasy 5
                    korzkorzysc_czarnaysc += 4

            if korzysc_czarna >= prog:  #decyzja o poswieceniu
                decyzja_czarny=True

    return decyzja_bialy, decyzja_czarny, wrog_bialego_ginie, wrog_czarnego_ginie,korzysc_biala,korzysc_czarna

def oszacuj_wynik_walki_SP(
    karta_biala,
    karta_czarna,
    bonus_bialy,
    bonus_czarny
):
    sila_biala = policz_sile_walki(karta_biala,bonus_bialy,False)
    sila_czarna = policz_sile_walki(karta_czarna,bonus_czarny,False)
    roznica = sila_biala - sila_czarna

    if roznica >= 3:
        return "Z"
    elif roznica > 0:
        return "W"
    elif roznica == 0:
        return "R"
    elif roznica <= -3:
        return "U"
    else:
        return "P"

def Logowanie_koncowe(statystyki,biale_gotowe,czarne_gotowe,biale_odpoczywajace,czarne_odpoczywajace):
    loguj("\nKarty Specjalne:")
    loguj("ŚMIERĆ żyje:",statystyki["Smierc_zyje"])
    loguj("ŁASKA żyje:",statystyki["Laska_zyje"])

    loguj("\nBiałe karty które przeżyły:")
    for karta in biale_gotowe.karty + biale_odpoczywajace.karty:
        loguj(karta.id, karta.imie, karta.sila)

    loguj("\nCzarne karty które przeżyły:")
    for karta in czarne_gotowe.karty + czarne_odpoczywajace.karty:
        loguj(karta.id, karta.imie, karta.sila)

def policz_sile_walki(karta, bonus_areny, rzut_kostka=True):
    sila = interpretuj_parametr(karta.sila)[0]
    sila += interpretuj_parametr(karta.walka_sila_bonus)[0]
    sila += bonus_areny
    if rzut_kostka:
        sila += rzut_k(4)
    return sila

def zarejestruj_uzycie_zdolnosci(statystyki, id_karty, kolor, numer_zdolnosci=1):
    klucz = (id_karty, kolor)
    if numer_zdolnosci == 1:
        statystyki["zdolnosci"][klucz]["zdolnosc1"] += 1
    elif numer_zdolnosci == 2:
        statystyki["zdolnosci"][klucz]["zdolnosc2"] += 1

def zarejestruj_wynik_karty(statystyki, karta_biala, karta_czarna, wynik):
    klucz_bialy = (karta_biala.id, karta_biala.kolor)
    klucz_czarny = (karta_czarna.id, karta_czarna.kolor)
    statystyki["wyniki_kart"][klucz_bialy][wynik] += 1
    odwrotny_wynik = {
        "W": "P",
        "P": "W",
        "R": "R",
        "Z": "U",
        "U": "Z"
    }
    statystyki["wyniki_kart"][klucz_czarny][odwrotny_wynik[wynik]] += 1