import math
import random


class ReseauNeurones:
    def __init__(
        self,
        nombre_entrees=11,
        nombre_neurones_caches=8,
        taux_apprentissage=0.001,
        graine=0,
        erreur_maximale=5.0,
    ):
        """
        Role : initialise un réseau avec une couche cachée ReLU.
        Entrees : nombre_entrees (int), nombre_neurones_caches (int), taux_apprentissage (float), graine (int)
        Sorties : aucune
        Pré-requis : les nombres doivent être positifs et le taux doit être positif
        """
        self.nombre_entrees = nombre_entrees
        self.nombre_neurones_caches = nombre_neurones_caches
        self.taux_apprentissage = float(taux_apprentissage)
        self.erreur_maximale = float(erreur_maximale)
        self.statistiques = {
            "mises_a_jour": 0,
            "erreur_quadratique_moyenne": 0.0,
        }
        hasard = random.Random(graine)
        amplitude = math.sqrt(2 / nombre_entrees)
        self.poids_caches = [
            [
                hasard.uniform(-amplitude, amplitude)
                for _ in range(nombre_entrees)
            ]
            for _ in range(nombre_neurones_caches)
        ]
        self.biais_caches = [0.0] * nombre_neurones_caches
        amplitude_sortie = math.sqrt(2 / nombre_neurones_caches)
        self.poids_sortie = [
            hasard.uniform(-amplitude_sortie, amplitude_sortie)
            for _ in range(nombre_neurones_caches)
        ]
        self.biais_sortie = 0.0

    @classmethod
    def depuis_donnees(cls, donnees):
        """
        Role : construit un réseau à partir de paramètres sauvegardés.
        Entrees : donnees (dict) : paramètres du réseau
        Sorties : ReseauNeurones : réseau reconstruit
        Pré-requis : les paramètres contiennent les poids et biais du réseau
        """
        nombre_entrees = donnees["nombre_entrees"]
        poids_caches = donnees["poids_caches"]
        if nombre_entrees == 22:
            nombre_entrees = 11
            poids_caches = [
                poids_entree[:nombre_entrees]
                for poids_entree in poids_caches
            ]
        reseau = cls(
            nombre_entrees,
            donnees["nombre_neurones_caches"],
            donnees.get("taux_apprentissage", 0.001),
            erreur_maximale=donnees.get("erreur_maximale", 5.0),
        )
        reseau.poids_caches = poids_caches
        reseau.biais_caches = donnees["biais_caches"]
        reseau.poids_sortie = donnees["poids_sortie"]
        reseau.biais_sortie = donnees["biais_sortie"]
        reseau.statistiques.update(donnees.get("statistiques") or {})
        return reseau

    def donnees(self, statistiques=None):
        """
        Role : prépare les paramètres du réseau pour une sauvegarde JSON.
        Entrees : statistiques (dict ou None) : statistiques à enregistrer
        Sorties : dict : paramètres sérialisables du réseau
        Pré-requis : aucun
        """
        return {
            "type": "reseau_neurones",
            "nombre_entrees": self.nombre_entrees,
            "nombre_neurones_caches": self.nombre_neurones_caches,
            "taux_apprentissage": self.taux_apprentissage,
            "erreur_maximale": self.erreur_maximale,
            "poids_caches": self.poids_caches,
            "biais_caches": self.biais_caches,
            "poids_sortie": self.poids_sortie,
            "biais_sortie": self.biais_sortie,
            "statistiques": statistiques or self.statistiques,
        }

    def calculer(self, caracteristiques):
        """
        Role : calcule le score produit par le réseau.
        Entrees : caracteristiques (list) : valeurs d'entrée
        Sorties : float : score calculé
        Pré-requis : le nombre de caractéristiques correspond au nombre d'entrées
        """
        # Chaque neurone caché reçoit les caractéristiques, puis ReLU
        # conserve uniquement sa réponse positive.
        sorties_cachees = [
            self._relu(
                biais + sum(
                    poids * caracteristique
                    for poids, caracteristique in zip(
                        poids_entree, caracteristiques
                    )
                )
            )
            for poids_entree, biais in zip(
                self.poids_caches, self.biais_caches
            )
        ]
        # La couche de sortie combine les réponses cachées en un score unique.
        return self.biais_sortie + sum(
            poids * sortie
            for poids, sortie in zip(self.poids_sortie, sorties_cachees)
        )

    def mettre_a_jour(self, caracteristiques, cible):
        """
        Role : ajuste les poids du réseau par rétropropagation.
        Entrees : caracteristiques (list) : valeurs d'entrée ; cible (float) : valeur attendue
        Sorties : float : erreur bornée utilisée
        Pré-requis : le nombre de caractéristiques correspond au nombre d'entrées
        """
        # On recalcule les valeurs intermédiaires nécessaires pour remonter
        # l'erreur de la sortie vers les neurones cachés.
        preactivations = [
            biais + sum(
                poids * caracteristique
                for poids, caracteristique in zip(
                    poids_entree, caracteristiques
                )
            )
            for poids_entree, biais in zip(
                self.poids_caches, self.biais_caches
            )
        ]
        sorties_cachees = [self._relu(valeur) for valeur in preactivations]
        prediction = self.biais_sortie + sum(
            poids * sortie
            for poids, sortie in zip(self.poids_sortie, sorties_cachees)
        )
        # La cible est la récompense cumulée sur quelques transitions.
        # La borne évite qu'une récompense exceptionnelle déstabilise le réseau.
        erreur = max(
            -self.erreur_maximale,
            min(self.erreur_maximale, float(cible) - prediction),
        )
        # Les gradients cachés utilisent les anciens poids de sortie :
        # toutes les corrections doivent correspondre au même calcul.
        poids_sortie_avant = list(self.poids_sortie)
        gradients_caches = [
            erreur * poids * self._derivee_relu(preactivation)
            for poids, preactivation in zip(
                poids_sortie_avant, preactivations
            )
        ]
        # Première étape de la rétropropagation : correction de la sortie.
        for index, sortie in enumerate(sorties_cachees):
            self.poids_sortie[index] += (
                self.taux_apprentissage * erreur * sortie
            )
        self.biais_sortie += self.taux_apprentissage * erreur
        # Deuxième étape : la correction revient vers chaque neurone caché.
        # Un neurone inactif par ReLU possède un gradient nul pour cet exemple.
        for index, gradient in enumerate(gradients_caches):
            for entree, caracteristique in enumerate(caracteristiques):
                self.poids_caches[index][entree] += (
                    self.taux_apprentissage
                    * gradient
                    * caracteristique
                )
            self.biais_caches[index] += self.taux_apprentissage * gradient
        total = self.statistiques["mises_a_jour"]
        self.statistiques["mises_a_jour"] = total + 1
        self.statistiques["erreur_quadratique_moyenne"] = (
            self.statistiques["erreur_quadratique_moyenne"] * total
            + erreur ** 2
        ) / (total + 1)
        return erreur

    @staticmethod
    def _relu(valeur):
        """
        Role : applique la fonction d'activation ReLU.
        Entrees : valeur (float) : valeur à activer
        Sorties : float : valeur positive ou nulle
        Pré-requis : aucun
        """
        return max(0.0, valeur)

    @staticmethod
    def _derivee_relu(valeur):
        """
        Role : calcule la dérivée de la fonction ReLU.
        Entrees : valeur (float) : valeur avant activation
        Sorties : float : dérivée de l'activation
        Pré-requis : aucun
        """
        return 1.0 if valeur > 0 else 0.0
