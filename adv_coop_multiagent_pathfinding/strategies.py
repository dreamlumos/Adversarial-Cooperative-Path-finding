from search.grid2D import ProblemeGrid2D
from search.grid3D import ProblemeGrid3D
from search import probleme

class Strategy:

    def newPath(self, init, goal, oldPath, posPlayers, iteration):
        raise NotImplementedError("Please implement this method")

class IndependentAStar(Strategy):
    """
    A* indépendants au sein d'une équipe.
    Heuristique : Distance de Manhattan.
    Recalcul des chemins en cas de blocage, ou après un certain nombre de pas.
    """

    name = "IndependentAStar"

    def __init__(self, grid):
        self.grid = grid
        
    def newPath(self, init, goal, oldPath, posPlayers, iteration):
        currentGrid = self.grid.copy()
        for pos in posPlayers:
            # print("posPlayers :", pos)
            if pos != init:
                currentGrid[pos] = False
        pb = ProblemeGrid2D(init, goal, currentGrid, 'manhattan')
        newPath = oldPath[:iteration] + probleme.astar(pb)[1:]
        return newPath

class PathSlicing(Strategy):
    """
    A* indépendants avec path slicing en cas de blocage.
    Heuristique : Distance de Manhattan.
    """
    
    name = "PathSlicing"

    def __init__(self, grid, M=5):
        self.grid = grid
        self.M = M
    
    def newPath(self, init, goal, oldPath, posPlayers, iteration):
        currentGrid = self.grid.copy()
        for pos in posPlayers:
            if pos != init:
                currentGrid[pos] = False
        if len(oldPath) <= iteration+self.M:
            pb = ProblemeGrid2D(init, goal, currentGrid, 'manhattan')
            newPath = oldPath[:iteration] + probleme.astar(pb)[1:]
        else:
            pb = ProblemeGrid2D(init, oldPath[iteration+self.M], currentGrid, 'manhattan')
            newPath = oldPath[:iteration] + probleme.astar(pb)[1:] + oldPath[iteration+self.M+1:]
        return newPath

class CooperativeAStar(Strategy):
    """
    A* coopératif.
    Heuristique : True distance.
    """

    name = "CooperativeAStar"
    depth = 10

    def __init__(self, grid3D, iterations):
        self.grid3D = grid3D
        self.iterations = iterations
        self.reservations = {}
        dim1, dim2, dim3 = grid3D.shape
        for x in range(dim1):
            for y in range(dim2):
                for t in range(dim3):
                    if grid3D[x,y,t] == False: 
                        self.reservations[(x,y,t)] = True
                    else:
                        self.reservations[(x,y,t)] = False

    def permanentReservation(self, pos, iteration):
        x,y = pos
        for t in range(iteration, self.iterations):
            expandedPos = (x,y,t)
            self.reservations[expandedPos] = True
        print("Pos ", pos, " reserved permanently.")

    def cancelReservations(self, oldPath, iteration):
        """ Annule les réservations futures qui ne sont plus utiles avant de recalculer un nouveau chemin.
        """
        for t in range(iteration, len(oldPath)):
            x,y = oldPath[t]
            self.reservations[(x,y,t)] = False

    def newPath(self, init, goal, oldPath, posPlayers, iteration):
        self.cancelReservations(oldPath, iteration)
        for pos in posPlayers:
            if pos != init:
                x,y = pos
                expandedPos = (x,y,iteration)
                self.reservations[expandedPos] = True
        x,y = init
        pb = ProblemeGrid3D((x,y,iteration-1), goal, self.grid3D, 'manhattan', self.iterations)
        astar = probleme.spaceTimeAStar(pb, self.reservations, self.depth)[1:]
        print("astar : ", astar)
        newPath = oldPath[:iteration] + astar
        return newPath
