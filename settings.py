import pygame
import os
from const import WIDTH, HEIGHT

class Settings:
    def __init__(self):
        self.visible = False
        self.sound_enabled = True
        self.font = pygame.font.SysFont('Arial', 16)
        # Đặt nút nhỏ hơn nữa, sát góc phải trên cùng vùng log
        self.button_rect = pygame.Rect(WIDTH + 300 - 70, 10, 60, 24)
        # Panel settings cao hơn để chứa 3 nút
        self.settings_rect = pygame.Rect(WIDTH + 300 - 150, 40, 140, 120)
        # Nút Restart nằm trên cùng
        self.restart_button_rect = pygame.Rect(self.settings_rect.x + 10, self.settings_rect.y + 32, 120, 18)
        # Nút Sound nằm dưới Restart
        self.sound_button_rect = pygame.Rect(self.settings_rect.x + 10, self.restart_button_rect.y + self.restart_button_rect.height + 8, 120, 18)
        # Nút Surrender nằm dưới Sound
        self.surrender_button_rect = pygame.Rect(self.settings_rect.x + 10, self.sound_button_rect.y + self.sound_button_rect.height + 8, 120, 20)
        self.surrender_confirm = False
        self.surrender_box_rect = pygame.Rect(WIDTH//2 - 120, HEIGHT//2 - 60, 240, 120)
        self.surrender_yes_rect = pygame.Rect(WIDTH//2 - 80, HEIGHT//2 + 20, 60, 32)
        self.surrender_no_rect = pygame.Rect(WIDTH//2 + 20, HEIGHT//2 + 20, 60, 32)
        
    def draw(self, screen):
        # Vẽ nút Settings
        pygame.draw.rect(screen, (220, 220, 220), self.button_rect, border_radius=8)
        text = self.font.render('Menu', True, (30, 30, 30))
        text_rect = text.get_rect(center=self.button_rect.center)
        screen.blit(text, text_rect)
        
        # Vẽ panel settings nếu đang hiển thị
        if self.visible:
            pygame.draw.rect(screen, (250, 250, 250), self.settings_rect, border_radius=12)
            pygame.draw.rect(screen, (100, 100, 100), self.settings_rect, 2, border_radius=12)
            
            # Vẽ tiêu đề
            title = self.font.render('Menu', True, (30, 30, 30))
            title_rect = title.get_rect(center=(self.settings_rect.centerx, self.settings_rect.y + 14))
            screen.blit(title, title_rect)
            
            # Vẽ nút Restart trong menu
            pygame.draw.rect(screen, (180, 220, 240), self.restart_button_rect, border_radius=8)
            restart_text = self.font.render('Restart', True, (0, 80, 120))
            restart_text_rect = restart_text.get_rect(center=self.restart_button_rect.center)
            screen.blit(restart_text, restart_text_rect)
            # Vẽ nút Sound
            pygame.draw.rect(screen, (200, 220, 200), self.sound_button_rect, border_radius=8)
            sound_text = f"Sound: {'ON' if self.sound_enabled else 'OFF'}"
            text = self.font.render(sound_text, True, (0, 80, 0) if self.sound_enabled else (120, 0, 0))
            text_rect = text.get_rect(center=self.sound_button_rect.center)
            screen.blit(text, text_rect)
            # Vẽ nút Surrender
            pygame.draw.rect(screen, (240, 180, 180), self.surrender_button_rect, border_radius=8)
            surrender_text = self.font.render('Surrender', True, (120, 0, 0))
            surrender_text_rect = surrender_text.get_rect(center=self.surrender_button_rect.center)
            screen.blit(surrender_text, surrender_text_rect)
            
            # Vẽ hộp xác nhận surrender nếu cần
            if self.surrender_confirm:
                pygame.draw.rect(screen, (255, 255, 255), self.surrender_box_rect, border_radius=12)
                pygame.draw.rect(screen, (100, 100, 100), self.surrender_box_rect, 2, border_radius=12)
                confirm_text = self.font.render('Do you want to surrender?', True, (30, 30, 30))
                confirm_rect = confirm_text.get_rect(center=(self.surrender_box_rect.centerx, self.surrender_box_rect.y + 35))
                screen.blit(confirm_text, confirm_rect)
                # Nút Yes
                pygame.draw.rect(screen, (200, 220, 200), self.surrender_yes_rect, border_radius=8)
                yes_text = self.font.render('Yes', True, (0, 80, 0))
                yes_rect = yes_text.get_rect(center=self.surrender_yes_rect.center)
                screen.blit(yes_text, yes_rect)
                # Nút No
                pygame.draw.rect(screen, (220, 200, 200), self.surrender_no_rect, border_radius=8)
                no_text = self.font.render('No', True, (120, 0, 0))
                no_rect = no_text.get_rect(center=self.surrender_no_rect.center)
                screen.blit(no_text, no_rect)
    
    def handle_click(self, pos):
        # Kiểm tra xác nhận surrender trước
        if self.surrender_confirm:
            if self.surrender_yes_rect.collidepoint(pos):
                return 'surrender_yes'
            if self.surrender_no_rect.collidepoint(pos):
                self.surrender_confirm = False
                return True
            return False
        # Kiểm tra click vào nút Settings
        if self.button_rect.collidepoint(pos):
            self.visible = not self.visible
            return True
        # Kiểm tra click vào các nút trong panel settings
        if self.visible:
            if self.restart_button_rect.collidepoint(pos):
                return 'restart_game'
            if self.sound_button_rect.collidepoint(pos):
                self.sound_enabled = not self.sound_enabled
                return True
            if self.surrender_button_rect.collidepoint(pos):
                self.surrender_confirm = True
                return True
        return False 