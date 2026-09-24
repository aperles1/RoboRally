# RoboRally

Projet Python réalisé dans le cadre de la licence MIASHS L2.

## Contenu

Le projet contient actuellement les classes de base du jeu :

- `Robot.py` : représentation d'un robot ;
- `Carte.py` : carte et vitesse (priorité du tour de jeu);
- `Case.py` : case de la carte ;
- `Direction.py` : directions possibles ;
- `Drapeau.py` : drapeau associé à une couleur ;
- `TypeCase.py` : types de cases disponibles.

## Lancer le projet

Le projet ne contient pas encore de point d'entrée. Depuis la racine du dépôt,
les modules peuvent être importés dans un script Python avec :

```python
from Robot import Robot
from Direction import Direction

robot = Robot("Robo", 0, 0, Direction.NORD, "bleu")
```

## Contrôler les robots

Pour lancer le plateau graphique :

```bash
python3 Plateau.py
```

Les touches `1` à `4` sélectionnent un robot. Les flèches, ou les touches
`Z`, `Q`, `S`, `D`, le déplacent d'une case lorsque le passage est libre.
La touche `T` lance directement un test visuel : les quatre robots exécutent
une séquence de déplacements sur le plateau et le résultat apparaît dans la
fenêtre.

## Travail collaboratif

Avant de commencer une modification :

```bash
git pull
```

Après avoir travaillé :

```bash
git add .
git commit -m "Décrire la modification"
git push
```

Pour éviter les conflits, créez de préférence une branche par fonctionnalité
et proposez une pull request avant de fusionner dans `main`.
