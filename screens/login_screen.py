import pygame
import sys
import os
from pygame.locals import *
from config import COLORS
from databse.data_manager import verify_user_credentials_from_db
from databse.db_connector import getConnection
pygame.init()

# importe do config:
try:
    import config
except ImportError:
    class Config:
        def __init__(self):
            self.COLORS = {
                 "background": (235, 235, 240),
                "light_shadow": (255, 255, 255),
                "dark_shadow": (205, 205, 210),
                "accent": (27, 185, 185),
                "text": (60, 60, 60),
                "success": (75, 181, 67),
                "warning": (251, 164, 31),
                "error": (232, 77, 77),
                "black": (0, 0, 0),
                "progress": (238, 32, 81),
                        }
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
        self.warning_color = config.COLORS["warning"]
        
        # Tentar carregar fontes personalizadas
        try:
            font_path = os.path.join("assets", "fonts", "pixel_font.ttf")
            self.title_font = pygame.font.Font(font_path, 70)
            self.text_font = pygame.font.Font(font_path, 18)
        except FileNotFoundError:
            print("Aviso: Fonte pixelada não encontrada. Usando fontes do sistema.")
            self.title_font = pygame.font.SysFont('Arial', 36, bold=True)
            self.text_font = pygame.font.SysFont('Arial', 18)
            self.error_font = pygame.font.SysFont('Arial', 16, italic=True)
        
        # Adicionar atributos para a mensagem de erro
        self.error_message = ""
        self.message_timer = 0
        # Tornar o offset um atributo da classe para ser usado em draw()
        self.vertical_offset = -50 
        
        # Criar elementos de UI (posicionados mais para cima)
        center_x = self.width // 2
        vertical_offset = -50  # Move tudo para cima
        
        # Painel principal
        self.main_panel = SimplePanel(
            center_x - 200, 100 + vertical_offset, 
            400, 450, 
            config.COLORS["accent"]
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
            self.bg_color, self.warning_color, 
            "ENTRAR", self.text_font
        )
        
        self.user_type = "student"  # Padrão: aluno
        
        # Botões de seleção de tipo de usuário
        self.student_button = SimpleButton(
            center_x - 150, 450 + vertical_offset,
            140, 40,
            self.bg_color, self.warning_color,
            "Aluno", self.text_font,
            is_toggle=True, is_active=True
        )
        
        self.teacher_button = SimpleButton(
            center_x + 10, 450 + vertical_offset,
            140, 40,
            self.bg_color, self.warning_color,
            "Professor", self.text_font,
            is_toggle=True, is_active=False
        )

    def _attempt_login(self):
        
        # Pega os dados dos inputs, chama a verificação no banco e lida com o resultado.
        
        ra_digitado = self.username_input.text.strip()
        senha_digitada = self.password_input.text
        tipo_selecionado = self.user_type # "student" ou "teacher"

        if not ra_digitado or not senha_digitada:
            self.error_message = "RA e Senha são obrigatórios."
            self.message_timer = 180
            return {"action": "login_failed"}

        try:
            # Chama a função do data_manager
            user_data = verify_user_credentials_from_db(ra_digitado, senha_digitada, tipo_selecionado, getConnection)
        except Exception as e:
            self.error_message = f"Erro de conexão: {e}"
            self.message_timer = 180
            return {"action": "login_failed"}

        if user_data:
            # LOGIN BEM-SUCEDIDO
            self.running = False # Encerra o loop da tela de login
            return {"action": "login_success", "user_data": user_data}
        else:
            # LOGIN FALHOU - Verifica se é para o outro tipo de usuário
            outro_tipo = "teacher" if tipo_selecionado == "student" else "student"
            user_data_outro_tipo = verify_user_credentials_from_db(ra_digitado, senha_digitada, outro_tipo, getConnection)
            
            if user_data_outro_tipo:
                tipo_correto_display = "Professor" if outro_tipo == "teacher" else "Aluno"
                self.error_message = f"Credenciais para {tipo_correto_display}? Selecione o tipo correto."
                self.message_timer = 240
            else:
                self.error_message = "RA ou Senha inválidos."
                self.message_timer = 180
            
            return {"action": "login_failed"}
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if self.username_input.is_clicked(mouse_pos):
                    self.username_input.active = True; self.password_input.active = False
                elif self.password_input.is_clicked(mouse_pos):
                    self.username_input.active = False; self.password_input.active = True
                elif self.student_button.is_clicked(mouse_pos):
                    self.student_button.is_active = True; self.teacher_button.is_active = False
                    self.user_type = "student"
                elif self.teacher_button.is_clicked(mouse_pos):
                    self.student_button.is_active = False; self.teacher_button.is_active = True
                    self.user_type = "teacher"
                elif self.login_button.is_clicked(mouse_pos): # Botão de Login
                    self.login_button.pressed = True
                    return self._attempt_login() # Chama a lógica de login
                else:
                    self.username_input.active = False; self.password_input.active = False
            
            if event.type == KEYDOWN:
                if event.key == K_RETURN: # Tecla Enter
                    return self._attempt_login() # Chama a lógica de login
                
                # Input de texto (seu código original)
                if self.username_input.active:
                    if event.key == K_BACKSPACE: self.username_input.text = self.username_input.text[:-1]
                    else: self.username_input.text += event.unicode
                elif self.password_input.active:
                    if event.key == K_BACKSPACE: self.password_input.text = self.password_input.text[:-1]
                    else: self.password_input.text += event.unicode
        
        return {"action": "none"}
    
    def update(self):
        if self.login_button.pressed:
            self.login_button.pressed = False
        if self.message_timer > 0:
            self.message_timer -= 1

    def draw(self):
        self.screen.fill(self.warning_color)

        # Painel principal (com os elemento - tp formulario)
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

        if self.message_timer > 0:
            error_color = config.COLORS.get("error", (232, 77, 77)) 
            error_surf = self.error_font.render(self.error_message, True, error_color)
            # Posicionar a mensagem de erro (ex: acima do botão de entrar)
            error_rect = error_surf.get_rect(center=(self.width // 2, 395 + self.vertical_offset))
            self.screen.blit(error_surf, error_rect)
    
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
