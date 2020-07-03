# Localization project 

# Project description
Projekt bazuje na zadaniu 7, w którym trzeba było obliczyć rozkład prawdopodobieństwa lokalizacji robota. Tym razem jednak nie jest znana orientacja robota, którą także trzeba uwzględnić w obliczeniach. Założenia rozpatrywanego świata:
- Robot nie zawsze poprawnie wykonuje manewr obracania i jazdy do przodu. Istnieje szansa ϵm=0.05, że robot pozostanie w tym samym miejscu w przypadku, gdy ostatnią komeną było forward lub się nie obróci w przypadku, gdy ostatnią komendą było turnleft lub turnright.
- Czujniki robota zwracają listę kierunków względem robota, w których zostały wykryte przeszkody, np. ['fwd', 'right'] oznacza, że przeszkody zostały wykryte na wprost i na prawo od robota (patrząc w aktualnym kierunku robota). Niestety, czujniki te nie są perfekcyjne i czasami zwracają błędne pomiary. Istnieje szansa ϵs=0.1, że sensor zwróci błędny pomiar, tzn. wykryje obecność przeszkody, jeśli jej tam nie ma lub nie wykryje przeszkody mimo jej obecności.
- Możesz także wykorzystać wartość bump otrzymaną w zmiennej percept, żeby poprawić dokładność lokalizacji.

## Tasks
- Napisanie kodu odpowiedzialnego za obliczanie rozkładu lokalizacji robota.
- Modyfikacja heurystyki poruszającej robotem, aby jak najbardziej przyspieszyć zbieżność algorytmu. Robot powinien wybierać takie akcje, które dostarczą mu jak najwięcej informacji.
