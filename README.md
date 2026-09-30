# RoboRally

Projet Python de RoboRally avec affichage graphique `pygame`.

## Lancer le projet

```bash
python3 main.py
```

La partie se déroule automatiquement sur un plateau de 12 x 12 cases avec
deux robots bleus et deux robots rouges.

## Fichiers du projet

- `main.py` : lance la partie et la boucle graphique ;
- `Jeu.py` : contient les règles, déplacements, tirs et victoires ;
- `Robot.py` : définit les robots, leurs PV, bonus et orientations ;
- `Perceptron.py` : contrôle les décisions de l'IA et le choix des cartes ;
- `Plateau.py` : crée et affiche le plateau avec pygame ;
- `Case.py` : définit les cases, terrains et murs ;
- `TypeCase.py` : liste les types de cases ;
- `Direction.py` : définit les directions cardinales ;
- `Carte.py` : définit les cartes de déplacement ;
- `Drapeau.py` : définit les drapeaux et leurs captures ;
- `images/` : contient les images utilisées pour l'affichage ;
- `README.md` : présente le projet et son lancement.
