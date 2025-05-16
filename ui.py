import pygame
import sys
from const import *

class UI:
    def __init__(self):
        pass
        
    def show_start(self, screen):
        # Tải ảnh nền nếu có
        try:
            background = pygame.image.load('assets/images/background.png')
            background = pygame.transform.scale(background, (WIDTH + 300, HEIGHT))
        except:
            background = None  # Nếu không có ảnh thì dùng nền đen

        button_font = pygame.font.SysFont("roboto", 40, bold=True)

        play_button_rect = pygame.Rect(WIDTH - 80, HEIGHT//2, 300, 60)

        while True:
            if background:
                screen.blit(background, (0, 0))
            else:
                screen.fill((0, 0, 0))

            # Nút "Start game"
            pygame.draw.rect(screen, (139, 174, 108), play_button_rect, border_radius=10)
            text_surf = button_font.render("Start game", True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=play_button_rect.center)
            screen.blit(text_surf, text_rect)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if play_button_rect.collidepoint(event.pos):
                        return True
    def show_start_menu(self, screen):
        # Tải ảnh nền nếu có
        try:
            background = pygame.image.load('assets/images/background.png')
            background = pygame.transform.scale(background, (WIDTH + 300, HEIGHT))
        except:
            background = None  # Nếu không có ảnh thì dùng nền đen

        play_button_font = pygame.font.SysFont("roboto", 30)

        playFriend_button_rect = pygame.Rect(WIDTH - 80, HEIGHT//2 - 50, 300, 60)
        playAi_button_rect = pygame.Rect(WIDTH - 80, HEIGHT//2 + 30, 300, 60)

        # Dropdown cho độ khó AI
        dropdown_rects = [
            pygame.Rect(WIDTH - 80, HEIGHT//2 + 100 + i*50, 300, 45) for i in range(3)
        ]
        dropdown_labels = ["Easy", "Medium", "Hard"]

        show_ai_dropdown = False

        while True:
            if background:
                screen.blit(background, (0, 0))
            else:
                screen.fill((0, 0, 0))

            # Nút "Play with friend"
            pygame.draw.rect(screen, (222, 184, 135), playFriend_button_rect, border_radius=10)
            text_surf = play_button_font.render("Play with friend", True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=playFriend_button_rect.center)
            screen.blit(text_surf, text_rect)

            # Nút "Play with bot"
            pygame.draw.rect(screen, (222, 184, 135), playAi_button_rect, border_radius=10)
            text_surf = play_button_font.render("Play with bot", True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=playAi_button_rect.center)
            screen.blit(text_surf, text_rect)

            # Vẽ dropdown nếu đang bật
            if show_ai_dropdown:
                for i, rect in enumerate(dropdown_rects):
                    pygame.draw.rect(screen, (100, 100, 200), rect, border_radius=8)
                    label = play_button_font.render(dropdown_labels[i], True, (255, 255, 255))
                    label_rect = label.get_rect(center=rect.center)
                    screen.blit(label, label_rect)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if playFriend_button_rect.collidepoint(event.pos):
                        return "friend"
                    elif playAi_button_rect.collidepoint(event.pos):
                        # Toggle dropdown hiện/ẩn
                        show_ai_dropdown = not show_ai_dropdown
                    elif show_ai_dropdown:
                        for i, rect in enumerate(dropdown_rects):
                            if rect.collidepoint(event.pos):
                                # Trả về độ khó tương ứng
                                return f"bot_{['easy','medium','hard'][i]}"
    def show_game_result(self, screen, result_text):
        # Màu và font
        popup_bg = (255, 255, 255)
        button_color = (139, 195, 74)
        black = (0, 0, 0)

        font = pygame.font.SysFont("arial", 30)
        button_font = pygame.font.SysFont("arial", 22)

        # Kích thước popup
        popup_width = 350
        popup_height = 150
        popup_x = (WIDTH - popup_width) // 2
        popup_y = (HEIGHT - popup_height) // 2
        popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)

        # Vẽ viền đen (border)
        border_thickness = 2
        border_rect = pygame.Rect(
            popup_x - border_thickness,
            popup_y - border_thickness,
            popup_width + 2 * border_thickness,
            popup_height + 2 * border_thickness
        )
        pygame.draw.rect(screen, (0, 0, 0), border_rect, border_radius=10)  # Viền đen

        # Kích thước nút "Chơi lại"
        button_width = 200
        button_height = 40
        button_x = (WIDTH - button_width) // 2
        button_y = popup_y + popup_height - button_height - 20  # cách mép dưới popup 20px
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)


        # Vẽ nền popup
        pygame.draw.rect(screen, popup_bg, popup_rect, border_radius=10)

        # Vẽ dòng thông báo kết quả
        text_surf = font.render(result_text, True, black)
        text_rect = text_surf.get_rect(center=(popup_rect.centerx, popup_rect.top + 40))
        screen.blit(text_surf, text_rect)

        # Vẽ nút “Chơi lại”
        pygame.draw.rect(screen, button_color, button_rect, border_radius=10)
        btn_text = button_font.render("Play Again", True, black)
        btn_text_rect = btn_text.get_rect(center=button_rect.center)
        screen.blit(btn_text, btn_text_rect)

        pygame.display.update()

        # Đợi người dùng click
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if button_rect.collidepoint(event.pos):
                        return True

