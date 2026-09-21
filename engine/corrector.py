"""Correction automatique d'un exercice.

Deux natures d'exercice, imposées par le descriptif officiel du module :
un examen pratique sur machine (code exécuté contre des tests) et un
examen théorique en QCM.

Ne dépend que de la bibliothèque standard, afin de tourner tel quel sous
CPython et sous Pyodide (l'interpréteur embarqué dans l'application).
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Resultat:
    libelle: str
    attendu: object
    obtenu: object = None
    reussi: bool = False
    exception: str | None = None


@dataclass
class Correction:
    reussi: bool
    note: float
    resultats: list[Resultat] = field(default_factory=list)
    message: str | None = None


def corriger(exercice: dict, reponse) -> Correction:
    """Corrige une réponse d'étudiant : du code source, ou des choix de QCM."""
    if exercice.get("type") == "qcm":
        return _corriger_qcm(exercice, reponse)
    return _corriger_code(exercice, reponse)


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


def _agreger(exercice: dict, resultats: list[Resultat], message: str | None = None) -> Correction:
    reussis = sum(1 for r in resultats if r.reussi)
    note = round(exercice.get("bareme", 0) * reussis / len(resultats), 2)
    if message is None and reussis < len(resultats):
        echec = next((r for r in resultats if r.exception), None)
        if echec:
            message = _message_cible(exercice, echec.exception)
    return Correction(reussi=reussis == len(resultats), note=note, resultats=resultats, message=message)


def _corriger_code(exercice: dict, code_etudiant: str) -> Correction:
    """Le code est exécuté sans bac à sable : en production il tourne dans
    Pyodide, sur l'appareil de l'étudiant et avec son propre code."""
    tests = exercice.get("tests") or []
    if not tests:
        return Correction(False, 0.0, message="Exercice sans test exécutable.")

    espace: dict = {}
    try:
        exec(code_etudiant, espace)
    except Exception as err:
        exception = type(err).__name__
        resultats = [
            Resultat(libelle=t["appel"], attendu=t.get("attendu"), exception=exception) for t in tests
        ]
        return _agreger(exercice, resultats, _message_cible(exercice, exception) or f"{exception}: {err}")

    resultats = []
    for test in tests:
        resultat = Resultat(libelle=test["appel"], attendu=test.get("attendu"))
        try:
            resultat.obtenu = eval(test["appel"], espace)
            resultat.reussi = _comparer(resultat.obtenu, resultat.attendu, test.get("tolerance"))
        except Exception as err:
            resultat.exception = type(err).__name__
        resultats.append(resultat)

    return _agreger(exercice, resultats)


def _choix(valeur) -> frozenset:
    """Une réponse de QCM est un indice, ou plusieurs quand la question
    admet plusieurs bonnes propositions."""
    if valeur is None:
        return frozenset()
    if isinstance(valeur, (list, tuple, set, frozenset)):
        return frozenset(valeur)
    return frozenset({valeur})


def _corriger_qcm(exercice: dict, reponses) -> Correction:
    questions = exercice.get("questions") or []
    if not questions:
        return Correction(False, 0.0, message="QCM sans question.")

    reponses = list(reponses or [])
    resultats = []
    for index, question in enumerate(questions):
        attendu = _choix(question.get("reponse"))
        donnee = _choix(reponses[index] if index < len(reponses) else None)
        resultats.append(
            Resultat(
                libelle=question.get("enonce", f"Question {index + 1}"),
                attendu=sorted(attendu),
                obtenu=sorted(donnee),
                reussi=donnee == attendu,
            )
        )

    return _agreger(exercice, resultats)
