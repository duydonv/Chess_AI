import pygame
import sys
import time

from const import *
from game import Game
from square import Square
from move import Move
from settings import Settings
from ui import UI

class Main:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH + 300, HEIGHT))
        pygame.display.set_caption('Chess')
        self.game = Game()
        self.game.screen = self.screen
        self.clock = pygame.time.Clock()
        self.waiting_for_ai = False
        self.last_move_time = 0
        self.AI_DELAY = 0.5  # Delay 
        # Hiện menu
        self.ui = UI()
        choose = self.ui.show_start(self.screen)
        if (choose):

            mode = self.ui.show_start_menu(self.screen)

            # Xử lý theo lựa chọn
            if mode == "bot_easy":
                self.game.ai_enabled = True
                self.game.ai_color = 'black'
                self.game.ai_depth = 2
            elif mode == "bot_medium":
                self.game.ai_enabled = True
                self.game.ai_color = 'black'
                self.game.ai_depth = 3
            elif mode == "bot_hard":
                self.game.ai_enabled = True
                self.game.ai_color = 'black'
                self.game.ai_depth = 4
            elif mode == "friend":
                self.game.ai_enabled = False
            else:
                pygame.quit()
                sys.exit()
        # Thêm settings
        self.settings = Settings()
        self.game.settings = self.settings
        self.should_restart = False
        # Lưu chế độ chơi hiện tại
        self.current_mode = mode

    def reset_game(self):
        # Lưu lại chế độ chơi hiện tại
        current_ai_enabled = self.game.ai_enabled
        current_ai_color = self.game.ai_color
        current_ai_depth = self.game.ai_depth
        
        self.game = Game()
        self.game.screen = self.screen
        # Khôi phục chế độ chơi
        self.game.ai_enabled = current_ai_enabled
        self.game.ai_color = current_ai_color
        self.game.ai_depth = current_ai_depth
        
        self.settings = Settings()
        self.game.settings = self.settings
        self.waiting_for_ai = False
        self.last_move_time = 0
        self.should_restart = False

    def update_display(self):
        self.game.show_bg(self.screen)
        self.game.show_last_move(self.screen)
        self.game.show_moves(self.screen)
        self.game.show_pieces(self.screen)
        self.game.show_move_history(self.screen)
        self.settings.draw(self.screen)
        if self.game.dragger.dragging and self.game.dragger.piece is not None:
            self.game.dragger.update_blit(self.screen)
        pygame.display.update()
        pygame.event.pump()

    def mainloop(self):
        screen = self.screen
        game = self.game
        board = game.board
        dragger = game.dragger

        drag_scroll = False
        scroll_drag_offset = 0
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
                self.update_display()
                result = game.check_game_over()
                if result:
                    gameOver = self.ui.show_game_result(screen, result)
                    if gameOver:
                        self.reset_game()
                        # Cập nhật lại các biến tham chiếu trong mainloop
                        game = self.game
                        board = game.board
                        dragger = game.dragger
                        # Vẽ lại màn hình với game mới
                        game.show_bg(screen)
                        game.show_pieces(screen)
                        pygame.display.update()
                        continue

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
                    # Nếu đang kéo thanh scroll log
                    if drag_scroll:
                        mouse_x, mouse_y = event.pos
                        bar_x = WIDTH + 285
                        bar_y = 30
                        max_lines = 18
                        bar_height = max_lines * 34
                        total_logs = len(game.move_history)
                        scroll_range = max(1, total_logs - max_lines)
                        thumb_height = max(30, min(bar_height, int(bar_height * max_lines / total_logs)))
                        rel_y = mouse_y - bar_y - scroll_drag_offset
                        rel_y = max(0, min(rel_y, bar_height - thumb_height))
                        if bar_height - thumb_height > 0:
                            percent = rel_y / (bar_height - thumb_height)
                        else:
                            percent = 0
                        # Kéo xuống: percent tăng, move_log_scroll giảm (log mới hơn)
                        game.move_log_scroll = int((1 - percent) * scroll_range)
                        if game.move_log_scroll < 0:
                            game.move_log_scroll = 0
                        if game.move_log_scroll > scroll_range:
                            game.move_log_scroll = scroll_range

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    result = self.settings.handle_click(event.pos)
                    if result == 'surrender_yes':
                        # Hiển thị kết quả surrender
                        winner = 'black' if game.next_player == 'white' else 'white'
                        result_text = f"{winner.capitalize()} Wins!"
                        self.ui.show_game_result(screen, result_text)
                        # Hiện menu mới
                        mode = self.ui.show_start_menu(self.screen)
                        # Cập nhật chế độ chơi mới
                        if mode == "bot_easy":
                            self.game.ai_enabled = True
                            self.game.ai_color = 'black'
                            self.game.ai_depth = 2
                        elif mode == "bot_medium":
                            self.game.ai_enabled = True
                            self.game.ai_color = 'black'
                            self.game.ai_depth = 3
                        elif mode == "bot_hard":
                            self.game.ai_enabled = True
                            self.game.ai_color = 'black'
                            self.game.ai_depth = 4
                        elif mode == "friend":
                            self.game.ai_enabled = False
                        else:
                            pygame.quit()
                            sys.exit()
                        self.current_mode = mode
                        self.reset_game()
                        # Cập nhật lại các biến tham chiếu trong mainloop
                        game = self.game
                        board = game.board
                        dragger = game.dragger
                        continue
                    if result == 'restart_game':
                        self.reset_game()
                        # Cập nhật lại các biến tham chiếu trong mainloop
                        game = self.game
                        board = game.board
                        dragger = game.dragger
                        continue
                    if result:
                        continue
                        
                    # Chỉ xử lý nếu click trong bàn cờ
                    if event.pos[0] < WIDTH:
                        if not dragger.dragging:
                            dragger.update_mouse(event.pos)
                            clicked_row = dragger.mouseY // SQSIZE
                            clicked_col = dragger.mouseX // SQSIZE
                            if board.squares[clicked_row][clicked_col].has_team_piece(game.next_player):
                                piece = board.squares[clicked_row][clicked_col].piece
                                dragger.save_initial(event.pos)
                                dragger.drag_piece(piece)
                    # Xử lý kéo thanh scroll log
                    else:
                        mouse_x, mouse_y = event.pos
                        bar_x = WIDTH + 285
                        bar_y = 30
                        bar_width = 10
                        bar_height = 20 * 34
                        total_logs = len(game.move_history)
                        max_lines = 20
                        scroll_range = max(1, total_logs - max_lines)
                        thumb_height = max(30, int(bar_height * max_lines / total_logs)) if total_logs > max_lines else bar_height
                        if (bar_x <= mouse_x <= bar_x + bar_width) and (bar_y <= mouse_y <= bar_y + bar_height):
                            # Tính toán vị trí thumb hiện tại
                            if scroll_range > 0:
                                thumb_y = bar_y + int((game.move_log_scroll / scroll_range) * (bar_height - thumb_height))
                            else:
                                thumb_y = bar_y
                            if thumb_y <= mouse_y <= thumb_y + thumb_height:
                                drag_scroll = True
                                scroll_drag_offset = mouse_y - thumb_y

                elif event.type == pygame.MOUSEBUTTONUP:
                    if dragger.dragging:
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
                            game.move(dragger.piece, move, self.settings.sound_enabled)
                            self.last_move_time = current_time
                            # Vẽ lại giao diện ngay lập tức
                            self.update_display()
                            # Chuyển lượt cho người chơi hoặc AI
                            #-------------------
                            if game.ai_enabled:
                                game.next_player = game.ai_color
                                self.waiting_for_ai = True
                            else:
                                game.next_player = 'black' if game.next_player == 'white' else 'white'
                            #------------------
                            result = game.check_game_over()
                            if result:
                                gameOver = self.ui.show_game_result(screen, result)
                                if gameOver:
                                    self.reset_game()
                                    # Cập nhật lại các biến tham chiếu trong mainloop
                                    game = self.game
                                    board = game.board
                                    dragger = game.dragger
                                    # Vẽ lại màn hình với game mới
                                    game.show_bg(screen)
                                    game.show_pieces(screen)
                                    pygame.display.update()
                                    continue
        
                        dragger.undrag_piece()
                    drag_scroll = False

                elif event.type == pygame.MOUSEWHEEL:
                    # Nếu chuột nằm trong vùng log (bên phải bàn cờ)
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    if mouse_x >= WIDTH:
                        max_lines = 18
                        total_logs = len(game.move_history)
                        max_scroll = max(0, total_logs - max_lines)
                        # Lăn xuống: log mới hơn, lăn lên: log cũ hơn
                        game.move_log_scroll -= event.y
                        if game.move_log_scroll < 0:
                            game.move_log_scroll = 0
                        if game.move_log_scroll > max_scroll:
                            game.move_log_scroll = max_scroll

            # Hiển thị
            self.update_display()

            if self.should_restart:
                break



main = Main()
main.mainloop()