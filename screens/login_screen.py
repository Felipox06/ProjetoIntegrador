import pygame
import sys
import os
from pygame.locals import *

# Cores do slide 2
COLORS = {
    "background": (30, 180, 195),     # #1EB4C3
    "light_shadow": (255, 255, 255),  # Branco
    "dark_shadow": (20, 140, 150),    # #148C96
    "accent": (251, 164, 31),         # Laranja #FBA41F
    "text": (0, 0, 0),
    "black": (0, 0, 0)
}

class LoginScreen:
    def __init__(self, screen):
        self.screen = screen
        self.running = True
        self.width, self.height = screen.get_size()

        self.bg_color = COLORS["background"]
        self.light_shadow = COLORS["light_shadow"]
        self.dark_shadow = COLORS["dark_shadow"]
        self.accent_color = COLORS["accent"]
        self.text_color = COLORS["text"]
        self.black = COLORS["black"]

        # Fundo
        try:
            bg_path = os.path.join("assets", "images", "background_slide2.png")
            self.background = pygame.image.load(bg_path).convert()
            self.background = pygame.transform.scale(self.background, (self.width, self.height))
        except:
            self.background = None

        # Fontes
        try:
            font_path = os.path.join("assets", "fonts", "pixel_font.ttf")
            self.title_font = pygame.font.Font(font_path, 48)
            self.text_font = pygame.font.Font(font_path, 24)
            self.input_font = pygame.font.Font(font_path, 22)
        except:
            self.title_font = pygame.font.SysFont('Arial', 48, bold=True)
            self.text_font = pygame.font.SysFont('Arial', 24)
            self.input_font = pygame.font.SysFont('Arial', 22)

        center_x = self.width // 2
        self.username_input = NeumorphicInput(center_x - 150, 240, 300, 50, self.bg_color, self.light_shadow, self.dark_shadow, "Usuário", self.input_font)
        self.password_input = NeumorphicInput(center_x - 150, 310, 300, 50, self.bg_color, self.light_shadow, self.dark_shadow, "Senha", self.input_font, is_password=True)

        self.login_button = NeumorphicButton(center_x - 150, 390, 300, 50, self.bg_color, self.light_shadow, self.dark_shadow, self.accent_color, "ENTRAR", self.text_font)

        self.student_button = NeumorphicButton(center_x - 150, 480, 140, 40, self.bg_color, self.light_shadow, self.dark_shadow, self.accent_color, "Aluno", self.text_font, is_toggle=True, is_active=True)
        self.teacher_button = NeumorphicButton(center_x + 10, 480, 140, 40, self.bg_color, self.light_shadow, self.dark_shadow, self.accent_color, "Professor", self.text_font, is_toggle=True)

        self.user_type = "student"
        self.show_password = False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if self.username_input.is_clicked(pos):
                    self.username_input.active = True
                    self.password_input.active = False
                elif self.password_input.is_clicked(pos):
                    self.username_input.active = False
                    self.password_input.active = True
                elif self.login_button.is_clicked(pos):
                    self.login_button.pressed = True
                    return {"action": "login_success", "user_type": self.user_type, "username": self.username_input.text}
                elif self.student_button.is_clicked(pos):
                    self.student_button.is_active = True
                    self.teacher_button.is_active = False
                    self.user_type = "student"
                elif self.teacher_button.is_clicked(pos):
                    self.teacher_button.is_active = True
                    self.student_button.is_active = False
                    self.user_type = "teacher"
                elif self.password_input.icon_rect.collidepoint(pos):
                    self.show_password = not self.show_password
                    self.password_input.show_password = self.show_password

            if event.type == KEYDOWN:
                active_input = self.username_input if self.username_input.active else self.password_input if self.password_input.active else None
                if active_input:
                    if event.key == K_BACKSPACE:
                        active_input.text = active_input.text[:-1]
                    elif event.key == K_RETURN:
                        return {"action": "login_success", "user_type": self.user_type, "username": self.username_input.text}
                    else:
                        active_input.text += event.unicode

        return {"action": "none"}

    def draw(self):
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(self.bg_color)

        # Caixa amarela central
        box_x, box_y = 50, 50
        box_width = self.width - 100
        box_height = self.height - 100
        pygame.draw.rect(self.screen, self.accent_color, (box_x, box_y, box_width, box_height), border_radius=20)

        # Título
        title_text = self.title_font.render("PoliGame Show", True, self.black)
        title_rect = title_text.get_rect(center=(self.width // 2, 100))
        self.screen.blit(title_text, title_rect)

        # Campos e botões
        self.username_input.draw(self.screen)
        self.password_input.draw(self.screen)
        self.login_button.draw(self.screen)
        self.student_button.draw(self.screen)
        self.teacher_button.draw(self.screen)

        # Texto tipo usuário
        type_text = self.text_font.render("Selecione seu tipo de usuário:", True, self.black)
        type_rect = type_text.get_rect(center=(self.width // 2, 460))
        self.screen.blit(type_text, type_rect)

        pygame.display.flip()

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            result = self.handle_events()
            if result["action"] == "login_success":
                return result
            self.draw()
            clock.tick(60)
        return {"action": "exit"}

class NeumorphicButton:
    def __init__(self, x, y, width, height, bg_color, light_shadow, dark_shadow, accent_color, text, font, is_toggle=False, is_active=False):
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

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    def draw(self, surface):
        is_pressed = self.pressed or (self.is_toggle and self.is_active)
        color = self.accent_color if is_pressed else self.bg_color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        border_color = self.accent_color if is_pressed else self.dark_shadow
        pygame.draw.rect(surface, border_color, self.rect, width=2, border_radius=10)

        text_color = (255, 255, 255) if is_pressed else (0, 0, 0)
        text_surf = self.font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

class NeumorphicInput:
    def __init__(self, x, y, width, height, bg_color, light_shadow, dark_shadow, placeholder, font, is_password=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = bg_color
        self.light_shadow = light_shadow
        self.dark_shadow = dark_shadow
        self.placeholder = placeholder
        self.font = font
        self.is_password = is_password
        self.text = ""
        self.active = False
        self.show_password = False
        self.icon_rect = pygame.Rect(x + width - 35, y + 15, 20, 20)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    def draw(self, surface):
        pygame.draw.rect(surface, self.bg_color, self.rect.inflate(-4, -4), border_radius=10)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, border_radius=10, width=2)

        if self.text:
            displayed_text = self.text if not (self.is_password and not self.show_password) else "•" * len(self.text)
            text_surface = self.font.render(displayed_text, True, (0, 0, 0))
        else:
            text_surface = self.font.render(self.placeholder, True, (150, 150, 150))

        text_rect = text_surface.get_rect(midleft=(self.rect.x + 15, self.rect.centery))
        surface.blit(text_surface, text_rect)

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 700))
    pygame.display.set_caption("Login Slide 2 - Quiz do Milhão")

    login_screen = LoginScreen(screen)
    result = login_screen.run()
    print("Resultado:", result)

if __name__ == "__main__":
    main()
