import json

from ia.reseau_neurones import ReseauNeurones


def charger_perceptron(chemin):
    """
    Role : charge un perceptron depuis un fichier JSON.
    Entrees : chemin (str) : chemin du modele
    Sorties : Perceptron : modele charge
    Pré-requis : le fichier contient des poids valides
    """
    with open(chemin, encoding="utf-8") as fichier:
        donnees = json.load(fichier)
    if donnees.get("type") == "reseau_neurones":
        return ReseauNeurones.depuis_donnees(donnees)
    return Perceptron(
        donnees["poids"],
        donnees.get("biais", 0),
        donnees.get("taux_apprentissage", 0.01),
        donnees.get("statistiques"),
    )


def sauvegarder_perceptron(perceptron, chemin, statistiques=None):
    """
    Role : sauvegarde un perceptron dans un fichier JSON.
    Entrees : perceptron (Perceptron) : modele ; chemin (str) : fichier ; statistiques (dict ou None) : statistiques
    Sorties : aucune
    Pré-requis : le dossier de destination existe
    """
    if isinstance(perceptron, ReseauNeurones):
        donnees = perceptron.donnees(statistiques)
    else:
        donnees = {
            "poids": perceptron.poids,
            "biais": perceptron.biais,
            "taux_apprentissage": perceptron.taux_apprentissage,
            "statistiques": statistiques or perceptron.statistiques,
        }
    with open(chemin, "w", encoding="utf-8") as fichier:
        json.dump(donnees, fichier, indent=2)


def erreur_quadratique_moyenne(perceptron):
    """
    Role : retourne l'erreur quadratique moyenne du modele.
    Entrees : perceptron (Perceptron) : modele concerne
    Sorties : float : erreur moyenne
    Pré-requis : perceptron contient ses statistiques
    """
    return perceptron.statistiques["erreur_quadratique_moyenne"]


class Perceptron:
    """Régression linéaire en ligne entraînée par la règle de Widrow-Hoff."""

    def __init__(
        self, poids, biais=0.0, taux_apprentissage=0.01,
        statistiques=None, erreur_maximale=5.0
    ):
        """
        Role : initialise les poids et les parametres du perceptron.
        Entrees : poids (list) : poids initiaux ; biais (float) : biais ; taux_apprentissage (float) : vitesse ; statistiques (dict) : statistiques ; erreur_maximale (float) : erreur maximale
        Sorties : aucune
        Pré-requis : poids n'est pas vide et taux_apprentissage est positif
        """
        if not poids:
            raise ValueError("Le perceptron doit avoir au moins un poids.")
        if taux_apprentissage <= 0:
            raise ValueError("Le taux d'apprentissage doit être positif.")
        self.poids = [float(poids_) for poids_ in poids]
        self.biais = float(biais)
        self.taux_apprentissage = float(taux_apprentissage)
        self.erreur_maximale = float(erreur_maximale)
        self.statistiques = {
            "mises_a_jour": 0,
            "erreur_quadratique_moyenne": 0.0,
        }
        if statistiques:
            self.statistiques.update(statistiques)
        self.statistiques.setdefault("erreur_quadratique_moyenne", 0.0)

    def calculer(self, caracteristiques):
        """
        Role : calcule la sortie lineaire du perceptron.
        Entrees : caracteristiques (list) : valeurs d'entree
        Sorties : float : score calcule
        Pré-requis : le nombre de caracteristiques egale le nombre de poids
        """
        if len(caracteristiques) != len(self.poids):
            raise ValueError("Le nombre de caractéristiques ne correspond pas aux poids.")
        return self.biais + sum(
            poids * caracteristique
            for poids, caracteristique in zip(self.poids, caracteristiques)
        )

    def mettre_a_jour(self, caracteristiques, cible):
        """
        Role : ajuste les poids selon l'erreur de prediction.
        Entrees : caracteristiques (list) : valeurs d'entree ; cible (float) : valeur attendue
        Sorties : float : erreur bornee utilisee
        Pré-requis : le nombre de caracteristiques egale le nombre de poids
        """
        prediction = self.calculer(caracteristiques)
        erreur = max(
            -self.erreur_maximale,
            min(self.erreur_maximale, float(cible) - prediction),
        )
        # E = 1/2 (c - y)^2
        # dE/dw_i = -(c - y) x_i
        # w_i <- w_i + eta (c - y) x_i
        self.poids = [
            poids + self.taux_apprentissage * erreur * caracteristique
            for poids, caracteristique in zip(self.poids, caracteristiques)
        ]
        self.biais += self.taux_apprentissage * erreur
        total = self.statistiques["mises_a_jour"]
        self.statistiques["mises_a_jour"] = total + 1
        self.statistiques["erreur_quadratique_moyenne"] = (
            self.statistiques["erreur_quadratique_moyenne"] * total
            + erreur ** 2
        ) / (total + 1)
        return erreur
