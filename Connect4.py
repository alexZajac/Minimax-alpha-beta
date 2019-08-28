import random
from math import floor, inf
from copy import deepcopy
from Intelligence import alpha_beta_search
from State import State
import time

# parameter that conteols the depth of search
MAX_DEPTH = 5

def determine_first_move():  
    """
    this function return random value between 0 and 1
    """        
    return random.getrandbits(1) + 1

class Connect4:
    def __init__(self):
        self.num_rows = 6
        self.num_columns = 7
        self.board = [[0] * self.num_columns for _ in range(self.num_rows)]
        #the lowest empty rows in columns
        self.index_lowest_empty_row = [self.num_rows] * self.num_columns

    def is_finished(self, player):
        """
        This method returns 0 if the game is not finished,
        and otherwise the value of the player
        """
        # horizontal check
        for i in range(self.num_rows):
            for j in range(self.num_columns-3):
                if(self.board[i][j] == player and self.board[i][j+1] == player and self.board[i][j+2] == player and self.board[i][j+3] == player):
                    return player
        
        # vertical check
        for j in range(self.num_columns):
            for i in range(self.num_rows-3):
                if(self.board[i][j] == player and self.board[i+1][j] == player and self.board[i+2][j] == player and self.board[i+3][j] == player):
                    return player

        #ascending diagonal check
        for j in range(self.num_columns-3):
            for i in range(3, self.num_rows):
                if(self.board[i][j] == player and self.board[i-1][j+1] == player and self.board[i-2][j+2] == player and self.board[i-3][j+3] == player):
                    return player

        #descending diagonal check
        for j in range(self.num_columns-3):
            for i in range(self.num_rows-3):
                if(self.board[i][j] == player and self.board[i+1][j+1] == player and self.board[i+2][j+2] == player and self.board[i+3][j+3] == player):
                    return player
        
        #else it's not a win
        return 0


    def get_size(self):
        """
        returns dimensions of board
        """
        return self.num_rows, self.num_columns

    def num_empty_cells(self):
        """ 
        This method return the number of empty cells in the grid
        """
        empty_cells = 0
        for row in self.board:
            for value in row:
                if(value == 0):
                    empty_cells += 1
        return empty_cells

    def is_safe(self, i, j):
        """
        This methods checks if the current player can place his move in the board
        move is between 1 and 7, and represents the columns in which the player wants the coin inserted
        """
        # if the provided row index is the one that is a the top of the considered column
        if(self.index_lowest_empty_row[j] - 1 == i):
            return True
        else:
            return False
        return False
    
    def display_board(self, s1, s2):
        """
        Prints the board with corresponding sympbols for players
        """
        for row in self.board:
            for value in row:
                to_print = '-'
                if(value == -1):
                    to_print = s1
                elif(value == 1):
                    to_print = s2
                print(to_print, end=' ')
            print()
        print()
    
    def map_move_to_column(self, move):
        """
        This function takes a string move as argument from the client and tries to convert it to integers index
        """
        try:
            #here a move is a column index
            column_index = int(move)-1
            return column_index
        except ValueError:
            return -1

    def evaluate_score(self, player, depth):
        """ 
        This function evaluates score for a given player number (player 1 -> -1 and player 2 -> 1)
        it serves as an heuristic for the minmax algorithm with depth cutting
        """
        # four consecutive values in the grid
        four_consecutive = 0
        #initializing score that advantages player and the other that disadvantages him
        positive_score = 0
        negative_score = 0

         # horizontal check
        for i in range(self.num_rows):
            for j in range(self.num_columns-3):
                four_consecutive = self.board[i][j] + self.board[i][j+1] + self.board[i][j+2] + self.board[i][j+3]  
                # if three same signes for the player are aligned with one empty slot
                if(four_consecutive == 3 * player):
                    positive_score += 10
                elif(four_consecutive == -3 * player):
                    negative_score += 10
        
        # vertical check
        for j in range(self.num_columns):
            for i in range(self.num_rows-3):
                four_consecutive = self.board[i][j] + self.board[i+1][j] + self.board[i+2][j] + self.board[i+3][j]  
                # if three same signes for the player are aligned with one empty slot
                if(four_consecutive == 3 * player):
                    positive_score += 10
                elif(four_consecutive == -3 * player):
                    negative_score += 10

        #ascending diagonal check
        for j in range(self.num_columns-3):
            for i in range(3, self.num_rows):
                four_consecutive = self.board[i][j] + self.board[i-1][j+1] + self.board[i-2][j+2] + self.board[i-3][j+3]  
                # if three same signes for the player are aligned with one empty slot
                if(four_consecutive == 3 * player):
                    positive_score += 10
                elif(four_consecutive == -3 * player):
                    negative_score += 10

        #descending diagonal check
        for j in range(self.num_columns-3):
            for i in range(self.num_rows-3):
                four_consecutive = self.board[i][j] + self.board[i+1][j+1] + self.board[i+2][j+2] + self.board[i+3][j+3]  
                # if three same signes for the player are aligned with one empty slot
                if(four_consecutive == 3 * player):
                    positive_score += 10
                elif(four_consecutive == -3 * player):
                    negative_score += 10
        
        # we return the difference divided by depth the number of steps to that state
        return (positive_score - negative_score) / depth
    
    def get_valid_column(self, num_player):
        move = input("C'est au tour du joueur {}, entrez une colonne (1 à 7): \n".format(1 if num_player == -1 else 2))
        j = self.map_move_to_column(move)
        # if the coumn index is not valid
        if(j < 0 or j >= self.num_columns):
            print("Index de colomne invalide, rééssayez: \n")
            return self.get_valid_column(num_player)
        #else we check if the column is not entierely filled
        elif(self.index_lowest_empty_row[j] > 0):
            return j
        else:
            print("La colonne est remplie, rééssayez : \n")
            return self.get_valid_column(num_player)
    
    def apply_action(self, i, j, num_player):
        self.board[i][j] = num_player
        self.index_lowest_empty_row[j] -= 1

    def player_turn(self, num_player):
        """
        Method for a human turn
        """
        # getting it from function to ensure safeness
        j = self.get_valid_column(num_player)
        # placing the move and incrementing lowest index in columns
        i = self.index_lowest_empty_row[j]-1
        self.apply_action(i, j, num_player)

    def ai_turn(self, num_player, depth_cut = True):
        """
        Method for AI turn
        """
        # here for the first move we force the algorithm to choose it randomly because 
        # it doesn't influence the state of the game and it's faster given that the 
        # search tree is the tallest possible
        if(all([x == self.num_rows-1 for x in self.index_lowest_empty_row])):
            t1 = time.clock()
            j = random.randint(0, self.num_columns-1)
            i = self.index_lowest_empty_row[j]-1
            self.apply_action(i, j, num_player)
            t2 = time.clock()
            print("Temps écoulé pour l'action de l'IA : {} s".format(t2 - t1))
        # for other states, we limit the depth if needed
        else:
            if(depth_cut): 
                max_depth = MAX_DEPTH
            else:
                max_depth = inf
            root_state = State(deepcopy(self), num_player)
            # if should_random is true, the games will be more diversified
            # if it's false, the first player will always win (perfect game)
            i, j = alpha_beta_search(root_state, max_depth=max_depth, should_random=True) 
            self.apply_action(i, j, num_player)
    
    def version_1(self, player_playing, s1, s2):
        """
        player_playing is either 1 or 2
        player 1 -> human plays with -1 
        player 2 -> human plays with 1
        """
        while(True):
            # here we test if previous move has not finished the game
            has_previous_won = 1 if player_playing == 1 else -1
            end = self.is_finished(has_previous_won)
            empty_cells_left = self.num_empty_cells()
            is_draw = empty_cells_left == 0
            self.display_board(s1, s2)
            #if game not finished
            if(end == 0 and not is_draw):
                if(player_playing == 1):
                    num_player = -1
                    self.player_turn(num_player)
                    player_playing += 1
                else: 
                    num_player = 1
                    self.player_turn(num_player)
                    player_playing -= 1
            elif(end != 0):
                print("Le joueur {} a gagné !".format(1 if end == -1 else 2))
                break              
            else:
                print("La partie est terminée, c'est une égalité ! \n")
                break
    
    def version_2(self, player_playing, s1, s2):
        """
        player_playing is either 1 or 2
        player 1 -> human plays with -1 
        player 2 -> A.I. plays with 1
        """
        while(True):
            # here we test if previous move has not finished the game
            has_previous_won = 1 if player_playing == 1 else -1
            end = self.is_finished(has_previous_won)
            empty_cells_left = self.num_empty_cells()
            is_draw = empty_cells_left == 0
            self.display_board(s1, s2)
            #if game not finished
            if(end == 0 and not is_draw):
                if(player_playing == 1):
                    num_player = -1
                    self.player_turn(num_player)
                    player_playing += 1
                # ai turn
                else: 
                    num_player = 1
                    self.ai_turn(num_player)
                    player_playing -= 1
            elif(end != 0):
                print("Le joueur {} a gagné !".format(1 if end == -1 else 2))
                break              
            else:
                print("La partie est terminée, c'est une égalité ! \n")
                break

    def version_3(self, player_playing, s1, s2):
        """
        player_playing is either 1 or 2
        player 1 -> A.I. plays with -1 
        player 2 -> A.I. plays with 1
        """
        while(True):
            # here we test if previous move has not finished the game
            has_previous_won = 1 if player_playing == 1 else -1
            end = self.is_finished(has_previous_won)
            empty_cells_left = self.num_empty_cells()
            is_draw = empty_cells_left == 0
            self.display_board(s1, s2)
            #if game not finished
            if(end == 0 and not is_draw):
                if(player_playing == 1):
                    num_player = -1
                    self.ai_turn(num_player)
                    player_playing += 1
                # ai turn
                else: 
                    num_player = 1
                    self.ai_turn(num_player)
                    player_playing -= 1
            elif(end != 0):
                print("Le joueur {} a gagné !".format(1 if end == -1 else 2))
                break              
            else:
                print("La partie est terminée, c'est une égalité ! \n")
                break

    def play(self, version=2):
        """
        This function begins the play between two players selected by the version variable
        version=1 -> player vs A.I.
        version=2 -> player to player
        version=3 -> A.I. to A.I.

        player_playing = 1 corresponds to player 1
        player_playing = 2 corresponds to player 2
        """
        
        print("Bienvenue dans le jeu du Puissance 4 !\n")
        print("Vous avez choisi la version {}\n".format(version))

        s1 = input("Choisissez un symbole pour le joueur 1 :\n")
        s2 = input("Choisissez un symbole pour le joueur 2 :\n")

        print("Nous allons determiner aléatoirement qui commence en premier : \n")
        player_playing = determine_first_move()
        print("C'est au joueur {} de commencer \n".format(player_playing))

        if(version == 1):
            self.version_1(player_playing, s1, s2)
        elif(version == 2):
            self.version_2(player_playing, s1, s2)
        else:
            self.version_3(player_playing, s1, s2) 
        

game = Connect4()
game.play(version=3)