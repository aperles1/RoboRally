# RoboRally

Auteur : Perles Alexis
Date de dernière modification : 10/11/2026
Contenu : Présente l'architecture et les commandes du projet.

Jeu Python avec affichage `pygame`, sur un plateau de 12 x 12 cases.

## Arborescence

```text
entites/    directions, cartes, cases, drapeaux et robots
regles/     jeu, déplacements, tirs et génération du plateau
affichage/  dessin pygame
ia/         perceptron, réseau neuronal, caractéristiques, simulation et entraînement
scripts/    vérification, entraînement et évaluation
modeles/    modèles JSON du perceptron et du réseau neuronal
images/     images utilisées par pygame
main.py     lancement du jeu
```

Les dépendances suivent un seul sens : `entites <- regles <- ia <- scripts`.

## Commandes

Lancer le jeu graphique :

```bash
python3 main.py
```

Visualiser une partie avec le réseau neuronal entraîné :

```bash
python3 main.py --modele modeles/modele_reseau.json
```

Entraîner 200 parties puis sauvegarder le modèle :

```bash
python3 scripts/entrainer.py
```

L'entraînement peut aussi être lancé depuis `main.py` :

```bash
python3 main.py --entrainer 200 --modele modeles/modele_perceptron.json
```

Entraîner le réseau neuronal :

```bash
python3 main.py --entrainer 1000 --reseau \
  --modele modeles/modele_reseau.json --evaluation 400
```

Le réseau utilise 11 caractéristiques, une couche cachée de 8 neurones ReLU
et une sortie qui produit le score de chaque carte.
