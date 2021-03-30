# -*- coding: utf-8 -*-

# Nicolas, 2021-03-05
from __future__ import absolute_import, print_function, unicode_literals

import random 
import numpy as np
import sys
from itertools import chain

import pygame

from pySpriteWorld.gameclass import Game, check_init_game_done
from pySpriteWorld.spritebuilder import SpriteBuilder
from pySpriteWorld.players import Player
from pySpriteWorld.sprite import MovingSprite
from pySpriteWorld.ontology import Ontology
import pySpriteWorld.glo

from search.grid2D import ProblemeGrid2D
from search import probleme

import strategies as strat
from TeamPlayers import RealPlayer
from TeamPlayers import Team

# ---- ---- ---- ---- ---- ----
# ---- Misc                ----
# ---- ---- ---- ---- ---- ----

# ---- ---- ---- ---- ---- ----
# ---- Main                ----
# ---- ---- ---- ---- ---- ----

game = Game() # ?

def init(_boardname=None):
    global player, game
    name = _boardname if _boardname is not None else 'demoMap'
    game = Game('Cartes/' + name + '.json', SpriteBuilder)
    game.O = Ontology(True, 'SpriteSheet-32x32/tiny_spritesheet_ontology.csv')
    game.populate_sprite_names(game.O)
    game.fps = 5  # frames per second
    game.mainiteration()
    player = game.player
    
def main():
    random.seed(40)

    iterations = 100 # default
    if len(sys.argv) == 2:
        iterations = int(sys.argv[1])
    print("Iterations: ", iterations)

    # Choix de carte
    # init("test")
    init("exAdvCoopMap")
    
    #-------------------------------
    # Initialisation de la carte
    #-------------------------------
    
    nbLignes = game.spriteBuilder.rowsize
    nbCols = game.spriteBuilder.colsize
    print("lignes", nbLignes)
    print("colonnes", nbCols)
    
    playerSprites = [o for o in game.layers['joueur']]
           
    # On localise tous les états initiaux (positions initiales des joueurs)
    initStates = [o.get_rowcol() for o in game.layers['joueur']]
    print("Init states:", initStates)
    
    # On localise tous les objets ramassables sur le layer ramassable (objectifs)
    goalStates = [o.get_rowcol() for o in game.layers['ramassable']]
    random.shuffle(goalStates) # Attribution aleatoire des objectifs
    print("Goal states:", goalStates)
    
    # On localise tous les murs sur le layer obstacle
    wallStates = [w.get_rowcol() for w in game.layers['obstacle']]
    print("Wall states:", wallStates)
    
    def legal_position(row, col):
        # une position legale est dans la carte et pas sur un mur
        return ((row,col) not in wallStates) and row>=0 and row<nbLignes and col>=0 and col<nbCols
    
    # Initialisation de la matrice représentant la carte
    grid = np.ones((nbLignes,nbCols), dtype=bool)  # par defaut la matrice comprend des True  
    for w in wallStates:         # putting False for walls
        grid[w] = False

    grid3D = np.ones((nbLignes,nbCols,iterations), dtype=bool)  # par defaut la matrice comprend des True  
    for w in wallStates:         # putting False for walls
        x, y = w
        for t in range(iterations):
            grid3D[(x,y,t)] = False

    #-------------------------------
    # Initialisation des joueurs, des équipes et des stratégies
    #-------------------------------

    nbPlayers = len(playerSprites)
    players = []
    posPlayers = initStates

    for i in range(nbPlayers):
        players.append(RealPlayer(playerSprites[i], i, initStates[i], goalStates[i]))
    
    team1 = Team(players[0 : nbPlayers//2], posPlayers, strat.IndependentAStar(grid))
    team2 = Team(players[nbPlayers//2 : nbPlayers], posPlayers, strat.PathSlicing(grid))         
    
    #-------------------------------
    # Boucle principale de déplacements 
    #-------------------------------

    nbPlayersArrived = 0

    enter = input("Press Enter to continue (s to stop)...")

    for i in range(1, iterations):
                
        # Team 1
        for p in team1.players:
            
            if p.arrived:
                continue
            
            row, col = (-1,-1)
            try:
                row, col = p.path[i] # prochaine case si tout va bien
            except IndexError:
                print("IndexError team 1, player", p.id, " at iteration ", i, " !!!!!!!!!!!!")

            # On vérifie si le joueur est bloqué (ce serait bien d'arriver à mettre ce test dans legal_position)
            playerBlocked = False
            for ps in players:
                if ps != p and ps.pos == (row,col):
                    playerBlocked = True
                    print("Le joueur ", p.id, " est bloqué par le joueur ", ps.id)
                    break
            
            # On recalcule le chemin toutes les 5 étapes ou si le joueur est bloqué
            if (i != 0 and i % 5 == 0) or playerBlocked:
                print("Joueur ", p.id, " est bloqué ?", playerBlocked)
                
                # On recalcule le chemin à partir de la case où le joueur se situe actuellement
                p.updatePath(posPlayers, i)
                row, col = p.path[i]
                
            # Joueur se déplace enfin
            p.updatePos(row, col, posPlayers)
            
            # Teste si le joueur est arrivé
            if p.updateArrived(i, iterations):
                nbPlayersArrived += 1
            
        # Team 2
        for p in team2.players:

            if p.arrived:
                continue
            
            try:
                row, col = p.path[i] # prochaine case si tout va bien
            except IndexError:
                print("IndexError team 2, player", p.id, " at iteration ", i, " !!!!!!!!!!!!")

            # On vérifie si le joueur est bloqué (ce serait bien d'arriver à mettre ce test dans legal_position)
            playerBlocked = False
            for ps in players:
                if ps != p and ps.pos == (row,col):
                    playerBlocked = True
                    print("Le joueur ", p.id, " est bloqué par le joueur ", ps.id)
                    break
            
            if playerBlocked:
                # On recalcule le chemin à partir de la case où le joueur se situe actuellement
                p.updatePath(posPlayers, i)
                row, col = p.path[i]
        
            # Joueur se déplace enfin
            p.updatePos(row, col, posPlayers)
            
            # Teste si le joueur est arrivé
            if p.updateArrived(i, iterations):
                nbPlayersArrived += 1

        # Fin du jeu si tous les joueurs sont arrivés
        if nbPlayersArrived == nbPlayers:
            break
        
        # On passe a l'iteration suivante du jeu
        game.mainiteration()
        enter = input("Press Enter to continue (s to stop)...")

    victoire(team1, team2)
    pygame.quit()

#-------------------------------

def victoire(team1, team2):
    score1=0
    score2=0
    
    for player in team1.players:
        score1 += player.score
    for player in team2.players:
        score2 += player.score
    if(score1 > score2):
        print("Victoire de l'équipe 1 avec", score1, "contre", score2)
    if(score1 < score2):
        print("Victoire de l'équipe 2 avec", score2, "contre", score1)
    else:
        print("match null") # Todo
    
   

if __name__ == '__main__':
    main()