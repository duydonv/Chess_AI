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
        self.AI_DELAY = 0.5  # Delay 
        # Bat AI
        self.game.ai_enabled = True
        self.game.ai_color = 'black'

    def mainloop(self):
        screen = self.screen
        game = self.game
        board = game.board
        dragger = game.dragger

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
                # Trả lượt lại cho người chơi
                game.next_player = 'white'

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEMOTION:
                    motion_row = event.pos[1] // SQSIZE
                    motion_col = event.pos[0] // SQSIZE
                    game.set_hover(motion_row, motion_col)
                    if dragger.dragging:
                        dragger.update_mouse(event.pos)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if not dragger.dragging and game.next_player == 'white':
                        dragger.update_mouse(event.pos)
                        clicked_row = dragger.mouseY // SQSIZE
                        clicked_col = dragger.mouseX // SQSIZE
                        if board.squares[clicked_row][clicked_col].has_team_piece(game.next_player):
                            piece = board.squares[clicked_row][clicked_col].piece
                            dragger.save_initial(event.pos)
                            dragger.drag_piece(piece)

                elif event.type == pygame.MOUSEBUTTONUP:
                    if dragger.dragging and game.next_player == 'white':
                        dragger.update_mouse(event.pos)
                        released_row = dragger.mouseY // SQSIZE
                        released_col = dragger.mouseX // SQSIZE
                        # Tạo move
                        initial = Square(dragger.initial_row, dragger.initial_col)
                        final = Square(released_row, released_col)
                        move = Move(initial, final)
                        # Kiểm tra nước đi hợp lệ
                        if board.valid_move(dragger.piece, move):
                            # Thực hiện nước đi
                            game.move(dragger.piece, move)
                            self.last_move_time = current_time
                            # Vẽ lại giao diện ngay lập tức
                            game.show_bg(screen)
                            game.show_last_move(screen)
                            game.show_pieces(screen)
                            pygame.display.update()
                            pygame.event.pump()
                            # Chuyển lượt cho AI
                            game.next_player = 'black'
                            if game.next_player == game.ai_color and game.ai_enabled:
                                self.waiting_for_ai = True
                        dragger.undrag_piece()

            # Hiển thị
            game.show_bg(screen)
            game.show_last_move(screen)
            game.show_moves(screen)
            game.show_pieces(screen)
            if dragger.dragging and dragger.piece is not None:
                dragger.update_blit(screen)
            pygame.display.update()

main = Main()
main.mainloop()