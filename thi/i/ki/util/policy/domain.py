"""
Protocol-Definition für Domains.

ZWECK
-----
Jede Domain muss dieses Protocol implementieren.
Ermöglicht Type-Checking und klare Schnittstellen ohne Vererbung.

DESIGN
------
- Protocol statt ABC: Duck-Typing mit Type-Safety
- Single Method: Nur build_skeleton() erforderlich
- Keine Basisklasse: Domains bleiben unabhängig
"""

from typing import Protocol
from .skeleton import GraphSkeleton


class Domain(Protocol):
    """
    Protocol für alle Problem-Domains.

    ZWECK
    -----
    Definiert einheitliche Schnittstelle für:
    - Turing Machine Sequenzen
    - Graph-Probleme
    - Beliebige zukünftige Domains

    SCHNITTSTELLE
    -------------
    build_skeleton() : GraphSkeleton
        Erzeugt die Graph-Repräsentation des Problems.
        Diese Methode ist die EINZIGE Anforderung an Domains.

    ERWEITERBARKEIT
    ---------------
    Neue Domains implementieren einfach diese Methode:

        class MyDomain:
            def build_skeleton(self) -> GraphSkeleton:
                return GraphSkeleton(
                    is_goal=lambda s: s == self.target,
                    successors=lambda s: [(s+1, "inc", 1)],
                    initial_states=[self.start],
                    direction="forward"
                )

    Keine Vererbung nötig, kein Boilerplate.

    BEISPIEL
    --------
    >>> class SimpleDomain:
    ...     def build_skeleton(self) -> GraphSkeleton:
    ...         return GraphSkeleton(...)
    >>> domain: Domain = SimpleDomain()  # Type-Check erfolgt
    """

    def build_skeleton(self) -> GraphSkeleton:
        """
        Erzeugt GraphSkeleton für dieses Problem.

        RÜCKGABE
        --------
        GraphSkeleton
            Problem-Repräsentation mit allen nötigen Callbacks und Metadata.

        VORAUSSETZUNGEN
        ---------------
        - Skeleton muss valid sein (siehe GraphSkeleton.validate())
        - Callbacks müssen deterministisch sein
        - States müssen hashable sein
        """
        ...