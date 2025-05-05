# screens/login_screen.py

import pygame
import sys
import os
from pygame.locals import *

# Importe direto do config no mesmo diretório
try:
    import config
except ImportError:
    # Definições padrão caso o arquivo config.py não exista
    class Config:
        def __init__(self):
            self.COLORS = {
                "background": (235, 235, 240),
                "light_shadow": (255, 255, 255),
                "dark_shadow": (205, 205, 210),
                "accent": (106, 130, 251),
                "text": (60, 60, 60)
            }
    config = Config()

class NeumorphicPanel:
    def __init__(self, x, y, width, height, bg_color, light_shadow, dark_shadow, border_radius=20):
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = bg_color
        self.light_shadow = light_shadow
        self.dark_shadow = dark_shadow
        self.border_radius = border_radius
    
    def draw(self, surface):
        # Desenhar retângulo principal com bordas arredondadas
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=self.border_radius)
        
        # Desenhar sombra clara (superior esquerda)
        shadow_rect_light = pygame.Rect(self.rect.x-3, self.rect.y-3, self.rect.width, self.rect.height)
        pygame.draw.rect(surface, self.light_shadow, shadow_rect_light, border_radius=self.border_radius, width=3)
        
        # Desenhar sombra escura (inferior direita)
        shadow_rect_dark = pygame.Rect(self.rect.x+3, self.rect.y+3, self.rect.width, self.rect.height)
        pygame.draw.rect(surface, self.dark_shadow, shadow_rect_dark, border_radius=self.border_radius, width=3)

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
        
        # Preparar superfície de texto
        self.text_surf = font.render(text, True, (50, 50, 50))
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)
    
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
    
    def draw(self, surface):
        # Determinar se o botão está pressionado (visualmente)
        is_pressed = self.pressed or (self.is_toggle and self.is_active)
        
        if is_pressed:
            # Estado pressionado: inverter sombras e aplicar cor de destaque
            pygame.draw.rect(surface, self.bg_color, 
                           pygame.Rect(self.rect.x+2, self.rect.y+2, self.rect.width-4, self.rect.height-4), 
                           border_radius=10)
            
            # Borda com cor de destaque
            pygame.draw.rect(surface, self.accent_color, 
                           self.rect, border_radius=10, width=2)
            
            # Deslocar o texto ligeiramente
            text_rect = self.text_surf.get_rect(center=(self.rect.centerx+1, self.rect.centery+1))
            surface.blit(self.text_surf, text_rect)
        else:
            # Estado normal: efeito neumórfico
            pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=10)
            
            # Desenhar sombras
            shadow_rect_light = pygame.Rect(self.rect.x-2, self.rect.y-2, self.rect.width, self.rect.height)
            pygame.draw.rect(surface, self.light_shadow, shadow_rect_light, border_radius=10, width=2)
            
            shadow_rect_dark = pygame.Rect(self.rect.x+2, self.rect.y+2, self.rect.width, self.rect.height)
            pygame.draw.rect(surface, self.dark_shadow, shadow_rect_dark, border_radius=10, width=2)
            
            # Desenhar texto
            surface.blit(self.text_surf, self.text_rect)

class NeumorphicInput:
    def __init__(self, x, y, width, height, bg_color, light_shadow, dark_shadow, 
                 placeholder, font, is_password=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = bg_color
        self.light_shadow = light_shadow
        self.dark_shadow = dark_shadow
        self.placeholder = placeholder
        self.font = font
        self.is_password = is_password
        self.text = ""
        self.active = False
        
        # Cursor piscante
        self.cursor_visible = True
        self.cursor_timer = 0
    
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
    
    def draw(self, surface):
        # Desenhar o fundo do input (invertido do normal para parecer afundado)
        pygame.draw.rect(surface, self.bg_color, 
                       pygame.Rect(self.rect.x+2, self.rect.y+2, self.rect.width-4, self.rect.height-4), 
                       border_radius=10)
        
        # Desenhar sombras internas (invertidas)
        shadow_rect_dark = pygame.Rect(self.rect.x-2, self.rect.y-2, self.rect.width, self.rect.height)
        pygame.draw.rect(surface, self.dark_shadow, shadow_rect_dark, border_radius=10, width=2)
        
        shadow_rect_light = pygame.Rect(self.rect.x+2, self.rect.y+2, self.rect.width, self.rect.height)
        pygame.draw.rect(surface, self.light_shadow, shadow_rect_light, border_radius=10, width=2)
        
        # Desenhar linha de destaque se ativo
        if self.active:
            pygame.draw.line(surface, (120, 120, 255), 
                           (self.rect.x + 15, self.rect.y + self.rect.height - 8),
                           (self.rect.x + self.rect.width - 15, self.rect.y + self.rect.height - 8),
                           2)
        
        # Exibir texto ou placeholder
        if self.text:
            if self.is_password:
                displayed_text = "•" * len(self.text)
            else:
                displayed_text = self.text
            
            text_surface = self.font.render(displayed_text, True, (50, 50, 50))
        else:
            text_surface = self.font.render(self.placeholder, True, (150, 150, 150))
        
        text_rect = text_surface.get_rect(midleft=(self.rect.x + 15, self.rect.y + self.rect.height // 2))
        surface.blit(text_surface, text_rect)
        
        # Desenhar cursor piscante se ativo
        if self.active:
            # Atualizar timer do cursor
            self.cursor_timer += 1
            if self.cursor_timer >= 30:  # piscar a cada 30 frames (aproximadamente 0.5s em 60fps)
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = 0
            
            if self.cursor_visible:
                if self.is_password:
                    cursor_x = text_rect.right + 2
                else:
                    cursor_x = text_rect.right + 2
                
                pygame.draw.line(surface, (50, 50, 50),
                               (cursor_x, self.rect.y + 15),
                               (cursor_x, self.rect.y + self.rect.height - 15),
                               2)

class LoginScreen:
    def __init__(self, screen):
        self.screen = screen
        self.running = True
        self.width, self.height = screen.get_size()
        
        # Cores do design neumorfista
        self.bg_color = config.COLORS["background"]
        self.light_shadow = config.COLORS["light_shadow"]
        self.dark_shadow = config.COLORS["dark_shadow"]
        self.accent_color = config.COLORS["accent"]
        
        # Usar fonte padrão do sistema em vez de carregar fonte externa
        self.title_font = pygame.font.SysFont('Arial', 36, bold=True)
        self.text_font = pygame.font.SysFont('Arial', 18)
        
        # Criar elementos de UI
        center_x = self.width // 2
        
        # Painel principal
        self.main_panel = NeumorphicPanel(
            center_x - 200, 150, 
            400, 450, 
            self.bg_color, self.light_shadow, self.dark_shadow
        )
        
        # Campos de entrada
        self.username_input = NeumorphicInput(
            center_x - 150, 280,
            300, 50,
            self.bg_color, self.light_shadow, self.dark_shadow,
            "Usuário", self.text_font
        )
        
        self.password_input = NeumorphicInput(
            center_x - 150, 350,
            300, 50,
            self.bg_color, self.light_shadow, self.dark_shadow,
            "Senha", self.text_font,
            is_password=True
        )
        
        # Botões
        self.login_button = NeumorphicButton(
            center_x - 150, 430,
            300, 50,
            self.bg_color, self.light_shadow, self.dark_shadow,
            self.accent_color, "ENTRAR", self.text_font
        )
        
        self.user_type = "student"  # Padrão: aluno
        
        # Botões de seleção de tipo de usuário
        self.student_button = NeumorphicButton(
            center_x - 150, 500,
            140, 40,
            self.bg_color, self.light_shadow, self.dark_shadow,
            self.accent_color, "Aluno", self.text_font,
            is_toggle=True, is_active=True
        )
        
        self.teacher_button = NeumorphicButton(
            center_x + 10, 500,
            140, 40,
            self.bg_color, self.light_shadow, self.dark_shadow,
            self.accent_color, "Professor", self.text_font,
            is_toggle=True, is_active=False
        )
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Verificar interações com os elementos
                if self.username_input.is_clicked(mouse_pos):
                    self.username_input.active = True
                    self.password_input.active = False
                
                elif self.password_input.is_clicked(mouse_pos):
                    self.username_input.active = False
                    self.password_input.active = True
                
                # Verificar se o botão de login foi clicado
                elif self.login_button.is_clicked(mouse_pos):
                    self.login_button.pressed = True
                    
                    # Simulação de login (fase de teste)
                    username = self.username_input.text
                    password = self.password_input.text
                    
                    # Nesta fase de testes, qualquer entrada é válida
                    self.running = False
                    return {"action": "login_success", "user_type": self.user_type, "username": username}
                
                # Verificar botões de seleção de tipo de usuário
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
                    
                    # Nesta fase de testes, qualquer entrada é válida
                    self.running = False
                    return {"action": "login_success", "user_type": self.user_type, "username": username}
        
        return {"action": "none"}
    
    def update(self):
        # Lógica de atualização (se necessário)
        if self.login_button.pressed:
            self.login_button.pressed = False
    
    def draw(self):
        # Limpa a tela com a cor de fundo
        self.screen.fill(self.bg_color)
        
        # Desenha o painel principal
        self.main_panel.draw(self.screen)
        
        # Desenha o título
        title_text = self.title_font.render("Quiz do Milhão", True, (60, 60, 60))
        title_rect = title_text.get_rect(center=(self.width // 2, 200))
        self.screen.blit(title_text, title_rect)
        
        # Desenha os campos de entrada
        self.username_input.draw(self.screen)
        self.password_input.draw(self.screen)
        
        # Desenha os botões
        self.login_button.draw(self.screen)
        self.student_button.draw(self.screen)
        self.teacher_button.draw(self.screen)
        
        # Desenha texto explicativo
        type_text = self.text_font.render("Selecione seu tipo de usuário:", True, (60, 60, 60))
        type_rect = type_text.get_rect(center=(self.width // 2, 480))
        self.screen.blit(type_text, type_rect)
        
        # Atualiza a tela
        pygame.display.flip()
    
    def run(self):
        while self.running:
            result = self.handle_events()
            if result["action"] == "login_success":
                return result
            self.update()
            self.draw()
            pygame.time.Clock().tick(60)
        
        # Retorno no caso de sair do loop por outros meios
        return {"action": "exit"}