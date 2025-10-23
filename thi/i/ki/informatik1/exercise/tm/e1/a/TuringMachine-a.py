from typing import Literal, cast

def main() -> None:
    """
    Führt die unäre Turingmaschine im interaktiven Modus aus.
    Fordert Eingaben vom Benutzer ab und zeigt das Ergebnis sowie
    Ablaufdetails nach der Operation an.
    """
    print("🧮 Willkommen zur unären Turing-Rechenmaschine")
    print("Erlaubte Operatoren: '+' (Addition), '-' (Subtraktion)")
    print("Hinweis: Nur natürliche Zahlen ≥ 0 erlaubt.\n")

    # Eingabe erfassen
    n1 = read_nat("n1 (erste Zahl): ")
    op_raw = read_operator("Operator (+ oder -): ", allowed={"+", "-"})
    n2 = read_nat("n2 (zweite Zahl): ")

    op = cast(Literal["+", "-"], op_raw)

    # Turingmaschine initialisieren und ausführen
    tm = TuringMachine(n1=n1, op=op, n2=n2)
    result = tm.run_operation()

    # Ergebnis anzeigen
    print("\n📤 Ergebnis der Turingmaschine")
    print(f"Eingabe  : {result['input']}")
    print(f"Operator : {result['operator']}")
    print(f"Ausgabe  : {result['output']}")
    print(f"Zustand  : {result['state']}")

    print(result)


if __name__ == '__main__':
    main()
