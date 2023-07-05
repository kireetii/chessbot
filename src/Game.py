import pygame as p
from ChessEngine import GameState
from ChessEngine import Move
import Searcher as Searcher

HEIGHT = WIDTH = 512
ROWS = COLS = 8
SQ_LEN = HEIGHT // ROWS
MAX_FPS = 15    # for animations
# colors
DARK = (121, 96, 76)
LIGHT = (171, 149, 132)
BLUE = (100, 149, 237)
PURPLE = (125, 122, 223)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# show methods
def show_board(chess_board):
    """
    Displays the chess board
    """
    global colors
    colors = [LIGHT, DARK]
    cnt = 0
    for row in range(ROWS):
        for col in range(COLS):
            if cnt % 2 == 0:
                p.draw.rect(chess_board, LIGHT, (SQ_LEN*col, SQ_LEN*row, SQ_LEN, SQ_LEN))
            else:
                p.draw.rect(chess_board, DARK, (SQ_LEN*col, SQ_LEN*row, SQ_LEN, SQ_LEN))
            cnt += 1
        cnt += 1

def show_pieces(chess_board, gs):
    """
    Displays the pieces over the board
    """
    for row in range(ROWS):
        for col in range(COLS):
            piece = gs.board[row][col]
            if piece != '--':
                chess_board.blit(p.image.load(f"assets/images/{piece}.png"), 
                                 p.Rect(SQ_LEN*col, SQ_LEN*row, SQ_LEN, SQ_LEN))

def show_moves(chess_board, gs, valid_moves, sq_selected):
    """
    Highlights valid move squares
    """
    if sq_selected != ():
        row, col = sq_selected
        if gs.board[row][col][0] == ('w' if gs.white_to_move else 'b'):
            s = p.Surface((SQ_LEN, SQ_LEN))
            s.set_alpha(100)    # transparency
            s.fill(PURPLE)
            chess_board.blit(s, (col * SQ_LEN, row * SQ_LEN))
            for move in valid_moves:
                if move.initial_pos_x == row and move.initial_pos_y == col:
                    s.fill(BLUE)
                    chess_board.blit(s, (move.final_pos_y * SQ_LEN, move.final_pos_x * SQ_LEN))

def show_text(chess_board, text):
    font = p.font.SysFont('helvetica', 25, True, False)
    text_object = font.render(text, 0, BLACK)
    text_width = text_object.get_width()
    text_location = p.Rect(0, 0, WIDTH, HEIGHT).move(HEIGHT / 2 - text_width / 2, WIDTH / 2 - text_width / 2)
    chess_board.blit(text_object, text_location)
    text_object = font.render(text, 0, WHITE)
    chess_board.blit(text_object, text_location.move(2, 2))

def animate_move(move, chess_board, board, clock):
    global colors
    dr = move.final_pos_x - move.initial_pos_x
    dc = move.final_pos_y - move.initial_pos_y
    frames_per_square = 5   # animation speed
    frames_count = (abs(dr) + abs(dc)) * frames_per_square
    for frame in range(frames_count+1):
        row, col = (move.initial_pos_x + dr * frame/frames_count, move.initial_pos_y + dc * frame/frames_count)
        show_board(chess_board)
        show_pieces(chess_board, board)

        color = colors[(move.final_pos_x + move.final_pos_y) % 2]
        end_square = p.Rect(move.final_pos_y*SQ_LEN, move.final_pos_x*SQ_LEN, SQ_LEN, SQ_LEN)
        p.draw.rect(chess_board, color, end_square)

        # draw moving piece
        chess_board.blit(p.image.load(f"assets/images/{move.piece_moved}.png"), 
                                 p.Rect(SQ_LEN*col, SQ_LEN*row, SQ_LEN, SQ_LEN))
        p.display.flip()
        clock.tick(50)

def main():
    """
    The main driver function
    """
    p.init()    # initialize all imported p modules
    chess_board = p.display.set_mode((HEIGHT, WIDTH))
    p.display.set_caption('chess')
    clock = p.time.Clock()
    gs = GameState()
    sq_selected = ()
    player_clicks = []

    valid_moves = gs.get_valid_moves()
    move_made = False
    game_over = False
    player_one = True  # if player playing white then true, if AI then false
    player_two = False  # same for black
    animate = True
    running = True
    while running:
        human_turn = (gs.white_to_move and player_one) or (not gs.white_to_move and player_two)
        for event in p.event.get():
            if event.type == p.QUIT:
                running = False

            # mouse handler
            elif event.type == p.MOUSEBUTTONDOWN:
                if not game_over and human_turn:
                    location = p.mouse.get_pos()
                    x = location[1] // SQ_LEN
                    y = location[0] // SQ_LEN
                    # if the same square clicked twice
                    if sq_selected == (x, y):   
                        sq_selected = ()    
                        player_clicks = []
                    else:
                        sq_selected = (x, y)
                        player_clicks.append(sq_selected)

                    if len(player_clicks) == 2:
                        move = Move(player_clicks[0], player_clicks[1], gs.board)
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                gs.make_move(valid_moves[i])
                                move_made = True
                                sq_selected = ()
                                player_clicks = []

                        if not move_made:
                            player_clicks = [sq_selected]
            # key handler                
            elif event.type == p.KEYDOWN:
                if event.key == p.K_z:
                    gs.undo_move()
                    move_made = True
                    if game_over:
                        game_over = False

        if move_made:
            if animate:
                animate_move(gs.move_log[-1], chess_board, gs, clock)
            valid_moves = gs.get_valid_moves()
            move_made = False
        
        if gs.checkmate:
            game_over = True
            if gs.white_to_move:
                text = 'Black wins by checkmate'
            else:
                text = 'White wins by checkmate'
            show_text(chess_board, text)

        elif gs.stalemate:
            game_over = True
            text = 'Draw by stalemate'
            show_text(chess_board, text)
            
        elif gs.three_move_draw:
            game_over = True
            text = 'Draw by repitition'
            show_text(chess_board, text)

        if not game_over and not human_turn:
            ai_move = Searcher.find_move(gs, valid_moves)
            gs.make_move(ai_move)
            move_made = True

        clock.tick(MAX_FPS)
        p.display.flip()
        show_board(chess_board)
        show_moves(chess_board, gs, valid_moves, sq_selected)
        show_pieces(chess_board, gs)

if __name__ == "__main__":
    main()