import pygame
import pygame.gfxdraw
import time
import sys

from const import *
from board import Board
from piece import *
from dragger import Dragger
from config import Config
from ai import find_best_move

class Game:

    def __init__(self):
        self.next_player = 'white'
        self.promotion_col = False
        self.promotion_color = False
        self.hovered_sqr = None
        self.board = Board()
        self.dragger = Dragger()
        self.config = Config()
        self.ai_enabled = False  # Thêm biến để bật/tắt AI
        self.ai_color = 'black'  # AI sẽ chơi quân đen
        self.game_over = False  # Thêm biến để kiểm tra kết thúc game
        self.ai_move_delay = 0.5  # Thời gian chờ trước khi AI đi (giây)
        self.valid_moves_cache = {}  # Cache cho các nước đi hợp lệ
        self.last_move_time = 0  # Thời gian của nước đi cuối cùng
        self.move_cooldown = 0.1  # Thời gian chờ giữa các nước đi
        self.drawn_moves = set()
        self.last_valid_moves = None  # Cache cho nước đi hợp lệ cuối cùng
        self.last_piece = None  # Cache cho quân cờ cuối cùng
        self.precomputed_moves = {}  # Cache cho các nước đi đã tính trước
        # self.pro()
        self._check_cache = {}  # Cache cho kiểm tra chiếu

    def set_hover(self, row, col):
        """
        Cập nhật ô cờ đang được hover
        """
        self.hovered_sqr = (row, col)

    def show_bg(self, surface):
        king_pos = None
        if self.is_check(self.next_player):
            # Tìm vị trí vua
            for row in range(ROWS):
                for col in range(COLS):
                    piece = self.board.squares[row][col].piece
                    if piece and isinstance(piece, King) and piece.color == self.next_player:
                        king_pos = (row, col)
                        break
                if king_pos:
                    break
        for row in range(ROWS):
            for col in range(COLS):
                if king_pos and (row, col) == king_pos:
                    color = (255, 0, 0)  # đỏ
                elif (row + col) % 2 == 0:
                    color = (234, 235, 200)
                else:
                    color = (119, 154, 88)
                rect = (col * SQSIZE, row * SQSIZE, SQSIZE, SQSIZE)
                pygame.draw.rect(surface, color, rect)

        letters = 'abcdefgh'
        font = pygame.font.SysFont("Arial", 18, bold=True)
        for row in range(ROWS):
            label = font.render(str(ROWS - row), True, (234, 235, 200)) if row%2 == 1 else font.render(str(ROWS - row), True, (119, 154, 88))
            x = 5 
            y = row * SQSIZE + 5
            surface.blit(label, (x, y))

        for col in range(COLS):
            label = font.render(letters[col], True, (119, 154, 88)) if col%2 == 1 else font.render(letters[col], True, (234, 235, 200))
            x = col * SQSIZE + SQSIZE // 2 + 28
            y = ROWS * SQSIZE - 22
            surface.blit(label, (x, y))

    def check_promotion(self):
        self.promotion_col = False
        self.promotion_color = False

        for col in range(COLS):
            if self.board.squares[0][col].has_piece():
                piece = self.board.squares[0][col].piece
                if isinstance(piece, Pawn):
                    self.promotion_col = col
                    self.promotion_color = "white"
            if self.board.squares[7][col].has_piece():
                piece = self.board.squares[7][col].piece
                if isinstance(piece, Pawn):
                    self.promotion_col = col
                    self.promotion_color = "black"

    def show_choose_promotion(self, surface):
        # Chỉ vẽ 4 ô chọn quân ở hàng cuối (hoặc đầu) của cột phong quân
        if self.promotion_col is False or self.promotion_color is False:
            return
        col = self.promotion_col
        if self.promotion_color == "white":
            rows = [0, 1, 2, 3]
            pieces = [Queen("white"), Rook("white"), Bishop("white"), Knight("white")]
        else:
            rows = [7, 6, 5, 4]
            pieces = [Queen("black"), Rook("black"), Bishop("black"), Knight("black")]
        for i, row in enumerate(rows):
            color = (255, 255, 255)
            rect = (col * SQSIZE, row * SQSIZE, SQSIZE, SQSIZE)
            pygame.draw.rect(surface, color, rect)
            # Vẽ hình quân cờ lên ô chọn
            piece = pieces[i]
            piece.set_texture(size=70)
            img = pygame.image.load(piece.texture)
            img_center = col * SQSIZE + SQSIZE // 2, row * SQSIZE + SQSIZE // 2
            piece.texture_rect = img.get_rect(center=img_center)
            surface.blit(img, piece.texture_rect)

    def check_row_promotion(self, a):
        if self.promotion_color == "white":
            return a < 4
        elif self.promotion_color == "black":
            return a >= 4
    
    # tạo quân phong cấp
    # def pro(self):
    #     for col in range(COLS):
    #         self.board.squares[0][col].promotion_piece = Queen("white")
    #         self.board.squares[1][col].promotion_piece = Rook("white")
    #         self.board.squares[2][col].promotion_piece = Knight("white")
    #         self.board.squares[3][col].promotion_piece = Bishop("white")

    #     for col in range(COLS):
    #         self.board.squares[7][col].promotion_piece = Queen("black")
    #         self.board.squares[6][col].promotion_piece = Rook("black")
    #         self.board.squares[5][col].promotion_piece = Knight("black")
    #         self.board.squares[4][col].promotion_piece = Bishop("black")

    def show_pieces(self, surface): #Update
        for row in range(ROWS):
            for col in range(COLS):
                square = self.board.squares[row][col]

                # Lấy quân cờ thực tế (ưu tiên promotion nếu có)
                piece = square.get_piece()

                # Bỏ qua nếu không có quân hoặc đang kéo quân đó
                if not piece or piece is self.dragger.piece:
                    continue

                # Nếu đang ở giai đoạn chọn quân phong cấp, chỉ hiển thị các ô chọn
                if self.promotion_col is not False and col == self.promotion_col and self.check_row_promotion(row):
                    piece = square.promotion_piece
                    if not piece:
                        continue

                piece.set_texture(size=70)
                img = pygame.image.load(piece.texture)
                img_center = col * SQSIZE + SQSIZE // 2, row * SQSIZE + SQSIZE // 2
                piece.texture_rect = img.get_rect(center=img_center)
                surface.blit(img, piece.texture_rect)
                        

    def get_valid_moves(self, piece, row, col):
        """
        Lấy các nước đi hợp lệ cho một quân cờ, chỉ trả về các nước đi mà sau khi đi xong vua không bị chiếu
        """
        cache_key = (piece, row, col, self.board.get_board_state())
        if cache_key in self.valid_moves_cache:
            return self.valid_moves_cache[cache_key]

        self.board.calc_moves(piece, row, col, bool=True)
        moves = piece.moves
        color = piece.color
        valid_moves = []
        for move in moves:
            # Thử đi nước cờ
            initial_piece = self.board.squares[move.initial.row][move.initial.col].piece
            final_piece = self.board.squares[move.final.row][move.final.col].piece
            self.board.squares[move.final.row][move.final.col].piece = initial_piece
            self.board.squares[move.initial.row][move.initial.col].piece = None
            still_in_check = self.is_check(color)
            self.board.squares[move.initial.row][move.initial.col].piece = initial_piece
            self.board.squares[move.final.row][move.final.col].piece = final_piece
            if not still_in_check:
                valid_moves.append(move)
        moves = valid_moves
        self.valid_moves_cache[cache_key] = moves
        self.last_valid_moves = moves
        self.last_piece = piece
        return moves

    def precompute_moves(self, piece, row, col):
        """
        Tính toán trước các nước đi hợp lệ cho một quân cờ
        """
        cache_key = (piece, row, col, self.board.get_board_state())
        if cache_key in self.precomputed_moves:
            return self.precomputed_moves[cache_key]

        moves = self.get_valid_moves(piece, row, col)
        self.precomputed_moves[cache_key] = moves
        return moves

    def show_moves(self, surface):
        if self.dragger.dragging:
            piece = self.dragger.piece
            self.drawn_moves.clear()
            
            # Chỉ hiển thị nước đi khi kéo từ vị trí ban đầu của quân cờ
            initial_row = self.dragger.initial_row
            initial_col = self.dragger.initial_col
            
            # Sử dụng các nước đi đã tính trước
            moves = self.precompute_moves(piece, initial_row, initial_col)

            # Hiển thị các nước đi hợp lệ
            for move in moves:
                if (move.final.row, move.final.col) in self.drawn_moves:
                    continue
                    
                # Kiểm tra xem ô đích có quân cờ không
                target_square = self.board.squares[move.final.row][move.final.col]
                if not target_square.isempty():
                    # Nếu có quân cờ đối phương
                    if target_square.has_enemy_piece(piece.color):
                        img = pygame.image.load('assets/images/circle.png').convert_alpha()
                        img_center = move.final.col * SQSIZE + SQSIZE // 2, move.final.row * SQSIZE + SQSIZE // 2
                        piece.texture_rect = img.get_rect(center = img_center)
                        surface.blit(img, piece.texture_rect)
                else:
                    # Nếu ô đích trống
                    light_gray = (100, 100, 120, 80)
                    center_x = move.final.col * SQSIZE + SQSIZE // 2
                    center_y = move.final.row * SQSIZE + SQSIZE // 2
                    radius = SQSIZE // 6
                    pygame.gfxdraw.filled_circle(surface, center_x, center_y, radius, light_gray)
                    pygame.gfxdraw.aacircle(surface, center_x, center_y, radius, light_gray)
                    self.drawn_moves.add((move.final.row, move.final.col))

    # chinh
    def reset_moves(self):
        self.drawn_moves.clear()

    def show_last_move(self, surface):
        if self.board.last_move:
            initial = self.board.last_move.initial
            final = self.board.last_move.final

            for pos in [initial, final]:
                color = (244, 247, 116) if (pos.row + pos.col) % 2 == 0 else (172, 195, 51)
                rect = (pos.col * SQSIZE, pos.row * SQSIZE, SQSIZE, SQSIZE)
                pygame.draw.rect(surface, color, rect)

    def next_turn(self):
        if self.game_over:
            return

        self.next_player = 'white' if self.next_player == 'black' else 'black'
        
        # Kiểm tra chiếu sau khi người chơi đi
        if self.next_player == self.ai_color:
            if self.is_checkmate('white'):
                self.game_over = True
                print("Black wins! Checkmate!")
            elif self.is_stalemate('white'):
                self.game_over = True
                print("Game over! Stalemate!")
            else:
                self.make_ai_move()

    def make_ai_move(self):
        """
        Thực hiện nước đi của AI
        """
        if self.game_over:
            return

        print('AI is thinking...')  # Log để kiểm tra AI được gọi
        current_time = time.time()
        if current_time - self.last_move_time < self.move_cooldown:
            return

        # Thêm độ trễ trước khi AI đi
        time.sleep(self.ai_move_delay)

        move = find_best_move(self.board, self.ai_color, depth=3)
        if move:
            print(f'AI move: {move}')  # Log nước đi của AI
            piece = self.board.squares[move.initial.row][move.initial.col].piece
            self.move(piece, move)
            self.last_move_time = time.time()

    def is_check(self, color):
        """
        Kiểm tra xem vua của một bên có đang bị chiếu không
        """
        # Kiểm tra cache
        cache_key = (color, self.board.get_board_state())
        if cache_key in self._check_cache:
            return self._check_cache[cache_key]

        # Tìm vị trí vua
        king_pos = None
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board.squares[row][col].piece
                if piece and isinstance(piece, King) and piece.color == color:
                    king_pos = (row, col)
                    break
            if king_pos:
                break

        if not king_pos:
            return False

        # Kiểm tra xem có quân cờ nào của đối phương có thể ăn vua không
        opponent_color = 'black' if color == 'white' else 'white'
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board.squares[row][col].piece
                if piece and piece.color == opponent_color:
                    moves = self.board.calc_moves(piece, row, col)
                    for move in moves:
                        if move.final.row == king_pos[0] and move.final.col == king_pos[1]:
                            self._check_cache[cache_key] = True
                            return True

        self._check_cache[cache_key] = False
        return False

    def is_checkmate(self, color):
        """
        Kiểm tra xem một bên có bị chiếu hết không
        """
        if not self.is_check(color):
            return False

        # Kiểm tra xem có nước đi nào để thoát chiếu không
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board.squares[row][col].piece
                if piece and piece.color == color:
                    moves = self.board.calc_moves(piece, row, col)
                    for move in moves:
                        # Thử đi nước cờ
                        initial_piece = self.board.squares[move.initial.row][move.initial.col].piece
                        final_piece = self.board.squares[move.final.row][move.final.col].piece
                        
                        # Thực hiện nước đi
                        self.board.squares[move.final.row][move.final.col].piece = initial_piece
                        self.board.squares[move.initial.row][move.initial.col].piece = None
                        
                        # Kiểm tra xem còn bị chiếu không
                        still_in_check = self.is_check(color)
                        
                        # Hoàn tác nước đi
                        self.board.squares[move.initial.row][move.initial.col].piece = initial_piece
                        self.board.squares[move.final.row][move.final.col].piece = final_piece
                        
                        if not still_in_check:
                            return False
        return True

    def is_stalemate(self, color):
        """
        Kiểm tra xem có bị hòa cờ không
        """
        if self.is_check(color):
            return False

        # Kiểm tra xem có nước đi hợp lệ nào không
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board.squares[row][col].piece
                if piece and piece.color == color:
                    moves = self.board.calc_moves(piece, row, col)
                    if moves:
                        return False
        return True

    def play_sound(self, captured=False):
        if captured:
            self.config.capture_sound.play()
        else:
            self.config.move_sound.play()

    def get_all_legal_moves(self, color):
        legal_moves = []
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board.squares[row][col].piece
                if piece and piece.color == color:
                    self.board.calc_moves(piece, row, col, bool=True)
                    for move in piece.moves:
                        # Thử đi nước cờ
                        initial_piece = self.board.squares[move.initial.row][move.initial.col].piece
                        final_piece = self.board.squares[move.final.row][move.final.col].piece
                        self.board.squares[move.final.row][move.final.col].piece = initial_piece
                        self.board.squares[move.initial.row][move.initial.col].piece = None
                        still_in_check = self.is_check(color)
                        self.board.squares[move.initial.row][move.initial.col].piece = initial_piece
                        self.board.squares[move.final.row][move.final.col].piece = final_piece
                        if not still_in_check:
                            legal_moves.append((piece, move))
        return legal_moves

    def move(self, piece, move):
        """
        Thực hiện nước đi và kiểm tra các điều kiện sau khi đi
        """
        # Chỉ cho phép đi nước hợp lệ
        legal_moves = self.get_all_legal_moves(piece.color)
        if not any(m == move for p, m in legal_moves):
            print("Nuoc di khong hop le!")
            return

        # Thực hiện nước đi
        self.board.move(piece, move)
        self.board.set_true_en_passant(piece)

        # Phát âm thanh
        self.play_sound(self.board.squares[move.final.row][move.final.col].has_piece())

        # Xóa cache
        self.clear_moves_cache()
        self.precomputed_moves.clear()

        # ===============================
        # 🟡 Xử lý phong cấp nếu là tốt
        # ===============================
        if isinstance(piece, Pawn) and (move.final.row == 0 or move.final.row == 7):
            self.show_choose_promotion(self.screen)
            pygame.display.update()

            # Vị trí phong cấp
            col = move.final.col
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_x, mouse_y = event.pos
                        clicked_col = mouse_x // SQSIZE
                        clicked_row = mouse_y // SQSIZE

                        # Chỉ xử lý nếu click đúng cột đang phong cấp
                        if clicked_col == col:
                            selected_index = clicked_row if piece.color == 'white' else 7 - clicked_row
                            if 0 <= selected_index <= 3:
                                promotion_choices = [Queen, Rook, Bishop, Knight]
                                new_piece_class = promotion_choices[selected_index]
                                new_piece = new_piece_class(piece.color)

                                square = self.board.squares[move.final.row][move.final.col]
                                square.piece = None
                                square.promotion_piece = new_piece
                                waiting = False

        # ===============================
        # Chuyển lượt / Kiểm tra kết thúc game
        # ===============================
        next_color = 'white' if piece.color == 'black' else 'black'
        legal_moves_next = self.get_all_legal_moves(next_color)
        if not legal_moves_next:
            if self.is_check(next_color):
                print(f"{piece.color.capitalize()} thắng! {next_color.capitalize()} bị chiếu hết!")
                self.game_over = True
            else:
                print("Hòa! Không còn nước đi hợp lệ.")
                self.game_over = True

    def clear_moves_cache(self):
        """
        Xóa cache các nước đi khi bàn cờ thay đổi
        """
        self.valid_moves_cache.clear()
        self.last_valid_moves = None
        self.last_piece = None
        self.precomputed_moves.clear()
