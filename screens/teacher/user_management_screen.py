# screens/teacher/user_management_screen.py
# -*- coding: utf-8 -*-

import pygame
import sys
from pygame.locals import *

# Importar config se existir
try:
    import config
    COLORS = config.COLORS
except ImportError:
    print("Arquivo config.py não encontrado. Usando configurações padrão.")
    COLORS = {
        "background": (235, 235, 240),
        "light_shadow": (255, 255, 255),
        "dark_shadow": (205, 205, 210),
        "accent": (106, 130, 251),
        "text": (60, 60, 60),
        "success": (75, 181, 67),
        "warning": (232, 181, 12),
        "error": (232, 77, 77)
    }

# Classes para componentes de UI neumórficos
class NeumorphicPanel:
    def __init__(self, x, y, width, height, bg_color, light_shadow, dark_shadow, border_radius=20):
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = bg_color
        self.light_shadow = light_shadow
        self.dark_shadow = dark_shadow
        self.border_radius = border_radius
    
    def draw(self, surface):
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=self.border_radius)
        shadow_rect_light = pygame.Rect(self.rect.x-3, self.rect.y-3, self.rect.width, self.rect.height)
        pygame.draw.rect(surface, self.light_shadow, shadow_rect_light, border_radius=self.border_radius, width=3)
        shadow_rect_dark = pygame.Rect(self.rect.x+3, self.rect.y+3, self.rect.width, self.rect.height)
        pygame.draw.rect(surface, self.dark_shadow, shadow_rect_dark, border_radius=self.border_radius, width=3)

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
        
        self.text_surf = font.render(text, True, (50, 50, 50))
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)
    
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
    
    def draw(self, surface):
        is_pressed = self.pressed or (self.is_toggle and self.is_active)
        
        if is_pressed:
            pygame.draw.rect(surface, self.bg_color, 
                           pygame.Rect(self.rect.x+2, self.rect.y+2, self.rect.width-4, self.rect.height-4), 
                           border_radius=10)
            pygame.draw.rect(surface, self.accent_color, 
                           self.rect, border_radius=10, width=2)
            text_rect = self.text_surf.get_rect(center=(self.rect.centerx+1, self.rect.centery+1))
            surface.blit(self.text_surf, text_rect)
        else:
            pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=10)
            shadow_rect_light = pygame.Rect(self.rect.x-2, self.rect.y-2, self.rect.width, self.rect.height)
            pygame.draw.rect(surface, self.light_shadow, shadow_rect_light, border_radius=10, width=2)
            shadow_rect_dark = pygame.Rect(self.rect.x+2, self.rect.y+2, self.rect.width, self.rect.height)
            pygame.draw.rect(surface, self.dark_shadow, shadow_rect_dark, border_radius=10, width=2)
            surface.blit(self.text_surf, self.text_rect)

class UserManagementScreen:
    def __init__(self, screen, user_data):
        self.screen = screen
        self.running = True
        self.width, self.height = screen.get_size()
        self.user_data = user_data
        self.center_x = self.width // 2
        
        self.bg_color = COLORS["background"]
        self.light_shadow = COLORS["light_shadow"]
        self.dark_shadow = COLORS["dark_shadow"]
        self.accent_color = COLORS["accent"]
        
        self.title_font = pygame.font.SysFont('Arial', 36, bold=True)
        self.subtitle_font = pygame.font.SysFont('Arial', 28, bold=True)
        self.text_font = pygame.font.SysFont('Arial', 18)
        self.small_font = pygame.font.SysFont('Arial', 16)
        
        self.setup_ui()
        
    def setup_ui(self):
        self.main_panel = NeumorphicPanel(
            self.center_x - 350, 50, 
            700, 500, 
            self.bg_color, self.light_shadow, self.dark_shadow
        )
        
        self.description_panel = NeumorphicPanel(
            self.center_x - 320, 120, 
            640, 100, 
            self.bg_color, self.light_shadow, self.dark_shadow,
            border_radius=15
        )
        
        button_width = 450
        button_height = 70
        button_spacing = 25
        start_y = 250
        
        self.add_button = NeumorphicButton(
            self.center_x - button_width // 2, start_y,
            button_width, button_height,
            self.bg_color, self.light_shadow, self.dark_shadow,
            COLORS.get("success", (75, 181, 67)),
            "ADICIONAR USUARIOS", self.subtitle_font
        )
        
        self.edit_button = NeumorphicButton(
            self.center_x - button_width // 2, start_y + button_height + button_spacing,
            button_width, button_height,
            self.bg_color, self.light_shadow, self.dark_shadow,
            COLORS.get("warning", (232, 181, 12)),
            "EDITAR USUARIOS", self.subtitle_font
        )
        
        self.remove_button = NeumorphicButton(
            self.center_x - button_width // 2, start_y + 2 * (button_height + button_spacing),
            button_width, button_height,
            self.bg_color, self.light_shadow, self.dark_shadow,
            COLORS.get("error", (232, 77, 77)),
            "REMOVER USUARIOS", self.subtitle_font
        )
        
        self.back_button = NeumorphicButton(
            self.center_x - 150, 490,
            300, 50,
            self.bg_color, self.light_shadow, self.dark_shadow,
            (180, 180, 180),
            "VOLTAR AO MENU", self.text_font
        )
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                return {"action": "exit"}
                
            if event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                if self.add_button.is_clicked(mouse_pos):
                    print("Clicou em ADICIONAR USUARIOS")
                    return {"action": "add_users"}
                
                if self.edit_button.is_clicked(mouse_pos):
                    print("Clicou em EDITAR USUARIOS")
                    return {"action": "edit_users"}
                
                if self.remove_button.is_clicked(mouse_pos):
                    print("Clicou em REMOVER USUARIOS")
                    return {"action": "remove_users"}
                
                if self.back_button.is_clicked(mouse_pos):
                    self.back_button.pressed = True
                    return {"action": "back_to_menu"}
        
        return {"action": "none"}
    
    def update(self):
        pass
    
    def draw(self):
        self.screen.fill(self.bg_color)
        self.main_panel.draw(self.screen)
        self.description_panel.draw(self.screen)
        
        title_text = self.title_font.render("Gerenciamento de Usuarios", True, (60, 60, 60))
        title_rect = title_text.get_rect(center=(self.center_x, 75))
        self.screen.blit(title_text, title_rect)
        
        description_lines = [
            "Escolha uma das opcoes abaixo para gerenciar os usuarios do sistema:",
            "• Adicionar: Cadastrar novos alunos ou professores",
            "• Editar: Modificar informacoes de usuarios existentes",
            "• Remover: Excluir usuarios do sistema"
        ]
        
        line_height = self.small_font.get_height() + 4
        start_y = 140
        
        for i, line in enumerate(description_lines):
            if i == 0:
                line_surf = self.text_font.render(line, True, (60, 60, 60))
            else:
                line_surf = self.small_font.render(line, True, (80, 80, 80))
            
            line_rect = line_surf.get_rect(centerx=self.center_x, y=start_y + i * line_height)
            self.screen.blit(line_surf, line_rect)
        
        self.add_button.draw(self.screen)
        self.edit_button.draw(self.screen)
        self.remove_button.draw(self.screen)
        self.back_button.draw(self.screen)
        
        user_info = f"Logado como: {self.user_data['username']} (Professor)"
        user_surf = self.small_font.render(user_info, True, (120, 120, 120))
        user_rect = user_surf.get_rect(bottomright=(self.width - 20, self.height - 10))
        self.screen.blit(user_surf, user_rect)
        
        pygame.display.flip()
    
    def run(self):
        clock = pygame.time.Clock()
        
        while self.running:
            result = self.handle_events()
            
            # Se qualquer ação diferente de "none" for retornada, sair do loop
            if result["action"] != "none":
                self.running = False
                return result
            
            self.update()
            self.draw()
            clock.tick(60)
        
        return {"action": "exit"}