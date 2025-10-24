"""
Sammlung von Such-Algorithmen für Policy-Berechnung.

ZWECK
-----
Modulare, austauschbare Such-Algorithmen.
Jeder Algorithmus ist eine reine Funktion: Inputs → (Distances, Parents).

VERFÜGBARE ALGORITHMEN
----------------------
- zero_one_bfs: Optimal für Graphen mit Kosten 0 oder 1
- dijkstra: Für beliebige nicht-negative Kosten (zukünftig)
- astar: Heuristische Suche (zukünftig)

DESIGN
------
- Stateless: Keine Klassen, nur pure functions
- Pluggable: Neue Algorithmen einfach hinzufügbar
- Testable: Isoliert testbar ohne Dependencies
"""

from .zero_one_bfs import (
    zero_one_bfs_backward,
    zero_one_bfs_forward,
)

__all__ = [
    "zero_one_bfs_backward",
    "zero_one_bfs_forward",
]