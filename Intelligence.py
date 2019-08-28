import random
from math import floor, inf
import time

# those positions maximizes the white probability of winning (first white move)
white_opening_positions = [
    [6, 6], [6, 7], [6, 8], 
    [7, 6],         [7, 8], 
    [8, 6], [8, 7], [8, 8]
]
# those positions maximizes the black probability of winning (second black move)
black_opening_positions = [
    [3, 3],  [3, 7],  [3, 11],                                                                 
    [7, 3],           [7, 11],
    [11, 3], [11, 7], [11, 11]
]



def alpha_beta_search(state, transposition_table, max_depth=inf, should_random=False):
    """
    This method searchs with the min_max_alpha_beta pruning algorithm 
    for the best move to be made and returns an action (move)
    the paramter should random will randomize the move if all the utility values are the same
    """
    # initialzing move, alpha and beta value and best score
    move = [-1, -1]
    alpha = -inf
    beta = inf
    score = -inf
    total_scores = []
    # calculating time for the AI to solve 
    t1 = time.clock()
    actions_possible = Actions(state, True)
    # print(sorted_base_actions)
    # for every action possible from the depth 0 of the search
    for action in actions_possible:
        # copying state to perform minimax
        state = Result(state, action)
        # first move is with min call
        next_score = min_value(state, state.depth + 1, max_depth, alpha, beta, transposition_table)
        # once score is found, unod the action
        state = Undo(state, action)
        # if next score if better, we replace it
        if next_score > score:
            move = action
            score = next_score
        # adding each score to total scores
        total_scores.append(next_score)
        print(action, next_score)
        alpha = max(alpha, score)
    t2 = time.clock()
    print("Temps écoulé pour l'action de l'IA : {} s".format(t2 - t1))
    # all scores are the same, choose a move randomly  
    if(all([total_scores[0] == item for item in total_scores]) and should_random):
        random_index = random.randint(0, len(actions_possible)-1)
        return actions_possible[random_index][0], actions_possible[random_index][1]
    return move[0], move[1]

def max_value(state, depth, max_depth, alpha, beta, transposition_table):
    """
    Acting as the maximizer for the min_max search with alpha beta
    """
    # updating depth
    state.depth = depth
    # checking entry in transposition table
    table_check = transposition_table.table_lookup(state)
    if(len(table_check) > 0):
        state.depth -= 1
        return table_check[1]

    if(Terminal_test(state) or depth == max_depth):
        utility = Utility(state)
        transposition_table.insert_value(state, utility)
        state.depth -= 1
        return utility
    # if we're not at a leaf-level, we search for better with minizing next state (that's why we switch min_max_player)
    v = -inf
    state.min_max_player = -state.min_max_player
    actions = Actions(state, False)
    for a in actions:
        state = Result(state, a)
        # maximizing value of next state
        v = max(v, min_value(state, state.depth+1, max_depth, alpha, beta, transposition_table))
        # undoing
        state = Undo(state, a)
        # checks for pruning and updating alpha
        if(v >= beta):
            transposition_table.insert_value(state, v)
            state.depth -= 1
            state.min_max_player = -state.min_max_player
            return v
        alpha = max(alpha, v)
    state.depth -= 1
    state.min_max_player = -state.min_max_player
    return v

def min_value(state, depth, max_depth, alpha, beta, transposition_table):
    """
    Acting as the minimizer for the min_max search with alpha beta
    """
    state.depth = depth
    # checking entry in transposition table
    table_check = transposition_table.table_lookup(state)
    if(len(table_check) > 0):
        state.depth -= 1
        return table_check[1]

    if(Terminal_test(state) or depth == max_depth):
        utility = Utility(state)
        transposition_table.insert_value(state, utility)
        state.depth -= 1
        return utility
    v = inf
    state.min_max_player = -state.min_max_player
    actions = Actions(state, False)
    for a in actions:
        state = Result(state, a)
        # minimizing value of next state
        v = min(v, max_value(state, state.depth+1, max_depth, alpha, beta, transposition_table))
        # undoing
        state = Undo(state, a)
        # checks for pruning and updating beta
        if(v <= alpha):
            transposition_table.insert_value(state, v)
            state.depth -= 1
            state.min_max_player = -state.min_max_player
            return v
        beta = min(beta, v)
    state.depth -= 1
    state.min_max_player = -state.min_max_player
    return v

def Actions(state, with_sort = False):
    """
    This method returns a list of all possible actions for given gomoku state
    """
    actions = []
    active_positions = []
    row_size, column_size = state.get_game_dimensions()
    max_neighbors = state.max_neighbors 

    for i in range(row_size):
        for j in range(column_size):
            if(state.game.board[i][j] != 0):
                active_positions.append([i, j])

    for position in active_positions:
        for i in range(position[0]-max_neighbors, position[0]+max_neighbors+1):
            for j in range(position[1]-max_neighbors, position[1]+max_neighbors+1):
                if(state.can_place_action(i, j)):
                    actions.append([i, j])
    
    unique_actions = [list(x) for x in set([tuple(y) for y in actions])]
    if(with_sort):
        unique_actions = SortedActions(state, unique_actions, True if state.min_max_player == state.default_player else False)
    return unique_actions

def Result(state, action):
    """
    This method applies the action to the state, action is a list of indices
    """
    state.apply_action(*action)
    return state

def Undo(state, action):
    """
    This method undoes the action to the state
    """
    state.undo_action(*action)
    return state

def Terminal_test(state):
    """
    This method tests if the given state is terminal
    """
    return state.is_terminal()

def Utility(state):
    """
    Returns a heuristic-based value for given state
    """
    # here we evaluate the score for the default player for which we initially called alpha beta search
    current_player = state.default_player
    if(state.is_winning(current_player)):
        return inf-1
    elif(state.is_winning(-current_player)):
        return -inf+1
    # if it's not a win, we evaluate a score (always < 100 and > -100) given the current state board
    else:
        return state.evaluate_score(current_player)

def SortedActions(state, actions, is_max):
    """
    This method sorts actions by heuristic value of first step action
    """
    dict_utilities = {}
    for i in range(len(actions)):
        state = Result(state, actions[i])
        current_utility = Utility(state)
        dict_utilities[i] = current_utility
        state = Undo(state, actions[i])
    # sorting and converting to action list
    sorted_utilities = sorted(dict_utilities.items(), key=lambda kv: kv[1], reverse=(True if is_max else False))
    new_sorted_actions = [actions[tple[0]] for tple in sorted_utilities]
    return new_sorted_actions