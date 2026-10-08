"""
Auteur : Perles Alexis
Date de dernière modification : 04/10/2026
Contenu : Construit le plateau et gère son affichage pygame.
"""

"""Création du plateau et affichage pygame.

Le rendu est séparé des règles : aucune décision de jeu n'est prise ici.
"""

from pathlib import Path

import pygame

from Entitées.Case import Case
from Entitées.Direction import Direction
from Jeu.Jeu import Jeu
from Entitées.TypeCase import TypeCase

TAILLE_CASE = 60
TAILLE_PLATEAU = 12
MARGE = 24
PANNEAU = 360
LARGEUR = TAILLE_PLATEAU * TAILLE_CASE + MARGE * 3 + PANNEAU
HAUTEUR = TAILLE_PLATEAU * TAILLE_CASE + MARGE * 2
FOND = (19, 24, 31)
PANNEAU_FOND = (35, 44, 56)
TEXTE = (235, 240, 245)
SECOND = (155, 170, 185)
ACCENT = (244, 180, 66)
POLICE = "DejaVu Sans"
BLEU = (64, 140, 235)
ROUGE = (224, 78, 78)
# Les images sont stockées à la racine du projet, et non dans `Jeu/images`.
DOSSIER_IMAGES = Path(__file__).resolve().parent.parent / "images"


def _origine_affichage(fenetre):
    """Calcule l'origine centrée de la zone de jeu.

    - Description : place le plateau et son panneau au centre de la fenêtre.
    - Prérequis : `fenetre` doit être une surface pygame initialisée.
    - Arguments : `fenetre` (`pygame.Surface`).
    - Retourne : coordonnées de l'origine (`tuple[int, int]`).
    """
    largeur, hauteur = fenetre.get_size()
    origine_x = (largeur - LARGEUR) // 2
    origine_y = (hauteur - HAUTEUR) // 2
    return max(0, origine_x), max(0, origine_y)


def creer_images():
    """Charge les images disponibles et les adapte à la taille d'une case.

    - Description : ouvre les fichiers d'image présents puis les redimensionne.
    - Prérequis : pygame doit être initialisé et le dossier `images` accessible.
    - Arguments : aucun.
    - Retourne : images indexées par leur nom logique (`dict[str, pygame.Surface]`).
    """
    fichiers = {
        "trou": "trou.png",
        "bonus": "bonus.png",
        "rotation": "rotation.png",
        "drapeau_bleu": "drapeau bleu.png",
        "drapeau_rouge": "drapeau rouge.png",
        "reparation": "reparation.png",
        "vide": "vide.png",
        "tapis_haut": "tapis haut.png",
        "tapis_droite": "tapis droite.png",
        "tapis_bas": "tapis bas.png",
        "tapis_gauche": "tapis gauche.png",
        "mur": "mur.png",
    }
    images = {}
    for nom, fichier in fichiers.items():
        chemin = DOSSIER_IMAGES / fichier
        if chemin.exists():
            image = pygame.image.load(str(chemin))
            images[nom] = pygame.transform.scale(
                image, (TAILLE_CASE, TAILLE_CASE)
            )
    return images


def creer_plateau(graine=None):
    """Construit la carte fixe et ses obstacles.

    - Description : place les tapis, trous, bonus, réparations et murs du plateau.
    - Prérequis : `graine` est réservée pour compatibilité et peut être `None`.
    - Arguments : `graine` (`int` ou `None`).
    - Retourne : cases et murs (`tuple[list[list[Case]], dict]`).
    """
    cases = [[Case() for _ in range(TAILLE_PLATEAU)] for _ in range(TAILLE_PLATEAU)]
    cases[2][3] = Case(TypeCase.TAPIS_EST)
    cases[2][4] = Case(TypeCase.TAPIS_EST)
    cases[2][5] = Case(TypeCase.TAPIS_NORD, rotation=180)
    cases[1][5] = Case(TypeCase.TAPIS_NORD)
    cases[0][5] = Case(TypeCase.TAPIS_NORD)
    cases[9][6] = Case(TypeCase.TAPIS_OUEST)
    cases[9][5] = Case(TypeCase.TAPIS_OUEST)
    cases[9][4] = Case(TypeCase.TAPIS_SUD, rotation=0)
    cases[10][4] = Case(TypeCase.TAPIS_SUD)
    cases[11][4] = Case(TypeCase.TAPIS_SUD)
    cases[4][2] = Case(TypeCase.TAPIS_SUD)
    cases[5][2] = Case(TypeCase.TAPIS_SUD)
    cases[6][2] = Case(TypeCase.TAPIS_EST, rotation=90)
    cases[6][3] = Case(TypeCase.TAPIS_EST)
    cases[6][4] = Case(TypeCase.TAPIS_EST)
    cases[4][9] = Case(TypeCase.TAPIS_NORD)
    cases[5][9] = Case(TypeCase.TAPIS_NORD)
    cases[6][9] = Case(TypeCase.TAPIS_NORD, rotation=180)
    cases[6][8] = Case(TypeCase.TAPIS_EST)
    cases[6][7] = Case(TypeCase.TAPIS_EST)
    tapis = set()
    for y, ligne in enumerate(cases):
        for x, case in enumerate(ligne):
            if case.type_case.est_tapis:
                tapis.add((x, y))

    # Cinq trous séparés : aucun n'est voisin horizontalement ou verticalement.
    trous = {(1, 4), (5, 5), (8, 3), (3, 9), (10, 6)}
    for x, y in trous:
        if (x, y) not in tapis:
            cases[y][x] = Case(TypeCase.TROU)

    bonus = {(2, 1), (5, 4), (9, 8)}
    reparations = {(4, 7), (7, 4), (10, 8)}
    depart = {(0, 0), (1, 0), (10, 11), (11, 11)}
    for x, y in bonus:
        if (x, y) not in tapis and (x, y) not in trous and (x, y) not in depart:
            cases[y][x] = Case(TypeCase.BONUS)
    for x, y in reparations:
        if (x, y) not in tapis and (x, y) not in trous and (x, y) not in depart:
            cases[y][x] = Case(TypeCase.REPARATION)

    # Obstacles fixes : leur emplacement ne recouvre aucun tapis ni élément.
    emplacements_murs = [
        ((0, 2), Direction.NORD),
        ((3, 3), Direction.EST),
        ((6, 3), Direction.SUD),
        ((9, 3), Direction.OUEST),
        ((4, 5), Direction.NORD),
        ((6, 6), Direction.EST),
        ((8, 6), Direction.SUD),
        ((3, 7), Direction.OUEST),
        ((6, 9), Direction.NORD),
        ((11, 8), Direction.EST),
        ((4, 11), Direction.SUD),
        ((10, 10), Direction.OUEST),
    ]
    murs = {}
    for (x, y), direction in emplacements_murs:
        if cases[y][x].type_case == TypeCase.VIDE:
            murs[(x, y)] = {direction}
            cases[y][x].murs.append(direction)
    return cases, murs


def dessiner(
    fenetre: pygame.Surface,
    jeu: Jeu,
    murs,
    images,
):
    """Dessine tous les éléments visibles de la partie.

    - Description : rend les cases, murs, drapeaux, robots, panneau et victoire.
    - Prérequis : pygame doit être initialisé et `jeu` doit fournir ses éléments.
    - Arguments : `fenetre` (`pygame.Surface`), `jeu` (`Jeu`), `murs` (`dict`),
      `images` (`dict[str, pygame.Surface]`).
    - Retourne : rien (`None`).
    """
    fenetre.fill(FOND)
    decalage_x, decalage_y = _origine_affichage(fenetre)
    origine = (decalage_x + MARGE, decalage_y + MARGE)
    for y, ligne in enumerate(jeu.cases):
        for x, case in enumerate(ligne):
            rectangle = pygame.Rect(origine[0] + x * TAILLE_CASE, origine[1] + y * TAILLE_CASE, TAILLE_CASE, TAILLE_CASE)
            _dessiner_case(
                fenetre,
                rectangle,
                case.type_case,
                images,
                case.rotation,
            )
            _dessiner_murs(
                fenetre,
                rectangle,
                murs.get((x, y), set()),
                images,
            )
    for drapeau, x, y in jeu.drapeaux:
        _dessiner_drapeau(
            fenetre,
            origine[0] + x * TAILLE_CASE,
            origine[1] + y * TAILLE_CASE,
            drapeau.couleur,
            images,
        )
    for robot in jeu.robots:
        if not robot.est_detruit:
            _dessiner_robot(fenetre, origine[0] + robot.x * TAILLE_CASE, origine[1] + robot.y * TAILLE_CASE, robot)
    _dessiner_panneau(fenetre, jeu)
    if jeu.equipe_gagnante is not None:
        _dessiner_victoire(fenetre, jeu.equipe_gagnante)


def _dessiner_case(fenetre, rectangle, type_case, images, rotation):
    """Dessine le fond et le contenu graphique d'une case.

    - Description : utilise une image si elle existe, sinon dessine une forme de secours.
    - Prérequis : `fenetre` doit être une surface pygame et `type_case` valide.
    - Arguments : `fenetre` (`pygame.Surface`), `rectangle` (`pygame.Rect`),
      `type_case` (`TypeCase`), `images` (`dict`), `rotation` (`int` ou `None`).
    - Retourne : rien (`None`).
    """
    couleurs = {
        TypeCase.VIDE: (76, 88, 101),
        TypeCase.TAPIS_NORD: (53, 112, 124), TypeCase.TAPIS_EST: (53, 112, 124),
        TypeCase.TAPIS_SUD: (53, 112, 124), TypeCase.TAPIS_OUEST: (53, 112, 124),
        TypeCase.BONUS: (101, 91, 49), TypeCase.REPARATION: (75, 86, 77),
    }
    image_par_type = {
        TypeCase.TROU: "trou",
        TypeCase.BONUS: "bonus",
        TypeCase.REPARATION: "reparation",
        TypeCase.TAPIS_NORD: "tapis_haut",
        TypeCase.TAPIS_EST: "tapis_droite",
        TypeCase.TAPIS_SUD: "tapis_bas",
        TypeCase.TAPIS_OUEST: "tapis_gauche",
    }
    nom_image = image_par_type.get(type_case, "vide")
    image = images.get(nom_image)
    if rotation is not None and images.get("rotation") is not None:
        image = pygame.transform.rotate(images["rotation"], rotation)
    if image is not None:
        fenetre.blit(image, rectangle.topleft)
    else:
        pygame.draw.rect(fenetre, couleurs.get(type_case, (30, 32, 38)), rectangle)
    pygame.draw.rect(fenetre, (42, 49, 58), rectangle, 1)
    centre = rectangle.center
    if type_case == TypeCase.TROU and image is None:
        pygame.draw.circle(fenetre, (8, 10, 14), centre, 24)
        pygame.draw.circle(fenetre, (105, 112, 122), centre, 24, 3)
        pygame.draw.ellipse(fenetre, (1, 2, 4), (centre[0] - 17, centre[1] - 10, 34, 20))
    elif type_case == TypeCase.BONUS and image is None:
        for dx in (-8, 8):
            pygame.draw.circle(fenetre, ACCENT, (centre[0] + dx, centre[1]), 11, 3)
            pygame.draw.circle(fenetre, ACCENT, (centre[0] + dx, centre[1]), 3)
    elif type_case == TypeCase.REPARATION and image is None:
        pygame.draw.line(fenetre, (215, 220, 225), (centre[0] - 15, centre[1] + 13), (centre[0] + 12, centre[1] - 13), 6)
        pygame.draw.line(fenetre, (215, 220, 225), (centre[0] + 7, centre[1] - 17), (centre[0] + 17, centre[1] - 7), 5)


def _dessiner_murs(fenetre, rectangle, directions, images):
    """Dessine les murs présents autour d'une case.

    - Description : affiche une texture de mur ou un segment de remplacement.
    - Prérequis : les directions doivent appartenir à `Direction`.
    - Arguments : `fenetre` (`pygame.Surface`), `rectangle` (`pygame.Rect`),
      `directions` (itérable de `Direction`), `images` (`dict`).
    - Retourne : rien (`None`).
    """
    image = images.get("mur")
    if image is not None:
        for direction in directions:
            _dessiner_mur_sur_bord(fenetre, rectangle, image, direction)
        return
    segments = {
        Direction.NORD: ((rectangle.left, rectangle.top), (rectangle.right, rectangle.top)),
        Direction.EST: ((rectangle.right, rectangle.top), (rectangle.right, rectangle.bottom)),
        Direction.SUD: ((rectangle.left, rectangle.bottom), (rectangle.right, rectangle.bottom)),
        Direction.OUEST: ((rectangle.left, rectangle.top), (rectangle.left, rectangle.bottom)),
    }
    for direction in directions:
        pygame.draw.line(fenetre, (25, 27, 31), *segments[direction], 7)


def _dessiner_mur_sur_bord(fenetre, rectangle, image, direction):
    """Place une texture de mur sur le bord demandé.

    - Description : redimensionne et tourne l'image pour suivre la direction.
    - Prérequis : `image` doit être une surface pygame et `direction` valide.
    - Arguments : `fenetre` (`pygame.Surface`), `rectangle` (`pygame.Rect`),
      `image` (`pygame.Surface`), `direction` (`Direction`).
    - Retourne : rien (`None`).
    """
    epaisseur = 11
    bande = pygame.transform.scale(image, (rectangle.width, epaisseur))
    angles = {
        Direction.NORD: 0,
        Direction.EST: -90,
        Direction.SUD: 180,
        Direction.OUEST: 90,
    }
    bande = pygame.transform.rotate(bande, angles[direction])
    positions = {
        Direction.NORD: (rectangle.left, rectangle.top),
        Direction.EST: (rectangle.right - epaisseur, rectangle.top),
        Direction.SUD: (rectangle.left, rectangle.bottom - epaisseur),
        Direction.OUEST: (rectangle.left, rectangle.top),
    }
    position = positions[direction]
    fenetre.blit(bande, position)


def _dessiner_robot(fenetre: pygame.Surface, x: int, y: int, robot) -> None:
    """Dessine un robot et une flèche indiquant son orientation.

    - Description : représente le robot par un cercle coloré et son orientation.
    - Prérequis : pygame doit être initialisé et `robot.orientation` valide.
    - Arguments : `fenetre` (`pygame.Surface`), `x` (`int`), `y` (`int`),
      `robot` (`Robot`).
    - Retourne : rien (`None`).
    """
    couleur = BLEU if robot.couleur == "bleu" else ROUGE
    centre = (x + TAILLE_CASE // 2, y + TAILLE_CASE // 2)
    pygame.draw.circle(fenetre, couleur, centre, 21)
    pygame.draw.circle(fenetre, (235, 240, 245), centre, 21, 2)
    dx, dy = robot.orientation.value
    pointe = (centre[0] + dx * 25, centre[1] + dy * 25)
    pygame.draw.line(fenetre, (25, 28, 33), centre, pointe, 7)
    _fleche(fenetre, pointe, robot.orientation, 9, (25, 28, 33))


def _dessiner_drapeau(fenetre, x, y, couleur, images):
    """Dessine un drapeau avec son image ou une forme de secours.

    - Description : affiche le drapeau de l'équipe à la position indiquée.
    - Prérequis : `couleur` doit identifier une équipe connue.
    - Arguments : `fenetre` (`pygame.Surface`), `x` (`int`), `y` (`int`),
      `couleur` (`str`), `images` (`dict`).
    - Retourne : rien (`None`).
    """
    image = images.get("drapeau_" + couleur)
    if image is not None:
        fenetre.blit(image, (x, y))
        return
    teinte = BLEU if couleur == "bleu" else ROUGE if couleur == "rouge" else (220, 220, 220)
    pygame.draw.line(fenetre, (45, 45, 50), (x + 18, y + 50), (x + 18, y + 10), 4)
    pygame.draw.polygon(fenetre, teinte, ((x + 20, y + 10), (x + 50, y + 20), (x + 20, y + 30)))


def _dessiner_panneau(fenetre: pygame.Surface, jeu: Jeu) -> None:
    """Dessine le panneau latéral d'informations de la partie.

    - Description : affiche les robots, les drapeaux et l'état du tour.
    - Prérequis : pygame doit être initialisé et `jeu` correctement initialisé.
    - Arguments : `fenetre` (`pygame.Surface`), `jeu` (`Jeu`).
    - Retourne : rien (`None`).
    """
    decalage_x, decalage_y = _origine_affichage(fenetre)
    x = decalage_x + MARGE * 2 + TAILLE_PLATEAU * TAILLE_CASE
    pygame.draw.rect(
        fenetre,
        PANNEAU_FOND,
        (x, decalage_y + MARGE, PANNEAU, HAUTEUR - 2 * MARGE),
        border_radius=12,
    )
    titre = pygame.font.SysFont(POLICE, 38, bold=True)
    petite = pygame.font.SysFont(POLICE, 21)
    section = pygame.font.SysFont(POLICE, 26, bold=True)
    fenetre.blit(titre.render("ROBO RALLY", True, ACCENT), (x + 22, decalage_y + 35))
    fenetre.blit(petite.render("MODE PRESENTATION", True, SECOND), (x + 23, decalage_y + 70))
    y = decalage_y + 108
    fenetre.blit(section.render("ÉQUIPES", True, ACCENT), (x + 22, y))
    y += 31
    for robot in jeu.robots:
        couleur = BLEU if robot.couleur == "bleu" else ROUGE
        pygame.draw.circle(fenetre, couleur, (x + 30, y + 9), 7)
        etat = "DÉTRUIT" if robot.est_detruit else f"PV {robot.pv}"
        if not robot.est_detruit and robot.bouclier:
            etat += f"  BOUCLIER {robot.bouclier}"
        elif not robot.est_detruit and robot.bonus_degats:
            etat += "  ATTAQUE +2"
        fenetre.blit(petite.render(f"{robot.nom}   {etat}", True, TEXTE), (x + 45, y))
        y += 27
    y += 20
    fenetre.blit(section.render("DRAPEAUX", True, ACCENT), (x + 22, y))
    y += 32
    for drapeau, _, _ in jeu.drapeaux:
        couleur = BLEU if drapeau.couleur == "bleu" else ROUGE
        pygame.draw.circle(fenetre, couleur, (x + 30, y + 9), 7)
        fenetre.blit(
            petite.render(f"Drapeau {drapeau.couleur}", True, TEXTE),
            (x + 45, y),
        )
        y += 27
    y += 12
    fenetre.blit(section.render("ÉTAT DU TOUR", True, ACCENT), (x + 22, y))
    fenetre.blit(petite.render(f"{len(jeu.cartes_du_tour)} cartes restantes", True, TEXTE), (x + 25, y + 32))
    fenetre.blit(petite.render("IA active", True, SECOND), (x + 25, y + 58))


def _dessiner_victoire(fenetre: pygame.Surface, equipe: str) -> None:
    """Affiche l'écran de victoire de l'équipe gagnante.

    - Description : ajoute un voile sombre et un message sans fermer pygame.
    - Prérequis : `fenetre` doit être une surface pygame.
    - Arguments : `fenetre` (`pygame.Surface`), `equipe` (`str`).
    - Retourne : rien (`None`).
    """
    voile = pygame.Surface(fenetre.get_size(), pygame.SRCALPHA)
    voile.fill((7, 10, 15, 205))
    fenetre.blit(voile, (0, 0))
    couleur = BLEU if equipe == "bleu" else ROUGE
    titre = pygame.font.SysFont(POLICE, 72, bold=True).render("VICTOIRE", True, ACCENT)
    message = pygame.font.SysFont(POLICE, 42, bold=True).render(
        f"EQUIPE {equipe.upper()}",
        True,
        couleur,
    )
    sous_titre = pygame.font.SysFont(POLICE, 26).render(
        "Tous les drapeaux sont captures ou les adversaires sont elimines.",
        True,
        TEXTE,
    )
    centre = (fenetre.get_width() // 2, fenetre.get_height() // 2)
    fenetre.blit(titre, titre.get_rect(center=(centre[0], centre[1] - 55)))
    fenetre.blit(message, message.get_rect(center=(centre[0], centre[1] + 10)))
    fenetre.blit(sous_titre, sous_titre.get_rect(center=(centre[0], centre[1] + 55)))


def afficher_tir(fenetre, jeu, murs, images, horloge, tireur, cible):
    """Affiche brièvement le rayon entre un robot et sa cible.

    - Description : dessine le plateau puis une ligne lumineuse entre les robots.
    - Prérequis : pygame doit être initialisé et les robots doivent être actifs.
    - Arguments : `fenetre` (`pygame.Surface`), `jeu` (`Jeu`), `murs` (`dict`),
      `images` (`dict`), `horloge` (`pygame.time.Clock`), `tireur` (`Robot`),
      `cible` (`Robot`).
    - Retourne : rien (`None`).
    """
    dessiner(fenetre, jeu, murs, images)
    decalage_x, decalage_y = _origine_affichage(fenetre)
    origine = (decalage_x + MARGE, decalage_y + MARGE)
    depart = (
        origine[0] + tireur.x * TAILLE_CASE + TAILLE_CASE // 2,
        origine[1] + tireur.y * TAILLE_CASE + TAILLE_CASE // 2,
    )
    arrivee = (
        origine[0] + cible.x * TAILLE_CASE + TAILLE_CASE // 2,
        origine[1] + cible.y * TAILLE_CASE + TAILLE_CASE // 2,
    )
    pygame.draw.line(fenetre, (255, 245, 180), depart, arrivee, 10)
    pygame.draw.line(fenetre, (255, 255, 255), depart, arrivee, 4)
    pygame.draw.circle(fenetre, (255, 80, 50), arrivee, 25, 4)
    pygame.display.flip()
    horloge.tick(8)


def _fleche(fenetre, centre, direction, taille, couleur) -> None:
    """Dessine une flèche orientée autour d'un point central.

    - Description : calcule la pointe et les deux côtés puis les dessine.
    - Prérequis : `direction` doit être un membre de `Direction`.
    - Arguments : `fenetre` (`pygame.Surface`), `centre` (`tuple[int, int]`),
      `direction` (`Direction`), `taille` (`int`), `couleur` (`tuple[int, int, int]`).
    - Retourne : rien (`None`).
    """
    dx, dy = direction.value
    pointe = (centre[0] + dx * taille, centre[1] + dy * taille)
    pygame.draw.line(fenetre, couleur, (centre[0] - dx * taille // 2, centre[1] - dy * taille // 2), pointe, max(3, taille // 4))
    pygame.draw.polygon(fenetre, couleur, (pointe, (pointe[0] - dx * taille // 2 - dy * taille // 2, pointe[1] - dy * taille // 2 + dx * taille // 2), (pointe[0] - dx * taille // 2 + dy * taille // 2, pointe[1] - dy * taille // 2 - dx * taille // 2)))
