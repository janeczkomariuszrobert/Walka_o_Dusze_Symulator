print("Walka o Dusze - symulator v0.1")

from Silnik.obiekty import Talia
from Silnik.mechanika import uzupelnij_gotowe
from Silnik.mechanika import walka_arena
from Silnik.mechanika import czy_ma_karty

biale_gotowe = Talia()
biale_odpoczywajace = Talia()
biale_stos_smierci = Talia()

czarne_gotowe = Talia()
czarne_odpoczywajace = Talia()
czarne_stos_smierci = Talia()

biale_gotowe.wczytaj("DANE/karty.json", "biała")
biale_gotowe.potasuj()

czarne_gotowe.wczytaj("DANE/karty.json", "czarna")

biale_gotowe.potasuj()
czarne_gotowe.potasuj()


maksymalna_liczba_rund = 100
runda = 1
while runda <= maksymalna_liczba_rund:

    if not czy_ma_karty(
        czarne_gotowe,
        czarne_odpoczywajace
    ):

        print("Koniec gry - czarne nie mają kart")
        break


    print()
    print("================")
    print("RUNDA", runda)
    print("================")

    # pobranie ręki
    biale_na_arenie = biale_gotowe.pobierz_reke(4)
    czarne_na_arenie = czarne_gotowe.pobierz_reke(4)

    # walka
    wynik, biale_zywe, czarne_zywe, biale_zabite_runda, czarne_zabite_runda = walka_arena(biale_na_arenie,czarne_na_arenie)

    print("Arena:", "".join(wynik))

    # żywe karty wracają do odpoczynku
    biale_odpoczywajace.dolacz(biale_zywe)
    czarne_odpoczywajace.dolacz(czarne_zywe)

    # martwe karty idą do stosu śmierci
    biale_stos_smierci.dolacz(biale_zabite_runda)
    czarne_stos_smierci.dolacz(czarne_zabite_runda)

    if len(biale_gotowe.karty) < 4 and len(biale_odpoczywajace.karty) > 0:
        uzupelnij_gotowe(
            biale_gotowe,
            biale_odpoczywajace,
            "biały",
            runda
        )

    if len(czarne_gotowe.karty) < 4 and len(biale_odpoczywajace.karty) > 0:
        uzupelnij_gotowe(
            czarne_gotowe,
            czarne_odpoczywajace,
            "czarny",
            runda
        )

    runda += 1