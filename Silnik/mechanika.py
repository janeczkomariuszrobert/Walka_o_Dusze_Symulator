import random
from Silnik.obiekty import Talia

LICZBA_SLOTOW_ARENY = 4

def uzupelnij_gotowe(gotowe, odpoczywajace, kolor,runda):
    if len(odpoczywajace.karty) == 0:
        return
    print(f"Runda {runda}: uzupełnienie stosu GOTOWYCH ({kolor})")
    gotowe.przenies(odpoczywajace)
    gotowe.potasuj()


def rzut_k(wartosc):
    return random.randint(1, wartosc)

def policz_sile_walki(karta, bonus_areny):

    sila = karta.sila
    sila += policz_bonus(karta.walka_sila_ty)
    sila += bonus_areny
    sila += rzut_k(4)
    return sila

def policz_bonus(wartosc):

    if isinstance(wartosc, int):
        return wartosc
    if wartosc == "+K4":
        return rzut_k(4)
    if wartosc == "+K2":
        return rzut_k(2)
    return 0

def policz_bonus_flag( karty_aktyw ):  #karty_aktyw jest listą kart aktywnych na arenie

    bonus = 0
    for karta in karty_aktyw:
        if karta.flaga == "tak":
            bonus += policz_bonus(karta.walka_sila_inni)
    return bonus


def walka_kart(karta_biala, karta_czarna, bonus_bialy=0, bonus_czarny=0):

    sila_biala = policz_sile_walki(
        karta_biala,
        bonus_bialy
    )

    sila_czarna = policz_sile_walki(
        karta_czarna,
        bonus_czarny
    )

    if sila_biala == sila_czarna:
        return {
            "wynik": "R",
            "biala_zyje": True,
            "czarna_zyje": True
        }
    if sila_biala > sila_czarna:
        roznica = sila_biala - sila_czarna
        if roznica >= 3:
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
        if roznica >= 3:
            return {
                "wynik": "U",
                "biala_zyje": False,
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

    #te talie będą sie kurczyc gdy ktora karta przegra lub zgidnia
    biale_aktywne = Talia()
    czarne_aktywne = Talia()

    biale_aktywne.kopiuj(biale_karty)
    czarne_aktywne.kopiuj(czarne_karty)

    biale_zywe = Talia()
    czarne_zywe = Talia()

    biale_zabite = Talia()
    czarne_zabite = Talia()

    for i in range(LICZBA_SLOTOW_ARENY):

        # print("Slot:", i)
        # print(
        #     "Białe:",
        #     len(biale_karty.karty),
        #     "Czarne:",
        #     len(czarne_karty.karty)
        # )

        if i < len(biale_karty.karty) and i < len(czarne_karty.karty):

            bonus_bialy = policz_bonus_flag(biale_aktywne.karty)
            bonus_czarny = policz_bonus_flag(czarne_aktywne.karty)

            rezultat = walka_kart(
                biale_karty.karty[i],
                czarne_karty.karty[i],
                bonus_bialy,
                bonus_czarny
            )
            wyniki.append(rezultat["wynik"])

            #zwiekszenie liczby zabitych pionkow, jesli ktora karta zabija pionki
            if rezultat["wynik"] in ("P","U") and czarne_karty.karty[i].zabija > 0:
                statystyki["zabite_pionki"] += czarne_karty.karty[i].zabija

            if rezultat["biala_zyje"]:
                biale_zywe.dodaj(biale_karty.karty[i])
            else:
                biale_zabite.dodaj(biale_karty.karty[i])

            if rezultat["czarna_zyje"]:
                czarne_zywe.dodaj(czarne_karty.karty[i])
            else:
                czarne_zabite.dodaj(czarne_karty.karty[i])
                if czarne_karty.karty[i].klasa == 5:
                    statystyki["zabite_klasa5"] += 1

        elif i < len(biale_karty.karty):
            # biała karta bez przeciwnika
            wyniki.append("W")
            biale_zywe.dodaj(biale_karty.karty[i])
        else:
            # czarna karta bez przeciwnika
            wyniki.append("U")
            czarne_zywe.dodaj(czarne_karty.karty[i])

        # usuwanie kart z aktywnych talii na arenie (tylko gdy był pojedynek i jeśli przegrały) aby wyłączyć ich flagi
        if i < len(biale_karty.karty) and i < len(czarne_karty.karty):
            biala = biale_karty.karty[i]
            czarna = czarne_karty.karty[i]

            if rezultat["wynik"] == "R":
                biale_aktywne.usun(biala)
                czarne_aktywne.usun(czarna)
            else:
                if rezultat["wynik"] in ("W","Z"):
                    czarne_aktywne.usun(czarna)
                else:
                    biale_aktywne.usun(biala)

    return (
        wyniki,
        biale_zywe,
        czarne_zywe,
        biale_zabite,
        czarne_zabite
    )

def debug_stan_gry(
        runda,
        biale_gotowe,
        biale_odpoczywajace,
        biale_stos_smierci,
        czarne_gotowe,
        czarne_odpoczywajace,
        czarne_stos_smierci,
        statystyki):

    print()
    print("=" * 50)
    print(f"DEBUG - RUNDA {runda}")
    print("=" * 50)

    print("BIAŁE")
    print(f"  Gotowe        : {len(biale_gotowe)}")
    print(f"  Odpoczywające : {len(biale_odpoczywajace)}")
    print(f"  Stos śmierci  : {len(biale_stos_smierci)}")
    print(f"  SUMA          : {len(biale_gotowe)+len(biale_odpoczywajace)+len(biale_stos_smierci)}")

    print()

    print("CZARNE")
    print(f"  Gotowe        : {len(czarne_gotowe)}")
    print(f"  Odpoczywające : {len(czarne_odpoczywajace)}")
    print(f"  Stos śmierci  : {len(czarne_stos_smierci)}")
    print(f"  SUMA          : {len(czarne_gotowe)+len(czarne_odpoczywajace)+len(czarne_stos_smierci)}")

    print()

    print("STATYSTYKI")
    print(f"  Zabite klasa 5 : {statystyki['zabite_klasa5']}")
    print(f"  Zabite pionki  : {statystyki['zabite_pionki']}")

    print("=" * 50)
    print()
