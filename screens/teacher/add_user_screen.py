# screens/teacher/add_user_screen.py
# -*- coding: utf-8 -*-

import pygame
import sys
from pygame.locals import *
from databse.data_manager import add_user_to_database # Corrigido: database
from databse.db_connector import getConnection # Corrigido: database

# Importar config se existir
try:
    import config
    COLORS = config.COLORS
    SUBJECTS = config.SUBJECTS
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

# Classes para componentes de UI neumórficos
class NeumorphicPanel:
    def __init__(self, x, y, width, height, bg_color, light_shadow, dark_shadow, border_radius=20):
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = bg_color
        self.light_shadow = light_shadow
        self.dark_shadow = dark_shadow
        self.border_radius = border_radius
    
    def draw(self, surface):
        # Desenha a sombra escura primeiro para ficar por baixo
        shadow_rect_dark_outer = pygame.Rect(self.rect.x + 3, self.rect.y + 3, self.rect.width, self.rect.height)
        pygame.draw.rect(surface, self.dark_shadow, shadow_rect_dark_outer, border_radius=self.border_radius)
        
        # Desenha a sombra clara
        shadow_rect_light_outer = pygame.Rect(self.rect.x - 3, self.rect.y - 3, self.rect.width, self.rect.height)
        pygame.draw.rect(surface, self.light_shadow, shadow_rect_light_outer, border_radius=self.border_radius)

        # Desenha o painel principal por cima das sombras
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
        
        self.text_surf = font.render(text, True, COLORS["text"]) # Usar COLORS["text"]
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)
    
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
    
    def draw(self, surface):
        is_pressed_state = self.pressed or (self.is_toggle and self.is_active)
        
        if is_pressed_state:
            # Efeito de botão pressionado (inset)
            pygame.draw.rect(surface, self.dark_shadow, self.rect, border_radius=10) # Sombra interna escura
            inner_rect = self.rect.inflate(-4, -4)
            pygame.draw.rect(surface, self.light_shadow, inner_rect, border_radius=8) # Sombra interna clara
            pygame.draw.rect(surface, self.bg_color, inner_rect.inflate(-2,-2), border_radius=6) # Fundo levemente ajustado

            text_color = self.accent_color if self.is_toggle else COLORS["text"]
            text_surf_pressed = self.font.render(self.text, True, text_color)
            text_rect_pressed = text_surf_pressed.get_rect(center=self.rect.center)
            surface.blit(text_surf_pressed, text_rect_pressed)
        else:
            # Efeito de botão elevado
            shadow_offset = 3
            shadow_color_light = self.light_shadow
            shadow_color_dark = self.dark_shadow

            # Sombra escura (embaixo e à direita)
            pygame.draw.rect(surface, shadow_color_dark, 
                             (self.rect.x + shadow_offset, self.rect.y + shadow_offset, self.rect.width, self.rect.height), 
                             border_radius=10)
            # Sombra clara (emcima e à esquerda)
            pygame.draw.rect(surface, shadow_color_light, 
                             (self.rect.x - shadow_offset, self.rect.y - shadow_offset, self.rect.width, self.rect.height), 
                             border_radius=10)
            # Botão principal
            pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=10)
            surface.blit(self.text_surf, self.text_rect)

class NeumorphicInput:
    def __init__(self, x, y, width, height, bg_color, light_shadow, dark_shadow, 
                 placeholder, font, text_color=COLORS["text"], placeholder_color=(150,150,150), 
                 is_password=False, numeric_only=False, max_length=50):
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = bg_color
        self.light_shadow = light_shadow
        self.dark_shadow = dark_shadow
        self.placeholder = placeholder
        self.font = font
        self.text_color = text_color
        self.placeholder_color = placeholder_color
        self.is_password = is_password
        self.numeric_only = numeric_only # Mantido para referência, mas não usado na lógica de add char
        self.max_length = max_length
        self.text = ""
        self.active = False
        
        self.cursor_visible = True
        self.cursor_timer = 0
        self.padding = 15 # Padding interno para o texto

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
    
    def draw(self, surface):
        # Efeito de input afundado (inset)
        # Sombra escura interna (canto superior esquerdo)
        pygame.draw.rect(surface, self.dark_shadow, self.rect, border_radius=10)
        
        # Sombra clara interna (canto inferior direito)
        inner_rect_light = self.rect.inflate(-3, -3) # Pequeno ajuste para a sombra clara não sobrepor totalmente
        pygame.draw.rect(surface, self.light_shadow, inner_rect_light, border_radius=8)
        
        # Fundo do input
        main_input_rect = self.rect.inflate(-6, -6) # Área interna para o texto
        pygame.draw.rect(surface, self.bg_color, main_input_rect, border_radius=6)

        # Linha de foco se ativo
        if self.active:
            focus_rect = self.rect.inflate(-2,-2)
            pygame.draw.rect(surface, COLORS.get("accent", (106, 130, 251)), focus_rect, width=2, border_radius=10)
        
        # Texto ou Placeholder
        if self.text:
            display_string = "*" * len(self.text) if self.is_password else self.text
            text_surface = self.font.render(display_string, True, self.text_color)
        else:
            text_surface = self.font.render(self.placeholder, True, self.placeholder_color)
        
        # Centraliza verticalmente, alinha à esquerda com padding
        text_rect = text_surface.get_rect(midleft=(self.rect.x + self.padding, self.rect.centery))
        surface.blit(text_surface, text_rect)
        
        # Cursor
        if self.active:
            self.cursor_timer += 1
            if self.cursor_timer >= 30: # Piscar a cada 0.5s a 60FPS
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = 0
            
            if self.cursor_visible:
                # Posição do cursor: depois do texto ou no início se vazio
                cursor_x_offset = text_surface.get_width() if self.text else 0
                cursor_x = self.rect.x + self.padding + cursor_x_offset + 2 # 2 pixels após o texto
                
                # Limitar cursor_x para não sair do campo de input
                max_cursor_x = self.rect.x + self.rect.width - self.padding
                cursor_x = min(cursor_x, max_cursor_x)

                cursor_y_start = self.rect.y + self.rect.height * 0.2
                cursor_y_end = self.rect.y + self.rect.height * 0.8
                pygame.draw.line(surface, self.text_color,
                                 (cursor_x, cursor_y_start),
                                 (cursor_x, cursor_y_end),
                                 2)

class AddUserScreen:
    def __init__(self, screen, user_data):
        self.screen = screen
        self.running = True
        self.width, self.height = screen.get_size()
        self.user_data = user_data
        self.center_x = self.width // 2
        
        self.bg_color = COLORS["background"]
        self.light_shadow = COLORS["light_shadow"]
        self.dark_shadow = COLORS["dark_shadow"]
        self.accent_color = COLORS["accent"]
        
        self.title_font = pygame.font.SysFont('Arial', 32, bold=True)
        self.subtitle_font = pygame.font.SysFont('Arial', 20, bold=True)
        self.text_font = pygame.font.SysFont('Arial', 16)
        self.small_font = pygame.font.SysFont('Arial', 14)
        
        self.selected_user_type = None
        self.selected_serie = None
        # self.selected_materia = None # Removido selected_materia daqui, pois ele é definido no handle_events
        
        self.message = None
        self.message_timer = 0
        self.message_type = "info"
        
        self.existing_ras = [12345, 67890, 11111, 22222]
        
        self.setup_ui()
        
    def setup_ui(self):
        self.main_panel = NeumorphicPanel(
            self.center_x - 380, 30, 
            760, self.height - 60, # Ajustado para ocupar mais altura
            self.bg_color, self.light_shadow, self.dark_shadow
        )
        
        input_width = 300
        input_height = 40
        input_x = self.center_x - input_width // 2
        
        self.ra_input = NeumorphicInput(
            input_x, 80, input_width, input_height,
            self.bg_color, self.light_shadow, self.dark_shadow,
            "RA (somente números)", self.text_font, text_color=COLORS["text"],
            numeric_only=True, max_length=8
        )
        
        self.nome_input = NeumorphicInput(
            input_x, 140, input_width, input_height,
            self.bg_color, self.light_shadow, self.dark_shadow,
            "Nome completo", self.text_font, text_color=COLORS["text"],
            max_length=100
        )
        
        self.senha_input = NeumorphicInput(
            input_x, 200, input_width, input_height,
            self.bg_color, self.light_shadow, self.dark_shadow,
            "Senha inicial", self.text_font, text_color=COLORS["text"],
            is_password=True, max_length=20
        )
        
        button_width = 110 # Aumentado para caber "PROFESSOR"
        button_height = 35
        user_type_y = 260
        self.aluno_button = NeumorphicButton(
            self.center_x - button_width - 10, user_type_y, button_width, button_height,
            self.bg_color, self.light_shadow, self.dark_shadow,
            self.accent_color, "ALUNO", self.text_font,
            is_toggle=True
        )
        
        self.professor_button = NeumorphicButton(
            self.center_x + 10, user_type_y, button_width, button_height,
            self.bg_color, self.light_shadow, self.dark_shadow,
            self.accent_color, "PROFESSOR", self.text_font,
            is_toggle=True
        )

        # --- Elementos para Aluno ---
        # OBS: self.serie_buttons não está sendo inicializado.
        # Se você for usar botões para série, precisará criá-los aqui. Exemplo:
        self.serie_buttons = [] # Inicialize a lista
        series_options = ["1º Ano", "2º Ano", "3º Ano"]
        serie_button_y = 320
        serie_button_width = 90
        serie_button_start_x = self.center_x - (len(series_options) * (serie_button_width + 10) - 10) / 2 # Centralizado
        for i, serie_text in enumerate(series_options):
            button = NeumorphicButton(
                serie_button_start_x + i * (serie_button_width + 10), serie_button_y,
                serie_button_width, 30,
                self.bg_color, self.light_shadow, self.dark_shadow,
                self.accent_color, serie_text, self.small_font,
                is_toggle=True
            )
            self.serie_buttons.append(button)

        # Posição Y do turma_input ajustada para ficar abaixo dos botões de série
        turma_input_y = serie_button_y + 30 + 20 # Abaixo dos botões de série + espaçamento

        self.turma_input = NeumorphicInput(
            self.center_x - 75, turma_input_y, # Ajustado para x e y
            150, 35, # Largura e altura ajustadas
            self.bg_color, self.light_shadow, self.dark_shadow,
            "Nome da Turma (Ex: A)", self.text_font, text_color=COLORS["text"],
            max_length=10 # Reduzido max_length para nome de turma
        )
        
        # --- Elementos para Professor ---
        self.materia_buttons = []
        materia_button_y_start = 320 # Mesma altura inicial que os botões de série (condicionalmente exibidos)
        materia_button_width = 90
        materia_per_row = 4
        materia_start_x = self.center_x - (materia_per_row * (materia_button_width + 10) - 10) / 2 # Centralizado

        for i, materia in enumerate(SUBJECTS):
            row = i // materia_per_row
            col = i % materia_per_row
            button = NeumorphicButton(
                materia_start_x + col * (materia_button_width + 10), materia_button_y_start + row * (30 + 5),
                materia_button_width, 30,
                self.bg_color, self.light_shadow, self.dark_shadow,
                self.accent_color, materia[:8], self.small_font, # Ex: Matema.
                is_toggle=True
            )
            self.materia_buttons.append(button)
        
        action_button_y = self.main_panel.rect.bottom - 60 # Posição relativa ao painel
        action_button_width = 120
        
        self.salvar_button = NeumorphicButton(
            self.center_x - action_button_width - 70, action_button_y, # Ajustado
            action_button_width, 40,
            self.bg_color, self.light_shadow, self.dark_shadow,
            COLORS["success"], "SALVAR", self.text_font
        )
        
        self.limpar_button = NeumorphicButton(
            self.center_x - action_button_width/2 , action_button_y, # Centralizado
            action_button_width, 40,
            self.bg_color, self.light_shadow, self.dark_shadow,
            self.accent_color, "LIMPAR", self.text_font
        )
        
        self.voltar_button = NeumorphicButton(
            self.center_x + 70, action_button_y, # Ajustado
            action_button_width, 40,
            self.bg_color, self.light_shadow, self.dark_shadow,
            (180, 180, 180), "VOLTAR", self.text_font
        )

    def validate_form(self):
        if not self.ra_input.text.strip():
            return False, "RA é obrigatório."
        try:
            ra = int(self.ra_input.text)
            # Simulação de verificação no banco:
            # conn = getConnection()
            # cursor = conn.cursor()
            # cursor.execute("SELECT RA FROM Usuarios WHERE RA = %s", (ra,))
            # if cursor.fetchone():
            #    return False, "RA já existe no sistema."
            # cursor.close()
            # conn.close()
            if ra in self.existing_ras: # Mantenha simulação se não tiver DB conectado aqui
                return False, "RA já existe no sistema."
        except ValueError:
            return False, "RA deve conter apenas números."
        
        if not self.nome_input.text.strip():
            return False, "Nome é obrigatório."
        if len(self.nome_input.text.strip()) < 3:
            return False, "Nome deve ter pelo menos 3 caracteres."
        
        if not self.senha_input.text.strip():
            return False, "Senha é obrigatória."
        if len(self.senha_input.text) < 4:
            return False, "Senha deve ter pelo menos 4 caracteres."
        
        if not self.selected_user_type:
            return False, "Selecione o tipo de usuário."
        
        if self.selected_user_type == "Aluno":
            if not self.selected_serie:
                return False, "Selecione a série do aluno."
            if not self.turma_input.text.strip(): # CORRIGIDO: verificar .text.strip()
                return False, "Escreva a turma do aluno."
        
        elif self.selected_user_type == "Professor":
            # Encontrar a matéria selecionada
            self.selected_materia = None
            for i, btn in enumerate(self.materia_buttons):
                if btn.is_active:
                    self.selected_materia = SUBJECTS[i]
                    break
            if not self.selected_materia:
                return False, "Selecione a matéria do professor."
        
        return True, "Formulário válido."

    def save_user(self):
        ra_text = self.ra_input.text.strip()
        nome_text = self.nome_input.text.strip()
        senha_text = self.senha_input.text # Senha não é "stripada" para manter espaços se desejado

        # Validações básicas já feitas em validate_form, mas uma dupla checagem não faz mal
        if not all([ra_text, nome_text, senha_text, self.selected_user_type]):
             return False, "Erro: Campos principais faltando."

        user_data = {
            "RA": int(ra_text), # Convertido para int
            "nome": nome_text,
            "senha": senha_text, # Lembre-se: HASH a senha antes de salvar em produção!
            "tipo": self.selected_user_type
        }

        if self.selected_user_type == "Aluno":
            if not self.selected_serie or not self.turma_input.text.strip():
                return False, "Série e Turma devem ser preenchidos para Aluno."
            # Combina série e turma no campo "turma"
            user_data["turma"] = f"{self.selected_serie} {self.turma_input.text.strip().upper()}"
        
        elif self.selected_user_type == "Professor":
            if not self.selected_materia: # selected_materia é atualizado em validate_form ou handle_events
                return False, "Matéria deve ser selecionada para Professor."
            user_data["materia"] = self.selected_materia
        
        sucesso, mensagem = add_user_to_database(user_data, getConnection)
        
        if sucesso:
            self.existing_ras.append(int(ra_text)) # Adiciona à lista de simulação
            # self.show_message("Sucesso", mensagem) 
            pass 
        else:
            # self.show_message("Erro de Cadastro", mensagem)
            pass 

        return sucesso, mensagem

    def clear_form(self):
        self.ra_input.text = ""
        self.nome_input.text = ""
        self.senha_input.text = ""
        self.turma_input.text = "" # CORRIGIDO: limpar texto do turma_input
        
        self.selected_user_type = None
        self.selected_serie = None
        # self.selected_materia = None # Não precisa resetar aqui, é determinado pelos botões

        self.aluno_button.is_active = False
        self.professor_button.is_active = False
        
        # Resetar botões de série (se existirem e estiverem inicializados)
        if hasattr(self, 'serie_buttons'):
            for button in self.serie_buttons:
                button.is_active = False
                
        # Resetar botões de matéria
        for button in self.materia_buttons:
            button.is_active = False
        
        self.ra_input.active = False
        self.nome_input.active = False
        self.senha_input.active = False
        self.turma_input.active = False # CORRIGIDO: resetar estado active
        
        self.message = "Formulário limpo."
        self.message_type = "info"
        self.message_timer = 120 # 2 segundos a 60 FPS

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                return {"action": "exit"}
            
            active_inputs = [self.ra_input, self.nome_input, self.senha_input]
            if self.selected_user_type == "Aluno":
                active_inputs.append(self.turma_input)

            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1: # Botão esquerdo do mouse
                    mouse_pos = pygame.mouse.get_pos()
                    
                    clicked_on_input = False
                    for input_field in active_inputs:
                        if input_field.is_clicked(mouse_pos):
                            for other_input in active_inputs: # Desativa todos
                                other_input.active = False
                            input_field.active = True # Ativa o clicado
                            clicked_on_input = True
                            break
                    if not clicked_on_input: # Se clicou fora de qualquer input ativo
                        for input_field in active_inputs:
                            input_field.active = False
                    
                    if self.aluno_button.is_clicked(mouse_pos):
                        self.selected_user_type = "Aluno"
                        self.aluno_button.is_active = True
                        self.professor_button.is_active = False
                        # Limpar seleção de matéria ao trocar para aluno
                        for btn in self.materia_buttons: btn.is_active = False
                        self.selected_materia = None 
                    
                    elif self.professor_button.is_clicked(mouse_pos):
                        self.selected_user_type = "Professor"
                        self.professor_button.is_active = True
                        self.aluno_button.is_active = False
                        # Limpar seleção de série e turma ao trocar para professor
                        for btn in self.serie_buttons: btn.is_active = False
                        self.selected_serie = None
                        self.turma_input.text = ""
                        self.turma_input.active = False

                    if self.selected_user_type == "Aluno":
                        if hasattr(self, 'serie_buttons'): # Checa se serie_buttons existe
                            for i, button in enumerate(self.serie_buttons):
                                if button.is_clicked(mouse_pos):
                                    self.selected_serie = series_options[i] # Use a lista de onde os textos vieram
                                    for j, other_button in enumerate(self.serie_buttons):
                                        other_button.is_active = (j == i)
                                    break # Sai do loop após encontrar o botão clicado
                    
                    elif self.selected_user_type == "Professor":
                        for i, button in enumerate(self.materia_buttons):
                            if button.is_clicked(mouse_pos):
                                self.selected_materia = SUBJECTS[i] # SUBJECTS é a lista original
                                for j, other_button in enumerate(self.materia_buttons):
                                    other_button.is_active = (j == i)
                                break # Sai do loop

                    if self.salvar_button.is_clicked(mouse_pos):
                        self.salvar_button.pressed = True # Para feedback visual rápido
                        is_valid, message = self.validate_form()
                        if is_valid:
                            success, save_message = self.save_user()
                            self.message = save_message
                            self.message_type = "success" if success else "error"
                            if success:
                                self.clear_form() # Limpa apenas em sucesso total
                        else:
                            self.message = message
                            self.message_type = "error"
                        self.message_timer = 180
                    
                    elif self.limpar_button.is_clicked(mouse_pos):
                        self.limpar_button.pressed = True
                        self.clear_form()
                    
                    elif self.voltar_button.is_clicked(mouse_pos):
                        self.voltar_button.pressed = True
                        return {"action": "back_to_user_management"}
            
            if event.type == MOUSEBUTTONUP: # Resetar estado 'pressed' dos botões
                if event.button == 1:
                    self.salvar_button.pressed = False
                    self.limpar_button.pressed = False
                    self.voltar_button.pressed = False

            if event.type == KEYDOWN:
                current_active_input = None
                if self.ra_input.active: current_active_input = self.ra_input
                elif self.nome_input.active: current_active_input = self.nome_input
                elif self.senha_input.active: current_active_input = self.senha_input
                elif self.turma_input.active and self.selected_user_type == "Aluno": # ADICIONADO: turma_input
                    current_active_input = self.turma_input

                if current_active_input:
                    if event.key == K_BACKSPACE:
                        current_active_input.text = current_active_input.text[:-1]
                    elif event.key == K_RETURN or event.key == K_KP_ENTER:
                        # Opcional: Pular para próximo campo ou salvar
                        pass 
                    elif len(current_active_input.text) < current_active_input.max_length:
                        char = event.unicode
                        if current_active_input == self.ra_input:
                            if char.isdigit():
                                current_active_input.text += char
                        elif current_active_input == self.turma_input: # Turma pode ter letras e números
                             if char.isalnum(): # Permitir alfanuméricos para turma (Ex: A, B, 1, 2)
                                current_active_input.text += char.upper() # Opcional: converter para maiúsculo
                        else: # Para nome e senha, permite mais caracteres
                            current_active_input.text += char
        
        return {"action": "none"}
    
    def update(self):
        if self.message_timer > 0:
            self.message_timer -= 1
            if self.message_timer == 0:
                self.message = None
    
    def draw(self):
        self.screen.fill(self.bg_color)
        self.main_panel.draw(self.screen)
        
        title_text = self.title_font.render("Adicionar Usuário", True, COLORS["text"])
        title_rect = title_text.get_rect(center=(self.center_x, self.main_panel.rect.top + 30))
        self.screen.blit(title_text, title_rect)
        
        # Labels e Inputs
        label_x_offset = self.ra_input.rect.left - 10 # Posição X dos labels, à esquerda dos inputs
        
        ra_label = self.small_font.render("RA:", True, COLORS["text"])
        self.screen.blit(ra_label, (label_x_offset - ra_label.get_width(), self.ra_input.rect.centery - ra_label.get_height()//2))
        self.ra_input.draw(self.screen)
        
        nome_label = self.small_font.render("Nome:", True, COLORS["text"])
        self.screen.blit(nome_label, (label_x_offset - nome_label.get_width(), self.nome_input.rect.centery - nome_label.get_height()//2))
        self.nome_input.draw(self.screen)
        
        senha_label = self.small_font.render("Senha:", True, COLORS["text"])
        self.screen.blit(senha_label, (label_x_offset - senha_label.get_width(), self.senha_input.rect.centery - senha_label.get_height()//2))
        self.senha_input.draw(self.screen)
        
        tipo_label_y = self.aluno_button.rect.top - 20
        tipo_label = self.subtitle_font.render("Tipo de Usuário:", True, COLORS["text"])
        self.screen.blit(tipo_label, (self.center_x - tipo_label.get_width()//2, tipo_label_y))
        
        self.aluno_button.draw(self.screen)
        self.professor_button.draw(self.screen)
        
        # Campos específicos
        base_y_specific_fields = self.aluno_button.rect.bottom + 25

        if self.selected_user_type == "Aluno":
            serie_label_y = base_y_specific_fields
            serie_label_text = self.small_font.render("Série:", True, COLORS["text"])
            # Centralizar o label "Série:" acima dos botões de série
            serie_label_x = self.center_x - serie_label_text.get_width() // 2
            self.screen.blit(serie_label_text, (serie_label_x, serie_label_y))
            
            if hasattr(self, 'serie_buttons'):
                for button in self.serie_buttons:
                    button.draw(self.screen)
            
            # Label e Input para Turma
            turma_label_y = self.turma_input.rect.top - 20 # Label acima do input da turma
            turma_label = self.small_font.render("Turma:", True, COLORS["text"])
            self.screen.blit(turma_label, (self.center_x - turma_label.get_width()//2, turma_label_y))
            self.turma_input.draw(self.screen) # <<< ADICIONADO O DESENHO DO TURMA_INPUT
        
        elif self.selected_user_type == "Professor":
            materia_label_y = base_y_specific_fields
            materia_label_text = self.small_font.render("Matéria que Leciona:", True, COLORS["text"])
            materia_label_x = self.center_x - materia_label_text.get_width() // 2
            self.screen.blit(materia_label_text, (materia_label_x, materia_label_y))

            for button in self.materia_buttons:
                button.draw(self.screen)
        
        self.salvar_button.draw(self.screen)
        self.limpar_button.draw(self.screen)
        self.voltar_button.draw(self.screen)
        
        if self.message and self.message_timer > 0:
            color_map = {
                "success": COLORS["success"], "error": COLORS["error"], "info": COLORS["text"]
            }
            msg_color = color_map.get(self.message_type, COLORS["text"])
            message_surf = self.text_font.render(self.message, True, msg_color)
            
            # Posicionar mensagem acima dos botões de ação
            msg_y = self.salvar_button.rect.top - message_surf.get_height() - 15
            message_rect = message_surf.get_rect(center=(self.center_x, msg_y))
            self.screen.blit(message_surf, message_rect)
        
        # Info do usuário logado (se necessário)
        # user_info = f"Logado como: {self.user_data.get('username', 'N/A')} ({self.user_data.get('role', 'N/A')})"
        # user_surf = self.small_font.render(user_info, True, (120, 120, 120))
        # user_rect = user_surf.get_rect(bottomright=(self.width - 10, self.height - 5))
        # self.screen.blit(user_surf, user_rect)
        
        pygame.display.flip()
    
    def run(self):
        clock = pygame.time.Clock()
        # Definir series_options aqui para ser acessível no handle_events
        # Esta é uma forma de contornar, idealmente seria uma constante ou atributo da classe
        # Se você já definiu self.serie_buttons com os textos corretos, pode usá-los.
        global series_options 
        series_options = ["1º Ano", "2º Ano", "3º Ano"] # Certifique-se que esta lista corresponde aos botões

        while self.running:
            result = self.handle_events()
            
            if result and result.get("action") != "none":
                self.running = False
                return result # Retorna o dicionário da ação
            
            self.update()
            self.draw()
            clock.tick(60)
        
        return {"action": "exit"} # Retorno padrão se o loop terminar por self.running = False