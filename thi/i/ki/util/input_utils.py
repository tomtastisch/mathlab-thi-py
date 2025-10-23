#!/usr/bin/env python3
"""input_utils – Hilfsfunktionen für Benutzereingaben

Dieses Modul stellt Hilfsfunktionen zur Validierung und Verarbeitung von
Benutzereingaben bereit.
"""


def read_operator(
        prompt: str,
        allowed: set[str] | tuple[str, ...]
) -> str:

    """Liest einen gültigen Operator ('+' oder '-') ein."""
    while True:
        op = input(prompt).strip()
        if op in allowed:
            return op
        print(f"Ungültiger Operator. Erlaubt: {', '.join(allowed)}")


def read_nat(prompt: str) -> int:
    """Liest eine natürliche Zahl von der Standardeingabe.

    Diese Funktion fordert den Benutzer wiederholt zur Eingabe auf, bis eine
    gültige natürliche Zahl (0, 1, 2, ...) eingegeben wird.

    Args:
        prompt: Die Eingabeaufforderung, die dem Benutzer angezeigt wird.

    Returns:
        Die eingegebene natürliche Zahl als int.

    Examples:
        >>> n = read_nat("Bitte eine Zahl eingeben: ")
        Bitte eine Zahl eingeben: abc
        Bitte eine natürliche Zahl (0,1,2,...) eingeben.
        Bitte eine Zahl eingeben: 42
        >>> print(n)
        42
    """
    while True:
        s = input(prompt).strip()
        if s.isdigit():
            return int(s)

        print("Bitte eine natürliche Zahl (0,1,2,...) eingeben.")
