"""
Zentrale Type-Definitionen für das Policy-System.

ZWECK
-----
Definiert wiederverwendbare Type-Aliase für alle Komponenten.
Ermöglicht konsistente Typisierung über alle Module hinweg.

VERWENDUNG
----------
>>> from thi.i.ki.util.policy.types import State, Action, Cost
>>> def my_function(state: State, action: Action) -> Cost:
...     return 1
"""

from typing import TypeAlias, Hashable, Iterable, Callable

# Kern-Typen
State: TypeAlias = Hashable
"""
Zustand im Problem-State-Space.
Muss hashable sein für effiziente Lookup in Dictionaries.
"""

Action: TypeAlias = Hashable
"""
Aktion, die einen Zustand in einen anderen überführt.
Muss hashable sein für deterministische Speicherung.
"""

Cost: TypeAlias = int
"""
Kosten einer Aktion oder Distanz zwischen Zuständen.
Nicht-negativ, ganzzahlig.
"""

# Callback-Typen
IsGoalFunc: TypeAlias = Callable[[State], bool]
"""
Prüft, ob ein Zustand ein Zielzustand ist.
"""

SuccessorsFunc: TypeAlias = Callable[[State], Iterable[tuple[State, Action, Cost]]]
"""
Liefert alle Nachfolger eines Zustands als (next_state, action, cost).
Wird lazy aufgerufen (on-demand expansion).
"""

PredecessorsFunc: TypeAlias = Callable[[State], Iterable[tuple[State, Action, Cost]]]
"""
Liefert alle Vorgänger eines Zustands als (prev_state, action, cost).
Optional, nur für Backward-Suche benötigt.
"""