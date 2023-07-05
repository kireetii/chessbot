ROWS = COLS = 8

class GameState():
    def __init__(self):
        # The board is an 8x8 2D list with 2 characters at each place
        # The first character represents the color of the piece
        # The second character represents the piece
        # '--'represents empty square
        self.board = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'], 
            ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
            ['--', '--', '--', '--', '--', '--', '--', '--'], 
            ['--', '--', '--', '--', '--', '--', '--', '--'], 
            ['--', '--', '--', '--', '--', '--', '--', '--'], 
            ['--', '--', '--', '--', '--', '--', '--', '--'], 
            ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']
        ]
        
        self.move_functions = {'p' : self.pawn_moves, 'R' : self.rook_moves, 'N' : self.knight_moves,
                              'B' : self.bishop_moves, 'Q' : self.queen_moves, 'K': self.king_moves}
        self.white_to_move = True
        self.move_log = []
        # locations of kings
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)
        self.in_check = False
        self.pins = []
        self.checks = []
        self.checkmate = False
        self.stalemate = False
        self.three_move_draw = False
        self.en_passant_square = ()
        self.castling = self.Castling(True, True, True, True)
        self.castle_log = [(True, True, True, True)]

    def make_move(self, move):
        """
        Takes a move and executes it
        """
        self.board[move.initial_pos_x][move.initial_pos_y] = '--'
        self.board[move.final_pos_x][move.final_pos_y] = move.piece_moved
        self.move_log.append(move)
        self.white_to_move = not self.white_to_move

        if move.piece_moved == 'wK':
            self.white_king_location = (move.final_pos_x, move.final_pos_y)
        if move.piece_moved == 'bK':
            self.black_king_location = (move.final_pos_x, move.final_pos_y)

        # Pawn promotion
        if move.is_pawn_promotion:
            self.board[move.final_pos_x][move.final_pos_y] = move.piece_moved[0] + 'Q'
        # en passant
        if move.is_en_passant_move:
            self.board[move.initial_pos_x][move.final_pos_y] = '--'
        # updating en_passant square
        if move.piece_moved[1] == 'p' and abs(move.initial_pos_x-move.final_pos_x) == 2:
            self.en_passant_square = ((move.initial_pos_x+move.final_pos_x) // 2, move.initial_pos_y)
        else:
            self.en_passant_square = ()
        # castling
        if move.is_castle_move:
            if move.final_pos_y - move.initial_pos_y == 2:
                # king side castling
                self.board[move.final_pos_x][move.final_pos_y-1] = self.board[move.final_pos_x][move.final_pos_y+1]
                self.board[move.final_pos_x][move.final_pos_y+1] = '--'
            if move.final_pos_y - move.initial_pos_y == -2:
                # queen side castling
                self.board[move.final_pos_x][move.final_pos_y+1] = self.board[move.final_pos_x][move.final_pos_y-2]
                self.board[move.final_pos_x][move.final_pos_y-2] = '--'
        # updating castling rights
        self.update_castling_rights(move)
        self.castle_log.append((self.castling.wks, self.castling.wqs, self.castling.bks, self.castling.bqs))

        self.check_three_move_draw()

    def undo_move(self):
        if len(self.move_log) != 0:
            move = self.move_log.pop()
            self.board[move.initial_pos_x][move.initial_pos_y] = move.piece_moved
            self.board[move.final_pos_x][move.final_pos_y] = move.piece_captured
            self.white_to_move = not self.white_to_move     # swtiching turns
            # update kings position
            if move.piece_moved == 'wK':
                self.white_king_location = (move.initial_pos_x, move.initial_pos_y)
            elif move.piece_moved == 'bK':
                self.black_king_location = (move.initial_pos_x, move.initial_pos_y)
            # undo en passant
            if move.is_en_passant_move:
                self.board[move.final_pos_x][move.final_pos_y] = '--'
                self.board[move.initial_pos_x][move.final_pos_y] = move.piece_captured
                self.en_passant_square = (move.final_pos_x, move.final_pos_y)
            # undo 2 square pawn move
            if move.piece_moved[1] == 'p' and abs(move.final_pos_x - move.initial_pos_x) == 2:
                self.en_passant_square = ()
            # undo castling rights
            self.castle_log.pop()
            self.castling.wks, self.castling.wqs, self.castling.bks, self.castling.wqs = self.castle_log[-1]
            # undo castle move
            if move.is_castle_move:
                # kingside castle
                if move.final_pos_y - move.initial_pos_y == 2:  
                    self.board[move.final_pos_x][move.final_pos_y+1] = self.board[move.final_pos_x][move.final_pos_y-1]
                    self.board[move.final_pos_x][move.final_pos_y-1] = '--'
                # queenside castle
                else:  
                    self.board[move.final_pos_x][move.final_pos_y-2] = self.board[move.final_pos_x][move.final_pos_y+1]
                    self.board[move.final_pos_x][move.final_pos_y+1] = '--'

            if self.checkmate:
                self.checkmate = False

            if self.stalemate:
                self.stalemate = False
            
            if self.three_move_draw:
                self.three_move_draw = False

    class Castling():
        """
        Keeps track of which side we are able to castle
        """
        def __init__(self, wks, wqs, bks, bqs):
            self.wks = wks
            self.wqs = wqs
            self.bks = bks
            self.bqs = bqs

    def check_three_move_draw(self):
        if len(self.move_log) >= 10:
            if self.move_log[-1].move_id == self.move_log[-5].move_id == self.move_log[-9].move_id and \
            self.move_log[-2].move_id == self.move_log[-6].move_id == self.move_log[-10].move_id:
                self.three_move_draw = True

    def update_castling_rights(self, move):
        piece = move.piece_moved[1]
        color = move.piece_moved[0]
        i_x = move.initial_pos_x
        i_y = move.initial_pos_y
        if piece == 'K':
            if color == 'w':
                self.castling.wks = False
                self.castling.wqs = False
            elif color == 'b':
                self.castling.bks = False
                self.castling.bqs = False
        elif piece == 'R':
            if color == 'w':
                if (i_x, i_y) == (7, 0):
                    self.castling.wqs = False
                elif (i_x, i_y) == (7, 7):
                    self.castling.wks = False
            elif color == 'b':
                if (i_x, i_y) == (0, 0):
                    self.castling.bqs = False
                elif (i_x, i_y) == (0, 7):
                    self.castling.bks = False
        # rook gets captured
        if self.castling.wks and self.board[7][7] != 'wR':
            self.castling.wks = False
        if self.castling.wqs and self.board[7][0] != 'wR':
            self.castling.wqs = False
        if self.castling.bks and self.board[0][7] != 'bR':
            self.castling.bks = False
        if self.castling.bqs and self.board[0][0] != 'bR':
            self.castling.bqs = False

    def in_range(self, row, col):
        """
        Checks if the square is inside the board range
        """
        return 0 <= row <= 7 and 0 <= col <= 7
    
    def has_piece(self, row, col):
        """
        Checks whether the square has a piece or not
        """
        return self.board[row][col] != '--'
    
    def is_empty(self, row, col):
        """
        Checks whether the square is empty or not
        """
        return self.board[row][col] == '--'
    
    def has_friendly_piece(self, row, col, color):
        """
        Checks if the square contains a piece of the same color
        """
        return self.board[row][col][0] == color
    
    def has_enemy_piece(self, row, col, color):
        """
        Checks if the square contains a piece of the opposite color
        """
        return self.board[row][col][0] != color

    def get_valid_moves(self):
        """
        All legal moves for a given game state with considering checks
        """
        if self.white_to_move:
            color = 'w'
            king_row = self.white_king_location[0]
            king_col = self.white_king_location[1]
        else:
            color = 'b'
            king_row = self.black_king_location[0]
            king_col = self.black_king_location[1]

        moves = []
        self.in_check, self.checks, self.pins = self.check_for_pins_and_checks()
        if self.in_check:
            if len(self.checks) == 1:
                moves = self.get_possible_moves()
                check = self.checks[0]
                check_row = check[0]
                check_col = check[1]
                piece_checking = self.board[check_row][check_col][1]
                valid_squares = []
                if piece_checking == 'N':
                    valid_squares = [(check_row, check_col)]
                else:   # block or capture
                    for i in range(1, 8):
                        valid_square = (king_row + check[2] * i, king_col + check[3] * i)
                        valid_squares.append(valid_square)
                        if valid_square[0] == check_row and valid_square[1] == check_col:
                            # capturing the piece
                            break
                # remove invalid moves
                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].piece_moved[1] != 'K':
                        if not (moves[i].final_pos_x, moves[i].final_pos_y) in valid_squares:
                            moves.remove(moves[i])
            else:
                self.king_moves(king_row, king_col, color, moves)
        else:
            moves = self.get_possible_moves()

        if moves == []:
            if self.in_check:
                self.checkmate = True
            else:
                self.stalemate = True
        return moves

    def get_possible_moves(self,):
        """
        All possible moves for a given game state without considering checks
        """
        possible_moves = []
        for row in range(ROWS):
            for col in range(COLS):

                color = self.board[row][col][0]
                if (color == 'w' and self.white_to_move) or (color == 'b' and not self.white_to_move):
                    piece = self.board[row][col][1]
                    self.move_functions[piece](row, col, color, possible_moves)

        return possible_moves

    def check_for_pins_and_checks(self):
        in_check = False
        pins = []
        checks = []

        if self.white_to_move:
            ally_color = 'w'
            rival_color = 'b'
            king_row = self.white_king_location[0]
            king_col = self.white_king_location[1]
        else:
            ally_color = 'b'
            rival_color = 'w'
            king_row = self.black_king_location[0]
            king_col = self.black_king_location[1]
        # check outward from king location in all directions
        directions = ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, 1), (-1, -1), (1, 1), (1, -1))
        for j in range(len(directions)):
            d = directions[j]
            possible_pin = ()
            for i in range(1, 8):
                final_row = king_row + d[0] * i
                final_col = king_col + d[1] * i
                if self.in_range(final_row, final_col):
                    piece_encountered = self.board[final_row][final_col]
                    if piece_encountered[0] == ally_color and piece_encountered[1] != 'K':
                        if possible_pin == ():  
                            possible_pin = (final_row, final_col, d[0], d[1])
                        else:
                            possible_pin = ()
                            break
                    elif piece_encountered[0] == rival_color:
                        piece_type = piece_encountered[1]
                        # Five possibilities:
                        # 1) Rook in straight line from king
                        # 2) Bishop diagonally
                        # 3) Queen in any direction
                        # 4) Pawn one square away diagonally
                        # 5) King one square away in any direction
                        if (0 <= j <= 3 and piece_type == 'R') or \
                        (4 <= j <= 7 and piece_type == 'B') or \
                        (piece_type == 'Q') or \
                        (i == 1 and piece_type == 'p' and \
                            ((rival_color == 'b' and 4 <= j <= 5) or (rival_color == 'w' and 6 <= j <= 7))) or \
                        (i == 1 and piece_type == 'K'):
                            if possible_pin == ():
                                in_check = True
                                checks.append((final_row, final_col, d[0], d[1]))
                            else:
                                pins.append(possible_pin)
                                break
                        else:
                            break
        # knight checks
        knight_squares = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (2, -1), (2, 1), (1, -2), (1, 2))
        for square in knight_squares:
            final_row = king_row + square[0]
            final_col = king_col + square[1]
            if self.in_range(final_row, final_col):
                piece_encountered = self.board[final_row][final_col]
                if piece_encountered[0] == rival_color and piece_encountered[1] == 'N':
                    in_check = True
                    checks.append((final_row, final_col, square[0], square[1]))
        return in_check, checks, pins

    def pawn_moves(self, row, col, color, possible_moves):
        """
        Returns all the possible moves for pawns
        """
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) -1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        direction = -1 if color == 'w' else 1
        steps = 1
        init_row = 6 if color == 'w' else 1
        if row == init_row:
            steps = 2
        
        # straight moves
        for step in range(1, steps+1):
            move_row = row + step * direction
            move_col = col
            if self.in_range(move_row, col):
                if self.is_empty(move_row, col):
                    if not piece_pinned or pin_direction == (direction, 0):
                        possible_moves.append(Move((row, col), (move_row, move_col), self.board))

                else:
                    break
            else:
                break
        
        # diagonal moves
        move_row = row + direction
        r = 3 if self.board[row][col][0] == 'w' else 4
        for c in [-1, 1]:
            move_col = col + c
            if self.in_range(move_row, move_col):
                if self.has_piece(move_row, move_col) and \
                    self.has_enemy_piece(move_row, move_col, color):
                    if not piece_pinned or pin_direction == (direction, c):
                        possible_moves.append(Move((row, col), (move_row, move_col), self.board))
                
                # en passant
                elif (row == r) and \
                    (move_row, move_col) == self.en_passant_square:
                    if not piece_pinned or pin_direction == (direction, c):
                        possible_moves.append(Move((row, col), (move_row, move_col), self.board, is_en_passant_move = True))

    def knight_moves(self, row, col, color, possible_moves):
        """
        Get all possible moves for knights
        """
        piece_pinned = False
        for i in range(len(self.pins) -1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                self.pins.remove(self.pins[i])
                break
        knight_moves = [
            (-2, -1),
            (-1, -2),
            (1, -2),
            (2, -1),
            (-2, 1),
            (1, 2),
            (-1, 2),
            (2, 1)
            ]
        
        for knight_move in knight_moves:
            move_row, move_col = row + knight_move[0], col + knight_move[1]
            if self.in_range(move_row, move_col) and \
                not self.has_friendly_piece(move_row, move_col, color):
                if not piece_pinned:
                    possible_moves.append(Move((row, col), (move_row, move_col), self.board))

    def straight_moves(self, row, col, color, incrs, possible_moves):
        """
        Get all possible moves for pieces moving in straight lines
        """
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) -1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        for incr in incrs:
            incr_row, incr_col = incr
            move_row, move_col = row + incr_row, col + incr_col
            while self.in_range(move_row, move_col):
                if self.is_empty(move_row, move_col):
                    if not piece_pinned or pin_direction == (incr_row, incr_col):
                        possible_moves.append(Move((row, col), (move_row, move_col), self.board))
                    
                    move_row += incr_row
                    move_col += incr_col

                elif self.has_enemy_piece(move_row, move_col, color):
                    if not piece_pinned or pin_direction == (incr_row, incr_col):
                        possible_moves.append(Move((row, col), (move_row, move_col), self.board))
                    break

                else:
                    break

    def rook_moves(self, row, col, color, possible_moves):
        """
        Get all possible moves for rooks
        """
        incrs = [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1)
            ]
        return self.straight_moves(row, col, color, incrs, possible_moves)

    def bishop_moves(self, row, col, color, possible_moves):
        """
        Get all possible moves for bishops
        """
        incrs = [
            (-1, 1),
            (-1, -1),
            (1, -1),
            (1, 1)
        ]
        return self.straight_moves(row, col, color, incrs, possible_moves)

    def queen_moves(self, row, col, color, possible_moves):
        """
        Get all possible moves for queen
        """
        incrs = [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
            (-1, 1),
            (-1, -1),
            (1, -1),
            (1, 1)
            ]
        self.straight_moves(row, col, color, incrs, possible_moves)

    def king_moves(self, row, col, color, possible_moves):
        """
        Get all possible moves for king
        """
        king_moves = [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
            (-1, 1),
            (-1, -1),
            (1, -1),
            (1, 1)
        ]

        def can_move(move_row, move_col):
            # move king temporarily
            if self.white_to_move:
                self.white_king_location = (move_row, move_col)
            else:
                self.black_king_location = (move_row, move_col)
            in_check, pins, checks = self.check_for_pins_and_checks()
                
            # move king back to original square
            if self.white_to_move:
                self.white_king_location = (row, col)
            else:
                self.black_king_location = (row, col)

            return not in_check
        
        for king_move in king_moves:
            move_row, move_col = row + king_move[0], col + king_move[1]
            if self.in_range(move_row, move_col) and \
                not self.has_friendly_piece(move_row, move_col, color):
                if can_move(move_row, move_col):
                    possible_moves.append(Move((row, col), (move_row, move_col), self.board))
                    
        # castling moves
        def castle_moves():
            """
            Castling moves
            """
            if self.in_check:
                return      # cannot castle while in check
            if (self.white_to_move and self.castling.wks) or (not self.white_to_move and self.castling.bks):
                # king side castling
                if self.board[row][col+1] == '--' and self.board[row][col+2] == '--':
                    if can_move(row, col+1) and can_move(row, col+2):
                        possible_moves.append(Move((row, col), (row, col+2), self.board, is_castle_move = True))
            if (self.white_to_move and self.castling.wqs) or (not self.white_to_move and self.castling.bqs):
                # queen side castling
                if self.board[row][col-1] == '--' and self.board[row][col-2] == '--' and \
                self.board[row][col-3] == '--':
                    if can_move(row, col-1) and can_move(row, col-2):
                        possible_moves.append(Move((row, col), (row, col-2), self.board, is_castle_move = True))

        castle_moves()

class Move():

    def __init__(self, initial, final, board, is_en_passant_move = False, is_castle_move = False):
        
        self.initial_pos_x = initial[0]
        self.initial_pos_y = initial[1]
        self.final_pos_x = final[0]
        self.final_pos_y = final[1]
        self.piece_moved = board[self.initial_pos_x][self.initial_pos_y]
        self.piece_captured = board[self.final_pos_x][self.final_pos_y]
        self.is_capture = False
        if self.piece_captured != '--':
            self.is_capture = True
        self.move_id = (self.initial_pos_x) * 1000 + (self.initial_pos_y) * 100 + \
                        (self.final_pos_x) * 10 + (self.final_pos_y)
        self.move_score = 0
        # pawn promotion
        self.is_pawn_promotion = (self.piece_moved == 'wp' and self.final_pos_x == 0) or \
            (self.piece_moved == 'bp' and self.final_pos_x == 7)
        # en passant
        self.is_en_passant_move = is_en_passant_move
        if self.is_en_passant_move:
            self.piece_captured = board[self.initial_pos_x][self.final_pos_y]
        # castling
        self.is_castle_move = is_castle_move

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id
        


