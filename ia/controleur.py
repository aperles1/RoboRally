from itertools import combinations

from entites.carte import tirer_main
from entites.direction import ActionCarte
from ia.caracteristiques import (
    NOMS_CARACTERISTIQUES,
    extraire_caracteristiques,
    preparer_contexte,
)
from ia.perceptron import Perceptron
from ia.reseau_neurones import ReseauNeurones
from ia.simulation import _simuler, combinaison, prochaine_action


POIDS_INITIAUX = (
    3.0, 2.0, -1.0, 1.0, -0.5, 0.3,
    2.0, -2.0, -1.0, -1.5, -2.0,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0,
)
if len(POIDS_INITIAUX) != len(NOMS_CARACTERISTIQUES):
    raise ValueError("Les poids initiaux ne correspondent pas aux caractéristiques.")


class ControleurRobot:
    def __init__(self, perceptron=None, reseau=False):
        """
        Role : initialise un contrôleur de robot.
        Entrees : perceptron (Perceptron ou ReseauNeurones) ou aucune, reseau (booléen)
        Sorties : aucune
        Pré-requis : le modèle doit avoir les caractéristiques attendues
        """
        if perceptron is not None and reseau:
            raise ValueError("Un modèle fourni ne peut pas être remplacé.")
        if perceptron is not None:
            self.perceptron = perceptron
        elif reseau:
            self.perceptron = ReseauNeurones(
                nombre_entrees=len(NOMS_CARACTERISTIQUES)
            )
        else:
            self.perceptron = Perceptron(POIDS_INITIAUX)
        self.epsilon = 0.0
        self._contextes_tour = {}
        if isinstance(self.perceptron, ReseauNeurones):
            nombre_entrees = self.perceptron.nombre_entrees
        else:
            nombre_entrees = len(self.perceptron.poids)
        if nombre_entrees == 11:
            self.perceptron.poids.extend([0.0] * 11)
            nombre_entrees = len(self.perceptron.poids)
        if nombre_entrees != len(NOMS_CARACTERISTIQUES):
            raise ValueError("Le modèle JSON n'utilise pas les bonnes caractéristiques.")

    def extraire_caracteristiques(self, jeu, robot, carte, cartes_precedentes=()):
        """
        Role : extrait les caractéristiques d’une carte.
        Entrees : jeu (Jeu), robot (Robot), carte (Carte), cartes_precedentes (itérable)
        Sorties : liste de caractéristiques
        Pré-requis : le jeu et le robot doivent être valides
        """
        actions = [carte_precedente.action for carte_precedente in cartes_precedentes]
        return extraire_caracteristiques(
            jeu, robot, carte.action, carte.vitesse, actions,
            self._contextes_tour.get(id(robot)),
        )

    def score_carte(self, jeu, robot, carte, cartes_precedentes=()):
        """
        Role : calcule le score d’une carte.
        Entrees : jeu (Jeu), robot (Robot), carte (Carte), cartes_precedentes (itérable)
        Sorties : flottant
        Pré-requis : la carte doit être compatible avec le contrôleur
        """
        if self._rotation_interdite(robot, carte):
            return -1000.0
        return self.perceptron.calculer(
            self.extraire_caracteristiques(
                jeu, robot, carte, cartes_precedentes
            )
        )

    def cartes_avec_scores(self, jeu, robot):
        """
        Role : associe un score à chaque carte du robot.
        Entrees : jeu (Jeu), robot (Robot)
        Sorties : liste de couples carte-score
        Pré-requis : le robot doit avoir une main
        """
        cartes = sorted(
            jeu.mains.get(id(robot), []),
            key=lambda carte: carte.vitesse,
            reverse=True,
        )
        resultat = []
        precedentes = []
        contexte = self._contextes_tour.get(id(robot))
        for carte in cartes:
            resultat.append((
                carte,
                self.perceptron.calculer(extraire_caracteristiques(
                    jeu, robot, carte.action, carte.vitesse,
                    [carte_precedente.action for carte_precedente in precedentes],
                    contexte,
                )),
            ))
            precedentes.append(carte)
        return resultat

    def tirer_et_choisir_cartes(self, jeu, robot):
        """
        Role : tire et sélectionne les meilleures cartes.
        Entrees : jeu (Jeu), robot (Robot)
        Sorties : liste de cartes
        Pré-requis : le jeu doit fournir une source aléatoire
        """
        cartes = tirer_main(jeu.aleatoire, jeu.CARTES_A_TIRER)
        choix = min(jeu.CARTES_PAR_ROBOT, len(cartes))
        if self.epsilon and jeu.aleatoire.random() < self.epsilon:
            main = jeu.aleatoire.sample(cartes, choix)
            return sorted(main, key=lambda carte: carte.vitesse, reverse=True)
        meilleure_main = max(
            # On évalue les combinaisons plutôt que chaque carte isolée :
            # l'ordre et les actions précédentes influencent la main complète.
            combinations(cartes, choix),
            key=lambda main: self._score_main(jeu, robot, main),
        )
        return sorted(meilleure_main, key=lambda carte: carte.vitesse, reverse=True)

    def _score_main(self, jeu, robot, cartes):
        """
        Role : calcule le score d’une main de cartes.
        Entrees : jeu (Jeu), robot (Robot), cartes (itérable)
        Sorties : flottant
        Pré-requis : les cartes doivent être valides
        """
        cartes = sorted(cartes, key=lambda carte: carte.vitesse, reverse=True)
        contexte = self._contextes_tour.get(id(robot)) or preparer_contexte(jeu, robot)
        score = 0.0
        precedentes = []
        position = (robot.x, robot.y)
        orientation = robot.orientation
        for carte in cartes:
            # La simulation permet d'estimer l'effet de toute la main avant
            # de la jouer réellement, notamment sur les tapis et les trous.
            score += self.score_carte(jeu, robot, carte, precedentes)
            etat = _simuler(
                jeu, position[0], position[1], orientation, carte.action
            )
            if etat is None:
                score -= 5.0
            else:
                position = etat[:2]
                orientation = etat[2]
            precedentes.append(carte)
        distance_finale = abs(
            position[0] - contexte["objectif"][0]
        ) + abs(position[1] - contexte["objectif"][1])
        # Plus la distance finale est petite, plus la main est intéressante.
        score -= distance_finale
        score -= 0.5 * sum(
            carte.action != ActionCarte.AVANCER for carte in cartes
        )
        return score

    def _rotation_interdite(self, robot, carte):
        """
        Role : indique si une rotation est interdite.
        Entrees : robot (Robot), carte (Carte)
        Sorties : booléen
        Pré-requis : le robot doit fournir son historique d’actions
        """
        rotations = ("Tourner à droite", "Tourner à gauche")
        return (
            carte.action.value in rotations
            and len(robot.actions_recentes) >= 2
            and all(
                action.value in rotations
                for action in robot.actions_recentes[-2:]
            )
        )

    def preparer_cartes(self, jeu, robots=None):
        """
        Role : prépare les cartes des robots actifs.
        Entrees : jeu (Jeu), robots (itérable) ou aucune
        Sorties : dictionnaire de cartes
        Pré-requis : le contrôleur doit être initialisé
        """
        actifs = robots or [robot for robot in jeu.robots if not robot.est_detruit]
        self._contextes_tour = {
            id(robot): preparer_contexte(jeu, robot)
            for robot in actifs
        }
        return {
            id(robot): self.tirer_et_choisir_cartes(jeu, robot)
            for robot in actifs
        }

    def preparer_tour(self, jeu):
        """
        Role : prépare les cartes du tour.
        Entrees : jeu (Jeu)
        Sorties : dictionnaire de cartes
        Pré-requis : le jeu doit fournir ses robots
        """
        cartes = self.preparer_cartes(jeu)
        jeu.installer_cartes(cartes)
        return cartes

    def doit_jouer_carte(self, jeu, robot, carte):
        """
        Role : indique si une carte doit être jouée.
        Entrees : jeu (Jeu), robot (Robot), carte (Carte)
        Sorties : booléen
        Pré-requis : les objets doivent être valides
        """
        return True

    def combinaison_oracle(self, jeu, robot):
        """
        Role : calcule la combinaison d’actions optimale.
        Entrees : jeu (Jeu), robot (Robot)
        Sorties : liste d’actions
        Pré-requis : le robot doit être dans le jeu
        """
        return combinaison(jeu, robot)

    def prochaine_action_oracle(self, jeu, robot):
        """
        Role : retourne la prochaine action optimale.
        Entrees : jeu (Jeu), robot (Robot)
        Sorties : action ou aucune
        Pré-requis : le robot doit être dans le jeu
        """
        return prochaine_action(jeu, robot)
