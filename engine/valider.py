"""Vérifie que chaque exercice est mécaniquement correct avant publication.

Un corrigé faux qui circule avant un examen coûte la réputation de la
plateforme. Ce contrôle est le garde-fou minimal : pour un exercice de code,
le corrigé de référence doit passer ses propres tests ; pour un QCM, chaque
question doit désigner une réponse existante et être expliquée.

Il ne juge pas la pertinence pédagogique, qui reste à la charge de l'enseignant.

    python3 -m engine.valider content/
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

from engine.corrector import corriger


def _valider_code(exercice: dict) -> list[str]:
    solution = exercice.get("solution")
    if not solution:
        return ["corrigé de référence absent (champ `solution`)"]
    if not exercice.get("tests"):
        return ["aucun test exécutable (champ `tests`)"]

    correction = corriger(exercice, solution)
    if correction.reussi:
        return []
    if correction.message:
        return [correction.message]
    return [
        f"{r.libelle} -> {r.exception or repr(r.obtenu)} (attendu {r.attendu!r})"
        for r in correction.resultats
        if not r.reussi
    ]


def _valider_qcm(exercice: dict) -> list[str]:
    questions = exercice.get("questions") or []
    if not questions:
        return ["aucune question (champ `questions`)"]

    problemes = []
    for numero, question in enumerate(questions, start=1):
        propositions = question.get("propositions") or []
        if len(propositions) < 2:
            problemes.append(f"question {numero} : moins de deux propositions")
            continue

        attendu = question.get("reponse")
        attendu = attendu if isinstance(attendu, list) else [attendu]
        hors_bornes = [
            choix for choix in attendu
            if not isinstance(choix, int) or not 0 <= choix < len(propositions)
        ]
        if hors_bornes:
            problemes.append(f"question {numero} : réponse {hors_bornes} hors des propositions")
        if not question.get("explication"):
            problemes.append(f"question {numero} : explication manquante")

    return problemes


def valider_fichier(chemin: Path) -> list[str]:
    exercice = yaml.safe_load(chemin.read_text(encoding="utf-8"))
    if exercice.get("type") == "qcm":
        return _valider_qcm(exercice)
    return _valider_code(exercice)


def main(argv: list[str]) -> int:
    racine = Path(argv[1]) if len(argv) > 1 else Path("content")
    fichiers = sorted(racine.glob("**/exercices/*.yaml"))

    if not fichiers:
        print(f"Aucun exercice trouvé dans {racine}/")
        return 1

    echecs = 0
    brouillons = 0
    for fichier in fichiers:
        problemes = valider_fichier(fichier)
        if problemes:
            echecs += 1
            print(f"ECHEC {fichier}")
            for probleme in problemes:
                print(f"       {probleme}")
        else:
            exercice = yaml.safe_load(fichier.read_text(encoding="utf-8"))
            if exercice.get("statut") == "brouillon":
                brouillons += 1
                print(f"OK    {fichier}  (brouillon : validation enseignant requise)")
            else:
                print(f"OK    {fichier}")

    print(f"\n{len(fichiers) - echecs}/{len(fichiers)} exercices mécaniquement valides")
    if brouillons:
        print(f"{brouillons} en brouillon, non publiables en l'état")
    return 1 if echecs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
