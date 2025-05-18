import pygame
import sys
import random
import time
from pygame.locals import *

# Configurações
try:
    import config
    COLORS = config.COLORS
    CHECKPOINT_INTERVALS = config.CHECKPOINT_INTERVALS
    TOTAL_QUESTIONS = config.TOTAL_QUESTIONS
except (ImportError, AttributeError):
    COLORS = {
        "background": (30, 180, 195),     # #1EB4C3
        "light_shadow": (255, 255, 255),  # Branco
        "dark_shadow": (20, 140, 150),    # #148C96
        "accent": (251, 164, 31),         # Laranja #FBA41F
        "text": (0, 0, 0),
        "black": (0, 0, 0),
        "success": (75, 181, 67),
        "warning": (232, 181, 12),
        "error": (232, 77, 77),
    }
    CHECKPOINT_INTERVALS = 5
    TOTAL_QUESTIONS = 15

# Componentes de UI
class NeumorphicPanel:
    def __init__(self, x, y, width, height, bg_color, light_shadow, dark_shadow, border_radius=20):
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = bg_color
        self.light_shadow = light_shadow
        self.dark_shadow = dark_shadow
        self.border_radius = border_radius

    def draw(self, surface):
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=self.border_radius)
        pygame.draw.rect(surface, COLORS["black"], self.rect, border_radius=self.border_radius, width=2)

class NeumorphicButton:
    def __init__(self, x, y, width, height, bg_color, light_shadow, dark_shadow,
                 accent_color, text, font, is_toggle=False, is_active=False, is_circular=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = bg_color
        self.light_shadow = light_shadow
        self.dark_shadow = dark_shadow
        self.accent_color = accent_color
        self.text = text
        self.font = font
        self.is_toggle = is_toggle
        self.is_active = is_active
        self.is_circular = is_circular
        self.pressed = False
        self.correct = None
        self.text_surf = font.render(text, True, (50, 50, 50))
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    def draw(self, surface):
        is_pressed = self.pressed or (self.is_toggle and self.is_active)
        bg_color = self.bg_color
        if self.correct is True:
            bg_color = (200, 255, 200)
        elif self.correct is False:
            bg_color = (255, 200, 200)

        if self.is_circular:
            pygame.draw.circle(surface, bg_color, self.rect.center, self.rect.width // 2)
            pygame.draw.circle(surface, COLORS["black"], self.rect.center, self.rect.width // 2, width=2)
            
            if is_pressed:
                pygame.draw.circle(surface, self.accent_color, self.rect.center, self.rect.width // 2 - 4)
                pygame.draw.circle(surface, COLORS["black"], self.rect.center, self.rect.width // 2 - 4, width=2)
                text_rect = self.text_surf.get_rect(center=(self.rect.centerx+1, self.rect.centery+1))
                surface.blit(self.text_surf, text_rect)
            else:
                surface.blit(self.text_surf, self.text_rect)
        else:
            if is_pressed:
                pygame.draw.rect(surface, bg_color, self.rect.inflate(-4, -4), border_radius=10)
                pygame.draw.rect(surface, COLORS["black"], self.rect.inflate(-4, -4), border_radius=10, width=2)
                border_color = self.accent_color
                if self.correct is True:
                    border_color = COLORS.get("success", (75, 181, 67))
                elif self.correct is False:
                    border_color = COLORS.get("error", (232, 77, 77))
                pygame.draw.rect(surface, border_color, self.rect, border_radius=10, width=2)
                text_rect = self.text_surf.get_rect(center=(self.rect.centerx+1, self.rect.centery+1))
                surface.blit(self.text_surf, text_rect)
            else:
                pygame.draw.rect(surface, bg_color, self.rect, border_radius=10)
                pygame.draw.rect(surface, COLORS["black"], self.rect, border_radius=10, width=2)
                surface.blit(self.text_surf, self.text_rect)

class ProgressBar:
    def __init__(self, x, y, width, height, bg_color, progress_color, border_color, total_steps):
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = bg_color
        self.progress_color = progress_color
        self.border_color = border_color
        self.total_steps = total_steps
        self.current_step = 0

    def update(self, current_step):
        self.current_step = min(current_step, self.total_steps)

    def draw(self, surface):
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=5)
        pygame.draw.rect(surface, COLORS["black"], self.rect, border_radius=5, width=2)
        if self.current_step > 0:
            progress_width = int(self.rect.width * (self.current_step / self.total_steps))
            progress_rect = pygame.Rect(self.rect.x, self.rect.y, progress_width, self.rect.height)
            pygame.draw.rect(surface, self.progress_color, progress_rect, border_radius=5)
        for i in range(1, self.total_steps // CHECKPOINT_INTERVALS):
            checkpoint_x = self.rect.x + (i * CHECKPOINT_INTERVALS / self.total_steps) * self.rect.width
            pygame.draw.line(surface, (100, 100, 100),
                             (checkpoint_x, self.rect.y),
                             (checkpoint_x, self.rect.y + self.rect.height), 2)

class Question:
    def __init__(self, text, options, correct_option, difficulty):
        self.text = text
        self.options = options
        self.correct_option = correct_option
        self.difficulty = difficulty
        self.used_help = {
            "skip": False,
            "eliminate": False,
            "hint": False
        }
        # Adicionando dicas para cada pergunta
        self.hint = self.generate_hint()

    def generate_hint(self):
        # Gerando dicas baseadas no assunto e dificuldade
        if "Matematica" in self.text:
            if "7 x 8" in self.text:
                return "Dica: Lembre-se da tabuada do 7 ou do 8."
            elif "área de um círculo" in self.text:
                return "Dica: A fórmula da área do círculo é π vezes raio ao quadrado."
            elif "equação 2x²" in self.text:
                return "Dica: Use a fórmula de Bhaskara para resolver equações quadráticas."
        elif "Fisica" in self.text:
            if "unidade de medida da força" in self.text:
                return "Dica: A unidade recebeu o nome de um famoso cientista."
            elif "lançado verticalmente" in self.text:
                return "Dica: No ponto mais alto, a velocidade vertical é zero, mas a aceleração continua."
            elif "capacitor de placas paralelas" in self.text:
                return "Dica: A capacitância é inversamente proporcional à distância entre as placas."
        return "Dica: Pense cuidadosamente sobre o tema da pergunta."

class MockQuestionGenerator:
    def __init__(self, subject, grade):
        self.subject = subject
        self.grade = grade
        self.money_values = [
            [1000, 2000, 3000, 5000, 10000],
            [20000, 30000, 50000, 100000, 200000],
            [300000, 500000, 750000, 1000000, 2000000]
        ]
    
    def get_questions(self, count=TOTAL_QUESTIONS):
        questions = []
        easy_count = min(5, count)
        for i in range(easy_count):
            questions.append(self._generate_question(difficulty=0))
        
        medium_count = min(5, count - easy_count)
        for i in range(medium_count):
            questions.append(self._generate_question(difficulty=1))
        
        hard_count = count - easy_count - medium_count
        for i in range(hard_count):
            questions.append(self._generate_question(difficulty=2))
        
        return questions
    
    def _generate_question(self, difficulty):
        if self.subject == "Matematica":
            if difficulty == 0:
                text = "Qual é o resultado de 7 x 8?"
                options = ["54", "56", "64", "72"]
                correct = 1
            elif difficulty == 1:
                text = "Qual é a área de um círculo com raio 5cm? (Use π = 3.14)"
                options = ["25π cm²", "10π cm²", "15π cm²", "20π cm²"]
                correct = 0
            else:
                text = "Qual é a solução da equação 2x² - 5x - 3 = 0?"
                options = ["x = 3 ou x = -0.5", "x = 2.5 ou x = -0.5", "x = 3 ou x = -1", "x = 2 ou x = -1.5"]
                correct = 0
        elif self.subject == "Fisica":
            if difficulty == 0:
                text = "Qual é a unidade de medida da força no Sistema Internacional (SI)?"
                options = ["Watt", "Joule", "Newton", "Pascal"]
                correct = 2
            elif difficulty == 1:
                text = "Um objeto é lançado verticalmente para cima. No ponto mais alto da trajetória:"
                options = ["A velocidade e a aceleração são nulas", "A velocidade é nula e a aceleração é g", 
                           "A velocidade é g e a aceleração é nula", "A velocidade e a aceleração são iguais a g"]
                correct = 1
            else:
                text = "Um capacitor de placas paralelas está conectado a uma bateria. O que acontece com a capacitância se a distância entre as placas for duplicada?"
                options = ["Aumenta 2 vezes", "Diminui pela metade", "Não muda", "Aumenta 4 vezes"]
                correct = 1
        else:
            if difficulty == 0:
                text = f"Pergunta fácil de {self.subject} para o {self.grade}"
                options = ["Opção A", "Opção B", "Opção C", "Opção D"]
                correct = random.randint(0, 3)
            elif difficulty == 1:
                text = f"Pergunta média de {self.subject} para o {self.grade}"
                options = ["Opção A", "Opção B", "Opção C", "Opção D"]
                correct = random.randint(0, 3)
            else:
                text = f"Pergunta difícil de {self.subject} para o {self.grade}"
                options = ["Opção A", "Opção B", "Opção C", "Opção D"]
                correct = random.randint(0, 3)
                
        return Question(text, options, correct, difficulty)
    
    def get_money_for_question(self, question_number):
        difficulty = 0 if question_number < 5 else 1 if question_number < 10 else 2
        value_index = question_number % 5
        return self.money_values[difficulty][value_index]

class QuizScreen:
    def __init__(self, screen, user_data, game_config):
        self.screen = screen
        self.running = True
        self.width, self.height = screen.get_size()
        self.user_data = user_data
        self.game_config = game_config
        
        self.bg_color = COLORS["background"]
        self.light_shadow = COLORS["light_shadow"]
        self.dark_shadow = COLORS["dark_shadow"]
        self.accent_color = COLORS["accent"]
        
        self.title_font = pygame.font.SysFont('Arial', 28, bold=True)
        self.question_font = pygame.font.SysFont('Arial', 22)
        self.option_font = pygame.font.SysFont('Arial', 18)
        self.info_font = pygame.font.SysFont('Arial', 16)
        self.small_font = pygame.font.SysFont('Arial', 14)
        
        self.question_generator = MockQuestionGenerator(
            game_config["subject"], 
            game_config["grade"]
        )
        self.questions = self.question_generator.get_questions(TOTAL_QUESTIONS)
        
        self.current_question = 0
        self.selected_option = None
        self.answer_correct = None
        self.accumulated_money = 0
        self.saved_money = 0
        self.game_over = False
        self.show_result = False
        self.waiting_for_next = False
        self.wait_timer = 0
        self.show_help_options = False
        self.show_hint = False
        self.help_buttons = []
        
        self.setup_ui()
        
    def setup_ui(self):
        # Painel esquerdo maior (75% da largura)
        left_panel_width = int(self.width * 0.75) - 30
        self.left_panel = NeumorphicPanel(
            20, 20, 
            left_panel_width, 
            self.height - 40,
            self.accent_color,
            self.light_shadow,
            self.dark_shadow
        )
        
        # Painel direito menor (25% da largura)
        right_panel_width = self.width - left_panel_width - 40
        self.right_panel = NeumorphicPanel(
            left_panel_width + 30, 20,
            right_panel_width,
            self.height - 40,
            self.accent_color,
            self.light_shadow,
            self.dark_shadow
        )
        
        # Barra de progresso (no topo do painel esquerdo)
        self.progress_bar = ProgressBar(
            40, 30,
            left_panel_width - 40, 20,
            (220, 220, 220),
            (238, 32, 81),  # Vermelho
            (150, 150, 150),
            TOTAL_QUESTIONS
        )
        
        # Painel da pergunta (dentro do painel esquerdo)
        self.question_panel = NeumorphicPanel(
            40, 70,
            left_panel_width - 40, 130,
            self.bg_color,
            self.light_shadow,
            self.dark_shadow,
            border_radius=15
        )
        
        # Painel da dica (será mostrado quando o botão de dica for clicado)
        self.hint_panel = NeumorphicPanel(
            self.width // 2 - 200,
            self.height // 2 - 100,
            400, 200,
            self.bg_color,
            self.light_shadow,
            self.dark_shadow,
            border_radius=15
        )
        
        # Botão para fechar a dica
        self.close_hint_button = NeumorphicButton(
            self.width // 2 - 20,
            self.height // 2 + 60,
            40, 40,
            self.bg_color,
            self.light_shadow,
            self.dark_shadow,
            COLORS["error"],
            "X", self.title_font,
            is_circular=True
        )
        
        # Botões de opções (dentro do painel esquerdo)
        self.option_buttons = []
        button_width = left_panel_width - 60
        button_height = 50
        button_y_start = 220
        button_y_gap = 70
        
        for i in range(4):
            button = NeumorphicButton(
                50,
                button_y_start + i * button_y_gap,
                button_width, button_height,
                self.bg_color,
                self.light_shadow,
                self.dark_shadow,
                self.accent_color,
                "", self.option_font
            )
            self.option_buttons.append(button)
        
        # Botões na parte inferior do painel esquerdo
        button_bottom_y = self.height - 80
        
        # Botão próxima pergunta (redondo)
        self.next_button = NeumorphicButton(
            left_panel_width // 2 + 215, 
            button_bottom_y, 60, 60,
            self.bg_color,
            self.light_shadow,
            self.dark_shadow,
            self.accent_color,
            ">", self.title_font,
            is_circular=True
        )
        
        # Botão desistir (redondo) - Habilitado e posicionado à esquerda
        self.quit_button = NeumorphicButton(
            50, button_bottom_y,
            60, 60,
            self.bg_color,
            self.light_shadow,
            self.dark_shadow,
            COLORS["error"],
            "X", self.title_font,
            is_circular=True
        )
        
        # Botão de ajuda (no painel direito) - Movido para cima
        self.help_button = NeumorphicButton(
            left_panel_width + 30 + (right_panel_width // 2) - 30, 
            button_bottom_y - 100,  # Movido 100 pixels para cima
            60, 60,
            self.bg_color,
            self.light_shadow,
            self.dark_shadow,
            self.accent_color,
            "?", self.title_font,
            is_circular=True
        )
        
        # Botões de ajuda (aparecem quando o botão de ajuda é clicado)
        help_button_width = right_panel_width - 40
        help_button_height = 40
        help_button_y_start = button_bottom_y - 200  # Movido para cima
        
        # Botão pular pergunta movido para a direita, próximo à borda da caixa esquerda
        self.skip_button = NeumorphicButton(
            left_panel_width + 50,  
            help_button_y_start - 30,
            help_button_width, help_button_height,
            self.bg_color,
            self.light_shadow,
            self.dark_shadow,
            self.accent_color,
            "Pular Pergunta", self.small_font
        )
        
        self.eliminate_button = NeumorphicButton(
            left_panel_width + 50,  # Mais próximo da borda
            help_button_y_start + 15,
            help_button_width, help_button_height,
            self.bg_color,
            self.light_shadow,
            self.dark_shadow,
            self.accent_color,
            "Eliminar Alternativa", self.small_font
        )
        
        self.hint_button = NeumorphicButton(
            left_panel_width + 50,  # Mais próximo da borda
            help_button_y_start + 60,
            help_button_width, help_button_height,
            self.bg_color,
            self.light_shadow,
            self.dark_shadow,
            self.accent_color,
            "Dica sobre o Tema", self.small_font
        )
        
        self.help_buttons = [self.skip_button, self.eliminate_button, self.hint_button]
        
        self.update_question_display()

    def update_question_display(self):
        if self.current_question < len(self.questions):
            question = self.questions[self.current_question]
            
            option_labels = ["A", "B", "C", "D"]
            for i, option in enumerate(question.options):
                self.option_buttons[i].text = f"{option_labels[i]}) {option}"
                self.option_buttons[i].text_surf = self.option_font.render(
                    self.option_buttons[i].text, True, (50, 50, 50)
                )
                self.option_buttons[i].text_rect = self.option_buttons[i].text_surf.get_rect(
                    center=self.option_buttons[i].rect.center
                )
                self.option_buttons[i].correct = None
                
            self.progress_bar.update(self.current_question)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                if self.waiting_for_next:
                    continue
                
                if self.game_over:
                    if self.quit_button.is_clicked(mouse_pos):
                        return {"action": "back_to_menu", "money_earned": self.saved_money}
                    continue
                
                # Verificar cliques no botão de fechar dica
                if self.show_hint:
                    if self.close_hint_button.is_clicked(mouse_pos):
                        self.close_hint_button.pressed = True
                        self.show_hint = False
                        continue
                
                # Verificar cliques nos botões de ajuda
                if self.show_help_options:
                    for button in self.help_buttons:
                        if button.is_clicked(mouse_pos):
                            button.pressed = True
                            self.handle_help_button(button)
                            self.show_help_options = False
                            break
                    else:
                        # Se clicou fora, fecha os botões de ajuda
                        self.show_help_options = False
                    continue
                
                # Verificar clique no botão de ajuda principal
                if self.help_button.is_clicked(mouse_pos):
                    self.help_button.pressed = True
                    self.show_help_options = not self.show_help_options
                    continue
                
                # Verificar cliques nos botões de opções
                if not self.show_result and not self.show_hint:
                    for i, button in enumerate(self.option_buttons):
                        if button.is_clicked(mouse_pos):
                            self.selected_option = i
                            self.check_answer()
                            self.show_result = True
                            break
                
                # Verificar clique no botão próxima
                elif self.next_button.is_clicked(mouse_pos):
                    self.next_button.pressed = True
                    self.go_to_next_question()
                
                # Verificar clique no botão desistir
                elif self.quit_button.is_clicked(mouse_pos):
                    self.quit_button.pressed = True
                    if self.show_result:
                        self.go_to_next_question()
                    else:
                        self.game_over = True
                        return {"action": "back_to_menu", "money_earned": self.saved_money}
        
        return {"action": "none"}
    
    def handle_help_button(self, button):
        current_question = self.questions[self.current_question]
        
        if button == self.skip_button and not current_question.used_help["skip"]:
            # Pular pergunta (avança para a próxima sem penalidade)
            current_question.used_help["skip"] = True
            self.go_to_next_question()
            
        elif button == self.eliminate_button and not current_question.used_help["eliminate"]:
            # Eliminar duas alternativas incorretas
            current_question.used_help["eliminate"] = True
            options_to_eliminate = 2
            correct_index = current_question.correct_option
            
            # Encontra índices das alternativas incorretas
            wrong_indices = [i for i in range(4) if i != correct_index]
            random.shuffle(wrong_indices)
            
            # Elimina até 2 alternativas incorretas
            for i in wrong_indices[:options_to_eliminate]:
                self.option_buttons[i].text = ""
                self.option_buttons[i].text_surf = self.option_font.render("", True, (50, 50, 50))
                
        elif button == self.hint_button and not current_question.used_help["hint"]:
            # Mostrar dica sobre o tema
            current_question.used_help["hint"] = True
            self.show_hint = True
    
    def check_answer(self):
        current = self.questions[self.current_question]
        self.answer_correct = (self.selected_option == current.correct_option)
        
        for i, button in enumerate(self.option_buttons):
            if i == current.correct_option:
                button.correct = True
            elif i == self.selected_option and i != current.correct_option:
                button.correct = False
        
        if self.answer_correct:
            self.accumulated_money = self.question_generator.get_money_for_question(self.current_question)
            
            next_question = self.current_question + 1
            if next_question % CHECKPOINT_INTERVALS == 0:
                self.saved_money = self.accumulated_money
        else:
            self.waiting_for_next = True
            self.wait_timer = pygame.time.get_ticks()
    
    def go_to_next_question(self):
        self.selected_option = None
        self.show_result = False
        self.next_button.pressed = False
        self.show_help_options = False
        self.show_hint = False
        
        if not self.answer_correct:
            self.game_over = True
            return
        
        self.current_question += 1
        
        if self.current_question >= len(self.questions):
            self.game_over = True
            return
        
        self.update_question_display()
    
    def update(self):
        if self.waiting_for_next:
            current_time = pygame.time.get_ticks()
            if current_time - self.wait_timer > 2000:
                self.waiting_for_next = False
                self.go_to_next_question()
    
    def draw(self):
        self.screen.fill(self.bg_color)
        
        self.left_panel.draw(self.screen)
        self.right_panel.draw(self.screen)
        
        self.progress_bar.draw(self.screen)
        
        # Informações do quiz
        info_text = f"{self.game_config['subject']} - {self.game_config['grade']}"
        info_surf = self.info_font.render(info_text, True, (80, 80, 80))
        info_rect = info_surf.get_rect(topleft=(40, 50))
        self.screen.blit(info_surf, info_rect)
        
        question_num_text = f"Pergunta {self.current_question + 1} de {TOTAL_QUESTIONS}"
        question_num_surf = self.info_font.render(question_num_text, True, (80, 80, 80))
        question_num_rect = question_num_surf.get_rect(midtop=(self.left_panel.rect.width // 2 + 20, 34))
        self.screen.blit(question_num_surf, question_num_rect)
        
        # Informações de dinheiro (painel direito)
        money_title = self.title_font.render("PoliCoins", True, (50, 50, 50))
        money_title_rect = money_title.get_rect(center=(self.right_panel.rect.centerx, 60))
        self.screen.blit(money_title, money_title_rect)
        
        money_text = f"Acumulado: R$ {self.accumulated_money:,}"
        money_surf = self.info_font.render(money_text, True, (50, 150, 50))
        money_rect = money_surf.get_rect(center=(self.right_panel.rect.centerx, 120))
        self.screen.blit(money_surf, money_rect)
        
        saved_money_text = f"Garantido: R$ {self.saved_money:,}"
        saved_money_surf = self.info_font.render(saved_money_text, True, (80, 80, 80))
        saved_money_rect = saved_money_surf.get_rect(center=(self.right_panel.rect.centerx, 160))
        self.screen.blit(saved_money_surf, saved_money_rect)
        
        if self.game_over:
            if self.current_question >= len(self.questions):
                result_text = f"Parabéns! Você completou o Quiz e ganhou R$ {self.accumulated_money:,}!"
            else:
                result_text = f"Fim de jogo! Você ganhou R$ {self.saved_money:,}."
            
            result_surf = self.title_font.render(result_text, True, (50, 50, 50))
            result_rect = result_surf.get_rect(center=(self.left_panel.rect.width // 2 + 20, self.height // 3))
            self.screen.blit(result_surf, result_rect)
            
            self.quit_button.text = "Sair"
            self.quit_button.text_surf = self.title_font.render(
                self.quit_button.text, True, (50, 50, 50)
            )
            self.quit_button.text_rect = self.quit_button.text_surf.get_rect(
                center=self.quit_button.rect.center
            )
            
            self.quit_button.rect.centerx = self.left_panel.rect.width // 2 + 20
            
            self.quit_button.draw(self.screen)
            
        else:
            self.question_panel.draw(self.screen)
            
            question_text = self.questions[self.current_question].text
            lines = self.wrap_text(question_text, self.question_font, self.left_panel.rect.width - 60)
            
            for i, line in enumerate(lines):
                line_surf = self.question_font.render(line, True, (50, 50, 50))
                line_rect = line_surf.get_rect(midtop=(self.left_panel.rect.width // 2 + 20, 80 + i * 30))
                self.screen.blit(line_surf, line_rect)
            
            for button in self.option_buttons:
                button.draw(self.screen)
            
            if self.show_result:
                self.next_button.draw(self.screen)
                
                value_text = f"Valor: R$ {self.question_generator.get_money_for_question(self.current_question):,}"
                value_surf = self.info_font.render(value_text, True, (50, 50, 50))
                value_rect = value_surf.get_rect(center=(self.left_panel.rect.width // 2 + 20, self.height - 120))
                self.screen.blit(value_surf, value_rect)
                
                if self.answer_correct:
                    feedback_text = "Resposta Correta!"
                    feedback_color = COLORS.get("success", (75, 181, 67))
                else:
                    feedback_text = "Resposta Incorreta!"
                    feedback_color = COLORS.get("error", (232, 77, 77))
                
                feedback_surf = self.title_font.render(feedback_text, True, feedback_color)
                feedback_rect = feedback_surf.get_rect(center=(self.left_panel.rect.width // 2 + 20, self.height - 160))
                self.screen.blit(feedback_surf, feedback_rect)
            
            self.quit_button.draw(self.screen)
            self.help_button.draw(self.screen)
            
            # Mostrar botões de ajuda se necessário
            if self.show_help_options:
                for button in self.help_buttons:
                    button.draw(self.screen)
            
            if not self.show_result:
                self.next_button.draw(self.screen)
            
            # Mostrar dica se necessário
            if self.show_hint:
                # Desenhar overlay semi-transparente
                overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 128))  # Preto semi-transparente
                self.screen.blit(overlay, (0, 0))
                
                # Desenhar painel da dica
                self.hint_panel.draw(self.screen)
                
                # Desenhar texto da dica
                hint_text = self.questions[self.current_question].hint
                hint_lines = self.wrap_text(hint_text, self.question_font, self.hint_panel.rect.width - 40)
                
                for i, line in enumerate(hint_lines):
                    line_surf = self.question_font.render(line, True, (50, 50, 50))
                    line_rect = line_surf.get_rect(center=(self.hint_panel.rect.centerx, self.hint_panel.rect.y + 40 + i * 30))
                    self.screen.blit(line_surf, line_rect)
                
                # Desenhar botão de fechar
                self.close_hint_button.draw(self.screen)
        
        pygame.display.flip()
    
    def wrap_text(self, text, font, max_width):
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_width, _ = font.size(test_line)
            
            if test_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
                    current_line = []
        
        if current_line:
            lines.append(' '.join(current_line))
            
        return lines
    
    def run(self):
        while self.running:
            result = self.handle_events()
            if result["action"] != "none":
                return result
            self.update()
            self.draw()
            pygame.time.Clock().tick(60)
        
        return {"action": "exit"}