from thi.i.ki.informatik1.exercise.tm.components.TuringMachine import TuringMachine
from thi.i.ki.util.input_utils import read_nat, read_operator


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
    n1: int = read_nat("n1 (erste Zahl): ")
    op: str = read_operator(
        f"Operator eingeben [{', '.join(sorted(TuringMachine.OPERATIONS))}]: ",
        allowed=TuringMachine.OPERATIONS
    )
    n2: int = read_nat("n2 (zweite Zahl): ")

    # Turingmaschine erstellen
    tm: TuringMachine = TuringMachine(
        n1=n1,
        op=op,
        n2=n2
    )

    # Turingmaschine initialisieren und ausführen
    result = tm.run_operation()

    # Ergebnis anzeigen
    # print("\n📤 Ergebnis der Turingmaschine")
    # print(f"Eingabe  : {result['input']}")
    # print(f"Operator : {result['operator']}")
    # ...

    print(result)


if __name__ == '__main__':
    main()
