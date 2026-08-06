print("Walka o Dusze - symulator v0.9")

from Silnik.obiekty import Talia
from Silnik.mechanika import uzupelnij_gotowe
from Silnik.mechanika import walka_arena
from Silnik.mechanika import debug_stan_gry

statystyki = {
    "runda": 0,
    "zabite_pionki": 0,
    "zabite_klasa5": 0
}

biale_gotowe = Talia()
biale_odpoczywajace = Talia()
biale_stos_smierci = Talia()

czarne_gotowe = Talia()
czarne_odpoczywajace = Talia()
czarne_stos_smierci = Talia()

biale_gotowe.wczytaj("DANE/karty_v1.json", "biały")
czarne_gotowe.wczytaj("DANE/karty_v1.json", "czarny")

# print("Po wczytaniu:")
# print("Białe :", len(biale_gotowe))
# print("Czarne:", len(czarne_gotowe))

biale_gotowe.potasuj()
czarne_gotowe.potasuj()


maksymalna_liczba_rund = 100
runda = 1
while runda <= maksymalna_liczba_rund:

    if statystyki["zabite_klasa5"] >= 3:
        print("Koniec gry - Biały zrealizował cel")
        break

    if statystyki["zabite_pionki"] >= 50:
        print("Koniec gry - Czarny zrealizował cel")
        break

    # debug_stan_gry(
    #     runda,
    #     biale_gotowe,
    #     biale_odpoczywajace,
    #     biale_stos_smierci,
    #     czarne_gotowe,
    #     czarne_odpoczywajace,
    #     czarne_stos_smierci,
    #     statystyki
    # )

    print("================")
    print("RUNDA", runda)
    print("================")

    # pobranie ręki
    biale_na_arenie = biale_gotowe.pobierz_reke(4)
    czarne_na_arenie = czarne_gotowe.pobierz_reke(4)

    # print("Arena przed walką:")
    # print("Białe:", len(biale_na_arenie))
    # print("Czarne:", len(czarne_na_arenie))

    # print("Białe karty:")
    # for karta in biale_na_arenie.karty:
    #     print(karta.imie)

    # print("Czarne karty:")
    # for karta in czarne_na_arenie.karty:
    #     print(karta.imie)


    # print("Czy będzie odnowa białych?", len(biale_gotowe) < 4)
    # print("Czy będzie odnowa czarnych?", len(czarne_gotowe) < 4)


    ### WALKA ###
    wynik, biale_zywe, czarne_zywe, biale_zabite_runda, czarne_zabite_runda = walka_arena(biale_na_arenie,czarne_na_arenie, statystyki)

    print("Arena Wynik:", "".join(wynik))

    # żywe karty wracają do odpoczynku
    biale_odpoczywajace.przenies(biale_zywe)
    czarne_odpoczywajace.przenies(czarne_zywe)

    # martwe karty idą do stosu śmierci
    biale_stos_smierci.przenies(biale_zabite_runda)
    czarne_stos_smierci.przenies(czarne_zabite_runda)



    print(
        "DEBUG Białe po bitwie:",
        len(biale_gotowe),
        len(biale_odpoczywajace),
        len(biale_stos_smierci),
        statystyki["zabite_klasa5"]
    )

    print(
        "DEBUG Czarne po bitwie:",
        len(czarne_gotowe),
        len(czarne_odpoczywajace),
        len(czarne_stos_smierci),
        statystyki["zabite_pionki"]
    )



    #zaprogramowania Odnowa zawsze w ostanim mozliwym momencie (bez strategi)
    if len(biale_gotowe.karty) < 4 and len(biale_odpoczywajace.karty) > 0:
        uzupelnij_gotowe(
            biale_gotowe,
            biale_odpoczywajace,
            "biały",
            runda
        )
    if len(czarne_gotowe.karty) < 4 and len(czarne_odpoczywajace.karty) > 0:
        uzupelnij_gotowe(
            czarne_gotowe,
            czarne_odpoczywajace,
            "czarny",
            runda
        )

    # print(
    #     "DEBUG: Po odnowie białych:",
    #     len(biale_gotowe),
    #     len(biale_odpoczywajace)
    # )


    runda += 1
    statystyki["runda"] += 1
    statystyki["zabite_pionki"] += 1  #sumulacja zabicia pionka za akcje pionkow

print("\nBiałe karty które przeżyły:")
for karta in biale_gotowe.karty + biale_odpoczywajace.karty:
    print(karta.imie)

print("\nCzarne karty które przeżyły:")
for karta in czarne_gotowe.karty + czarne_odpoczywajace.karty:
    print(karta.imie)