import pygame
import sys
from pygame.locals import *
from databse.data_manager import get_materia_id_by_name, get_serie_id_by_name, get_difficulty_id_by_name
from databse.db_connector import getConnection

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
DEFAULT_DIFFICULTY_LEVELS = ["Automatico", "Facil", "Medio", "Dificil"]

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
        "text": (60, 60, 60)
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

class GameConfigScreen:
    def __init__(self, screen, user_data):
        self.screen = screen
        self.running = True
        self.width, self.height = screen.get_size()
        self.user_data = user_data  # Contém user_type (student/teacher) e username
       
        # Cores do design neumorfista
        self.bg_color = COLORS["background"]
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
        self.selected_difficulty = "Automatico"  # Padrão é automático
       
        # Criar elementos de UI
        center_x = self.width // 2
       
        # Painel principal (aumentado para acomodar a nova seção)
        self.main_panel = NeumorphicPanel(
            center_x - 350, 30,
            700, 540,
            self.bg_color, self.light_shadow, self.dark_shadow
        )
       
        # Criar botões para matérias
        self.subject_buttons = self.create_subject_buttons()
       
        # Criar botões para séries (anos)
        self.grade_buttons = self.create_grade_buttons()
       
        # Criar botões para dificuldade
        self.difficulty_buttons = self.create_difficulty_buttons()
       
        # Botões de navegação (movidos mais para baixo)
        self.start_button = NeumorphicButton(
            center_x + 50, 500,
            200, 50,
            self.bg_color, self.light_shadow, self.dark_shadow,
            (75, 181, 67),  # Verde
            "INICIAR", self.subtitle_font
        )
       
        self.back_button = NeumorphicButton(
            center_x - 250, 500,
            200, 50,
            self.bg_color, self.light_shadow, self.dark_shadow,
            (232, 77, 77),  # Vermelho
            "VOLTAR", self.subtitle_font
        )
       
    def create_subject_buttons(self):
        buttons = []
        center_x = self.width // 2
       
        # Botões para matérias (layout em grade 4x2) - posição ajustada
        button_width = 150
        button_height = 50
        margin_x = 20
        margin_y = 15
        start_x = center_x - (button_width * 2 + margin_x/2)
        start_y = 160  # Movido um pouco para baixo
       
        for i, subject in enumerate(SUBJECTS):
            row = i // 4
            col = i % 4
           
            x = start_x + col * (button_width + margin_x)
            y = start_y + row * (button_height + margin_y)
           
            buttons.append(NeumorphicButton(
                x, y,
                button_width, button_height,
                self.bg_color, self.light_shadow, self.dark_shadow,
                self.accent_color, subject, self.text_font,
                is_toggle=True, is_active=False
            ))
           
        return buttons
   
    def create_grade_buttons(self):
        buttons = []
        center_x = self.width // 2
       
        # Botões para séries (layout horizontal) - posição ajustada
        button_width = 150
        button_height = 50
        margin_x = 20
        start_x = center_x - (button_width * 1.5 + margin_x)
        start_y = 310  # Movido para baixo
       
        for i, grade in enumerate(GRADE_LEVELS):
            x = start_x + i * (button_width + margin_x)
           
            buttons.append(NeumorphicButton(
                x, start_y,
                button_width, button_height,
                self.bg_color, self.light_shadow, self.dark_shadow,
                self.accent_color, grade, self.text_font,
                is_toggle=True, is_active=False
            ))
           
        return buttons
   
    def create_difficulty_buttons(self):
        buttons = []
        center_x = self.width // 2
       
        # Botões para dificuldade (layout horizontal)
        button_width = 140
        button_height = 50
        margin_x = 15
        total_width = button_width * 4 + margin_x * 3
        start_x = center_x - total_width // 2
        start_y = 410  # Nova seção
       
        # Cores diferentes para cada nível de dificuldade
        difficulty_colors = {
            "Automatico": (106, 130, 251),  # Azul padrão
            "Facil": (75, 181, 67),         # Verde
            "Medio": (232, 181, 12),        # Amarelo
            "Dificil": (232, 77, 77)        # Vermelho
        }
       
        for i, difficulty in enumerate(DIFFICULTY_LEVELS):
            x = start_x + i * (button_width + margin_x)
           
            # Definir se o botão está ativo (Automático é o padrão)
            is_active = (difficulty == "Automatico")
           
            buttons.append(NeumorphicButton(
                x, start_y,
                button_width, button_height,
                self.bg_color, self.light_shadow, self.dark_shadow,
                difficulty_colors[difficulty], difficulty, self.text_font,
                is_toggle=True, is_active=is_active
            ))
           
        return buttons
    
    def _prepare_game_settings(self):
        """
        Prepara os dados de configuração do jogo, buscando IDs no banco
        com base nas seleções de NOME feitas na UI.
        Retorna um dicionário com os parâmetros para o quiz, ou None se houver erro.
        """
        # 1. Obtenha os NOMES selecionados na UI
        subject_name = self.selected_subject
        grade_name = self.selected_grade
        difficulty_name = self.selected_difficulty # Pode ser "Automatico", "Facil", etc.

        # 2. Validação básica
        if not all([subject_name, grade_name, difficulty_name]):
            # Defina uma mensagem de erro para a UI aqui, se tiver esse mecanismo
            # Ex: self.error_message = "Selecione Matéria, Série e Dificuldade!"
            # self.message_timer = 180 
            print("ERRO (GameConfigScreen): Opções não selecionadas.")
            return None # Indica que não deve prosseguir

        # 3. Busque os IDs correspondentes no banco de dados
        try:
            print(f"GameConfigScreen: Buscando ID para Matéria '{subject_name}'...")
            subject_id = get_materia_id_by_name(subject_name, getConnection)
            
            print(f"GameConfigScreen: Buscando ID para Série '{grade_name}'...")
            grade_id = get_serie_id_by_name(grade_name, getConnection)
            
            difficulty_id = None # Será None se difficulty_name for "Automatico"
            if difficulty_name != "Automatico":
                print(f"GameConfigScreen: Buscando ID para Dificuldade '{difficulty_name}'...")
                difficulty_id = get_difficulty_id_by_name(difficulty_name, getConnection)
                if difficulty_id is None: # Dificuldade específica selecionada mas não encontrada
                    # self.error_message = f"Dificuldade '{difficulty_name}' não encontrada."
                    print(f"GameConfigScreen ERRO: Dificuldade '{difficulty_name}' não encontrada no sistema.")
                    return None
            
        except Exception as e:
            # self.error_message = f"Erro de Conexão/DB: {e}"
            print(f"GameConfigScreen ERRO: Erro de Conexão/DB ao buscar IDs: {e}")
            return None

        # 4. Verifique se os IDs foram encontrados
        if subject_id is None:
            # self.error_message = f"Matéria '{subject_name}' não encontrada."
            print(f"GameConfigScreen ERRO: Matéria '{subject_name}' não encontrada no banco.")
            return None
        
        if grade_id is None:
            # self.error_message = f"Série '{grade_name}' não encontrada."
            print(f"GameConfigScreen ERRO: Série '{grade_name}' não encontrada no banco.")
            return None
        
        print(f"GameConfigScreen: IDs preparados - MatériaID: {subject_id}, SérieID: {grade_id}, DificuldadeID: {difficulty_id} (Modo: {difficulty_name})")

        # 5. Monte o dicionário de configuração do jogo para a QuizScreen
        game_settings_data = {
            "subject_name": subject_name,
            "subject_id": subject_id,
            "grade_name": grade_name, 
            "grade_id": grade_id,
            "difficulty_name_selected": difficulty_name,
            "difficulty_id": difficulty_id 
        }
        
        print(f"DEBUG: Nomes Selecionados: ('{subject_name}', '{grade_name}', '{difficulty_name}')")
        print(f"DEBUG: IDs Encontrados: (Matéria: {subject_id}, Série: {grade_id}, Dificuldade: {difficulty_id})")

        
        return game_settings_data
   
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Variável para controlar se um botão de filtro foi clicado e o loop deve reiniciar
                filter_button_clicked = False

                # Verificar cliques nos botões de matéria
                for i, button in enumerate(self.subject_buttons):
                    if button.is_clicked(mouse_pos):
                        for j, other_button in enumerate(self.subject_buttons):
                            other_button.is_active = (j == i)
                        self.selected_subject = SUBJECTS[i]
                        filter_button_clicked = True
                        break # Processou um clique, sai do loop de botões de matéria
                if filter_button_clicked:
                    continue # Reinicia o loop de eventos para registrar a mudança visual

                # Verificar cliques nos botões de série
                for i, button in enumerate(self.grade_buttons):
                    if button.is_clicked(mouse_pos):
                        for j, other_button in enumerate(self.grade_buttons):
                            other_button.is_active = (j == i)
                        self.selected_grade = GRADE_LEVELS[i]
                        filter_button_clicked = True
                        break
                if filter_button_clicked:
                    continue

                # Verificar cliques nos botões de dificuldade
                for i, button in enumerate(self.difficulty_buttons):
                    if button.is_clicked(mouse_pos):
                        for j, other_button in enumerate(self.difficulty_buttons):
                            other_button.is_active = (j == i)
                        self.selected_difficulty = DIFFICULTY_LEVELS[i]
                        filter_button_clicked = True
                        break
                if filter_button_clicked:
                    continue

                # Verificar clique no botão INICIAR
                if self.start_button.is_clicked(mouse_pos):
                    self.start_button.pressed = True
                    
                    # Chama o método auxiliar que busca os IDs e valida as seleções
                    game_settings = self._prepare_game_settings()
                    
                    if game_settings: # Se os parâmetros foram obtidos com sucesso (não é None)
                        return {
                            "action": "start_game",
                            # Passa o dicionário completo com nomes e IDs
                            "game_settings": game_settings 
                        }
                    else:
                        # Se for None, um erro ocorreu e a mensagem já foi impressa (e deveria ser mostrada na UI)
                        # Retorna "none" para permanecer na tela e o usuário corrigir.
                        return {"action": "none"} 

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
        self.screen.fill(self.bg_color)
       
        # Desenha o painel principal
        self.main_panel.draw(self.screen)
       
        # Desenha o título
        title_text = self.title_font.render("Configurar Jogo", True, (60, 60, 60))
        title_rect = title_text.get_rect(center=(self.width // 2, 70))
        self.screen.blit(title_text, title_rect)
       
        # Desenha subtítulo para matérias
        subject_text = self.subtitle_font.render("Selecione a Materia:", True, (60, 60, 60))
        subject_rect = subject_text.get_rect(center=(self.width // 2, 130))
        self.screen.blit(subject_text, subject_rect)
       
        # Desenha botões de matéria
        for button in self.subject_buttons:
            button.draw(self.screen)
       
        # Desenha subtítulo para séries
        grade_text = self.subtitle_font.render("Selecione a Serie:", True, (60, 60, 60))
        grade_rect = grade_text.get_rect(center=(self.width // 2, 280))
        self.screen.blit(grade_text, grade_rect)
       
        # Desenha botões de série
        for button in self.grade_buttons:
            button.draw(self.screen)
       
        # Desenha subtítulo para dificuldade
        difficulty_text = self.subtitle_font.render("Selecione a Dificuldade:", True, (60, 60, 60))
        difficulty_rect = difficulty_text.get_rect(center=(self.width // 2, 380))
        self.screen.blit(difficulty_text, difficulty_rect)
       
        # Desenha botões de dificuldade
        for button in self.difficulty_buttons:
            button.draw(self.screen)
       
        # Desenha explicação sobre o modo automático
        if self.selected_difficulty == "Automatico":
            auto_text = self.text_font.render("Modo Automatico: Inicia facil e aumenta gradualmente", True, (100, 100, 100))
            auto_rect = auto_text.get_rect(center=(self.width // 2, 470))
            self.screen.blit(auto_text, auto_rect)
        else:
            fixed_text = self.text_font.render(f"Modo {self.selected_difficulty}: Todas as questoes serao {self.selected_difficulty.lower()}s", True, (100, 100, 100))
            fixed_rect = fixed_text.get_rect(center=(self.width // 2, 470))
            self.screen.blit(fixed_text, fixed_rect)
       
        # Desenha botões de navegação
        self.start_button.draw(self.screen)
        self.back_button.draw(self.screen)
       
        # Mensagem de ajuda para o botão iniciar
        if not (self.selected_subject and self.selected_grade):
            hint_text = self.text_font.render("Selecione uma materia e uma serie para iniciar", True, (150, 150, 150))
            hint_rect = hint_text.get_rect(center=(self.width // 2, 560))
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

# Integração com Banco de Dados
# Quando implementar o MySQL, as seguintes funções serão necessárias:

def get_subject_id_from_name(subject_name):
    """
    Consulta o banco de dados para obter o ID da matéria baseado no nome
   
    Args:
        subject_name (str): Nome da matéria (ex: "Matematica")
   
    Returns:
        int: ID da matéria no banco de dados
   
    Exemplo de implementação:
    ```
    import mysql.connector
   
    connection = mysql.connector.connect(...)
    cursor = connection.cursor()
    cursor.execute("SELECT id_materia FROM materias WHERE nome_materia = %s", (subject_name,))
    result = cursor.fetchone()
    return result[0] if result else None
    ```
    """
    pass

def get_grade_id_from_name(grade_name):
    """
    Consulta o banco de dados para obter o ID da série baseado no nome
   
    Args:
        grade_name (str): Nome da série (ex: "1 Ano")
   
    Returns:
        int: ID da série no banco de dados
   
    Exemplo de implementação:
    ```
    import mysql.connector
   
    connection = mysql.connector.connect(...)
    cursor = connection.cursor()
    cursor.execute("SELECT id_serie FROM serie WHERE nome_serie = %s", (grade_name,))
    result = cursor.fetchone()
    return result[0] if result else None
    ```
    """
    pass

def get_questions_from_database(subject_id, grade_id, difficulty_mode, total_questions=15):
    """
    Consulta questões no banco de dados baseado nas configurações
   
    Args:
        subject_id (int): ID da matéria
        grade_id (int): ID da série
        difficulty_mode (str): Modo de dificuldade ("Automatico", "Facil", "Medio", "Dificil")
        total_questions (int): Número total de questões para o quiz
   
    Returns:
        list: Lista de questões no formato esperado pelo quiz
   
    Exemplo de implementação:
    ```
    import mysql.connector
   
    connection = mysql.connector.connect(...)
    cursor = connection.cursor()
   
    if difficulty_mode == "Automatico":
        # Buscar questões de todas as dificuldades proporcionalmente
        # 5 fáceis, 5 médias, 5 difíceis
        easy_questions = get_questions_by_difficulty(subject_id, grade_id, "fácil", 5)
        medium_questions = get_questions_by_difficulty(subject_id, grade_id, "média", 5)
        hard_questions = get_questions_by_difficulty(subject_id, grade_id, "difícil", 5)
        return easy_questions + medium_questions + hard_questions
    else:
        # Buscar apenas questões da dificuldade específica
        difficulty_name = difficulty_mode.lower()
        return get_questions_by_difficulty(subject_id, grade_id, difficulty_name, total_questions)
    ```
    """
    pass
