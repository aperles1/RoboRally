"""
Auteur : Perles Alexis
Date de dernière modification : 22/10/2026
Contenu : Entraîne un perceptron sur plusieurs parties de RoboRally.
"""

from Perceptron.ControleurRobot import ControleurRobot


class EntraineurPerceptron:
    """Fait jouer des parties et ajuste un perceptron avec des récompenses différées."""

    HORIZON_RECOMPENSE = 3

    def __init__(
        self,
        creer_jeu,
        controleur=None,
        nombre_max_tours=100,
        facteur_actualisation=0.9,
    ):
        """Construit un entraîneur de parties sans interface graphique.

        - Description : mémorise une fabrique de parties et le modèle à entraîner.
        - Prérequis : `creer_jeu` doit retourner un objet `Jeu` ou un couple
          dont le premier élément est un objet `Jeu`.
        - Arguments : `creer_jeu` (`callable`), `controleur`
          (`ControleurRobot` ou `None`), `nombre_max_tours` (`int` positif),
          `facteur_actualisation` (`float` entre 0 et 1).
        - Retourne : rien (`None`).
        """
        if nombre_max_tours <= 0:
            raise ValueError("Le nombre maximal de tours doit être positif.")
        if not 0 < facteur_actualisation <= 1:
            raise ValueError("Le facteur d'actualisation doit être entre 0 et 1.")
        self.creer_jeu = creer_jeu
        self.controleur = controleur or ControleurRobot()
        self.nombre_max_tours = nombre_max_tours
        self.facteur_actualisation = float(facteur_actualisation)

    def jouer_partie(self):
        """Joue une partie complète et entraîne le perceptron avec un horizon de trois cartes.

        - Description : sélectionne les cartes, joue chaque carte obligatoire
          et entraîne le modèle sur des retours de trois actions successives.
        - Prérequis : la fabrique doit produire une partie réinitialisée.
        - Arguments : aucun.
        - Retourne : statistiques de la partie (`dict[str, float]`).
        """
        resultat = self.creer_jeu()
        jeu = resultat[0] if isinstance(resultat, tuple) else resultat
        nombre_cartes = 0
        recompense_totale = 0.0
        transitions = []

        for _ in range(self.nombre_max_tours):
            if jeu.equipe_gagnante is not None:
                break
            if not jeu.cartes_du_tour:
                self.controleur.preparer_tour(jeu)
            actuelle = jeu.carte_actuelle()
            if actuelle is None:
                break
            robot, carte = actuelle
            caracteristiques = self.controleur.extraire_caracteristiques(
                jeu, robot, carte
            )
            etat_avant = self._capturer_etat(jeu)
            jeu.jouer_carte_actuelle(
                self.controleur.doit_jouer_carte(jeu, robot, carte)
            )
            recompense = self.calculer_recompense(jeu, etat_avant, robot)
            transitions.append((caracteristiques, recompense))
            if len(transitions) == self.HORIZON_RECOMPENSE:
                self._mettre_a_jour_premiere_transition(transitions)
            nombre_cartes += 1
            recompense_totale += recompense

        self._vider_transitions(transitions)
        return {
            "cartes_jouees": nombre_cartes,
            "recompense": recompense_totale,
            "equipe_gagnante": jeu.equipe_gagnante,
        }

    def _mettre_a_jour_premiere_transition(self, transitions):
        """Met à jour la première action avec trois récompenses successives."""
        cible = sum(
            self.facteur_actualisation ** index * recompense
            for index, (_, recompense) in enumerate(transitions)
        )
        caracteristiques, _ = transitions.pop(0)
        self.controleur.perceptron.mettre_a_jour(caracteristiques, cible)

    def _vider_transitions(self, transitions):
        """Entraîne les dernières actions avec leur retour disponible."""
        while transitions:
            cible = sum(
                self.facteur_actualisation ** index * recompense
                for index, (_, recompense) in enumerate(transitions)
            )
            caracteristiques, _ = transitions.pop(0)
            self.controleur.perceptron.mettre_a_jour(caracteristiques, cible)

    def entrainer(self, nombre_parties):
        """Enchaîne plusieurs parties avec le même perceptron.

        - Description : réinitialise une partie à chaque épisode et conserve
          les statistiques de chaque partie.
        - Prérequis : `nombre_parties` doit être un entier positif.
        - Arguments : `nombre_parties` (`int`).
        - Retourne : résultats des épisodes (`list[dict[str, float]]`).
        """
        if nombre_parties <= 0:
            raise ValueError("Le nombre de parties doit être positif.")
        return [self.jouer_partie() for _ in range(nombre_parties)]

    def entrainer_et_sauvegarder(self, nombre_parties, chemin_modele):
        """Entraîne le modèle puis sauvegarde ses paramètres et les résultats.

        - Description : exécute les épisodes et écrit les poids appris dans le
          fichier JSON indiqué. Les statistiques sont conservées en mémoire.
        - Prérequis : `nombre_parties` doit être positif et le chemin accessible.
        - Arguments : `nombre_parties` (`int`), `chemin_modele` (`str` ou `Path`).
        - Retourne : résultats des épisodes (`list[dict]`).
        """
        resultats = self.entrainer(nombre_parties)
        self.controleur.perceptron.sauvegarder(chemin_modele)
        return resultats

    @staticmethod
    def _capturer_etat(jeu):
        """Capture les données utiles avant l'exécution d'une carte.

        - Description : mémorise les positions, les PV et les captures pour
          mesurer les conséquences du coup joué.
        - Prérequis : `jeu` doit posséder des robots et des drapeaux.
        - Arguments : `jeu` (`Jeu`).
        - Retourne : état instantané (`dict`).
        """
        return {
            "robots": {
                id(robot): (robot.x, robot.y, robot.pv, robot.est_detruit)
                for robot in jeu.robots
            },
            "drapeaux": tuple(
                drapeau.equipe_capture for drapeau, _, _ in jeu.drapeaux
            ),
        }

    @classmethod
    def calculer_recompense(cls, jeu, etat_avant, robot):
        """Calcule la récompense immédiate produite par une carte.

        - Description : récompense un déplacement, une capture et les dégâts
          infligés, tout en pénalisant les dégâts reçus et la destruction.
        - Prérequis : `etat_avant` doit provenir de `_capturer_etat`.
        - Arguments : `jeu` (`Jeu`), `etat_avant` (`dict`), `robot` (`Robot`).
        - Retourne : récompense numérique (`float`).
        """
        ancien_x, ancien_y, anciens_pv, etait_detruit = etat_avant["robots"][id(robot)]
        recompense = 0.0
        if (robot.x, robot.y) != (ancien_x, ancien_y):
            recompense += 0.2
        else:
            recompense -= 0.05
        recompense += 2.0 * (anciens_pv - robot.pv)
        for autre in jeu.robots:
            if autre is robot:
                continue
            anciens_pv_ennemi = etat_avant["robots"][id(autre)][2]
            recompense += 2.0 * (anciens_pv_ennemi - autre.pv)
        if robot.est_detruit and not etait_detruit:
            recompense -= 10.0
        recompense += 15.0 * sum(
            avant is None and drapeau.equipe_capture is not None
            for avant, (drapeau, _, _) in zip(
                etat_avant["drapeaux"], jeu.drapeaux
            )
        )
        recompense += 8.0 * sum(
            not etat_avant["robots"][id(autre)][3] and autre.est_detruit
            for autre in jeu.robots
            if autre is not robot
        )
        if jeu.equipe_gagnante == robot.couleur:
            recompense += 100.0
        elif jeu.equipe_gagnante is not None:
            recompense -= 100.0
        return recompense
