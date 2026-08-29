from Silnik.obiekty import *
from Silnik.mechanika import *


def walka_kart(
    karta_biala,
    karta_czarna,
    statystyki,
    remis_bialy,
    remis_czarny,
    bonus_bialy,
    bonus_czarny,
    specjalna_wlasna_biala,
    specjalna_wlasna_czarna,
    rzut_kostka
):
    sila_biala = policz_sile_walki(
        karta_biala,
        bonus_bialy,
        rzut_kostka
    )
    sila_czarna = policz_sile_walki(
        karta_czarna,
        bonus_czarny,
        rzut_kostka
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

    prog_cz = 4 if karta_czarna.walka_zdolnosc in ("T", "RT") else 3  #domyslnie 3 chyba że walka_zdolnosc=T lub RT
    prog_b = 4 if karta_biala.walka_zdolnosc in ("T", "RT") else 3

    if sila_biala == sila_czarna:
        if karta_biala.walka_zdolnosc in ("R", "RT") or remis_bialy==True or (specjalna_wlasna_biala == "W" and specjalna_wlasna_czarna != "W"):  #biały wygrywa mimo remisu
            zarejestruj_uzycie_zdolnosci(statystyki, karta_biala.id, "bialy",2)
            return {
                "wynik": "W",
                "biala_zyje": True,
                "czarna_zyje": True
            }
        if karta_czarna.walka_zdolnosc in ("R", "RT") or remis_czarny==True or (specjalna_wlasna_czarna == "W" and specjalna_wlasna_biala != "W"): #czarny wygrywa mimo remisu
            zarejestruj_uzycie_zdolnosci(statystyki, karta_czarna.id, "czarny",2)
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
            # nie rejestrujemy bo to jest zdolnosc warunkowa (rejestowana gdzie indziej)
            return {
                "wynik": "P",
                "biala_zyje": True,
                "czarna_zyje": True
            }
        elif roznica >= prog_cz:          
            if karta_czarna.walka_zdolnosc == "Z2":   #na razie brak takiej karty
                if rzut_k(2) == 2:
                    # czarna przeżyła
                    zarejestruj_uzycie_zdolnosci(statystyki, karta_czarna.id, "czarny",1)
                    return {
                        "wynik": "W",
                        "biala_zyje": True,
                        "czarna_zyje": True 
                    }
            elif karta_czarna.walka_zdolnosc == "Z4" and karta_biala.id != 19: #jezeli nie walczysz z Jezusem
                if rzut_k(4) == 4:
                    # czarna przeżyła
                    zarejestruj_uzycie_zdolnosci(statystyki, karta_czarna.id, "czarny",1) #falsz prorok
                    return {
                        "wynik": "W",
                        "biala_zyje": True,
                        "czarna_zyje": True 
                    }
                
            if karta_czarna.id==14: 
                zarejestruj_uzycie_zdolnosci(statystyki, 14, "czarny",1) #SMIERC, przegrala ale nie umiera
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
            if roznica == 3 and karta_czarna.walka_zdolnosc in ("T", "RT"):
                zarejestruj_uzycie_zdolnosci(statystyki, karta_czarna.id, "czarny", 1)

            return {
                "wynik": "W",
                "biala_zyje": True,
                "czarna_zyje": True
            }
        
    else:
        roznica = sila_czarna - sila_biala

        if specjalna_wlasna_biala == "W":
            # nie rejestrujemy bo to jest zdolnosc warunkowa (rejestowana gdzie indziej)
            return {
                "wynik": "W",
                "biala_zyje": True,
                "czarna_zyje": True
            }  
        elif roznica >= prog_b:

            if karta_biala.walka_zdolnosc == "Z2":   #Serafin 10
                if rzut_k(2) == 2:
                    # biała przeżyła
                    zarejestruj_uzycie_zdolnosci(statystyki, karta_biala.id, "bialy",1)
                    return {
                        "wynik": "P",
                        "biala_zyje": True,
                        "czarna_zyje": True 
                    }
            if karta_biala.walka_zdolnosc == "Z4":   #Serafin 8
                if rzut_k(4) == 4:
                    # biała przeżyła
                    zarejestruj_uzycie_zdolnosci(statystyki, karta_biala.id, "bialy",1)
                    return {
                        "wynik": "P",
                        "biala_zyje": True,
                        "czarna_zyje": True 
                    }    
            return {
                "wynik": "U",
                "biala_zyje": karta_biala.walka_zdolnosc == "n", #jezeli jest 'n' to wynik bedize TRUE wiec bedzie zyc, w przeciwnym wypadku FALSE czyli umiera
                "czarna_zyje": True
            }
        else:
            if roznica == 3 and karta_biala.walka_zdolnosc in ("T", "RT"):
                zarejestruj_uzycie_zdolnosci(statystyki, karta_biala.id, "bialy", 1)

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

    biale_sojusznicy = Talia()
    czarne_sojusznicy = Talia()

    biale_sojusznicy.kopiuj(biale_karty)
    czarne_sojusznicy.kopiuj(czarne_karty)


    #--------Zdolnosci PRZED walką-----
    #SR to mozliwość zmiany pozycji "Super Ruch"
    wykonaj_zdolnosci_SR(statystyki,biale_karty, czarne_karty,0) #pozycja 0 oznacza ze jeszcze nie zaczeło sie układanie kart na arenie
    #SP to mozliwość poświecenia karty w zamian za bonus "Super Poświęcenie"
    bonus_sp_bialy,bonus_sp_czarny=wykonaj_zdolnosc_SP(statystyki,biale_karty,czarne_karty,biale_zabite,czarne_zabite,biale_zywe,czarne_zywe,biale_aktywne,czarne_aktywne)
    


    #------PETLA GLOWNA PO SLOTACH ARENY-------------------
    for i in 1+range(LICZBA_SLOTOW_ARENY):  #liczymy od 1 do 4

        bonus_wlasny_bialy = 0      
        bonus_wlasny_czarny = 0
        specjalna_wlasna_biala = None
        specjalna_wlasna_czarna = None

        if i < len(biale_karty.karty) and i < len(czarne_karty.karty):

            karta_biala = biale_karty.karty[i]
            karta_czarna = czarne_karty.karty[i]

            #-----Anioł 2------------------------
            if karta_biala.id == 2 and karta_biala.kolor == "biały": 
                kandydaci = [
                    karta for karta in biale_zabite.karty #szukamy żywego sojusznika, który już zginął
                    if karta.klasa > 1
                ]
                if kandydaci:
                    zarejestruj_uzycie_zdolnosci(statystyki, 2, "biały")
                    kandydat = max(kandydaci, key=lambda karta: (karta.klasa, karta.sila))
                    biale_zabite.dodaj(karta_biala) #ANIOŁ umiera zamiast sojusznika
                    biale_zywe.dodaj(kandydat)
                    biale_zabite.usun(kandydat)
                    wyniki.append("U") #Przeciwnik wygrywa
                    biale_aktywne.usun(karta_biala)
                    continue       

            #---- zdolnosci SR+ (Zły duch 4)------ 
            wykonaj_zdolnosci_SR(statystyki,biale_karty,czarne_karty,i)   #sprawdzenie czy wykonać jest w środku


            sojusznicy_bialego = [
                karta for karta in biale_karty.karty
                if karta is not karta_biala
            ]
            sojusznicy_czarnego = [
                karta for karta in czarne_karty.karty
                if karta is not karta_czarna
            ]

            bonus_wlasny_bialy, specjalna_wlasna_biala = pobierz_zdolnosc_wlasna(statystyki, karta_biala,karta_czarna,sojusznicy_bialego)  
            bonus_wlasny_czarny, specjalna_wlasna_czarna = pobierz_zdolnosc_wlasna(statystyki, karta_czarna,karta_biala,sojusznicy_czarnego)

            bonus_wspolpracy_wlasnej_bialy = wykonaj_zdolnosc_przed_walka(statystyki, karta_biala,karta_czarna,sojusznicy_bialego)
            bonus_wspolpracy_wlasnej_czarny = wykonaj_zdolnosc_przed_walka(statystyki, karta_czarna,karta_biala,sojusznicy_czarnego)

            bonus_flagi_bialy=policz_bonus_flag(biale_aktywne.karty)
            bonus_flagi_czarny=policz_bonus_flag(czarne_aktywne.karty)

            bonus_wspolpracy_od_innych_biały=pobierz_bonusy_wspolpracy(stan_areny, "bialy")
            bonus_wspolpracy_od_innych_czarny=pobierz_bonusy_wspolpracy(stan_areny, "czarny")

            #Fianalny bonus do sily karty
            bonus_bialy =  bonus_flagi_bialy + bonus_wspolpracy_od_innych_biały + bonus_wlasny_bialy + bonus_wspolpracy_wlasnej_bialy + bonus_sp_bialy
            bonus_czarny = bonus_flagi_czarny + bonus_wspolpracy_od_innych_czarny +bonus_wlasny_czarny + bonus_wspolpracy_wlasnej_czarny + bonus_sp_czarny

            loguj('DEBUG: Biale bonus: ', bonus_flagi_bialy, bonus_wspolpracy_od_innych_biały, bonus_wlasny_bialy, bonus_wspolpracy_wlasnej_bialy)
            loguj('DEBUG: Czarne bonus: ', bonus_flagi_czarny, bonus_wspolpracy_od_innych_czarny, bonus_wlasny_czarny, bonus_wspolpracy_wlasnej_czarny)

            rezultat = walka_kart(
                karta_biala,
                karta_czarna,
                statystyki,
                stan_areny.remis_wygrywa_bialy,
                stan_areny.remis_wygrywa_czarny,
                bonus_bialy,
                bonus_czarny,
                specjalna_wlasna_biala,
                specjalna_wlasna_czarna,
                True         
            )
            wynik=rezultat["wynik"]

            #-------KARTY SPECJALNE------
            if karta_biala.id == 17: # DUCH ŚWIĘTY nie może umrzeć
                if wynik == "Z":
                    wynik = "P"
                    rezultat["biala_zyje"] = True
                    zarejestruj_uzycie_zdolnosci(statystyki, 17, 'bialy')

            if karta_biala.id == 14: # ŻYCIE   
                if karta_czarna.id == 14: # Walka ze ŚMIERCIĄ - automatyczne zwycięstwo
                    wynik = "Z"
                    rezultat["biala_zyje"] = True
                    rezultat["czarna_zyje"] = False
                    zarejestruj_uzycie_zdolnosci(statystyki, 14, "bialy",2)
                elif karta_czarna.klasa <= 3 and wynik == "Z": # ŻYCIE nie może zabić karty klasy <= 3
                    wynik = "W"
                    rezultat["biala_zyje"] = True
                    rezultat["czarna_zyje"] = True
                    zarejestruj_uzycie_zdolnosci(statystyki, 14, "bialy",1)

            #-----------------------------

            wyniki.append(wynik)
            zarejestruj_wynik_karty(statystyki,karta_biala,karta_czarna,wynik)

            if rezultat["biala_zyje"]:
                biale_zywe.dodaj(karta_biala)
            else:
                biale_zabite.dodaj(karta_biala)  #to sa zabite per runda
                biale_sojusznicy.usun(karta_biala)

            if rezultat["czarna_zyje"]:
                czarne_zywe.dodaj(karta_czarna)
            else:
                czarne_zabite.dodaj(karta_czarna)
                czarne_sojusznicy.usun(karta_czarna)
                if czarne_karty.karty[i].klasa == 5:
                    statystyki["zabite_klasa5"] += 1

            #----- Zdolnosci wspolpracy po walce-------
            if wynik in ("W", "Z") and karta_biala.typ_wspolpracy in ("1", "3", "R"):
                wykonaj_zdolnosc_po_walce(wynik, karta_biala, stan_areny,statystyki) #dostaw ewentualne bonusy sojusznikom zwycięzcy (przez stan areny)         
            elif wynik in ("P", "U") and karta_czarna.typ_wspolpracy in ("1", "3", "R"):
                wykonaj_zdolnosc_po_walce(wynik, karta_czarna, stan_areny,statystyki)
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
            if wynik == "R":
                biale_aktywne.usun(karta_biala)
                czarne_aktywne.usun(karta_czarna)
            else:
                if wynik in ("W","Z"):
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







def symuluj_testowa_arena(statystyki,biale_karty,czarne_karty,biale_wybrane, czarne_wybrane):

    testowe_biale = Talia()
    testowe_czarne = Talia()

    # Wybierz wskazane karty z pełnych talii
    for id_karty in biale_wybrane:
        for karta in biale_karty.karty:
            if int(karta.id) == id_karty:
                testowe_biale.dodaj(karta)
                break

    for id_karty in czarne_wybrane:
        for karta in czarne_karty.karty:
            if int(karta.id) == id_karty:
                testowe_czarne.dodaj(karta)
                break

    # Sprawdzenie czy znaleziono wszystkie karty
    if len(testowe_biale.karty) != len(biale_wybrane):
        print("BŁĄD: Nie znaleziono wszystkich wskazanych kart białych.")
        return

    if len(testowe_czarne.karty) != len(czarne_wybrane):
        print("BŁĄD: Nie znaleziono wszystkich wskazanych kart czarnych.")
        return

    # Stan początkowy
    print("\n================================")
    print("TESTOWA ARENA")
    print("================================")

    print("\nBIAŁE:")
    for i, karta in enumerate(testowe_biale.karty):
        print(i + 1, karta)

    print("\nCZARNE:")
    for i, karta in enumerate(testowe_czarne.karty):
        print(i + 1, karta)

    print("\n--- ROZPOCZYNAM WALKĘ ---")

    # Uruchamiamy normalny silnik walki
    wynik = walka_arena(
        testowe_biale,
        testowe_czarne,
        statystyki
    )

    print("\n--- WYNIK ---")
    print("Wyniki walk:", wynik[0])

    print("\nBIAŁE ŻYWE:")
    for karta in wynik[1].karty:
        print(karta)

    print("\nCZARNE ŻYWE:")
    for karta in wynik[2].karty:
        print(karta)

    print("\nBIAŁE ZABITE:")
    for karta in wynik[5].karty:
        print(karta)

    print("\nCZARNE ZABITE:")
    for karta in wynik[6].karty:
        print(karta)

    return wynik