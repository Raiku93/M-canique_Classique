import pygame
import sys
import math

# Initialisation de Pygame
pygame.init()

# Dimensions de l'écran
largeur = 800
hauteur = 600
ecran = pygame.display.set_mode((largeur, hauteur))
pygame.display.set_caption("Simulateur Physique avec Vecteurs")

# Couleurs
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
ROUGE = (255, 0, 0)
VERT = (0, 255, 0) # Utilisé pour le vecteur accélération
BLEU = (0, 0, 255) # Utilisé pour le vecteur vitesse
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
    def __init__(self, x, y, couleur, coefficient_restitution=1.0):
        self.x = x
        self.y = y
        self.couleur = couleur
        self.vx = 0  # Vitesse en x
        self.vy = 0  # Vitesse en y
        self.ax = 0  # Accélération en x
        self.ay = 0  # Accélération en y
        self.coefficient_restitution = coefficient_restitution

        # Facteurs d'échelle pour la visualisation des vecteurs (ajustez si besoin)
        self.echelle_vitesse = 0.5  # Longueur du vecteur vitesse = magnitude * echelle_vitesse
        self.echelle_acceleration = 0.3 # Longueur du vecteur accélération = magnitude * echelle_acceleration

    def deplacer(self, dt):
        self.vx += self.ax * dt
        self.vy += self.ay * dt
        self.x += self.vx * dt
        self.y += self.vy * dt

    def dessiner(self, surface):
        raise NotImplementedError("La méthode dessiner doit être implémentée par les sous-classes.")

    def get_centre(self):
        # Par défaut, le point (x,y) est le centre (utile pour les objets ponctuels ou si surchargé)
        # Pour les formes, cette méthode sera surchargée
        return self.x, self.y

    def dessiner_vecteurs(self, surface):
        centre_x, centre_y = self.get_centre()
        longueur_pointe = 8
        epaisseur_vecteur = 2

        # Dessiner le vecteur vitesse (en bleu)
        fin_vx = centre_x + self.vx * self.echelle_vitesse
        fin_vy = centre_y + self.vy * self.echelle_vitesse
        pygame.draw.line(surface, BLEU, (int(centre_x), int(centre_y)), (int(fin_vx), int(fin_vy)), epaisseur_vecteur)
        
        magnitude_v = math.sqrt(self.vx**2 + self.vy**2)
        if magnitude_v > 0.01: # Éviter atan2(0,0) et dessiner pour des vecteurs non nuls
            angle_v = math.atan2(self.vy, self.vx)
            pygame.draw.line(surface, BLEU, (int(fin_vx), int(fin_vy)), (int(fin_vx - longueur_pointe * math.cos(angle_v - math.pi / 6)), int(fin_vy - longueur_pointe * math.sin(angle_v - math.pi / 6))), epaisseur_vecteur)
            pygame.draw.line(surface, BLEU, (int(fin_vx), int(fin_vy)), (int(fin_vx - longueur_pointe * math.cos(angle_v + math.pi / 6)), int(fin_vy - longueur_pointe * math.sin(angle_v + math.pi / 6))), epaisseur_vecteur)

        # Dessiner le vecteur accélération (en vert)
        fin_ax = centre_x + self.ax * self.echelle_acceleration
        fin_ay = centre_y + self.ay * self.echelle_acceleration
        pygame.draw.line(surface, VERT, (int(centre_x), int(centre_y)), (int(fin_ax), int(fin_ay)), epaisseur_vecteur)

        magnitude_a = math.sqrt(self.ax**2 + self.ay**2)
        if magnitude_a > 0.01: # Éviter atan2(0,0) et dessiner pour des vecteurs non nuls
            angle_a = math.atan2(self.ay, self.ax)
            pygame.draw.line(surface, VERT, (int(fin_ax), int(fin_ay)), (int(fin_ax - longueur_pointe * math.cos(angle_a - math.pi / 6)), int(fin_ay - longueur_pointe * math.sin(angle_a - math.pi / 6))), epaisseur_vecteur)
            pygame.draw.line(surface, VERT, (int(fin_ax), int(fin_ay)), (int(fin_ax - longueur_pointe * math.cos(angle_a + math.pi / 6)), int(fin_ay - longueur_pointe * math.sin(angle_a + math.pi / 6))), epaisseur_vecteur)

    def collision(self, autre_objet):
        raise NotImplementedError("La méthode collision doit être implémentée par les sous-classes.")

    def gestion_collision(self, autre_objet):
        pass

# Classe pour les cercles
class Cercle(ObjetPhysique):
    def __init__(self, x, y, rayon, couleur, coefficient_restitution=0.8):
        super().__init__(x, y, couleur, coefficient_restitution)
        self.rayon = rayon
        self.masse = math.pi * rayon**2 # Masse proportionnelle à l'aire (densité = 1)

    def dessiner(self, surface):
        pygame.draw.circle(surface, self.couleur, (int(self.x), int(self.y)), self.rayon)

    def get_centre(self):
        return self.x, self.y

    def collision(self, autre_objet):
        if isinstance(autre_objet, Cercle):
            distance_centre = math.sqrt((self.x - autre_objet.x)**2 + (self.y - autre_objet.y)**2)
            return distance_centre < self.rayon + autre_objet.rayon
        elif isinstance(autre_objet, Carre):
            # Le point le plus proche sur le carré du centre du cercle
            closest_x = max(autre_objet.x, min(self.x, autre_objet.x + autre_objet.taille))
            closest_y = max(autre_objet.y, min(self.y, autre_objet.y + autre_objet.taille))
            distance_sq = (self.x - closest_x)**2 + (self.y - closest_y)**2
            return distance_sq < self.rayon**2
        elif isinstance(autre_objet, Rectangle):
            closest_x = max(autre_objet.x, min(self.x, autre_objet.x + autre_objet.largeur))
            closest_y = max(autre_objet.y, min(self.y, autre_objet.y + autre_objet.hauteur))
            distance_sq = (self.x - closest_x)**2 + (self.y - closest_y)**2
            return distance_sq < self.rayon**2
        return False

    def gestion_collision(self, autre_objet):
        if isinstance(autre_objet, Cercle):
            # S'assurer que les deux objets ont une masse
            if not hasattr(self, 'masse'): self.masse = 1 
            if not hasattr(autre_objet, 'masse'): autre_objet.masse = 1

            distance_centre = math.sqrt((self.x - autre_objet.x)**2 + (self.y - autre_objet.y)**2)
            if distance_centre == 0: # Éviter la division par zéro si superposés parfaitement
                return 

            nx = (autre_objet.x - self.x) / distance_centre
            ny = (autre_objet.y - self.y) / distance_centre
            
            # Vitesses le long de la normale
            v1n = self.vx * nx + self.vy * ny
            v2n = autre_objet.vx * nx + autre_objet.vy * ny

            e = min(self.coefficient_restitution, autre_objet.coefficient_restitution)
            
            # Calcul des nouvelles vitesses le long de la normale
            # Formule de collision 1D pour masses m1, m2 et vitesses u1, u2:
            # v1_new = (m1*u1 + m2*u2 + m2*e*(u2-u1)) / (m1+m2)
            # v2_new = (m1*u1 + m2*u2 + m1*e*(u1-u2)) / (m1+m2)
            m1 = self.masse
            m2 = autre_objet.masse

            v1n_new = (m1 * v1n + m2 * v2n + m2 * e * (v2n - v1n)) / (m1 + m2)
            v2n_new = (m1 * v1n + m2 * v2n + m1 * e * (v1n - v2n)) / (m1 + m2)

            # Mettre à jour les vitesses des objets
            self.vx += (v1n_new - v1n) * nx
            self.vy += (v1n_new - v1n) * ny
            autre_objet.vx += (v2n_new - v2n) * nx
            autre_objet.vy += (v2n_new - v2n) * ny

            # Résoudre le chevauchement
            overlap = 0.5 * (self.rayon + autre_objet.rayon - distance_centre)
            if overlap > 0: # S'assurer qu'il y a bien chevauchement à corriger
                self.x -= overlap * nx
                self.y -= overlap * ny
                autre_objet.x += overlap * nx
                autre_objet.y += overlap * ny


# Classe pour les carrés
class Carre(ObjetPhysique):
    def __init__(self, x, y, taille, couleur, coefficient_restitution=0.7):
        super().__init__(x, y, couleur, coefficient_restitution)
        self.taille = taille
        self.masse = taille**2 # Masse proportionnelle à l'aire

    def dessiner(self, surface):
        pygame.draw.rect(surface, self.couleur, (int(self.x), int(self.y), self.taille, self.taille))

    def get_centre(self):
        return self.x + self.taille / 2, self.y + self.taille / 2

    def collision(self, autre_objet):
        if isinstance(autre_objet, Carre):
            return (self.x < autre_objet.x + autre_objet.taille and
                    self.x + self.taille > autre_objet.x and
                    self.y < autre_objet.y + autre_objet.taille and
                    self.y + self.taille > autre_objet.y)
        elif isinstance(autre_objet, Cercle):
            return autre_objet.collision(self) # Déléguer à la méthode du cercle
        elif isinstance(autre_objet, Rectangle):
            return (self.x < autre_objet.x + autre_objet.largeur and
                    self.x + self.taille > autre_objet.x and
                    self.y < autre_objet.y + autre_objet.hauteur and
                    self.y + self.taille > autre_objet.y)
        return False

    def gestion_collision(self, autre_objet):
        if isinstance(autre_objet, Carre):
            # Simplifié, sans utiliser la masse explicitement ici
            v1x, v1y = self.vx, self.vy
            v2x, v2y = autre_objet.vx, autre_objet.vy
            e = min(self.coefficient_restitution, autre_objet.coefficient_restitution)
            
            # Échange simple de vitesses (comme si les masses étaient égales)
            self.vx, autre_objet.vx = e * v2x, e * v1x
            self.vy, autre_objet.vy = e * v2y, e * v1y

            # Ajustement de position pour éviter le chevauchement (méthode de séparation par axe)
            overlap_x = (self.taille / 2 + autre_objet.taille / 2) - abs((self.x + self.taille/2) - (autre_objet.x + autre_objet.taille/2))
            overlap_y = (self.taille / 2 + autre_objet.taille / 2) - abs((self.y + self.taille/2) - (autre_objet.y + autre_objet.taille/2))

            if overlap_x > 0 and overlap_y > 0:
                dx = (autre_objet.x + autre_objet.taille/2) - (self.x + self.taille/2)
                dy = (autre_objet.y + autre_objet.taille/2) - (self.y + self.taille/2)

                if overlap_x < overlap_y:
                    if dx > 0: # L'autre objet est à droite
                        self.x -= overlap_x / 2
                        autre_objet.x += overlap_x / 2
                    else: # L'autre objet est à gauche
                        self.x += overlap_x / 2
                        autre_objet.x -= overlap_x / 2
                else:
                    if dy > 0: # L'autre objet est en dessous
                        self.y -= overlap_y / 2
                        autre_objet.y += overlap_y / 2
                    else: # L'autre objet est au-dessus
                        self.y += overlap_y / 2
                        autre_objet.y -= overlap_y / 2


# Classe pour les rectangles
class Rectangle(ObjetPhysique):
    def __init__(self, x, y, largeur, hauteur, couleur, coefficient_restitution=0.6):
        super().__init__(x, y, couleur, coefficient_restitution)
        self.largeur = largeur
        self.hauteur = hauteur
        self.masse = largeur * hauteur # Masse proportionnelle à l'aire

    def dessiner(self, surface):
        pygame.draw.rect(surface, self.couleur, (int(self.x), int(self.y), self.largeur, self.hauteur))

    def get_centre(self):
        return self.x + self.largeur / 2, self.y + self.hauteur / 2

    def collision(self, autre_objet):
        if isinstance(autre_objet, Rectangle):
            return (self.x < autre_objet.x + autre_objet.largeur and
                    self.x + self.largeur > autre_objet.x and
                    self.y < autre_objet.y + autre_objet.hauteur and
                    self.y + self.hauteur > autre_objet.y)
        elif isinstance(autre_objet, Cercle):
            return autre_objet.collision(self)
        elif isinstance(autre_objet, Carre):
            return autre_objet.collision(self) # Déléguer au carré ou réimplémenter
        return False

    def gestion_collision(self, autre_objet):
         if isinstance(autre_objet, Rectangle):
            v1x, v1y = self.vx, self.vy
            v2x, v2y = autre_objet.vx, autre_objet.vy
            e = min(self.coefficient_restitution, autre_objet.coefficient_restitution)
            
            self.vx, autre_objet.vx = e * v2x, e * v1x
            self.vy, autre_objet.vy = e * v2y, e * v1y
            
            # Ajustement de position
            overlap_x = (self.largeur / 2 + autre_objet.largeur / 2) - abs((self.x + self.largeur/2) - (autre_objet.x + autre_objet.largeur/2))
            overlap_y = (self.hauteur / 2 + autre_objet.hauteur / 2) - abs((self.y + self.hauteur/2) - (autre_objet.y + autre_objet.hauteur/2))

            if overlap_x > 0 and overlap_y > 0:
                dx = (autre_objet.x + autre_objet.largeur/2) - (self.x + self.largeur/2)
                dy = (autre_objet.y + autre_objet.hauteur/2) - (self.y + self.hauteur/2)

                if overlap_x < overlap_y:
                    if dx > 0:
                        self.x -= overlap_x / 2
                        autre_objet.x += overlap_x / 2
                    else:
                        self.x += overlap_x / 2
                        autre_objet.x -= overlap_x / 2
                else:
                    if dy > 0:
                        self.y -= overlap_y / 2
                        autre_objet.y += overlap_y / 2
                    else:
                        self.y += overlap_y / 2
                        autre_objet.y -= overlap_y / 2


# Création du sol
sol = Sol(hauteur - 50, 50, GRIS, 0.3)

# Liste pour stocker les objets physiques
objets = []

# Création d'objets
cercle1 = Cercle(150, 100, 30, NOIR, 0.5) # Changé en ROUGE pour mieux le voir
cercle1.vx = 50
cercle1.vy = 0
cercle1.ay = 98 # Simule la gravité (pixels/s^2)
cercle1.masse = 5 # Masse spécifique
objets.append(cercle1)

cercle2 = Cercle(50, 150, 20, NOIR, 0.5) # Changé en BLEU
cercle2.vx = 70
cercle2.vy = -20
cercle2.ay = 98
cercle2.masse = 10 # Masse spécifique plus grande
objets.append(cercle2)

cercle3 = Cercle(330, 80, 25, VERT, 0.7) # Changé en VERT
cercle3.vx = -70
cercle3.vy = 10
cercle3.ay = 98
cercle3.masse = 1
objets.append(cercle3)

# carre1 = Carre(400, 100, 40, NOIR, 0.7)
# carre1.vx = -30
# carre1.ay = 98
# objets.append(carre1)

# Boucle principale du jeu
en_cours = True
clock = pygame.time.Clock()
FPS = 60 # Frames par seconde

while en_cours:
    dt = 1 / FPS # Delta de temps en secondes

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            en_cours = False

    # Effacer l'écran
    ecran.fill(BLANC)

    # Dessiner le sol
    sol.dessiner(ecran)

    # Mettre à jour et dessiner les objets
    for objet in objets:
        # Appliquer la gravité si ce n'est pas déjà une accélération constante
        # Si vous voulez que ay soit toujours la gravité, vous pouvez le définir ici.
        # Pour l'instant, on suppose que ay est correctement géré (par ex. initialisé à la gravité)
        # objet.ay = 98 # Si vous voulez une gravité constante appliquée ici
        
        objet.deplacer(dt)
        objet.dessiner(ecran)
        objet.dessiner_vecteurs(ecran) # <<< DESSIN DES VECTEURS ICI

        # Gestion des collisions avec les bords
        if isinstance(objet, Cercle):
            if objet.x + objet.rayon > largeur:
                objet.x = largeur - objet.rayon
                objet.vx *= -objet.coefficient_restitution
            elif objet.x - objet.rayon < 0:
                objet.x = objet.rayon
                objet.vx *= -objet.coefficient_restitution
            
            if objet.y + objet.rayon > sol.y:
                objet.y = sol.y - objet.rayon
                objet.vy *= -sol.coefficient_restitution
                # Optionnel: friction au sol
                # objet.vx *= 0.98 
            elif objet.y - objet.rayon < 0 : # Plafond
                objet.y = objet.rayon
                objet.vy *= -objet.coefficient_restitution

        elif isinstance(objet, (Carre, Rectangle)): # Traitement unifié pour Carre et Rectangle
            obj_largeur = objet.taille if isinstance(objet, Carre) else objet.largeur
            obj_hauteur = objet.taille if isinstance(objet, Carre) else objet.hauteur

            if objet.x + obj_largeur > largeur:
                objet.x = largeur - obj_largeur
                objet.vx *= -objet.coefficient_restitution
            elif objet.x < 0:
                objet.x = 0
                objet.vx *= -objet.coefficient_restitution

            if objet.y + obj_hauteur > sol.y:
                objet.y = sol.y - obj_hauteur
                objet.vy *= -sol.coefficient_restitution
                # objet.vx *= 0.98
            elif objet.y < 0: # Plafond
                objet.y = 0
                objet.vy *= -objet.coefficient_restitution
        
        # La ligne "objet.ay = objet.ay" a été retirée car elle n'avait pas d'effet.
        # Si la gravité doit être toujours appliquée, initialisez ay et ne le modifiez pas,
        # ou réaffectez-le à chaque image avant deplacer().

    # Vérifier les collisions entre les objets
    for i in range(len(objets)):
        for j in range(i + 1, len(objets)):
            if objets[i].collision(objets[j]):
                objets[i].gestion_collision(objets[j])
                # Note: gestion_collision peut aussi appeler la gestion de l'autre objet si nécessaire,
                # ou être symétrique. Pour l'instant, seul le premier objet gère.

    # Mettre à jour l'affichage
    pygame.display.flip()

    # Contrôler la vitesse de la boucle
    clock.tick(FPS)

# Quitter Pygame
pygame.quit()
sys.exit()
