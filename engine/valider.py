"""Vérifie que le corrigé de référence de chaque exercice passe ses propres tests.

Un corrigé faux qui circule avant un examen coûte la réputation de la
plateforme : aucun exercice ne doit être publié sans passer ce contrôle.

    python3 -m engine.valider content/
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

from engine.corrector import corriger


def valider_fichier(chemin: Path) -> list[str]:
    exercice = yaml.safe_load(chemin.read_text(encoding="utf-8"))

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
        f"{r.appel} -> {r.exception or repr(r.obtenu)} (attendu {r.attendu!r})"
        for r in correction.tests
        if not r.reussi
    ]


def main(argv: list[str]) -> int:
    racine = Path(argv[1]) if len(argv) > 1 else Path("content")
    fichiers = sorted(racine.glob("**/exercices/*.yaml"))

    if not fichiers:
        print(f"Aucun exercice trouvé dans {racine}/")
        return 1

    echecs = 0
    for fichier in fichiers:
        problemes = valider_fichier(fichier)
        if problemes:
            echecs += 1
            print(f"ECHEC {fichier}")
            for probleme in problemes:
                print(f"       {probleme}")
        else:
            print(f"OK    {fichier}")

    print(f"\n{len(fichiers) - echecs}/{len(fichiers)} exercices valides")
    return 1 if echecs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
