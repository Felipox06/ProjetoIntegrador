# screens/teacher/class_edit_screen.py
# -*- coding: utf-8 -*-

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
        "accent": (106, 130, 251),
        "text": (60, 60, 60),
        "success": (75, 181, 67),
        "warning": (232, 181, 12),
        "error": (232, 77, 77)
    }

# Classes para componentes de UI neumórficos
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

class ClassListItem:
    def __init__(self, x, y, width, height, bg_color, light_shadow, dark_shadow, 
                 class_id, class_name, grade, shift, year, font, is_selected=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = bg_color
        self.light_shadow = light_shadow
        self.dark_shadow = dark_shadow
        self.class_id = class_id
        self.class_name = class_name
        self.grade = grade
        self.shift = shift
        self.year = year
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
        line_height = self.font.get_height()
        
        # ID da turma (pequeno, canto superior esquerdo)
        id_surf = self.small_font.render(f"ID: {self.class_id}", True, (100, 100, 100))
        id_rect = id_surf.get_rect(topleft=(self.rect.x + margin, self.rect.y + 10))
        surface.blit(id_surf, id_rect)
        
        # Nome da turma (principal)
        name_surf = self.font.render(self.class_name, True, (50, 50, 50))
        name_rect = name_surf.get_rect(topleft=(self.rect.x + margin, self.rect.y + 30))
        surface.blit(name_surf, name_rect)
        
        # Informações adicionais (série, turno, ano)
        info_text = f"{self.grade} | {self.shift} | Ano Letivo: {self.year}"
        info_surf = self.small_font.render(info_text, True, (100, 100, 100))
        info_rect = info_surf.get_rect(bottomleft=(self.rect.x + margin, self.rect.y + self.rect.height - 10))
        surface.blit(info_surf, info_rect)

class NeumorphicInput:
    def __init__(self, x, y, width, height, bg_color, light_shadow, dark_shadow, 
                 placeholder, font, is_numeric=False, max_length=30):
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = bg_color
        self.light_shadow = light_shadow
        self.dark_shadow = dark_shadow
        self.placeholder = placeholder
        self.font = font
        self.is_numeric = is_numeric
        self.max_length = max_length
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
            text_surface = self.font.render(self.text, True, (50, 50, 50))
        else:
            text_surface = self.font.render(self.placeholder, True, (150, 150, 150))
        
        text_rect = text_surface.get_rect(midleft=(self.rect.x + 15, self.rect.y + self.rect.height // 2))
        surface.blit(text_surface, text_rect)
        
        # Desenhar cursor piscante se ativo
        if self.active:
            # Atualizar timer do cursor
            self.cursor_timer += 1
            if self.cursor_timer >= 30:  # piscar a cada 30 frames (aproximadamente 0.5s em 60fps)
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = 0
            
            if self.cursor_visible:
                cursor_x = text_rect.right + 2 if self.text else self.rect.x + 15
                pygame.draw.line(surface, (50, 50, 50),
                               (cursor_x, self.rect.y + 15),
                               (cursor_x, self.rect.y + self.rect.height - 15),
                               2)

class ClassEditScreen:
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
        
        # Estado da seleção
        self.selected_class = None
        self.show_edit_form = False
        
        # Estado do formulário de edição
        self.class_name_input = None
        self.selected_grade = None
        self.selected_shift = None
        self.year_input = None
        self.grade_buttons = []
        self.shift_buttons = []
        
        # Estado de mensagem
        self.message = None
        self.message_timer = 0
        
        # Para rolagem na lista
        self.scroll_offset = 0
        self.max_items_visible = 5  # Número de turmas visíveis por vez
        
        # Criar elementos de UI
        self.setup_ui()
        
        # Carregar turmas
        self.classes = self.load_classes()
        
    def setup_ui(self):
        # Painel principal
        self.main_panel = NeumorphicPanel(
            self.center_x - 350, 20, 
            700, 560, 
            self.bg_color, self.light_shadow, self.dark_shadow
        )
        
        # Painel da lista de turmas
        self.list_panel = NeumorphicPanel(
            self.center_x - 330, 70, 
            660, 220, 
            self.bg_color, self.light_shadow, self.dark_shadow,
            border_radius=15
        )
        
        # Botões de rolagem para a lista
        self.scroll_up_button = NeumorphicButton(
            self.center_x + 290, 100,
            35, 35,
            self.bg_color, self.light_shadow, self.dark_shadow,
            self.accent_color, "▲", self.text_font
        )
        
        self.scroll_down_button = NeumorphicButton(
            self.center_x + 290, 220,
            35, 35,
            self.bg_color, self.light_shadow, self.dark_shadow,
            self.accent_color, "▼", self.text_font
        )
        
        # Painel do formulário de edição (inicialmente oculto)
        self.form_panel = NeumorphicPanel(
            self.center_x - 330, 300, 
            660, 220, 
            self.bg_color, self.light_shadow, self.dark_shadow,
            border_radius=15
        )
        
        # Botão para editar a turma selecionada
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
        """Criar formulário de edição para a turma selecionada"""
        # Campo para nome da turma
        self.class_name_input = NeumorphicInput(
            self.center_x - 250, 330,
            500, 40,
            self.bg_color, self.light_shadow, self.dark_shadow,
            "Nome da Turma", self.text_font
        )
        self.class_name_input.text = self.selected_class["name"]
        
        # Botões para série (ano)
        self.grade_buttons = []
        grades = ["1º Ano", "2º Ano", "3º Ano"]
        btn_width = 120
        btn_height = 30
        btn_x_start = self.center_x - 250
        btn_y = 400
        
        for i, grade in enumerate(grades):
            btn_x = btn_x_start + i * (btn_width + 20)
            button = NeumorphicButton(
                btn_x, btn_y,
                btn_width, btn_height,
                self.bg_color, self.light_shadow, self.dark_shadow,
                self.accent_color, grade, self.text_font,
                is_toggle=True, is_active=(grade == self.selected_class["grade"])
            )
            self.grade_buttons.append(button)
            
            if grade == self.selected_class["grade"]:
                self.selected_grade = grade
        
        # Botões para turno
        self.shift_buttons = []
        shifts = ["Manhã", "Tarde", "Noite"]
        btn_width = 120
        btn_x_start = self.center_x - 250
        btn_y = 450
        
        for i, shift in enumerate(shifts):
            btn_x = btn_x_start + i * (btn_width + 20)
            button = NeumorphicButton(
                btn_x, btn_y,
                btn_width, btn_height,
                self.bg_color, self.light_shadow, self.dark_shadow,
                self.accent_color, shift, self.text_font,
                is_toggle=True, is_active=(shift == self.selected_class["shift"])
            )
            self.shift_buttons.append(button)
            
            if shift == self.selected_class["shift"]:
                self.selected_shift = shift
        
        # Campo para ano letivo
        self.year_input = NeumorphicInput(
            self.center_x + 50, 400,
            120, 30,
            self.bg_color, self.light_shadow, self.dark_shadow,
            "Ano Letivo", self.text_font,
            is_numeric=True, max_length=4
        )
        self.year_input.text = str(self.selected_class["year"])
    
    def load_classes(self):
        """Função mockup para carregar turmas do banco"""
        # No código real, faria uma consulta ao banco de dados
        classes = [
            {
                "id": 1,
                "name": "3º Ano A",
                "grade": "3º Ano",
                "shift": "Manhã",
                "year": 2025,
                "teacher": "Professor Silva"
            },
            {
                "id": 2,
                "name": "2º Ano B",
                "grade": "2º Ano",
                "shift": "Tarde",
                "year": 2025,
                "teacher": "Professor Silva"
            },
            {
                "id": 3,
                "name": "1º Ano C",
                "grade": "1º Ano",
                "shift": "Manhã",
                "year": 2025,
                "teacher": "Professor Silva"
            },
            {
                "id": 4,
                "name": "3º Ano B",
                "grade": "3º Ano",
                "shift": "Noite",
                "year": 2025,
                "teacher": "Professor Silva"
            },
            {
                "id": 5,
                "name": "2º Ano A",
                "grade": "2º Ano",
                "shift": "Manhã",
                "year": 2025,
                "teacher": "Professor Silva"
            },
            {
                "id": 6,
                "name": "1º Ano A",
                "grade": "1º Ano",
                "shift": "Tarde",
                "year": 2025,
                "teacher": "Professor Silva"
            },
        ]
        return classes
    
    def validate_form(self):
        """Verificar se todos os campos necessários estão preenchidos"""
        # Verificar se o nome da turma foi preenchido
        if not self.class_name_input.text.strip():
            return False, "Digite o nome da turma"
        
        # Verificar se a série foi selecionada
        if not self.selected_grade:
            return False, "Selecione a série"
        
        # Verificar se o turno foi selecionado
        if not self.selected_shift:
            return False, "Selecione o turno"
        
        # Verificar se o ano letivo foi preenchido
        if not self.year_input.text.strip():
            return False, "Digite o ano letivo"
        
        # Verificar se o ano letivo é um número válido
        try:
            year = int(self.year_input.text)
            if year < 2000 or year > 2100:  # Validação simples
                return False, "Ano letivo deve estar entre 2000 e 2100"
        except ValueError:
            return False, "Ano letivo deve ser um número"
        
        return True, "Formulário válido"
    
    def save_edited_class(self):
        """Salvar as alterações na turma"""
        is_valid, message = self.validate_form()
        if not is_valid:
            self.message = message
            self.message_timer = 180  # 3 segundos
            return False
        
        # Preparar dados atualizados
        updated_data = {
            "id": self.selected_class["id"],
            "name": self.class_name_input.text.strip(),
            "grade": self.selected_grade,
            "shift": self.selected_shift,
            "year": int(self.year_input.text),
            "teacher": self.selected_class["teacher"]
        }
        
        # Atualizar na lista local (simulação)
        for i, cls in enumerate(self.classes):
            if cls["id"] == self.selected_class["id"]:
                self.classes[i] = updated_data
                self.selected_class = updated_data
                break
        
        # Simulação de atualização no banco de dados
        print(f"Turma atualizada: {updated_data}")
        
        # Mostrar mensagem de sucesso
        self.message = "Turma atualizada com sucesso!"
        self.message_timer = 120  # 2 segundos
        
        return True
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Se o formulário de edição estiver aberto
                if self.show_edit_form:
                    # Verificar cliques nos campos de entrada
                    if self.class_name_input.is_clicked(mouse_pos):
                        self.class_name_input.active = True
                        self.year_input.active = False
                    elif self.year_input.is_clicked(mouse_pos):
                        self.class_name_input.active = False
                        self.year_input.active = True
                    else:
                        self.class_name_input.active = False
                        self.year_input.active = False
                    
                    # Verificar cliques nos botões de série
                    for i, button in enumerate(self.grade_buttons):
                        if button.is_clicked(mouse_pos):
                            # Desativar todos os outros botões de série
                            for j, other_button in enumerate(self.grade_buttons):
                                other_button.is_active = (j == i)
                            
                            grades = ["1º Ano", "2º Ano", "3º Ano"]
                            self.selected_grade = grades[i]
                            break
                    
                    # Verificar cliques nos botões de turno
                    for i, button in enumerate(self.shift_buttons):
                        if button.is_clicked(mouse_pos):
                            # Desativar todos os outros botões de turno
                            for j, other_button in enumerate(self.shift_buttons):
                                other_button.is_active = (j == i)
                            
                            shifts = ["Manhã", "Tarde", "Noite"]
                            self.selected_shift = shifts[i]
                            break
                    
                    # Verificar clique no botão SALVAR
                    if self.save_button.is_clicked(mouse_pos):
                        self.save_button.pressed = True
                        if self.save_edited_class():
                            # Reset para o estado de seleção após salvar
                            self.show_edit_form = False
                else:
                    # Verificar cliques na lista de turmas
                    list_y = self.list_panel.rect.y + 20
                    item_height = 80
                    item_spacing = 10
                    
                    visible_classes = self.classes[self.scroll_offset:self.scroll_offset + self.max_items_visible]
                    for i, class_item in enumerate(visible_classes):
                        item_y = list_y + i * (item_height + item_spacing)
                        item_rect = pygame.Rect(
                            self.list_panel.rect.x + 20,
                            item_y,
                            self.list_panel.rect.width - 80,
                            item_height
                        )
                        
                        if item_rect.collidepoint(mouse_pos):
                            # Selecionar esta turma
                            self.selected_class = class_item
                            break
                
                # Verificar cliques nos botões de rolagem (sempre visíveis)
                if self.scroll_up_button.is_clicked(mouse_pos) and self.scroll_offset > 0:
                    self.scroll_up_button.pressed = True
                    self.scroll_offset -= 1
                
                if self.scroll_down_button.is_clicked(mouse_pos) and self.scroll_offset < len(self.classes) - self.max_items_visible:
                    self.scroll_down_button.pressed = True
                    self.scroll_offset += 1
                
                # Verificar rolagem com roda do mouse
                if event.button == 4 and self.list_panel.rect.collidepoint(mouse_pos):  # Rolar para cima
                    if self.scroll_offset > 0:
                        self.scroll_offset -= 1
                        
                elif event.button == 5 and self.list_panel.rect.collidepoint(mouse_pos):  # Rolar para baixo
                    if self.scroll_offset < len(self.classes) - self.max_items_visible:
                        self.scroll_offset += 1
                
                # Verificar clique no botão EDITAR
                if self.edit_button.is_clicked(mouse_pos) and self.selected_class and not self.show_edit_form:
                    self.edit_button.pressed = True
                    self.show_edit_form = True
                    self.create_edit_form()
                
                # Verificar clique no botão VOLTAR
                if self.back_button.is_clicked(mouse_pos):
                    self.back_button.pressed = True
                    return {"action": "back_to_menu"}
            
            # Lidar com entrada de texto se o formulário estiver aberto
            if self.show_edit_form and event.type == KEYDOWN:
                # Processar entrada para o campo de nome da turma
                if self.class_name_input.active:
                    if event.key == K_BACKSPACE:
                        self.class_name_input.text = self.class_name_input.text[:-1]
                    elif len(self.class_name_input.text) < self.class_name_input.max_length:
                        # Aceitar qualquer caractere
                        self.class_name_input.text += event.unicode
                
                # Processar entrada para o campo de ano letivo
                elif self.year_input.active:
                    if event.key == K_BACKSPACE:
                        self.year_input.text = self.year_input.text[:-1]
                    elif len(self.year_input.text) < self.year_input.max_length:
                        # Aceitar apenas números
                        if self.year_input.is_numeric and event.unicode.isdigit():
                            self.year_input.text += event.unicode
                        elif not self.year_input.is_numeric:
                            self.year_input.text += event.unicode
        
        return {"action": "none"}
    
    def update(self):
        # Resetar estado dos botões
        self.edit_button.pressed = False
        self.back_button.pressed = False
        if self.show_edit_form:
            self.save_button.pressed = False
        
        # Atualizar temporizador de mensagem
        if self.message_timer > 0:
            self.message_timer -= 1
            if self.message_timer == 0:
                self.message = None
    
    def draw(self):
        # Limpa a tela com a cor de fundo
        self.screen.fill(self.bg_color)
        
        # Desenha o painel principal
        self.main_panel.draw(self.screen)
        
        # Desenha o título
        title_text = self.title_font.render("Editar Turmas", True, (60, 60, 60))
        title_rect = title_text.get_rect(center=(self.center_x, 45))
        self.screen.blit(title_text, title_rect)
        
        # Desenha o painel da lista de turmas
        self.list_panel.draw(self.screen)
        
        # Desenha a lista de turmas
        if len(self.classes) == 0:
            # Mensagem se não houver turmas
            no_classes_text = self.text_font.render("Nenhuma turma encontrada", True, (100, 100, 100))
            no_classes_rect = no_classes_text.get_rect(center=(self.list_panel.rect.centerx, self.list_panel.rect.centery))
            self.screen.blit(no_classes_text, no_classes_rect)
        else:
            # Desenha as turmas visíveis
            list_y = self.list_panel.rect.y + 20
            item_height = 80
            item_spacing = 10
            
            visible_classes = self.classes[self.scroll_offset:self.scroll_offset + self.max_items_visible]
            for i, class_item in enumerate(visible_classes):
                item_y = list_y + i * (item_height + item_spacing)
                
                # Verifica se a turma está selecionada
                is_selected = self.selected_class and self.selected_class["id"] == class_item["id"]
                
                class_list_item = ClassListItem(
                    self.list_panel.rect.x + 20,
                    item_y,
                    self.list_panel.rect.width - 80,
                    item_height,
                    self.bg_color,
                    self.light_shadow,
                    self.dark_shadow,
                    class_item["id"],
                    class_item["name"],
                    class_item["grade"],
                    class_item["shift"],
                    class_item["year"],
                    self.text_font,
                    is_selected
                )
                class_list_item.draw(self.screen)
            
            # Desenha indicadores de rolagem se houver mais itens
            if len(self.classes) > self.max_items_visible:
                self.scroll_up_button.draw(self.screen)
                self.scroll_down_button.draw(self.screen)
        
        # Se o formulário de edição estiver aberto, desenha-o
        if self.show_edit_form and self.selected_class:
            # Desenha o painel do formulário
            self.form_panel.draw(self.screen)
            
            # Desenha o título do formulário
            form_title = self.subtitle_font.render(f"Editar: {self.selected_class['name']}", True, (60, 60, 60))
            form_title_rect = form_title.get_rect(midtop=(self.center_x, self.form_panel.rect.y + 10))
            self.screen.blit(form_title, form_title_rect)
            
            # Desenha os campos de edição
            self.class_name_input.draw(self.screen)
            self.year_input.draw(self.screen)
            
            # Desenha os rótulos
            name_label = self.small_font.render("Nome:", True, (80, 80, 80))
            name_rect = name_label.get_rect(bottomleft=(self.class_name_input.rect.x, self.class_name_input.rect.y - 5))
            self.screen.blit(name_label, name_rect)
            
            year_label = self.small_font.render("Ano Letivo:", True, (80, 80, 80))
            year_rect = year_label.get_rect(bottomleft=(self.year_input.rect.x, self.year_input.rect.y - 5))
            self.screen.blit(year_label, year_rect)
            
            grade_label = self.small_font.render("Série:", True, (80, 80, 80))
            grade_rect = grade_label.get_rect(bottomleft=(self.grade_buttons[0].rect.x, self.grade_buttons[0].rect.y - 5))
            self.screen.blit(grade_label, grade_rect)
            
            shift_label = self.small_font.render("Turno:", True, (80, 80, 80))
            shift_rect = shift_label.get_rect(bottomleft=(self.shift_buttons[0].rect.x, self.shift_buttons[0].rect.y - 5))
            self.screen.blit(shift_label, shift_rect)
            
            # Desenha os botões de opção
            for button in self.grade_buttons:
                button.draw(self.screen)
                
            for button in self.shift_buttons:
                button.draw(self.screen)
            
            # Desenha o botão de salvar
            self.save_button.draw(self.screen)
        else:
            # Desenha o botão de editar (ativo apenas se uma turma estiver selecionada)
            if self.selected_class:
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
                hint_text = self.small_font.render("Selecione uma turma para editar", True, (120, 120, 120))
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