# RoboRally

Projet Python de RoboRally avec affichage graphique `pygame`.

## Lancer le projet

```bash
python3 main.py
```

La partie se déroule automatiquement sur un plateau de 12 x 12 cases avec
deux robots bleus et deux robots rouges.

Pour entraîner l'IA sans afficher pygame :

```bash
python3 main.py --entrainer 1000 --modele modele_perceptron.json
```

Le fichier JSON est chargé au début s'il existe, puis remplacé avec les poids
mis à jour à la fin. L'entraînement peut donc être repris sur plusieurs
exécutions. Les transitions détaillées ne sont pas conservées, car
l'apprentissage est effectué immédiatement après chaque carte ; les poids
sauvegardés constituent l'état utile pour continuer.

## Fichiers du projet

- `main.py` : lance la partie et la boucle graphique ;
- `Jeu/Jeu.py` : contient les règles, déplacements, tirs et victoires ;
- `Entitées/Robot.py` : définit les robots, leurs PV, bonus et orientations ;
- `Perceptron/ControleurRobot.py` : contrôle les décisions de l'IA et le choix des cartes ;
- `Perceptron/ModelePerceptron.py` : définit le modèle, sa formule et son apprentissage ;
- `Perceptron/Caracteristiques.py` : extrait les données numériques du jeu pour le modèle ;
- `Perceptron/Entrainement.py` : fait jouer plusieurs parties et entraîne l'IA avec des récompenses ;
- `Jeu/Plateau.py` : crée et affiche le plateau avec pygame ;
- `Entitées/Case.py` : définit les cases, terrains et murs ;
- `Entitées/TypeCase.py` : liste les types de cases ;
- `Entitées/Direction.py` : définit les directions cardinales ;
- `Entitées/Carte.py` : définit les cartes de déplacement ;
- `Entitées/Drapeau.py` : définit les drapeaux et leurs captures ;
- `images/` : contient les images utilisées pour l'affichage ;
- `README.md` : présente le projet et son lancement.