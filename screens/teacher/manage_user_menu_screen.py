import pygame
import os
from pygame.locals import *

class ManageUserMenuScreen:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.running = True

        # Cores
        self.bg_color = (30, 180, 195)
        self.button_color = (251, 164, 31)
        self.text_color = (0, 0, 0)

        # Fonte
        try:
            font_path = os.path.join("assets", "fonts", "pixel_font.ttf")
            self.title_font = pygame.font.Font(font_path, 36)
            self.text_font = pygame.font.Font(font_path, 24)
        except:
            self.title_font = pygame.font.SysFont("Arial", 36, bold=True)
            self.text_font = pygame.font.SysFont("Arial", 24)

        # Botões
        self.buttons = [
            {"label": "Adicionar Usuário", "rect": pygame.Rect(250, 180, 300, 50), "action": "add_user"},
            {"label": "Remover Usuário", "rect": pygame.Rect(250, 260, 300, 50), "action": "remove_user"},
            {"label": "Atualizar Usuário", "rect": pygame.Rect(250, 340, 300, 50), "action": "update_user"},
            {"label": "Voltar", "rect": pygame.Rect(250, 420, 300, 50), "action": "back_to_menu"}
        ]

    def draw_button(self, label, rect):
        pygame.draw.rect(self.screen, self.button_color, rect, border_radius=4)
        pygame.draw.rect(self.screen, (0, 0, 0), rect, 3, border_radius=4)
        text_surf = self.text_font.render(label, True, self.text_color)
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    return {"action": "logout"}
                if event.type == MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    for btn in self.buttons:
                        if btn["rect"].collidepoint(pos):
                            return {"action": btn["action"]}

            self.screen.fill(self.bg_color)

            title = self.title_font.render("Gerenciar Usuário", True, (0, 0, 0))
            self.screen.blit(title, title.get_rect(center=(self.width // 2, 100)))

            for btn in self.buttons:
                self.draw_button(btn["label"], btn["rect"])

            pygame.display.flip()
            clock.tick(60)
