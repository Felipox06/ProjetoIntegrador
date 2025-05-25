import pygame
import sys
import os
from pygame.locals import *

# importacoes
try:
    import config
except ImportError:
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    
    COLORS = {
    "background": (235, 235, 240),
    "light_shadow": (255, 255, 255),
    "dark_shadow": (205, 205, 210),
    "accent": (27, 185, 185),
    "text": (0, 0, 0),
    "success": (75, 181, 67),
    "warning": (251, 164, 31),
    "error": (232, 77, 77),
    "black": (0, 0, 0),
}

class NeumorphicPanel:
    def __init__(self, x, y, width, height, bg_color, light_shadow, dark_shadow, border_radius=20):
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = bg_color
        self.light_shadow = light_shadow
        self.dark_shadow = dark_shadow
        self.border_radius = border_radius
    
    def draw(self, surface):
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=self.border_radius)

        pygame.draw.rect(surface, (0, 0, 0), self.rect, width=1, border_radius=self.border_radius)

class NeumorphicButton:
    def __init__(self, x, y, width, height, bg_color, light_shadow, dark_shadow, 
                 accent_color, text, font, is_toggle=False, is_active=False, icon=None):
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
        self.icon = icon
        
        # Preparar superfície de texto
        self.text_surf = font.render(text, True, (50, 50, 50))
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)
        
        # Se tiver ícone, ajustar posição do texto
        if self.icon:
            self.text_rect.centerx += 15
    
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
    
    def draw(self, surface):
        # Determinar se o botão está pressionado
        is_pressed = self.pressed or (self.is_toggle and self.is_active)

        # Desenhar o fundo do botão (com ou sem efeito de pressionado)
        if is_pressed:
            pygame.draw.rect(
                surface, self.bg_color,
                pygame.Rect(self.rect.x + 2, self.rect.y + 2, self.rect.width - 4, self.rect.height - 4),
                border_radius=10
            )
        else:
            pygame.draw.rect(
                surface, self.bg_color,
                self.rect,
                border_radius=10
            )

        #contorno preto:
        pygame.draw.rect(surface, (0, 0, 0), self.rect, width=1, border_radius=10)

        text_rect = self.text_surf.get_rect(center=self.rect.center)
        if self.icon:
            text_rect.centerx += 15  # Desloca o texto para a direita se houver ícone

        #texto:
        surface.blit(self.text_surf, text_rect)

        # ícone:
        if self.icon:
            icon_rect = self.icon.get_rect(midright=(text_rect.left - 5, text_rect.centery))
            surface.blit(self.icon, icon_rect)


class MenuScreen:
    def __init__(self, screen, user_data):
        self.screen = screen
        self.running = True
        self.width, self.height = screen.get_size()
        self.user_data = user_data 
        
        # Cores do design neumorfista
        try:
            self.bg_color = config.COLORS["background"]
            self.light_shadow = config.COLORS["light_shadow"]
            self.dark_shadow = config.COLORS["dark_shadow"]
            self.accent_color = config.COLORS["accent"]
            self.warning_color = config.COLORS["warning"]
        except (AttributeError, NameError):
            self.bg_color = (235, 235, 240)
            self.light_shadow = (255, 255, 255)
            self.dark_shadow = (205, 205, 210)
            self.accent_color = (106, 130, 251)
            self.warning_color = (251, 164, 31)
        
        # Usar fonte padrão do sistema
        self.title_font = pygame.font.SysFont('Arial', 36, bold=True)
        self.subtitle_font = pygame.font.SysFont('Arial', 24, bold=True)
        self.text_font = pygame.font.SysFont('Arial', 18)
        
        # Criar elementos de UI
        center_x = self.width // 2
        
        # Painel principal
        panel_height = 520 if self.user_data["user_type"] == "teacher" else 500
        self.main_panel = NeumorphicPanel(
            center_x - 350, 50, 700, 
            panel_height, 
            self.accent_color, self.light_shadow, self.dark_shadow
        )
        
        # Criar botões com base no tipo de usuário
        self.buttons = self.create_buttons()
        
        
    def create_buttons(self):
        buttons = []
        center_x = self.width // 2
        
        # Criar botões baseados no tipo de usuário
        if self.user_data["user_type"] == "student":
            buttons.append(NeumorphicButton(
                center_x - 250, 180,
                500, 60,
                self.warning_color, self.light_shadow, self.dark_shadow,  # Fundo amarelo warning
                self.accent_color, "JOGAR", self.subtitle_font
            ))
            
            buttons.append(NeumorphicButton(
                center_x - 250, 270,
                500, 60,
                self.warning_color, self.light_shadow, self.dark_shadow,  # Fundo amarelo warning
                self.accent_color, "Pontuação", self.subtitle_font
            ))
            
            # Botão de sair para estudantes 
            buttons.append(NeumorphicButton(
                center_x - 250, 450,
                500, 40,
                self.warning_color, self.light_shadow, self.dark_shadow, 
                (232, 77, 77),  
                "SAIR", self.text_font
            ))

        else:
            # Para professores - todos os botões de gerenciamento
            buttons.append(NeumorphicButton(
                center_x - 250, 160,
                500, 55,
                self.warning_color, self.light_shadow, self.dark_shadow,  # Fundo amarelo warning
                self.accent_color, "JOGAR", self.subtitle_font
            ))
        
            buttons.append(NeumorphicButton(
                center_x - 250, 230,
                500, 55,
                self.warning_color, self.light_shadow, self.dark_shadow,  # Fundo amarelo warning
                self.accent_color, "GERENCIAR QUESTÕES", self.subtitle_font
            ))
        
            buttons.append(NeumorphicButton(
                center_x - 250, 300,
                500, 55,
                self.warning_color, self.light_shadow, self.dark_shadow,  # Fundo amarelo warning
                self.accent_color, "GERENCIAR TURMAS", self.subtitle_font
            ))
            
            # Botão GERENCIAR USUÁRIOS (com fundo amarelo e texto roxo)
            buttons.append(NeumorphicButton(
                center_x - 250, 370,
                500, 55,
                self.warning_color, self.light_shadow, self.dark_shadow,  # Fundo amarelo warning
                (180, 120, 255),  # Cor roxa para diferenciar
                "GERENCIAR USUÁRIOS", self.subtitle_font
            ))
           
            buttons.append(NeumorphicButton(
                center_x - 250, 440,
                500, 55,
                self.warning_color, self.light_shadow, self.dark_shadow,  # Fundo amarelo warning
                self.accent_color, "RANKING", self.subtitle_font
            ))
            
            # Botão de sair para professores (mantemos vermelho como destaque)
            buttons.append(NeumorphicButton(
                center_x - 250, 500,
                500, 40,
                self.warning_color, self.light_shadow, self.dark_shadow,
                (232, 77, 77),  
                "SAIR", self.text_font
            ))
        
        return buttons
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Verificar cliques nos botões
                for i, button in enumerate(self.buttons):
                    if button.is_clicked(mouse_pos):
                        button.pressed = True
                        
                        # Processar ação do botão para estudantes
                        if self.user_data["user_type"] == "student":
                            if i == 0:  # JOGAR
                                return {"action": "play_game"}
                            elif i == 1:  # pontuacao
                                return {"action": "show_history"}
                            elif i == 2:  # SAIR
                                return {"action": "logout"}
                        # Processar ação do botão para professores
                        else:
                            if i == 0:  # JOGAR
                                return {"action": "play_game"}
                            elif i == 1:  # GERENCIAR QUESTÕES
                                return {"action": "manage_questions"}
                            elif i == 2:  # GERENCIAR TURMAS
                                return {"action": "manage_classes"}
                            elif i == 3:  # GERENCIAR USUÁRIOS (NOVO)
                                return {"action": "manage_users"}
                            elif i == 4:  # RANKING
                                return {"action": "show_ranking"}
                            elif i == 5:  # SAIR
                                return {"action": "logout"}
        
        return {"action": "none"}
    
    def update(self):
        # Redefinir estado dos botões
        for button in self.buttons:
            button.pressed = False
    
    def draw(self):
        self.screen.fill(self.warning_color)
        self.main_panel.draw(self.screen) #painel principal
        # titulo:
        title_text = self.title_font.render("PoliGame Show", True, (60, 60, 60))
        title_rect = title_text.get_rect(center=(self.width // 2, 90))
        self.screen.blit(title_text, title_rect)
        
        #info do usuário:
        welcome_text = f"Bem-vindo {self.user_data['username']}  " + \
              ("PoliMestre" if self.user_data["user_type"] == "teacher" else "PoliGamer")

        user_text = self.text_font.render(welcome_text, True, (60, 60, 60))
        user_rect = user_text.get_rect(center=(self.width // 2, 130))
        self.screen.blit(user_text, user_rect)

        #botoes:
        for button in self.buttons:
            button.draw(self.screen)

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