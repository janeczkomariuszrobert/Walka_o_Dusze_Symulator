from Silnik.obiekty import *
from Silnik.mechanika import *


def walka_kart(
    karta_biała,
    karta_czarna,
    statystyki,
    remis_biały,
    remis_czarny,
    bonus_biały,
    bonus_czarny,
    specjalna_wlasna_biała,
    specjalna_wlasna_czarna,
    rzut_kostka
):
    sila_biała = policz_sile_walki(karta_biała,bonus_biały,rzut_kostka)
    sila_czarna = policz_sile_walki(karta_czarna,bonus_czarny,rzut_kostka)

    print("DEBUG SIŁA:", karta_biała.imie, "=", sila_biała, "|", karta_czarna.imie, "=", sila_czarna)

    #wynik identyfikujemy od strony białego

    #----Wyjątki----
    if karta_czarna.id == 14 and karta_czarna.kolor == "czarny":#ŚMIERĆ
        if karta_biała.id in (19, 14):  #Jezus lub Życie
            statystyki['Smierc_zyje']='NIE'
            return {
                "wynik": "Z",
                "biała_zyje": True,
                "czarna_zyje": False
            }
    #---------------

    prog_cz = 4 if karta_czarna.walka_zdolnosc in ("T", "RT") else 3  #domyslnie 3 chyba że walka_zdolnosc=T lub RT
    prog_b = 4 if karta_biała.walka_zdolnosc in ("T", "RT") else 3

    if sila_biała == sila_czarna:
        if karta_biała.walka_zdolnosc in ("R", "RT") or remis_biały==True or (specjalna_wlasna_biała == "W" and specjalna_wlasna_czarna != "W"):  #biały wygrywa mimo remisu
            numer = numer_zdolnosci_R(karta_biała)
            if not remis_biały:
                zarejestruj_uzycie_zdolnosci(statystyki, karta_biała.id, "biały",numer)
            return {
                "wynik": "W",
                "biała_zyje": True,
                "czarna_zyje": True
            }
        if karta_czarna.walka_zdolnosc in ("R", "RT") or remis_czarny==True or (specjalna_wlasna_czarna == "W" and specjalna_wlasna_biała != "W"): #czarny wygrywa mimo remisu
            numer = numer_zdolnosci_R(karta_czarna)
            if not remis_czarny:
                zarejestruj_uzycie_zdolnosci(statystyki, karta_czarna.id, "czarny",numer)
            return {
                "wynik": "P",
                "biała_zyje": True,
                "czarna_zyje": True
            }

        return {
            "wynik": "R",
            "biała_zyje": True,
            "czarna_zyje": True
        }

    
    if sila_biała > sila_czarna:
        roznica = sila_biała - sila_czarna

        if specjalna_wlasna_czarna == "W":
            # nie rejestrujemy bo to jest zdolnosc warunkowa (rejestowana gdzie indziej)
            return {
                "wynik": "P",
                "biała_zyje": True,
                "czarna_zyje": True
            }
        elif roznica >= prog_cz:          
            if karta_czarna.walka_zdolnosc == "Z2":   #na razie brak takiej karty
                if rzut_k(2) == 2:
                    # czarna przeżyła
                    zarejestruj_uzycie_zdolnosci(statystyki, karta_czarna.id, "czarny",1)
                    return {
                        "wynik": "W",
                        "biała_zyje": True,
                        "czarna_zyje": True 
                    }
            elif karta_czarna.walka_zdolnosc == "Z4" and karta_biała.id != 19: #jezeli nie walczysz z Jezusem
                if rzut_k(4) == 4:
                    # czarna przeżyła
                    zarejestruj_uzycie_zdolnosci(statystyki, karta_czarna.id, "czarny",1) #falsz prorok
                    return {
                        "wynik": "W",
                        "biała_zyje": True,
                        "czarna_zyje": True 
                    }
                
            if karta_czarna.id==14: 
                zarejestruj_uzycie_zdolnosci(statystyki, 14, "czarny",1) #SMIERC, przegrala ale nie umiera
                return {
                    "wynik": "W",
                    "biała_zyje": True,
                    "czarna_zyje": True
                }
            
            # czarna umiera:
            return {
                "wynik": "Z",
                "biała_zyje": True,
                "czarna_zyje": False
            }
        else:
            if roznica == 3 and karta_czarna.walka_zdolnosc in ("T", "RT"):
                zarejestruj_uzycie_zdolnosci(statystyki, karta_czarna.id, "czarny", 1)

            return {
                "wynik": "W",
                "biała_zyje": True,
                "czarna_zyje": True
            }
        
    else:
        roznica = sila_czarna - sila_biała

        if specjalna_wlasna_biała == "W":
            # nie rejestrujemy bo to jest zdolnosc warunkowa (rejestowana gdzie indziej)
            return {
                "wynik": "W",
                "biała_zyje": True,
                "czarna_zyje": True
            }  
        elif roznica >= prog_b:

            if karta_biała.walka_zdolnosc == "Z2":   #Serafin 10
                if rzut_k(2) == 2:
                    # biała przeżyła
                    zarejestruj_uzycie_zdolnosci(statystyki, karta_biała.id, "biały",1)
                    return {
                        "wynik": "P",
                        "biała_zyje": True,
                        "czarna_zyje": True 
                    }
            if karta_biała.walka_zdolnosc == "Z4":   #Serafin 8
                if rzut_k(4) == 4:
                    # biała przeżyła
                    zarejestruj_uzycie_zdolnosci(statystyki, karta_biała.id, "biały",1)
                    return {
                        "wynik": "P",
                        "biała_zyje": True,
                        "czarna_zyje": True 
                    }    
            return {
                "wynik": "U",
                "biała_zyje": karta_biała.walka_zdolnosc == "n", #jezeli jest 'n' to wynik bedize TRUE wiec bedzie zyc, w przeciwnym wypadku FALSE czyli umiera
                "czarna_zyje": True
            }
        else:
            if roznica == 3 and karta_biała.walka_zdolnosc in ("T", "RT"):
                zarejestruj_uzycie_zdolnosci(statystyki, karta_biała.id, "biały", 1)

            return {
                "wynik": "P",
                "biała_zyje": True,
                "czarna_zyje": True
            }


def walka_arena(białe_karty, czarne_karty, statystyki):

    wyniki = []

    stan_areny = StanAreny()  #inicjuj parametrami startowymi w clasie

    #te talie będą sie kurczyc gdy ktora karta przegra lub zgineła
    białe_aktywne = Talia()
    czarne_aktywne = Talia()

    białe_aktywne.kopiuj(białe_karty)
    czarne_aktywne.kopiuj(czarne_karty)

    białe_zywe = Talia()
    czarne_zywe = Talia()

    białe_zabite = Talia()
    czarne_zabite = Talia()

    białe_sojusznicy = Talia()
    czarne_sojusznicy = Talia()

    białe_sojusznicy.kopiuj(białe_karty)
    czarne_sojusznicy.kopiuj(czarne_karty)


    #--------Zdolnosci PRZED walką-----
    #SR to mozliwość zmiany pozycji "Super Ruch"
    wykonaj_zdolnosci_SR(statystyki,białe_karty, czarne_karty,0) #pozycja 0 oznacza ze jeszcze nie zaczeło sie układanie kart na arenie

    #SP to mozliwość poświecenia karty w zamian za bonus "Super Poświęcenie"
    bonus_sp_biały,bonus_sp_czarny,slot_sp_biały, slot_sp_czarny, wynik_sp_biały, wynik_sp_czarny=wykonaj_zdolnosc_SP(statystyki,białe_karty,czarne_karty,białe_zabite,czarne_zabite,białe_zywe,czarne_zywe,białe_aktywne,czarne_aktywne)
    


    #------PETLA GLOWNA PO SLOTACH ARENY-------------------
    for i in range(1,LICZBA_SLOTOW_ARENY+1):  #liczymy od 1 do 4

        bonus_wlasny_biały = 0      
        bonus_wlasny_czarny = 0
        specjalna_wlasna_biała = None
        specjalna_wlasna_czarna = None

        if i <= len(białe_karty.karty) and i <= len(czarne_karty.karty):
            loguj('\nDEBUG walka nr: ',i)       

            karta_biała = pobierz_karta(białe_karty.karty, i) 
            karta_czarna = pobierz_karta(czarne_karty.karty, i)

            if i == slot_sp_biały or i == slot_sp_czarny:
                if i == slot_sp_biały:
                    wynik = wynik_sp_biały
                else:
                    wynik = wynik_sp_czarny
                loguj("DEBUG: W tej walce użyto zdolności SP (poświęcenia karty) - walka roztrzygnieta wynikiem ",wynik)
                wyniki.append(wynik)
                zarejestruj_wynik_karty(statystyki,karta_biała,karta_czarna,wynik)
                continue

            statystyki["wyniki_kart"][(karta_biała.id, karta_biała.kolor)]["liczba_walk"] += 1
            statystyki["wyniki_kart"][(karta_czarna.id, karta_czarna.kolor)]["liczba_walk"] += 1

            #-----Anioł 2------------------------
            if karta_biała.id == 2 and karta_biała.kolor == "biały": 
                
                kandydaci = [
                    karta for karta in białe_zabite.karty #szukamy żywego sojusznika, który już zginął
                    if karta.klasa > 1
                ]
                #print('DEBUG znalazłem Anioła 2. Kandydaci= ',kandydaci)

                if kandydaci:
                    zarejestruj_uzycie_zdolnosci(statystyki, 2, "biały")
                    kandydat = max(kandydaci, key=lambda karta: (karta.klasa, karta.sila))
                    statystyki["wyniki_kart"][(kandydat.id, kandydat.kolor)]["wskrzesz"] += 1
                    białe_zabite.dodaj(karta_biała) #ANIOŁ umiera zamiast sojusznika
                    białe_zywe.dodaj(kandydat)
                    białe_zabite.usun(kandydat)
                    wyniki.append("U") #Przeciwnik wygrywa
                    białe_aktywne.usun(karta_biała)
                    continue       

            #---- zdolnosci SR+ (Zły duch 4)------ 
            wykonaj_zdolnosci_SR(statystyki,białe_karty,czarne_karty,i)   #sprawdzenie czy wykonać jest w środku


            sojusznicy_białego = [
                karta for karta in białe_karty.karty
                if karta is not karta_biała
            ]
            sojusznicy_czarnego = [
                karta for karta in czarne_karty.karty
                if karta is not karta_czarna
            ]

            bonus_wlasny_biały, specjalna_wlasna_biała = pobierz_zdolnosc_wlasna(statystyki, karta_biała,karta_czarna,sojusznicy_białego)  
            bonus_wlasny_czarny, specjalna_wlasna_czarna = pobierz_zdolnosc_wlasna(statystyki, karta_czarna,karta_biała,sojusznicy_czarnego)

            bonus_wspolpracy_wlasnej_biały = wykonaj_zdolnosc_przed_walka(statystyki, karta_biała,karta_czarna,sojusznicy_białego,białe_zabite,czarne_zabite)
            bonus_wspolpracy_wlasnej_czarny = wykonaj_zdolnosc_przed_walka(statystyki, karta_czarna,karta_biała,sojusznicy_czarnego,białe_zabite,czarne_zabite)

            bonus_flagi_biały=policz_bonus_flag(karta_biała,statystyki,białe_aktywne.karty,True)
            bonus_flagi_czarny=policz_bonus_flag(karta_czarna,statystyki,czarne_aktywne.karty,True)

            bonus_wspolpracy_od_innych_biały=pobierz_bonusy_wspolpracy(stan_areny, "biały")
            bonus_wspolpracy_od_innych_czarny=pobierz_bonusy_wspolpracy(stan_areny, "czarny")

            #Fianalny bonus do sily karty
            bonus_biały =  bonus_flagi_biały + bonus_wspolpracy_od_innych_biały + bonus_wlasny_biały + bonus_wspolpracy_wlasnej_biały + bonus_sp_biały
            bonus_czarny = bonus_flagi_czarny + bonus_wspolpracy_od_innych_czarny +bonus_wlasny_czarny + bonus_wspolpracy_wlasnej_czarny + bonus_sp_czarny

            loguj('DEBUG: białe bonus: FLAGA ', bonus_flagi_biały,' | WSPOLPRACA OD', bonus_wspolpracy_od_innych_biały,' | WLASNY ', bonus_wlasny_biały, ' | WSPOLPRACA JA ', bonus_wspolpracy_wlasnej_biały, ' | od SP ', bonus_sp_biały)
            loguj('DEBUG: Czarne bonus: FLAGA ', bonus_flagi_czarny,' | WSPOLPRACA OD', bonus_wspolpracy_od_innych_czarny,' | WLASNY ',bonus_wlasny_czarny, ' | WSPOLPRACA JA ',  bonus_wspolpracy_wlasnej_czarny, ' | od SP ', bonus_sp_czarny)

            rezultat = walka_kart(
                karta_biała,
                karta_czarna,
                statystyki,
                stan_areny.remis_wygrywa_biały,
                stan_areny.remis_wygrywa_czarny,
                bonus_biały,
                bonus_czarny,
                specjalna_wlasna_biała,
                specjalna_wlasna_czarna,
                True         
            )
            wynik=rezultat["wynik"]

            #-------KARTY SPECJALNE------
            if karta_biała.id == 17 and wynik == "U": # DUCH ŚWIĘTY nie może umrzeć
                wynik = "P"
                rezultat["biała_zyje"] = True
                zarejestruj_uzycie_zdolnosci(statystyki, 17, 'biały')

            if karta_biała.id == 14: # ŻYCIE   
                if karta_czarna.id == 14: # Walka ze ŚMIERCIĄ - automatyczne zwycięstwo
                    wynik = "Z"
                    rezultat["biała_zyje"] = True
                    rezultat["czarna_zyje"] = False
                    #stan_areny.zabity_czarny = True
                    # zarejestruj_uzycie_zdolnosci(statystyki, 14, "biały",2)
                elif karta_czarna.klasa <= 3 and wynik == "Z": # ŻYCIE nie może zabić karty klasy <= 3
                    wynik = "W"
                    rezultat["biała_zyje"] = True
                    rezultat["czarna_zyje"] = True
                    zarejestruj_uzycie_zdolnosci(statystyki, 14, "biały",1)

            if (
                karta_biała.id == 19 and karta_biała.kolor == "biały" #Jezus
                and karta_czarna.klasa in (1, 2)
                and karta_czarna.typ_wspolpracy != "SR"
            ):
                wynik = "W"
                rezultat["czarna_zyje"] = True
                zarejestruj_uzycie_zdolnosci(statystyki, 19, "biały")
                statystyki["akcje_biały"] += karta_czarna.klasa





            #-----------------------------

            wyniki.append(wynik)
            zarejestruj_wynik_karty(statystyki,karta_biała,karta_czarna,wynik)

            if rezultat["biała_zyje"]:
                białe_zywe.dodaj(karta_biała)
            else:
                białe_zabite.dodaj(karta_biała)  #to sa zabite per runda
                #stan_areny.zabity_biały = True
                białe_sojusznicy.usun(karta_biała)

            if rezultat["czarna_zyje"]:
                czarne_zywe.dodaj(karta_czarna)
            else:
                czarne_zabite.dodaj(karta_czarna)
                czarne_sojusznicy.usun(karta_czarna)
                #stan_areny.zabity_czarny = True
                if karta_czarna.klasa == 5:
                    statystyki["zabite_klasa5"] += 1

            loguj(f"DEBUG: Wynik walki nr {i}: {karta_biała.imie} ({karta_biała.kolor}) vs {karta_czarna.imie} ({karta_czarna.kolor}) = {wynik}")

            #----- Zdolnosci wspolpracy po walce-------
            if wynik in ("W", "Z") and karta_biała.typ_wspolpracy in (1, 3, "R"):
                wykonaj_zdolnosc_po_walce(wynik, karta_biała, stan_areny, statystyki, i) #dostaw ewentualne bonusy sojusznikom zwycięzcy (przez stan areny)         
            elif wynik in ("P", "U") and karta_czarna.typ_wspolpracy in (1, 3, "R"):
                wykonaj_zdolnosc_po_walce(wynik, karta_czarna, stan_areny, statystyki, i)
            #-----------------------------------


        elif i < len(białe_karty.karty):
            # biała karta bez przeciwnika
            wyniki.append("W")
            białe_zywe.dodaj(karta_biała)
        else:
            # czarna karta bez przeciwnika
            wyniki.append("U")
            czarne_zywe.dodaj(karta_czarna)

        # usuwanie kart z aktywnych talii na arenie (tylko gdy był pojedynek i jeśli przegrały) aby wyłączyć ich flagi
        if i < len(białe_karty.karty) and i < len(czarne_karty.karty):
            if wynik == "R":
                białe_aktywne.usun(karta_biała)
                czarne_aktywne.usun(karta_czarna)
            else:
                if wynik in ("W","Z"):
                    czarne_aktywne.usun(karta_czarna)
                else:
                    białe_aktywne.usun(karta_biała)

    #dodaj punkty akcj z wpływu kart aktywnych na arenie (jeżeli mają taki wpływ)
    for karta in białe_aktywne.karty:
        statystyki["akcje_biały"] += interpretuj_parametr(karta.mod_akcji)[0]
    for karta in czarne_aktywne.karty:
        statystyki["akcje_czarny"] += interpretuj_parametr(karta.mod_akcji)[0]

    return (
        wyniki,
        białe_zywe,
        czarne_zywe,
        białe_aktywne,
        czarne_aktywne,
        białe_zabite,
        czarne_zabite
    )







def symuluj_testowa_arena(statystyki,białe_karty,czarne_karty,białe_wybrane, czarne_wybrane):

    testowe_białe = Talia()
    testowe_czarne = Talia()

    # Wybierz wskazane karty z pełnych talii
    for id_karty in białe_wybrane:
        for karta in białe_karty.karty:
            if int(karta.id) == id_karty:
                testowe_białe.dodaj(karta)
                break

    for id_karty in czarne_wybrane:
        for karta in czarne_karty.karty:
            if int(karta.id) == id_karty:
                testowe_czarne.dodaj(karta)
                break

    # Sprawdzenie czy znaleziono wszystkie karty
    if len(testowe_białe.karty) != len(białe_wybrane):
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
    for i, karta in enumerate(testowe_białe.karty):
        print(i + 1, karta)

    print("\nCZARNE:")
    for i, karta in enumerate(testowe_czarne.karty):
        print(i + 1, karta)

    print("\n--- ROZPOCZYNAM WALKĘ ---")

    # Uruchamiamy normalny silnik walki
    wynik = walka_arena(
        testowe_białe,
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