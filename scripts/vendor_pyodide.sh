#!/usr/bin/env sh
# Récupère le runtime Pyodide et l'installe dans web/vendor/pyodide/.
#
# L'application doit fonctionner sans réseau : l'interpréteur est embarqué,
# jamais chargé depuis un CDN. Ces fichiers ne sont pas versionnés (voir
# .gitignore) ; ce script les reconstitue à l'identique.

set -eu

VERSION="${1:-0.26.4}"
RACINE="$(cd "$(dirname "$0")/.." && pwd)"
CIBLE="$RACINE/web/vendor/pyodide"
TRAVAIL="$(mktemp -d)"
trap 'rm -rf "$TRAVAIL"' EXIT

echo "Téléchargement de Pyodide $VERSION depuis npm..."
curl -sSfL "https://registry.npmjs.org/pyodide/-/pyodide-$VERSION.tgz" -o "$TRAVAIL/pyodide.tgz"
tar -xzf "$TRAVAIL/pyodide.tgz" -C "$TRAVAIL"

mkdir -p "$CIBLE"
for fichier in pyodide.js pyodide.asm.js pyodide.asm.wasm python_stdlib.zip pyodide-lock.json; do
  cp "$TRAVAIL/package/$fichier" "$CIBLE/$fichier"
done

echo "Installé dans web/vendor/pyodide/ :"
du -sh "$CIBLE"
