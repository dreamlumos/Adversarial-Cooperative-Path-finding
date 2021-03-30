# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 09:32:05 2016

@author: nicolas
"""

import numpy as np
import copy
import heapq
from abc import ABCMeta, abstractmethod
import search.probleme as probleme
from search.probleme import Probleme
    
###############################################################################

class ProblemeGrid2D(Probleme): 
    """ On definit un probleme de labyrithe comme étant: 
        - un état initial
        - un état but
        - une grid, donné comme un array booléen (False: obstacle)
        - une heuristique (supporte Manhattan, euclidienne)
        """ 
    def __init__(self, init, but, grid, heuristique):
            self.init = init
            self.but = but
            self.grid = grid
            self.heuristique = heuristique
        
    def cost(self, e1, e2):
        """ donne le cout d'une action entre e1 et e2, 
            toujours 1 pour le taquin
            """
        return 1
        
    def estBut(self, e):
        """ retourne vrai si l'état e est un état but
            """
        return (self.but == e)
        
    def estObstacle(self, e):
        """ retourne vrai si l'état est un obstacle
            """
        return (self.grid[e] == False)
        
    def estDehors(self, etat):
        """retourne vrai si en dehors de la grille
            """
        (s,_) = self.grid.shape
        (x,y) = etat
        return ((x>=s) or (y>=s) or (x<0) or (y<0))

    def successeurs(self, etat):
            """ retourne des positions successeurs possibles
                """
            current_x,current_y = etat
            d = [(0,1),(1,0),(0,-1),(-1,0),(0,0)] # Pause possible
            etatsApresMove = [(current_x+inc_x,current_y+inc_y) for (inc_x,inc_y) in d]
            return [e for e in etatsApresMove if not(self.estDehors(e)) and not(self.estObstacle(e))]

    def immatriculation(self, etat):
        """ génère une chaine permettant d'identifier un état de manière unique
            """
        s = ""
        (x,y) = etat
        s += str(x) + '_' + str(y)
        return s
        
    def h_value(self, e1, e2):
        """ applique l'heuristique pour le calcul 
            """
        if self.heuristique == 'manhattan':
            h = probleme.distManhattan(e1, e2)
        elif self.heuristique == 'uniform':
            h = 1
        return h