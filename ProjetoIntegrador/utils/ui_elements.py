# utils/ui_elements.py

import pygame
import pygame.gfxdraw
from pygame.locals import *

class NeumorphicPanel:
    def __init__(self, x, y, width, height, bg_color, light_shadow, dark_shadow, border_radius=20):
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = bg_color
        self.light_shadow = light_shadow
        self.dark_shadow = dark_shadow
        self.border_radius = border_radius
    
    def draw(self, surface):
        # Criar superfícies para sombras
        shadow_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        
        # Desenhar retângulo principal com bordas arredondadas
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=self.border_radius)
        
        # Desenhar sombra clara (superior esquerda)
        pygame.draw.rect(shadow_surface, (*self.light_shadow, 128), 
                         pygame.Rect(0, 0, self.rect.width, self.rect.height), 
                         border_radius=self.border_radius)
        pygame.draw.rect(shadow_surface, (0, 0, 0, 0), 
                         pygame.Rect(3, 3, self.rect.width-6, self.rect.height-6), 
                         border_radius=self.border_radius)
        surface.blit(shadow_surface, (self.rect.x-3, self.rect.y-3))
        
        # Desenhar sombra escura (inferior direita)
        shadow_surface.fill((0, 0, 0, 0))
        pygame.draw.rect(shadow_surface, (*self.dark_shadow, 128), 
                         pygame.Rect(0, 0, self.rect.width, self.rect.height), 
                         border_radius=self.border_radius)
        pygame.draw.rect(shadow_surface, (0, 0, 0, 0), 
                         pygame.Rect(3, 3, self.rect.width-6, self.rect.height-6), 
                         border_radius=self.border_radius)
        surface.blit(shadow_surface, (self.rect.x+3, self.rect.y+3))

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
        self.hover = False
        
        # Preparar superfície de texto
        self.text_surf = font.render(text, True, (50, 50, 50))
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)
    
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
    
    def draw(self, surface):
        # Determinar se o botão está pressionado (visualmente)
        is_pressed = self.pressed or (self.is_toggle and self.is_active)
        
        # Criar superfícies para sombras
        button_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        
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
            
            # Desenhar sombra clara (superior esquerda)
            pygame.draw.rect(button_surface, (*self.light_shadow, 128), 
                           pygame.Rect(0, 0, self.rect.width, self.rect.height), 
                           border_radius=10)
            pygame.draw.rect(button_surface, (0, 0, 0, 0), 
                           pygame.Rect(2, 2, self.rect.width-4, self.rect.height-4), 
                           border_radius=8)
            surface.blit(button_surface, (self.rect.x-2, self.rect.y-2))
            
            # Desenhar sombra escura (inferior direita)
            button_surface.fill((0, 0, 0, 0))
            pygame.draw.rect(button_surface, (*self.dark_shadow, 128), 
                           pygame.Rect(0, 0, self.rect.width, self.rect.height), 
                           border_radius=10)
            pygame.draw.rect(button_surface, (0, 0, 0, 0), 
                           pygame.Rect(2, 2, self.rect.width-4, self.rect.height-4), 
                           border_radius=8)
            surface.blit(button_surface, (self.rect.x+2, self.rect.y+2))
            
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
        
        # Criar superfícies para sombras internas (invertidas)
        input_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        
        # Desenhar sombra escura (superior esquerda - invertida)
        pygame.draw.rect(input_surface, (*self.dark_shadow, 128), 
                       pygame.Rect(0, 0, self.rect.width, self.rect.height), 
                       border_radius=10)
        pygame.draw.rect(input_surface, (0, 0, 0, 0), 
                       pygame.Rect(2, 2, self.rect.width-4, self.rect.height-4), 
                       border_radius=8)
        surface.blit(input_surface, (self.rect.x-2, self.rect.y-2))
        
        # Desenhar sombra clara (inferior direita - invertida)
        input_surface.fill((0, 0, 0, 0))
        pygame.draw.rect(input_surface, (*self.light_shadow, 128), 
                       pygame.Rect(0, 0, self.rect.width, self.rect.height), 
                       border_radius=10)
        pygame.draw.rect(input_surface, (0, 0, 0, 0), 
                       pygame.Rect(2, 2, self.rect.width-4, self.rect.height-4), 
                       border_radius=8)
        surface.blit(input_surface, (self.rect.x+2, self.rect.y+2))
        
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