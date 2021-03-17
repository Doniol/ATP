# Esoterische Programmeertaal:
# "Siekiera, Motyka" door Daniel van Eijk-Bos

## Turing compleet omdat:
* Het fibonacci-algoritme er in geïmplementeerd kan worden.
* While loops geïmplementeerd zijn en oneindig door kunnen gaan loopen als dit zo geprogrammeerd wordt.
* Er geen limiet is aan de grootte van het geheugen, zolang de hardware dit ondersteunt.
* Conditional branching mogelijk is dankzij de combinatie van if's en functie calls.

## Functionele code stijl
De code van de lexer, parser, interpreter en de nodes zelf is in een functionele stijl geschreven.

## De taal ondersteunt loops
Een voorbeeld hiervan is te vinden in [test_2.txt](/test_files/test_2.txt#L59) op regel 59. Om te begrijp wat daar gebeurt kan je kijken in [test_2.py](/test_files/test_2.py#L8) op regel 8.

## Bevat:
* Klassen die gebruik maken van inheritance. Kan gevonden worden in [nodes.py](/nodes.py) op regel 74, in de rest van [nodes.py](/nodes.py) wordt hier ook veel gebruik van gemaakt.
* Object printing voor elke klasse.
