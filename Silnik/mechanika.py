import random
import Silnik.obiekty as Talia

def uzupelnij_gotowe(gotowe, odpoczywajace, runda, kolor):
    if len(odpoczywajace.karty) == 0:
        return
    print(f"Runda {runda}: uzupełnienie stosu GOTOWYCH ({kolor})")
    gotowe.dolacz(odpoczywajace)
    gotowe.potasuj()


def rzut_k4():
    return random.randint(1, 4)

def walka_kart(karta_biala, karta_czarna):

    sila_biala = karta_biala.sila + rzut_K4()
    sila_czarna = karta_czarna.sila + rzut_K4()

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


def walka_arena(biale_karty, czarne_karty):

    wyniki = []

    biale_zywe = Talia()
    czarne_zywe = Talia()

    biale_zabite = Talia()
    czarne_zabite = Talia()

    liczba_slotow = max(
        len(biale_karty.karty),
        len(czarne_karty.karty)
    )

    for i in range(liczba_slotow):

        if i < len(biale_karty.karty) and i < len(czarne_karty.karty):
            rezultat = walka_kart(
                biale_karty.karty[i],
                czarne_karty.karty[i]
            )
            wyniki.append(rezultat["wynik"])

            if rezultat["biala_zyje"]:
                biale_zywe.dodaj(biale_karty.karty[i])
            else:
                biale_zabite.dodaj(biale_karty.karty[i])
            if rezultat["czarna_zyje"]:
                czarne_zywe.dodaj(czarne_karty.karty[i])
            else:
                czarne_zabite.dodaj(czarne_karty.karty[i])
        elif i < len(biale_karty.karty):
            # biała karta bez przeciwnika
            wyniki.append("W")
            biale_zywe.dodaj(biale_karty.karty[i])
        else:
            # czarna karta bez przeciwnika
            wyniki.append("U")
            czarne_zywe.dodaj(czarne_karty.karty[i])
    return (
        wyniki,
        biale_zywe,
        czarne_zywe,
        biale_zabite,
        czarne_zabite
    )

def czy_ma_karty(gotowe, odpoczywajace):

    return (
        len(gotowe.karty) > 0
        or
        len(odpoczywajace.karty) > 0
    )