from typing import List

def foo_bar(pismo: str, liczby: List[int], liczba: int, numer: float):
    pali: int = 0
    szwaba: int = 0
    szwaba = len(liczby)
    wynik: int = 0
    while szwaba > pali:
        szwaba = -1 + szwaba
        powstania: int = liczby[szwaba]
        if powstania > -1:
            wynik = powstania + wynik
    prozno: tuple() = [wynik, pismo]
    return prozno

kurwa: str = ""
pizde: List[int] = [1, -2, 3]
costam: int = 0
tezcos: float = 60.1
resultat: tuple() = []

resultat = foo_bar(kurwa, pizde, costam, tezcos)

print(resultat)