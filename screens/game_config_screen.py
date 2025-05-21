# screens/game_config_screen.py
# -*- coding: utf-8 -*-

import pygame
import sys
from pygame.locals import *

DEFAULT_SUBJECTS = [
    "Matematica", "Fisica", "Biologia", "Quimica",
    "Historia", "Geografia", "Portugues"
]
DEFAULT_GRADE_LEVELS = ["1 Ano", "2 Ano", "3 Ano"]
DEFAULT_DIFFICULTIES = ["Facil", "Medio", "Dificil"]

try:
    import config
    COLORS = config.COLORS
    SUBJECTS = getattr(config, "SUBJECTS", DEFAULT_SUBJECTS)
    GRADE_LEVELS = getattr(config, "GRADE_LEVELS", DEFAULT_GRADE_LEVELS)
except ImportError:
    COLORS = {
        "background": (30, 180, 195),
        "light_shadow": (255, 255, 255),
        "dark_shadow": (20, 140, 150),
        "accent": (251, 164, 31),
        "text": (0, 0, 0),
        "black": (0, 0, 0)
    }
    SUBJECTS = DEFAULT_SUBJECTS
    GRADE_LEVELS = DEFAULT_GRADE_LEVELS

HIGHLIGHT_COLOR = (238, 32, 81)  # #EE2051 - rosa meio vermelho para botao selecionado

class NeumorphicPanel:
    def __init__(self, x, y, width, height, bg_color, light_shadow, dark_shadow, border_radius=20):
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = bg_color
        self.light_shadow = light_shadow
        self.dark_shadow = dark_shadow
        self.border_radius = border_radius

    def draw(self, surface):
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=self.border_radius)
        pygame.draw.rect(surface, self.dark_shadow, self.rect.inflate(6, 6), border_radius=self.border_radius, width=3)

class NeumorphicButton:
    def __init__(self, x, y, width, height, bg_color, light_shadow, dark_shadow,
                 accent_color, text, font, is_toggle=False, is_active=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = bg_color
        self.light_shadow = light_shadow
        self.dark_shadow = dark_shadow
        self.accent_color = accent_color
        self.text = text
        self.font = font
        self.is_toggle = is_toggle
        self.is_active = is_active
        self.pressed = False
        self.text_surf = font.render(text, True, (0, 0, 0))
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    def draw(self, surface):
        is_pressed = self.pressed or (self.is_toggle and self.is_active)
        if is_pressed:
            pygame.draw.rect(surface, self.bg_color, self.rect.inflate(-4, -4), border_radius=10)
            pygame.draw.rect(surface, self.accent_color, self.rect, border_radius=10, width=2)
            text_rect = self.text_surf.get_rect(center=(self.rect.centerx + 1, self.rect.centery + 1))
            surface.blit(self.text_surf, text_rect)
        else:
            pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=10)
            pygame.draw.rect(surface, self.dark_shadow, self.rect.inflate(4, 4), border_radius=10, width=2)
            surface.blit(self.text_surf, self.text_rect)

class GameConfigScreen:
    def __init__(self, screen, user_data):
        self.screen = screen
        self.running = True
        self.width, self.height = screen.get_size()
        self.user_data = user_data

        self.bg_color = COLORS["background"]
        self.light_shadow = COLORS["light_shadow"]
        self.dark_shadow = COLORS["dark_shadow"]
        self.accent_color = COLORS["accent"]

        self.title_font = pygame.font.SysFont('Arial', 36, bold=True)
        self.subtitle_font = pygame.font.SysFont('Arial', 24, bold=True)
        self.text_font = pygame.font.SysFont('Arial', 18)

        self.selected_subject = None
        self.selected_grade = None
        self.selected_difficulty = None

        panel_width = 700
        panel_height = 550
        self.panel_x = (self.width - panel_width) // 2
        self.panel_y = (self.height - panel_height) // 2
        self.main_panel = NeumorphicPanel(self.panel_x, self.panel_y, panel_width, panel_height,
                                          COLORS["accent"], self.light_shadow, self.dark_shadow)

        self.subject_buttons = self.create_subject_buttons()
        self.grade_buttons = self.create_grade_buttons()
        self.difficulty_buttons = self.create_difficulty_buttons()

        self.start_button = NeumorphicButton(self.width // 2 + 50, self.panel_y + 470, 200, 50,
                                             self.bg_color, self.light_shadow, self.dark_shadow,
                                             (75, 181, 67), "INICIAR", self.subtitle_font)

        self.back_button = NeumorphicButton(self.width // 2 - 250, self.panel_y + 470, 200, 50,
                                            self.bg_color, self.light_shadow, self.dark_shadow,
                                            (232, 77, 77), "VOLTAR", self.subtitle_font)

    def create_subject_buttons(self):
        buttons = []
        button_width = 150
        button_height = 50
        margin_x = 20
        margin_y = 15
        total_width = 4 * button_width + 3 * margin_x
        start_x = self.panel_x + (700 - total_width) // 2
        start_y = self.panel_y + 100
        for i, subject in enumerate(SUBJECTS):
            row = i // 4
            col = i % 4
            x = start_x + col * (button_width + margin_x)
            y = start_y + row * (button_height + margin_y)
            buttons.append(NeumorphicButton(x, y, button_width, button_height,
                                            self.bg_color, self.light_shadow, self.dark_shadow,
                                            self.accent_color, subject, self.text_font, is_toggle=True))
        return buttons

    def create_grade_buttons(self):
        buttons = []
        button_width = 150
        button_height = 50
        margin_x = 20
        start_x = self.width // 2 - (button_width * 1.5 + margin_x)
        start_y = self.panel_y + 260
        for i, grade in enumerate(GRADE_LEVELS):
            x = start_x + i * (button_width + margin_x)
            buttons.append(NeumorphicButton(x, start_y, button_width, button_height,
                                            self.bg_color, self.light_shadow, self.dark_shadow,
                                            self.accent_color, grade, self.text_font, is_toggle=True))
        return buttons

    def create_difficulty_buttons(self):
        buttons = []
        button_width = 150
        button_height = 50
        margin_x = 20
        start_x = self.width // 2 - (button_width * 1.5 + margin_x)
        start_y = self.panel_y + 360
        for i, level in enumerate(DEFAULT_DIFFICULTIES):
            x = start_x + i * (button_width + margin_x)
            buttons.append(NeumorphicButton(x, start_y, button_width, button_height,
                                            self.bg_color, self.light_shadow, self.dark_shadow,
                                            self.accent_color, level, self.text_font, is_toggle=True))
        return buttons

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for i, btn in enumerate(self.subject_buttons):
                    if btn.is_clicked(pos):
                        for j, b in enumerate(self.subject_buttons): b.is_active = (j == i)
                        self.selected_subject = SUBJECTS[i]
                for i, btn in enumerate(self.grade_buttons):
                    if btn.is_clicked(pos):
                        for j, b in enumerate(self.grade_buttons): b.is_active = (j == i)
                        self.selected_grade = GRADE_LEVELS[i]
                for i, btn in enumerate(self.difficulty_buttons):
                    if btn.is_clicked(pos):
                        for j, b in enumerate(self.difficulty_buttons): b.is_active = (j == i)
                        self.selected_difficulty = DEFAULT_DIFFICULTIES[i]
                if self.start_button.is_clicked(pos):
                    self.start_button.pressed = True
                    if self.selected_subject and self.selected_grade and self.selected_difficulty:
                         return {
                            "action": "start_game",
                             "subject": self.selected_subject,
                             "grade": self.selected_grade,
                             "difficulty": self.selected_difficulty
                         }
                if self.back_button.is_clicked(pos):
                    self.back_button.pressed = True
                    return {"action": "back_to_menu"}
        return {"action": "none"}

    def update(self):
        self.start_button.pressed = False
        self.back_button.pressed = False

    def draw(self):
        self.screen.fill(self.bg_color)
        self.main_panel.draw(self.screen)

        title = self.title_font.render("Configurar Jogo", True, COLORS["text"])
        self.screen.blit(title, title.get_rect(center=(self.width // 2, self.panel_y + 30)))

        subtitle1 = self.subtitle_font.render("Selecione a Matéria:", True, COLORS["text"])
        self.screen.blit(subtitle1, subtitle1.get_rect(center=(self.width // 2, self.panel_y + 80)))

        for btn in self.subject_buttons:
            btn.draw(self.screen)

        subtitle2 = self.subtitle_font.render("Selecione a Série:", True, COLORS["text"])
        self.screen.blit(subtitle2, subtitle2.get_rect(center=(self.width // 2, self.panel_y + 240)))

        for btn in self.grade_buttons:
            btn.draw(self.screen)

        subtitle3 = self.subtitle_font.render("Dificuldade:", True, COLORS["text"])
        self.screen.blit(subtitle3, subtitle3.get_rect(center=(self.width // 2, self.panel_y + 340)))

        for btn in self.difficulty_buttons:
            btn.draw(self.screen)

        self.start_button.draw(self.screen)
        self.back_button.draw(self.screen)

        if not (self.selected_subject and self.selected_grade):
            hint = self.text_font.render("Selecione uma matéria e uma série para iniciar", True, (0, 0, 0))
            self.screen.blit(hint, hint.get_rect(center=(self.width // 2, self.panel_y + 440)))

        if not (self.selected_subject and self.selected_grade and self.selected_difficulty):
            hint = self.text_font.render(
            "Selecione matéria, série e dificuldade para iniciar", True, (0, 0, 0)
            )
            self.screen.blit(hint, hint.get_rect(center=(self.width // 2, self.panel_y + 440)))

        pygame.display.flip()

    def run(self):
        while self.running:
            result = self.handle_events()
            if result["action"] != "none":
                return result
            self.update()
            self.draw()
            pygame.time.Clock().tick(60)
        return {"action": "exit"}
