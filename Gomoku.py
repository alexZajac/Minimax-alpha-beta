# ZAJAC ALEXANDRE
import random
import time
from math import floor, inf
from copy import deepcopy
from Intelligence import alpha_beta_search, white_opening_positions, black_opening_positions
from State import State
from Hash import TranspositionTable

BLACK = -1 
WHITE = 1
MAX_NEIGHBORS = 1
MAX_DEPTH = 2



class Gomoku:
    def __init__(self):
        self.size = 15
        self.board = [[0] * self.size for _ in range(self.size)]
        self.tokens = [60, 60]
        self.transposition_table = TranspositionTable()

    def is_finished(self):
        """
        This method returns 0 if the game is not finished,
        and otherwise the value of the player
        """
       # horizontal check
        for i in range(self.size):
            for j in range(self.size-4):
                if(self.board[i][j] == BLACK and self.board[i][j+1] == BLACK and self.board[i][j+2] == BLACK and self.board[i][j+3] == BLACK and self.board[i][j+4] == BLACK):
                    return BLACK
                elif(self.board[i][j] == WHITE and self.board[i][j+1] == WHITE and self.board[i][j+2] == WHITE and self.board[i][j+3] == WHITE and self.board[i][j+4] == WHITE):
                    return WHITE
        
        # vertical check
        for j in range(self.size):
            for i in range(self.size-4):
                if(self.board[i][j] == BLACK and self.board[i+1][j] == BLACK and self.board[i+2][j] == BLACK and self.board[i+3][j] == BLACK and self.board[i+4][j] == BLACK):
                    return BLACK
                elif(self.board[i][j] == WHITE and self.board[i+1][j] == WHITE and self.board[i+2][j] == WHITE and self.board[i+3][j] == WHITE and self.board[i+4][j] == WHITE):
                    return WHITE

        #ascending diagonal check
        for j in range(self.size-4):
            for i in range(4, self.size):
                if(self.board[i][j] == BLACK and self.board[i-1][j+1] == BLACK and self.board[i-2][j+2] == BLACK and self.board[i-3][j+3] == BLACK and self.board[i-4][j+4] == BLACK):
                    return BLACK
                elif(self.board[i][j] == WHITE and self.board[i-1][j+1] == WHITE and self.board[i-2][j+2] == WHITE and self.board[i-3][j+3] == WHITE and self.board[i-4][j+4] == WHITE):
                    return WHITE

        #descending diagonal check
        for j in range(self.size-4):
            for i in range(self.size-4):
                if(self.board[i][j] == BLACK and self.board[i+1][j+1] == BLACK and self.board[i+2][j+2] == BLACK and self.board[i+3][j+3] == BLACK and self.board[i+4][j+4] == BLACK):
                    return BLACK
                elif(self.board[i][j] == WHITE and self.board[i+1][j+1] == WHITE and self.board[i+2][j+2] == WHITE and self.board[i+3][j+3] == WHITE and self.board[i+4][j+4] == WHITE):
                    return WHITE
        #else it's not a win
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
        """
        # if indices are valid
        if(i > -1 and j > -1 and i < self.size and j < self.size):
            if(self.board[i][j] == 0):
                return True
            else:
                return False 
        return False

    def get_size(self):
        """returns dimensions of board"""
        return self.size, self.size
    
    def determine_square_symbol(self, i, j):
        """
        Function used for printing empty cells on the board
        """
        s = '-'
        if(self.is_outside_center(i, j) == False):
            s = '.'
        return s

    def map_to_cell(self, i, j):
        """
        Function that returns grid cell from i j values
        """
        return str(chr(65 + i)) + str(j+1)

    def display_board(self, s1, s2):
        """
        Prints the board with corresponding sympbols for players
        """
        print("   1", end="")
        for i in range(2, self.size+1):
                print(" {:3d}".format(i), end="")
        print('\n')
        letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O']
        for i in range(self.size):
            print(letters[i], end="  ")
            for j in range(self.size):
                to_print = self.determine_square_symbol(i, j)
                if(self.board[i][j] == -1):
                    to_print = s1
                elif(self.board[i][j] == 1):
                    to_print = s2
                print(to_print, end='   ')
            print()
        print()

    def apply_action(self, i, j, num_player):
        """
        This methods applies the actions for given player and reduces its tokens
        """
        self.board[i][j] = num_player
        self.tokens[0 if num_player == BLACK else 1] -= 1

    def undo_action(self, i, j, num_player):
        """
        This methods undoes the actions for given player and increases its tokens
        """
        self.board[i][j] = 0
        self.tokens[0 if num_player == BLACK else 1] += 1

    def get_valid_black_openings(self, positions):
        row = 7
        col = 7
        col_white = -1
        rwo_white = -1
        for i in range(row-1, row+2):
            for j in range(col-1, col+2):
                if(self.board[i][j] == WHITE):
                    row_white = i
                    col_white = j
                    break
        if(col_white != -1 and row_white != -1):     
            if(col_white == 6):
                if(row_white == 6):
                    positions.remove([3,3])
                elif(row_white == 7):
                    positions.remove([7,3])
                else:
                    positions.remove([11,3])
            elif(col_white == 7):
                if(row_white == 6):
                    positions.remove([3,7])
                else:
                    positions.remove([11,7])
            elif(col_white == 8):
                if(row_white == 6):
                    positions.remove([3,11])
                elif(row_white == 7):
                    positions.remove([7,11])
                else:
                    positions.remove([11,11])
        return positions

    def get_row(self, num_player):# we traverse middle square
        """
        This method checks the user-inputted row for playing
        """
        r = input("C'est au tour du joueur {}, entrez une ligne (A à O): \n".format(1 if num_player == BLACK else 2))
        if(len(r) > 1 or len(r) == 0):
            print("La valeur de la ligne n'est pas valide, réessayez : ")
            return self.get_row(num_player)
        else:           
            ascii_value = ord(r)
            # if not between A and O
            if(ascii_value >= 65 and ascii_value <= 79):
                return ascii_value - 65
            elif(ascii_value >= 97 and ascii_value <= 111):
                return ascii_value - 97
            else:
                print("La valeur de la ligne est hors limites, réessayez : ")
                return self.get_row(num_player)

    def get_column(self, num_player):
        """
        This method checks the user-inputted column for playing
        """
        c = input("C'est au tour du joueur {}, entrez une colonne (1 à 15): \n".format(1 if num_player == BLACK else 2))
        try:
            integer_c = int(c)
            if(integer_c < 1 or integer_c > 15):
                print("La valeur de la colonne est hors limites, réessayez : ")
                return self.get_column(num_player)
            else:
                return integer_c - 1
        except:
            print("La valeur de la colonne n'est pas valide, réessayez : ")
            return self.get_column(num_player)

    def get_random_play(self, list_pos):
        """
        This method returns a random valid move in a list of moves
        """
        random_position = list_pos[random.randint(0, len(list_pos)-1)]
        i = random_position[0]
        j = random_position[1]
        if(self.is_safe(i, j) == False):
            return self.get_random_play(list_pos)
        else:
            return i, j

    def is_outside_center(self, i, j):
        """
        This function checks if the indexes are outside the 7x7 center square
        """
        if((i >= 4 and i <= 10) and (j >= 4 and j <= 10)):
            return False
        return True

    def player_turn(self, empty_cells_left, num_player):
        """
        Method for a human turn
        """
        exclude_middle_square = False
        # black second play
        if(empty_cells_left == self.size**2 - 2):
            exclude_middle_square = True
        i = self.get_row(num_player)
        j = self.get_column(num_player)
        while(self.is_safe(i, j) == False):
            print("Impossible de jouer dans cette case, rééssayez: \n")
            i = self.get_row(num_player)
            j = self.get_column(num_player)
        while(exclude_middle_square == True and self.is_outside_center(i, j) == False):
            print("Les opening-rules impliquent de jouer hors du carrée central 7x7, rééssayez: \n")
            i = self.get_row(num_player)
            j = self.get_column(num_player)
        else:
            # placing the move
            self.apply_action(i, j, num_player)
    
    def ai_turn(self, empty_cells_left, num_player, depth_cut = True):
        """
        Method for AI turn
        """
        # white first play
        if(empty_cells_left == self.size**2 - 1):
            i, j = self.get_random_play(white_opening_positions)
        # second black play
        elif(empty_cells_left == self.size**2 - 2):
            i, j = self.get_random_play(self.get_valid_black_openings(black_opening_positions))
        else:
            # parameters of the search
            root_state = State(deepcopy(self), num_player, MAX_NEIGHBORS)
            print("L'IA est en train de jouer...")
            i, j = alpha_beta_search(root_state, self.transposition_table, max_depth=MAX_DEPTH, should_random=True) 
            # once position is found, clear the transposition table
            self.transposition_table.clear_table()
            print("Action de l'IA : {}".format(self.map_to_cell(i, j)))
        self.apply_action(i, j, num_player)        

    def version_1(self, s1, s2):
        """
        player_playing is either 1 or 2
        player 1 -> human plays with -1 
        player 2 -> human plays with 1
        """
        choosen_color = input("Quel joueur souhaitez-vous être (1 noir ou 2 blanc) : ")
        num_player_human1 = BLACK if choosen_color == "1" else WHITE
        num_player_human2 = BLACK if num_player_human1 == WHITE else WHITE
        player_playing = WHITE

        while(True):
            end = self.is_finished()
            empty_cells_left = self.num_empty_cells()
            is_draw = empty_cells_left == 0
            no_tokens = self.tokens[0] + self.tokens[1] == 0
            self.display_board(s1, s2)
            #if game not finished
            if(end == 0 and not is_draw and not no_tokens):
                if(player_playing == num_player_human1):
                    self.player_turn(empty_cells_left, num_player_human1)
                    player_playing = BLACK if num_player_human1 == WHITE else WHITE
                else: 
                    self.player_turn(empty_cells_left, num_player_human2)
                    player_playing = BLACK if num_player_human2 == WHITE else WHITE
            elif(end != 0):
                print("Le joueur {} a gagné !".format(1 if end == -1 else 2))
                print("Pourcentage de la planche joué {} %".format((self.size**2-empty_cells_left)*100 / self.size**2))
                break              
            else:
                print("La partie est terminée, c'est une égalité ! \n")
                break

    def version_2(self, s1, s2):
        """
        player_playing is either number 1 (black) or 2 (white)
        player 1 -> human plays with -1 value
        player 2 -> A.I. plays with 1 value
        """
        choosen_color = input("Quel joueur souhaitez-vous être (1 noir ou 2 blanc) : ")
        num_player_human = BLACK if choosen_color == "1" else WHITE
        num_player_ai = BLACK if num_player_human == WHITE else WHITE

        player_playing = WHITE
        while(True):
            # here we test if previous move has not finished the game
            end = self.is_finished()
            empty_cells_left = self.num_empty_cells()
            is_draw = empty_cells_left == 0
            no_tokens = self.tokens[0] + self.tokens[1] == 0
            self.display_board(s1, s2)
            #if game not finished
            if(end == 0 and not is_draw and no_tokens == False):
                if(num_player_human == player_playing):
                    self.player_turn(empty_cells_left, num_player_human)
                    player_playing = BLACK if player_playing == WHITE else WHITE
                # ai turn
                else: 
                    self.ai_turn(empty_cells_left, num_player_ai)
                    player_playing = BLACK if player_playing == WHITE else WHITE
            elif(end != 0):
                print("Le joueur {} a gagné !".format(1 if end == BLACK else 2))
                print("Pourcentage de la planche joué {} %".format((self.size**2-empty_cells_left)*100 / self.size**2))
                break              
            else:
                print("La partie est terminée, c'est une égalité ! \n")
                break

    def version_3(self, s1, s2):
        """
        player_playing is either 1 or 2
        player 1 -> A.I. plays with -1 
        player 2 -> A.I. plays with 1
        for two AI's we don't take in counter depth cut, we let them explore all solutions and draw evenly
        perfect game always leads to draw
        """
        num_player_ai1 = BLACK
        num_player_ai2 = WHITE

        player_playing = WHITE
        while(True):
            # here we test if previous move has not finished the game
            end = self.is_finished()
            empty_cells_left = self.num_empty_cells()
            is_draw = empty_cells_left == 0
            no_tokens = self.tokens[0] + self.tokens[1] == 0
            self.display_board(s1, s2)
            #if game not finished
            if(end == 0 and not is_draw and no_tokens == False):
                if(num_player_ai1 == player_playing):
                    self.ai_turn(empty_cells_left, num_player_ai1)
                    player_playing = BLACK if player_playing == WHITE else WHITE
                # ai turn
                else: 
                    self.ai_turn(empty_cells_left, num_player_ai2)
                    player_playing = BLACK if player_playing == WHITE else WHITE
            elif(end != 0):
                print("Le joueur {} a gagné !".format(1 if end == -1 else 2))
                print("Pourcentage de la planche joué {} %".format((self.size**2-empty_cells_left)*100 / self.size**2))
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
        
        print("Bienvenue dans le jeu du Gomoku !\n")
        print("Vous avez choisi la version {}\n".format(version))

        s1 = 'X'
        s2 = 'O'
        print("Le joueur noir joue avec {} et le joueur blanc avec {}\n".format(s1, s2))
        # le joueur 1 commence
        player_playing = BLACK

        print("C'est au joueur {} de commencer \n".format(1 if player_playing == BLACK else 2))
        # on place le pion au centre au début de la partie
        self.board[7][7] = player_playing
        self.tokens[0] -= 1

        if(version == 1):
            self.version_1(s1, s2)
        elif(version == 2):
            self.version_2(s1, s2)
        else:
            self.version_3(s1, s2)  

game = Gomoku()
game.play(version=2)