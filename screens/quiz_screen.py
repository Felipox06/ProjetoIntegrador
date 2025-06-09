import pygame
import sys
import random
import time
from pygame.locals import *
from databse.data_manager import search_questions_for_quiz, get_difficulty_id_by_name
from databse.db_connector import getConnection


# Importar config se existir
try:
    import config
    COLORS = config.COLORS
    CHECKPOINT_INTERVALS = config.CHECKPOINT_INTERVALS
    TOTAL_QUESTIONS = config.TOTAL_QUESTIONS
except (ImportError, AttributeError):
    COLORS = {
        "background": (30, 180, 195),     # Azul vibrante
        "light_shadow": (255, 255, 255),  # Branco para sombras claras
        "dark_shadow": (20, 140, 150),    # Azul mais escuro para sombras
        "accent": (251, 164, 31),         # Laranja/amarelo para painéis
        "text": (0, 0, 0),                # Preto para texto
        "black": (0, 0, 0),               # Preto para bordas
        "success": (75, 181, 67),         # Verde para sucesso
        "warning": (232, 181, 12),        # Amarelo para avisos
        "error": (232, 77, 77),           # Vermelho para erros
        "progress": (238, 32, 81),        # Vermelho para barra de progresso
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
        # Desenhar retângulo principal com bordas arredondadas
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=self.border_radius)
        pygame.draw.rect(surface, config.COLORS["black"], self.rect, border_radius=self.border_radius, width=1)

        # Borda preta para definição
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
       
        # Preparar superfície de texto
        self.text_surf = font.render(text, True, (50, 50, 50))
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)
   
    def is_clicked(self, pos):
        if self.is_circular:
            # Para botões circulares
            center_x, center_y = self.rect.center
            radius = self.rect.width // 2
            distance = ((pos[0] - center_x) ** 2 + (pos[1] - center_y) ** 2) ** 0.5
            return distance <= radius
        else:
            return self.rect.collidepoint(pos)
   
    def draw(self, surface):
        # Determinar se o botão está pressionado (visualmente)
        is_pressed = self.pressed or (self.is_toggle and self.is_active)
       
        # Determinar cor de fundo baseado no estado de correto/incorreto
        bg_color = self.bg_color
        if self.correct is True:  # Resposta correta
            bg_color = (200, 255, 200)  # Verde claro
        elif self.correct is False:  # Resposta incorreta
            bg_color = (255, 200, 200)  # Vermelho claro
       
        if self.is_circular:
            # Desenhar botão circular
            center = self.rect.center
            radius = self.rect.width // 2
           
            # Fundo principal
            pygame.draw.circle(surface, bg_color, center, radius)
           
            # Sombras circulares
            pygame.draw.circle(surface, self.light_shadow, center, radius - 2, 2)
            pygame.draw.circle(surface, self.dark_shadow, center, radius + 2, 2)
           
            # Borda preta
            pygame.draw.circle(surface, COLORS["black"], center, radius, width=2)
           
            if is_pressed:
                # Estado pressionado
                pygame.draw.circle(surface, self.accent_color, center, radius - 4)
                pygame.draw.circle(surface, COLORS["black"], center, radius - 4, width=2)
                text_rect = self.text_surf.get_rect(center=(center[0]+1, center[1]+1))
                surface.blit(self.text_surf, text_rect)
            else:
                # Estado normal
                surface.blit(self.text_surf, self.text_rect)
        else:
            # Desenhar botão retangular (comportamento original)
            if is_pressed:
                # Estado pressionado: inverter sombras e aplicar cor de destaque
                pygame.draw.rect(surface, bg_color, self.rect.inflate(-4, -4), border_radius=10)
                pygame.draw.rect(surface, COLORS["black"], self.rect.inflate(-4, -4), border_radius=10, width=2)
               
                # Borda com cor de destaque
                border_color = self.accent_color
                if self.correct is True:
                    border_color = COLORS.get("success", (75, 181, 67))
                elif self.correct is False:
                    border_color = COLORS.get("error", (232, 77, 77))
                   
                pygame.draw.rect(surface, border_color, self.rect, border_radius=10, width=2)
               
                # Deslocar o texto ligeiramente
                text_rect = self.text_surf.get_rect(center=(self.rect.centerx+1, self.rect.centery+1))
                surface.blit(self.text_surf, text_rect)
            else:
                # Estado normal: efeito neumórfico
                pygame.draw.rect(surface, bg_color, self.rect, border_radius=10)
               
                # Desenhar sombras
                pygame.draw.rect(surface, self.light_shadow, self.rect.inflate(-2, -2), border_radius=10, width=2)
                pygame.draw.rect(surface, self.dark_shadow, self.rect.inflate(2, 2), border_radius=10, width=2)
               
                # Borda preta
                pygame.draw.rect(surface, COLORS["black"], self.rect, border_radius=10, width=2)
               
                # Desenhar texto
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
        # Desenhar fundo
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=5)
        pygame.draw.rect(surface, COLORS["black"], self.rect, border_radius=5, width=2)
       
        # Desenhar progresso
        if self.current_step > 0:
            progress_width = int(self.rect.width * (self.current_step / self.total_steps))
            progress_rect = pygame.Rect(self.rect.x, self.rect.y, progress_width, self.rect.height)
            pygame.draw.rect(surface, self.progress_color, progress_rect, border_radius=5)
       
        # Desenhar borda
        pygame.draw.rect(surface, self.border_color, self.rect, border_radius=5, width=2)
       
        # Desenhar marcadores de checkpoint
        for i in range(1, self.total_steps // CHECKPOINT_INTERVALS):
            checkpoint_x = self.rect.x + (i * CHECKPOINT_INTERVALS / self.total_steps) * self.rect.width
            pygame.draw.line(surface, (100, 100, 100),
                           (checkpoint_x, self.rect.y),
                           (checkpoint_x, self.rect.y + self.rect.height),
                           2)

# Classe de pergunta para o Quiz
class Question:
    def __init__(self, text, options, correct_option, difficulty):
        self.text = text
        self.options = options
        self.correct_option = correct_option
        self.difficulty = difficulty  # 0: fácil, 1: médio, 2: difícil
       
        # Sistema de ajuda - cada pergunta pode ter poderes usados uma vez
        self.used_help = {
            "skip": False,
            "eliminate": False,
            "hint": False
        }
       
        # Gerar dica automaticamente
        self.hint = self.generate_hint()
   
    def generate_hint(self):
        """Gera dicas específicas baseadas no conteúdo da pergunta"""
        # Dicas para Matemática
        if "7 x 8" in self.text:
            return "Dica: Lembre-se da tabuada do 7 ou do 8. Pode usar os dedos!"
        elif "área de um círculo" in self.text:
            return "Dica: A fórmula da área do círculo é π × r². O raio ao quadrado!"
        elif "equação 2x²" in self.text or "2x² - 5x - 3" in self.text:
            return "Dica: Use a fórmula de Bhaskara: x = (-b ± √(b² - 4ac)) / 2a"
        elif "perímetro" in self.text and "quadrado" in self.text:
            return "Dica: Perímetro do quadrado = 4 × lado"
        elif "derivada" in self.text:
            return "Dica: A derivada de ax^n é n×ax^(n-1)"
        elif "log" in self.text:
            return "Dica: log₂(64) = ? significa 2^? = 64"
       
        # Dicas para Física
        elif "unidade de medida da força" in self.text:
            return "Dica: A unidade recebeu o nome de um famoso cientista inglês."
        elif "lançado verticalmente" in self.text:
            return "Dica: No ponto mais alto, a velocidade é zero, mas a gravidade continua agindo."
        elif "capacitor de placas paralelas" in self.text:
            return "Dica: A capacitância é inversamente proporcional à distância entre as placas."
        elif "temperatura" in self.text and "água" in self.text:
            return "Dica: Pense na temperatura de fervura da água ao nível do mar."
        elif "velocidade da luz" in self.text:
            return "Dica: É uma constante física muito importante, aproximadamente 300.000 km/s."
        elif "energia de ligação" in self.text:
            return "Dica: O hélio-4 tem uma energia de ligação por núcleon bem específica."
       
        # Dicas para outras matérias
        elif "capital" in self.text and "França" in self.text:
            return "Dica: É a cidade do amor e da Torre Eiffel!"
        elif "fórmula química" in self.text and "água" in self.text:
            return "Dica: Duas moléculas de hidrogênio e uma de oxigênio."
        elif "Dom Casmurro" in self.text:
            return "Dica: Foi escrito pelo autor de O Cortiço e Memórias Póstumas."
        elif "linfócitos" in self.text and "anticorpos" in self.text:
            return "Dica: São células B, diferentes dos linfócitos T."
        elif "fotossíntese" in self.text:
            return "Dica: É o 'açúcar' que as plantas produzem com luz solar."
       
        # Dica genérica baseada na dificuldade
        if self.difficulty == 0:
            return "Dica: Esta é uma pergunta básica. Pense nos conceitos fundamentais!"
        elif self.difficulty == 1:
            return "Dica: Lembre-se das fórmulas e conceitos intermediários da matéria."
        else:
            return "Dica: Esta pergunta requer conhecimento avançado. Analise todas as opções cuidadosamente!"

class QuizScreen:
    DEFAULT_MONEY_VALUES = [
        [1000, 2000, 3000, 5000, 10000],          # Fácil (nível 0)
        [20000, 30000, 50000, 100000, 200000],    # Médio (nível 1)
        [300000, 500000, 750000, 1000000, 2000000] # Difícil (nível 2)
    ]
    
    def __init__(self, screen, user_data, game_config):
        self.screen = screen
        self.running = True
        self.width, self.height = screen.get_size()
        self.user_data = user_data  
        self.game_config = game_config  
       
        # Cores 
        self.bg_color = COLORS.get("background", (240, 240, 240))
        self.light_shadow = COLORS.get("light_shadow", (255, 255, 255))
        self.dark_shadow = COLORS.get("dark_shadow", (200, 200, 200))
        self.accent_color = COLORS.get("accent", (251, 164, 31))
        self.warning_color = COLORS.get("warning", (232, 181, 12))
        self.error_color = COLORS.get("error", (232, 77, 77))
        self.progress_color = COLORS.get("progress", (238, 32, 81))

       
        # Usar fonte padrão do sistema
        self.title_font = pygame.font.SysFont('Arial', 28, bold=True)
        self.question_font = pygame.font.SysFont('Arial', 22)
        self.option_font = pygame.font.SysFont('Arial', 18)
        self.info_font = pygame.font.SysFont('Arial', 16)
        self.small_font = pygame.font.SysFont('Arial', 14)
       
        # Gerar perguntas para o quiz (com suporte a dificuldade)
        print(f"QuizScreen: Configurações recebidas para buscar questões: {self.game_config}")
        self.questions = [] # Inicializa como lista vazia por segurança
        try:
            # Chama a função do data_manager
            self.questions = search_questions_for_quiz(
                subject_name=self.game_config.get("subject_name"),
                grade_name=self.game_config.get("grade_name"),
                difficulty_name=self.game_config.get("difficulty_name_selected"),
                connection = getConnection()
            )
            for question_dict in self.questions:
                question_dict["used_help"] = {"skip": False, "eliminate": False, "hint": False}
        except NameError as ne:
            print(f"Erro de Configuração (QuizScreen): Função não encontrada. Verifique os imports. {ne}")
        except Exception as e:
            print(f"Erro inesperado (QuizScreen) ao carregar questões: {e}")

        # Verifica se as questões foram carregadas para definir o estado do jogo
        if not self.questions:
            self.error_message = "Não há questões para esta configuração."
            self.message_timer = 180 
            self.game_over = True     
            print(f"AVISO (QuizScreen): Nenhuma questão carregada. Jogo não pode iniciar.")
        else:
            self.game_over = False
            print(f"QuizScreen: {len(self.questions)} questões carregadas do banco.")

        # Prepara a lógica de pontuação (cálculo de dinheiro)
        self.money_values = self.DEFAULT_MONEY_VALUES 
        self.db_id_to_score_level_map = {} 
        if not self.game_over: 
            try:
                # Busca os IDs das dificuldades uma vez para usar no cálculo de score
                id_facil = get_difficulty_id_by_name("Facil", getConnection)
                id_medio = get_difficulty_id_by_name("Medio", getConnection)
                id_dificil = get_difficulty_id_by_name("Dificil", getConnection)

                if id_facil is not None: self.db_id_to_score_level_map[id_facil] = 0
                if id_medio is not None: self.db_id_to_score_level_map[id_medio] = 1
                if id_dificil is not None: self.db_id_to_score_level_map[id_dificil] = 2
                
                print(f"DEBUG QuizScreen: Mapa de dificuldade para score: {self.db_id_to_score_level_map}")

            except Exception as e:
                print(f"Erro ao buscar IDs de dificuldade para o mapa de score: {e}")
                

        # Estado do quiz
        self.current_question = 0
        self.selected_option = None  # Opção selecionada visualmente (não confirmada)
        self.confirmed_option = None  # Opção confirmada (processada)
        self.answer_correct = None
        self.accumulated_money = 0
        self.saved_money = 0  # Dinheiro garantido nos checkpoints
        self.game_over = False
        self.show_result = False
        self.waiting_for_next = False
        self.wait_timer = 0
        self.auto_advance = False  # Para controlar avanço automático
       
        # Estado do sistema de ajuda
        self.show_help_options = False
        self.show_hint = False
        self.help_buttons = []
       
        # Criar elementos de UI
        self.setup_ui()
       
    def setup_ui(self):
        # Layout em dois painéis
        left_panel_width = int(self.width * 0.75) - 30  
        right_panel_width = self.width - left_panel_width - 40 
       
        # Painel esquerdo (questões e controles principais)
        self.left_panel = NeumorphicPanel(
            20, 20,
            left_panel_width,
            self.height - 40,
            self.accent_color,
            self.light_shadow,
            self.dark_shadow
        )
       
        # Painel direito (informações e ajuda)
        self.right_panel = NeumorphicPanel(
            left_panel_width + 30, 20,
            right_panel_width,
            self.height - 40,
            self.accent_color,
            self.light_shadow,
            self.dark_shadow
        )

        self.progress_bar = ProgressBar(
        40, 30,
        left_panel_width - 40, 20,
        COLORS.get("background", (220, 220, 220)),  # Cor de fundo da barra
        COLORS.get("progress", (238, 32, 81)),      # Cor de progresso (vermelho)
        COLORS.get("black", (0, 0, 0)),             # Cor da borda
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
       
        # Painel da dica (modal)
        self.hint_panel = NeumorphicPanel(
            self.width // 2 - 200,
            self.height // 2 - 100,
            400, 200,
            self.warning_color,
            self.light_shadow,
            self.dark_shadow,
            border_radius=15
        )
       
        # Botão para fechar a dica
        self.close_hint_button = NeumorphicButton(
            self.width // 2 - 20,
            self.height // 2 + 60,
            40, 40,
            self.warning_color,
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
       
        for i in range(4):  # 4 opções (A, B, C, D)
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
       
        # Botão confirmar resposta (circular) - renomeado de "próxima"
        self.confirm_button = NeumorphicButton(
            left_panel_width // 2 + 215,
            button_bottom_y, 60, 60,
            self.bg_color,
            self.light_shadow,
            self.dark_shadow,
            self.accent_color,
            "✓", self.title_font,  # Mudado de ">" para "✓"
            is_circular=True
        )
       
        # Botão desistir (circular)
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
       
        # Botão de ajuda (no painel direito)
        self.help_button = NeumorphicButton(
            left_panel_width + 30 + (right_panel_width // 2) - 30,
            button_bottom_y - 100,  # Movido para cima
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
        help_button_y_start = button_bottom_y - 200
       
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
            left_panel_width + 50,
            help_button_y_start + 15,
            help_button_width, help_button_height,
            self.bg_color,
            self.light_shadow,
            self.dark_shadow,
            self.accent_color,
            "Eliminar Alternativa", self.small_font
        )
       
        self.hint_button = NeumorphicButton(
            left_panel_width + 50,
            help_button_y_start + 60,
            help_button_width, help_button_height,
            self.bg_color,
            self.light_shadow,
            self.dark_shadow,
            self.accent_color,
            "Dica sobre o Tema", self.small_font
        )
       
        self.help_buttons = [self.skip_button, self.eliminate_button, self.hint_button]
       
        # Atualizar textos dos botões de opções
        self.update_question_display()
       
    def update_question_display(self):
        """
        Atualiza a UI para mostrar a pergunta e as opções atuais.
        """
        if self.current_question < len(self.questions):
            question_data = self.questions[self.current_question] 
            
            option_labels = ["A", "B", "C", "D"]
            question_options = question_data.get("options", []) 
            
            for i, option_text in enumerate(question_options):
                if i < len(self.option_buttons):
                    button = self.option_buttons[i]
                    button.text = f"{option_labels[i]}) {option_text}"
                    button.text_surf = self.option_font.render(
                        button.text, True, (50, 50, 50)
                    )
                    button.text_rect = button.text_surf.get_rect(
                        center=button.rect.center
                    )
                    button.correct = None 
            
            # Resetar seleção e estados do quiz 
            self.selected_option = None
            self.confirmed_option = None
            self.auto_advance = False
                
            # Atualizar barra de progresso
            self.progress_bar.update(self.current_question)
   
    def handle_help_button(self, button):
        """Processa os botões de ajuda"""
        # current_question_data é um dicionário da lista self.questions
        current_question_data = self.questions[self.current_question]
    
        if button == self.skip_button and not current_question_data["used_help"]["skip"]:
            # Altera o valor dentro do dicionário
            current_question_data["used_help"]["skip"] = True
        
            # Resetar estado antes de pular
            self.selected_option = None
            self.confirmed_option = None
            self.show_result = False
            self.auto_advance = False
            self.waiting_for_next = False
            self.go_to_next_question()
        
        elif button == self.eliminate_button and not current_question_data["used_help"]["eliminate"]:
            # Altera o valor dentro do dicionário
            current_question_data["used_help"]["eliminate"] = True
        
            options_to_eliminate = 2
            # Acessa a opção correta usando a chave do dicionário
            correct_index = current_question_data.get("correct_option")
        
            # Encontra índices das alternativas incorretas
            wrong_indices = [i for i in range(4) if i != correct_index]
            random.shuffle(wrong_indices)
        
            # Elimina até 2 alternativas incorretas
            for i in wrong_indices[:options_to_eliminate]:
                # Limpa o texto dos botões correspondentes
                self.option_buttons[i].text = ""
                self.option_buttons[i].text_surf = self.option_font.render("", True, (50, 50, 50))
            
        elif button == self.hint_button and not current_question_data["used_help"]["hint"]:
            # Altera o valor dentro do dicionário
            current_question_data["used_help"]["hint"] = True
            self.show_hint = True
   
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
               
                # Verificar clique no botão desistir - SEMPRE sai do jogo
                if self.quit_button.is_clicked(mouse_pos):
                    self.quit_button.pressed = True
                    return {"action": "back_to_menu", "money_earned": self.saved_money}
               
                # Verificar cliques nos botões de opções (apenas selecionar visualmente)
                if not self.show_result and not self.show_hint:
                    for i, button in enumerate(self.option_buttons):
                        if button.is_clicked(mouse_pos):
                            self.selected_option = i  # Apenas marca visualmente
                            break
               
                # Verificar clique no botão confirmar (processar resposta)
                if self.confirm_button.is_clicked(mouse_pos) and not self.waiting_for_next:
                    self.confirm_button.pressed = True
                   
                    if self.selected_option is not None and not self.show_result:
                        # Se tem opção selecionada e ainda não processou, confirma e processa
                        self.confirmed_option = self.selected_option
                        self.check_answer()
                        self.show_result = True
       
        return {"action": "none"}
    
    def get_money_for_question(self, current_question_index):
        """
        Calcula o valor da questão atual baseado na dificuldade do modo de jogo
        ou na dificuldade da própria questão vinda do banco.
        """
        if not self.questions or current_question_index >= len(self.questions):
            return 0

        difficulty_level_for_scoring = 0 
        difficulty_mode_selected = self.game_config.get("difficulty_name_selected")

        if difficulty_mode_selected == "Automatico":
            # No modo automático, a dificuldade é baseada no índice da pergunta no quiz
            if current_question_index < CHECKPOINT_INTERVALS:       # Perguntas 0-4
                difficulty_level_for_scoring = 0  # Nível Fácil
            elif current_question_index < CHECKPOINT_INTERVALS * 2: # Perguntas 5-9
                difficulty_level_for_scoring = 1  # Nível Médio
            else: # Perguntas 10-14
                difficulty_level_for_scoring = 2  # Nível Difícil
        else:
            # No modo de dificuldade fixa, usa o ID da dificuldade da questão atual
            current_question_data = self.questions[current_question_index]
            question_db_difficulty_id = current_question_data.get("difficulty_id")
            difficulty_level_for_scoring = self.db_id_to_score_level_map.get(question_db_difficulty_id, 0)
        
        value_index = current_question_index % CHECKPOINT_INTERVALS
        
        try:
            return self.money_values[difficulty_level_for_scoring][value_index]
        except IndexError:
            print(f"Erro ao buscar valor para questão: nível={difficulty_level_for_scoring}, índice={value_index}")
            return 0
   
    def check_answer(self):
        # Garante que não haverá erro se a lista de questões estiver vazia ou o índice for inválido
        if self.current_question >= len(self.questions):
            print("AVISO (check_answer): Tentativa de checar resposta para uma questão inválida.")
            self.game_over = True
            return

        # Pega os dados da questão atual (que é um dicionário)
        current_q_data = self.questions[self.current_question]
        
        # Verifica se a resposta está correta usando a chave do dicionário
        self.answer_correct = (self.confirmed_option == current_q_data.get("correct_option"))
        
        # --- Lógica para colorir os botões de resposta (importante para feedback visual) ---
        for i, button in enumerate(self.option_buttons):
            if i == current_q_data.get("correct_option"):
                # Marca o botão da resposta correta
                button.correct = True
            elif i == self.confirmed_option and not self.answer_correct:
                # Marca o botão da resposta incorreta que o usuário selecionou
                button.correct = False
        
        # --- Lógica para atualizar dinheiro e estado do jogo ---
        if self.answer_correct:
            # Se a resposta estiver correta, chama o novo método para calcular a pontuação
            self.accumulated_money = self.get_money_for_question(self.current_question)
            
            # Verifica se atingiu um checkpoint para salvar o dinheiro
            next_question_index = self.current_question + 1
            if next_question_index % CHECKPOINT_INTERVALS == 0:
                self.saved_money = self.accumulated_money
            
            # Configura timers para avançar para a próxima questão automaticamente
            self.auto_advance = True
            self.waiting_for_next = True
            self.wait_timer = pygame.time.get_ticks()
        else:
            # Se a resposta estiver errada, configura um timer para mostrar o resultado
            # e, depois do timer, o jogo terminará (a lógica para self.game_over = True
            # está no seu método `update()`)
            self.waiting_for_next = True
            self.wait_timer = pygame.time.get_ticks()
   
    def go_to_next_question(self):
        # Resetar estado
        self.selected_option = None
        self.confirmed_option = None
        self.show_result = False
        self.confirm_button.pressed = False
        self.show_help_options = False
        self.show_hint = False
        self.auto_advance = False
       
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
        # Verificar timer para próxima pergunta após resposta
        if self.waiting_for_next:
            current_time = pygame.time.get_ticks()
            if current_time - self.wait_timer > 2000:  # 2 segundos
                self.waiting_for_next = False
               
                if self.auto_advance and self.answer_correct:
                    # Avanço automático para resposta correta
                    self.auto_advance = False
                    self.go_to_next_question()
                elif not self.answer_correct:
                    # Resposta errada - terminar o jogo
                    self.game_over = True
   
    def draw(self):
        # Limpa a tela com a cor de fundo
        self.screen.fill(self.bg_color)
       
        # Desenha os painéis principais
        self.left_panel.draw(self.screen)
        self.right_panel.draw(self.screen)
       
        # Desenha a barra de progresso
        self.progress_bar.draw(self.screen)
       
        # Informações do quiz (no painel esquerdo)
        difficulty_mode = self.game_config.get("difficulty", "Automatico")
        info_text = f"{self.game_config.get('subject_name', '')} - {self.game_config.get('grade_name', '')}"
        info_surf = self.info_font.render(info_text, True, (80, 80, 80))
        info_rect = info_surf.get_rect(topleft=(40, 50))
        self.screen.blit(info_surf, info_rect)
       
        # Desenha número da pergunta
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
            # Desenha mensagem de fim de jogo
            if self.current_question >= len(self.questions):
                result_text = f"Parabéns! Você completou o Quiz e ganhou R$ {self.accumulated_money:,}!"
            else:
                result_text = f"Fim de jogo! Você ganhou R$ {self.saved_money:,}."
           
            result_surf = self.title_font.render(result_text, True, (50, 50, 50))
            result_rect = result_surf.get_rect(center=(self.left_panel.rect.width // 2 + 20, self.height // 3))
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
            self.quit_button.rect.centerx = self.left_panel.rect.width // 2 + 20
           
            # Desenhar apenas o botão de quit
            self.quit_button.draw(self.screen)
           
        else:
            # Desenha o painel da pergunta
            self.question_panel.draw(self.screen)
           
            # Quebra o texto da pergunta em múltiplas linhas se necessário
            question_text = self.questions[self.current_question].get("text", "")
            lines = self.wrap_text(question_text, self.question_font, self.left_panel.rect.width - 60)
           
            # Desenha cada linha da pergunta
            for i, line in enumerate(lines):
                line_surf = self.question_font.render(line, True, (50, 50, 50))
                line_rect = line_surf.get_rect(midtop=(self.left_panel.rect.width // 2 + 20, 80 + i * 30))
                self.screen.blit(line_surf, line_rect)
           
            # Desenha as opções com destaque visual para selecionada
            for i, button in enumerate(self.option_buttons):
                # Destacar opção selecionada mas não confirmada
                if i == self.selected_option and not self.show_result:
                    # Salvar cor original
                    original_bg = button.bg_color
                    # Aplicar cor de seleção temporária
                    button.bg_color = (200, 220, 255)  # Azul claro para seleção
                    button.draw(self.screen)
                    # Restaurar cor original
                    button.bg_color = original_bg
                else:
                    button.draw(self.screen)
           
            # Se estiver mostrando o resultado, desenhar feedback
            if self.show_result:
                # Mostrar valor da pergunta
                value_text = f"Valor: R$ {self.get_money_for_question(self.current_question):,}"
                value_surf = self.info_font.render(value_text, True, (50, 50, 50))
                value_rect = value_surf.get_rect(center=(self.left_panel.rect.width // 2 + 20, self.height - 120))
                self.screen.blit(value_surf, value_rect)
               
                # Mostrar feedback da resposta
                if self.answer_correct:
                    feedback_text = "Resposta Correta!"
                    feedback_color = COLORS.get("success", (75, 181, 67))
                   
                    # Mostrar mensagem de avanço automático
                    if self.waiting_for_next:
                        auto_text = "Avançando automaticamente..."
                        auto_surf = self.small_font.render(auto_text, True, (100, 100, 100))
                        auto_rect = auto_surf.get_rect(center=(self.left_panel.rect.width // 2 + 20, self.height - 140))
                        self.screen.blit(auto_surf, auto_rect)
                else:
                    feedback_text = "Resposta Incorreta!"
                    feedback_color = COLORS.get("error", (232, 77, 77))
               
                feedback_surf = self.title_font.render(feedback_text, True, feedback_color)
                feedback_rect = feedback_surf.get_rect(center=(self.left_panel.rect.width // 2 + 20, self.height - 160))
                self.screen.blit(feedback_surf, feedback_rect)
            else:
                # Mostrar botão confirmar apenas se tem opção selecionada
                if self.selected_option is not None:
                    self.confirm_button.draw(self.screen)
                   
                    # Mostrar instrução
                    instruction_text = "Clique em ✓ para confirmar sua resposta"
                    instruction_surf = self.small_font.render(instruction_text, True, (100, 100, 100))
                    instruction_rect = instruction_surf.get_rect(center=(self.left_panel.rect.width // 2 + 20, self.height - 120))
                    self.screen.blit(instruction_surf, instruction_rect)
           
            # Desenha os botões de controle
            self.quit_button.draw(self.screen)
            self.help_button.draw(self.screen)
           
            # Mostrar botões de ajuda se necessário
            if self.show_help_options:
                for button in self.help_buttons:
                    button.draw(self.screen)
           
            # Mostrar dica se necessário
            if self.show_hint:
                # Desenhar overlay semi-transparente
                overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 128))  # Preto semi-transparente
                self.screen.blit(overlay, (0, 0))
               
                # Desenhar painel da dica
                self.hint_panel.draw(self.screen)
               
                # Desenhar título da dica
                hint_title = self.title_font.render("DICA", True, (50, 50, 50))
                hint_title_rect = hint_title.get_rect(center=(self.hint_panel.rect.centerx, self.hint_panel.rect.y + 30))
                self.screen.blit(hint_title, hint_title_rect)
               
                # Desenhar texto da dica
                hint_text = self.questions[self.current_question].get("hint", "")
                hint_lines = self.wrap_text(hint_text, self.question_font, self.hint_panel.rect.width - 40)
               
                for i, line in enumerate(hint_lines):
                    line_surf = self.question_font.render(line, True, (50, 50, 50))
                    line_rect = line_surf.get_rect(center=(self.hint_panel.rect.centerx, self.hint_panel.rect.y + 70 + i * 30))
                    self.screen.blit(line_surf, line_rect)
               
                # Desenhar botão de fechar
                self.close_hint_button.draw(self.screen)
       
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

# TODO: Integração com Banco de Dados
"""
Quando implementar o MySQL, será necessário:

1. Modificar a classe Question para carregar dicas do banco:
   - Campo 'dicas' na tabela questoes
   - Método generate_hint() buscar do banco em vez de gerar

2. Modificar MockQuestionGenerator para usar consultas reais:
   - get_questions_from_database() em vez de _generate_question()
   - Buscar por matéria, série e dificuldade

3. Adicionar sistema de estatísticas de uso dos poderes:
   - Tabela de estatísticas de ajuda por usuário
   - Registro de quais poderes foram usados em cada partida

4. Exemplo de consulta para buscar questões:
   ```sql
   SELECT q.enunciado_questao, q.dicas, a.texto_alt, a.correta, d.nome_dificuldade
   FROM questoes q
   JOIN alternativas a ON q.id_questao = a.id_questao
   JOIN dificuldades d ON q.id_dificuldade = d.id_dificuldade
   WHERE q.id_materia = %s AND q.id_serie = %s
   ORDER BY RAND()
   LIMIT %s
   ```
"""