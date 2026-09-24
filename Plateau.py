""" carte graphique"""


import pygame

from Direction import Direction
from Drapeau import Drapeau
from Robot import Robot

pygame.init()

#taille de la grille
taille_case= 64
nb_lignes= 10
nb_colonnes= 10 

#creation de la fenetre

largeur_fenetre= nb_colonnes * taille_case
hauteur_fenetre= nb_lignes * taille_case
fenetre= pygame.display.set_mode((largeur_fenetre, hauteur_fenetre))
pygame.display.set_caption("Robot Rally")

#def couleur vide
vide=(200,200,200)

# def images
images={
    "mur":pygame.image.load("images/mur.png"),
    "trou":pygame.image.load("images/trou.png"),
    "bonus":pygame.image.load("images/bonus.png"),
    "robot":pygame.image.load("images/robot.png"),
    "coeur":pygame.image.load("images/coeur.png"),
    "drapeau":pygame.image.load("images/drapeau.png"),
    "tapis_droite":pygame.image.load("images/tapis_droite.png"),
    "tapis_gauche":pygame.image.load("images/tapis_gauche.png"),
    "tapis_bas":pygame.image.load("images/tapis_bas.png"),
    "tapis_haut":pygame.image.load("images/tapis_haut.png"),
    }

#redimmensionner images
for cle in images:
    images[cle]= pygame.transform.scale(images[cle],(taille_case,taille_case))

carte=[
    ["vide","vide","vide","vide","trou","vide","vide","vide","vide","vide",],
    ["tapis_gauche","tapis_gauche","tapis_gauche","tapis_gauche","vide","vide","vide","tapis_gauche","tapis_gauche","tapis_gauche",],
    ["bonus","vide","vide","tapis_haut","vide","vide","vide","tapis_bas","vide","vide",],
    ["vide","vide","vide","tapis_haut","vide","vide","vide","tapis_bas","vide","vide",],
    ["vide","vide","vide","tapis_haut","vide","vide","vide","tapis_bas","vide","vide",],
    ["vide","vide","vide","tapis_haut","vide","vide","vide","tapis_bas","vide","vide",],
    ["vide","vide","vide","tapis_haut","vide","vide","vide","tapis_bas","vide","vide",],
    ["vide","vide","vide","tapis_haut","tapis_gauche","tapis_gauche","tapis_gauche","tapis_gauche","vide","vide",],
    ["vide","vide","vide","vide","vide","vide","vide","vide","coeur","vide",],
    ["vide","vide","vide","vide","vide","trou","vide","vide","vide","vide",]
    ]

# Les murs sont indépendants du contenu de la case. Ils sont placés uniquement
# sur des cases normales, jamais sur les tapis roulants.
murs = {
    (3, 0): {Direction.EST},
    (5, 4): {Direction.NORD},
    (6, 6): {Direction.OUEST},
    (7, 9): {Direction.SUD},
}

# Les robots affichés sont de vraies instances de la classe Robot.
robots = [
    Robot("Robo bleu", 9, 3, Direction.OUEST, "bleu"),
    Robot("Robo rouge", 0, 7, Direction.EST, "rouge"),
    Robot("Robo vert", 1, 0, Direction.SUD, "vert"),
    Robot("Robo jaune", 8, 8, Direction.NORD, "jaune"),
]

# Chaque drapeau est une instance de la classe Drapeau, associée à sa case.
drapeaux = [
    (Drapeau("rouge"), 1, 2),
    (Drapeau("jaune"), 8, 4),
    (Drapeau("bleu"), 5, 8),
]

def mur_present(x, y, direction):
    return direction in murs.get((x, y), set())


def passage_autorise(x, y, direction):
    """Indique si le déplacement ne traverse pas un mur."""
    dx, dy = direction.value
    nx, ny = x + dx, y + dy

    if not (0 <= nx < nb_colonnes and 0 <= ny < nb_lignes):
        return False

    direction_opposee = {
        Direction.NORD: Direction.SUD,
        Direction.EST: Direction.OUEST,
        Direction.SUD: Direction.NORD,
        Direction.OUEST: Direction.EST,
    }
    return not (
        mur_present(x, y, direction)
        or mur_present(nx, ny, direction_opposee[direction])
    )


def case_valide(carte,x,y):
    if x<0 or x>= nb_colonnes or y<0 or y>= nb_lignes:
        return False
    return carte[y][x] != "trou"


def deplacer_robot(robot, direction):
    """Déplace un robot avec sa méthode deplacer si le passage est libre."""
    nx = robot.x + direction.value[0]
    ny = robot.y + direction.value[1]
    if not case_valide(carte, nx, ny):
        return
    if not passage_autorise(robot.x, robot.y, direction):
        return
    if any(
        autre is not robot and autre.x == nx and autre.y == ny
        for autre in robots
    ):
        return
    robot.deplacer(direction)


def deplacement_depuis_tapis(x, y, type_tapis):
    if type_tapis=="tapis_droite":
        return x+1,y
    if type_tapis=="tapis_gauche":
        return x-1,y
    if type_tapis =="tapis_haut":
        return x, y-1
    if type_tapis== "tapis_bas":
        return x,y+1
    return x,y

def animer_tapis_droite(image, offset):
    largeur, hauteur = image.get_size()
    surf = pygame.Surface((largeur, hauteur), pygame.SRCALPHA)
    surf.blit(image, (offset, 0))
    surf.blit(image, (offset - largeur, 0))
    return surf

def animer_tapis_gauche(image, offset):
    largeur, hauteur = image.get_size()
    surf = pygame.Surface((largeur, hauteur), pygame.SRCALPHA)
    surf.blit(image, (-offset, 0))
    surf.blit(image, (-offset + largeur, 0))
    return surf

def animer_tapis_haut(image, offset):
    largeur, hauteur = image.get_size()
    surf = pygame.Surface((largeur, hauteur), pygame.SRCALPHA)
    surf.blit(image, (0, -offset))
    surf.blit(image, (0, -offset + hauteur))
    return surf

def animer_tapis_bas(image, offset):
    largeur, hauteur = image.get_size()
    surf = pygame.Surface((largeur, hauteur), pygame.SRCALPHA)
    surf.blit(image, (0, offset))
    surf.blit(image, (0, offset - hauteur))
    return surf


offset_tapis = 0
vitesse_tapis = 1
robot_selectionne = 0
test_visuel_en_cours = False
test_visuel_termine = False
test_visuel_etape = 0
prochaine_etape_test = 0
message_test = "Appuyez sur T pour lancer le test visuel"

sequence_test = [
    (0, Direction.EST),
    (1, Direction.SUD),
    (2, Direction.OUEST),
    (3, Direction.NORD),
]


def demarrer_test_visuel():
    global test_visuel_en_cours, test_visuel_termine
    global test_visuel_etape, prochaine_etape_test, message_test

    positions_initiales = [(9, 3), (0, 7), (1, 0), (8, 8)]
    for robot, (x, y) in zip(robots, positions_initiales):
        robot.x, robot.y = x, y
        robot.est_detruit = False
    test_visuel_en_cours = True
    test_visuel_termine = False
    test_visuel_etape = 0
    prochaine_etape_test = pygame.time.get_ticks()
    message_test = "Test en cours..."


def executer_etape_test():
    global test_visuel_en_cours, test_visuel_termine
    global test_visuel_etape, prochaine_etape_test, message_test

    if test_visuel_etape >= len(sequence_test):
        test_visuel_en_cours = False
        test_visuel_termine = True
        message_test = "Test termine : deplacements reussis"
        return

    index_robot, direction = sequence_test[test_visuel_etape]
    robot = robots[index_robot]
    ancienne_position = (robot.x, robot.y)
    deplacer_robot(robot, direction)
    nouvelle_position = (robot.x, robot.y)
    if ancienne_position == nouvelle_position:
        test_visuel_en_cours = False
        test_visuel_termine = True
        message_test = "Test echoue : deplacement bloque"
        return

    test_visuel_etape += 1
    prochaine_etape_test = pygame.time.get_ticks() + 700


#boucle principale
en_cours=True
while en_cours:
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            en_cours=False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_t and not test_visuel_en_cours:
                demarrer_test_visuel()
                continue
            directions = {
                pygame.K_UP: Direction.NORD,
                pygame.K_z: Direction.NORD,
                pygame.K_RIGHT: Direction.EST,
                pygame.K_d: Direction.EST,
                pygame.K_DOWN: Direction.SUD,
                pygame.K_s: Direction.SUD,
                pygame.K_LEFT: Direction.OUEST,
                pygame.K_q: Direction.OUEST,
            }
            touches_selection = {
                pygame.K_1: 0,
                pygame.K_2: 1,
                pygame.K_3: 2,
                pygame.K_4: 3,
            }
            if event.key in touches_selection:
                robot_selectionne = touches_selection[event.key]
            elif event.key in directions:
                deplacer_robot(robots[robot_selectionne], directions[event.key])

    if test_visuel_en_cours and pygame.time.get_ticks() >= prochaine_etape_test:
        executer_etape_test()
    # Logique des tapis : les coordonnées sont mises à jour sur les objets
    # Robot, et non dans la représentation graphique de la carte.
    deplaces = set()
    for robot in robots:
        rx, ry = robot.x, robot.y
        if (rx, ry) in deplaces or not case_valide(carte, rx, ry):
            continue
        if carte[ry][rx] in ("tapis_droite","tapis_gauche","tapis_haut","tapis_bas"):
            nx, ny = deplacement_depuis_tapis(rx, ry, carte[ry][rx])
            if not case_valide(carte, nx, ny):
                continue
            direction_tapis = {
                "tapis_droite": Direction.EST,
                "tapis_gauche": Direction.OUEST,
                "tapis_haut": Direction.NORD,
                "tapis_bas": Direction.SUD,
            }[carte[ry][rx]]
            if not passage_autorise(rx, ry, direction_tapis):
                continue
            cible = carte[ny][nx]
            if cible not in ("vide", "trou"):
                continue
            if any(other.x == nx and other.y == ny for other in robots):
                continue
            robot.deplacer(direction_tapis)
            deplaces.add((nx, ny))

    offset_tapis = (offset_tapis + vitesse_tapis) % taille_case


    #dessiner la carte
    for ligne in range (nb_lignes):
        for colonne in range (nb_colonnes):
            type_case= carte[ligne][colonne]

            #calcul de la position de la case
            x= colonne * taille_case
            y= ligne * taille_case
        
            if type_case == "vide":
                pygame.draw.rect(fenetre, vide, (x, y, taille_case, taille_case))
            else:
                if type_case == "tapis_droite":
                    img = animer_tapis_droite(images["tapis_droite"], offset_tapis)
                    fenetre.blit(img, (x, y))

                elif type_case == "tapis_gauche":
                    img = animer_tapis_gauche(images["tapis_gauche"], offset_tapis)
                    fenetre.blit(img, (x, y))

                elif type_case == "tapis_haut":
                    img = animer_tapis_haut(images["tapis_haut"], offset_tapis)
                    fenetre.blit(img, (x, y))

                elif type_case == "tapis_bas":
                    img = animer_tapis_bas(images["tapis_bas"], offset_tapis)
                    fenetre.blit(img, (x, y))

                else:
                    fenetre.blit(images[type_case], (x, y))


            pygame.draw.rect(fenetre, (50, 50, 50), (x, y, taille_case, taille_case), 1)

            # Dessine uniquement les côtés où un mur est présent.
            epaisseur_mur = 8
            couleur_mur = (40, 40, 40)
            segments_murs = {
                Direction.NORD: ((x, y), (x + taille_case, y)),
                Direction.EST: ((x + taille_case, y), (x + taille_case, y + taille_case)),
                Direction.SUD: ((x, y + taille_case), (x + taille_case, y + taille_case)),
                Direction.OUEST: ((x, y), (x, y + taille_case)),
            }
            for direction in murs.get((colonne, ligne), set()):
                pygame.draw.line(
                    fenetre,
                    couleur_mur,
                    *segments_murs[direction],
                    epaisseur_mur,
                )

    # Les drapeaux sont dessinés au-dessus du contenu des cases.
    for drapeau, colonne, ligne in drapeaux:
        fenetre.blit(
            images["drapeau"],
            (colonne * taille_case, ligne * taille_case),
        )

    # Les robots sont dessinés au-dessus du contenu de leur case.
    for robot in robots:
        if not robot.est_detruit:
            fenetre.blit(
                images["robot"],
                (robot.x * taille_case, robot.y * taille_case),
            )

    police = pygame.font.Font(None, 26)
    texte_test = police.render(message_test, True, (20, 20, 20))
    fenetre.blit(texte_test, (8, 8))

    #mettre a jour l'affichage
    pygame.display.flip()

#quitter pygame
pygame.quit()
