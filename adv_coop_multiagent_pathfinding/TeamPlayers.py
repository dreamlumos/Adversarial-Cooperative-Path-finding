class RealPlayer:
    """
    Classe qui contient tous les attributs nécessaires pour un joueur.
    Le sprite doit être déplacé quand le joueur se déplace pour que cela soit reflété sur l'affichage.
    """

    def __init__(self, sprite, id, pos, goal):
        self.sprite = sprite
        self.id = id
        self.pos = pos
        self.goal = goal
        self.path = []
        self.arrived = False
        self.score = 0
        self.strategy = None
    
    def updateStrategy(self, strategy):
        self.strategy = strategy

    def updateArrived(self, iteration, iterations):
        if self.pos == self.goal:
            self.arrived = True
            self.score += 1
            print("Le joueur", self.id," a atteint son but !")
            if self.strategy.name == "CooperativeAStar":
                self.strategy.permanentReservation(self.pos, iteration)
        return self.arrived
        
    def updatePos(self, row, col, posPlayers):
        self.pos = (row, col)
        self.sprite.set_rowcol(row, col)
        posPlayers[self.id] = (row, col)
        print("pos ", self.id, " : ", row, col)

    def updatePath(self, posPlayers, iteration):
        self.path = self.strategy.newPath(self.pos, self.goal, self.path, posPlayers, iteration)
        print("Chemin trouvé pour joueur ", self.id, " : ", self.path)

class Team:
    """
    Classe qui contient la liste des joueurs de l'équipe, ainsi que sa stratégie.
    """

    def __init__(self, players, posPlayers, strategy=None):
        self.nbPlayers = len(players)
        self.players = players
        self.strategy = strategy

        for player in players:
            player.updateStrategy(strategy)
            player.updatePath(posPlayers, 0) 