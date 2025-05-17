import pygame
import os
from pygame.locals import *

class MenuScreen:
    def __init__(self, screen, user_data):
        self.screen = screen
        self.user_data = user_data
        self.running = True
        self.width, self.height = screen.get_size()

        # Cores do slide
        self.bg_color = (30, 180, 195)  # #1EB4C3
        self.button_color = (251, 164, 31)  # #FBA41F
        self.text_color = (0, 0, 0)  # preto

        # Fonte
        try:
            font_path = os.path.join("assets", "fonts", "pixel_font.ttf")
            self.title_font = pygame.font.Font(font_path, 40)
            self.text_font = pygame.font.Font(font_path, 24)
        except:
            self.title_font = pygame.font.SysFont("Arial", 40, bold=True)
            self.text_font = pygame.font.SysFont("Arial", 24)

        # Carregar background
        try:
            bg_path = os.path.join("assets", "images", "background.png")
            self.background = pygame.image.load(bg_path).convert()
            self.background = pygame.transform.scale(self.background, (self.width, self.height))
        except:
            self.background = None

        # Botões (posição fixa como no código original)
        center_x = self.width // 2
        self.buttons = [
            {"label": "Gerenciar Usuário", "rect": pygame.Rect(250, 150, 300, 50), "action": "create_user"},
            {"label": "Gerenciar Turma", "rect": pygame.Rect(250, 220, 300, 50), "action": "create_class"},
            {"label": "Gerenciar Questão", "rect": pygame.Rect(250, 290, 300, 50), "action": "edit_questions"},
            {"label": "Visualizar Ranking", "rect": pygame.Rect(250, 360, 300, 50), "action": "show_ranking"},
            {"label": "JOGAR", "rect": pygame.Rect(250, 430, 300, 70), "action": "play_game"},
            {"label": "Sair", "rect": pygame.Rect(self.width - 110, 20, 90, 30), "action": "logout"}
        ]

    def draw_button(self, label, rect):
        pygame.draw.rect(self.screen, self.button_color, rect, border_radius=4)
        pygame.draw.rect(self.screen, (0, 0, 0), rect, 3, border_radius=4)  # borda preta
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

            # Desenhar fundo
            if self.background:
                self.screen.blit(self.background, (0, 0))
            else:
                self.screen.fill(self.bg_color)

            # Desenhar título e subtítulo
            title_surf = self.title_font.render("Menu Principal", True, (0, 0, 0))
            title_rect = title_surf.get_rect(center=(self.width // 2, 60))
            self.screen.blit(title_surf, title_rect)

            subtitle = f"Bem-Vindo {'PoliMestre' if self.user_data['user_type'] == 'teacher' else 'PoliGamer'}"
            subtitle_surf = self.text_font.render(subtitle, True, (0, 0, 0))
            subtitle_rect = subtitle_surf.get_rect(center=(self.width // 2, 100))
            self.screen.blit(subtitle_surf, subtitle_rect)

            # Desenhar botões
            for btn in self.buttons:
                self.draw_button(btn["label"], btn["rect"])

            pygame.display.flip()
            clock.tick(60)

        return {"action": "logout"}
