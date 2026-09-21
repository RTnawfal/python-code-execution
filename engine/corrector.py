"""Correction automatique d'un exercice de code.

Ne dépend que de la bibliothèque standard, afin de tourner tel quel sous
CPython et sous Pyodide (l'interpréteur embarqué dans l'application).
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ResultatTest:
    appel: str
    attendu: object
    obtenu: object = None
    reussi: bool = False
    exception: str | None = None


@dataclass
class Correction:
    reussi: bool
    note: float
    tests: list[ResultatTest] = field(default_factory=list)
    message: str | None = None


def _comparer(obtenu: object, attendu: object, tolerance: float | None) -> bool:
    if tolerance is None:
        return obtenu == attendu
    if isinstance(obtenu, bool) or isinstance(attendu, bool):
        return obtenu == attendu
    if isinstance(obtenu, (int, float)) and isinstance(attendu, (int, float)):
        return abs(obtenu - attendu) <= tolerance
    return obtenu == attendu


def _message_cible(exercice: dict, exception: str) -> str | None:
    for connue in exercice.get("erreurs_frequentes") or []:
        if connue.get("symptome") == exception:
            return connue.get("message")
    return None


def corriger(exercice: dict, code_etudiant: str) -> Correction:
    """Exécute le code de l'étudiant contre les tests de l'exercice.

    Le code est exécuté sans bac à sable : en production il tourne dans
    Pyodide, sur l'appareil de l'étudiant et avec son propre code.
    """
    tests = exercice.get("tests") or []
    espace: dict = {}

    try:
        exec(code_etudiant, espace)
    except Exception as err:
        exception = type(err).__name__
        return Correction(
            reussi=False,
            note=0.0,
            tests=[
                ResultatTest(appel=t["appel"], attendu=t.get("attendu"), exception=exception)
                for t in tests
            ],
            message=_message_cible(exercice, exception) or f"{exception}: {err}",
        )

    resultats = []
    for test in tests:
        resultat = ResultatTest(appel=test["appel"], attendu=test.get("attendu"))
        try:
            resultat.obtenu = eval(test["appel"], espace)
            resultat.reussi = _comparer(resultat.obtenu, resultat.attendu, test.get("tolerance"))
        except Exception as err:
            resultat.exception = type(err).__name__
        resultats.append(resultat)

    if not resultats:
        return Correction(reussi=False, note=0.0, message="Exercice sans test exécutable.")

    reussis = sum(1 for r in resultats if r.reussi)
    note = round(exercice.get("bareme", 0) * reussis / len(resultats), 2)

    message = None
    if reussis < len(resultats):
        echec = next((r for r in resultats if r.exception), None)
        if echec:
            message = _message_cible(exercice, echec.exception)

    return Correction(reussi=reussis == len(resultats), note=note, tests=resultats, message=message)
