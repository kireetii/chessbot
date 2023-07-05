import ChessEngine as ChessEngine

ROWS = COLS = 8

# tune these values to change the behaviour of the engine
CHECKMATE = 60000
STALEMATE = 0
DEPTH = 5
piece = {'p' : 100, 'N' : 320, 'B' : 330, 'R' : 500, 'Q' : 900, 'K' : 20000}

pst = {
    'p': (  0,  0,  0,  0,  0,  0,  0,  0,
            50, 50, 50, 50, 50, 50, 50, 50,
            10, 10, 20, 30, 30, 20, 10, 10,
            5,  5, 10, 25, 25, 10,  5,  5,
            0,  0,  0, 20, 20,  0,  0,  0,
            5, -5,-10,  0,  0,-10, -5,  5,
            5, 10, 10,-20,-20, 10, 10,  5,
            0,  0,  0,  0,  0,  0,  0,  0),

    'N': (  -50,-40,-30,-30,-30,-30,-40,-50,
            -40,-20,  0,  0,  0,  0,-20,-40,
            -30,  0, 10, 15, 15, 10,  0,-30,
            -30,  5, 15, 20, 20, 15,  5,-30,
            -30,  0, 15, 20, 20, 15,  0,-30,
            -30,  5, 10, 15, 15, 10,  5,-30,
            -40,-20,  0,  5,  5,  0,-20,-40,
            -50,-40,-30,-30,-30,-30,-40,-50),

    'B': (  -20,-10,-10,-10,-10,-10,-10,-20,
            -10,  0,  0,  0,  0,  0,  0,-10,
            -10,  0,  5, 10, 10,  5,  0,-10,
            -10,  5,  5, 10, 10,  5,  5,-10,
            -10,  0, 10, 10, 10, 10,  0,-10,
            -10, 10, 10, 10, 10, 10, 10,-10,
            -10,  5,  0,  0,  0,  0,  5,-10,
            -20,-10,-10,-10,-10,-10,-10,-20),

    'R': (   0,  0,  0,  0,  0,  0,  0,  0,
             5, 10, 10, 10, 10, 10, 10,  5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            -5,  0,  0,  0,  0,  0,  0, -5,
             0,  0,  0,  5,  5,  0,  0,  0),

    'Q': (  -20,-10,-10, -5, -5,-10,-10,-20,
            -10,  0,  0,  0,  0,  0,  0,-10,
            -10,  0,  5,  5,  5,  5,  0,-10,
             -5,  0,  5,  5,  5,  5,  0, -5,
              0,  0,  5,  5,  5,  5,  0, -5,
            -10,  5,  5,  5,  5,  5,  0,-10,
            -10,  0,  5,  0,  0,  0,  0,-10,
            -20,-10,-10, -5, -5,-10,-10,-20),

    'K': (  -30,-40,-40,-50,-50,-40,-40,-30,
            -30,-40,-40,-50,-50,-40,-40,-30,
            -30,-40,-40,-50,-50,-40,-40,-30,
            -30,-40,-40,-50,-50,-40,-40,-30,
            -20,-30,-30,-40,-40,-30,-30,-20,
            -10,-20,-20,-20,-20,-20,-20,-10,
             20, 20,  0,  0,  0,  0, 20, 20,
             20, 20, 30,  0,  0, 10, 30, 20),
}
# join piece and pst dictionaries
for k, table in pst.items():
    sumrow = lambda row: tuple(x + piece[k] for x in row)
    pst[k] = sum((sumrow(table[i*8 : i*8+8]) for i in range(8)), ())

def find_move(gs, valid_moves):
    """
    Root call for search
    """
    global best_move
    global nodes
    nodes = 0
    best_move = None
    alpha = -CHECKMATE
    beta = CHECKMATE
    # negamaxalphabeta(gs, DEPTH, alpha, beta, 1 if gs.white_to_move else -1)
    pvs(gs, alpha, beta, DEPTH, 1 if gs.white_to_move else -1)
    print(nodes)
    if best_move == None:
        best_move = valid_moves[0]
    return best_move

def quiescence(gs, alpha, beta, turn_multiplier):
    global nodes
    nodes += 1
    stand_pat = evaluation(gs) * turn_multiplier
    if stand_pat >= beta:
        return beta
    if alpha < stand_pat:
        alpha = stand_pat
    valid_moves = gs.get_valid_moves()
    captures = []
    for m in valid_moves:
        if m.is_capture:
            captures.append(m)
    order_moves(captures)
    for capture_move in captures:
        if not capture_move.is_capture:
            continue
        gs.make_move(capture_move)
        score = -quiescence(gs, -beta, -alpha, -turn_multiplier)
        gs.undo_move()
        if score >= beta:
            return beta
        if score > alpha:
            alpha = score

    return alpha

def negamaxalphabeta(gs, depth, alpha, beta, turn_multiplier):
    global best_move
    global nodes
    nodes += 1
    if depth == 0:
        # return turn_multiplier * evaluation(gs)
        return quiescence(gs, alpha, beta, turn_multiplier)
    
    max_score = -CHECKMATE
    if gs.checkmate:
        return -CHECKMATE + depth
    if gs.stalemate:
        return 0
    valid_moves = gs.get_valid_moves()
    order_moves(valid_moves)
    for move in valid_moves:
        gs.make_move(move)
        score = -negamaxalphabeta(gs, depth-1, -beta, -alpha, -turn_multiplier)
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                best_move = move
        gs.undo_move()
        if max_score > alpha:
            alpha = max_score
        if beta <= alpha:
            break
    return max_score

def pvs(gs, alpha, beta, depth, turn_multiplier):
    global best_move
    if depth == 0:
        return quiescence(gs, alpha, beta, turn_multiplier)
    valid_moves = gs.get_valid_moves()
    order_moves(valid_moves)
    bSearchPv = True
    for move in valid_moves:
        gs.make_move(move)
        if bSearchPv:
            score = -pvs(gs, -beta, -alpha, depth-1, -turn_multiplier)
        else:
            score = -pvs(gs, -alpha-1, -alpha, depth-1, -turn_multiplier)
            if score > alpha:
                score = -pvs(gs, -beta, -alpha, depth-1, -turn_multiplier)
        gs.undo_move()
        if score >= beta:
            return beta
        if score > alpha:
            alpha = score
            best_move = move
            bSearchPv = False
        
    return alpha

def order_moves(valid_moves):
    """
    Sort the moves according to the MVVLVA-
    Most Valuable Victim - Least Valuable Agressor
    """
    for i in range(len(valid_moves)):
        move_score = 0
        piece_captured = valid_moves[i].piece_captured
        piece_moved = valid_moves[i].piece_moved
        if valid_moves[i].piece_captured != '--':
            move_score += 10 * piece[piece_captured[1]] - piece[piece_moved[1]]

        if valid_moves[i].is_pawn_promotion:
            move_score += piece['Q']

        if valid_moves[i].is_castle_move:
            move_score += 10000
        
        valid_moves[i].move_score = move_score
    # sorting
    for i in range(len(valid_moves)):
        for j in range(len(valid_moves) - i - 1):
            if valid_moves[j].move_score < valid_moves[j + 1].move_score:
                valid_moves[j], valid_moves[j+1] = valid_moves[j+1], valid_moves[j]

def evaluation(gs):
    """
    Returns the evaluation of a state
    """
    if gs.checkmate:
        if gs.white_to_move:
            return -CHECKMATE
        else:
            return CHECKMATE
    if gs.stalemate:
        return STALEMATE
    
    evaluation = 0
    for i in range(ROWS):
        for j in range(COLS):
            if gs.board[i][j][0] == 'w':
                evaluation += pst[gs.board[i][j][1]][i*8 + j]

            if gs.board[i][j][0] == 'b':
                evaluation -= pst[gs.board[i][j][1]][(7-i)*8 + j]

    return evaluation

# def move_generation_test(g, depth):
#     """
#     To test the number of total valid moves
#     """
#     if depth == 0:
#         return 1
#     moves = g.get_valid_moves()
#     positions = 0
#     for move in moves:
#         g.make_move(move)
#         positions += move_generation_test(g, depth-1)
#         g.undo_move()
#     return positions

# g = ChessEngine.GameState()
# print(move_generation_test(g, 3))

