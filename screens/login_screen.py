import pygame
import sys
import os
from pygame.locals import *
pygame.init()

# importe do config:
try:
    import config
except ImportError:
    class Config:
        def __init__(self):
            self.COLORS = {
               "background": (30, 180, 195),     
                "light_shadow": (255, 255, 255), 
                "dark_shadow": (20, 140, 150),    
                "accent": (27, 185, 185),    
                "text": (0, 0, 0),
                "warning": (251, 164, 31),
                "black": (0, 0, 0)}       
            try:
                # Caminho absoluto ou relativo determinado pelo seu projeto
                font_path = os.path.join("assets", "fonts", "pixel_font.ttf")
                self.title_font = pygame.font.Font(font_path, 36)
                self.text_font = pygame.font.Font(font_path, 18)
            except FileNotFoundError:
                # Fallback para fontes do sistema caso não encontre as pixeladas
                print("Aviso: Fonte pixelada não encontrada. Usando fontes do sistema.")
                self.title_font = pygame.font.SysFont('Arial', 36, bold=True)
                self.text_font = pygame.font.SysFont('Arial', 18)
    config = Config()

class SimplePanel:
    def __init__(self, x, y, width, height, bg_color, border_radius=20):
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = bg_color
        self.border_radius = border_radius
    
    def draw(self, surface):
        # Desenhar retângulo principal com bordas arredondadas e contorno preto fino
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=self.border_radius)
        pygame.draw.rect(surface, config.COLORS["black"], self.rect, border_radius=self.border_radius, width=1)

class SimpleButton:
    def __init__(self, x, y, width, height, bg_color, accent_color, text, font, is_toggle=False, is_active=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = bg_color
        self.accent_color = accent_color
        self.text = text
        self.font = font
        self.is_toggle = is_toggle
        self.is_active = is_active
        self.pressed = False
        
        # Preparar superfície de texto
        self.text_surf = font.render(text, True, config.COLORS["text"])
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)
    
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
    
    def draw(self, surface):
        # Determinar se o botão está pressionado (visualmente)
        is_pressed = self.pressed or (self.is_toggle and self.is_active)
        
        if is_pressed:
            # Estado pressionado: cor de destaque e contorno mais espesso
            pygame.draw.rect(surface, self.accent_color, self.rect, border_radius=10)
            pygame.draw.rect(surface, config.COLORS["black"], self.rect, border_radius=10, width=2)
            
            # Texto em branco para contraste
            pressed_text = self.font.render(self.text, True, (255, 255, 255))
            surface.blit(pressed_text, self.text_rect)
        else:
            # Estado normal: contorno preto fino
            pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=10)
            pygame.draw.rect(surface, config.COLORS["black"], self.rect, border_radius=10, width=1)
            
            # Desenhar texto
            surface.blit(self.text_surf, self.text_rect)

class SimpleInput:
    def __init__(self, x, y, width, height, bg_color, placeholder, font, is_password=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = bg_color
        self.placeholder = placeholder
        self.font = font
        self.is_password = is_password
        self.text = ""
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0
    
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
    
    def draw(self, surface):
        # Desenhar o fundo do input com contorno preto fino
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=10)
        pygame.draw.rect(surface, config.COLORS["black"], self.rect, border_radius=10, width=1)
        
        # Linha de destaque se ativo (em azul)
        if self.active:
            pygame.draw.line(surface, (0, 100, 255), 
                           (self.rect.x + 15, self.rect.y + self.rect.height - 8),
                           (self.rect.x + self.rect.width - 15, self.rect.y + self.rect.height - 8),
                           2)
        
        # Exibir texto ou placeholder
        if self.text:
            if self.is_password:
                displayed_text = "•" * len(self.text)
            else:
                displayed_text = self.text
            
            text_surface = self.font.render(displayed_text, True, config.COLORS["text"])
        else:
            text_surface = self.font.render(self.placeholder, True, (100, 100, 100))
        
        text_rect = text_surface.get_rect(midleft=(self.rect.x + 15, self.rect.y + self.rect.height // 2))
        surface.blit(text_surface, text_rect)
        
        # Desenhar cursor piscante se ativo
        if self.active:
            self.cursor_timer += 1
            if self.cursor_timer >= 30:
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = 0
            
            if self.cursor_visible:
                cursor_x = text_rect.right + 2
                pygame.draw.line(surface, config.COLORS["text"],
                               (cursor_x, self.rect.y + 15),
                               (cursor_x, self.rect.y + self.rect.height - 15),
                               2)

class LoginScreen:
    def __init__(self, screen):
        self.screen = screen
        self.running = True
        self.width, self.height = screen.get_size()
        
        # Cores
        self.bg_color = config.COLORS["background"]
        self.accent_color = config.COLORS["accent"]
        
        # Tentar carregar fontes personalizadas
        try:
            font_path = os.path.join("assets", "fonts", "pixel_font.ttf")
            self.title_font = pygame.font.Font(font_path, 70)
            self.text_font = pygame.font.Font(font_path, 18)
        except FileNotFoundError:
            print("Aviso: Fonte pixelada não encontrada. Usando fontes do sistema.")
            self.title_font = pygame.font.SysFont('Arial', 36, bold=True)
            self.text_font = pygame.font.SysFont('Arial', 18)
        
        # Criar elementos de UI (posicionados mais para cima)
        center_x = self.width // 2
        vertical_offset = -50  # Move tudo para cima
        
        # Painel principal
        self.main_panel = SimplePanel(
            center_x - 200, 100 + vertical_offset, 
            400, 450, 
            self.bg_color
        )
        
        # Campos de entrada
        self.username_input = SimpleInput(
            center_x - 150, 230 + vertical_offset,
            300, 50,
            self.bg_color,
            "RA do Aluno", self.text_font
        )
        
        self.password_input = SimpleInput(
            center_x - 150, 300 + vertical_offset,
            300, 50,
            self.bg_color,
            "Senha", self.text_font,
            is_password=True
        )
        
        # Botões
        self.login_button = SimpleButton(
            center_x - 150, 380 + vertical_offset,
            300, 50,
            self.bg_color, self.accent_color, 
            "ENTRAR", self.text_font
        )
        
        self.user_type = "student"  # Padrão: aluno
        
        # Botões de seleção de tipo de usuário
        self.student_button = SimpleButton(
            center_x - 150, 450 + vertical_offset,
            140, 40,
            self.bg_color, self.accent_color,
            "Aluno", self.text_font,
            is_toggle=True, is_active=True
        )
        
        self.teacher_button = SimpleButton(
            center_x + 10, 450 + vertical_offset,
            140, 40,
            self.bg_color, self.accent_color,
            "Professor", self.text_font,
            is_toggle=True, is_active=False
        )
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                if self.username_input.is_clicked(mouse_pos):
                    self.username_input.active = True
                    self.password_input.active = False
                
                elif self.password_input.is_clicked(mouse_pos):
                    self.username_input.active = False
                    self.password_input.active = True
                
                elif self.login_button.is_clicked(mouse_pos):
                    self.login_button.pressed = True
                    username = self.username_input.text
                    password = self.password_input.text
                    self.running = False
                    return {"action": "login_success", "user_type": self.user_type, "username": username}
                
                elif self.student_button.is_clicked(mouse_pos):
                    self.student_button.is_active = True
                    self.teacher_button.is_active = False
                    self.user_type = "student"
                
                elif self.teacher_button.is_clicked(mouse_pos):
                    self.student_button.is_active = False
                    self.teacher_button.is_active = True
                    self.user_type = "teacher"
                
                else:
                    self.username_input.active = False
                    self.password_input.active = False
            
            if event.type == KEYDOWN:
                if self.username_input.active:
                    if event.key == K_BACKSPACE:
                        self.username_input.text = self.username_input.text[:-1]
                    else:
                        self.username_input.text += event.unicode
                
                elif self.password_input.active:
                    if event.key == K_BACKSPACE:
                        self.password_input.text = self.password_input.text[:-1]
                    else:
                        self.password_input.text += event.unicode
                
                if event.key == K_RETURN:
                    self.login_button.pressed = True
                    username = self.username_input.text
                    password = self.password_input.text
                    self.running = False
                    return {"action": "login_success", "user_type": self.user_type, "username": username}
        
        return {"action": "none"}
    
    def update(self):
        if self.login_button.pressed:
            self.login_button.pressed = False

    def draw(self):
        self.screen.fill(self.bg_color)

        # Caixa amarela (accent) atrás do painel principal para destaque
        accent_rect = pygame.Rect(
            self.main_panel.rect.x - 10, 
            self.main_panel.rect.y - 10, 
            self.main_panel.rect.width + 20, 
            self.main_panel.rect.height + 20
        )
        pygame.draw.rect(self.screen, self.accent_color, accent_rect, border_radius=25)
        
        # Painel principal (sobre a caixa amarela)
        self.main_panel.draw(self.screen)
        
        # titulo:
        title_text = self.title_font.render("PoliGame Show", True, config.COLORS["text"])
        title_rect = title_text.get_rect(center=(self.width // 2, 100))
        self.screen.blit(title_text, title_rect)
        
        # botoes e inputs
        self.username_input.draw(self.screen)
        self.password_input.draw(self.screen)
        self.login_button.draw(self.screen)
        self.student_button.draw(self.screen)
        self.teacher_button.draw(self.screen)
    
    def run(self):
        clock = pygame.time.Clock()
        result = {"action": "none"}
        
        while self.running:
            result = self.handle_events()
            self.update()
            self.draw()
            pygame.display.flip()
            clock.tick(60)
        
        return result

def main():
    screen = pygame.display.set_mode((800, 700))
    pygame.display.set_caption("Login Screen Example")
    
    login_screen = LoginScreen(screen)
    result = login_screen.run()
    
    print("Resultado do login:", result)
    pygame.quit()

if __name__ == "__main__":
    main()
