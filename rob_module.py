from tkinter import *
from math import sin, cos, radians
from time import sleep

class Rob(object):
    
    ORI_KIND_CODES = ("N","E","S","O")
    ORI_ANGLES = {"EST":0, "SUD":90, "OUEST":180, "NORD":270}
    
    def __init__(self, jardin, x_init, y_init, orientation):
        """
        Jardin:jardin
        int:x_init : position x de la case initiale
        int:y_init : position y de la case initiale
        str:orientation : orientation NORD, SUD, EST ou OUEST
        """
        
        self.jardin = jardin
        self.x = x_init
        self.y = y_init
        self.orientation = orientation
        
        self.eye_size = self.jardin.cell_size/5 # Taille d'un oeil (px)
        self.eye_center_dist = self.jardin.cell_size*0.4 # distance centre robot - centre oeil (px)
        self.lateral_eyes_angle = 40 # angle centre oeil central - centres yeux latéraux
        
        self.plugged = False
        
    
    def eye_center(self, angle):
        """
        Retourne les coordonnées x et y (en px) du centre d'un oeil du robot
        pour un angle donné (0° à 360°, sens horaire, origine à 3h)
        Remarque : le sens est trigonométrique pour les axes x-y
        informatiques, et non mathématiques. 
        """
        
        x_eye = (self.x+0.5)*self.jardin.cell_size + self.eye_center_dist*cos(radians(angle))
        y_eye = (self.y+0.5)*self.jardin.cell_size + self.eye_center_dist*sin(radians(angle))
        
        return x_eye, y_eye
    
    
    def all_eye_centers(self, angle):
        """
        Retourne les 3 paires de coordonnées x et y des 3 yeux,
        sous la forme d'un tuple à 6 composants.
        """
        
        x_central_eye, y_central_eye = self.eye_center(angle)
        x_left_eye, y_left_eye = self.eye_center(angle - self.lateral_eyes_angle)
        x_right_eye, y_right_eye = self.eye_center(angle + self.lateral_eyes_angle)
        
        return (x_central_eye, y_central_eye,
                x_left_eye, y_left_eye,
                x_right_eye, y_right_eye)
        
    
    def draw(self):
        """
        Crée le dessin initial du robot
        """
        self.body_default_color = "#bfbfbf"
        self.eyes_default_color = "#ff3300"
        
        self.body = self.jardin.canvas.create_oval(
            self.jardin.cell_size*self.x,
            self.jardin.cell_size*self.y,
            self.jardin.cell_size*(self.x+1),
            self.jardin.cell_size*(self.y+1),
            fill=self.body_default_color)
        
        angle_rob = Rob.ORI_ANGLES[self.orientation]
        
        (x_central_eye, y_central_eye,
         x_left_eye, y_left_eye,
         x_right_eye, y_right_eye) = self.all_eye_centers(angle_rob)
        
        self.central_eye = self.jardin.canvas.create_oval(
            x_central_eye - self.eye_size/2, y_central_eye - self.eye_size/2,
            x_central_eye + self.eye_size/2, y_central_eye + self.eye_size/2,
            fill=self.eyes_default_color)
        
        self.left_eye = self.jardin.canvas.create_oval(
            x_left_eye - self.eye_size/2, y_left_eye - self.eye_size/2,
            x_left_eye + self.eye_size/2, y_left_eye + self.eye_size/2,
            fill=self.eyes_default_color)
        
        self.right_eye = self.jardin.canvas.create_oval(
            x_right_eye - self.eye_size/2, y_right_eye - self.eye_size/2,
            x_right_eye + self.eye_size/2, y_right_eye + self.eye_size/2,
            fill=self.eyes_default_color)
        
    
    def get_coords_case(self, direction):
        """
        Retourne les coordonnées d'une case située à proximité du robot
        str:direction : DEVANT, GAUCHE ou DROITE
        """
        
        return {("NORD", "DEVANT"):(self.x, self.y - 1),
                ("EST" , "DEVANT"):(self.x + 1, self.y),
                ("SUD" , "DEVANT"):(self.x, self.y + 1),
                ("OUEST","DEVANT"):(self.x - 1, self.y),
                
                ("NORD", "GAUCHE"):(self.x - 1, self.y),
                ("EST" , "GAUCHE"):(self.x, self.y - 1),
                ("SUD" , "GAUCHE"):(self.x + 1, self.y),
                ("OUEST","GAUCHE"):(self.x, self.y + 1),
                
                ("NORD", "DROITE"):(self.x + 1, self.y),
                ("EST" , "DROITE"):(self.x, self.y + 1),
                ("SUD" , "DROITE"):(self.x - 1, self.y),
                ("OUEST","DROITE"):(self.x, self.y - 1)}[
                    (self.orientation, direction)
                    ]
    
    
    def avancer(self, n_steps, dt):
        """
        Fait avancer Rob d'une case
        int:n_steps : le nombre d'étapes pour accomplir le déplacement
        int:dt : l'intervale de temps entre chaque étape
        """
        
        if self.plugged:
            raise Exception(
                "Rob a tenté d'avancer, mais il est branché, il ne peut plus bouger !")
        
        x_case_cible, y_case_cible = self.get_coords_case("DEVANT")
        
        if (not 0 <= x_case_cible <= self.jardin.largeur or
            not 0 <= y_case_cible <= self.jardin.hauteur or
            not self.jardin.get_case(x_case_cible, y_case_cible).kind
            in ("herbe", "borne")):
            self.collision()
        
        else:
            delta_x = (x_case_cible - self.x)/n_steps*self.jardin.cell_size
            delta_y = (y_case_cible - self.y)/n_steps*self.jardin.cell_size
            
            for _ in range(n_steps):
                for polygon in [self.body, self.central_eye,
                        self.left_eye, self.right_eye]:
                    self.jardin.canvas.move(polygon, delta_x, delta_y)
                
                self.jardin.update()
                sleep(dt)
        
            self.x = x_case_cible
            self.y = y_case_cible
            
            case_cible = self.jardin.get_case(x_case_cible, y_case_cible)
            case_cible.lawned = True
            self.jardin.canvas.itemconfig(case_cible.rect_id,
                                          fill = case_cible.get_color())
            self.jardin.update()
            
    
    def fissurer_devant(self):
        """
        Crée un dessin de fissure orienté dans le bloc dans lequel
        Rob a butté
        """
        
        x_case, y_case = self.get_coords_case("DEVANT")
        
        x_start, y_start, angle = {
            "NORD": ((x_case+0.5)*self.jardin.cell_size,
                     (y_case+1)*self.jardin.cell_size,
                     270),
            "EST": (x_case*self.jardin.cell_size,
                    (y_case+0.5)*self.jardin.cell_size,
                    0),
            "SUD": ((x_case+0.5)*self.jardin.cell_size,
                    y_case*self.jardin.cell_size,
                    90),
            "OUEST": ((x_case+1)*self.jardin.cell_size,
                      (y_case+0.5)*self.jardin.cell_size,
                      180)
            }[self.orientation]
        
        taille_1 = self.jardin.cell_size*0.4
        taille_2 = self.jardin.cell_size*0.2
        taille_3 = self.jardin.cell_size*0.3
        taille_0 = taille_1*1/4
        taille_4 = self.jardin.cell_size*0.3
        d_angle_12 = 150
        d_angle_23 = -130
        d_angle_14 = -60
        width = 2
        
        x2 = x_start+taille_1*cos(radians(angle))
        y2 = y_start+taille_1*sin(radians(angle))
        
        angle += d_angle_12
        
        x3 = x2+taille_2*cos(radians(angle))
        y3 = y2+taille_2*sin(radians(angle))
        
        angle += d_angle_23
        
        x4 = x3+taille_3*cos(radians(angle))
        y4 = y3+taille_3*sin(radians(angle))
        
        self.jardin.canvas.create_line(x_start, y_start, x2, y2,
                                       x3, y3, x4, y4, width = width)
        self.jardin.update()
        
        angle -= d_angle_12+d_angle_23
        
        x5 = x_start + taille_0*cos(radians(angle))
        y5 = y_start + taille_0*sin(radians(angle))
        
        angle += d_angle_14
        
        x6 = x5 + taille_4*cos(radians(angle))
        y6 = y5 + taille_4*sin(radians(angle))
        
        self.jardin.canvas.create_line(x5, y5, x6, y6, width = width)
        self.jardin.update()
    
    
    def collision(self):
        """
        Indique que Rob a buté contre un mur ou les frontières du jardin
        """
        
        self.fissurer_devant()
        
        blink_color = "#ffffff"
        final_color = "#000000"
        
        dt = 0.1
        
        self.blink(self.central_eye, blink_color, self.eyes_default_color, dt)
        sleep(dt)
        self.blink(self.central_eye, blink_color, final_color, dt)

        raise Exception("Rob a tenté d'entrer dans une case inaccessible !")
    
    
    def pivoter(self, direction, n_steps, dt):
        """
        Pivote Rob de 90° à gauche ou à droite
        str:direction : GAUCHE ou DROITE
        int:n_steps : le nombre d'étapes pour accomplir la rotation
        int:dt : l'intervale de temps entre chaque étape
        """
        
        if self.plugged:
            raise Exception(
                "Rob a tenté de pivoter, mais il est branché, il ne peut plus bouger !")
        
        angle_actuel = Rob.ORI_ANGLES[self.orientation]
        angle_cible = angle_actuel+90 if direction == "DROITE" else angle_actuel-90
        delta_angle = (angle_cible - angle_actuel)/n_steps
        
        (new_x_central_eye, new_y_central_eye,
         new_x_left_eye, new_y_left_eye,
         new_x_right_eye, new_y_right_eye) = self.all_eye_centers(angle_actuel)
        
        for _ in range(n_steps):
            
            x_central_eye, y_central_eye = new_x_central_eye, new_y_central_eye
            x_left_eye, y_left_eye = new_x_left_eye, new_y_left_eye
            x_right_eye, y_right_eye = new_x_right_eye, new_y_right_eye
            
            angle_actuel += delta_angle
            
            (new_x_central_eye, new_y_central_eye,
             new_x_left_eye, new_y_left_eye,
             new_x_right_eye, new_y_right_eye) = self.all_eye_centers(angle_actuel)
            
            self.jardin.canvas.move(self.central_eye,
                                    new_x_central_eye - x_central_eye,
                                    new_y_central_eye - y_central_eye)
            self.jardin.canvas.move(self.left_eye,
                                    new_x_left_eye - x_left_eye,
                                    new_y_left_eye - y_left_eye)
            self.jardin.canvas.move(self.right_eye,
                                    new_x_right_eye - x_right_eye,
                                    new_y_right_eye - y_right_eye)
            
            self.jardin.update()
            
            sleep(dt)
        
        
        orientation_cible = {("NORD","GAUCHE"):"OUEST",
                             ("NORD","DROITE"):"EST",
                             ("EST","GAUCHE"):"NORD",
                             ("EST","DROITE"):"SUD",
                             ("SUD","GAUCHE"):"EST",
                             ("SUD","DROITE"):"OUEST",
                             ("OUEST","GAUCHE"):"SUD",
                             ("OUEST","DROITE"):"NORD"}[
                                 (self.orientation, direction)
                                 ]
        
        self.orientation = orientation_cible
        
    
    def blink(self, eye, transit_color, final_color, dt):
        """
        Fait clignoter l'un des yeux du robot
        int:eye : l'identifiant de l'oeil à faire clignoter
        str:transit_color : le code-couleur de la couleur de clignotement
        str:final_color : le code-couleur de la couleur finale
        float:dt : la durée du clignotement
        """
        
        self.jardin.canvas.itemconfig(eye, fill = transit_color)
        self.jardin.update()
        sleep(dt)
        self.jardin.canvas.itemconfig(eye, fill = final_color)
        self.jardin.update()
    
    
    def detecter(self, direction, dt):
        """
        Indique en français le type de la case dans la direction demandée
        """
        detect_color = "#66ffff"
        
        if direction == "GAUCHE":
            self.blink(self.left_eye, detect_color, self.eyes_default_color, dt)
        elif direction == "DROITE":
            self.blink(self.right_eye, detect_color, self.eyes_default_color, dt)
        else:
            self.blink(self.central_eye, detect_color, self.eyes_default_color, dt)
        
        x_cible, y_cible = self.get_coords_case(direction)
        
        assert 0 <= x_cible <= self.jardin.largeur, "Rob ne voit pas au-delà des limites du jardin."
        assert 0 <= y_cible <= self.jardin.hauteur, "Rob ne voit pas au-delà des limites du jardin."
        
        case_cible = self.jardin.get_case(x_cible, y_cible)
        
        if case_cible.kind == "mur":
            return "mur"
        
        elif case_cible.kind == "borne":
            return "borne"
        
        elif case_cible.kind == "herbe":
            if case_cible.rock_here:
                return "caillou"
            elif case_cible.leaf_here:
                return "feuille"
            elif case_cible.lawned:
                return "herbe tondue"
            else:
                return "herbe haute"
        
        else:
            raise Exception("Rob a tenté de détecter un type de case inconnu")
        
    
    def changer_couleur_yeux(self, couleur_cible):
        """
        Change la couleur des trois yeux du robot vers couleur_cible
        """
        for eye in (self.left_eye, self.central_eye, self.right_eye):
            self.jardin.canvas.itemconfig(eye, fill = couleur_cible)
            self.jardin.update()
    
    
    def brancher(self):
        """
        Fait passer les yeux de Rob au vert
        pour simuler le fait qu'il est "en charge"
        Ne fonctionne que si Rob est sur une borne.
        """
        
        if self.jardin.get_case(self.x, self.y).kind == "borne":
            self.changer_couleur_yeux("#99ff99")
            self.plugged = True
        else:
            self.changer_couleur_yeux("#000000")
            raise Exception("Rob' a tenté de se brancher hors d'une borne !")
        
    
    def ramasser(self, dt):
        """
        Permet à Rob de ramasser la feuille qui se trouve sur sa case.
        Fait disparaître le dessin de la feuille.
        Provoque une erreur si Rob n'est pas sur une feuille.
        float:dt : temps durant lequel les yeux de Rob changent de couleur
        pour indiquer un ramassage réussi
        """
        
        case_cible = self.jardin.get_case(self.x, self.y)
        
        if not case_cible.leaf_here:
            raise Exception("Rob a tenté de ramasser une feuile sur une case vide !")
        
        for leaf_elem in case_cible.leaf_elems:
            self.jardin.canvas.delete(leaf_elem)
        case_cible.leaf_here = False
        
        self.changer_couleur_yeux("#cccc00")
        sleep(dt)
        self.changer_couleur_yeux(self.eyes_default_color)
        
                
                                        
class Case(object):
    def __init__(self, kind_code, parity):
        """
        str:kind_code : code à une lettre qui indique le type de la case
        bool:parity : indique si la case est "paire" ou "impaire"
                      de façon à être colorée correctement
        """
        self.rect_id = None
        self.leaf_elems = None
        
        self.leaf_here = False
        self.rock_here = False
        self.lawned = False
        self.parity = parity
        
        if kind_code == "M":
            self.kind = "mur"
        
        elif kind_code == "H":
            self.kind = "herbe"
        
        elif kind_code in Rob.ORI_KIND_CODES:
            self.kind = "herbe"
            self.lawned = True
            
        elif kind_code == "F":
            self.kind = "herbe"
            self.leaf_here = True
            
        elif kind_code == "C":
            self.kind = "herbe"
            self.rock_here = True
            raise Exception("Les cailloux ne sont pas implémentés actuellement !")
            
        elif kind_code == "B":
            self.kind = "borne"
            
        else:
            raise Exception("Unknown kind_code : " + kind_code)
      
      
    def get_color(self):
        
        if self.kind == "herbe":
            if self.lawned:
                if self.parity:
                    return "#ccff66"
                else:
                    return "#ccff99"
            else:
                if self.parity:
                    return "#009900"
                else:
                    return "#33cc33"
        
        elif self.kind == "mur":
            return "#cc3300"
        
        elif self.kind == "borne":
            return "#b3b3b3"
        
        else:
            raise Exception("Unknown kind : " + self.kind)
            
        
class Jardin(Tk):
    
    def __init__(self, name):
        """
        str:name : the name of the garden (without file extension)
        """
        
        Tk.__init__(self)
        
        self.cell_size = 50
        
        self.load_garden(name+".txt")
        
        self.title(name)
        
        self.canvas = Canvas(self, bg="lemonchiffon",
                             height=self.hauteur*self.cell_size,
                             width=self.largeur*self.cell_size)
        
        self.draw_garden()
        
        
    def load_garden(self, file):
        """
        Charge le dessin initial d'un jardin sous une forme exploitable
        Initialise les attributs garden (grille de case),
        rob (objet Rob), largeur et hauteur (dimensions, en cases, du jardin).
        """
        
        with open(file, encoding = "utf-8") as f:
            
            kind_codes = f.read()
            
            kind_codes_grid = [list(row) for row in kind_codes.split()]
            
            self.garden = []
            
            i = 0 # Not useful, but prevent warning
            j = 0 # Not useful, but prevent warning
            
            for i, kind_code_row in enumerate(kind_codes_grid):
                garden_row = []
                for j, kind_code in enumerate(kind_code_row):
                    garden_row.append(Case(kind_code, (i+j)%2==1))
                    
                    if kind_code in Rob.ORI_KIND_CODES:
                        self.rob = Rob(self, j, i, {"N":"NORD",
                                                    "E":"EST",
                                                    "O":"OUEST",
                                                    "S":"SUD"}[kind_code])
                        
                self.garden.append(garden_row)
                
            self.largeur = j+1 # Largeur du jardin en nb de cases
            self.hauteur = i+1 # Hauteur du jardin en nb de cases
     
     
    def draw_borne(self, x, y):
        self.canvas.create_oval(
            self.cell_size*(x+0.05), self.cell_size*(y+0.05),
            self.cell_size*(x+0.95), self.cell_size*(y+0.95),
            fill = "#cccccc", width = 0)
        
        self.canvas.create_polygon(
            self.cell_size*(x+0.6), self.cell_size*(y+0.2),
            self.cell_size*(x+0.35), self.cell_size*(y+0.6),
            self.cell_size*(x+0.45), self.cell_size*(y+0.55),
            self.cell_size*(x+0.4), self.cell_size*(y+0.8),
            self.cell_size*(x+0.65), self.cell_size*(y+0.4),
            self.cell_size*(x+0.55), self.cell_size*(y+0.45),
            self.cell_size*(x+0.6), self.cell_size*(y+0.2),
            fill = "#ffff00")
        
        
    def draw_leaf(self, x, y):
        leaf_color = "#ff8000"
        line_color = "#804000"
        extent = 0.4
        demi_width = 0.12
        left_leaf_id = self.canvas.create_oval(
            self.cell_size*(x+0.5-extent), self.cell_size*(y+0.5-demi_width),
            self.cell_size*(x+0.5), self.cell_size*(y+0.5+demi_width),
            fill = leaf_color, width = 0)
        top_leaf_id = self.canvas.create_oval(
            self.cell_size*(x+0.5-demi_width), self.cell_size*(y+0.5-extent),
            self.cell_size*(x+0.5+demi_width), self.cell_size*(y+0.5),
            fill = leaf_color, width = 0)
        right_leaf_id = self.canvas.create_oval(
            self.cell_size*(x+0.5), self.cell_size*(y+0.5-demi_width),
            self.cell_size*(x+0.5+extent), self.cell_size*(y+0.5+demi_width),
            fill = leaf_color, width = 0)
        stem_id = self.canvas.create_line(
            self.cell_size*(x+0.5), self.cell_size*(y+0.5),
            self.cell_size*(x+0.5), self.cell_size*(y+0.5+extent*3/4),
            fill = leaf_color, width = 5)
        line_id = self.canvas.create_line(
            self.cell_size*(x+0.5-0.7*extent), self.cell_size*(y+0.5),
            self.cell_size*(x+0.5+0.7*extent), self.cell_size*(y+0.5),
            self.cell_size*(x+0.5), self.cell_size*(y+0.5),
            self.cell_size*(x+0.5), self.cell_size*(y+0.5-0.7*extent),
            self.cell_size*(x+0.5), self.cell_size*(y+0.5+0.3*extent),
            fill=line_color
            )
        
        self.get_case(x,y).leaf_elems = (
            left_leaf_id, top_leaf_id, right_leaf_id, stem_id, line_id)
    
    def draw_mur_vertical_line(self, x, y, n, dy):
        m_vertical = n%2 + 1
        dx = 1 / (1+m_vertical)
        for m in range (1, 1+m_vertical):
            self.canvas.create_line(
                self.cell_size*(x+m*dx), self.cell_size*(y+n*dy),
                self.cell_size*(x+m*dx), self.cell_size*(y+(n-1)*dy),
                fill="white"
                )
    
    def draw_mur(self, x, y):
        n_horizontal = 3
        dy = 1 / (1+n_horizontal)
        for n in range(1, 1+n_horizontal):
            self.canvas.create_line(
                self.cell_size*x, self.cell_size*(y+n*dy),
                self.cell_size*(x+1), self.cell_size*(y+n*dy),
                fill="white"
                )
            self.draw_mur_vertical_line(x,y,n,dy)
        self.draw_mur_vertical_line(x,y,1+n_horizontal,dy)
                
        
        
    def draw_garden(self):
        """
        Dessine dans le canvas les éléments initiaux du jardin
        N'utiliser qu'une seule fois au début du dessin.
        Ensuite, les cases doivent être modifiées avec leur attribut rect_id
        et Rob doit être déplacé avec les fonctions appropriées.
        """
        
        for y, row in enumerate(self.garden):
            for x, case in enumerate(row):
                case.rect_id = self.canvas.create_rectangle(
                    self.cell_size*x, self.cell_size*y,
                    self.cell_size*(x+1), self.cell_size*(y+1),
                    fill = case.get_color())
                
                if case.kind == "mur":
                    self.draw_mur(x,y)
                
                if case.kind == "borne":
                    self.draw_borne(x, y)
                
                if case.leaf_here:
                    self.draw_leaf(x, y)
        
        # Note : actuellement, ne dessine pas les cailloux
        # A ajouter lors d'une future update
        
        self.rob.draw()
        
        self.canvas.pack()
        
        self.update()
            
    
    def get_case(self, x, y):
        return self.garden[y][x]
        

### Partie principale (fonctions appelables) ###

class Instance:
    pass

_instance = Instance()

def charger_jardin(nom):
    assert isinstance(nom, str), "Le nom de fichier indiqué doit être un str."
    _instance.jardin = Jardin(nom)
    
def avancer():
    _instance.jardin.rob.avancer(n_steps = 20, dt = 0.02)
    
def pivoter(direction):
    assert isinstance(direction, str), "La direction indiquée doit être un str."
    direction = direction.upper()
    assert direction == "GAUCHE" or direction == "DROITE", "Direction invalide !"
    _instance.jardin.rob.pivoter(direction, n_steps = 12, dt = 0.02)
    
def identifier(direction):
    assert isinstance(direction, str), "La direction indiquée doit être un str."
    direction = direction.upper()
    assert direction in ["GAUCHE", "DROITE", "DEVANT"], "Direction invalide !"
    return _instance.jardin.rob.detecter(direction, dt = 0.1)

def se_brancher():
    _instance.jardin.rob.brancher()
    
def ramasser():
    _instance.jardin.rob.ramasser(dt = 0.2)

__all__ = ("charger_jardin", "avancer", "pivoter", "identifier",
           "se_brancher", "ramasser")