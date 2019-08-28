import random
import time
from math import floor, inf
from copy import deepcopy
from Intelligence import alpha_beta_search
from State import State

def determine_first_move():  
    """
    this function return random value between 0 and 1
    """        
    return random.getrandbits(1) + 1

class Tictactoe:
    def __init__(self, size=3):
        self.size = size
        self.board = [[0] * size for _ in range(size)]

    def is_finished(self, player):
        """
        This method returns 0 if the game is not finished,
        and otherwise the value of the player
        """
        diagonal_down_left = diagonal_up_left = row = 0
        columns = [0 for _ in range(self.size)]

        for i in range(self.size):
            for j in range(self.size):
                if(i == j):
                    diagonal_down_left += self.board[i][j]
                if(i + j == self.size-1):
                    diagonal_up_left += self.board[i][j]
                row += self.board[i][j]
                columns[j] += self.board[i][j]
            if(row == self.size*player):
                return player
            row = 0
        if(diagonal_down_left == self.size*player):
            return player
        elif(diagonal_up_left == self.size*player):
            return player
        elif(self.size*player in columns):
            return player
        # if not any of the above, then the player hasn't won
        return 0

    def num_empty_cells(self):
        """ 
        This method return the number of empty cells in the grid
        """
        empty_cells = 0
        for row in self.board:
            for elm in row: 
                if(elm == 0):
                    empty_cells += 1
        return empty_cells

    def is_safe(self, i, j):
        """
        This methods checks if the current player can place his move in the board
        move is between 1 and 9, we have to map it to a matrix index
        """
        # if indices are valid
        if(i > -1 and j > -1 and i < 3 and j < 3):
            if(self.board[i][j] == 0):
                return True
            else:
                return False 
        return False

    def get_size(self):
        """returns dimensions of board"""
        return self.size, self.size
    
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
    
    def map_move_to_indices(self, move):
        """
        This function takes a string move as argument from the client and tries to convert it to integers indices
        """
        try:
            number_move = int(move)
            row_index = floor((number_move-1) / self.size)
            column_index = (number_move-1) % self.size
            return row_index, column_index
        except ValueError:
            return -1, -1
    
    def evaluate_score(self, num_player, depth):
        """ 
        This function evaluates score for a given player number (player 1 -> -1 and player 2 -> 1)
        it serves as an heuristic for the minmax algorithm with depth cutting
        it returns the difference between what advantages the current player and what doesn't
        """
        diagonal_down_left = diagonal_up_left = row = 0
        columns = [0 for _ in range(self.size)]
        #initializing score that advantages player and the other that disadvantages him
        positive_score = 0
        negative_score = 0
        #we will count two following signs for each caracteristic dimension
        advantage_position = (self.size-1) * num_player
        disadvantage_position = (self.size-1) * (-num_player)

        for i in range(self.size):
            for j in range(self.size):
                if(i == j):
                    diagonal_down_left += self.board[i][j]
                if(i + j == self.size-1):
                    diagonal_up_left += self.board[i][j]
                row += self.board[i][j]
                columns[j] += self.board[i][j]
            # we check if the num_player has two signs on the same row
            if(row == advantage_position):
                positive_score += 10
            # test for his opponent
            elif(row == disadvantage_position):
                negative_score += 10
            row = 0
        # diagonal down left for our player
        if(diagonal_down_left == advantage_position):
            positive_score += 10
        # diagonal down left for the opponent
        elif(diagonal_down_left == disadvantage_position):
            negative_score += 10
        #diagonal up left for our player
        if(diagonal_up_left == advantage_position):
            positive_score += 10
        # diagonal up left for opponent
        elif(diagonal_up_left == disadvantage_position):
            negative_score += 10
        # column testing
        for elm in columns:
            if(elm == advantage_position):
                positive_score += 10
            elif(elm == disadvantage_position):
                negative_score += 10

        return (positive_score - negative_score) / depth

    def apply_action(self, i, j, num_player):
        self.board[i][j] = num_player

    def undo_action(self, i, j):
        self.board[i][j] = 0

    def player_turn(self, num_player):
        """
        Method for a human turn
        """
        move = input("C'est au tour du joueur {}, entrez une position (1 à 9): \n".format(1 if num_player == -1 else 2))
        i, j = self.map_move_to_indices(move)
        while(self.is_safe(i, j) == False):
            move = input("Impossible de jouer dans cette case, rééssayez: \n")
            i, j = self.map_move_to_indices(move)
        # placing the move
        self.apply_action(i, j, num_player)
    
    def ai_turn(self, empty_cells_left, num_player, depth_cut = True):
        """
        Method for AI turn
        """
        # here for the first move we force the algorithm to choose it randomly because 
        # it doesn't influence the state of the game and it's faster given that the 
        # search tree is the tallest possible
        if(empty_cells_left == self.size**2):
            t1 = time.clock()
            i = random.randint(0, self.size-1)
            j = random.randint(0, self.size-1)
            self.apply_action(i, j, num_player)
            t2 = time.clock()
            print("Temps écoulé pour l'action de l'IA : {} s".format(t2 - t1))
        # for other states, we limit the depth if needed
        else:
            if(depth_cut): 
                max_depth = 2
            else:
                max_depth = inf
            root_state = State(deepcopy(self), num_player, 5)
            i, j = alpha_beta_search(root_state, max_depth=max_depth) 
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
                    self.ai_turn(empty_cells_left, num_player)
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
        for two AI's we don't take in counter depth cut, we let them explore all solutions and draw evenly
        perfect game always leads to draw
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
                    self.ai_turn(empty_cells_left, num_player)
                    player_playing += 1
                # ai turn
                else: 
                    num_player = 1
                    self.ai_turn(empty_cells_left, num_player)
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

        player_playing = 1 corresponds to the player playing with -1
        player_playing = 2 corresponds to the player playing with 1
        """
        
        print("Bienvenue dans le jeu du Morpion !\n")
        print("Vous avez choisi la version {}\n".format(version))

        s1 = 'x'
        s2 = 'o'

        print("Nous allons determiner aléatoirement qui commence en premier : \n")
        player_playing = 1
        print("C'est au joueur {} de commencer \n".format(player_playing))

        if(version == 1):
            self.version_1(player_playing, s1, s2)
        elif(version == 2):
            self.version_2(player_playing, s1, s2)
        else:
            self.version_3(player_playing, s1, s2)  
        

game = Tictactoe()
game.play(version=3)