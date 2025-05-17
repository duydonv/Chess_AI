import os
import copy

from const import *
from square import Square
from piece import *
from move import Move
from sound import Sound

class MoveState:
    def __init__(self, initial, final, moved_piece, captured_piece, last_move, move_number, en_passant_state, moved_piece_moved, captured_piece_moved, castle_info=None):
        self.initial = initial
        self.final = final
        self.moved_piece = moved_piece
        self.captured_piece = captured_piece
        self.last_move = last_move
        self.move_number = move_number
        self.en_passant_state = en_passant_state
        self.moved_piece_moved = moved_piece_moved
        self.captured_piece_moved = captured_piece_moved
        self.castle_info = castle_info  # dict chứa thông tin nhập thành nếu có

class Board:

    def __init__(self):
        # Sử dụng list lồng nhau để biểu diễn bàn cờ (tối ưu hơn numpy object array)
        self.squares = [[Square(row, col) for col in range(8)] for row in range(8)]
        self.last_move = None
        self.move_number = 0  # Thêm biến đếm số nước đi
        self._create()
        #self.setup_king_vs_full() # Dùng để test bàn cờ gỡ
        self._move_cache = {}  # Cache cho các nước đi
        self._valid_moves_cache = {}  # Cache cho các nước đi hợp lệ
        self._check_cache = {}  # Cache cho trạng thái chiếu
        self.move_stack = []  # Stack lưu trạng thái để undo

    def move(self, piece, move, testing=False):
        initial = move.initial
        final = move.final
        en_passant_empty = self.squares[final.row][final.col].isempty()
        # cập nhật vị trí quân cờ
        self.squares[initial.row][initial.col].piece = None
        self.squares[final.row][final.col].piece = piece
        # Bắt tốt qua đường
        if isinstance(piece, Pawn):
            diff = final.col - initial.col
            if diff != 0 and en_passant_empty:
                self.squares[initial.row][initial.col + diff].piece = None
                self.squares[final.row][final.col].piece = piece
        # Nhập thành
        if isinstance(piece, King):
            if abs(final.col - initial.col) == 2 and not testing:
                row = initial.row
                if final.col > initial.col:
                    # Nhập thành gần
                    rook_from = self.squares[row][7].piece
                    self.squares[row][7].piece = None
                    self.squares[row][final.col-1].piece = rook_from
                    if rook_from is not None:
                        rook_from.moved = True
                else:
                    # Nhập thành xa
                    rook_from = self.squares[row][0].piece
                    self.squares[row][0].piece = None
                    self.squares[row][final.col+1].piece = rook_from
                    if rook_from is not None:
                        rook_from.moved = True
        # đánh dấu đã di chuyển
        piece.moved = True
        # xóa các bước có thể đi ở vị trí cũ
        piece.clear_moves()
        # lưu vị trí cũ
        self.last_move = move
        # Tăng số nước đi
        if not testing:
            self.move_number += 1
        # Xóa cache
        self._move_cache.clear()
        self._valid_moves_cache.clear()
        self._check_cache.clear()

    def valid_move(self, piece, move):
        # Kiểm tra cache
        cache_key = (piece, move.initial.row, move.initial.col, move.final.row, move.final.col, self.get_board_state())
        if cache_key in self._valid_moves_cache:
            return self._valid_moves_cache[cache_key]

        # Kiểm tra nước đi có trong danh sách nước đi có thể không
        self.calc_moves(piece, move.initial.row, move.initial.col)
        if move not in piece.moves:
            self._valid_moves_cache[cache_key] = False
            return False

        # Thử đi nước cờ
        initial_piece = self.squares[move.initial.row][move.initial.col].piece
        final_piece = self.squares[move.final.row][move.final.col].piece
        self.squares[move.final.row][move.final.col].piece = initial_piece
        self.squares[move.initial.row][move.initial.col].piece = None
        still_in_check = self._is_king_in_check(piece.color)
        self.squares[move.initial.row][move.initial.col].piece = initial_piece
        self.squares[move.final.row][move.final.col].piece = final_piece

        # Lưu vào cache
        self._valid_moves_cache[cache_key] = not still_in_check
        return not still_in_check
    
    def set_true_en_passant(self, piece):
        
        if not isinstance(piece, Pawn):
            return

        for row in range(ROWS):
            for col in range(COLS):
                if isinstance(self.squares[row][col].piece, Pawn):
                    self.squares[row][col].piece.en_passant = False
        
        piece.en_passant = True
    

    def calc_moves(self, piece, row, col, checking_checks=False ):
        piece.clear_moves()
        
        # Kiểm tra cache
        cache_key = (piece, row, col, checking_checks, self.get_board_state())
        if cache_key in self._move_cache:
            piece.moves = self._move_cache[cache_key]
            return piece.moves

        # Tính toán các nước đi có thể
        if piece.name == 'pawn':
            self._calc_pawn_moves(piece, row, col)
        elif piece.name == 'knight':
            self._calc_knight_moves(piece, row, col)
        elif piece.name == 'bishop':
            self._calc_bishop_moves(piece, row, col)
        elif piece.name == 'rook':
            self._calc_rook_moves(piece, row, col)
        elif piece.name == 'queen':
            self._calc_queen_moves(piece, row, col)
        elif piece.name == 'king':
            self._calc_king_moves(piece, row, col, checking_checks)


        # Lưu vào cache
        self._move_cache[cache_key] = piece.moves
        return piece.moves

    def _calc_pawn_moves(self, piece, row, col):
        # Tối ưu hóa việc tính toán nước đi của tốt
        if piece.color == 'white':
            # Di chuyển lên
            if row > 0 and not self.squares[row-1][col].has_piece():
                piece.add_move(Move(Square(row, col), Square(row-1, col)))
                # Di chuyển 2 ô ở nước đầu
                if row == 6 and not self.squares[row-2][col].has_piece():
                    piece.add_move(Move(Square(row, col), Square(row-2, col)))
            # Ăn chéo
            for col_offset in [-1, 1]:
                if 0 <= col + col_offset < 8 and row > 0:
                    if self.squares[row-1][col+col_offset].has_enemy_piece(piece.color):
                        piece.add_move(Move(Square(row, col), Square(row-1, col+col_offset)))
                    # Bắt tốt qua đường
                    elif row == 3 and self.squares[row][col+col_offset].has_piece():
                        p = self.squares[row][col+col_offset].piece
                        if isinstance(p, Pawn) and p.en_passant:
                            piece.add_move(Move(Square(row, col), Square(row-1, col+col_offset)))
        else:
            # Di chuyển xuống
            if row < 7 and not self.squares[row+1][col].has_piece():
                piece.add_move(Move(Square(row, col), Square(row+1, col)))
                # Di chuyển 2 ô ở nước đầu
                if row == 1 and not self.squares[row+2][col].has_piece():
                    piece.add_move(Move(Square(row, col), Square(row+2, col)))
            # Ăn chéo
            for col_offset in [-1, 1]:
                if 0 <= col + col_offset < 8 and row < 7:
                    if self.squares[row+1][col+col_offset].has_enemy_piece(piece.color):
                        piece.add_move(Move(Square(row, col), Square(row+1, col+col_offset)))
                    # Bắt tốt qua đường
                    elif row == 4 and self.squares[row][col+col_offset].has_piece():
                        p = self.squares[row][col+col_offset].piece
                        if isinstance(p, Pawn) and p.en_passant:
                            piece.add_move(Move(Square(row, col), Square(row+1, col+col_offset)))

    def _calc_knight_moves(self, piece, row, col):
        # Tối ưu hóa việc tính toán nước đi của mã
        knight_moves = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]
        for row_offset, col_offset in knight_moves:
            new_row, new_col = row + row_offset, col + col_offset
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                if not self.squares[new_row][new_col].has_team_piece(piece.color):
                    piece.add_move(Move(Square(row, col), Square(new_row, new_col)))

    def _calc_bishop_moves(self, piece, row, col):
        # Tối ưu hóa việc tính toán nước đi của tượng
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        self._calc_sliding_moves(piece, row, col, directions)

    def _calc_rook_moves(self, piece, row, col):
        # Tối ưu hóa việc tính toán nước đi của xe
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        self._calc_sliding_moves(piece, row, col, directions)

    def _calc_queen_moves(self, piece, row, col):
        # Tối ưu hóa việc tính toán nước đi của hậu
        directions = [
            (-1, -1), (-1, 1), (1, -1), (1, 1),  # Đường chéo
            (-1, 0), (1, 0), (0, -1), (0, 1)     # Đường thẳng
        ]
        self._calc_sliding_moves(piece, row, col, directions)

    def _calc_king_moves(self, piece, row, col,  checking_checks=False):
        # Nước đi thường của vua
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for row_offset, col_offset in directions:
            new_row, new_col = row + row_offset, col + col_offset
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                if not self.squares[new_row][new_col].has_team_piece(piece.color):
                    piece.add_move(Move(Square(row, col), Square(new_row, new_col)))
        # Chỉ thêm nước nhập thành khi không đang "checking_checks"
        if not checking_checks and not piece.moved:
            # Nhập thành gần (king-side)
            if self._can_castle(piece, row, col, king_side=True):
                piece.add_move(Move(Square(row, col), Square(row, col+2)))
            # Nhập thành xa (queen-side)
            if self._can_castle(piece, row, col, king_side=False):
                piece.add_move(Move(Square(row, col), Square(row, col-2)))

    def _can_castle(self, king, row, col, king_side=True):
        # Kiểm tra điều kiện nhập thành gần hoặc xa
        if king.color == 'white':
            back_row = 7
        else:
            back_row = 0
        if king_side:
            rook_col = 7
            step = 1
            between = [col+1, col+2]
        else:
            rook_col = 0
            step = -1
            between = [col-1, col-2, col-3]
        # Kiểm tra xe
        rook = self.squares[back_row][rook_col].piece
        if not (rook and isinstance(rook, Rook) and not rook.moved):
            return False
        # Các ô giữa phải trống
        for c in between:
            if self.squares[back_row][c].has_piece():
                return False
        # Vua không bị chiếu, không đi qua hoặc đến ô bị chiếu
        for c in [col, col+step, col+2*step] if king_side else [col, col-1, col-2]:
            # Swap tạm thời
            orig_king = self.squares[back_row][col].piece
            orig_target = self.squares[back_row][c].piece
            self.squares[back_row][col].piece = None
            self.squares[back_row][c].piece = king
            in_check = self._is_king_in_check(king.color)
            self.squares[back_row][col].piece = orig_king
            self.squares[back_row][c].piece = orig_target
            if in_check:
                return False
        return True

    def _is_king_in_check(self, color):
        # Tìm vị trí vua
        king_pos = None
        for row in range(8):
            for col in range(8):
                piece = self.squares[row][col].piece
                if piece and isinstance(piece, King) and piece.color == color:
                    king_pos = (row, col)
                    break
            if king_pos:
                break
        if not king_pos:
            return False
        # Kiểm tra có quân đối phương nào ăn được vua không
        opponent = 'black' if color == 'white' else 'white'
        for row in range(8):
            for col in range(8):
                piece = self.squares[row][col].piece
                if piece and piece.color == opponent:
                    self.calc_moves(piece, row, col, checking_checks=True )
                    for move in piece.moves:
                        if move.final.row == king_pos[0] and move.final.col == king_pos[1]:
                            return True
        return False

    def _calc_sliding_moves(self, piece, row, col, directions):
        # Tối ưu hóa việc tính toán nước đi trượt (tượng, xe, hậu)
        for row_offset, col_offset in directions:
            new_row, new_col = row + row_offset, col + col_offset
            while 0 <= new_row < 8 and 0 <= new_col < 8:
                if not self.squares[new_row][new_col].has_piece():
                    piece.add_move(Move(Square(row, col), Square(new_row, new_col)))
                elif self.squares[new_row][new_col].has_enemy_piece(piece.color):
                    piece.add_move(Move(Square(row, col), Square(new_row, new_col)))
                    break
                else:
                    break
                new_row += row_offset
                new_col += col_offset

    def _create(self):
        # Khởi tạo bàn cờ với các quân cờ
        for row in range(8):
            for col in range(8):
                self.squares[row][col] = Square(row, col)

        # Đặt quân đen
        self.squares[0][0] = Square(0, 0, Rook('black'))
        self.squares[0][1] = Square(0, 1, Knight('black'))
        self.squares[0][2] = Square(0, 2, Bishop('black'))
        self.squares[0][3] = Square(0, 3, Queen('black'))
        self.squares[0][4] = Square(0, 4, King('black'))
        self.squares[0][5] = Square(0, 5, Bishop('black'))
        self.squares[0][6] = Square(0, 6, Knight('black'))
        self.squares[0][7] = Square(0, 7, Rook('black'))
        for col in range(8):
            self.squares[1][col] = Square(1, col, Pawn('black'))

        # Đặt quân trắng
        self.squares[7][0] = Square(7, 0, Rook('white'))
        self.squares[7][1] = Square(7, 1, Knight('white'))
        self.squares[7][2] = Square(7, 2, Bishop('white'))
        self.squares[7][3] = Square(7, 3, Queen('white'))
        self.squares[7][4] = Square(7, 4, King('white'))
        self.squares[7][5] = Square(7, 5, Bishop('white'))
        self.squares[7][6] = Square(7, 6, Knight('white'))
        self.squares[7][7] = Square(7, 7, Rook('white'))
        for col in range(8):
            self.squares[6][col] = Square(6, col, Pawn('white'))

    def get_board_state(self):
        # Tạo một chuỗi đại diện cho trạng thái bàn cờ
        state = []
        for row in range(8):
            for col in range(8):
                piece = self.squares[row][col].piece
                if piece:
                    state.append(f"{piece.color}_{piece.name}_{row}_{col}")
        return tuple(state)

    def clear_moves_cache(self):
        """
        Xóa cache các nước đi
        """
        self._move_cache.clear()
        self._valid_moves_cache.clear()
        self._check_cache.clear()

    def make_move(self, piece, move):
        """
        Lưu trạng thái và thực hiện nước đi
        """
        # 1. Lưu trạng thái trước khi đi
        initial = move.initial
        final = move.final
        moved_piece = piece
        captured_piece = self.squares[final.row][final.col].piece
        last_move = self.last_move
        move_number = self.move_number
        moved_piece_moved = piece.moved
        captured_piece_moved = captured_piece.moved if captured_piece else None

        # 2. Lưu trạng thái en passant
        en_passant_state = {}
        for row in range(8):
            for col in range(8):
                p = self.squares[row][col].piece
                if p and hasattr(p, 'en_passant'):
                    en_passant_state[(row, col)] = p.en_passant

        # 3. Lưu thông tin nhập thành nếu có
        castle_info = None
        if isinstance(piece, King) and abs(final.col - initial.col) == 2:
            row = initial.row
            if final.col > initial.col:
                rook_from_col = 7
                rook_to_col = final.col - 1
            else:
                rook_from_col = 0
                rook_to_col = final.col + 1
            rook_piece = self.squares[row][rook_from_col].piece
            rook_moved = rook_piece.moved if rook_piece else None
            king_moved = piece.moved
            castle_info = {
                'row': row,
                'rook_from_col': rook_from_col,
                'rook_to_col': rook_to_col,
                'rook_piece': rook_piece,
                'rook_moved': rook_moved,
                'king_piece': piece,
                'king_initial': (initial.row, initial.col),
                'king_final': (final.row, final.col),
                'king_moved': king_moved
            }

        # 4. Tạo và lưu trạng thái
        state = MoveState(
            initial, final, moved_piece, captured_piece,
            last_move, move_number, en_passant_state,
            moved_piece_moved, captured_piece_moved,
            castle_info
        )
        self.move_stack.append(state)

        # 5. Thực hiện nước đi
        self.move(piece, move, False)

    def undo_move(self):
        """
        Khôi phục trạng thái trước nước đi
        """
        if not self.move_stack:
            return

        # 1. Lấy trạng thái cần khôi phục
        state = self.move_stack.pop()

        # 2. Khôi phục nhập thành nếu có
        if state.castle_info is not None:
            info = state.castle_info
            row = info['row']
            # Khôi phục xe
            self.squares[row][info['rook_from_col']].piece = info['rook_piece']
            self.squares[row][info['rook_to_col']].piece = None
            if info['rook_piece']:
                info['rook_piece'].moved = info['rook_moved']
            # Khôi phục vua
            self.squares[info['king_initial'][0]][info['king_initial'][1]].piece = info['king_piece']
            self.squares[info['king_final'][0]][info['king_final'][1]].piece = None
            if info['king_piece']:
                info['king_piece'].moved = info['king_moved']
        else:
            # 3. Khôi phục quân cờ bình thường
            self.squares[state.initial.row][state.initial.col].piece = state.moved_piece
            self.squares[state.final.row][state.final.col].piece = state.captured_piece
            # Khôi phục trạng thái moved
            state.moved_piece.moved = state.moved_piece_moved
            if state.captured_piece:
                state.captured_piece.moved = state.captured_piece_moved

        # 4. Khôi phục trạng thái en passant
        for (row, col), en_passant in state.en_passant_state.items():
            p = self.squares[row][col].piece
            if p and hasattr(p, 'en_passant'):
                p.en_passant = en_passant

        # 5. Khôi phục last_move và move_number
        self.last_move = state.last_move
        self.move_number = state.move_number

        # 6. Xóa cache
        self.clear_moves_cache()

    def get_legal_moves(self, color):
        """
        Lấy tất cả nước đi hợp lệ cho một bên
        """
        legal_moves = []
        for row in range(8):
            for col in range(8):
                piece = self.squares[row][col].piece
                if piece and piece.color == color:
                    self.calc_moves(piece, row, col)
                    for move in piece.moves:
                        if self.valid_move(piece, move):
                            legal_moves.append((piece, move))
        return legal_moves

    def is_checkmate(self, color):
        """
        Kiểm tra có bị chiếu hết không
        """
        if not self._is_king_in_check(color):
            return False

        # Kiểm tra xem có nước đi nào để thoát chiếu không
        legal_moves = self.get_legal_moves(color)
        return len(legal_moves) == 0
    
    def insufficient_material(self):
        pieces = []
        for row in range(8):
            for col in range(8):
                if self.squares[row][col].piece:
                    pieces.append((self.squares[row][col].piece, row, col))

        # Chỉ còn vua
        if len(pieces) == 2:
            return True

        # Vua + mã hoặc vua + tượng vs vua
        if len(pieces) == 3:
            names = [p[0].name for p in pieces]
            if names.count("king") == 2 and ("knight" in names or "bishop" in names):
                return True

        # Vua + tượng vs vua + tượng (cùng màu ô)
        if len(pieces) == 4:
            bishops = [(p, row, col) for p, row, col in pieces if p.name == "bishop"]
            if len(bishops) == 2:
                colors = []
                for _, row, col in bishops:
                    colors.append((row + col) % 2)
                if colors[0] == colors[1]:
                    return True

        return False
    def is_stalemate(self, color):
        """
        Kiểm tra có bị hòa không
        """
        if self._is_king_in_check(color):
            return False
        if self.insufficient_material():
            return True
        # Kiểm tra xem có nước đi hợp lệ nào không
        legal_moves = self.get_legal_moves(color)
        return len(legal_moves) == 0
    def setup_king_vs_full(self):
        # Xóa toàn bộ quân cờ hiện tại
        for row in range(ROWS):
            for col in range(COLS):
                self.squares[row][col].piece = None

        # Trắng: chỉ còn vua
        self.squares[0][4] = Square(0, 4, King('black'))

        # Đặt quân trắng
        self.squares[7][0] = Square(7, 0, Rook('white'))
        self.squares[7][1] = Square(7, 1, Knight('white'))
        self.squares[7][2] = Square(7, 2, Bishop('white'))
        self.squares[7][3] = Square(7, 3, Queen('white'))
        self.squares[7][4] = Square(7, 4, King('white'))
        self.squares[7][5] = Square(7, 5, Bishop('white'))
        self.squares[7][6] = Square(7, 6, Knight('white'))
        self.squares[7][7] = Square(7, 7, Rook('white'))
