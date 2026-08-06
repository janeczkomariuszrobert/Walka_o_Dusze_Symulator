import random
import json

class Karta:

    def __init__(self, imie, kolor, klasa, sila, walka_sila_ty, walka_sila_inni,wspolpraca,warunek_inni,flaga,zabija,koszt):
        self.imie = imie
        self.kolor = kolor
        self.klasa = klasa
        self.sila = sila
        self.walka_sila_ty = walka_sila_ty
        self.walka_sila_inni = walka_sila_inni
        self.wspolpraca = wspolpraca
        self.warunek_inni = warunek_inni
        self.flaga = flaga
        self.zabija = zabija
        self.koszt = koszt

    def __str__(self):
        return f"{self.imie} | {self.kolor} | klasa {self.klasa} | siła {self.sila}"


class Talia:

    def __init__(self):
        self.karty = []

    def dodaj(self, karta):
        self.karty.append(karta)

    def usun(self, karta):
        self.karty.remove(karta)     

    def wczytaj(self, nazwa_pliku, kolor=None):
        with open(nazwa_pliku, "r", encoding="utf-8") as plik:
            dane = json.load(plik)
            # print("Liczba rekordów JSON:", len(dane))
            # print("Pierwszy rekord:", dane[0])
        for element in dane:
            if kolor is None or element["kolor"] == kolor:
                karta = Karta(
                    element["imie"],
                    element["kolor"],
                    element["klasa"],
                    element["sila"],
                    element["walka_sila_ty"],
                    element["walka_sila_inni"],
                    element["wspolpraca"],
                    element["warunek_inni"],
                    element["flaga"],
                    element["zabija"],
                    element["koszt"]
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