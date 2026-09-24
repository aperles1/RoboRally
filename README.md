# RoboRally

Projet Python de RoboRally avec un plateau graphique et quatre robots.

## Organisation

- `TypeCase.py` : enum unique des terrains. Une `Case` ne possède qu'un seul
  `TypeCase` ;
- `Case.py` : case, murs, terrain et direction des tapis roulants ;
- `Robot.py` : état d'un robot, déplacements, dégâts et effets des bonus ;
- `Carte.py` et `Direction.py` : cartes de programmation, vitesses et création
  des cartes aléatoires ;
- `Jeu.py` : règles, pioche, ordre des priorités, déplacements, tapis,
  trous, poussées, tirs et captures de drapeaux ;
- `Plateau.py` : génération du plateau et rendu pygame ;
- `main.py` : lancement de la partie automatique.

## Lancer

```bash
python3 main.py
```

La partie se joue sur un plateau de 12 x 12 cases. Deux robots bleus
commencent dans le coin supérieur gauche et deux robots rouges dans le coin
inférieur droit. Le programme actuel affiche le plateau et les robots sans
exécuter de cartes ni de déplacements.

Les équipiers ne se tirent pas dessus. Une case possède un seul type défini
dans `TypeCase.py`, les trous détruisent les robots et les tapis les déplacent
case par case. Un bonus donne soit une attaque infligeant 2 dégâts
supplémentaires au prochain tir, soit un bouclier qui bloque deux tirs. Les
bonus et les réparations sont consommés après utilisation. Les bonus,
réparations, murs et trous sont dessinés directement par pygame, sans
dépendre d'images externes.

Les commentaires présents dans `Jeu.py` et `Plateau.py` expliquent les
parties les plus difficiles : poussée en chaîne, ordre des cartes, effets de
terrain et séparation entre règles et interface.
