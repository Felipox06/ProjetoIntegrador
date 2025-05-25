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
        "accent": (27, 185, 185),
        "text": (0, 0, 0),
        "success": (75, 181, 67),
        "warning": (251, 164, 31),
        "error": (232, 77, 77),
        "black": (0, 0, 0),
    }

# Classes para elementos de UI neumórficos
class NeumorphicPanel:
    def __init__(self, x, y, width, height, bg_color, light_shadow, dark_shadow, border_radius=20):
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = bg_color
        self.light_shadow = light_shadow
        self.dark_shadow = dark_shadow
        self.border_radius = border_radius

        self.bg_color = COLORS["background"]
        self.warning_color = COLORS["warning"]
        self.light_shadow = COLORS["light_shadow"]
        self.dark_shadow = COLORS["dark_shadow"]
        self.accent_color = COLORS["accent"]
    
    def draw(self, surface):
        # Desenhar retângulo principal com bordas arredondadas
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=self.border_radius)


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
            # Borda preta externa
            pygame.draw.rect(surface, (0, 0, 0), self.rect.inflate(4, 4), border_radius=12)

            # Botão em si
            pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=10)

            # Desenhar texto
            surface.blit(self.text_surf, self.text_rect)

class QuestionManagementScreen:
    def __init__(self, screen, user_data):
        self.screen = screen
        self.running = True
        self.width, self.height = screen.get_size()
        self.user_data = user_data  # Contém user_type (teacher) e username
        
        # Cores do design neumorfista
        self.bg_color = COLORS["background"]
        self.warning_color = COLORS["warning"]
        self.light_shadow = COLORS["light_shadow"]
        self.dark_shadow = COLORS["dark_shadow"]
        self.accent_color = COLORS["accent"]

        # Usar fonte padrão do sistema
        self.title_font = pygame.font.SysFont('Arial', 36, bold=True)
        self.subtitle_font = pygame.font.SysFont('Arial', 24, bold=True)
        self.text_font = pygame.font.SysFont('Arial', 18)
        
        # Criar elementos de UI
        self.setup_ui()
        
    def setup_ui(self):
        center_x = self.width // 2
        
        # Painel principal
        self.main_panel = NeumorphicPanel(
            center_x - 350, 50, 
            700, 500, 
            self.accent_color, self.light_shadow, self.dark_shadow
        )
        
        # Painel de opções de gerenciamento
        self.options_panel = NeumorphicPanel(
            center_x - 300, 150, 
            600, 280, 
            self.warning_color, self.light_shadow, self.dark_shadow,
            border_radius=15
        )
        
        # Botões de ações para questões
        btn_width = 500
        btn_height = 60
        btn_spacing = 30
        
        # Botão CRIAR
        self.create_button = NeumorphicButton(
            center_x - btn_width//2, 180,
            btn_width, btn_height,
            self.warning_color, self.light_shadow, self.dark_shadow,
            COLORS.get("success", (75, 181, 67)),  # Verde para criar
            "CRIAR NOVA QUESTÃO", self.subtitle_font
        )
        
        # Botão EDITAR
        self.edit_button = NeumorphicButton(
            center_x - btn_width//2, 180 + btn_height + btn_spacing,
            btn_width, btn_height,
            self.warning_color, self.light_shadow, self.dark_shadow,
            self.accent_color,  # Azul para editar
            "EDITAR QUESTÃO EXISTENTE", self.subtitle_font
        )
        
        # Botão REMOVER
        self.remove_button = NeumorphicButton(
            center_x - btn_width//2, 180 + 2 * (btn_height + btn_spacing),
            btn_width, btn_height,
            self.warning_color, self.light_shadow, self.dark_shadow,
            COLORS.get("error", (232, 77, 77)),  # Vermelho para remover
            "REMOVER QUESTÃO", self.subtitle_font
        )
        
        # Botão para voltar ao menu
        self.back_button = NeumorphicButton(
            center_x - 75, 470,
            150, 40,
            self.warning_color, self.light_shadow, self.dark_shadow,
            (232, 77, 77),  # Vermelho para botão de voltar
            "VOLTAR", self.text_font
        )
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Verificar clique no botão de CRIAR
                if self.create_button.is_clicked(mouse_pos):
                    self.create_button.pressed = True
                    return {"action": "create_question"}
                
                # Verificar clique no botão de EDITAR
                if self.edit_button.is_clicked(mouse_pos):
                    self.edit_button.pressed = True
                    return {"action": "edit_question"}
                
                # Verificar clique no botão de REMOVER
                if self.remove_button.is_clicked(mouse_pos):
                    self.remove_button.pressed = True
                    return {"action": "remove_question"}
                
                # Verificar clique no botão de VOLTAR
                if self.back_button.is_clicked(mouse_pos):
                    self.back_button.pressed = True
                    return {"action": "back_to_menu"}
        
        return {"action": "none"}
    
    def update(self):
        # Redefinir estado dos botões
        self.create_button.pressed = False
        self.edit_button.pressed = False
        self.remove_button.pressed = False
        self.back_button.pressed = False
    
    def draw(self):
        # Limpa a tela com a cor de fundo
        self.screen.fill(self.warning_color)
        # Caixa ao redor de todos os elementos (borda preta)
        margin = 40
        pygame.draw.rect(
            self.screen, 
            (0, 0, 0), 
        pygame.Rect(margin, margin, self.width - 2 * margin, self.height - 2 * margin),
        width=3,  # Espessura da borda
        border_radius=25
)
       
        # Desenha o painel principal
        self.main_panel.draw(self.screen)
        
        # Desenha o título
        title_text = self.title_font.render("Gerenciamento de Questões", True, (60, 60, 60))
        title_rect = title_text.get_rect(center=(self.width // 2, 90))
        self.screen.blit(title_text, title_rect)
        
        # Desenha o painel de opções
        self.options_panel.draw(self.screen)
        
        # Desenha os botões de ações
        self.create_button.draw(self.screen)
        self.edit_button.draw(self.screen)
        self.remove_button.draw(self.screen)
        
        # Desenha o botão de voltar
        self.back_button.draw(self.screen)
        
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