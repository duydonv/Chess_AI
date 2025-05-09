import os
import copy

from const import *
from square import Square
from piece import *
from move import Move
from sound import Sound

class Board:

    def __init__(self):
        self.squares = [[0, 0, 0, 0, 0, 0, 0, 0] for col in range(COLS)]
        self.last_move = None
        self._creat()
        self._add_piece('white')
        self._add_piece('black')

    def move(self, piece, move, testing=False):
        initial = move.initial
        final = move.final

        en_passant_empty = self.squares[final.row][final.col].isempty()

        # cập nhật vị trí quân cờ
        self.squares[initial.row][initial.col].piece = None
        self.squares[final.row][final.col].piece = piece
        
        if isinstance(piece, Pawn):
            # bắt tốt qua đường
            diff = final.col - initial.col
            if diff != 0 and en_passant_empty:
                # console board move update
                self.squares[initial.row][initial.col + diff].piece = None
                self.squares[final.row][final.col].piece = piece
                if not testing:
                    sound = Sound(
                        os.path.join('assets/sounds/capture.wav'))
                    sound.play()

            # # phong cấp tốt
            # else:
            #     self.check_promotion(piece, final)

        # nhập thành
        if isinstance(piece, King):
            if self.castling(initial, final) and not testing:
                diff = final.col - initial.col
                rook = piece.left_rook if (diff < 0) else piece.right_rook
                self.move(rook, rook.moves[-1])
        # đánh dấu đã di chuyển
        piece.moved = True

        # xóa các bước có thể đi ở vị trí cũ
        piece.clear_moves()

        # lưu vị trí cũ
        self.last_move = move

    def valid_move(self, piece, move):
        return move in piece.moves
    
    def check_promotion(self, piece, final):
        if final.row == 0 or final.row == 7:
            self.squares[final.row][final.col].promotion = True

    def castling(seft, initial, final):
        return abs(initial.col - final.col) == 2
    
    # kiểm tra xem có quân địch nào chặn đường nhập thành hay không
    def check_castling(self, color):
        check_squares = [Square(7,2), Square(7,3), Square(7,5), Square(7,6)]
        temp_board = copy.deepcopy(self)
        for row in range(ROWS):
            for col in range(COLS):
                if temp_board.squares[row][col].has_enemy_piece(color):
                    p = temp_board.squares[row][col].piece
                    temp_board.calc_moves(p, row, col, bool=False)
                    for m in p.moves:
                        if m.final in check_squares:
                            return True
        return False
    
    def set_true_en_passant(self, piece):
        
        if not isinstance(piece, Pawn):
            return

        for row in range(ROWS):
            for col in range(COLS):
                if isinstance(self.squares[row][col].piece, Pawn):
                    self.squares[row][col].piece.en_passant = False
        
        piece.en_passant = True
    
    # kiểm tra có phải nước cuối ko
    def in_check(self, piece1, move1, piece2=None, move2=None):
        temp_board = copy.deepcopy(self)
        temp_piece = copy.deepcopy(piece1)
        temp_board.move(temp_piece, move1, testing=True)
        if(piece2 != None):
            temp_piece = copy.deepcopy(piece2)
            temp_board.move(temp_piece, move2, testing=True)

        for row in range(ROWS):
            for col in range(COLS):
                if temp_board.squares[row][col].has_enemy_piece(piece1.color):
                    p = temp_board.squares[row][col].piece
                    temp_board.calc_moves(p, row, col, bool=False)
                    for m in p.moves:
                        if isinstance(m.final.piece, King):
                            return True
        
        return False

    # thêm bool tạo sự khác biệt giữa khi gọi ở in_check để ko bị gọi đệ quy
    def calc_moves(self, piece, row, col, bool=True):

        def pawn_moves():
            # đi thẳng = 2 nếu là first move 
            steps = 1 if piece.moved else 2

            start = row + piece.dir
            end = row + (piece.dir * (1 + steps))
            for move_row in range(start, end, piece.dir):
                if Square.in_range(move_row):
                    if self.squares[move_row][col].isempty():
                        initial = Square(row, col)
                        final = Square(move_row, col)
                        move = Move(initial, final)
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                        else:
                            piece.add_move(move)
                    else: break
                else: break
            
            # ăn chéo
            possible_move_row = row + piece.dir
            possible_move_cols = [col-1, col+1]
            for possible_move_col in possible_move_cols:
                if Square.in_range(possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].has_enemy_piece(piece.color):
                        initial = Square(row, col)
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final = Square(possible_move_row, possible_move_col, final_piece)
                        move = Move(initial, final)
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                        else:
                            piece.add_move(move)

            # bắt tốt qua đường
            r = 3 if piece.color == 'white' else 4
            fr = 2 if piece.color == 'white' else 5
            if Square.in_range(col-1) and row == r:
                if self.squares[row][col-1].has_enemy_piece(piece.color):
                    p = self.squares[row][col-1].piece
                    if isinstance(p, Pawn):
                        if p.en_passant:
                            initial = Square(row, col)
                            final = Square(fr, col-1, p)
                            move = Move(initial, final)
                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)
                            else:
                                piece.add_move(move)
            
            if Square.in_range(col+1) and row == r:
                if self.squares[row][col+1].has_enemy_piece(piece.color):
                    p = self.squares[row][col+1].piece
                    if isinstance(p, Pawn):
                        if p.en_passant:
                            initial = Square(row, col)
                            final = Square(fr, col+1, p)
                            move = Move(initial, final)
                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)
                            else:
                                piece.add_move(move)

        def knight_moves():
            # quân mã có 8 nước đi
            possible_moves = [
                (row-2, col+1),
                (row-1, col+2),
                (row+1, col+2),
                (row+2, col+1),
                (row+2, col-1),
                (row+1, col-2),
                (row-1, col-2),
                (row-2, col-1),
            ]

            for possible_move in possible_moves:
                possible_move_row, possible_move_col = possible_move

                if Square.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].isempty_or_enemy(piece.color):
                        initial = Square(row, col)
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final  = Square(possible_move_row, possible_move_col, final_piece)
                        move = Move(initial, final)
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                            else: break
                        else:
                            piece.add_move(move)

        def straightline_moves(incrs):
            for incr in incrs:
                row_incr, col_incr = incr
                possible_move_row = row + row_incr
                possible_move_col = col + col_incr
                while True:
                    if Square.in_range(possible_move_row, possible_move_col):
                        initial = Square(row, col)
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final  = Square(possible_move_row, possible_move_col, final_piece)

                        move = Move(initial, final)
                        
                        if self.squares[possible_move_row][possible_move_col].isempty():
                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)
                            else:
                                piece.add_move(move)

                        elif self.squares[possible_move_row][possible_move_col].has_enemy_piece(piece.color):
                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)
                            else:
                                piece.add_move(move)
                            break
                        elif self.squares[possible_move_row][possible_move_col].has_team_piece(piece.color):
                            break
                    else: break
                    possible_move_row = possible_move_row + row_incr
                    possible_move_col = possible_move_col + col_incr

        def king_moves():
            adjs = [
                (row-1, col+0), 
                (row-1, col+1), 
                (row+0, col+1),
                (row+1, col+1), 
                (row+1, col+0), 
                (row+1, col-1),
                (row+0, col-1), 
                (row-1, col-1), 
            ]

            for possible_move in adjs:
                possible_move_row, possible_move_col = possible_move

                if Square.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].isempty_or_enemy(piece.color):
                        initial = Square(row, col)
                        final = Square(possible_move_row, possible_move_col) 
                        move = Move(initial, final)
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                        else:
                            piece.add_move(move)

            # nhập thành
            if not piece.moved:
                left_rook = self.squares[row][0].piece
                if isinstance(left_rook, Rook):
                    if not left_rook.moved:
                        for c in range(1, 4):
                            if self.squares[row][c].has_piece():
                                break

                            if c == 3:
                                piece.left_rook = left_rook

                                initial = Square(row, 0)
                                final = Square(row, 3)
                                moveR = Move(initial, final)

                                initial = Square(row, col)
                                final = Square(row, 2)
                                moveK = Move(initial, final)

                                if not self.check_castling(piece.color):
                                    if bool:
                                        if not self.in_check(piece, moveK, left_rook, moveR):
                                            left_rook.add_move(moveR)
                                            piece.add_move(moveK)
                                    else:
                                        left_rook.add_move(moveR)
                                        piece.add_move(moveK)

                right_rook = self.squares[row][7].piece
                if isinstance(right_rook, Rook):
                    if not right_rook.moved:
                        for c in range(5, 7):
                            if self.squares[row][c].has_piece():
                                break

                            if c == 6:
                                piece.right_rook = right_rook

                                initial = Square(row, 7)
                                final = Square(row, 5)
                                moveR = Move(initial, final)

                                initial = Square(row, col)
                                final = Square(row, 6)
                                moveK = Move(initial, final)
                                if not self.check_castling(piece.color):
                                    if bool:
                                        if not self.in_check(piece, moveK, right_rook, moveR):
                                            right_rook.add_move(moveR)
                                            piece.add_move(moveK)
                                    else:
                                        right_rook.add_move(moveR)
                                        piece.add_move(moveK)

        if isinstance(piece, Pawn): 
            pawn_moves()

        elif isinstance(piece, Knight): 
            knight_moves()

        elif isinstance(piece, Bishop): 
            straightline_moves([
                (-1, 1),
                (-1, -1),
                (1, 1),
                (1, -1)
            ])

        elif isinstance(piece, Rook): 
            straightline_moves([
                (-1, 0),
                (0, 1),
                (1, 0),
                (0, -1)
            ])

        elif isinstance(piece, Queen): 
            straightline_moves([
                (-1, 1),
                (-1, -1),
                (1, 1),
                (1, -1),
                (-1, 0),
                (0, 1),
                (1, 0),
                (0, -1)
            ])

        elif isinstance(piece, King): 
            king_moves()

    def _creat(self):
        for row in range(ROWS):
            for col in range(COLS):
                self.squares[row][col] = Square(row, col)

    def _add_piece(self, color):
        row_pawn, row_other = (6, 7) if color == "white" else (1, 0)
        
        # tạo quân tốt
        for col in range(COLS):
            self.squares[row_pawn][col] = Square(row_pawn, col, Pawn(color))
        # tạo quân mã
        self.squares[row_other][1] = Square(row_pawn, col, Knight(color))
        self.squares[row_other][6] = Square(row_pawn, col, Knight(color))

        # tạo quân tượng
        self.squares[row_other][2] = Square(row_pawn, col, Bishop(color))
        self.squares[row_other][5] = Square(row_pawn, col, Bishop(color))

        # tạo quân xe
        self.squares[row_other][0] = Square(row_pawn, col, Rook(color))
        self.squares[row_other][7] = Square(row_pawn, col, Rook(color))

        # tạo quân hậu
        self.squares[row_other][3] = Square(row_pawn, col, Queen(color))

        # tạo quân vua
        self.squares[row_other][4] = Square(row_pawn, col, King(color))