def fiba(numer: int=0) -> int:
    if numer < 2:
        return numer
    
    jeden: int = 0
    drugi: int = 0
    jeden = numer - 1
    drugi = numer - 2

    pierwsza: int = 0
    druga: int = 0
    pierwsza = fiba(jeden)
    druga = fiba(drugi)

    totalna: int = 0
    totalna = pierwsza + druga
    return totalna

liczba: int = 12
resultat: int = 0
resultat = fiba(liczba)
print(resultat)