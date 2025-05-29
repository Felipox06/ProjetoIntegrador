import pygame
import sys
import os
from pygame.locals import *

# Verificação de paths e imports
try:
    import config
except ImportError:
    # Definições padrão caso config.py não exista
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    COLORS = {
        "background": (235, 235, 240),
        "light_shadow": (255, 255, 255),
        "dark_shadow": (205, 205, 210),
        "accent": (106, 130, 251),
        "text": (0, 0, 0)
    }


class NeumorphicPanel:
    def __init__(self, x, y, width, height, bg_color, light_shadow, dark_shadow, border_radius=20):
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = bg_color
        self.light_shadow = light_shadow
        self.dark_shadow = dark_shadow
        self.border_radius = border_radius
   
    def draw(self, surface):
        # Desenhar retângulo principal com bordas arredondadas e contorno preto fino
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=self.border_radius)
        pygame.draw.rect(surface, config.COLORS["black"], self.rect, border_radius=self.border_radius, width=1)

       

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

        # Superfície de texto
        self.text_surf = font.render(text, True, (0, 0, 0))  # texto preto
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    def draw(self, surface):
        is_pressed = self.pressed or (self.is_toggle and self.is_active)

        # Fundo do botão (pressionado ou não)
        if is_pressed:
            inner_rect = pygame.Rect(self.rect.x + 2, self.rect.y + 2, self.rect.width - 4, self.rect.height - 4)
            pygame.draw.rect(surface, self.bg_color, inner_rect, border_radius=10)
        else:
            pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=10)

        # Borda preta fina
        pygame.draw.rect(surface, (0, 0, 0), self.rect, border_radius=10, width=1)

        # Texto (com leve deslocamento se pressionado)
        text_offset = (1, 1) if is_pressed else (0, 0)
        text_rect = self.text_surf.get_rect(center=(self.rect.centerx + text_offset[0], self.rect.centery + text_offset[1]))

        # Ajustar se tiver ícone
        if self.icon:
            text_rect.centerx += 15  # desloca texto para a direita

        surface.blit(self.text_surf, text_rect)

        # Desenhar ícone, se houver
        if self.icon:
            icon_rect = self.icon.get_rect(midright=(text_rect.left - 5, text_rect.centery))
            surface.blit(self.icon, icon_rect)

class MenuScreen:
    def __init__(self, screen, user_data):
        self.screen = screen
        self.running = True
        self.width, self.height = screen.get_size()
        self.user_data = user_data  # Contém user_type (student/teacher) e username
       
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
       
        # Painel principal - ajustado para comportar mais botões se necessário
        panel_height = 520 if self.user_data["user_type"] == "teacher" else 500
        self.main_panel = NeumorphicPanel(
            center_x - 350, 50,
            700, panel_height,
            self.accent_color, self.light_shadow, self.dark_shadow
        )
       
        # Criar botões com base no tipo de usuário
        self.buttons = self.create_buttons()
       
        # Dados simulados para testes
        self.student_data = {
            "games_played": 8,
            "last_game_date": "2025-04-15"
        }
       
    def create_buttons(self):
        buttons = []
        center_x = self.width // 2
       
       
        # Criar botões baseados no tipo de usuário
        if self.user_data["user_type"] == "student":
            # Para estudantes - apenas JOGAR e HISTÓRICO
            buttons.append(NeumorphicButton(
                center_x - 250, 180,
                500, 60,
                self.warning_color, self.light_shadow, self.dark_shadow,
                self.accent_color, "JOGAR", self.subtitle_font
            ))
           
            buttons.append(NeumorphicButton(
                center_x - 250, 270,
                500, 60,
                self.warning_color, self.light_shadow, self.dark_shadow,
                self.accent_color, "HISTÓRICO", self.subtitle_font
            ))
           
            # Botão de sair para estudantes
            buttons.append(NeumorphicButton(
                center_x - 250, 500,
                500, 40,
                (232, 77, 77), self.light_shadow, self.dark_shadow,
                 (251, 164, 31),  
                "SAIR", self.text_font
            ))
        else:
            # Para professores - todos os botões de gerenciamento
            buttons.append(NeumorphicButton(
                center_x - 250, 160,
                500, 55,
                self.warning_color, self.light_shadow, self.dark_shadow,
                self.accent_color, "JOGAR", self.subtitle_font
            ))
       
            buttons.append(NeumorphicButton(
                center_x - 250, 230,
                500, 55,
                self.warning_color, self.light_shadow, self.dark_shadow,
                self.accent_color, "GERENCIAR QUESTÕES", self.subtitle_font
            ))
       
            buttons.append(NeumorphicButton(
                center_x - 250, 300,
                500, 55,
                self.warning_color, self.light_shadow, self.dark_shadow,
                self.accent_color, "GERENCIAR TURMAS", self.subtitle_font
            ))
           
            # NOVO BOTÃO: GERENCIAR USUÁRIOS
            buttons.append(NeumorphicButton(
                center_x - 250, 370,
                500, 55,
                self.warning_color, self.light_shadow, self.dark_shadow,
                (180, 120, 255),  # Cor roxa para diferenciar
                "GERENCIAR USUÁRIOS", self.subtitle_font
            ))
           
            buttons.append(NeumorphicButton(
                center_x - 250, 440,
                500, 55,
                self.warning_color, self.light_shadow, self.dark_shadow,
                self.accent_color, "RANKING", self.subtitle_font
            ))
           
            # Botão de sair para professores
            buttons.append(NeumorphicButton(
                center_x - 250, 510,
                500, 40,
                (232, 77, 77), self.light_shadow, self.dark_shadow,
                (251, 164, 31),
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
                            elif i == 1:  # HISTÓRICO
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
        # Limpa a tela com a cor de fundo
        self.screen.fill(self.warning_color)
       
        # Desenha o painel principal
        self.main_panel.draw(self.screen)
       
        # Desenha o título
        title_text = self.title_font.render("PoliGame Show", True, (60, 60, 60))
        title_rect = title_text.get_rect(center=(self.width // 2, 90))
        self.screen.blit(title_text, title_rect)
       
        # Desenha info do usuário centralizada
        user_text = self.text_font.render(f"Bem-vindo {self.user_data['username']}", True, (60, 60, 60))
        user_rect = user_text.get_rect(midtop=(self.width // 2, 105))  # Centralizado no topo
        self.screen.blit(user_text, user_rect)

        # Desenha função do usuário também centralizada (abaixo do nome)
        role_text = self.text_font.render(
        "PoliMaster" if self.user_data["user_type"] == "teacher" else "PoliGamer",
        True, (0, 0, 0)
)
        role_rect = role_text.get_rect(midtop=(self.width // 2, user_rect.bottom + 5))  
        self.screen.blit(role_text, role_rect)

       
        # Desenha todos os botões
        for button in self.buttons:
            button.draw(self.screen)
       
        # Atualiza a tela
        pygame.display.flip()
   
    def run(self):
        while self.running:
            result = self.handle_events()
            if result["action"] != "none":
                return result
            self.update()
            self.draw()
            pygame.time.Clock().tick(60)
       
        # Retorno no caso de sair do loop por outros meios
        return {"action": "exit"}