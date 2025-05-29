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
        "text": (60, 60, 60)
    }

# Classes base para componentes neumórficos (podem ser movidas para utils/ui_elements.py posteriormente)
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
       
        # Preparar superfície de texto
        self.text_surf = font.render(text, True, (50, 50, 50))
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)
       
        # Se tiver ícone, ajustar posição do texto
        if self.icon:
            self.text_rect.centerx += 15
   
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
            if self.icon:
                text_rect.centerx += 15
            surface.blit(self.text_surf, text_rect)
           
            # Desenhar ícone se existir
            if self.icon:
                icon_rect = self.icon.get_rect(midright=(text_rect.left-5, text_rect.centery))
                surface.blit(self.icon, icon_rect)
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
           
            # Desenhar ícone se existir
            if self.icon:
                icon_rect = self.icon.get_rect(midright=(self.text_rect.left-5, self.text_rect.centery))
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
        except (AttributeError, NameError):
            self.bg_color = (235, 235, 240)
            self.light_shadow = (255, 255, 255)
            self.dark_shadow = (205, 205, 210)
            self.accent_color = (106, 130, 251)
       
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
            self.bg_color, self.light_shadow, self.dark_shadow
        )
       
        # Criar botões com base no tipo de usuário
        self.buttons = self.create_buttons()
       
        # Dados simulados para testes
        self.student_data = {
            "money": 5000,
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
                self.bg_color, self.light_shadow, self.dark_shadow,
                self.accent_color, "JOGAR", self.subtitle_font
            ))
           
            buttons.append(NeumorphicButton(
                center_x - 250, 270,
                500, 60,
                self.bg_color, self.light_shadow, self.dark_shadow,
                self.accent_color, "HISTÓRICO", self.subtitle_font
            ))
           
            # Botão de sair para estudantes
            buttons.append(NeumorphicButton(
                center_x - 250, 500,
                500, 40,
                self.bg_color, self.light_shadow, self.dark_shadow,
                (232, 77, 77),  # Vermelho para botão de sair
                "SAIR", self.text_font
            ))
        else:
            # Para professores - todos os botões de gerenciamento
            buttons.append(NeumorphicButton(
                center_x - 250, 160,
                500, 55,
                self.bg_color, self.light_shadow, self.dark_shadow,
                self.accent_color, "JOGAR", self.subtitle_font
            ))
       
            buttons.append(NeumorphicButton(
                center_x - 250, 230,
                500, 55,
                self.bg_color, self.light_shadow, self.dark_shadow,
                self.accent_color, "GERENCIAR QUESTÕES", self.subtitle_font
            ))
       
            buttons.append(NeumorphicButton(
                center_x - 250, 300,
                500, 55,
                self.bg_color, self.light_shadow, self.dark_shadow,
                self.accent_color, "GERENCIAR TURMAS", self.subtitle_font
            ))
           
            # NOVO BOTÃO: GERENCIAR USUÁRIOS
            buttons.append(NeumorphicButton(
                center_x - 250, 370,
                500, 55,
                self.bg_color, self.light_shadow, self.dark_shadow,
                (180, 120, 255),  # Cor roxa para diferenciar
                "GERENCIAR USUÁRIOS", self.subtitle_font
            ))
           
            buttons.append(NeumorphicButton(
                center_x - 250, 440,
                500, 55,
                self.bg_color, self.light_shadow, self.dark_shadow,
                self.accent_color, "RANKING", self.subtitle_font
            ))
           
            # Botão de sair para professores
            buttons.append(NeumorphicButton(
                center_x - 250, 510,
                500, 40,
                self.bg_color, self.light_shadow, self.dark_shadow,
                (232, 77, 77),  # Vermelho para botão de sair
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
        self.screen.fill(self.bg_color)
       
        # Desenha o painel principal
        self.main_panel.draw(self.screen)
       
        # Desenha o título
        title_text = self.title_font.render("Quiz do Milhão", True, (60, 60, 60))
        title_rect = title_text.get_rect(center=(self.width // 2, 90))
        self.screen.blit(title_text, title_rect)
       
        # Desenha info do usuário
        user_text = self.text_font.render(f"Bem-vindo, {self.user_data['username']}!", True, (60, 60, 60))
        user_rect = user_text.get_rect(topright=(self.width - 70, 65))
        self.screen.blit(user_text, user_rect)
       
        role_text = self.text_font.render(
            "Professor" if self.user_data["user_type"] == "teacher" else "Aluno",
            True, (120, 120, 120)
        )
        role_rect = role_text.get_rect(topright=(self.width - 70, 90))
        self.screen.blit(role_text, role_rect)
       
        # Para alunos, mostrar dinheiro acumulado
        if self.user_data["user_type"] == "student":
            money_text = self.text_font.render(f"R$ {self.student_data['money']:,}", True, (50, 150, 50))
            money_rect = money_text.get_rect(topleft=(70, 90))
            self.screen.blit(money_text, money_rect)
       
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