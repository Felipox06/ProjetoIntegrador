import pygame
import sys
import random
import time
from pygame.locals import *

# Importar config se existir
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

# Componentes de UI neumórficos
class NeumorphicPanel:
    def __init__(self, x, y, width, height, bg_color, light_shadow, dark_shadow, border_radius=20):
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = bg_color
        self.light_shadow = light_shadow
        self.dark_shadow = dark_shadow
        self.border_radius = border_radius

    def draw(self, surface):
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=self.border_radius)
        shadow_light = pygame.Rect(self.rect.x-3, self.rect.y-3, self.rect.width, self.rect.height)
        pygame.draw.rect(surface, self.light_shadow, shadow_light, border_radius=self.border_radius, width=3)
        shadow_dark = pygame.Rect(self.rect.x+3, self.rect.y+3, self.rect.width, self.rect.height)
        pygame.draw.rect(surface, self.dark_shadow, shadow_dark, border_radius=self.border_radius, width=3)

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
            # Desenha botão circular
            pygame.draw.circle(surface, bg_color, self.rect.center, self.rect.width // 2)
            pygame.draw.circle(surface, self.light_shadow, self.rect.center, self.rect.width // 2 - 2, 2)
            pygame.draw.circle(surface, self.dark_shadow, self.rect.center, self.rect.width // 2 + 2, 2)
            
            if is_pressed:
                pygame.draw.circle(surface, self.accent_color, self.rect.center, self.rect.width // 2 - 4)
                text_rect = self.text_surf.get_rect(center=(self.rect.centerx+1, self.rect.centery+1))
                surface.blit(self.text_surf, text_rect)
            else:
                surface.blit(self.text_surf, self.text_rect)
        else:
            # Desenha botão retangular (código original)
            if is_pressed:
                pygame.draw.rect(surface, bg_color, self.rect.inflate(-4, -4), border_radius=10)
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
                pygame.draw.rect(surface, self.light_shadow, self.rect.inflate(-2, -2), border_radius=10, width=2)
                pygame.draw.rect(surface, self.dark_shadow, self.rect.inflate(2, 2), border_radius=10, width=2)
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
        if self.current_step > 0:
            progress_width = int(self.rect.width * (self.current_step / self.total_steps))
            progress_rect = pygame.Rect(self.rect.x, self.rect.y, progress_width, self.rect.height)
            pygame.draw.rect(surface, self.progress_color, progress_rect, border_radius=5)
        pygame.draw.rect(surface, self.border_color, self.rect, border_radius=5, width=2)
        for i in range(1, self.total_steps // CHECKPOINT_INTERVALS):
            checkpoint_x = self.rect.x + (i * CHECKPOINT_INTERVALS / self.total_steps) * self.rect.width
            pygame.draw.line(surface, (100, 100, 100),
                             (checkpoint_x, self.rect.y),
                             (checkpoint_x, self.rect.y + self.rect.height), 2)

# Classe de pergunta para o Quiz
class Question:
    def __init__(self, text, options, correct_option, difficulty):
        self.text = text
        self.options = options
        self.correct_option = correct_option
        self.difficulty = difficulty  # 0: fácil, 1: médio, 2: difícil

# Gerador de perguntas mock (simulação para testes sem banco de dados)
class MockQuestionGenerator:
    def __init__(self, subject, grade):
        self.subject = subject
        self.grade = grade
        
        # Configurações para o prêmio em dinheiro por dificuldade
        self.money_values = [
            [1000, 2000, 3000, 5000, 10000],          # Fácil (perguntas 1-5)
            [20000, 30000, 50000, 100000, 200000],    # Médio (perguntas 6-10)
            [300000, 500000, 750000, 1000000, 2000000] # Difícil (perguntas 11-15)
        ]
    
    def get_questions(self, count=TOTAL_QUESTIONS):
        questions = []
        
        # Adicionar perguntas fáceis
        easy_count = min(5, count)
        for i in range(easy_count):
            question = self._generate_question(difficulty=0)
            questions.append(question)
        
        # Adicionar perguntas médias
        medium_count = min(5, count - easy_count)
        for i in range(medium_count):
            question = self._generate_question(difficulty=1)
            questions.append(question)
        
        # Adicionar perguntas difíceis
        hard_count = count - easy_count - medium_count
        for i in range(hard_count):
            question = self._generate_question(difficulty=2)
            questions.append(question)
        
        return questions
    
    def _generate_question(self, difficulty):
        # Mock questions para diferentes matérias e séries
        if self.subject == "Matematica":
            if difficulty == 0:  # Fácil
                text = "Qual é o resultado de 7 x 8?"
                options = ["54", "56", "64", "72"]
                correct = 1  # 56
            elif difficulty == 1:  # Médio
                text = "Qual é a área de um círculo com raio 5cm? (Use π = 3.14)"
                options = ["25π cm²", "10π cm²", "15π cm²", "20π cm²"]
                correct = 0  # 25π cm²
            else:  # Difícil
                text = "Qual é a solução da equação 2x² - 5x - 3 = 0?"
                options = ["x = 3 ou x = -0.5", "x = 2.5 ou x = -0.5", "x = 3 ou x = -1", "x = 2 ou x = -1.5"]
                correct = 0  # x = 3 ou x = -0.5
        
        elif self.subject == "Fisica":
            if difficulty == 0:  # Fácil
                text = "Qual é a unidade de medida da força no Sistema Internacional (SI)?"
                options = ["Watt", "Joule", "Newton", "Pascal"]
                correct = 2  # Newton
            elif difficulty == 1:  # Médio
                text = "Um objeto é lançado verticalmente para cima. No ponto mais alto da trajetória:"
                options = ["A velocidade e a aceleração são nulas", "A velocidade é nula e a aceleração é g", "A velocidade é g e a aceleração é nula", "A velocidade e a aceleração são iguais a g"]
                correct = 1  # A velocidade é nula e a aceleração é g
            else:  # Difícil
                text = "Um capacitor de placas paralelas está conectado a uma bateria. O que acontece com a capacitância se a distância entre as placas for duplicada?"
                options = ["Aumenta 2 vezes", "Diminui pela metade", "Não muda", "Aumenta 4 vezes"]
                correct = 1  # Diminui pela metade
        
        else:  # Para outras matérias
            if difficulty == 0:  # Fácil
                text = f"Pergunta fácil de {self.subject} para o {self.grade}"
                options = ["Opção A", "Opção B", "Opção C", "Opção D"]
                correct = random.randint(0, 3)
            elif difficulty == 1:  # Médio
                text = f"Pergunta média de {self.subject} para o {self.grade}"
                options = ["Opção A", "Opção B", "Opção C", "Opção D"]
                correct = random.randint(0, 3)
            else:  # Difícil
                text = f"Pergunta difícil de {self.subject} para o {self.grade}"
                options = ["Opção A", "Opção B", "Opção C", "Opção D"]
                correct = random.randint(0, 3)
                
        return Question(text, options, correct, difficulty)
    
    def get_money_for_question(self, question_number):
        # Calcular o índice baseado na dificuldade
        difficulty = 0 if question_number < 5 else 1 if question_number < 10 else 2
        value_index = question_number % 5
        return self.money_values[difficulty][value_index]

COLORS = {
    "background": (30, 180, 195),    # Azul
    "light_shadow": (30, 180, 195),  # Mesma cor que o fundo para "remover" sombra clara
    "dark_shadow": (30, 180, 195),   # Mesma cor que o fundo para "remover" sombra escura
    "accent": (251, 164, 31),        # Amarelo para a caixa principal
    "text": (0, 0, 0),
    "black": (0, 0, 0),
    "success": (75, 181, 67),
    "warning": (232, 181, 12),
    "error": (232, 77, 77),
}

class QuizScreen:
    def __init__(self, screen, user_data, game_config):
        self.screen = screen
        self.running = True
        self.width, self.height = screen.get_size()
        self.user_data = user_data
        self.game_config = game_config
        
        # Usando cores do novo dicionário COLORS
        self.bg_color = COLORS["background"]       # Fundo da tela azul
        self.light_shadow = COLORS["light_shadow"] # Para sombras claras = fundo, sombra removida
        self.dark_shadow = COLORS["dark_shadow"]   # Para sombras escuras = fundo, sombra removida
        self.accent_color = COLORS["accent"]       # Amarelo para a caixa principal
        
        # Fontes
        self.title_font = pygame.font.SysFont('Arial', 28, bold=True)
        self.question_font = pygame.font.SysFont('Arial', 22)
        self.option_font = pygame.font.SysFont('Arial', 18)
        self.info_font = pygame.font.SysFont('Arial', 16)
        
        self.question_generator = MockQuestionGenerator(
            game_config["subject"], 
            game_config["grade"]
        )
        self.questions = self.question_generator.get_questions(TOTAL_QUESTIONS)
        
        # Estado do quiz
        self.current_question = 0
        self.selected_option = None
        self.answer_correct = None
        self.accumulated_money = 0
        self.saved_money = 0
        self.game_over = False
        self.show_result = False
        self.waiting_for_next = False
        self.wait_timer = 0
        
        self.setup_ui()
        
    def setup_ui(self):
        # Painel esquerdo (questões)
        self.left_panel = NeumorphicPanel(20, 20, 
        self.width // 2 - -30, self.height - 40,  # aumentou 20px para a direita
        self.accent_color,
        self.light_shadow,
        self.dark_shadow
)
        # Painel direito (informações)
        painel_largura = 300  # mais estreito
        self.right_panel = NeumorphicPanel(
        self.width - painel_largura - 20, 20,
        painel_largura,
        self.height - 40,
        self.accent_color,
        self.light_shadow,
        self.dark_shadow
)

        # Barra de progresso (no topo do painel esquerdo)
        self.progress_bar = ProgressBar(
            40, 30,
            self.width // 2 - 90, 20,
            (220, 220, 220),
            (238, 32, 81),  # #EE2051
            (150, 150, 150),
            TOTAL_QUESTIONS
        )
        
        # Painel da pergunta (dentro do painel esquerdo)
        self.question_panel = NeumorphicPanel(
            40, 70,
            self.width // 2 - 90, 130,
            self.bg_color,
            self.light_shadow,
            self.dark_shadow,
            border_radius=15
        )
        
        # Botões de opções (dentro do painel esquerdo)
        self.option_buttons = []
        button_width = self.width // 2 - 110
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
            self.width // 2 - 80, button_bottom_y,
            60, 60,
            self.bg_color,
            self.light_shadow,
            self.dark_shadow,
            self.accent_color,
            ">", self.title_font,
            is_circular=True
        )
        
        # Botão desistir (redondo)
        self.quit_button = NeumorphicButton(
            80, button_bottom_y,
            60, 60,
            self.bg_color,
            self.light_shadow,
            self.dark_shadow,
            COLORS["error"],
            "X", self.title_font,
            is_circular=True
        )
        
        # Botão de ajuda (no painel direito)
        self.help_button = NeumorphicButton(
            self.width // 2 + (self.width // 2 - 80) // 2, button_bottom_y,
            60, 60,
            self.bg_color,
            self.light_shadow,
            self.dark_shadow,
            self.accent_color,
            "?", self.title_font,
            is_circular=True
        )
        
        self.update_question_display()

    def update_question_display(self):
        if self.current_question < len(self.questions):
            question = self.questions[self.current_question]
            
            # Atualizar textos dos botões de opções
            option_labels = ["A", "B", "C", "D"]
            for i, option in enumerate(question.options):
                self.option_buttons[i].text = f"{option_labels[i]}) {option}"
                self.option_buttons[i].text_surf = self.option_font.render(
                    self.option_buttons[i].text, True, (50, 50, 50)
                )
                self.option_buttons[i].text_rect = self.option_buttons[i].text_surf.get_rect(
                    center=self.option_buttons[i].rect.center
                )
                self.option_buttons[i].correct = None  # Resetar estado de correto/incorreto
                
            # Atualizar barra de progresso
            self.progress_bar.update(self.current_question)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Se estiver esperando para mostrar a próxima pergunta, não processar cliques
                if self.waiting_for_next:
                    continue
                
                # Se o jogo acabou, verificar apenas o botão de quit
                if self.game_over:
                    if self.quit_button.is_clicked(mouse_pos):
                        return {"action": "back_to_menu", "money_earned": self.saved_money}
                    continue
                
                # Verificar cliques nos botões de opções (apenas se ainda não tiver selecionado)
                if not self.show_result:
                    for i, button in enumerate(self.option_buttons):
                        if button.is_clicked(mouse_pos):
                            self.selected_option = i
                            self.check_answer()
                            self.show_result = True
                            break
                
                # Verificar clique no botão próxima (apenas se estiver mostrando o resultado)
                elif self.next_button.is_clicked(mouse_pos):
                    self.next_button.pressed = True
                    self.go_to_next_question()
                
                # Verificar clique no botão desistir
                elif self.quit_button.is_clicked(mouse_pos):
                    self.quit_button.pressed = True
                    if self.show_result:  # Se já mostrou o resultado, vai para a próxima
                        self.go_to_next_question()
                    else:
                        # Desistir com o dinheiro garantido
                        self.game_over = True
                        return {"action": "back_to_menu", "money_earned": self.saved_money}
                
                # Verificar clique no botão de ajuda
                elif self.help_button.is_clicked(mouse_pos):
                    self.help_button.pressed = True
                    # Aqui pode ser adicionada a lógica para mostrar ajuda
                    print("Botão de ajuda pressionado")
        
        return {"action": "none"}
    
    def check_answer(self):
        current = self.questions[self.current_question]
        self.answer_correct = (self.selected_option == current.correct_option)
        
        # Atualizar aparência dos botões
        for i, button in enumerate(self.option_buttons):
            if i == current.correct_option:
                button.correct = True
            elif i == self.selected_option and i != current.correct_option:
                button.correct = False
        
        # Atualizar dinheiro
        if self.answer_correct:
            self.accumulated_money = self.question_generator.get_money_for_question(self.current_question)
            
            # Verificar se atingiu um checkpoint
            next_question = self.current_question + 1
            if next_question % CHECKPOINT_INTERVALS == 0:
                self.saved_money = self.accumulated_money
        else:
            # Resposta errada - termina o jogo, ganha o dinheiro do último checkpoint
            self.waiting_for_next = True
            self.wait_timer = pygame.time.get_ticks()
    
    def go_to_next_question(self):
        # Resetar estado
        self.selected_option = None
        self.show_result = False
        self.next_button.pressed = False
        
        # Se errou a resposta, terminar o jogo
        if not self.answer_correct:
            self.game_over = True
            return
        
        # Avançar para a próxima pergunta
        self.current_question += 1
        
        # Verificar se terminou o quiz
        if self.current_question >= len(self.questions):
            self.game_over = True
            return
        
        # Atualizar display da próxima pergunta
        self.update_question_display()
    
    def update(self):
        # Verificar timer para próxima pergunta após resposta errada
        if self.waiting_for_next:
            current_time = pygame.time.get_ticks()
            if current_time - self.wait_timer > 2000:  # 2 segundos
                self.waiting_for_next = False
                self.go_to_next_question()
    
    def draw(self):
        # Limpa a tela com a cor de fundo
        self.screen.fill(self.bg_color)
        
        # Desenha os painéis principais
        self.left_panel.draw(self.screen)
        self.right_panel.draw(self.screen)
        
        # Desenha a barra de progresso
        self.progress_bar.draw(self.screen)
        
        # Desenha informações do quiz (no painel esquerdo)
        info_text = f"{self.game_config['subject']} - {self.game_config['grade']}"
        info_surf = self.info_font.render(info_text, True, (80, 80, 80))
        info_rect = info_surf.get_rect(topleft=(40, 40))
        self.screen.blit(info_surf, info_rect)
        
        # Desenha número da pergunta (no painel esquerdo)
        question_num_text = f"Pergunta {self.current_question + 1} de {TOTAL_QUESTIONS}"
        question_num_surf = self.info_font.render(question_num_text, True, (80, 80, 80))
        question_num_rect = question_num_surf.get_rect(midtop=(self.width // 4, 40))
        self.screen.blit(question_num_surf, question_num_rect)
        
        # Desenha informações de dinheiro (no painel direito)
        money_title = self.title_font.render("PRÊMIOS", True, (50, 50, 50))
        money_title_rect = money_title.get_rect(center=(self.width // 4 * 3, 60))
        self.screen.blit(money_title, money_title_rect)
        
        money_text = f"Acumulado: R$ {self.accumulated_money:,}"
        money_surf = self.info_font.render(money_text, True, (50, 150, 50))
        money_rect = money_surf.get_rect(center=(self.width // 4 * 3, 120))
        self.screen.blit(money_surf, money_rect)
        
        saved_money_text = f"Garantido: R$ {self.saved_money:,}"
        saved_money_surf = self.info_font.render(saved_money_text, True, (80, 80, 80))
        saved_money_rect = saved_money_surf.get_rect(center=(self.width // 4 * 3, 160))
        self.screen.blit(saved_money_surf, saved_money_rect)
        
        if self.game_over:
            # Desenha mensagem de fim de jogo (no painel esquerdo)
            if self.current_question >= len(self.questions):
                result_text = f"Parabéns! Você completou o Quiz e ganhou R$ {self.accumulated_money:,}!"
            else:
                result_text = f"Fim de jogo! Você ganhou R$ {self.saved_money:,}."
            
            result_surf = self.title_font.render(result_text, True, (50, 50, 50))
            result_rect = result_surf.get_rect(center=(self.width // 4, self.height // 3))
            self.screen.blit(result_surf, result_rect)
            
            # Atualizar botão de sair
            self.quit_button.text = "Sair"
            self.quit_button.text_surf = self.title_font.render(
                self.quit_button.text, True, (50, 50, 50)
            )
            self.quit_button.text_rect = self.quit_button.text_surf.get_rect(
                center=self.quit_button.rect.center
            )
            
            # Centralizar o botão de sair
            self.quit_button.rect.centerx = self.width // 4
            
            # Desenhar apenas o botão de quit
            self.quit_button.draw(self.screen)
            
        else:
            # Desenha o painel da pergunta
            self.question_panel.draw(self.screen)
            
            # Quebra o texto da pergunta em múltiplas linhas se necessário
            question_text = self.questions[self.current_question].text
            lines = self.wrap_text(question_text, self.question_font, self.width // 2 - 110)
            
            # Desenha cada linha da pergunta
            for i, line in enumerate(lines):
                line_surf = self.question_font.render(line, True, (50, 50, 50))
                line_rect = line_surf.get_rect(midtop=(self.width // 4, 80 + i * 30))
                self.screen.blit(line_surf, line_rect)
            
            # Desenha as opções
            for button in self.option_buttons:
                button.draw(self.screen)
            
            # Se estiver mostrando o resultado, desenhar o botão de próxima
            if self.show_result:
                self.next_button.draw(self.screen)
                
                # Mostrar valor da pergunta
                value_text = f"Valor: R$ {self.question_generator.get_money_for_question(self.current_question):,}"
                value_surf = self.info_font.render(value_text, True, (50, 50, 50))
                value_rect = value_surf.get_rect(center=(self.width // 4, self.height - 120))
                self.screen.blit(value_surf, value_rect)
                
                # Mostrar feedback da resposta
                if self.answer_correct:
                    feedback_text = "Resposta Correta!"
                    feedback_color = COLORS.get("success", (75, 181, 67))
                else:
                    feedback_text = "Resposta Incorreta!"
                    feedback_color = COLORS.get("error", (232, 77, 77))
                
                feedback_surf = self.title_font.render(feedback_text, True, feedback_color)
                feedback_rect = feedback_surf.get_rect(center=(self.width // 4, self.height - 160))
                self.screen.blit(feedback_surf, feedback_rect)
            
            # Desenha os botões inferiores
            self.quit_button.draw(self.screen)
            self.help_button.draw(self.screen)
            if not self.show_result:
                self.next_button.draw(self.screen)
        
        # Atualiza a tela
        pygame.display.flip()
    
    def wrap_text(self, text, font, max_width):
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