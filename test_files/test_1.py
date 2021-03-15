from typing import List, Tuple, Any
 
def wojna(jedna: int=0, drugiej: int=0) -> int:
    fajki: int = 0
    fajki = jedna - drugiej
    return fajki

def ojciec(liczby: List[int]=[], pierwsze: str="", drugie: str="") -> Tuple[Any]:
    walki: int = 0
    przekleci = liczby[0]
    wien = liczby[1]
    walki = wojna(przekleci, wien)
    walki = walki * 2
    boga: str = ""
    boga = pierwsze + drugie
    bitwa: tuple() = [walki, boga]
    print(bitwa)
    return bitwa

pierwsza: List[int] = [1, 2, 3]
jedno: str = "Good"
drugie: str = "bye"
druga: tuple() = []
druga = ojciec(pierwsza, jedno, drugie)
print(druga)