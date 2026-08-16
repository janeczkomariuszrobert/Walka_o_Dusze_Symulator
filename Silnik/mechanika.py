import pandas as pd
import random
import os
from Silnik.obiekty import Talia


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

    if wartosc.endswith("W"):
        return int(wartosc[:-1]), "W"

    if wartosc.endswith("p"):
        return int(wartosc[:-1]), True

    if wartosc == "+K4":
        return rzut_k(4), False

    if wartosc == "+K2":
        return rzut_k(2), False

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


def dodaj_bonus_wspolpracy(stan_areny, kolor, sila, limit):
    bonus = {
        "sila": sila,
        "pozostalo": limit
    }
    if kolor == "bialy":
        stan_areny.bonusy_bialy.append(bonus)
    else:
        stan_areny.bonusy_czarny.append(bonus)


def pobierz_bonusy_wspolpracy(stan_areny, kolor):
    if kolor == "bialy":
        bonusy = stan_areny.bonusy_bialy
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
    wynik=None,
    byla_smierc_wroga=False
):
    if not warunek:
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
    
    if warunek == "klasa_wrog=":
        return przeciwnik.klasa == karta.klasa
    if warunek == "klasa_wrog>":
        return przeciwnik.klasa > karta.klasa
    
    return False


def oblicz_zdolnosc_wlasna(karta, przeciwnik, sojusznicy):
    if not karta.walka_sila_ty:
        return 0, None

    wynik_warunku = sprawdz_warunek(
        karta.warunek_wlasny,
        karta,
        przeciwnik,
        sojusznicy
    )

    if not wynik_warunku:
        return 0, None

    sila, specjalna = interpretuj_parametr(karta.walka_sila_ty)

    if isinstance(wynik_warunku, bool):
        mnoznik = 1
    else:
        mnoznik = wynik_warunku

    return sila * mnoznik, specjalna 