import search.probleme as probleme
from search.probleme import Probleme

class ProblemeGrid3D(Probleme): 
    """ On definit un probleme de labyrithe comme étant: 
        - un état initial
        - un état but
        - une grid, donné comme un array booléen (False: obstacle)
        - une heuristique (supporte Manhattan, euclidienne)
    """

    def __init__(self, init, but, grid3D, heuristique, iterations):
            self.init = init
            self.but = but
            self.grid = grid3D
            self.heuristique = heuristique
            self.iterations = iterations
        
    def cost(self, e1, e2):
        """ Donne le cout d'une action entre e1 et e2.
        """
        return 1
        
    def estBut(self, e):
        """ Retourne vrai si l'état e est un état but.
        """
        (x,y,t) = e
        return (self.but == (x,y))
        
    def estObstacle(self, e):
        """ Retourne vrai si l'état est un obstacle.
        """
        return (self.grid[e] == False)
        
    def estDehors(self, etat):
        """ Retourne vrai si en dehors de la grille 3D.
        """
        s,*_ = self.grid.shape
        x,y,t = etat
        return (x>=s) or (y>=s) or (x<0) or (y<0) or (t<0) or (t>=self.iterations)

    def successeurs(self, etat):
        """ Retourne les positions successeurs possibles.
        """
        current_x, current_y, current_t = etat
        d = [(0,1,1),(1,0,1),(0,-1,1),(-1,0,1),(0,0,1)] # Pause possible
        etatsApresMove = [(current_x + inc_x, current_y + inc_y, current_t + inc_t) for (inc_x, inc_y, inc_t) in d]
        return [e for e in etatsApresMove if not(self.estDehors(e)) and not(self.estObstacle(e))]

    def immatriculation(self, etat):
        """ Génère une chaine permettant d'identifier un état de manière unique.
        """
        s = ""
        (x,y,t) = etat
        s += str(x) + '_' + str(y) + '_' + str(t)
        return s
        
    def h_value(self, e1, e2):
        """ Applique l'heuristique pour le calcul de h.
        """
        if self.heuristique == 'true':
            h = 0 
            # TODO
        elif self.heuristique == 'manhattan':
            x1,y1,t1 = e1
            x2,y2 = e2
            h = probleme.distManhattan((x1,y1), (x2,y2))
        elif self.heuristique == 'uniform':
            h = 1
        return h