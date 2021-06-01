# Esoterische Programmeertaal:
# "Siekiera, Motyka" door Daniel van Eijk-Bos

# Interpreter & Compiler
## Turing compleet omdat:
* Het fibonacci-algoritme er in geïmplementeerd kan worden.
* While loops geïmplementeerd zijn en oneindig door kunnen gaan loopen als dit zo geprogrammeerd wordt.
* Er geen limiet is aan de grootte van het geheugen, zolang de hardware dit ondersteunt.
* Conditional branching mogelijk is dankzij de combinatie van if's en functie calls.

## Functionele code stijl
De code van de lexer, parser, interpreter, compiler en de nodes zelf is in een functionele stijl geschreven.

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

## Gebruiksaanwijzing
1. Execute de code van main.py.
2. Kies een van de test-files om te gebruiken. (Deze kunnen in het mapje test_files gevonden worden, hier staat niet alleen de originele "Siekiera, Motyka" code, maar ook de Python equivalent.) Tests 1 en 2 werken alleen voor de interpreter, tests 3 en 4 werken op beide de interpreter en de compiler.
3. Kies of de geselecteerde test-code ge-interpret of ge-compiled moet worden. Voor het interpreten zie Stap 4, voor het compilen zie Stap 5 en wat daarna volgt.
4. Als de code ge-interpret moet worden, zie je de resultaten van eventuele print-functies direct in de terminal verschijnen. Nu ben je klaar met het interpreten van de code.
5. Als de code ge-compiled moet worden, verschijnt er een bestand genaamd main.asm met de gecompilede .asm code erin.
6. Deze code kan op de Arduino Due gezet worden door middel van de [Makefile](/Makefile) die erbij zit. Dit doe je door "make run" aan te roepen binnen de map met beiden de Makefile en main.asm. (Ik had hier zelf wat problemen met het verbinden met de Due (op Linux), en moest ook nog [deze code](/Makefile#2) uitvoeren.)
7. Als de code correct geupload is naar de Due, zullen de resultaten van de code (eventuele print functies) weergegeven worden in de terminal waar "make run" uitgevoerd is. Nu ben je klaar met het compilen, uploaden en het executen van de code.

## Extra opmerkingen over de taal
* Ik ben matiger in Pools dan ik mij herriner, als dat wordt gecombineerd met het rijmend proberen te maken van de tekst gaat dat niet goed. Ik raad daarom aan om de tekst niet te vertalen.
* [De woorden in my_lexer.py](/my_lexer.py#L8) waren origineel verzonnen zodat deze óf een directe vertaling van het token-type óf een woord dat erop lijkt waren. Hier heb ik spijt van aangezien deze woorden vrij slecht rijmen, en ook niet allemaal correcte Poolse woorden zijn. Ik zou dit willen veranderen, maar ben bang dat het daar nu iets te laat voor is, dus mij excuses hiervoor.
* In [main.py](/main.py) staat een lijst met wat er mogelijk is binnen functies, en wat daarbuiten mogelijk is.
* De inspiratie voor de taal komt [hiervandaan](https://www.youtube.com/watch?v=kPYdzFiW2SQ).
