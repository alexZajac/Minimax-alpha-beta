from Intelligence import Utility
from math import inf

# weights used for evaluation function
WEIGHTS = [10**8, 10**7, 10**6, 10**5, 10**4, 10**3, 10**2, 10, 1]
# the side of a square in which we update the score for specific points
LOCAL_AREA_RADIUS = 15

BLACK = -1 
WHITE = 1

class State:
    def __init__(self, game, default_player, max_neighbors):
        """
        We define the game, the default_player doesn't change 
        while min_max_player is with each call of the minmax search
        depth is always 0 when the state is initialized
        we track last moves
        """
        self.game = game
        self.max_neighbors = max_neighbors
        self.default_player = default_player
        self.min_max_player = default_player
        self.depth = 0
        self.last_move = [-1, -1]
    
    def get_game_dimensions(self): 
        """
        returns the dimensions of the current game
        """
        rows, cols = self.game.get_size()
        return rows, cols

    def can_place_action(self, i, j):
        """
        return boolean testing is move is possible
        """
        return self.game.is_safe(i, j)
    
    def apply_action(self, i, j):
        """
        Applying the action to the game
        """
        self.game.apply_action(i, j, self.min_max_player)
        self.last_move = [i, j]

    def undo_action(self, i, j):
        """
        Applying the action to the game
        """
        self.game.undo_action(i, j, self.min_max_player)
        self.last_move = [-1, -1]

    def is_terminal(self):
        """
        Tests if the game is finished
        """
        finished_number = self.game.is_finished()
        return (
            finished_number == BLACK 
            or 
            finished_number == WHITE 
            or 
            self.game.num_empty_cells() == 0
            or 
            (self.game.tokens[0] + self.game.tokens[1] == 0)
        )
    
    def is_winning(self, player_type):
        """
        Returns boolean if one player has won
        """
        finished_number = self.game.is_finished() 
        if(player_type == BLACK and finished_number == BLACK):
            return True
        elif(player_type == WHITE and finished_number == WHITE):
            return True
        else:
            return False

    def evaluate_score(self, num_player):
        """ 
        This function evaluates score for a given player number (player 1 -> -1 and player 2 -> 1)
        it serves as an heuristic for the minmax algorithm with depth cutting
        it returns the difference between what advantages the current player and what doesn't
        """
        # combinations of threats
        threats_to_opponent = [0 for _ in range(9)]
        threats_to_player   = [0 for _ in range(9)]
        # more readable
        i = self.last_move[0]
        j = self.last_move[1]
        # we serach in local area of the last move
        rows, cols = self.get_game_dimensions()
        start_row = max(0, i - LOCAL_AREA_RADIUS // 2)
        end_row = min(rows, i + LOCAL_AREA_RADIUS // 2)
        start_col = max(0, j - LOCAL_AREA_RADIUS // 2)
        end_col = min(cols, j + LOCAL_AREA_RADIUS // 2)
        board = self.game.board
        # for each dimension, we count a serie of six values and identify the number of threats they cause

        # horizontal check
        for i in range(start_row, end_row):
            for j in range(start_col, end_col-5):
                six_consecutive = [board[i][j], board[i][j+1], board[i][j+2], board[i][j+3], board[i][j+4], board[i][j+5]]
                index_threat_opponent = self.evaluate_serie(six_consecutive, num_player)
                index_threat_player = self.evaluate_serie(six_consecutive, -num_player)
                threats_to_opponent[index_threat_opponent] += 1
                threats_to_player[index_threat_player] += 1
        
        # vertical check
        for j in range(start_col, end_col):
            for i in range(start_row, end_row-5):
                six_consecutive = [board[i][j], board[i+1][j], board[i+2][j], board[i+3][j], board[i+4][j], board[i+5][j]]
                index_threat_opponent = self.evaluate_serie(six_consecutive, num_player)
                index_threat_player = self.evaluate_serie(six_consecutive, -num_player)
                threats_to_opponent[index_threat_opponent] += 1
                threats_to_player[index_threat_player] += 1

        #ascending diagonal check
        for j in range(start_col, end_col-5):
            for i in range(start_row + 5, end_row):
                six_consecutive = [board[i][j], board[i-1][j+1], board[i-2][j+2], board[i-3][j+3], board[i-4][j+4], board[i-5][j+5]]          
                index_threat_opponent = self.evaluate_serie(six_consecutive, num_player)
                index_threat_player = self.evaluate_serie(six_consecutive, -num_player)
                threats_to_opponent[index_threat_opponent] += 1
                threats_to_player[index_threat_player] += 1

        #descending diagonal check
        for j in range(start_col, end_col-5):
            for i in range(start_row, end_row-5):
                six_consecutive = [board[i][j], board[i+1][j+1], board[i+2][j+2], board[i+3][j+3], board[i+4][j+4], board[i+5][j+5]]        
                index_threat_opponent = self.evaluate_serie(six_consecutive, num_player)
                index_threat_player = self.evaluate_serie(six_consecutive, -num_player)
                threats_to_opponent[index_threat_opponent] += 1
                threats_to_player[index_threat_player] += 1
        # have o4
        if(threats_to_opponent[1] > 0 and threats_to_player[0] == 0):
            return inf-2
        # block o3
        if(threats_to_player[4] > 0 and (threats_to_opponent[1] == 0 and threats_to_opponent[2] == 0)):
            return inf-3
        # have o3
        if(threats_to_opponent[4] > 0 and (threats_to_player[1] == 0 and threats_to_player[2] == 0 and threats_to_player[4] == 0)):
            return inf-4
        #initializing score that advantages player and the other that disadvantages him
        positive_score = [WEIGHTS[i] * threats_to_opponent[i] for i in range(7)]
        negative_score = [WEIGHTS[i] * threats_to_player[i] for i in range(7)]
        # we return the difference 
        return (sum(positive_score) - sum(negative_score)) 

    def evaluate_serie(self, serie, num_player):
        """
        This method returns the index in the weights array corresponding to the most powerful threat from num_player to opponent
        """
        if(self.open_five(num_player, serie)):
            return 0
        if(self.open_four(num_player, serie)):
            return 1
        if(self.closed_four(num_player, serie)):
            return 2
        if(self.broken_three(num_player, serie)):
            return 3
        if(self.open_three(num_player, serie)):
            return 4
        if(self.closed_three(num_player, serie)):
            return 5
        if(self.open_two(num_player, serie)):
            return 6
        if(self.broken_two(num_player, serie)):
            return 7
        else:
            return 8
        
    def open_five(self, num_player, serie):
        return( 
            ((serie[1] + serie[2] + serie[3] + serie[4] + serie[5]) == num_player*5)
            or
            ((serie[1] + serie[2] + serie[3] + serie[4] + serie[0]) == num_player*5)
        )

    def open_four(self, num_player, serie):
        if(serie[0] == 0 and serie[5] == 0):
            return (serie[1] + serie[2] + serie[3] + serie[4]) == num_player*4
        else:
            return False

    def open_three(self, num_player, serie):
        if(serie[0] == 0 and serie[5] == 0):
            if(serie[1] == 0):
                return (serie[2] + serie[3] + serie[4]) == 3*num_player
            elif(serie[4] == 0):
                return (serie[1] + serie[2] + serie[3]) == 3*num_player
            else:
                return False
        else:
            return False
    
    def closed_three(self, num_player, serie):
        if(serie[0] == 0 and serie[5] == 0):
            if(serie[1] == -num_player):
                return (serie[2] + serie[3] + serie[4]) == 3*num_player
            elif(serie[4] == -num_player):
                return (serie[1] + serie[2] + serie[3]) == 3*num_player
            else:
                return False
        else:
            return False
        
    def open_two(self, num_player, serie):
        if(serie[0] == 0 and serie[5] == 0):
            if(serie[1] == 0):
                if(serie[2] == 0):
                    return (serie[3] + serie[4]) == 2*num_player
                elif(serie[4] == 0):
                    return (serie[2] + serie[2]) == 2*num_player
            elif(serie[2] == 0):
                return (serie[3] + serie[4]) == 2*num_player
            elif(serie[3] == 0):
                return (serie[1] + serie[2]) == 2*num_player
            elif(serie[4] == 0):
                if(serie[1] == 0):
                    return (serie[2] + serie[3]) == 2*num_player
                elif(serie[3] == 0):
                    return (serie[1] + serie[2]) == 2*num_player
            else:
                return False
        else:
            return False
    
    def closed_four(self, num_player, serie):
        if(serie[0] == 0):
            if(serie[1] == num_player):
                return (serie[2] + serie[3] + serie[4]) == 3*num_player
            elif(serie[1] == -num_player):
                return (serie[2] + serie[3] + serie[4] + serie[5]) == 4*num_player
        elif(serie[0] == num_player):
            return (serie[1] + serie[2] + serie[3]) == 3*num_player
        else:
            return (serie[1] + serie[2] + serie[3] + serie[4]) == 4*num_player

    def broken_three(self, num_player, serie):
        if(serie[0] == 0 and serie[5] == 0):
            if(serie[1] == num_player and serie[4] == num_player):
                if(serie[2] == 0):
                    return serie[3] == num_player
                elif(serie[3] == 0):
                    return serie[2] == num_player
                else: 
                    return False
            else:
                return False
        else:
            return False

    def broken_two(self, num_player, serie):
        if(serie[0] == 0 and serie[5] == 0):
            return ((serie[1] + serie[2] + serie[3] + serie[4]) == 2*num_player)
        else:
            return False