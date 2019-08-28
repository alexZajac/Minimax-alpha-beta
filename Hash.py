from random import randint

RANDOM_HASH_TABLE = [
        [
            [
                randint(1, 2**64 - 1) for _ in range(2)
            ] 
            for _ in range(15)
        ] 
        for _ in range(15)
    ]

class TranspositionTable:
    def __init__(self):
        self.hashtable = {}
    
    def table_lookup(self, state):
        """
        This method returns the value for a state if found in the hashtable else -1
        """
        zobrist_game_key = compute_zobrist_key(state.game.board)
        zobrist_table_index = zobrist_to_index(zobrist_game_key)
        if(zobrist_table_index in self.hashtable.keys() and self.hashtable[zobrist_table_index][0] == zobrist_game_key and self.hashtable[zobrist_table_index][2] >= state.depth):
            return self.hashtable[zobrist_table_index]
        else:
            return []
        
    def insert_value(self, state, state_value):
        """
        This method puts in the dictionney the corresponding hash value given a state
        """
        zobrist_game_key = compute_zobrist_key(state.game.board)
        zobrist_table_index = zobrist_to_index(zobrist_game_key)
        self.hashtable[zobrist_table_index] = [zobrist_game_key, state_value, state.depth]

    def clear_table(self):
        """
        We clear the table between each move
        """
        self.hashtable.clear()


   
def piece_to_index(piece_value):
    """
    Maps piece value ton valid index
    """
    if piece_value == -1:
        return 0
    elif piece_value == 1:
        return 1
    else:
        return -1

def compute_zobrist_key(board):
    """
    This function computes the zobrist key for given board state
    """
    h = 0
    rows, cols = (15 for i in range(2))
    for i in range(rows):
        for j in range(cols):
            if(board[i][j] != 0):
                piece_index = piece_to_index(board[i][j])
                h ^= RANDOM_HASH_TABLE[i][j][piece_index]
    return h

def zobrist_to_index(zobrist_key):
    """
    This method hashes the zobrist key to get an index in the transposition table
    """
    return zobrist_key & 0xffff    
