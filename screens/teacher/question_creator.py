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
DEFAULT_DIFFICULTY_LEVELS = ["Facil", "Medio", "Dificil"]

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
    
    try:
        DIFFICULTY_LEVELS = config.DIFFICULTY_LEVELS
    except (AttributeError, UnicodeDecodeError):
        print("Usando níveis de dificuldade padrão")
        DIFFICULTY_LEVELS = DEFAULT_DIFFICULTY_LEVELS
    
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
    SUBJECTS = DEFAULT_SUBJECTS
    GRADE_LEVELS = DEFAULT_GRADE_LEVELS
    DIFFICULTY_LEVELS = DEFAULT_DIFFICULTY_LEVELS

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
    # Adicionar borda preta fina ao redor do painel
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
            # Estado normal: efeito neumórfico
            pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=10)

            # Desenhar contorno preto fino
            pygame.draw.rect(surface, (0, 0, 0), self.rect, width=1, border_radius=10)

            # Desenhar texto
            surface.blit(self.text_surf, self.text_rect)

class NeumorphicInput:
    def __init__(self, x, y, width, height, bg_color, light_shadow, dark_shadow, 
                 placeholder, font, multiline=False, max_length=100):
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = bg_color
        self.light_shadow = light_shadow
        self.dark_shadow = dark_shadow
        self.placeholder = placeholder
        self.font = font
        self.multiline = multiline
        self.max_length = max_length
        self.text = ""
        self.active = False
        self.highlight_color = None  # Cor para destacar (usado para alternativa correta)
        
        # Cursor piscante
        self.cursor_visible = True
        self.cursor_timer = 0
        
        # Para campos multiline
        self.lines = [""]
        self.current_line = 0
    
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
    
    def add_text(self, text):
        if not self.multiline:
            if len(self.text) < self.max_length:
                self.text += text
        else:
            # Para campos multiline
            if len(self.lines[self.current_line]) < self.max_length:
                self.lines[self.current_line] += text
    
    def backspace(self):
        if not self.multiline:
            self.text = self.text[:-1]
        else:
            # Para campos multiline
            if self.lines[self.current_line]:
                self.lines[self.current_line] = self.lines[self.current_line][:-1]
            elif self.current_line > 0:
                self.lines.pop(self.current_line)
                self.current_line -= 1
    
    def new_line(self):
        if self.multiline:
            self.lines.insert(self.current_line + 1, "")
            self.current_line += 1
    
    def get_text(self):
        if not self.multiline:
            return self.text
        else:
            return "\n".join(self.lines)
    
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
        
        # Se tiver uma cor de destaque, desenhar uma borda adicional
        if self.highlight_color:
            highlight_rect = pygame.Rect(self.rect.x-4, self.rect.y-4, self.rect.width+8, self.rect.height+8)
            pygame.draw.rect(surface, self.highlight_color, highlight_rect, border_radius=12, width=2)
        
        # Desenhar linha de destaque se ativo
        if self.active:
            pygame.draw.line(surface, (120, 120, 255), 
                           (self.rect.x + 15, self.rect.y + self.rect.height - 8),
                           (self.rect.x + self.rect.width - 15, self.rect.y + self.rect.height - 8),
                           2)
        
        # Exibir texto ou placeholder
        if not self.multiline:
            if self.text:
                text_surface = self.font.render(self.text, True, (50, 50, 50))
            else:
                text_surface = self.font.render(self.placeholder, True, (150, 150, 150))
            
            text_rect = text_surface.get_rect(midleft=(self.rect.x + 15, self.rect.y + self.rect.height // 2))
            surface.blit(text_surface, text_rect)
            
            # Desenhar cursor piscante se ativo
            if self.active and self.cursor_visible:
                cursor_x = text_rect.right + 2 if self.text else self.rect.x + 15
                pygame.draw.line(surface, (50, 50, 50),
                               (cursor_x, self.rect.y + 15),
                               (cursor_x, self.rect.y + self.rect.height - 15),
                               2)
        else:
            # Renderizar texto multilinha
            if any(line for line in self.lines):
                y_offset = self.rect.y + 15
                for i, line in enumerate(self.lines):
                    if line:
                        text_surface = self.font.render(line, True, (50, 50, 50))
                        text_rect = text_surface.get_rect(topleft=(self.rect.x + 15, y_offset))
                        surface.blit(text_surface, text_rect)
                    
                    # Cursor na linha atual
                    if self.active and self.cursor_visible and i == self.current_line:
                        if line:
                            cursor_x = self.rect.x + 15 + self.font.size(line)[0]
                        else:
                            cursor_x = self.rect.x + 15
                        
                        pygame.draw.line(surface, (50, 50, 50),
                                       (cursor_x, y_offset),
                                       (cursor_x, y_offset + self.font.get_height()),
                                       2)
                    
                    y_offset += self.font.get_height() + 5
            else:
                # Mostrar placeholder
                text_surface = self.font.render(self.placeholder, True, (150, 150, 150))
                text_rect = text_surface.get_rect(topleft=(self.rect.x + 15, self.rect.y + 15))
                surface.blit(text_surface, text_rect)
                
                # Cursor no placeholder
                if self.active and self.cursor_visible:
                    pygame.draw.line(surface, (50, 50, 50),
                                   (self.rect.x + 15, self.rect.y + 15),
                                   (self.rect.x + 15, self.rect.y + 15 + self.font.get_height()),
                                   2)
        
        # Atualizar timer do cursor
        self.cursor_timer += 1
        if self.cursor_timer >= 30:  # piscar a cada 30 frames (aproximadamente 0.5s em 60fps)
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

class QuestionEditor:
    def __init__(self, screen, user_data):
        self.screen = screen
        self.running = True
        self.width, self.height = screen.get_size()
        self.user_data = user_data  # Contém user_type (teacher) e username
        
        # Cores do design neumorfista
        self.bg_color = COLORS["background"]
        self.light_shadow = COLORS["light_shadow"]
        self.dark_shadow = COLORS["dark_shadow"]
        self.accent_color = COLORS["accent"]
        self.success_color = COLORS.get("success", (75, 181, 67))  # Verde para alternativa correta
        
        # Usar fonte padrão do sistema
        self.title_font = pygame.font.SysFont('Arial', 32, bold=True)
        self.subtitle_font = pygame.font.SysFont('Arial', 24, bold=True)
        self.text_font = pygame.font.SysFont('Arial', 18)
        self.small_font = pygame.font.SysFont('Arial', 14)
        
        # Estado da edição
        self.selected_subject = None
        self.selected_grade = None
        self.selected_difficulty = None
        self.correct_option = None  # Índice da alternativa correta (0-3)
        
        # Estado do formulário
        self.error_message = None
        self.success_message = None
        self.message_timer = 0
        
        # Criar elementos de UI
        self.setup_ui()
    
    def setup_ui(self):
        center_x = self.width // 2
        
        # Painel principal (ajustado para garantir que caiba na tela)
        self.main_panel = NeumorphicPanel(
            20, 20, 
            self.width - 40, self.height - 40, 
            self.bg_color, self.light_shadow, self.dark_shadow
        )
        
        # Redimensionar e reposicionar os painéis para evitar sobreposição
        left_panel_width = self.width * 0.3  # 30% da largura da tela
        right_panel_width = self.width * 0.65  # 65% da largura da tela
        
        # Painéis de configuração (lado esquerdo - mais estreito)
        self.config_panel = NeumorphicPanel(
            40, 80, 
            left_panel_width - 20, self.height - 120, 
            self.bg_color, self.light_shadow, self.dark_shadow
        )
        
        # Painel do editor (lado direito - mais largo)
        self.editor_panel = NeumorphicPanel(
            left_panel_width + 40, 80, 
            right_panel_width - 60, self.height - 120, 
            self.bg_color, self.light_shadow, self.dark_shadow
        )
        
        # Botões para matérias (layout em duas colunas)
        self.subject_buttons = []
        btn_width = (left_panel_width - 60) / 2  # Dividir em duas colunas
        btn_height = 40
        btn_spacing = 10
        
        # Organizar em 2 colunas
        for i, subject in enumerate(SUBJECTS):
            col = i % 2  # 0 ou 1 (coluna)
            row = i // 2  # linha
            
            btn_x = 60 + col * (btn_width + 10)
            btn_y = 140 + row * (btn_height + btn_spacing)
            
            button = NeumorphicButton(
                btn_x, btn_y,
                btn_width, btn_height,
                self.bg_color, self.light_shadow, self.dark_shadow,
                self.accent_color, subject, self.text_font,
                is_toggle=True, is_active=False
            )
            self.subject_buttons.append(button)
        
        # Calcular a posição vertical para os próximos elementos
        grade_y_start = 140 + ((len(SUBJECTS) + 1) // 2) * (btn_height + btn_spacing) + 20
        
        # Título para a seção de séries
        self.grade_section_y = grade_y_start
        
        # Botões para séries (anos) - layout horizontal
        self.grade_buttons = []
        grade_btn_width = (left_panel_width - 60) / len(GRADE_LEVELS) - 5
        grade_y = grade_y_start + 30
        
        for i, grade in enumerate(GRADE_LEVELS):
            btn_x = 60 + i * (grade_btn_width + 10)
            
            button = NeumorphicButton(
                btn_x, grade_y,
                grade_btn_width, btn_height,
                self.bg_color, self.light_shadow, self.dark_shadow,
                self.accent_color, grade, self.text_font,
                is_toggle=True, is_active=False
            )
            self.grade_buttons.append(button)
        
        # Calcular posição para a seção de dificuldade
        difficulty_y_start = grade_y + btn_height + 30
        self.difficulty_section_y = difficulty_y_start
        
        # Botões para níveis de dificuldade - layout horizontal
        self.difficulty_buttons = []
        diff_btn_width = (left_panel_width - 60) / len(DIFFICULTY_LEVELS) - 5
        diff_y = difficulty_y_start + 30
        
        for i, difficulty in enumerate(DIFFICULTY_LEVELS):
            btn_x = 60 + i * (diff_btn_width + 10)
            
            button = NeumorphicButton(
                btn_x, diff_y,
                diff_btn_width, btn_height,
                self.bg_color, self.light_shadow, self.dark_shadow,
                self.accent_color, difficulty, self.text_font,
                is_toggle=True, is_active=False
            )
            self.difficulty_buttons.append(button)
        
        # Campos do editor (lado direito) - ajustados para o novo painel
        editor_x = left_panel_width + 60
        editor_width = right_panel_width - 100
        
        # Coordenadas iniciais para o editor
        question_y = 120
        options_y = 230
        option_height = 45
        option_spacing = 10
        last_option_bottom = options_y + 4 * (option_height + option_spacing)
        explanation_y = last_option_bottom + 30  # 30px de espaço após a última alternativa

        
        # Campo para o enunciado da pergunta
        self.question_input = NeumorphicInput(
            editor_x, question_y,
            editor_width, 90,
            self.bg_color, self.light_shadow, self.dark_shadow,
            "Digite o enunciado da pergunta...", self.text_font,
            multiline=True, max_length=300
        )
        
        # Campos para as alternativas (A, B, C, D)
        self.option_inputs = []
        option_labels = ["A", "B", "C", "D"]
        option_height = 45
        option_spacing = 10
        
        for i in range(4):
            option = NeumorphicInput(
                editor_x, options_y + i * (option_height + option_spacing),
                editor_width, option_height,
                self.bg_color, self.light_shadow, self.dark_shadow,
                f"Digite a alternativa {option_labels[i]}...", self.text_font,
                max_length=200
            )
            self.option_inputs.append(option)
        
        # Campo para explicação da resposta
        self.explanation_input = NeumorphicInput(
            editor_x, explanation_y,
            editor_width, 60,
            self.bg_color, self.light_shadow, self.dark_shadow,
            "Digite uma breve explicação da resposta correta...", self.text_font,
            multiline=True, max_length=300
        )
        
        # Botões para salvar e cancelar - bem posicionados no fundo da tela
        button_width = 150
        button_height = 50
        button_y = self.height - 80
        
        # Botão CANCELAR à esquerda
        self.cancel_button = NeumorphicButton(
            center_x - button_width - 20, button_y - -25,
            button_width, button_height,
            self.bg_color, self.light_shadow, self.dark_shadow,
            COLORS.get("error", (232, 77, 77)), "CANCELAR", self.subtitle_font
        )
        
        # Botão SALVAR à direita
        self.save_button = NeumorphicButton(
            center_x + 20, button_y - -25,
            button_width, button_height,
            self.bg_color, self.light_shadow, self.dark_shadow,
            self.success_color, "SALVAR", self.subtitle_font
        )
        
        # Botões para selecionar a resposta correta - reposicionados
        self.correct_option_buttons = []
        correct_btn_width = 30
        correct_btn_height = 30
        correct_btn_x = editor_x - 40  # Antes do campo de alternativa
        
        for i in range(4):
            y_pos = options_y + i * (option_height + option_spacing) + (option_height // 2) - (correct_btn_height // 2)
            button = NeumorphicButton(
                correct_btn_x, y_pos,
                correct_btn_width, correct_btn_height,
                self.bg_color, self.light_shadow, self.dark_shadow,
                self.success_color, "", self.small_font,
                is_toggle=True, is_active=False
            )
            self.correct_option_buttons.append(button)
    
    def validate_form(self):
        """Verificar se todos os campos necessários estão preenchidos"""
        # Verificar se matéria, série e dificuldade foram selecionadas
        if not all([self.selected_subject, self.selected_grade, self.selected_difficulty]):
            return False, "Selecione matéria, série e dificuldade"
        
        # Verificar se o enunciado foi preenchido
        if not self.question_input.get_text().strip():
            return False, "Digite o enunciado da pergunta"
        
        # Verificar se todas as alternativas foram preenchidas
        for i, option in enumerate(self.option_inputs):
            if not option.text.strip():
                return False, f"Preencha a alternativa {chr(65+i)}"
        
        # Verificar se uma alternativa correta foi selecionada
        if self.correct_option is None:
            return False, "Selecione a alternativa correta"
        
        # Verificar se a explicação foi preenchida
        if not self.explanation_input.get_text().strip():
            return False, "Digite uma explicação para a resposta"
        
        return True, "Formulário válido"
    
    def prepare_question_data(self):
        """Preparar dados da questão para salvar no banco de dados"""
        question_data = {
            "subject": self.selected_subject,
            "grade": self.selected_grade,
            "difficulty": self.selected_difficulty,
            "text": self.question_input.get_text().strip(),
            "options": [option.text.strip() for option in self.option_inputs],
            "correct_option": self.correct_option,
            "explanation": self.explanation_input.get_text().strip()
        }
        return question_data
    
    def save_question(self):
        """Salvar a questão no banco de dados (simulação)"""
        is_valid, message = self.validate_form()
        if not is_valid:
            # Mostrar mensagem de erro
            self.error_message = message
            self.message_timer = 180  # 3 segundos a 60 FPS
            print(f"Erro ao salvar: {message}")
            return False
        
        # Preparar dados da questão
        question_data = self.prepare_question_data()
        
        # Simulação de salvamento (para futura integração com o banco de dados)
        # Na implementação real, aqui seria a chamada ao modelo para salvar no banco
        print(f"Questão salva com sucesso: {question_data}")
        
        # Exibir mensagem de sucesso
        self.success_message = "Questão salva com sucesso!"
        self.message_timer = 120  # 2 segundos a 60 FPS
        
        # Limpar o formulário após salvar
        self.clear_form()
        
        return True
    
    def clear_form(self):
        """Limpar todos os campos do formulário"""
        # Limpar seleções
        self.selected_subject = None
        self.selected_grade = None
        self.selected_difficulty = None
        self.correct_option = None
        
        # Resetar botões de toggle
        for button in self.subject_buttons:
            button.is_active = False
        
        for button in self.grade_buttons:
            button.is_active = False
        
        for button in self.difficulty_buttons:
            button.is_active = False
            
        for button in self.correct_option_buttons:
            button.is_active = False
        
        # Limpar inputs
        self.question_input.text = ""
        self.question_input.lines = [""]
        self.question_input.current_line = 0
        
        for option in self.option_inputs:
            option.text = ""
            
        self.explanation_input.text = ""
        self.explanation_input.lines = [""]
        self.explanation_input.current_line = 0
        
        # Limpar destaque verde da opção correta
        for option in self.option_inputs:
            option.highlight_color = None
    
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
                
                # Verificar cliques nos botões de dificuldade
                for i, button in enumerate(self.difficulty_buttons):
                    if button.is_clicked(mouse_pos):
                        # Desativar todos os outros botões de dificuldade
                        for j, other_button in enumerate(self.difficulty_buttons):
                            other_button.is_active = (j == i)
                        
                        self.selected_difficulty = DIFFICULTY_LEVELS[i]
                        break
                
                # Verificar cliques nos campos de texto
                if self.question_input.is_clicked(mouse_pos):
                    self.question_input.active = True
                    self.explanation_input.active = False
                    for option in self.option_inputs:
                        option.active = False
                elif self.explanation_input.is_clicked(mouse_pos):
                    self.explanation_input.active = True
                    self.question_input.active = False
                    for option in self.option_inputs:
                        option.active = False
                else:
                    option_clicked = False
                    for i, option in enumerate(self.option_inputs):
                        if option.is_clicked(mouse_pos):
                            option.active = True
                            self.question_input.active = False
                            self.explanation_input.active = False
                            
                            # Desativar outras opções
                            for j, other_option in enumerate(self.option_inputs):
                                if j != i:
                                    other_option.active = False
                            
                            option_clicked = True
                            break
                    
                    if not option_clicked:
                        self.question_input.active = False
                        self.explanation_input.active = False
                        for option in self.option_inputs:
                            option.active = False
                
                # Verificar cliques nos botões para selecionar a resposta correta
                for i, button in enumerate(self.correct_option_buttons):
                    if button.is_clicked(mouse_pos):
                        # Desativar todos os outros botões de resposta correta
                        for j, other_button in enumerate(self.correct_option_buttons):
                            other_button.is_active = (j == i)
                        
                        # Marcar a alternativa correta
                        self.correct_option = i
                        
                        # Destacar visualmente a alternativa selecionada
                        for j, option in enumerate(self.option_inputs):
                            option.highlight_color = self.success_color if j == i else None
                        
                        break
                
                # Verificar clique no botão SALVAR
                if self.save_button.is_clicked(mouse_pos):
                    self.save_button.pressed = True
                    saved = self.save_question()
                    if saved:
                        # Só retornamos para o menu após alguns frames, para mostrar a mensagem de sucesso
                        if not self.success_message:
                            return {"action": "question_saved"}
                
                # Verificar clique no botão CANCELAR
                if self.cancel_button.is_clicked(mouse_pos):
                    self.cancel_button.pressed = True
                    # Retornar diretamente para o menu
                    return {"action": "back_to_menu"}
            
            # Lidar com entrada de texto
            if event.type == KEYDOWN:
                # Processar entrada para o campo de enunciado
                if self.question_input.active:
                    if event.key == K_BACKSPACE:
                        self.question_input.backspace()
                    elif event.key == K_RETURN:
                        self.question_input.new_line()
                    elif event.unicode:
                        self.question_input.add_text(event.unicode)
                
                # Processar entrada para o campo de explicação
                elif self.explanation_input.active:
                    if event.key == K_BACKSPACE:
                        self.explanation_input.backspace()
                    elif event.key == K_RETURN:
                        self.explanation_input.new_line()
                    elif event.unicode:
                        self.explanation_input.add_text(event.unicode)
                
                # Processar entrada para os campos de alternativas
                else:
                    for option in self.option_inputs:
                        if option.active:
                            if event.key == K_BACKSPACE:
                                option.backspace()
                            elif event.unicode:
                                option.add_text(event.unicode)
        
        return {"action": "none"}
    
    def update(self):
        # Resetar estado dos botões
        self.save_button.pressed = False
        self.cancel_button.pressed = False
        
        # Atualizar temporizador de mensagens
        if self.message_timer > 0:
            self.message_timer -= 1
            if self.message_timer == 0:
                self.error_message = None
                self.success_message = None
                
                # Se a mensagem de sucesso acabou de desaparecer, retornar ao menu
                if self.success_message:
                    return {"action": "question_saved"}
        
        return {"action": "none"}
    
    def draw(self):
        # Limpa a tela com a cor de fundo
        self.screen.fill(self.bg_color)
        
        # Desenha os painéis principais
        self.main_panel.draw(self.screen)
        self.config_panel.draw(self.screen)
        self.editor_panel.draw(self.screen)
        
        # Desenha o título
        title_text = self.title_font.render("Editor de Perguntas", True, (60, 60, 60))
        title_rect = title_text.get_rect(center=(self.width // 2, 50))
        self.screen.blit(title_text, title_rect)
        
        # Desenha subtítulos para configuração
        subject_text = self.subtitle_font.render("Matéria:", True, (60, 60, 60))
        subject_rect = subject_text.get_rect(topleft=(60, 100))
        self.screen.blit(subject_text, subject_rect)
        
        grade_text = self.subtitle_font.render("Série:", True, (60, 60, 60))
        grade_rect = grade_text.get_rect(topleft=(60, self.grade_section_y))
        self.screen.blit(grade_text, grade_rect)
        
        difficulty_text = self.subtitle_font.render("Dificuldade:", True, (60, 60, 60))
        difficulty_rect = difficulty_text.get_rect(topleft=(60, self.difficulty_section_y))
        self.screen.blit(difficulty_text, difficulty_rect)
        
        # Desenha subtítulos para o editor
        question_text = self.subtitle_font.render("Enunciado:", True, (60, 60, 60))
        question_rect = question_text.get_rect(topleft=(self.question_input.rect.x, self.question_input.rect.y - 30))
        self.screen.blit(question_text, question_rect)
        
        options_text = self.subtitle_font.render("Alternativas:", True, (60, 60, 60))
        options_rect = options_text.get_rect(topleft=(self.option_inputs[0].rect.x, self.option_inputs[0].rect.y - 30))
        self.screen.blit(options_text, options_rect)
        
        correct_text = self.subtitle_font.render("", True, (60, 60, 60))
        correct_rect = correct_text.get_rect(topleft=(self.correct_option_buttons[0].rect.x - 15, self.option_inputs[0].rect.y - 10))
        correct_rect.centerx = self.correct_option_buttons[0].rect.centerx
        self.screen.blit(correct_text, correct_rect)
        
        explanation_text = self.subtitle_font.render("Explicação:", True, (60, 60, 60))
        explanation_rect = explanation_text.get_rect(topleft=(self.explanation_input.rect.x, self.explanation_input.rect.y - 30))
        self.screen.blit(explanation_text, explanation_rect)
        
        # Desenha botões de matéria
        for button in self.subject_buttons:
            button.draw(self.screen)
        
        # Desenha botões de série
        for button in self.grade_buttons:
            button.draw(self.screen)
        
        # Desenha botões de dificuldade
        for button in self.difficulty_buttons:
            button.draw(self.screen)
        
        # Desenha campos de entrada
        self.question_input.draw(self.screen)
        
        # Desenha campos de alternativas
        option_labels = ["A", "B", "C", "D"]
        for i, option in enumerate(self.option_inputs):
            # Desenhar rótulo da alternativa
            label_surf = self.text_font.render(f"{option_labels[i]})", True, (80, 80, 80))
            label_x = option.rect.x - 25
            label_y = option.rect.y + (option.rect.height // 2) - 10
            self.screen.blit(label_surf, (label_x, label_y))
            
            # Desenhar campo de entrada
            option.draw(self.screen)
        
        # Desenha botões de seleção de resposta correta
        for button in self.correct_option_buttons:
            button.draw(self.screen)
        
        # Desenha campo de explicação
        self.explanation_input.draw(self.screen)
        
        # Desenha botões de salvar e cancelar
        self.save_button.draw(self.screen)
        self.cancel_button.draw(self.screen)
        
        # Desenha mensagens de erro ou sucesso, se existirem
        if self.error_message:
            error_surf = self.text_font.render(self.error_message, True, COLORS.get("error", (232, 77, 77)))
            error_rect = error_surf.get_rect(center=(self.width // 2, self.height - 120))
            self.screen.blit(error_surf, error_rect)
        
        if self.success_message:
            success_surf = self.text_font.render(self.success_message, True, COLORS.get("success", (75, 181, 67)))
            success_rect = success_surf.get_rect(center=(self.width // 2, self.height - 120))
            self.screen.blit(success_surf, success_rect)
        
        # Atualiza a tela
        pygame.display.flip()
    
    def run(self):
        while self.running:
            result = self.handle_events()
            
            # Se recebemos uma ação de navegação, retornamos imediatamente
            if result["action"] != "none":
                return result
            
            # Atualizamos o estado da tela e verificamos se há novas ações
            update_result = self.update()
            if update_result["action"] != "none":
                return update_result
            
            # Desenhamos a tela
            self.draw()
            
            # Controlamos a taxa de quadros
            pygame.time.Clock().tick(60)
        
        # Retorno no caso de sair do loop por outros meios
        return {"action": "exit"}