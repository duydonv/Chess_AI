import pygame
import sys

from const import *
from game import Game
from square import Square
from move import Move

class Main:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode( (WIDTH, HEIGHT))
        pygame.display.set_caption('Chess')
        self.game = Game()

    def mainloop(self):
                
        screen = self.screen
        game = self.game
        board = self.game.board
        dragger = self.game.dragger
        
        while True:
            game.check_promotion()
            game.show_bg(screen)
            game.show_last_move(screen)
            if game.promotion_col:
                game.show_choose_promotion(screen)
            game.show_moves(screen)
            game.show_pieces(screen)

            if dragger.dragging:
                dragger.update_blit(screen)

            for event in pygame.event.get():
                # lắng nghe sự kiện click chuột
                if event.type == pygame.MOUSEBUTTONDOWN:
                    dragger.update_mouse(event.pos)

                    clicked_row = dragger.mouseY // SQSIZE
                    clicked_col = dragger.mouseX // SQSIZE
                    if game.promotion_col:
                        if clicked_col == game.promotion_col and game.check_row_promotion(clicked_row):
                            piece = board.squares[clicked_row][clicked_col].promotion_piece
                            if game.promotion_color == "white":
                                board.squares[0][clicked_col].piece = piece
                            elif game.promotion_color == "black":
                                board.squares[7][clicked_col].piece = piece

                            game.show_bg(screen)
                            game.show_last_move(screen)
                            game.show_moves(screen)
                            game.show_pieces(screen)
                    elif board.squares[clicked_row][clicked_col].has_piece():
                        # chinh
                        game.reset_moves()
                        piece = board.squares[clicked_row][clicked_col].piece
                        if piece.color == game.next_player:
                            board.calc_moves(piece, clicked_row, clicked_col, bool=True)
                            dragger.save_initial(event.pos)
                            dragger.drag_piece(piece)
                            # chỉnh mouse cursor khi dragging 
                            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)

                            game.show_bg(screen)
                            game.show_last_move(screen)
                            game.show_moves(screen)
                            game.show_pieces(screen)

                # lắng nghe sự kiện di chuyển chuột
                elif event.type == pygame.MOUSEMOTION:
                    if dragger.dragging:
                        dragger.update_mouse(event.pos)
                        game.show_bg(screen)
                        game.show_last_move(screen)
                        game.show_moves(screen)
                        game.show_pieces(screen)
                        dragger.update_blit(screen)

                # lắng nghe sự kiện nhả chuột
                elif event.type == pygame.MOUSEBUTTONUP:
                    if dragger.dragging:
                        dragger.update_mouse(event.pos)
                        released_row = dragger.mouseY // SQSIZE
                        released_col = dragger.mouseX // SQSIZE

                        initial = Square(dragger.initial_row, dragger.initial_col)
                        final = Square(released_row, released_col)
                        move = Move(initial, final)

                        if board.valid_move(dragger.piece, move):
                            captured = board.squares[released_row][released_col].has_piece()

                            board.move(dragger.piece, move)

                            board.set_true_en_passant(dragger.piece)
                            game.play_sound(captured)
                            game.show_bg(screen)
                            game.show_last_move(screen)
                            game.show_pieces(screen)

                            game.next_turn()

                    dragger.undrag_piece()
                        
                    # chỉnh mouse cursor sau khi dragging 
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

                # xử lí sự kiện thoát
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            pygame.display.update()

main = Main()
main.mainloop()