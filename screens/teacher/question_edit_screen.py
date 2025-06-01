# screens/teacher/question_edit_screen.py
# -*- coding: utf-8 -*-

import pygame
import sys
from pygame.locals import *
from databse.data_manager import update_question_in_db
from databse.db_connector import getConnection
import mysql.connector

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

# Tentar importar componentes neumórficos do módulo de utilitários
try:
    from utils.ui_elements import NeumorphicPanel, NeumorphicButton, NeumorphicInput
except ImportError:
    # Definições das classes UI se não conseguir importar
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
                if self.cursor_timer >= 30:  # piscar a cada 30 frames
                    self.cursor_visible = not self.cursor_visible
                    self.cursor_timer = 0
                
                if self.cursor_visible:
                    cursor_x = text_rect.right + 2 if self.text else self.rect.x + 15
                    pygame.draw.line(surface, (50, 50, 50),
                                  (cursor_x, self.rect.y + 15),
                                  (cursor_x, self.rect.y + self.rect.height - 15),
                                  2)


class QuestionListItem:
    def __init__(self, x, y, width, height, bg_color, light_shadow, dark_shadow, 
                 question_id, question_text, subject, difficulty, font, is_selected=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = bg_color
        self.light_shadow = light_shadow
        self.dark_shadow = dark_shadow
        self.question_id = question_id
        self.question_text = question_text
        self.subject = subject
        self.difficulty = difficulty
        self.font = font
        self.small_font = pygame.font.SysFont('Arial', font.get_height() - 4)
        self.is_selected = is_selected
        
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
    
    def draw(self, surface):
        # Fundo do item (diferente se selecionado)
        bg_color = (220, 230, 255) if self.is_selected else self.bg_color
        
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=10)
        
        # Sombras neumórficas
        shadow_rect_light = pygame.Rect(self.rect.x-2, self.rect.y-2, self.rect.width, self.rect.height)
        pygame.draw.rect(surface, self.light_shadow, shadow_rect_light, border_radius=10, width=2)
        
        shadow_rect_dark = pygame.Rect(self.rect.x+2, self.rect.y+2, self.rect.width, self.rect.height)
        pygame.draw.rect(surface, self.dark_shadow, shadow_rect_dark, border_radius=10, width=2)
        
        # Adicionar borda especial se selecionado
        if self.is_selected:
            pygame.draw.rect(surface, COLORS.get("accent", (106, 130, 251)), 
                           self.rect, border_radius=10, width=2)
        
        # Desenhar textos
        margin = 15
        
        # ID da questão (pequeno, canto superior esquerdo)
        id_surf = self.small_font.render(f"ID: {self.question_id}", True, (100, 100, 100))
        id_rect = id_surf.get_rect(topleft=(self.rect.x + margin, self.rect.y + 10))
        surface.blit(id_surf, id_rect)
        
        # Matéria e dificuldade (canto superior direito)
        diff_color = {
            "fácil": (75, 181, 67),
            "média": (232, 181, 12),
            "difícil": (232, 77, 77)
        }.get(self.difficulty.lower(), (100, 100, 100))
        
        subject_diff_surf = self.small_font.render(f"{self.subject} | ", True, (100, 100, 100))
        diff_surf = self.small_font.render(f"{self.difficulty}", True, diff_color)
        
        # Calcular posição para o texto de matéria + dificuldade
        subject_diff_rect = subject_diff_surf.get_rect(topright=(self.rect.right - margin - diff_surf.get_width(), self.rect.y + 10))
        diff_rect = diff_surf.get_rect(topright=(self.rect.right - margin, self.rect.y + 10))
        
        surface.blit(subject_diff_surf, subject_diff_rect)
        surface.blit(diff_surf, diff_rect)
        
        # Texto da questão (principal, limitado a 2 linhas)
        lines = self._wrap_text(self.question_text, self.font, self.rect.width - margin*2)
        lines = lines[:2]  # Limitar a 2 linhas
        
        for i, line in enumerate(lines):
            text_surf = self.font.render(line, True, (50, 50, 50))
            text_rect = text_surf.get_rect(topleft=(self.rect.x + margin, self.rect.y + 35 + i*self.font.get_height()))
            surface.blit(text_surf, text_rect)
        
        # Se o texto foi truncado, adicionar "..."
        if len(self._wrap_text(self.question_text, self.font, self.rect.width - margin*2)) > 2:
            ellipsis = self.font.render("...", True, (50, 50, 50))
            surface.blit(ellipsis, (self.rect.x + margin, self.rect.y + 35 + 2*self.font.get_height()))
    
    def _wrap_text(self, text, font, max_width):
        """Quebra o texto em múltiplas linhas para caber na largura definida"""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            # Testa se adicionar a próxima palavra excederia a largura máxima
            test_line = ' '.join(current_line + [word])
            test_width, _ = font.size(test_line)
            
            if test_width <= max_width:
                current_line.append(word)
            else:
                # Se a linha atual não estiver vazia, adiciona à lista de linhas
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # Se a palavra for maior que a largura máxima, adiciona assim mesmo
                    lines.append(word)
                    current_line = []
        
        # Adiciona a última linha
        if current_line:
            lines.append(' '.join(current_line))
            
        return lines


class QuestionEditScreen:
    def __init__(self, screen, user_data):
        self.screen = screen
        self.running = True
        self.width, self.height = screen.get_size()
        self.user_data = user_data  # Contém user_type (teacher) e username
        self.center_x = self.width // 2
        
        # Cores do design neumorfista
        self.bg_color = COLORS["background"]
        self.light_shadow = COLORS["light_shadow"]
        self.dark_shadow = COLORS["dark_shadow"]
        self.accent_color = COLORS["accent"]
        
        # Usar fonte padrão do sistema
        self.title_font = pygame.font.SysFont('Arial', 32, bold=True)
        self.subtitle_font = pygame.font.SysFont('Arial', 24, bold=True)
        self.text_font = pygame.font.SysFont('Arial', 18)
        self.small_font = pygame.font.SysFont('Arial', 14)
        
        # Matérias e dificuldades disponíveis
        self.subjects = ["Matematica", "Fisica", "Biologia", "Quimica", "Historia", "Geografia", "Portugues"]
        self.difficulties = ["fácil", "média", "difícil"]
        
        # Estado da tela
        self.selected_question = None
        self.show_edit_form = False
        self.show_options_form = False
        self.current_filter = {"subject": None, "difficulty": None}
        
        # Estado do formulário de edição
        self.question_text_input = None
        self.hint_input = None
        self.selected_subject = None
        self.selected_difficulty = None
        self.option_inputs = []
        self.correct_option = None
        self.subject_buttons = []
        self.difficulty_buttons = []
        
        # Estado de mensagem
        self.message = None
        self.message_timer = 0
        
        # Para rolagem na lista
        self.scroll_offset = 0
        self.max_items_visible = 4  # Número de questões visíveis por vez
        
        # Criar elementos de UI
        self.setup_ui()
        
        # Carregar questões
        self.questions = self.load_questions()
        self.filtered_questions = self.questions.copy()
        
    def setup_ui(self):
        # Painel principal
        self.main_panel = NeumorphicPanel(
            self.center_x - 350, 20, 
            700, 560, 
            self.bg_color, self.light_shadow, self.dark_shadow
        )
        
        # Painel de filtros (aumentado para 100px de altura)
        self.filter_panel = NeumorphicPanel(
            self.center_x - 330, 70, 
            660, 100, 
            self.bg_color, self.light_shadow, self.dark_shadow,
            border_radius=15
        )
        
        # Painel da lista de questões (movido para baixo)
        self.list_panel = NeumorphicPanel(
            self.center_x - 330, 180, 
            660, 200, 
            self.bg_color, self.light_shadow, self.dark_shadow,
            border_radius=15
        )
        
        # Botões de rolagem para a lista (ajustados)
        self.scroll_up_button = NeumorphicButton(
            self.center_x + 290, 200,
            35, 35,
            self.bg_color, self.light_shadow, self.dark_shadow,
            self.accent_color, "▲", self.text_font
        )
        
        self.scroll_down_button = NeumorphicButton(
            self.center_x + 290, 320,
            35, 35,
            self.bg_color, self.light_shadow, self.dark_shadow,
            self.accent_color, "▼", self.text_font
        )
        
        # Filtro por matéria - Layout balanceado: 4 na primeira linha, 3 na segunda
        self.filter_subject_buttons = []
        button_width = 85
        button_spacing = 8
        
        # Primeira linha (4 matérias)
        first_row_count = 4
        total_width_first_row = first_row_count * button_width + (first_row_count - 1) * button_spacing
        start_x_first_row = self.center_x - total_width_first_row // 2
        
        for i in range(first_row_count):
            x = start_x_first_row + i * (button_width + button_spacing)
            y = 85
            
            button = NeumorphicButton(
                x, y,
                button_width, 25,
                self.bg_color, self.light_shadow, self.dark_shadow,
                self.accent_color, self.subjects[i], self.small_font,
                is_toggle=True, is_active=False
            )
            self.filter_subject_buttons.append(button)
        
        # Segunda linha (3 matérias restantes)
        second_row_count = len(self.subjects) - first_row_count
        total_width_second_row = second_row_count * button_width + (second_row_count - 1) * button_spacing
        start_x_second_row = self.center_x - total_width_second_row // 2
        
        for i in range(second_row_count):
            x = start_x_second_row + i * (button_width + button_spacing)
            y = 120  # Segunda linha
            
            button = NeumorphicButton(
                x, y,
                button_width, 25,
                self.bg_color, self.light_shadow, self.dark_shadow,
                self.accent_color, self.subjects[i + first_row_count], self.small_font,
                is_toggle=True, is_active=False
            )
            self.filter_subject_buttons.append(button)
        
        # Filtro por dificuldade - Posicionados à direita
        self.filter_difficulty_buttons = []
        button_colors = {
            "fácil": (75, 181, 67),  # Verde
            "média": (232, 181, 12),  # Amarelo
            "difícil": (232, 77, 77)  # Vermelho
        }
        
        diff_button_width = 70
        diff_button_spacing = 5
        diff_start_x = self.center_x + 150
        
        for i, difficulty in enumerate(self.difficulties):
            button = NeumorphicButton(
                diff_start_x, 85 + i * 30,
                diff_button_width, 25,
                self.bg_color, self.light_shadow, self.dark_shadow,
                button_colors[difficulty], difficulty, self.small_font,
                is_toggle=True, is_active=False
            )
            self.filter_difficulty_buttons.append(button)
        
        # Botão para limpar filtros - Reposicionado
        self.clear_filter_button = NeumorphicButton(
            self.center_x + 270, 85,
            40, 25,
            self.bg_color, self.light_shadow, self.dark_shadow,
            (150, 150, 150), "✕", self.small_font
        )
        
        # Painel do formulário de edição (ajustado)
        self.form_panel = NeumorphicPanel(
            self.center_x - 330, 390, 
            660, 130, 
            self.bg_color, self.light_shadow, self.dark_shadow,
            border_radius=15
        )
        
        # Botão para editar a questão selecionada
        self.edit_button = NeumorphicButton(
            self.center_x - 75, 530,
            150, 40,
            self.bg_color, self.light_shadow, self.dark_shadow,
            self.accent_color, "EDITAR", self.text_font
        )
        
        # Botão para voltar ao menu
        self.back_button = NeumorphicButton(
            self.center_x - 250, 530,
            150, 40,
            self.bg_color, self.light_shadow, self.dark_shadow,
            (232, 77, 77),  # Vermelho para botão de voltar
            "VOLTAR", self.text_font
        )
        
        # Botão para salvar alterações (inicialmente oculto)
        self.save_button = NeumorphicButton(
            self.center_x + 100, 530,
            150, 40,
            self.bg_color, self.light_shadow, self.dark_shadow,
            COLORS.get("success", (75, 181, 67)),  # Verde para salvar
            "SALVAR", self.text_font
        )
        
    def create_edit_form(self):
        """Criar formulário de edição para a questão selecionada"""
        # Campo para texto da questão (reduzido em altura)
        self.question_text_input = NeumorphicInput(
            self.center_x - 320, 410,
            640, 50,
            self.bg_color, self.light_shadow, self.dark_shadow,
            "Texto da Questão", self.text_font
        )
        self.question_text_input.text = self.selected_question["text"]
        
        # Campo para dica (reduzido)
        self.hint_input = NeumorphicInput(
            self.center_x - 320, 470,
            300, 35,
            self.bg_color, self.light_shadow, self.dark_shadow,
            "Dica para a questão", self.text_font
        )
        self.hint_input.text = self.selected_question["hint"]
        
        # Botões para matérias (reajustados)
        self.subject_buttons = []
        button_width = 70
        button_height = 25
        btn_x_start = self.center_x + 20
        btn_y = 470
        
        for i, subject in enumerate(self.subjects):
            if i > 0 and i % 4 == 0:  # 4 botões por linha
                btn_y += button_height + 5
                btn_x_start = self.center_x + 20
            
            button = NeumorphicButton(
                btn_x_start, btn_y,
                button_width, button_height,
                self.bg_color, self.light_shadow, self.dark_shadow,
                self.accent_color, subject[:4], self.small_font,  # Mostrar apenas 4 caracteres
                is_toggle=True, is_active=(subject == self.selected_question["subject"])
            )
            self.subject_buttons.append(button)
            btn_x_start += button_width + 5
            
            if subject == self.selected_question["subject"]:
                self.selected_subject = subject
        
        # Botão para editar opções
        self.edit_options_button = NeumorphicButton(
            self.center_x - 100, self.hint_input.rect.y + 40,
            200, 30,
            self.bg_color, self.light_shadow, self.dark_shadow,
            self.accent_color, "EDITAR OPÇÕES", self.small_font
        )
    
    def create_options_form(self):
        """Criar formulário para edição de opções da questão"""
        # Painel que ocupa toda a tela
        self.option_panel = NeumorphicPanel(
            20, 20, 
            self.width - 40, self.height - 40, 
            self.bg_color, self.light_shadow, self.dark_shadow
        )
        
        self.option_inputs = []
        option_height = 60
        option_spacing = 20
        option_letters = ["A", "B", "C", "D"]
        
        for i, option in enumerate(self.selected_question["options"]):
            option_input = NeumorphicInput(
                self.center_x - 300, 100 + i * (option_height + option_spacing),
                600, option_height,
                self.bg_color, self.light_shadow, self.dark_shadow,
                f"Opção {option_letters[i]}", self.text_font
            )
            option_input.text = option
            self.option_inputs.append(option_input)
        
        # Botões para selecionar alternativa correta
        self.correct_option_buttons = []
        
        for i in range(4):
            button = NeumorphicButton(
                self.center_x - 350, 100 + i * (option_height + option_spacing),
                40, 40,
                self.bg_color, self.light_shadow, self.dark_shadow,
                COLORS.get("success", (75, 181, 67)), option_letters[i], self.text_font,
                is_toggle=True, is_active=(i == self.selected_question["correct_option"])
            )
            self.correct_option_buttons.append(button)
            
            if i == self.selected_question["correct_option"]:
                self.correct_option = i
                
        last_option_bottom = 100 + 3 * (option_height + option_spacing) + option_height + 20
        
        # Botões para dificuldade
        self.difficulty_buttons = []
        button_colors = {
            "fácil": (75, 181, 67),
            "média": (232, 181, 12),
            "difícil": (232, 77, 77)
        }
        
        btn_width = 90
        btn_spacing = 10
        btn_x_start = self.center_x - 150
        btn_y = last_option_bottom
        
        for i, difficulty in enumerate(self.difficulties):
            button = NeumorphicButton(
                btn_x_start + i * (btn_width + btn_spacing), btn_y,
                btn_width, 40,
                self.bg_color, self.light_shadow, self.dark_shadow,
                button_colors[difficulty], difficulty, self.text_font,
                is_toggle=True, is_active=(difficulty == self.selected_question["difficulty"])
            )
            self.difficulty_buttons.append(button)
            
            if difficulty == self.selected_question["difficulty"]:
                self.selected_difficulty = difficulty
                
        nav_btn_y = btn_y + 60
        
        # Botão para voltar à tela principal SEM salvar
        self.back_to_main_button = NeumorphicButton(
            self.center_x - 175, nav_btn_y,
            150, 40,
            self.bg_color, self.light_shadow, self.dark_shadow,
            (232, 77, 77), "VOLTAR", self.text_font
        )
        
        # Botão para salvar e voltar à tela principal
        self.done_options_button = NeumorphicButton(
            self.center_x + 25, nav_btn_y,
            150, 40,
            self.bg_color, self.light_shadow, self.dark_shadow,
            COLORS.get("success", (75, 181, 67)), "SALVAR", self.text_font
        )
    
    def load_questions(self):
        # Carrega a lista de questões do banco de dados
        loaded_questions = []
        connection = None
        cursor = None

        # Nomes das suas tabelas e colunas - CONFIRA COM SEU SCRIPT SQL!
        # Tabela questoes
        tbl_q = "questoes"
        col_q_id = "id_questao"
        col_q_enunciado = "enunciado"       # Seu SQL tem 'enunciado TEXT'
        col_q_fk_materia = "id_materia"     # FK para materias
        col_q_fk_dificuldade = "id_dificuldade" # FK para dificuldades
        col_q_fk_serie = "id_serie"         # FK para serie (NOVO)
        col_q_alt1 = "alternativa_1"
        col_q_alt2 = "alternativa_2"
        col_q_alt3 = "alternativa_3"
        col_q_alt4 = "alternativa_4"
        col_q_idx_correta = "indice_alternativa_correta"
        col_q_explicacao = "explicacao"     # Seu SQL tem 'explicacao TEXT'

        # Tabela materias
        tbl_m = "materias"
        col_m_id_pk = "id_materia"          # PK em materias
        col_m_nome = "nome_materia"         # Nome da matéria

        # Tabela dificuldades
        tbl_d = "dificuldades"
        col_d_id_pk = "id_dificuldade"      # PK em dificuldades
        col_d_nome = "nome_dificuldade"     # Nome da dificuldade

        # Tabela serie (NOVA)
        tbl_s = "serie"
        col_s_id_pk = "id_serie"            # PK em serie
        col_s_nome = "nome_serie"           # Nome da série

        try:
            connection = getConnection() # Usa o método da classe
            if not connection:
                print("Erro (load_questions): Não foi possível conectar ao banco de dados.")
                return loaded_questions

            cursor = connection.cursor(dictionary=True) # Retorna resultados como dicionários

            query = f"""
                SELECT
                    q.{col_q_id} AS id, 
                    q.{col_q_enunciado} AS text, 
                    m.{col_m_nome} AS subject, 
                    s.{col_s_nome} AS grade,         -- Nome da série vindo da tabela 'serie'
                    d.{col_d_nome} AS difficulty, 
                    q.{col_q_alt1} AS alt1, 
                    q.{col_q_alt2} AS alt2, 
                    q.{col_q_alt3} AS alt3,
                    q.{col_q_alt4} AS alt4, 
                    q.{col_q_idx_correta} AS correct_option, 
                    q.{col_q_explicacao} AS hint      -- Mapeando 'explicacao' do DB para 'hint' na UI
                FROM
                    {tbl_q} q
                JOIN {tbl_m} m ON q.{col_q_fk_materia} = m.{col_m_id_pk}
                JOIN {tbl_d} d ON q.{col_q_fk_dificuldade} = d.{col_d_id_pk}
                JOIN {tbl_s} s ON q.{col_q_fk_serie} = s.{col_s_id_pk} -- ADICIONADO JOIN com 'serie'
                ORDER BY
                    q.{col_q_id}; 
            """
            # print(f"DEBUG SQL (load_questions): {query}") # Descomente para depuração
            cursor.execute(query)
            database_results = cursor.fetchall() # Lista de dicionários

            for row_dict in database_results:
                # As chaves em row_dict agora são os aliases definidos no SELECT (id, text, subject, etc.)
                question_dict = {
                    "id": row_dict["id"],
                    "text": row_dict["text"],
                    "subject": row_dict["subject"],
                    "grade": row_dict["grade"],       # Veio do JOIN com a tabela serie
                    "difficulty": row_dict["difficulty"],
                    "options": [row_dict["alt1"], row_dict["alt2"], row_dict["alt3"], row_dict["alt4"]],
                    "correct_option": row_dict["correct_option"],
                    "hint": row_dict["hint"] 
                }
                loaded_questions.append(question_dict)

        except mysql.connector.Error as err:
            print(f"Erro (load_questions) ao buscar questões do banco: {err}")
        except Exception as e:
            print(f"Erro inesperado (load_questions): {e}")
        finally:
            if cursor:
                try:
                    cursor.close()
                except mysql.connector.Error: pass
            if connection and connection.is_connected():
                try:
                    connection.close()
                except mysql.connector.Error: pass
        
        return loaded_questions
    
    def apply_filters(self):
        """Aplicar filtros à lista de questões"""
        self.filtered_questions = []
        
        for question in self.questions:
            # Verificar se atende aos filtros de matéria e dificuldade
            subject_match = (self.current_filter["subject"] is None or 
                            question["subject"] == self.current_filter["subject"])
            
            difficulty_match = (self.current_filter["difficulty"] is None or 
                              question["difficulty"] == self.current_filter["difficulty"])
            
            if subject_match and difficulty_match:
                self.filtered_questions.append(question)
        
        # Resetar a posição de rolagem
        self.scroll_offset = 0
        
        # Limpar a seleção atual se a questão selecionada não estiver na lista filtrada
        if self.selected_question:
            question_in_filtered = any(q["id"] == self.selected_question["id"] for q in self.filtered_questions)
            if not question_in_filtered:
                self.selected_question = None
    
    def validate_form(self):
        """Verificar se todos os campos necessários estão preenchidos"""
        # Verificar se o texto da questão foi preenchido
        if not self.question_text_input.text.strip():
            return False, "Digite o texto da questão"
            
        if self.show_options_form:
            # Verificar se as opções estão preenchidas
            for i, option_input in enumerate(self.option_inputs):
                if not option_input.text.strip():
                    return False, f"Digite o texto da opção {chr(65+i)}"
            
            # Verificar se a alternativa correta foi selecionada
            if self.correct_option is None:
                return False, "Selecione a alternativa correta"
            
            # Verificar se a dificuldade foi selecionada
            if not self.selected_difficulty:
                return False, "Selecione a dificuldade"
        else:
            # Verificar se a dica foi preenchida
            if not self.hint_input.text.strip():
                return False, "Digite a dica da questão"
                
            # Verificar se a matéria foi selecionada
            if not self.selected_subject:
                return False, "Selecione a matéria"
        
        return True, "Formulário válido"
    
    def save_edited_question(self):
        """Salva as alterações da questão editada no banco de dados."""
        is_valid, validation_message = self.validate_form()
        if not is_valid:
            self.message = validation_message
            self.message_timer = 180
            print(f"Erro de validação: {validation_message}")
            return False
        
        if not self.selected_question or "id" not in self.selected_question:
            self.message = "Nenhuma questão selecionada para editar."
            self.message_timer = 180
            print(self.message)
            return False
        
        data_for_db_update = {}

        if self.show_options_form: 
            current_options = [opt_input.text.strip() for opt_input in self.option_inputs]
            if len(current_options) != 4:
                self.message = "Erro: São necessárias 4 alternativas."
                self.message_timer = 180
                return False
            
            data_for_db_update["options"] = current_options # Chave 'options'
            data_for_db_update["correct_option"] = self.correct_option # Chave 'correct_option'
            data_for_db_update["difficulty"] = self.selected_difficulty # Chave 'difficulty' (nome)
            
            # Mantém os outros campos com os valores originais de self.selected_question
            # usando as chaves que update_question_in_db espera
            data_for_db_update["text"] = self.selected_question.get("text")
            data_for_db_update["explanation"] = self.selected_question.get("hint") # UI 'hint' -> DB 'explanation'
            data_for_db_update["subject"] = self.selected_question.get("subject") # UI 'subject' -> DB 'subject'
            data_for_db_update["grade"] = self.selected_question.get("grade")     # UI 'grade' -> DB 'grade'

        else: # Usuário está editando enunciado, dica/explicação, matéria
            data_for_db_update["text"] = self.question_text_input.text.strip() # Chave 'text'
            data_for_db_update["explanation"] = self.hint_input.text.strip()      # Chave 'explanation'
            data_for_db_update["subject"] = self.selected_subject                # Chave 'subject' (nome)
            data_for_db_update["grade"] = self.selected_question.get("grade") # Série original (nome)
            data_for_db_update["difficulty"] = self.selected_question.get("difficulty") # Dificuldade original (nome)
            data_for_db_update["options"] = list(self.selected_question.get("options", []))
            data_for_db_update["correct_option"] = self.selected_question.get("correct_option")
        
        question_id_to_update = self.selected_question["id"]

        # DEBUG: Verifique este print!
        print("DEBUG (save_edited_question): Dados sendo enviados para update_question_in_db:", data_for_db_update) 

        # --- CHAMADA REAL AO BANCO PARA ATUALIZAR ---
        try:
            # Adapte 'self.get_connection' ao seu método/função real de obter conexão
            was_successful, db_message = update_question_in_db(
                question_id_to_update,
                data_for_db_update, 
                getConnection 
            )
        except NameError as ne:
            self.message = f"Erro de configuração no código: {ne}"
            self.message_timer = 180
            print(self.message)
            return False
        except Exception as e:
            self.message = f"Erro inesperado no sistema ao salvar questão: {e}"
            self.message_timer = 180
            print(self.message)
            return False

        # Processar o resultado
        if was_successful:
            self.message = db_message 
            self.message_timer = 120
            
            print("Recarregando lista de questões após atualização...")
            self.questions = self.load_questions() 
            if hasattr(self, 'apply_filters') and callable(self.apply_filters):
                self.apply_filters() 
            elif hasattr(self, 'update_filtered_list') and callable(self.update_filtered_list):
                 self.update_filtered_list()
            
            updated_question_in_list = next((q for q in self.questions if q["id"] == question_id_to_update), None)
            if updated_question_in_list:
                self.selected_question = updated_question_in_list
            else: 
                self.selected_question = None
            
            print(f"Sucesso no DB: {db_message}")
            return True
        else:
            self.message = db_message 
            self.message_timer = 180
            print(f"Erro no DB ao atualizar questão: {db_message}")
            return False
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Se estiver na tela de edição de opções
                if self.show_options_form:
                    # Verificar cliques nos campos de entrada de opções
                    for i, option_input in enumerate(self.option_inputs):
                        if option_input.is_clicked(mouse_pos):
                            # Ativar este campo e desativar os outros
                            for j, other_input in enumerate(self.option_inputs):
                                other_input.active = (j == i)
                    
                    # Verificar cliques nos botões de alternativa correta
                    for i, button in enumerate(self.correct_option_buttons):
                        if button.is_clicked(mouse_pos):
                            # Desativar todos os outros botões
                            for j, other_button in enumerate(self.correct_option_buttons):
                                other_button.is_active = (j == i)
                            
                            self.correct_option = i
                            break
                    
                    # Verificar cliques nos botões de dificuldade
                    for i, button in enumerate(self.difficulty_buttons):
                        if button.is_clicked(mouse_pos):
                            # Desativar todos os outros botões
                            for j, other_button in enumerate(self.difficulty_buttons):
                                other_button.is_active = (j == i)
                            
                            self.selected_difficulty = self.difficulties[i]
                            break
                    
                    # Verificar clique no botão VOLTAR à tela principal
                    if self.back_to_main_button.is_clicked(mouse_pos):
                        self.back_to_main_button.pressed = True
                        self.show_options_form = False
                    
                    # Verificar clique no botão SALVAR
                    if self.done_options_button.is_clicked(mouse_pos):
                        self.done_options_button.pressed = True
                        if self.save_edited_question():
                            # Voltar para a tela de edição principal
                            self.show_options_form = False
                            self.show_edit_form = True  # Garantir que continuamos na tela de edição
                
                # Se estiver no formulário de edição principal
                elif self.show_edit_form:
                    # Verificar cliques nos campos de entrada
                    if self.question_text_input.is_clicked(mouse_pos):
                        self.question_text_input.active = True
                        self.hint_input.active = False
                    elif self.hint_input.is_clicked(mouse_pos):
                        self.question_text_input.active = False
                        self.hint_input.active = True
                    else:
                        self.question_text_input.active = False
                        self.hint_input.active = False
                    
                    # Verificar cliques nos botões de matéria
                    for i, button in enumerate(self.subject_buttons):
                        if button.is_clicked(mouse_pos):
                            # Desativar todos os outros botões de matéria
                            for j, other_button in enumerate(self.subject_buttons):
                                other_button.is_active = (j == i)
                            
                            self.selected_subject = self.subjects[i]
                            break
                    
                    # Verificar clique no botão EDITAR OPÇÕES
                    if self.edit_options_button.is_clicked(mouse_pos):
                        self.edit_options_button.pressed = True
                        if self.validate_form()[0]:  # Validar o formulário principal
                            # Salvar os dados do formulário principal
                            self.selected_question["text"] = self.question_text_input.text.strip()
                            self.selected_question["hint"] = self.hint_input.text.strip()
                            self.selected_question["subject"] = self.selected_subject
                            
                            # Abrir tela de edição de opções
                            self.show_options_form = True
                            self.create_options_form()
                        else:
                            self.message = "Preencha todos os campos antes de editar as opções"
                            self.message_timer = 180
                    
                    # Verificar clique no botão VOLTAR (sem salvar)
                    if self.back_button.is_clicked(mouse_pos):
                        self.back_button.pressed = True
                        # Voltar para o estado de seleção
                        self.show_edit_form = False
                    
                    # Verificar clique no botão SALVAR
                    if self.save_button.is_clicked(mouse_pos):
                        self.save_button.pressed = True
                        if self.save_edited_question():
                            # Voltar para o estado de seleção após salvar
                            self.show_edit_form = False
                
                # Na tela principal (lista de questões)
                else:
                    # Verificar cliques nos botões de filtro de matéria (seleção exclusiva)
                    for i, button in enumerate(self.filter_subject_buttons):
                        if button.is_clicked(mouse_pos):
                            if button.is_active:
                                # Se já está ativo, desativar (remover filtro)
                                button.is_active = False
                                self.current_filter["subject"] = None
                            else:
                                # Desativar todos os outros e ativar este
                                for j, other_button in enumerate(self.filter_subject_buttons):
                                    other_button.is_active = (j == i)
                                self.current_filter["subject"] = self.subjects[i]
                            
                            # Aplicar os filtros
                            self.apply_filters()
                            break
                    
                    # Verificar cliques nos botões de filtro de dificuldade (seleção exclusiva)
                    for i, button in enumerate(self.filter_difficulty_buttons):
                        if button.is_clicked(mouse_pos):
                            if button.is_active:
                                # Se já está ativo, desativar (remover filtro)
                                button.is_active = False
                                self.current_filter["difficulty"] = None
                            else:
                                # Desativar todos os outros e ativar este
                                for j, other_button in enumerate(self.filter_difficulty_buttons):
                                    other_button.is_active = (j == i)
                                self.current_filter["difficulty"] = self.difficulties[i]
                            
                            # Aplicar os filtros
                            self.apply_filters()
                            break
                    
                    # Verificar clique no botão de limpar filtros
                    if self.clear_filter_button.is_clicked(mouse_pos):
                        self.clear_filter_button.pressed = True
                        
                        # Resetar todos os botões de filtro
                        for button in self.filter_subject_buttons:
                            button.is_active = False
                        
                        for button in self.filter_difficulty_buttons:
                            button.is_active = False
                        
                        # Limpar os filtros
                        self.current_filter = {"subject": None, "difficulty": None}
                        self.apply_filters()
                    
                    # Verificar cliques na lista de questões
                    list_y = self.list_panel.rect.y + 20
                    item_height = 90
                    item_spacing = 10
                    
                    visible_questions = self.filtered_questions[self.scroll_offset:self.scroll_offset + self.max_items_visible]
                    for i, question in enumerate(visible_questions):
                        item_y = list_y + i * (item_height + item_spacing)
                        item_rect = pygame.Rect(
                            self.list_panel.rect.x + 20,
                            item_y,
                            self.list_panel.rect.width - 80,
                            item_height
                        )
                        
                        if item_rect.collidepoint(mouse_pos):
                            # Selecionar esta questão
                            self.selected_question = question
                            break
                
                # Verificar cliques nos botões de rolagem (sempre visíveis)
                if len(self.filtered_questions) > self.max_items_visible:
                    if self.scroll_up_button.is_clicked(mouse_pos) and self.scroll_offset > 0:
                        self.scroll_up_button.pressed = True
                        self.scroll_offset -= 1
                    
                    if self.scroll_down_button.is_clicked(mouse_pos) and self.scroll_offset < len(self.filtered_questions) - self.max_items_visible:
                        self.scroll_down_button.pressed = True
                        self.scroll_offset += 1
                
                # Verificar rolagem com roda do mouse
                if event.button == 4 and self.list_panel.rect.collidepoint(mouse_pos):  # Rolar para cima
                    if self.scroll_offset > 0:
                        self.scroll_offset -= 1
                        
                elif event.button == 5 and self.list_panel.rect.collidepoint(mouse_pos):  # Rolar para baixo
                    if self.scroll_offset < len(self.filtered_questions) - self.max_items_visible:
                        self.scroll_offset += 1
                
                # Verificar clique no botão EDITAR
                if not self.show_options_form and not self.show_edit_form:
                    if self.edit_button.is_clicked(mouse_pos) and self.selected_question:
                        self.edit_button.pressed = True
                        self.show_edit_form = True
                        self.create_edit_form()
                    
                    # Verificar clique no botão VOLTAR
                    if self.back_button.is_clicked(mouse_pos):
                        self.back_button.pressed = True
                        return {"action": "back_to_menu"}
            
            # Lidar com entrada de texto se algum campo estiver ativo
            if event.type == KEYDOWN:
                # Verificar se estamos na tela de edição de opções
                if self.show_options_form:
                    # Processar entrada para os campos de opções
                    for option_input in self.option_inputs:
                        if option_input.active:
                            if event.key == K_BACKSPACE:
                                option_input.text = option_input.text[:-1]
                            else:
                                option_input.text += event.unicode
                
                # Verificar se estamos no formulário de edição principal
                elif self.show_edit_form:
                    # Processar entrada para o campo de texto da questão
                    if self.question_text_input.active:
                        if event.key == K_BACKSPACE:
                            self.question_text_input.text = self.question_text_input.text[:-1]
                        else:
                            self.question_text_input.text += event.unicode
                    
                    # Processar entrada para o campo de dica
                    elif self.hint_input.active:
                        if event.key == K_BACKSPACE:
                            self.hint_input.text = self.hint_input.text[:-1]
                        else:
                            self.hint_input.text += event.unicode
        
        return {"action": "none"}
    
    def update(self):
        # Resetar estado dos botões
        self.edit_button.pressed = False
        self.back_button.pressed = False
        self.scroll_up_button.pressed = False
        self.scroll_down_button.pressed = False
        self.clear_filter_button.pressed = False
        
        if self.show_edit_form:
            if hasattr(self, 'edit_options_button'):
                self.edit_options_button.pressed = False
            
            if hasattr(self, 'save_button'):
                self.save_button.pressed = False
        
        if self.show_options_form:
            if hasattr(self, 'back_to_main_button'):
                self.back_to_main_button.pressed = False
            
            if hasattr(self, 'done_options_button'):
                self.done_options_button.pressed = False
        
        # Atualizar temporizador de mensagem
        if self.message_timer > 0:
            self.message_timer -= 1
            if self.message_timer == 0:
                self.message = None
    
    def draw(self):
        # Limpa a tela com a cor de fundo
        self.screen.fill(self.bg_color)
        
        # Se estiver na tela de edição de opções, desenhar apenas essa tela
        if self.show_options_form:
            # Desenha o painel principal
            self.option_panel.draw(self.screen)
            
            # Desenha o título
            title_text = self.title_font.render("Editar Opções", True, (60, 60, 60))
            title_rect = title_text.get_rect(center=(self.center_x, 45))
            self.screen.blit(title_text, title_rect)
            
            # Desenha os campos de entrada para as opções
            for i, option_input in enumerate(self.option_inputs):
                option_input.draw(self.screen)
                
                # Desenha o rótulo da opção
                letter = chr(65 + i)  # A, B, C, D
                option_label = self.subtitle_font.render(letter, True, (80, 80, 80))
                option_rect = option_label.get_rect(midright=(option_input.rect.x - 10, option_input.rect.y + option_input.rect.height // 2))
                self.screen.blit(option_label, option_rect)
            
            # Desenha os botões de alternativa correta
            for button in self.correct_option_buttons:
                button.draw(self.screen)
            
            # Desenha os botões de dificuldade
            for button in self.difficulty_buttons:
                button.draw(self.screen)
            
            # Desenha os botões de navegação
            self.back_to_main_button.draw(self.screen)
            self.done_options_button.draw(self.screen)
            
            # Desenha instruções
            instruct1 = self.small_font.render("Selecione a alternativa correta:", True, (80, 80, 80))
            instruct1_rect = instruct1.get_rect(bottomleft=(self.center_x - 330, self.option_inputs[0].rect.y - 10))
            self.screen.blit(instruct1, instruct1_rect)
            
            instruct2 = self.small_font.render("Selecione a dificuldade:", True, (80, 80, 80))
            instruct2_rect = instruct2.get_rect(bottomleft=(self.difficulty_buttons[0].rect.x, self.difficulty_buttons[0].rect.y - 10))
            self.screen.blit(instruct2, instruct2_rect)
        
        else:
            # Desenha o painel principal
            self.main_panel.draw(self.screen)
            
            # Desenha o título
            title_text = self.title_font.render("Editar Questões", True, (60, 60, 60))
            title_rect = title_text.get_rect(center=(self.center_x, 45))
            self.screen.blit(title_text, title_rect)
            
            # Desenha o painel de filtros
            self.filter_panel.draw(self.screen)
            
            # Desenha o painel da lista de questões
            self.list_panel.draw(self.screen)
            
            # Desenha os botões de filtro
            for button in self.filter_subject_buttons:
                button.draw(self.screen)
            
            for button in self.filter_difficulty_buttons:
                button.draw(self.screen)
            
            # Desenha o botão de limpar filtros
            self.clear_filter_button.draw(self.screen)
            
            # Desenha os rótulos para os filtros
            subject_label = self.small_font.render("Filtrar por matéria:", True, (80, 80, 80))
            subject_rect = subject_label.get_rect(bottomleft=(self.center_x - 170, 82))
            self.screen.blit(subject_label, subject_rect)
            
            difficulty_label = self.small_font.render("Dificuldade:", True, (80, 80, 80))
            difficulty_rect = difficulty_label.get_rect(bottomleft=(self.center_x + 150, 82))
            self.screen.blit(difficulty_label, difficulty_rect)
            
            # Contador de questões
            count_text = f"{len(self.filtered_questions)} de {len(self.questions)} questões"
            count_surf = self.small_font.render(count_text, True, (100, 100, 100))
            count_rect = count_surf.get_rect(topright=(self.center_x + 250, 145))
            self.screen.blit(count_surf, count_rect)
            
            # Desenha a lista de questões
            if len(self.filtered_questions) == 0:
                # Mensagem se não houver questões
                no_questions_text = self.text_font.render("Nenhuma questão encontrada", True, (100, 100, 100))
                no_questions_rect = no_questions_text.get_rect(center=(self.list_panel.rect.centerx, self.list_panel.rect.centery))
                self.screen.blit(no_questions_text, no_questions_rect)
            else:
                # Desenha as questões visíveis
                list_y = self.list_panel.rect.y + 20
                item_height = 90
                item_spacing = 10
                
                visible_questions = self.filtered_questions[self.scroll_offset:self.scroll_offset + self.max_items_visible]
                for i, question in enumerate(visible_questions):
                    item_y = list_y + i * (item_height + item_spacing)
                    
                    # Verifica se a questão está selecionada
                    is_selected = self.selected_question and self.selected_question["id"] == question["id"]
                    
                    question_list_item = QuestionListItem(
                        self.list_panel.rect.x + 20,
                        item_y,
                        self.list_panel.rect.width - 80,
                        item_height,
                        self.bg_color,
                        self.light_shadow,
                        self.dark_shadow,
                        question["id"],
                        question["text"],
                        question["subject"],
                        question["difficulty"],
                        self.text_font,
                        is_selected
                    )
                    question_list_item.draw(self.screen)
                
                # Desenha indicadores de rolagem se houver mais itens
                if len(self.filtered_questions) > self.max_items_visible:
                    self.scroll_up_button.draw(self.screen)
                    self.scroll_down_button.draw(self.screen)
            
            # Se o formulário de edição estiver aberto, desenha-o
            if self.show_edit_form and self.selected_question:
                # Desenha o painel do formulário
                self.form_panel.draw(self.screen)
                
                # Desenha o título do formulário
                form_title = self.subtitle_font.render(f"Editar Questão #{self.selected_question['id']}", True, (60, 60, 60))
                form_title_rect = form_title.get_rect(midtop=(self.center_x, self.form_panel.rect.y + 10))
                self.screen.blit(form_title, form_title_rect)
                
                # Desenha os campos de edição
                self.question_text_input.draw(self.screen)
                self.hint_input.draw(self.screen)
                
                # Desenha os rótulos
                hint_label = self.small_font.render("Dica:", True, (80, 80, 80))
                hint_rect = hint_label.get_rect(bottomleft=(self.hint_input.rect.x, self.hint_input.rect.y - 5))
                self.screen.blit(hint_label, hint_rect)
                
                subject_label = self.small_font.render("Matéria:", True, (80, 80, 80))
                subject_rect = subject_label.get_rect(bottomleft=(self.subject_buttons[0].rect.x, self.subject_buttons[0].rect.y - 5))
                self.screen.blit(subject_label, subject_rect)
                
                # Desenha os botões de matéria
                for button in self.subject_buttons:
                    button.draw(self.screen)
                
                # Desenha o botão para editar opções
                self.edit_options_button.draw(self.screen)
                
                # Desenha os botões de salvar e voltar
                self.back_button.draw(self.screen)
                self.save_button.draw(self.screen)
            else:
                # Desenha o botão de editar (ativo apenas se uma questão estiver selecionada)
                if self.selected_question:
                    self.edit_button.draw(self.screen)
                else:
                    # Versão desativada do botão
                    disabled_button = NeumorphicButton(
                        self.edit_button.rect.x, self.edit_button.rect.y,
                        self.edit_button.rect.width, self.edit_button.rect.height,
                        self.bg_color, self.light_shadow, self.dark_shadow,
                        (180, 180, 180),  # Cinza para botão desativado
                        "EDITAR", self.text_font
                    )
                    disabled_button.draw(self.screen)
                    
                    # Mensagem de dica
                    hint_text = self.small_font.render("Selecione uma questão para editar", True, (120, 120, 120))
                    hint_rect = hint_text.get_rect(midtop=(self.edit_button.rect.centerx, self.edit_button.rect.bottom + 5))
                    self.screen.blit(hint_text, hint_rect)
                
                # Desenha o botão de voltar
                self.back_button.draw(self.screen)
        
        # Desenha mensagem de feedback, se houver
        if self.message:
            message_color = COLORS.get("success", (75, 181, 67)) if "sucesso" in self.message else COLORS.get("error", (232, 77, 77))
            message_surf = self.text_font.render(self.message, True, message_color)
            message_rect = message_surf.get_rect(midbottom=(self.center_x, self.height - 10))
            self.screen.blit(message_surf, message_rect)
        
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