import time

from ia.controleur import ControleurRobot
from ia.perceptron import erreur_quadratique_moyenne, sauvegarder_perceptron
from ia.simulation import ORACLE


class EntraineurPerceptron:
    HORIZON_RECOMPENSE = 3
    EPSILON_DEPART = 0.30
    EPSILON_MINIMUM = 0.02
    EPSILON_DECROISSANCE = 0.995

    def __init__(
        self,
        creer_jeu,
        controleur=None,
        nombre_max_tours=1000,
        facteur_actualisation=0.9,
        controleurs=None,
        creer_jeu_evaluation=None,
    ):
        """
        Role : initialise l’entraîneur du perceptron.
        Entrees : creer_jeu (fonction), controleur (ControleurRobot) ou aucune, nombre_max_tours (int), facteur_actualisation (float), controleurs (dict) ou aucune, creer_jeu_evaluation (fonction) ou aucune
        Sorties : aucune
        Pré-requis : le nombre de tours doit être positif et le facteur compris entre 0 et 1
        """
        if nombre_max_tours <= 0:
            raise ValueError("Le nombre maximal de tours doit être positif.")
        if not 0 < facteur_actualisation <= 1:
            raise ValueError("Le facteur d'actualisation doit être entre 0 et 1.")
        self.creer_jeu = creer_jeu
        self.controleur = controleur or ControleurRobot()
        self.nombre_max_tours = nombre_max_tours
        self.facteur_actualisation = facteur_actualisation
        self.nombre_parties_jouees = 0
        self.controleurs = controleurs or {
            "bleu": self.controleur,
            "rouge": self.controleur,
        }
        self.creer_jeu_evaluation = creer_jeu_evaluation or creer_jeu

    def controleur_pour(self, robot):
        """
        Role : retourne le contrôleur de l'equipe du robot.
        Entrees : robot (Robot) : robot concerne
        Sorties : ControleurRobot : contrôleur de l'equipe
        Pré-requis : robot possède une couleur connue
        """
        return self.controleurs.get(robot.couleur, self.controleur)

    def preparer_tour(self, jeu):
        """
        Role : prépare les cartes avec un contrôleur par équipe.
        Entrees : jeu (Jeu) : partie à préparer
        Sorties : aucune
        Pré-requis : les contrôleurs sont compatibles avec les caractéristiques
        """
        cartes = {}
        for couleur, controleur in self.controleurs.items():
            robots = [
                robot for robot in jeu.robots
                if robot.couleur == couleur and not robot.est_detruit
            ]
            cartes.update(controleur.preparer_cartes(jeu, robots))
        jeu.installer_cartes(cartes)

    def jouer_partie(self, evaluation=False):
        """
        Role : joue une partie et calcule ses statistiques.
        Entrees : evaluation (booléen)
        Sorties : dictionnaire de statistiques
        Pré-requis : le générateur de partie doit être disponible
        """
        creer_jeu = (
            self.creer_jeu_evaluation if evaluation else self.creer_jeu
        )
        resultat = creer_jeu()
        jeu = resultat[0] if isinstance(resultat, tuple) else resultat
        transitions = []
        cartes_jouees = 0
        actions_oracle = 0
        actions_correctes = 0
        recompense_totale = 0.0
        temps_total = 0.0
        cartes_precedentes = {}

        while (
            jeu.equipe_gagnante is None
            and cartes_jouees < self.nombre_max_tours
        ):
            if not jeu.cartes_du_tour:
                for controleur in set(self.controleurs.values()):
                    controleur.epsilon = 0.0 if evaluation else max(
                        self.EPSILON_MINIMUM,
                        self.EPSILON_DEPART
                        * self.EPSILON_DECROISSANCE ** self.nombre_parties_jouees,
                    )
                self.preparer_tour(jeu)
            actuelle = jeu.carte_actuelle()
            if actuelle is None:
                break
            robot, carte = actuelle
            controleur = self.controleur_pour(robot)
            action_oracle = controleur.prochaine_action_oracle(jeu, robot)
            actions_oracle += action_oracle is not None
            actions_correctes += action_oracle == carte.action
            caracteristiques = None
            if not evaluation:
                caracteristiques = controleur.extraire_caracteristiques(
                    jeu, robot, carte, cartes_precedentes.get(id(robot), []),
                )
            avant = self._capturer_etat(jeu)
            debut = time.perf_counter()
            jeu.jouer_carte_actuelle(True)
            temps_total += time.perf_counter() - debut
            recompense = self.calculer_recompense(
                jeu, avant, robot, carte.action, action_oracle
            )
            if not evaluation:
                # Une transition relie l'état observé, l'action jouée et sa
                # récompense. Elle sera utilisée après un horizon de 3 cartes.
                transitions.append((controleur, caracteristiques, recompense))
            cartes_precedentes.setdefault(id(robot), []).append(carte)
            if not evaluation and len(transitions) == self.HORIZON_RECOMPENSE:
                self._mettre_a_jour(transitions)
            cartes_jouees += 1
            recompense_totale += recompense

        if not evaluation:
            self._vider_transitions(transitions)
            self.nombre_parties_jouees += 1
        return {
            "cartes_jouees": cartes_jouees,
            "accord_oracle": (
                actions_correctes / actions_oracle if actions_oracle else 0.0
            ),
            "recompense": recompense_totale,
            "equipe_gagnante": jeu.equipe_gagnante,
            "temps_par_tour": temps_total / cartes_jouees if cartes_jouees else 0.0,
        }

    def _mettre_a_jour(self, transitions):
        """
        Role : met à jour le perceptron à partir des transitions.
        Entrees : transitions (liste)
        Sorties : aucune
        Pré-requis : les transitions doivent contenir des caractéristiques et des récompenses
        """
        controleur, _, _ = transitions[0]
        recompenses = []
        for controleur_courant, _, recompense in transitions:
            if controleur_courant is not controleur:
                break
            recompenses.append(recompense)
        # La cible donne davantage de poids aux récompenses proches, tout en
        # conservant une part des récompenses futures.
        cible = sum(
            self.facteur_actualisation ** index * recompense
            for index, recompense in enumerate(recompenses)
        )
        _, caracteristiques, _ = transitions.pop(0)
        controleur.perceptron.mettre_a_jour(caracteristiques, cible)

    def _vider_transitions(self, transitions):
        """
        Role : traite les transitions restantes.
        Entrees : transitions (liste)
        Sorties : aucune
        Pré-requis : les transitions doivent être valides
        """
        while transitions:
            self._mettre_a_jour(transitions)

    def entrainer(self, nombre_parties):
        """
        Role : entraîne le perceptron sur plusieurs parties.
        Entrees : nombre_parties (int)
        Sorties : liste de statistiques
        Pré-requis : nombre_parties doit être positif
        """
        if nombre_parties <= 0:
            raise ValueError("Le nombre de parties doit être positif.")
        return [self.jouer_partie() for _ in range(nombre_parties)]

    def evaluer(self, nombre_parties=400):
        """
        Role : aucun
        Entrees : aucune
        Sorties : aucune
        Pré-requis : aucun
        """
        if nombre_parties < 400:
            raise ValueError("L'évaluation doit contenir au moins 400 parties.")
        return [
            self.jouer_partie(evaluation=True)
            for _ in range(nombre_parties)
        ]

    def entrainer_et_sauvegarder(
        self, nombre_parties, chemin_modele, nombre_parties_evaluation=400,
        chemins_modeles=None,
    ):
        """
        Role : entraîne puis sauvegarde le perceptron.
        Entrees : nombre_parties (int), chemin_modele (Path), nombre_parties_evaluation (int), chemins_modeles (dict) ou aucune
        Sorties : liste de statistiques
        Pré-requis : les nombres de parties doivent respecter les minimums requis
        """
        if nombre_parties_evaluation < 400:
            raise ValueError("L'évaluation doit contenir au moins 400 parties.")
        resultats = self.entrainer(nombre_parties)
        resultats_evaluation = self.evaluer(nombre_parties_evaluation)
        parties_terminees = sum(
            resultat["equipe_gagnante"] is not None for resultat in resultats
        )
        cartes = sum(resultat["cartes_jouees"] for resultat in resultats)
        recompense = sum(resultat["recompense"] for resultat in resultats)
        accord_oracle = sum(
            resultat["accord_oracle"] for resultat in resultats
        ) / nombre_parties
        parties_terminees_evaluation = sum(
            resultat["equipe_gagnante"] is not None
            for resultat in resultats_evaluation
        )
        cartes_evaluation = sum(
            resultat["cartes_jouees"] for resultat in resultats_evaluation
        )
        accord_evaluation = sum(
            resultat["accord_oracle"] for resultat in resultats_evaluation
        ) / nombre_parties_evaluation
        statistiques = {
            "parties": nombre_parties,
            "parties_terminees": parties_terminees,
            "taux_termination": parties_terminees / nombre_parties,
            "cartes_jouees": cartes,
            "recompense_moyenne": recompense / nombre_parties,
            "accord_oracle": accord_oracle,
            "evaluation_parties": nombre_parties_evaluation,
            "evaluation_parties_terminees": parties_terminees_evaluation,
            "evaluation_taux_termination": (
                parties_terminees_evaluation / nombre_parties_evaluation
            ),
            "evaluation_cartes_moyennes": (
                cartes_evaluation / nombre_parties_evaluation
            ),
            "evaluation_accord_oracle": accord_evaluation,
            **ORACLE.statistiques(),
            "erreur_quadratique_moyenne": (
                erreur_quadratique_moyenne(self.controleur.perceptron)
            ),
        }
        controleurs_uniques = {
            id(controleur): controleur
            for controleur in self.controleurs.values()
        }
        for controleur in controleurs_uniques.values():
            controleur.perceptron.statistiques.update(statistiques)
        sauvegarder_perceptron(
            self.controleur.perceptron, chemin_modele, statistiques
        )
        for couleur, chemin in (chemins_modeles or {}).items():
            controleur = self.controleurs.get(couleur)
            if controleur is not None:
                sauvegarder_perceptron(
                    controleur.perceptron,
                    chemin,
                    {
                        **statistiques,
                        "erreur_quadratique_moyenne": (
                            erreur_quadratique_moyenne(controleur.perceptron)
                        ),
                    },
                )
        return resultats

    def _capturer_etat(self, jeu):
        """
        Role : capture l’état courant du jeu.
        Entrees : jeu (Jeu)
        Sorties : dictionnaire d’état
        Pré-requis : le jeu doit fournir ses robots et ses drapeaux
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

    def calculer_recompense(self, jeu, avant, robot, action, action_oracle):
        """
        Role : calcule la récompense d’une action.
        Entrees : jeu (Jeu), avant (dict), robot (Robot), action (ActionCarte), action_oracle (ActionCarte) ou aucune
        Sorties : flottant
        Pré-requis : l’état précédent doit correspondre au robot
        """
        ancien_x, ancien_y, anciens_pv, etait_detruit = avant["robots"][id(robot)]
        recompense = 0.2 if (robot.x, robot.y) != (ancien_x, ancien_y) else -0.05
        if action_oracle is not None:
            recompense += 1 if action == action_oracle else -1
        recompense -= min(1, max(0, anciens_pv - robot.pv))
        for autre in jeu.robots:
            if autre is not robot and autre.couleur != robot.couleur:
                recompense += min(
                    1, max(0, avant["robots"][id(autre)][2] - autre.pv)
                )
        if robot.est_detruit and not etait_detruit:
            recompense -= 5
        recompense +=         3 * sum(
            ancien != robot.couleur
            and drapeau.equipe_capture == robot.couleur
            for ancien, (drapeau, _, _) in zip(
                avant["drapeaux"], jeu.drapeaux
            )
        )
        recompense += 2 * sum(
            not avant["robots"][id(autre)][3] and autre.est_detruit
            for autre in jeu.robots
            if autre is not robot and autre.couleur != robot.couleur
        )
        if jeu.equipe_gagnante == robot.couleur:
            recompense += 10
        elif jeu.equipe_gagnante is not None:
            recompense -= 10
        return recompense
