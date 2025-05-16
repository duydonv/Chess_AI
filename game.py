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
        self.move_history = []  # Lưu lịch sử nước đi
        self.move_log_scroll = 0  # Vị trí scroll log

    def set_hover(self, row, col):
        """
        Cập nhật ô cờ đang được hover
        """
        self.hovered_sqr = (row, col)

    def show_bg(self, surface):
        king_pos = None
        if self.board._is_king_in_check(self.next_player):
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
            still_in_check = self.board._is_king_in_check(color)
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
            if self.board.is_checkmate('white'):
                self.game_over = True
                print("Black wins! Checkmate!")
            elif self.board.is_stalemate('white'):
                self.game_over = True
                print("Game over! Stalemate!")
            else:
                self.make_ai_move()

    def check_game_over(self):
        color = self.next_player  # Người sắp chơi tiếp

        if self.board.is_checkmate(color):
            self.game_over = True
            winner = 'Black' if color == 'white' else 'White'
            return f"{winner} wins! Checkmate!"

        elif self.board.is_stalemate(color):
            self.game_over = True
            return "Game over! Stalemate!"

        return None



    def make_ai_move(self):
        """
        Thực hiện nước đi của AI
        """
        if self.game_over:
            return

        # Lấy nước đi tốt nhất từ AI
        best_move = find_best_move(self.board, self.ai_color)
        if best_move:
            # Tìm quân cờ ở vị trí initial
            piece = self.board.squares[best_move.initial.row][best_move.initial.col].piece
            if piece:
                # Thực hiện nước đi
                self.move(piece, best_move)
                # Chuyển lượt cho người chơi
                self.next_player = 'white'

    def play_sound(self, captured=False):
        # Giả sử self.settings là đối tượng Settings
        if hasattr(self, 'settings') and not self.settings.sound_enabled:
            return
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
                        still_in_check = self.board._is_king_in_check(color)
                        self.board.squares[move.initial.row][move.initial.col].piece = initial_piece
                        self.board.squares[move.final.row][move.final.col].piece = final_piece
                        if not still_in_check:
                            legal_moves.append((piece, move))
        return legal_moves

    def move(self, piece, move):
        """
        Thực hiện nước đi và kiểm tra các điều kiện sau khi đi
        """
        # 1. Kiểm tra nước đi hợp lệ
        if not self.board.valid_move(piece, move):
            print("Nuoc di khong hop le!")
            return False

        # 2. Lưu trạng thái trước khi đi
        captured_piece = self.board.squares[move.final.row][move.final.col].piece
        
        # 3. Thực hiện nước đi
        self.board.make_move(piece, move)
        self.board.set_true_en_passant(piece)

        # 4. Thêm số thứ tự nước đi vào log
        self._add_move_to_history(piece, move, captured_piece)

        # 5. Phát âm thanh
        self.play_sound(captured_piece is not None)

        # 6. Xóa cache
        self.clear_moves_cache()
        self.precomputed_moves.clear()

        # 7. Xử lý phong cấp nếu là tốt
        if isinstance(piece, Pawn) and (move.final.row == 0 or move.final.row == 7):
            self._handle_promotion(piece, move)

        # 8. Kiểm tra kết thúc game
        next_color = 'white' if piece.color == 'black' else 'black'
        if self.board.is_checkmate(next_color):
            print(f"{piece.color.capitalize()} thang! {next_color.capitalize()} bi chieu het!")
            self.game_over = True
        elif self.board.is_stalemate(next_color):
            print("Hoa! Khong con nuoc di hop le.")
            self.game_over = True

        return True

    def _add_move_to_history(self, piece, move, captured_piece):
        """
        Thêm nước đi vào lịch sử
        """
        move_number = len(self.move_history) + 1
        piece_symbol = {
            'king': 'K',
            'queen': 'Q',
            'rook': 'R',
            'bishop': 'B',
            'knight': 'N',
            'pawn': 'P',
        }[piece.name]
        start_pos = f"{chr(move.initial.col + ord('a'))}{8 - move.initial.row}"
        end_pos = f"{chr(move.final.col + ord('a'))}{8 - move.final.row}"
        color_str = "White" if piece.color == "white" else "Black"
        # Nhập thành
        if piece.name == 'king' and abs(move.initial.col - move.final.col) == 2:
            if move.final.col > move.initial.col:
                move_str = "O-O"
            else:
                move_str = "O-O-O"
        # Phong tốt
        elif piece.name == 'pawn' and (move.final.row == 0 or move.final.row == 7):
            # Giả sử luôn phong hậu
            move_str = f"{end_pos}=Q"
            if move.initial.col != move.final.col:
                move_str = f"{chr(move.initial.col + ord('a'))}x{end_pos}=Q"
        # Ăn quân
        elif captured_piece is not None:
            captured_name = captured_piece.__class__.__name__
            if piece.name == 'pawn':
                move_str = f"{chr(move.initial.col + ord('a'))}x{end_pos} "
            else:
                move_str = f"{piece_symbol}x{end_pos}"
        # Nước đi thường
        else:
            move_str = f"{piece_symbol}{start_pos} -> {end_pos}"
        self.move_history.append(f"{move_number}. {color_str}: {move_str}")
        # Tự động cuộn log về đầu (log cũ nhất) mỗi khi có log mới
        max_lines = 18
        total_logs = len(self.move_history)
        max_scroll = max(0, total_logs - max_lines)
        self.move_log_scroll = max_scroll

    def _handle_promotion(self, piece, move):
        """
        Xử lý phong cấp tốt
        """
        self.show_choose_promotion(self.screen)
        # 1) Đánh dấu cột + màu để show menu
        self.promotion_col = move.final.col
        self.promotion_color = piece.color
        # 2) Hiển thị menu chọn
        self.show_choose_promotion(self.screen)
        pygame.display.update()

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

                    if clicked_col == col:
                        selected_index = clicked_row if piece.color == 'white' else 7 - clicked_row
                        if 0 <= selected_index <= 3:
                            promotion_choices = [Queen, Rook, Bishop, Knight]
                            new_piece_class = promotion_choices[selected_index]
                            new_piece = new_piece_class(piece.color)

                            square = self.board.squares[move.final.row][move.final.col]
                            square.piece = None
                            square.promotion_piece = new_piece
                            # Gán trực tiếp quân mới vào ô
                            square.piece = new_piece
                            square.promotion_piece = None
                            waiting = False
        self.promotion_col   = False
        self.promotion_color = False

    def clear_moves_cache(self):
        """
        Xóa cache các nước đi khi bàn cờ thay đổi
        """
        self.valid_moves_cache.clear()
        self.last_valid_moves = None
        self.last_piece = None
        self.precomputed_moves.clear()

    def show_move_history(self, surface):
        # Vẽ nền đen cho vùng log
        pygame.draw.rect(surface, (20, 20, 20), (SQSIZE * 8, 0, 300, HEIGHT))
        font = pygame.font.SysFont("Roboto", 22, bold=False)
        x = SQSIZE * 8 + 20  # Bên phải bàn cờ
        y = 30
        max_lines = 18
        total_logs = len(self.move_history)
        max_scroll = max(0, total_logs - max_lines)
        self.move_log_scroll = max(0, min(self.move_log_scroll, max_scroll))

        if total_logs <= max_lines:
            start = 0
            end = total_logs
        else:
            start = self.move_log_scroll
            end = min(start + max_lines, total_logs)
        logs_to_show = self.move_history[start:end]
        for i, log in enumerate(logs_to_show):
            # Tách số thứ tự, màu quân, nội dung nước đi để căn cột
            try:
                num, rest = log.split('.', 1)
                color, move = rest.strip().split(':', 1)
            except Exception:
                num, color, move = '', '', log
            label_num = font.render(num.strip(), True, (200, 200, 100))
            label_color = font.render(color.strip(), True, (100, 200, 255) if color.strip() == 'White' else (255, 180, 100))
            label_move = font.render(move.strip(), True, (255, 255, 255))
            surface.blit(label_num, (x, y + i * 34))
            surface.blit(label_color, (x + 40, y + i * 34))
            surface.blit(label_move, (x + 120, y + i * 34))
        # Vẽ thanh scroll nếu cần
        if total_logs > max_lines:
            bar_x = SQSIZE * 8 + 285
            bar_y = 30
            bar_width = 10
            bar_height = HEIGHT - 2 * bar_y
            pygame.draw.rect(surface, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height), border_radius=5)
            scroll_range = max(1, total_logs - max_lines)
            thumb_height = max(30, min(bar_height, int(bar_height * max_lines / total_logs)))
            if scroll_range > 0:
                percent = self.move_log_scroll / scroll_range
                thumb_y = bar_y + int(percent * (bar_height - thumb_height))
            else:
                thumb_y = bar_y
            pygame.draw.rect(surface, (180, 180, 180), (bar_x, thumb_y, bar_width, thumb_height), border_radius=5)
