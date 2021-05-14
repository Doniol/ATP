# Esoterische Programmeertaal:
# "Siekiera, Motyka" door Daniel van Eijk-Bos

# Interpreter
## Turing compleet omdat:
* Het fibonacci-algoritme er in geïmplementeerd kan worden.
* While loops geïmplementeerd zijn en oneindig door kunnen gaan loopen als dit zo geprogrammeerd wordt.
* Er geen limiet is aan de grootte van het geheugen, zolang de hardware dit ondersteunt.
* Conditional branching mogelijk is dankzij de combinatie van if's en functie calls.

## Functionele code stijl
De code van de lexer, parser, interpreter en de nodes zelf is in een functionele stijl geschreven.

## De taal ondersteunt loops
Een voorbeeld hiervan is te vinden in [test_2.txt op regel 59](/test_files/test_2.txt#L59). Om te begrijpen wat daar gebeurt kan je kijken in [test_2.py op regel 8](/test_files/test_2.py#L8).

## Bevat:
* Klassen die gebruik maken van inheritance. Kan gevonden worden in [nodes.py op regel 74](/nodes.py#L74), in de rest van [nodes.py](/nodes.py) wordt hier ook veel gebruik van gemaakt.
* Object printing voor elke klasse.
* Een decorator in [my_lexer.py op regel 103](/my_lexer.py#L103), die toegepast is in [my_lexer.py op regel 131](/my_lexer.py#131).
* Type-annotatie voor elke functie, waarbij elke functie ook extra documentatie over zichzelf bevat.
* Minimaal 3 toepassingen van hogere-order functies, bijvoorbeeld: in [nodes.py op regel 94](/nodex.py#L94), in [my_interpreter.py op regel 37](/my_interpreter.py#L37) en in [my_interpreter.py op regel 83](/my_interpreter.py#L83).

## Functionaliteit:
* De mogelijkheid om meerdere functies per bestand te maken.
* Functieparameters kunnen in de code meegegeven worden wanneer deze functie aan wordt geroepen.
* Functies kunnen andere functies aanroepen, bijvoorbeeld [test_1.txt op regel 71](/test_files/test_1.txt#L71), wat [in deze Python-equivalent op regel 12](/test_files/test_1.py#L12) iets duidelijker staat.
* Functie resultaten kunnen weergeven worden door middel van het uitprinten of returneren ervan. Voorbeelden hiervan zijn [het printen in test_2.txt op regel 114](/test_files/test_2.txt#L114), [de bijbehorende Python-equivalent](/test_files/test_2.py#14) en het daarna returneren van deze data in de regels erna.

## Onderdelen voor eventuele bonuspunten:
* Error messages voor wanneer [een gevraagde variabele of functie niet bestaat](/nodes.py#L21), [niet geïmplementeerde operators](/nodes.py#160) en verscheiden type-errors waaronder [deze](/nodes.py#249).
* [Operatoren voor addities, subtracties, multiplicaties en divisies](/nodes.py#426) voor het aanpassen van bestaande variabelen.
* De mogelijkheid om comments te plaatsen binnen de code, die genegeerd worden door de compiler.

## Extra opmerkingen over de taal
* Ik ben matiger in Pools dan ik mij herriner, als dat wordt gecombineerd met het rijmend proberen te maken van de tekst gaat dat niet goed. Ik raad daarom aan om de tekst niet te vertalen.
* [De woorden in my_lexer.py](/my_lexer.py#L8) waren origineel verzonnen zodat deze óf een directe vertaling van het token-type óf een woord dat erop lijkt waren. Hier heb ik spijt van aangezien deze woorden vrij slecht rijmen, en ook niet allemaal correcte Poolse woorden zijn. Ik zou dit willen veranderen, maar ben bang dat het daar nu iets te laat voor is, dus mij excuses hiervoor.
* In [main.py](/main.py) staat een lijst met wat er mogelijk is binnen functies, en wat daarbuiten mogelijk is.