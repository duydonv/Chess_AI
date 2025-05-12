import pygame
import sys
import time

from const import *
from game import Game
from square import Square
from move import Move

class Main:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Chess')
        self.game = Game()
        self.game.screen = self.screen
        self.clock = pygame.time.Clock()
        self.waiting_for_ai = False
        self.last_move_time = 0
        self.AI_DELAY = 0.5  # Delay in seconds before AI starts thinking
        self.selected_square = None  # (row, col) or None
        self.valid_moves = []  # List of Move objects
        # Đảm bảo AI được bật
        self.game.ai_enabled = True
        self.game.ai_color = 'black'

    def mainloop(self):
        screen = self.screen
        game = self.game
        board = game.board

        while True:
            self.clock.tick(FPS)
            current_time = time.time()

            # AI move
            if (self.waiting_for_ai and 
                game.next_player == game.ai_color and 
                game.ai_enabled and 
                (current_time - self.last_move_time) >= self.AI_DELAY):
                game.make_ai_move()
                self.waiting_for_ai = False
                # CHUYỂN LƯỢT LẠI CHO NGƯỜI CHƠI
                game.next_player = 'white'
                self.selected_square = None
                self.valid_moves = []

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if game.next_player == 'white':
                        mouse_x, mouse_y = event.pos
                        row = mouse_y // SQSIZE
                        col = mouse_x // SQSIZE
                        square = board.squares[row][col]
                        piece = square.piece
                        # Nếu chưa chọn quân hoặc chọn lại quân mình
                        if self.selected_square is None:
                            if piece and piece.color == 'white':
                                self.selected_square = (row, col)
                                self.valid_moves = game.get_valid_moves(piece, row, col)
                        else:
                            # Nếu click vào ô đích hợp lệ
                            move = None
                            for m in self.valid_moves:
                                if m.final.row == row and m.final.col == col:
                                    move = m
                                    break
                            if move:
                                # Thực hiện nước đi
                                game.move(board.squares[self.selected_square[0]][self.selected_square[1]].piece, move)
                                self.last_move_time = current_time
                                self.selected_square = None
                                self.valid_moves = []

                                # VẼ LẠI GIAO DIỆN NGAY LẬP TỨC
                                game.show_bg(screen)
                                game.show_last_move(screen)
                                game.show_pieces(screen)
                                pygame.display.update()
                                pygame.event.pump()

                                # CHUYỂN LƯỢT
                                game.next_player = 'black' if game.next_player == 'white' else 'white'

                                # Sau đó mới set flag cho AI
                                if game.next_player == game.ai_color and game.ai_enabled:
                                    self.waiting_for_ai = True
                            elif piece and piece.color == 'white':
                                # Đổi chọn quân khác
                                self.selected_square = (row, col)
                                self.valid_moves = game.get_valid_moves(piece, row, col)
                            else:
                                # Click linh tinh, bỏ chọn
                                self.selected_square = None
                                self.valid_moves = []

            # Hiển thị
            game.show_bg(screen)
            game.show_last_move(screen)
            # Hiển thị nước đi hợp lệ
            if self.selected_square and self.valid_moves:
                for move in self.valid_moves:
                    center_x = move.final.col * SQSIZE + SQSIZE // 2
                    center_y = move.final.row * SQSIZE + SQSIZE // 2
                    radius = SQSIZE // 6
                    pygame.draw.circle(screen, (100, 100, 120, 80), (center_x, center_y), radius)
            # Highlight ô đang chọn
            if self.selected_square:
                row, col = self.selected_square
                pygame.draw.rect(screen, (50, 150, 255), (col*SQSIZE, row*SQSIZE, SQSIZE, SQSIZE), 4)
            game.show_pieces(screen)
            pygame.display.update()

main = Main()
main.mainloop()