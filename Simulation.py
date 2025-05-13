import pygame
import sys
import math

# Initialisation de Pygame
pygame.init()

# Dimensions de l'écran
largeur = 800
hauteur = 600
ecran = pygame.display.set_mode((largeur, hauteur))
pygame.display.set_caption("Simulateur Physique")

# Couleurs
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
ROUGE = (255, 0, 0)
VERT = (0, 255, 0)
BLEU = (0, 0, 255)
GRIS = (200, 200, 200)

# Classe pour représenter le sol
class Sol:
    def __init__(self, y, hauteur, couleur, coefficient_restitution):
        self.y = y
        self.hauteur = hauteur
        self.couleur = couleur
        self.coefficient_restitution = coefficient_restitution

    def dessiner(self, surface):
        pygame.draw.rect(surface, self.couleur, (0, self.y, largeur, self.hauteur))

# Classe de base pour les objets physiques
class ObjetPhysique:
    def __init__(self, x, y, couleur):
        self.x = x
        self.y = y
        self.couleur = couleur
        self.vx = 0  # Vitesse en x
        self.vy = 0  # Vitesse en y
        self.ax = 0  # Accélération en x
        self.ay = 0  # Accélération en y

    def deplacer(self, dt):
        # Mise à jour de la vitesse en fonction de l'accélération
        self.vx += self.ax * dt
        self.vy += self.ay * dt

        # Mise à jour de la position en fonction de la vitesse
        self.x += self.vx * dt
        self.y += self.vy * dt

    def dessiner(self, surface):
        raise NotImplementedError("La méthode dessiner doit être implémentée par les sous-classes.")

    def collision(self, autre_objet):
        raise NotImplementedError("La méthode collision doit être implémentée par les sous-classes.")

    def gestion_collision(self, autre_objet):
        # Méthode à surcharger pour gérer la réaction à une collision
        pass

# Classe pour les cercles
class Cercle(ObjetPhysique):
    def __init__(self, x, y, rayon, couleur):
        super().__init__(x, y, couleur)
        self.rayon = rayon

    def dessiner(self, surface):
        pygame.draw.circle(surface, self.couleur, (int(self.x), int(self.y)), self.rayon)

    def collision(self, autre_objet):
        if isinstance(autre_objet, Cercle):
            distance_centre = math.sqrt((self.x - autre_objet.x)**2 + (self.y - autre_objet.y)**2)
            return distance_centre < self.rayon + autre_objet.rayon
        elif isinstance(autre_objet, Carre):
            dx = max(autre_objet.x - self.x, 0, self.x - (autre_objet.x + autre_objet.taille))
            dy = max(autre_objet.y - self.y, 0, self.y - (autre_objet.y + autre_objet.taille))
            return (dx**2 + dy**2)**0.5 < self.rayon
        elif isinstance(autre_objet, Rectangle):
            dx = max(autre_objet.x - self.x, 0, self.x - (autre_objet.x + autre_objet.largeur))
            dy = max(autre_objet.y - self.y, 0, self.y - (autre_objet.y + autre_objet.hauteur))
            return (dx**2 + dy**2)**0.5 < self.rayon
        return False

    def gestion_collision(self, autre_objet):
        if isinstance(autre_objet, Cercle):
            distance_centre = math.sqrt((self.x - autre_objet.x)**2 + (self.y - autre_objet.y)**2)
            if distance_centre != 0:
                nx = (autre_objet.x - self.x) / distance_centre
                ny = (autre_objet.y - self.y) / distance_centre
                v1n = self.vx * nx + self.vy * ny
                v2n = autre_objet.vx * nx + autre_objet.vy * ny

                p = 2 * (v1n - v2n) / (1 + 1)  # Masse supposée égale à 1

                self.vx -= p * nx
                self.vy -= p * ny
                autre_objet.vx += p * nx
                autre_objet.vy += p * ny
                overlap = 0.5 * (self.rayon + autre_objet.rayon - distance_centre)
                self.x -= overlap * nx
                self.y -= overlap * ny
                autre_objet.x += overlap * nx
                autre_objet.y += overlap * ny

# Classe pour les carrés
class Carre(ObjetPhysique):
    def __init__(self, x, y, taille, couleur):
        super().__init__(x, y, couleur)
        self.taille = taille

    def dessiner(self, surface):
        pygame.draw.rect(surface, self.couleur, (int(self.x), int(self.y), self.taille, self.taille))

    def collision(self, autre_objet):
        if isinstance(autre_objet, Carre):
            return (self.x < autre_objet.x + autre_objet.taille and
                    self.x + self.taille > autre_objet.x and
                    self.y < autre_objet.y + autre_objet.taille and
                    self.y + self.taille > autre_objet.y)
        elif isinstance(autre_objet, Cercle):
            return autre_objet.collision(self)
        elif isinstance(autre_objet, Rectangle):
            return (self.x < autre_objet.x + autre_objet.largeur and
                    self.x + self.taille > autre_objet.x and
                    self.y < autre_objet.y + autre_objet.hauteur and
                    self.y + self.taille > autre_objet.y)
        return False

    def gestion_collision(self, autre_objet):
        if isinstance(autre_objet, Carre):
            self.vx, autre_objet.vx = autre_objet.vx, self.vx
            self.vy, autre_objet.vy = autre_objet.vy, self.vy
            delta_x = (self.x + self.taille / 2) - (autre_objet.x + autre_objet.taille / 2)
            delta_y = (self.y + self.taille / 2) - (autre_objet.y + autre_objet.taille / 2)
            if abs(delta_x) > abs(delta_y):
                if delta_x > 0:
                    self.x = autre_objet.x + autre_objet.taille
                else:
                    self.x = autre_objet.x - self.taille
            else:
                if delta_y > 0:
                    self.y = autre_objet.y + autre_objet.taille
                else:
                    self.y = autre_objet.y - self.taille

# Classe pour les rectangles
class Rectangle(ObjetPhysique):
    def __init__(self, x, y, largeur, hauteur, couleur):
        super().__init__(x, y, couleur)
        self.largeur = largeur
        self.hauteur = hauteur

    def dessiner(self, surface):
        pygame.draw.rect(surface, self.couleur, (int(self.x), int(self.y), self.largeur, self.hauteur))

    def collision(self, autre_objet):
        if isinstance(autre_objet, Rectangle):
            return (self.x < autre_objet.x + autre_objet.largeur and
                    self.x + self.largeur > autre_objet.x and
                    self.y < autre_objet.y + autre_objet.hauteur and
                    self.y + self.hauteur > autre_objet.y)
        elif isinstance(autre_objet, Cercle):
            return autre_objet.collision(self)
        elif isinstance(autre_objet, Carre):
            return autre_objet.collision(self)
        return False

    def gestion_collision(self, autre_objet):
        if isinstance(autre_objet, Rectangle):
            self.vx, autre_objet.vx = autre_objet.vx, self.vx
            self.vy, autre_objet.vy = autre_objet.vy, self.vy
            delta_x = (self.x + self.largeur / 2) - (autre_objet.x + autre_objet.largeur / 2)
            delta_y = (self.y + self.hauteur / 2) - (autre_objet.y + autre_objet.hauteur / 2)
            if abs(delta_x) > abs(delta_y):
                if delta_x > 0:
                    self.x = autre_objet.x + autre_objet.largeur
                else:
                    self.x = autre_objet.x - self.largeur
            else:
                if delta_y > 0:
                    self.y = autre_objet.y + autre_objet.hauteur
                else:
                    self.y = autre_objet.y - self.hauteur

# Création du sol
sol = Sol(hauteur - 50, 50, GRIS, 0.2) # Sol gris avec un coefficient de restitution de 0.8

# Liste pour stocker les objets physiques
objets = []

# Création d'objets
cercle1 = Cercle(100, 100, 30, NOIR)
cercle1.vx = 50
cercle1.vy = 0
cercle1.ay = 40
objets.append(cercle1)

cercle2 = Cercle(50, 100, 30, NOIR)
cercle2.vx = -100
cercle2.vy = 0
cercle2.ay = 40
objets.append(cercle2)

cercle3 = Cercle(50, 150, 30, NOIR)
cercle3.vx = -100
cercle3.vy = 1
cercle3.ay = 40
objets.append(cercle3)

# Boucle principale du jeu
en_cours = True
clock = pygame.time.Clock()
dt = 0.016 # Delta de temps (environ 60 FPS)

while en_cours:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            en_cours = False

    # Effacer l'écran
    ecran.fill(BLANC)

    # Dessiner le sol
    sol.dessiner(ecran)

    # Mettre à jour et dessiner les objets
    for objet in objets:
        objet.deplacer(dt)
        objet.dessiner(ecran)

        # Gestion des collisions avec les bords gauche et droit
        if isinstance(objet, (Cercle, Carre, Rectangle)):
            if isinstance(objet, Cercle):
                if objet.x + objet.rayon > largeur or objet.x - objet.rayon < 0:
                    objet.vx *= -1
            elif isinstance(objet, Carre):
                if objet.x + objet.taille > largeur or objet.x < 0:
                    objet.vx *= -1
            elif isinstance(objet, Rectangle):
                if objet.x + objet.largeur > largeur or objet.x < 0:
                    objet.vx *= -1

            # Gestion de la collision avec le sol
            if isinstance(objet, Cercle):
                if objet.y + objet.rayon > sol.y:
                    objet.y = sol.y - objet.rayon
                    objet.vy *= -sol.coefficient_restitution
                    objet.ay = 0 # Supprimer l'accélération verticale après le rebond
            elif isinstance(objet, Carre):
                if objet.y + objet.taille > sol.y:
                    objet.y = sol.y - objet.taille
                    objet.vy *= -sol.coefficient_restitution
                    objet.ay = 0
            elif isinstance(objet, Rectangle):
                if objet.y + objet.hauteur > sol.y:
                    objet.y = sol.y - objet.hauteur
                    objet.vy *= -sol.coefficient_restitution
                    objet.ay = 0
            else:
                # Si l'objet n'est pas en contact avec le sol, réappliquer la gravité
                objet.ay = 40

    # Vérifier les collisions entre les objets
    for i in range(len(objets)):
        for j in range(i + 1, len(objets)):
            if objets[i].collision(objets[j]):
                objets[i].gestion_collision(objets[j])

    # Mettre à jour l'affichage
    pygame.display.flip()

    # Contrôler la vitesse de la boucle
    clock.tick(60)

# Quitter Pygame
pygame.quit()
sys.exit()
