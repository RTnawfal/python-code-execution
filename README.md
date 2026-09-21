
# Plateforme de révision — cours, TD, TP et examens corrigés

Catalogue de modules universitaires marocains construit à partir des
descriptifs officiels accrédités, avec exécution de code et correction
automatique **hors ligne** sur téléphone.

## Décisions prises

- **Accès gratuit.** Le catalogue et les capsules sont ouverts. Le format de
  contenu ci-dessous n'interdit pas d'ajouter plus tard une couche payante
  (packs d'examens, formations) sans rien réécrire.
- **Vidéo hébergée sur YouTube**, référencée par identifiant. Aucun fichier
  vidéo dans le dépôt : l'hébergement propre coûte cher et ne protège rien
  face à l'enregistrement d'écran.
- **Le contenu vit dans des fichiers YAML**, pas dans une base de données.
  Un enseignant doit pouvoir relire et corriger un exercice sans outil.
- **Les tests sont séparés du corrigé rédigé.** Les tests servent à la
  correction automatique dans l'interpréteur embarqué ; le corrigé sert à
  l'explication. Confondre les deux rend le contenu inexploitable par la
  machine.

## Arborescence

```
content/modules/<module>/
├── module.yaml              fiche issue du descriptif officiel
└── exercices/
    └── td1.yaml             énoncé + tests + corrigé
```

`content/modules/exemple-python/` est un exemple destiné à être remplacé par
un vrai module. Les champs `# TODO` attendent les valeurs exactes du
descriptif accrédité.

## Moteur de correction

`engine/corrector.py` exécute le code de l'étudiant contre les tests de
l'exercice et renvoie une note, le détail par test, et un message ciblé
lorsque l'erreur figure dans `erreurs_frequentes`. Il n'utilise que la
bibliothèque standard, donc le même fichier tournera dans l'application via
Pyodide, hors ligne.

`engine/valider.py` vérifie que le corrigé de référence de chaque exercice
passe ses propres tests. À lancer avant toute publication de contenu :

```
python3 -m engine.valider content/
python3 -m unittest discover -p 'test_*.py'
```

Limite connue : une boucle infinie dans le code de l'étudiant bloque
l'exécution. Il faudra une interruption côté application (exécution de
Pyodide dans un *web worker*) avant la mise entre les mains d'étudiants.

## Ce qui manque pour avancer

Un module réel et complet : descriptif officiel, deux ou trois TD corrigés,
un TP, un sujet d'examen corrigé. Le format ci-dessus sera ajusté sur ce
contenu avant d'écrire la moindre ligne d'application.
