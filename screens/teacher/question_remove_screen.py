# screens/teacher/question_remove_screen.py
# -*- coding: utf-8 -*-

import pygame
import sys
from pygame.locals import *

# Importar config se existir
try:
    import config
    COLORS = config.COLORS
    # Tentar obter SUBJECTS e GRADE_LEVELS, ou usar valores padrão
    try:
        SUBJECTS = config.SUBJECTS
    except (AttributeError, UnicodeDecodeError):
        print("Usando matérias padrão")
        SUBJECTS = ["Matematica", "Fisica", "Biologia", "Quimica", "Historia", "Geografia", "Portugues"]
    
    try:
        GRADE_LEVELS = config.GRADE_LEVELS
    except (AttributeError, UnicodeDecodeError):
        print("Usando séries padrão")
        GRADE_LEVELS = ["1 Ano", "2 Ano", "3 Ano"]
    
    try:
        DIFFICULTY_LEVELS = config.DIFFICULTY_LEVELS
    except (AttributeError, UnicodeDecodeError):
        print("Usando níveis de dificuldade padrão")
        DIFFICULTY_LEVELS = ["Facil", "Medio", "Dificil"]
    
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
    SUBJECTS = ["Matematica", "Fisica", "Biologia", "Quimica", "Historia", "Geografia", "Portugues"]
    GRADE_LEVELS = ["1 Ano", "2 Ano", "3 Ano"]
    DIFFICULTY_LEVELS = ["Facil", "Medio", "Dificil"]

# Classes de componentes da UI
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

class QuestionListItem:
    def __init__(self, x, y, width, height, bg_color, light_shadow, dark_shadow, 
                 question_id, question_text, subject, grade, difficulty, font, is_selected=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = bg_color
        self.light_shadow = light_shadow
        self.dark_shadow = dark_shadow
        self.question_id = question_id
        self.question_text = question_text
        self.subject = subject
        self.grade = grade
        self.difficulty = difficulty
        self.font = font
        self.small_font = pygame.font.SysFont('Arial', font.get_height() - 4)
        self.is_selected = is_selected
        
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
    
    def draw(self, surface):
        # Fundo do item (diferente se selecionado)
        bg_color = (255, 220, 220) if self.is_selected else self.bg_color  # Vermelho claro para seleção
        
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=10)
        
        # Sombras neumórficas
        shadow_rect_light = pygame.Rect(self.rect.x-2, self.rect.y-2, self.rect.width, self.rect.height)
        pygame.draw.rect(surface, self.light_shadow, shadow_rect_light, border_radius=10, width=2)
        
        shadow_rect_dark = pygame.Rect(self.rect.x+2, self.rect.y+2, self.rect.width, self.rect.height)
        pygame.draw.rect(surface, self.dark_shadow, shadow_rect_dark, border_radius=10, width=2)
        
        # Adicionar borda especial se selecionado
        if self.is_selected:
            pygame.draw.rect(surface, COLORS.get("error", (232, 77, 77)), 
                           self.rect, border_radius=10, width=2)
        
        # Mostrar o texto da questão (truncado se for muito longo)
        max_text_width = self.rect.width - 40
        question_text = self.question_text
        if self.font.size(question_text)[0] > max_text_width:
            # Truncar o texto e adicionar "..."
            while self.font.size(question_text + "...")[0] > max_text_width and len(question_text) > 0:
                question_text = question_text[:-1]
            question_text += "..."
        
        # Desenhar textos
        margin = 15
        
        # ID da questão (pequeno, canto superior esquerdo)
        id_surf = self.small_font.render(f"ID: {self.question_id}", True, (100, 100, 100))
        id_rect = id_surf.get_rect(topleft=(self.rect.x + margin, self.rect.y + 10))
        surface.blit(id_surf, id_rect)
        
        # Texto da questão (principal)
        question_surf = self.font.render(question_text, True, (50, 50, 50))
        question_rect = question_surf.get_rect(topleft=(self.rect.x + margin, self.rect.y + 35))
        surface.blit(question_surf, question_rect)
        
        # Informações adicionais (matéria, série, dificuldade)
        info_text = f"{self.subject} | {self.grade} | {self.difficulty}"
        info_surf = self.small_font.render(info_text, True, (100, 100, 100))
        info_rect = info_surf.get_rect(bottomleft=(self.rect.x + margin, self.rect.y + self.rect.height - 10))
        surface.blit(info_surf, info_rect)

class ConfirmationDialog:
    def __init__(self, x, y, width, height, bg_color, light_shadow, dark_shadow, 
                 text, font, text_font):
        self.panel = NeumorphicPanel(x, y, width, height, bg_color, light_shadow, dark_shadow)
        self.text = text
        self.font = font
        self.text_font = text_font
        
        # Botões
        button_width = 120
        button_height = 40
        button_y = y + height - 60
        
        self.confirm_button = NeumorphicButton(
            x + width//2 - button_width - 10, button_y,
            button_width, button_height,
            bg_color, light_shadow, dark_shadow,
            COLORS.get("error", (232, 77, 77)),
            "CONFIRMAR", text_font
        )
        
        self.cancel_button = NeumorphicButton(
            x + width//2 + 10, button_y,
            button_width, button_height,
            bg_color, light_shadow, dark_shadow,
            (100, 100, 100),
            "CANCELAR", text_font
        )
    
    def handle_events(self, event, mouse_pos):
        if event.type == MOUSEBUTTONDOWN:
            if self.confirm_button.is_clicked(mouse_pos):
                self.confirm_button.pressed = True
                return "confirm"
            
            if self.cancel_button.is_clicked(mouse_pos):
                self.cancel_button.pressed = True
                return "cancel"
        
        return None
    
    def update(self):
        self.confirm_button.pressed = False
        self.cancel_button.pressed = False
    
    def draw(self, surface):
        # Desenhar painel de fundo semi-transparente
        overlay = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Preto com 50% de opacidade
        surface.blit(overlay, (0, 0))
        
        # Desenhar o painel do diálogo
        self.panel.draw(surface)
        
        # Desenhar título
        title_surf = self.font.render("Confirmação", True, COLORS.get("error", (232, 77, 77)))
        title_rect = title_surf.get_rect(midtop=(self.panel.rect.centerx, self.panel.rect.y + 20))
        surface.blit(title_surf, title_rect)
        
        # Desenhar texto
        text_surf = self.text_font.render(self.text, True, (50, 50, 50))
        text_rect = text_surf.get_rect(center=(self.panel.rect.centerx, self.panel.rect.centery - 20))
        surface.blit(text_surf, text_rect)
        
        # Desenhar botões
        self.confirm_button.draw(surface)
        self.cancel_button.draw(surface)

class QuestionRemoveScreen:
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
        
        # Usar fonte padrão do sistema
        self.title_font = pygame.font.SysFont('Arial', 32, bold=True)
        self.subtitle_font = pygame.font.SysFont('Arial', 24, bold=True)
        self.text_font = pygame.font.SysFont('Arial', 18)
        self.small_font = pygame.font.SysFont('Arial', 14)
        
        # Estado da seleção
        self.selected_subject = None
        self.selected_grade = None
        self.selected_difficulty = None
        self.selected_question = None
        self.filter_active = False
        
        # Estado do filtro
        self.filter_message = None
        self.filter_timer = 0
        
        # Estado da confirmação
        self.show_confirmation = False
        self.confirmation_result = None
        
        # Estado de feedback após remoção
        self.removal_message = None
        self.removal_timer = 0
        
        # Para rolagem na lista
        self.scroll_offset = 0
        self.max_items_visible = 5  # Número de questões visíveis por vez
        
        # Criar elementos de UI
        self.setup_ui()
        
        # Carregar questões (mockup para testes)
        self.questions = self.load_questions()
        self.filtered_questions = self.questions
        
    def setup_ui(self):
        center_x = self.width // 2
        
        # Painel principal
        self.main_panel = NeumorphicPanel(
            center_x - 350, 20, 
            700, 560, 
            self.bg_color, self.light_shadow, self.dark_shadow
        )
        
        # Painel de filtros
        self.filter_panel = NeumorphicPanel(
            center_x - 330, 70, 
            660, 100, 
            self.bg_color, self.light_shadow, self.dark_shadow,
            border_radius=15
        )
        
        # Botões para matérias (filtro)
        self.subject_buttons = []
        btn_width = 90
        btn_height = 30
        btn_x_start = center_x - 300
        btn_y = 85
        
        for i, subject in enumerate(SUBJECTS[:7]):  # Limitamos a 7 matérias para caber
            btn_x = btn_x_start + i * (btn_width + 10)
            button = NeumorphicButton(
                btn_x, btn_y,
                btn_width, btn_height,
                self.bg_color, self.light_shadow, self.dark_shadow,
                self.accent_color, subject, self.small_font,
                is_toggle=True, is_active=False
            )
            self.subject_buttons.append(button)
        
        # Botões para séries (filtro)
        self.grade_buttons = []
        btn_width = 80
        btn_x_start = center_x - 150
        btn_y = 125
        
        for i, grade in enumerate(GRADE_LEVELS):
            btn_x = btn_x_start + i * (btn_width + 10)
            button = NeumorphicButton(
                btn_x, btn_y,
                btn_width, btn_height,
                self.bg_color, self.light_shadow, self.dark_shadow,
                self.accent_color, grade, self.small_font,
                is_toggle=True, is_active=False
            )
            self.grade_buttons.append(button)
        
        # Botões para dificuldade (filtro)
        self.difficulty_buttons = []
        btn_x_start = center_x + 40
        
        for i, difficulty in enumerate(DIFFICULTY_LEVELS):
            btn_x = btn_x_start + i * (btn_width + 10)
            button = NeumorphicButton(
                btn_x, btn_y,
                btn_width, btn_height,
                self.bg_color, self.light_shadow, self.dark_shadow,
                self.accent_color, difficulty, self.small_font,
                is_toggle=True, is_active=False
            )
            self.difficulty_buttons.append(button)
        
        # Botão para aplicar filtros
        self.apply_filter_button = NeumorphicButton(
            center_x + 200, 105,
            100, 30,
            self.bg_color, self.light_shadow, self.dark_shadow,
            COLORS.get("success", (75, 181, 67)),
            "FILTRAR", self.small_font
        )
        
        # Botão para limpar filtros
        self.clear_filter_button = NeumorphicButton(
            center_x + 200, 145,
            100, 30,
            self.bg_color, self.light_shadow, self.dark_shadow,
            COLORS.get("warning", (232, 181, 12)),
            "LIMPAR", self.small_font
        )
        
        # Painel da lista de questões
        self.list_panel = NeumorphicPanel(
            center_x - 330, 180, 
            660, 330, 
            self.bg_color, self.light_shadow, self.dark_shadow,
            border_radius=15
        )
        
        # Botões de rolagem para a lista
        self.scroll_up_button = NeumorphicButton(
            center_x + 290, 240,
            35, 35,
            self.bg_color, self.light_shadow, self.dark_shadow,
            self.accent_color, "▲", self.text_font
        )
        
        self.scroll_down_button = NeumorphicButton(
            center_x + 290, 410,
            35, 35,
            self.bg_color, self.light_shadow, self.dark_shadow,
            self.accent_color, "▼", self.text_font
        )
        
        # Botão para remover a questão selecionada
        self.remove_button = NeumorphicButton(
            center_x - 100, 520,
            200, 40,
            self.bg_color, self.light_shadow, self.dark_shadow,
            COLORS.get("error", (232, 77, 77)), "REMOVER QUESTÃO", self.text_font
        )
        
        # Botão para voltar ao menu
        self.back_button = NeumorphicButton(
            center_x - 320, 520,
            180, 40,
            self.bg_color, self.light_shadow, self.dark_shadow,
            (100, 100, 100),  # Cinza para botão de voltar
            "VOLTAR", self.text_font
        )
        
        # Diálogo de confirmação
        self.confirmation_dialog = ConfirmationDialog(
            center_x - 200, center_x - 100,
            400, 200,
            self.bg_color, self.light_shadow, self.dark_shadow,
            "Tem certeza que deseja excluir esta questão?",
            self.subtitle_font, self.text_font
        )
        
    def load_questions(self):
        # Função mockup para carregar questões do banco
        # No código real, faria uma consulta SQL
        
        mock_questions = [
            {
                "id": 1,
                "text": "Qual é o resultado de 7 x 8?",
                "subject": "Matematica",
                "grade": "1 Ano",
                "difficulty": "Facil",
                "options": ["54", "56", "64", "72"],
                "correct_option": 1,
                "explanation": "Multiplicação simples: 7 × 8 = 56"
            },
            {
                "id": 2,
                "text": "Qual é a capital da França?",
                "subject": "Geografia",
                "grade": "2 Ano",
                "difficulty": "Facil",
                "options": ["Londres", "Paris", "Roma", "Madri"],
                "correct_option": 1,
                "explanation": "Paris é a capital da França."
            },
            {
                "id": 3,
                "text": "Qual é a fórmula química da água?",
                "subject": "Quimica",
                "grade": "1 Ano",
                "difficulty": "Facil",
                "options": ["CO2", "H2O", "O2", "NaCl"],
                "correct_option": 1,
                "explanation": "A água é formada por duas moléculas de hidrogênio e uma de oxigênio, H2O."
            },
            {
                "id": 4,
                "text": "Qual é a área de um círculo com raio 5cm? (Use π = 3.14)",
                "subject": "Matematica",
                "grade": "2 Ano",
                "difficulty": "Medio",
                "options": ["25π cm²", "10π cm²", "15π cm²", "20π cm²"],
                "correct_option": 0,
                "explanation": "A área de um círculo é A = π × r², assim A = π × 5² = 25π cm²"
            },
            {
                "id": 5,
                "text": "Quem escreveu 'Dom Casmurro'?",
                "subject": "Portugues",
                "grade": "3 Ano",
                "difficulty": "Medio",
                "options": ["José de Alencar", "Machado de Assis", "Clarice Lispector", "Carlos Drummond de Andrade"],
                "correct_option": 1,
                "explanation": "Dom Casmurro é um romance escrito por Machado de Assis, publicado em 1899."
            },
            {
                "id": 6,
                "text": "Qual é a solução da equação 2x² - 5x - 3 = 0?",
                "subject": "Matematica",
                "grade": "3 Ano",
                "difficulty": "Dificil",
                "options": ["x = 3 ou x = -0.5", "x = 2.5 ou x = -0.5", "x = 3 ou x = -1", "x = 2 ou x = -1.5"],
                "correct_option": 0,
                "explanation": "Usando a fórmula de Bhaskara: x = (-b ± √(b² - 4ac))/2a, onde a=2, b=-5, c=-3"
            },
            {
                "id": 7,
                "text": "Um objeto é lançado verticalmente para cima. No ponto mais alto da trajetória:",
                "subject": "Fisica",
                "grade": "2 Ano",
                "difficulty": "Medio",
                "options": ["A velocidade e a aceleração são nulas", "A velocidade é nula e a aceleração é g", 
                           "A velocidade é g e a aceleração é nula", "A velocidade e a aceleração são iguais a g"],
                "correct_option": 1,
                "explanation": "No ponto mais alto, a velocidade instantânea é zero, mas a aceleração da gravidade continua agindo."
            },
            {
                "id": 8,
                "text": "Quais são os principais tipos de RNA e suas funções?",
                "subject": "Biologia",
                "grade": "3 Ano",
                "difficulty": "Dificil",
                "options": ["mRNA, tRNA e rRNA - transcrição, tradução e estrutura ribossômica", 
                           "DNA, RNA e proteínas - replicação, transcrição e tradução", 
                           "Ribossomos, lisossomos e mitocôndrias - síntese, digestão e energia", 
                           "Núcleo, citoplasma e membrana - controle, metabolismo e proteção"],
                "correct_option": 0,
                "explanation": "Os principais tipos de RNA são: mRNA (RNA mensageiro), tRNA (RNA transportador) e rRNA (RNA ribossômico)."
            }
        ]
        
        return mock_questions
    
    def apply_filters(self):
        # Filtrar as questões com base nas seleções
        if not any([self.selected_subject, self.selected_grade, self.selected_difficulty]):
            # Se nenhum filtro estiver selecionado, mostrar todas as questões
            self.filtered_questions = self.questions
            self.filter_message = "Mostrando todas as questões"
            self.filter_timer = 120
            self.filter_active = False
            return
        
        # Aplicar filtros selecionados
        filtered = self.questions
        
        if self.selected_subject:
            filtered = [q for q in filtered if q["subject"] == self.selected_subject]
            
        if self.selected_grade:
            filtered = [q for q in filtered if q["grade"] == self.selected_grade]
            
        if self.selected_difficulty:
            filtered = [q for q in filtered if q["difficulty"] == self.selected_difficulty]
        
        self.filtered_questions = filtered
        self.scroll_offset = 0  # Reset da rolagem
        
        # Preparar mensagem de feedback
        if len(filtered) == 0:
            self.filter_message = "Nenhuma questão encontrada com os filtros selecionados"
        else:
            self.filter_message = f"Encontradas {len(filtered)} questões"
        
        self.filter_timer = 120  # 2 segundos a 60 FPS
        self.filter_active = True
    
    def clear_filters(self):
        # Limpar todas as seleções de filtro
        self.selected_subject = None
        self.selected_grade = None
        self.selected_difficulty = None
        
        # Resetar estado dos botões de toggle
        for button in self.subject_buttons:
            button.is_active = False
            
        for button in self.grade_buttons:
            button.is_active = False
            
        for button in self.difficulty_buttons:
            button.is_active = False
        
        # Mostrar todas as questões
        self.filtered_questions = self.questions
        self.scroll_offset = 0
        
        # Mostrar mensagem de feedback
        self.filter_message = "Filtros removidos"
        self.filter_timer = 120
        self.filter_active = False
    
    def remove_question(self, question):
        # Remover a questão da lista (simulação)
        # Em um app real, executaria um DELETE no banco de dados
        
        self.questions = [q for q in self.questions if q["id"] != question["id"]]
        self.filtered_questions = [q for q in self.filtered_questions if q["id"] != question["id"]]
        
        # Mostrar mensagem de confirmação
        self.removal_message = f"Questão #{question['id']} removida com sucesso"
        self.removal_timer = 180  # 3 segundos
        
        # Resetar seleção
        self.selected_question = None
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
                
            # Se o diálogo de confirmação estiver aberto, processar apenas seus eventos
            if self.show_confirmation:
                result = self.confirmation_dialog.handle_events(event, pygame.mouse.get_pos())
                if result == "confirm":
                    self.remove_question(self.selected_question)
                    self.show_confirmation = False
                elif result == "cancel":
                    self.show_confirmation = False
                continue
                
            if event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Verificar cliques nos botões de filtro de matéria
                for i, button in enumerate(self.subject_buttons):
                    if button.is_clicked(mouse_pos):
                        # Toggle do botão
                        button.is_active = not button.is_active
                        
                        # Atualizar seleção
                        self.selected_subject = SUBJECTS[i] if button.is_active else None
                        
                        # Desativar outros botões de matéria se este foi ativado
                        if button.is_active:
                            for j, other_button in enumerate(self.subject_buttons):
                                if j != i:
                                    other_button.is_active = False
                        
                        break
                
                # Verificar cliques nos botões de filtro de série
                for i, button in enumerate(self.grade_buttons):
                    if button.is_clicked(mouse_pos):
                        # Toggle do botão
                        button.is_active = not button.is_active
                        
                        # Atualizar seleção
                        self.selected_grade = GRADE_LEVELS[i] if button.is_active else None
                        
                        # Desativar outros botões de série se este foi ativado
                        if button.is_active:
                            for j, other_button in enumerate(self.grade_buttons):
                                if j != i:
                                    other_button.is_active = False
                        
                        break
                
                # Verificar cliques nos botões de filtro de dificuldade
                for i, button in enumerate(self.difficulty_buttons):
                    if button.is_clicked(mouse_pos):
                        # Toggle do botão
                        button.is_active = not button.is_active
                        
                        # Atualizar seleção
                        self.selected_difficulty = DIFFICULTY_LEVELS[i] if button.is_active else None
                        
                        # Desativar outros botões de dificuldade se este foi ativado
                        if button.is_active:
                            for j, other_button in enumerate(self.difficulty_buttons):
                                if j != i:
                                    other_button.is_active = False
                        
                        break
                
                # Verificar clique no botão APLICAR FILTRO
                if self.apply_filter_button.is_clicked(mouse_pos):
                    self.apply_filter_button.pressed = True
                    self.apply_filters()
                
                # Verificar clique no botão LIMPAR FILTRO
                if self.clear_filter_button.is_clicked(mouse_pos):
                    self.clear_filter_button.pressed = True
                    self.clear_filters()
                
                # Verificar cliques na lista de questões
                start_y = self.list_panel.rect.y + 40
                item_height = 80
                item_spacing = 10
                
                visible_items = self.filtered_questions[self.scroll_offset:self.scroll_offset + self.max_items_visible]
                for i, question in enumerate(visible_items):
                    item_y = start_y + i * (item_height + item_spacing)
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
                        
                # Verificar cliques nos botões de rolagem
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
                
                # Verificar clique no botão REMOVER
                if self.remove_button.is_clicked(mouse_pos) and self.selected_question:
                    self.remove_button.pressed = True
                    # Abrir diálogo de confirmação
                    self.show_confirmation = True
                
                # Verificar clique no botão VOLTAR
                if self.back_button.is_clicked(mouse_pos):
                    self.back_button.pressed = True
                    return {"action": "back_to_menu"}
        
        return {"action": "none"}
    
    def update(self):
        # Resetar estado dos botões
        self.apply_filter_button.pressed = False
        self.clear_filter_button.pressed = False
        self.remove_button.pressed = False
        self.back_button.pressed = False
        self.scroll_up_button.pressed = False
        self.scroll_down_button.pressed = False
        
        # Atualizar diálogo de confirmação
        if self.show_confirmation:
            self.confirmation_dialog.update()
        
        # Atualizar temporizador de mensagem de filtro
        if self.filter_timer > 0:
            self.filter_timer -= 1
            if self.filter_timer == 0:
                self.filter_message = None
        
        # Atualizar temporizador de mensagem de remoção
        if self.removal_timer > 0:
            self.removal_timer -= 1
            if self.removal_timer == 0:
                self.removal_message = None
    
    def draw(self):
        # Limpa a tela com a cor de fundo
        self.screen.fill(self.bg_color)
        
        # Desenha o painel principal
        self.main_panel.draw(self.screen)
        
        # Desenha o título
        title_text = self.title_font.render("Remover Questões", True, (60, 60, 60))
        title_rect = title_text.get_rect(center=(self.width // 2, 45))
        self.screen.blit(title_text, title_rect)
        
        # Desenha o painel de filtros
        self.filter_panel.draw(self.screen)
        
        # Desenha o texto do filtro
        filter_label = self.text_font.render("Filtrar por:", True, (80, 80, 80))
        filter_rect = filter_label.get_rect(topleft=(self.filter_panel.rect.x + 15, self.filter_panel.rect.y + 10))
        self.screen.blit(filter_label, filter_rect)
        
        # Desenha os botões de filtro
        for button in self.subject_buttons:
            button.draw(self.screen)
            
        for button in self.grade_buttons:
            button.draw(self.screen)
            
        for button in self.difficulty_buttons:
            button.draw(self.screen)
        
        # Desenha os botões de aplicar/limpar filtro
        self.apply_filter_button.draw(self.screen)
        self.clear_filter_button.draw(self.screen)
        
        # Desenha o painel da lista de questões
        self.list_panel.draw(self.screen)
        
        # Desenha a mensagem de filtro se houver
        if self.filter_message:
            message_color = (50, 50, 50) if self.filter_active else COLORS.get("warning", (232, 181, 12))
            message_surf = self.text_font.render(self.filter_message, True, message_color)
            message_rect = message_surf.get_rect(midtop=(self.width // 2, self.list_panel.rect.y + 10))
            self.screen.blit(message_surf, message_rect)
        
        # Desenha a mensagem de remoção se houver
        if self.removal_message:
            message_surf = self.text_font.render(self.removal_message, True, COLORS.get("success", (75, 181, 67)))
            message_rect = message_surf.get_rect(center=(self.width // 2, self.height - 40))
            self.screen.blit(message_surf, message_rect)
        
        # Desenha as questões filtradas
        if len(self.filtered_questions) == 0:
            # Mensagem se não houver questões
            no_questions_text = self.text_font.render("Nenhuma questão encontrada", True, (100, 100, 100))
            no_questions_rect = no_questions_text.get_rect(center=(self.list_panel.rect.centerx, self.list_panel.rect.centery))
            self.screen.blit(no_questions_text, no_questions_rect)
        else:
            # Desenha as questões visíveis
            start_y = self.list_panel.rect.y + 40
            item_height = 80
            item_spacing = 10
            
            visible_items = self.filtered_questions[self.scroll_offset:self.scroll_offset + self.max_items_visible]
            for i, question in enumerate(visible_items):
                item_y = start_y + i * (item_height + item_spacing)
                
                # Verifica se a questão está selecionada
                is_selected = self.selected_question and self.selected_question["id"] == question["id"]
                
                question_item = QuestionListItem(
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
                    question["grade"],
                    question["difficulty"],
                    self.text_font,
                    is_selected
                )
                question_item.draw(self.screen)
            
            # Desenha indicadores de rolagem se houver mais itens
            if len(self.filtered_questions) > self.max_items_visible:
                self.scroll_up_button.draw(self.screen)
                self.scroll_down_button.draw(self.screen)
                
                # Indicador de posição da rolagem
                total_items = len(self.filtered_questions)
                progress_height = 100
                progress_rect = pygame.Rect(
                    self.scroll_up_button.rect.centerx - 2,
                    self.scroll_up_button.rect.bottom + 10,
                    4,
                    progress_height
                )
                pygame.draw.rect(self.screen, (200, 200, 200), progress_rect, border_radius=2)
                
                # Indicador de posição atual
                if total_items > 0:
                    indicator_height = max(20, progress_height / total_items * self.max_items_visible)
                    indicator_pos = (self.scroll_offset / max(1, total_items - self.max_items_visible)) * (progress_height - indicator_height)
                    indicator_rect = pygame.Rect(
                        progress_rect.x - 1,
                        progress_rect.y + indicator_pos,
                        6,
                        indicator_height
                    )
                    pygame.draw.rect(self.screen, self.accent_color, indicator_rect, border_radius=3)
        
        # Desenha o botão de remover (ativo apenas se uma questão estiver selecionada)
        if self.selected_question:
            self.remove_button.draw(self.screen)
        else:
            # Versão desativada do botão
            disabled_button = NeumorphicButton(
                self.remove_button.rect.x, self.remove_button.rect.y,
                self.remove_button.rect.width, self.remove_button.rect.height,
                self.bg_color, self.light_shadow, self.dark_shadow,
                (180, 180, 180),  # Cinza para botão desativado
                "REMOVER QUESTÃO", self.text_font
            )
            disabled_button.draw(self.screen)
            
            # Mensagem de dica
            hint_text = self.small_font.render("Selecione uma questão para remover", True, (120, 120, 120))
            hint_rect = hint_text.get_rect(midtop=(self.remove_button.rect.centerx, self.remove_button.rect.bottom + 5))
            self.screen.blit(hint_text, hint_rect)
        
        # Desenha o botão de voltar
        self.back_button.draw(self.screen)
        
        # Desenha o diálogo de confirmação se estiver aberto
        if self.show_confirmation:
            self.confirmation_dialog.draw(self.screen)
        
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