import pygame
import sys
from pygame.locals import *

# Matérias e séries padrão sem acentos
DEFAULT_SUBJECTS = [
    "Matematica", 
    "Fisica", 
    "Biologia", 
    "Quimica", 
    "Historia", 
    "Geografia", 
    "Portugues"
]
DEFAULT_GRADE_LEVELS = ["1 Ano", "2 Ano", "3 Ano"]
DIFFICULTY_LEVELS = ["Facil", "Medio", "Dificil"]

# Importar config se existir
try:
    import config
    COLORS = config.COLORS
    # Tentar obter SUBJECTS e GRADE_LEVELS, ou usar valores padrão
    try:
        SUBJECTS = config.SUBJECTS
    except (AttributeError, UnicodeDecodeError):
        print("Usando matérias padrão")
        SUBJECTS = DEFAULT_SUBJECTS
    
    try:
        GRADE_LEVELS = config.GRADE_LEVELS
    except (AttributeError, UnicodeDecodeError):
        print("Usando séries padrão")
        GRADE_LEVELS = DEFAULT_GRADE_LEVELS
    
except ImportError:
    print("Arquivo config.py não encontrado. Usando configurações padrão.")
    COLORS = {
        "background": (30, 180, 195),     
        "light_shadow": (255, 255, 255), 
        "dark_shadow": (20, 140, 150),    
        "accent": (27, 185, 185),    
        "text": (0, 0, 0),
       "warning": (251, 164, 31),
        "black": (0, 0, 0)}       
    
SUBJECTS = DEFAULT_SUBJECTS
GRADE_LEVELS = DEFAULT_GRADE_LEVELS

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

        pygame.draw.rect(surface, (0, 0, 0), self.rect, width=1, border_radius=self.border_radius)

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
            # Estado normal: fundo e contorno preto fino
            pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=10)
            pygame.draw.rect(surface, COLORS["black"], self.rect, border_radius=10, width=1)

            surface.blit(self.text_surf, self.text_rect)

class GameConfigScreen:
    def __init__(self, screen, user_data):
        self.screen = screen
        self.running = True
        self.width, self.height = screen.get_size()
        self.user_data = user_data  
        
        # Cores
        self.bg_color = COLORS["background"]
        self.warning_color = COLORS["warning"]
        self.light_shadow = COLORS["light_shadow"]
        self.dark_shadow = COLORS["dark_shadow"]
        self.accent_color = COLORS["accent"]
        
        # Usar fonte padrão do sistema
        self.title_font = pygame.font.SysFont('Arial', 36, bold=True)
        self.subtitle_font = pygame.font.SysFont('Arial', 24, bold=True)
        self.text_font = pygame.font.SysFont('Arial', 18)
        
        # Configurações selecionadas
        self.selected_subject = None
        self.selected_grade = None
        self.selected_difficulty = None
        
        # Criar elementos de UI
        center_x = self.width // 2
        
        # Painel principal
        self.main_panel = NeumorphicPanel(
            center_x - 350, 50, 
            700, 500, 
            self.accent_color, self.light_shadow, self.dark_shadow
        )
        
        # Criar botões para matérias
        self.subject_buttons = self.create_subject_buttons()
        
        # Criar botões para séries (anos)
        self.grade_buttons = self.create_grade_buttons()

        # Novo: Criar botões para dificuldade
        self.difficulty_buttons = self.create_difficulty_buttons()
        
        # Botões de navegação
        self.start_button = NeumorphicButton(
            center_x + 50, 520,
            200, 50,
            self.warning_color, self.light_shadow, self.dark_shadow,
            (75, 181, 67),  # Verde
            "INICIAR", self.subtitle_font
        )
        
        self.back_button = NeumorphicButton(
            center_x - 250, 520,
            200, 50,
            self.warning_color, self.light_shadow, self.dark_shadow,
            (232, 77, 77),  # Vermelho
            "VOLTAR", self.subtitle_font
        )

    def create_subject_buttons(self):
        buttons = []
        center_x = self.width // 2
        
        # Botões para matérias (layout em grade 4x2)
        button_width = 150
        button_height = 50
        margin_x = 20
        margin_y = 15
        start_x = center_x - (button_width * 2 + margin_x/2)
        start_y = 180
        
        for i, subject in enumerate(SUBJECTS):
            row = i // 4
            col = i % 4
            
            x = start_x + col * (button_width + margin_x)
            y = start_y + row * (button_height + margin_y)
            
            buttons.append(NeumorphicButton(
                x, y,
                button_width, button_height,
                self.warning_color, self.light_shadow, self.dark_shadow,
                self.warning_color, subject, self.text_font,
                is_toggle=True, is_active=False
            ))
            
        return buttons
    
    def create_grade_buttons(self):
        buttons = []
        center_x = self.width // 2
        
        # Botões para séries (layout horizontal)
        button_width = 150
        button_height = 50
        margin_x = 20
        start_x = center_x - (button_width * 1.5 + margin_x)
        start_y = 350
        
        for i, grade in enumerate(GRADE_LEVELS):
            x = start_x + i * (button_width + margin_x)
            
            buttons.append(NeumorphicButton(
                x, start_y,
                button_width, button_height,
                self.warning_color, self.light_shadow, self.dark_shadow,
                self.warning_color, grade, self.text_font,
                is_toggle=True, is_active=False
            ))
            
        return buttons
    
    def create_difficulty_buttons(self):
        buttons = []
        center_x = self.width // 2

    # Botões para dificuldade (layout horizontal)
        button_width = 150
        button_height = 50
        margin_x = 20
        start_x = center_x - (button_width * 1.5 + margin_x)
        start_y = 450  

        for i, difficulty in enumerate(DIFFICULTY_LEVELS):
            x = start_x + i * (button_width + margin_x)
        
            buttons.append(NeumorphicButton(
            x, start_y,
            button_width, button_height,
            self.warning_color, self.light_shadow, self.dark_shadow,
            self.warning_color, difficulty, self.text_font,
            is_toggle=True, is_active=False))
        return buttons
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Verificar cliques nos botões de matéria
                for i, button in enumerate(self.subject_buttons):
                    if button.is_clicked(mouse_pos):
                        # Desativar todos os outros botões de matéria
                        for j, other_button in enumerate(self.subject_buttons):
                            other_button.is_active = (j == i)
                        
                        self.selected_subject = SUBJECTS[i]
                        break
                
                # Verificar cliques nos botões de série
                for i, button in enumerate(self.grade_buttons):
                    if button.is_clicked(mouse_pos):
                        # Desativar todos os outros botões de série
                        for j, other_button in enumerate(self.grade_buttons):
                            other_button.is_active = (j == i)
                        
                        self.selected_grade = GRADE_LEVELS[i]
                        break
                
                # Novo: Verificar cliques nos botões de dificuldade
                for i, button in enumerate(self.difficulty_buttons):
                    if button.is_clicked(mouse_pos):
                        # Desativar todos os outros botões de dificuldade
                        for j, other_button in enumerate(self.difficulty_buttons):
                            other_button.is_active = (j == i)
                        
                        self.selected_difficulty = DIFFICULTY_LEVELS[i]
                        break

                # Verificar clique no botão INICIAR
                if self.start_button.is_clicked(mouse_pos):
                    self.start_button.pressed = True
                    
                    # Verificar se ambas as opções foram selecionadas
                    if self.start_button.is_clicked(mouse_pos):
                        self.start_button.pressed = True
                    if self.selected_subject and self.selected_grade:
                        return {
                            "action": "start_game",
                            "subject": self.selected_subject,
                            "grade": self.selected_grade,
                            "difficulty": self.selected_difficulty 
                        }
                
                # Verificar clique no botão VOLTAR
                if self.back_button.is_clicked(mouse_pos):
                    self.back_button.pressed = True
                    return {"action": "back_to_menu"}
        
        return {"action": "none"}
    
    def update(self):
        # Redefinir estado dos botões
        self.start_button.pressed = False
        self.back_button.pressed = False
    
    def draw(self):
        # Limpa a tela com a cor de fundo
        self.screen.fill(self.warning_color)
        
        # Desenha o painel principal
        self.main_panel.draw(self.screen)
        
        # Desenha o título
        title_text = self.title_font.render("Configurar Jogo", True, (60, 60, 60))
        title_rect = title_text.get_rect(center=(self.width // 2, 90))
        self.screen.blit(title_text, title_rect)
        
        # Desenha subtítulo para matérias
        subject_text = self.subtitle_font.render("Selecione a Materia:", True, (60, 60, 60))
        subject_rect = subject_text.get_rect(center=(self.width // 2, 150))
        self.screen.blit(subject_text, subject_rect)
        
        # Desenha botões de matéria
        for button in self.subject_buttons:
            button.draw(self.screen)
        
        # Desenha subtítulo para séries
        grade_text = self.subtitle_font.render("Selecione a Serie:", True, (60, 60, 60))
        grade_rect = grade_text.get_rect(center=(self.width // 2, 320))
        self.screen.blit(grade_text, grade_rect)
        
        # Desenha botões de série
        for button in self.grade_buttons:
            button.draw(self.screen)

        # Novo: Desenha subtítulo para dificuldade
        difficulty_text = self.subtitle_font.render("Dificuldade:", True, (60, 60, 60))
        difficulty_rect = difficulty_text.get_rect(center=(self.width // 2, 420))
        self.screen.blit(difficulty_text, difficulty_rect)

        # Novo: Desenha botões de dificuldade
        for button in self.difficulty_buttons:
            button.draw(self.screen)
        
        # Desenha botões de navegação
        self.start_button.draw(self.screen)
        self.back_button.draw(self.screen)
        
        # Mensagem de ajuda para o botão iniciar
        if not (self.selected_subject and self.selected_grade):
            hint_text = self.text_font.render("Selecione uma materia e uma serie para iniciar", True, (150, 150, 150))
            hint_rect = hint_text.get_rect(center=(self.width // 2, 510))
            self.screen.blit(hint_text, hint_rect)
        
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