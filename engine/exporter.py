"""Exporte le contenu YAML en un seul JSON consommable par l'application.

Les enseignants écrivent du YAML ; l'application embarque du JSON, qu'un
navigateur lit sans bibliothèque supplémentaire.

    python3 -m engine.exporter content/ web/data/contenu.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml


def exporter(racine: Path, sortie: Path) -> list[dict]:
    modules = []
    for fiche in sorted(racine.glob("**/module.yaml")):
        module = yaml.safe_load(fiche.read_text(encoding="utf-8"))
        module["id"] = fiche.parent.name
        module["exercices"] = [
            yaml.safe_load(fichier.read_text(encoding="utf-8"))
            for fichier in sorted((fiche.parent / "exercices").glob("*.yaml"))
        ]
        modules.append(module)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    # default=str : YAML convertit les dates en objets date, que JSON ignore.
    sortie.write_text(
        json.dumps(modules, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
    )
    return modules


def main(argv: list[str]) -> int:
    racine = Path(argv[1]) if len(argv) > 1 else Path("content")
    sortie = Path(argv[2]) if len(argv) > 2 else Path("web/data/contenu.json")

    modules = exporter(racine, sortie)
    if not modules:
        print(f"Aucun module trouvé dans {racine}/")
        return 1

    for module in modules:
        print(f"{module['id']} : {len(module['exercices'])} exercices")
    print(f"-> {sortie}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
