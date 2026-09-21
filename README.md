
# Plateforme de révision — cours, TD, TP et examens corrigés

Catalogue de modules universitaires marocains construit à partir des
descriptifs officiels accrédités, avec exécution de code et correction
automatique **hors ligne** sur téléphone.

## Décisions prises

- **Accès gratuit.** Le catalogue et les capsules sont ouverts. Le format de
  contenu n'interdit pas d'ajouter plus tard une couche payante (packs
  d'examens, formations) sans rien réécrire.
- **Vidéo hébergée sur YouTube**, référencée par identifiant. Aucun fichier
  vidéo dans le dépôt : l'hébergement propre coûte cher et ne protège rien
  face à l'enregistrement d'écran.
- **Le contenu vit dans des fichiers YAML**, pas dans une base de données.
  Un enseignant doit pouvoir relire et corriger un exercice sans outil.
- **Les tests sont séparés du corrigé rédigé.** Les tests servent à la
  correction automatique dans l'interpréteur embarqué ; le corrigé sert à
  l'explication.
- **Deux natures d'exercice**, imposées par le descriptif officiel du module :
  code exécuté sur machine, et QCM.

## Arborescence

```
content/modules/<module>/
├── module.yaml              fiche issue du descriptif officiel
└── exercices/
    ├── td-*.yaml            énoncé + tests + corrigé
    ├── tp-*.yaml
    └── qcm-*.yaml           questions + réponses + explications
```

## Moteur de correction

`engine/corrector.py` corrige une réponse d'étudiant — du code ou des choix de
QCM — et renvoie une note, le détail par test et un message ciblé lorsque
l'erreur figure dans `erreurs_frequentes`. Il n'utilise que la bibliothèque
standard, donc le même fichier tournera dans l'application via Pyodide, hors
ligne.

`engine/valider.py` contrôle mécaniquement chaque exercice avant publication :
le corrigé de référence doit passer ses propres tests, et chaque question de
QCM doit désigner une réponse existante et être expliquée.

```
python3 -m engine.valider content/
python3 -m unittest discover -p 'test_*.py'
```

## Prototype web

`web/index.html` charge l'interpréteur, exécute `engine/corrector.py` tel quel
et corrige dans le navigateur. Le même fichier servira dans l'application
mobile via une WebView.

```
./scripts/vendor_pyodide.sh              # runtime Pyodide (14 Mo), une fois
python3 -m engine.exporter content/ web/data/contenu.json
python3 -m http.server 8111              # puis ouvrir /web/
```

L'interpréteur est embarqué, jamais chargé depuis un CDN : vérifié en coupant
tout accès réseau hors du serveur local, l'exécution et la correction
continuent de fonctionner. Les 14 Mo ne sont pas versionnés, le script les
reconstitue.

Le champ `statut: brouillon` marque un exercice dont la correction mécanique
passe mais dont la pertinence pédagogique n'a pas été validée par
l'enseignant. Le validateur les signale ; ils ne sont pas publiables en l'état.

Limite connue : une boucle infinie dans le code de l'étudiant bloque
l'exécution. Il faudra une interruption côté application (exécution de
Pyodide dans un *web worker*) avant la mise entre les mains d'étudiants.

## État du contenu

Le module `python-pc-bcg-s2` reprend le descriptif officiel
« Algorithmique et Programmation en Python », S2, Tronc commun Chimie
(PC-BCG), 4 crédits.

Deux réserves à lever avant toute publication :

1. **Version du descriptif.** La source est `descriptif PC BCG 2023-2024.pdf`,
   la plus récente disponible. Elle doit être confrontée à l'accréditation en
   vigueur (champ `descriptif.statut: a_confirmer`).
2. **Droits sur les supports.** Les cours et TD rassemblés par ailleurs
   proviennent du cours d'Andrea G. B. Tettamanzi (Université Nice Sophia
   Antipolis, 2018) et ne peuvent pas être republiés. Les exercices présents
   ici sont originaux et alignés sur le descriptif.
