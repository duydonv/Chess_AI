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
        self.screen = pygame.display.set_mode((WIDTH + 300, HEIGHT))
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
    def show_start_menu(self):
        # Tải ảnh nền nếu có
        try:
            background = pygame.image.load('assets/images/background.png')
            background = pygame.transform.scale(background, (WIDTH + 300, HEIGHT))
        except:
            background = None  # Nếu không có ảnh thì dùng nền đen

        button_font = pygame.font.SysFont("roboto", 40, bold=True)
        play_button_font = pygame.font.SysFont("roboto", 30)

        play_button_rect = pygame.Rect(WIDTH - 80, HEIGHT//2 - 130, 300, 60)
        playFriend_button_rect = pygame.Rect(WIDTH - 80, HEIGHT//2 - 50, 300, 60)
        playAi_button_rect = pygame.Rect(WIDTH - 80, HEIGHT//2 + 30, 300, 60)


        while True:
            if background:
                self.screen.blit(background, (0, 0))
            else:
                self.screen.fill((0,0,0))


            # Nút "Bắt đầu"
            pygame.draw.rect(self.screen, (139, 174, 108), play_button_rect, border_radius=10)
            text_surf = button_font.render("Start game", True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=play_button_rect.center)
            self.screen.blit(text_surf, text_rect)

            pygame.display.flip()

            # Nút ""
            pygame.draw.rect(self.screen, (222, 184, 135), playFriend_button_rect, border_radius=10)
            text_surf = play_button_font.render("Play with friend", True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=playFriend_button_rect.center)
            self.screen.blit(text_surf, text_rect)

            # Nút ""
            pygame.draw.rect(self.screen, (222, 184, 135), playAi_button_rect, border_radius=10)
            text_surf = play_button_font.render("Play with bot", True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=playAi_button_rect.center)
            self.screen.blit(text_surf, text_rect)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if play_button_rect.collidepoint(event.pos):
                        return  # Bắt đầu game

    def mainloop(self):
        self.show_start_menu()
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
                    # Chỉ xử lý nếu click trong bàn cờ
                    if event.pos[0] < WIDTH:
                        if not dragger.dragging and game.next_player == 'white':
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
            game.show_bg(screen)
            game.show_last_move(screen)
            game.show_moves(screen)
            game.show_pieces(screen)
            game.show_move_history(screen)
            if dragger.dragging and dragger.piece is not None:
                dragger.update_blit(screen)
            pygame.display.update()

main = Main()
main.mainloop()