from Silnik.obiekty import *
from Silnik.mechanika import *

def policz_bonus_flag( karty_aktyw ):  #karty_aktyw jest listą kart aktywnych na arenie
    bonus = 0
    for karta in karty_aktyw:
        if karta.czy_flaga == "tak":
            bonus += interpretuj_parametr(karta.flaga_sila)[0]
    return bonus

def policz_sile_walki(karta, bonus_areny):
    sila = interpretuj_parametr(karta.sila)[0]
    sila += interpretuj_parametr(karta.walka_sila_ty)[0]
    sila += bonus_areny
    sila += rzut_k(4)
    return sila

def walka_kart(
    karta_biala,
    karta_czarna,
    statystyki,
    remis_bialy,
    remis_czarny,
    bonus_bialy,
    bonus_czarny,
    specjalna_wlasna_biala,
    specjalna_wlasna_czarna
):
    sila_biala = policz_sile_walki(
        karta_biala,
        bonus_bialy
    )
    sila_czarna = policz_sile_walki(
        karta_czarna,
        bonus_czarny
    )

    #wynik identyfikujemy od storny białego

    #----Wyjątki----
    if karta_czarna.id == 14 and karta_czarna.kolor == "czarny":#ŚMIERĆ
        if karta_biala.id in (19, 14):  #Jezus lub Życie
            statystyki['Smierc_zyje']='NIE'
            return {
                "wynik": "Z",
                "biala_zyje": True,
                "czarna_zyje": False
            }
    #---------------

    prog_cz = 4 if karta_czarna.wspolpraca_sila in ("T", "RT") else 3  #domyslnie 3 chyba ze wspolpraca_sila=R
    prog_b = 4 if karta_biala.wspolpraca_sila in ("T", "RT") else 3

    if sila_biala == sila_czarna:
        if karta_biala.walka_sila_ty in ("R", "RT") or remis_bialy==True or (specjalna_wlasna_biala == "W" and specjalna_wlasna_czarna != "W"):  #biały wygrywa mimo remisu
            return {
                "wynik": "W",
                "biala_zyje": True,
                "czarna_zyje": True
            }
        if karta_czarna.walka_sila_ty in ("R", "RT") or remis_czarny==True or (specjalna_wlasna_czarna == "W" and specjalna_wlasna_biala != "W"): #czarny wygrywa mimo remisu
            return {
                "wynik": "P",
                "biala_zyje": True,
                "czarna_zyje": True
            }

        return {
            "wynik": "R",
            "biala_zyje": True,
            "czarna_zyje": True
        }

    
    if sila_biala > sila_czarna:
        roznica = sila_biala - sila_czarna
        if specjalna_wlasna_czarna == "W":
            return {
                "wynik": "P",
                "biala_zyje": True,
                "czarna_zyje": True
            }
        elif roznica >= prog_cz:          
            if karta_czarna.walka_sila_ty == "Z2":
                if rzut_k(2) == 2:
                    # czarna przeżyła
                    return {
                        "wynik": "W",
                        "biala_zyje": True,
                        "czarna_zyje": True 
                    }
            elif karta_czarna.walka_sila_ty == "Z4" and karta_biala.id != 19: #jezeli nie walczysz z Jezusem
                if rzut_k(4) == 4:
                    # czarna przeżyła
                    return {
                        "wynik": "W",
                        "biala_zyje": True,
                        "czarna_zyje": True 
                    }
            # czarna umiera:
            return {
                "wynik": "Z",
                "biala_zyje": True,
                "czarna_zyje": False
            }
        else:
            return {
                "wynik": "W",
                "biala_zyje": True,
                "czarna_zyje": True
            }
        
    else:
        roznica = sila_czarna - sila_biala

        if specjalna_wlasna_biala == "W":
            return {
                "wynik": "W",
                "biala_zyje": True,
                "czarna_zyje": True
            }  
        elif roznica >= prog_b:
            return {
                "wynik": "U",
                "biala_zyje": karta_biala.walka_sila_ty == "n", #jezeli jest 'n' to wynik bedize TRUE wiec bedzie zyc, w przeciwnym wypadku FALSE czyli umiera
                "czarna_zyje": True
            }
        else:
            return {
                "wynik": "P",
                "biala_zyje": True,
                "czarna_zyje": True
            }


def walka_arena(biale_karty, czarne_karty, statystyki):

    wyniki = []

    stan_areny = StanAreny()  #inicjuj parametrami startowymi w clasie

    #te talie będą sie kurczyc gdy ktora karta przegra lub zgineła
    biale_aktywne = Talia()
    czarne_aktywne = Talia()

    biale_aktywne.kopiuj(biale_karty)
    czarne_aktywne.kopiuj(czarne_karty)

    biale_zywe = Talia()
    czarne_zywe = Talia()

    biale_zabite = Talia()
    czarne_zabite = Talia()

    biale_sojusznicy = biale_karty.karty.copy()
    czarne_sojusznicy = czarne_karty.karty.copy()

    for i in range(LICZBA_SLOTOW_ARENY):

        karta_biala = biale_karty.karty[i]
        karta_czarna = czarne_karty.karty[i]

        bonus_wlasny_bialy = 0      
        bonus_wlasny_czarny = 0
        specjalna_wlasna_biala = None
        specjalna_wlasna_czarna = None

        if i < len(biale_karty.karty) and i < len(czarne_karty.karty):

            #aktualni sojusznicy (karta walcząca nie liczy sie)
            sojusznicy_bialego = [
                karta for karta in biale_sojusznicy
                if karta != karta_biala
            ]

            sojusznicy_czarnego = [
                karta for karta in czarne_sojusznicy
                if karta != karta_czarna
            ]

            bonus_wlasny_bialy, specjalna_wlasna_biala = oblicz_zdolnosc_wlasna(karta_biala,karta_czarna,sojusznicy_bialego)
            bonus_wlasny_czarny, specjalna_wlasna_czarna = oblicz_zdolnosc_wlasna(karta_czarna,karta_biala,sojusznicy_czarnego)

            #Fianalny bonus do sily karty
            bonus_bialy = policz_bonus_flag(biale_aktywne.karty) + pobierz_bonusy_wspolpracy(stan_areny, "bialy") + bonus_wlasny_bialy 
            bonus_czarny = policz_bonus_flag(czarne_aktywne.karty) + pobierz_bonusy_wspolpracy(stan_areny, "czarny") +bonus_wlasny_czarny

            rezultat = walka_kart(
                karta_biala,
                karta_czarna,
                statystyki,
                stan_areny.remis_wygrywa_bialy,
                stan_areny.remis_wygrywa_czarny,
                bonus_bialy,
                bonus_czarny,
                specjalna_wlasna_biala,
                specjalna_wlasna_czarna           
            )
            wyniki.append(rezultat["wynik"])

            if rezultat["biala_zyje"]:
                biale_zywe.dodaj(karta_biala)
            else:
                biale_zabite.dodaj(karta_biala)
                biale_sojusznicy.usun(karta_biala)

            if rezultat["czarna_zyje"]:
                czarne_zywe.dodaj(karta_czarna)
            else:
                czarne_zabite.dodaj(karta_czarna)
                czarne_sojusznicy.usun(karta_czarna)
                if czarne_karty.karty[i].klasa == 5:
                    statystyki["zabite_klasa5"] += 1

        #----- Zdolnosci wspolpracy -------
            # karta = karta_biala
            # if rezultat["wynik"] in ("W", "Z") and karta.czy_wspolpraca=='tak':   

            #     if karta.wspolpraca_sila=='R': #Wspolpraca karty Cherub 5
            #         stan_areny.remis_wygrywa_bialy = True
            #     else:
            #         bonus, _ = interpretuj_parametr(karta.wspolpraca_sila)
            #         stan_areny.bonus_nastepna_biala = bonus    

            # elif rezultat["wynik"] in ("P", "U") and karta_czarna.czy_wspolpraca=='tak':
            #     karta = karta_czarna

            #     if karta.wspolpraca_sila=='R': #na razie nie ma takiej karty ale zostaje dla porządku kodu
            #         stan_areny.remis_wygrywa_czarny = True
            #     else:
            #         bonus, _ = interpretuj_parametr(karta.wspolpraca_sila)
            #         stan_areny.bonus_nastepna_czarna = bonus  

        #-----------------------------------


        elif i < len(biale_karty.karty):
            # biała karta bez przeciwnika
            wyniki.append("W")
            biale_zywe.dodaj(karta_biala)
        else:
            # czarna karta bez przeciwnika
            wyniki.append("U")
            czarne_zywe.dodaj(karta_czarna)

        # usuwanie kart z aktywnych talii na arenie (tylko gdy był pojedynek i jeśli przegrały) aby wyłączyć ich flagi
        if i < len(biale_karty.karty) and i < len(czarne_karty.karty):
            if rezultat["wynik"] == "R":
                biale_aktywne.usun(karta_biala)
                czarne_aktywne.usun(karta_czarna)
            else:
                if rezultat["wynik"] in ("W","Z"):
                    czarne_aktywne.usun(karta_czarna)
                else:
                    biale_aktywne.usun(karta_biala)


    #dodaj punkty akcj z wpływu kart aktywnych na arenie (jeżeli mają taki wpływ)
    for karta in biale_aktywne.karty:
        statystyki["akcje_bialy"] += interpretuj_parametr(karta.mod_akcji)[0]
    for karta in czarne_aktywne.karty:
        statystyki["akcje_czarny"] += interpretuj_parametr(karta.mod_akcji)[0]

    return (
        wyniki,
        biale_zywe,
        czarne_zywe,
        biale_aktywne,
        czarne_aktywne,
        biale_zabite,
        czarne_zabite
    )
