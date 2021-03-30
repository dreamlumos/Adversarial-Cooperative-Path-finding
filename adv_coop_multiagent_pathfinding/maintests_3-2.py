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
    game.fps = 100 # frames per second
    game.mainiteration()
    player = game.player

TOURS = 50
ITERATIONS = 30

def main():
    tour = 0
    m_score1 = 0
    m_score2 = 0
    
    while tour < TOURS:
        
        print(" --------- Tour ", tour, " : ---------")

        random.seed(tour)
        iterations = ITERATIONS

        #-------------------------------
        # Choix de scenario
        #-------------------------------

        # Scenario 1 : Exchange
        scen = "exAdvCoopMap_exchange"
        
        # Scenario 2 : Race
        # scen = "exAdvCoopMap_race"
    
        # Scenario 3 : Mingle
        # scen = "exAdvCoopMap_mingle"

        init(scen)

        #-------------------------------
        # Initialisation de la carte
        #-------------------------------
    
        nbLignes = game.spriteBuilder.rowsize
        nbCols = game.spriteBuilder.colsize

        playerSprites = [o for o in game.layers['joueur']]
        goalSprites = [o for o in game.layers['ramassable']]
        nbPlayers = len(playerSprites)

        initStates = []
        goalStates = []

        if scen == "exAdvCoopMap_exchange":
            
            # Positionnement aléatoire des joueurs
            for i in range(nbPlayers//2):
                row = 0             # Team1 sur la première ligne
                col = -1
                while  col < 0 or (row,col) in initStates:
                     col = random.randint(0, nbCols-1)
                initStates.append((row,col))
            for i in range(nbPlayers//2):
                row = nbLignes - 1  # Team2 sur la dernière ligne
                col = -1
                while  col < 0 or (row,col) in initStates:
                     col = random.randint(0, nbCols-1)
                initStates.append((row,col))
            
            # Positionnement aléatoire des objectifs
            for i in range(nbPlayers//2):
                row = nbLignes - 1  # Objectifs de Team1 sur la dernière ligne
                col = -1
                while  col < 0 or (row,col) in initStates or (row,col) in goalStates:
                     col = random.randint(0, nbCols-1)
                goalStates.append((row,col))
            for i in range(nbPlayers//2):
                row = 0             # Objectifs de Team2 sur la première ligne
                col = -1
                while  col < 0 or (row,col) in initStates or (row,col) in goalStates:
                     col = random.randint(0, nbCols-1)
                goalStates.append((row,col))

        elif scen == "exAdvCoopMap_race":
            
            # Positionnement aléatoire des joueurs sur la première ligne
            for i in range(nbPlayers):
                row = 0       
                col = -1
                while col < 0 or (row,col) in initStates:
                    col = random.randint(0, nbCols-1)
                initStates.append((row,col))
            
            # Positionnement aléatoire des objectifs sur la dernière ligne
            for i in range(nbPlayers):
                row = nbLignes - 1 
                col = -1
                while col < 0 or (row,col) in goalStates:
                    col = random.randint(0, nbCols-1)
                goalStates.append((row,col))
            
        elif scen == "exAdvCoopMap_mingle":
            
            # Positionnement aléatoire des joueurs
            for i in range(nbPlayers//2):
                row = 0             # Team1 sur la première ligne
                col = -1
                while col < 0 or (row,col) in initStates:
                    col = random.randint(0, nbCols-1)
                initStates.append((row,col))
            for i in range(nbPlayers//2):
                row = -1            # Team2 sur la dernière colonne
                col = nbCols - 1
                while row < 0 or (row,col) in initStates:
                    row = random.randint(0, nbLignes-1)
                initStates.append((row,col))
            
            # Positionnement aléatoire des objectifs
            for i in range(nbPlayers//2):
                row = nbLignes - 1  # Objectifs de Team1 sur la dernière ligne
                col = -1
                while col < 0 or (row,col) in initStates or (row,col) in goalStates:
                    col = random.randint(0, nbCols-1)
                goalStates.append((row,col))
            for i in range(nbPlayers//2):
                row = -1            # Objectifs de Team2 sur la première colonne
                col = 0
                while row < 0 or (row,col) in initStates or (row,col) in goalStates:
                    row = random.randint(0, nbLignes-1)
                goalStates.append((row,col))

        for i in range(nbPlayers):
            row, col = initStates[i]
            playerSprites[i].set_rowcol(row, col)
        for i in range(nbPlayers):
            row, col = goalStates[i]
            goalSprites[i].set_rowcol(row, col)
        
        wallStates = [w.get_rowcol() for w in game.layers['obstacle']]
        
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

        print("Init states:", initStates)
        print("Goal states:", goalStates)
        print("Wall states:", wallStates)

        game.mainiteration()

        #-------------------------------
        # Initialisation des joueurs, des équipes et des stratégies
        #-------------------------------

        players = []
        posPlayers = initStates

        for i in range(nbPlayers):
            players.append(RealPlayer(playerSprites[i], i, initStates[i], goalStates[i]))
        
        team1 = Team(players[0 : nbPlayers//2], posPlayers, strat.CooperativeAStar(grid3D, iterations))
        team2 = Team(players[nbPlayers//2 : nbPlayers], posPlayers, strat.PathSlicing(grid))         
        
        #-------------------------------
        # Boucle principale de déplacements 
        #-------------------------------

        nbPlayersArrived = 0

        # enter = input("Press Enter to continue...")

        for i in range(iterations):
                    
            # Team 1
            for p in team1.players:
                
                if p.arrived:
                    continue
                
                row, col = (-1,-1)
                if (len(p.path) < i+1): # Chemin trop court
                    playerBlocked = True
                else:
                    try:
                        row, col = p.path[i] # prochaine case si tout va bien
                    except IndexError:
                        print("IndexError : team 2, player", p.id, " at iteration ", i, " !!!!!!!!!!!!")

                    # On vérifie si le joueur est bloqué
                    playerBlocked = False
                    for ps in players:
                        if ps != p and ps.pos == (row,col):
                            playerBlocked = True
                            # print("Le joueur ", p.id, " est bloqué par le joueur ", ps.id)
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

            # # Team 1
            # for p in team1.players:
                
            #     if p.arrived:
            #         continue
                
            #     row, col = (-1,-1)
            #     if (len(p.path) < i+1): # Chemin trop court
            #         playerBlocked = True
            #     else:
            #         try:
            #             row, col = p.path[i] # prochaine case si tout va bien
            #         except IndexError:
            #             print("IndexError : team 1, player", p.id, " at iteration ", i, " !!!!!!!!!!!!")
            #             print("path length :", len(p.path))

            #         # On vérifie si le joueur est bloqué
            #         playerBlocked = False
            #         for ps in players:
            #             if ps != p and ps.pos == (row,col):
            #                 playerBlocked = True
            #                 # print("Le joueur ", p.id, " est bloqué par le joueur ", ps.id)
            #                 break

            #     # On recalcule le chemin toutes les 3 étapes ou si le joueur est bloqué
            #     if (i != 0 and i % 3 == 0) or playerBlocked:
            #         # print("Joueur ", p.id, " est bloqué ?", playerBlocked)
                    
            #         # On recalcule le chemin à partir de la case où le joueur se situe actuellement
            #         p.updatePath(posPlayers, i)
            #         row, col = p.path[i]
                    
            #     # Joueur se déplace enfin
            #     p.updatePos(row, col, posPlayers)
                
            #     # Teste si le joueur est arrivé
            #     if p.updateArrived(i, iterations):
            #         nbPlayersArrived += 1
                
            # Team 2
            for p in team2.players:

                if p.arrived:
                    continue
                
                row, col = (-1,-1)
                if (len(p.path) < i+1): # Chemin trop court
                    playerBlocked = True
                else:
                    try:
                        row, col = p.path[i] # prochaine case si tout va bien
                    except IndexError:
                        print("IndexError : team 2, player", p.id, " at iteration ", i, " !!!!!!!!!!!!")

                    # On vérifie si le joueur est bloqué
                    playerBlocked = False
                    for ps in players:
                        if ps != p and ps.pos == (row,col):
                            playerBlocked = True
                            # print("Le joueur ", p.id, " est bloqué par le joueur ", ps.id)
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
            # enter = input("Press Enter to continue ...")

        tour += 1 

        vainqueurs = victoire(team1, team2)
        if vainqueurs == 1:
            m_score1 += 1
        elif vainqueurs == 2:
            m_score2 += 1 

   
    if m_score1 > m_score2: 
        print("Victoire de l'équipe 1 avec un score de", m_score1, "contre un score de", m_score2, "pour l'équipe 2, sur", TOURS, "nombre de tours" )
    elif m_score1 < m_score2: 
        print("Victoire de l'équipe 2 avec un score de", m_score2, "contre un score de", m_score1, "pour l'équipe 1, sur", TOURS, "nombre de tours" )
    else:
        print("Match nul. Score de", m_score2, "pour l'équipe 1, contre un score de", m_score1, "pour l'équipe 2, sur", TOURS, "nombre de tours" )
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
        return 1
    elif(score1 < score2):
        print("Victoire de l'équipe 2 avec", score2, "contre", score1)
        return 2
    else:
        print("match nul") # Todo
        return 0

    


if __name__ == '__main__':
    main()
