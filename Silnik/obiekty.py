import random
import json

class Karta:

    def __init__(
        self,
        id, imie, kolor, klasa, sila,
        liczba_zdolnosci_walk,
        walka_sila_bonus,
        walka_zdolnosc,
        warunek_wlasny,
        flaga_sila,
        wspolpraca_sila,
        typ_wspolpracy,
        czy_wspolpraca,
        warunek_wspolpraca,
        czy_flaga,
        zaraza,
        zabija,
        koszt,
        limit_akcji,
        mod_akcji,
        opis_koszt
    ):
        self.id = id
        self.imie = imie
        self.kolor = kolor
        self.klasa = klasa
        self.sila = sila
        self.liczba_zdolnosci_walk=liczba_zdolnosci_walk
        self.walka_sila_bonus = walka_sila_bonus
        self.walka_zdolnosc=walka_zdolnosc
        self.warunek_wlasny=warunek_wlasny
        self.flaga_sila = flaga_sila
        self.wspolpraca_sila = wspolpraca_sila
        self.typ_wspolpracy = typ_wspolpracy
        self.czy_wspolpraca=czy_wspolpraca
        self.warunek_wspolpraca = warunek_wspolpraca
        self.czy_flaga = czy_flaga
        self.zaraza = zaraza
        self.zabija = zabija
        self.koszt = koszt
        self.limit = limit_akcji
        self.mod_akcji = mod_akcji
        self.opis_koszt = opis_koszt
        self.wykonana = False

    def __str__(self):
        return f"{self.imie} | {self.kolor} | klasa {self.klasa} | siła {self.sila}"


class Talia:

    def __init__(self):
        self.karty = []

    def dodaj(self, karta):
        self.karty.append(karta)

    def usun(self, karta):
        self.karty.remove(karta)     

    def wczytaj(self, sciezka, kolor=None):
        nazwa_pliku = sciezka + ".json"
        with open(nazwa_pliku, "r", encoding="utf-8") as plik:
            dane = json.load(plik)
            # print("Liczba rekordów JSON:", len(dane))
            # print("Pierwszy rekord:", dane[0])
        for element in dane:
            if kolor is None or element["kolor"] == kolor:
                karta = Karta(
                    element["id"],
                    element["imie"],
                    element["kolor"],
                    element["klasa"],
                    element["sila"],
                    element["liczba_zdolnosci_walk"],
                    element["walka_sila_bonus"],
                    element["walka_zdolnosc"],
                    element["warunek_wlasny"],
                    element["flaga_sila"],
                    element["wspolpraca_sila"],
                    element["typ_wspolpracy"],
                    element["czy_wspolpraca"],
                    element["warunek_wspolpraca"],
                    element["czy_flaga"],
                    element["zaraza"],
                    element["zabija"],
                    element["koszt"],
                    element["limit_akcji"],
                    element["mod_akcji"],
                    element["opis_koszt"]
                )
                self.dodaj(karta)

    def __len__(self):
        return len(self.karty)

    def __str__(self):
        wynik = ""
        for karta in self.karty:
            wynik += str(karta) + "\n"
        return wynik

    def wybierz_kolor(self, kolor):
        wynik = Talia()
        for karta in self.karty:
            if karta.kolor == kolor:
                wynik.dodaj(karta)
        return wynik

    def potasuj(self):
        random.shuffle(self.karty)

    def pobierz_reke(self, ile):
        ile = min(ile, len(self.karty))
        wynik = Talia()
        for i in range(ile):
            karta = self.karty.pop(0)   #przesuwa wszystkie karty w lewo i usuwa pierwszą kartę z talii - mozliwe do optymalizacji
            wynik.dodaj(karta)
        return wynik

    def przenies(self, inna_talia):
        for karta in inna_talia.karty:
            self.dodaj(karta)
        inna_talia.karty.clear()

    def odloz(self, karta):
        self.dodaj(karta)

    def kopiuj(self, inna_talia):
        for karta in inna_talia.karty:
            self.dodaj(karta)


class StanAreny:
    def __init__(self):
        self.remis_wygrywa_biały = False
        self.remis_wygrywa_czarny = False
        self.bonusy_biały = []
        self.bonusy_czarny = []
        self.zabity_biały = False
        self.zabity_czarny = False

        self.limit_wspolpracy_biały = 0 #zero oznacza bez limitu, 1 oznacza na jedną kartę
        self.limit_wspolpracy_czarny = 0