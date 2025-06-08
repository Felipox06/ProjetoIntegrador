# screens/teacher/edit_user_screen.py
# -*- coding: utf-8 -*-

import pygame
import sys
from pygame.locals import *
from databse.data_manager import search_all_users_from_db
from databse.db_connector import getConnection
from databse.data_manager import update_user_in_db
import mysql.connector

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

# Classes para componentes de UI neumórficos (reutilizadas)
class NeumorphicPanel:
    def __init__(self, x, y, width, height, bg_color, light_shadow, dark_shadow, border_radius=20):
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = bg_color
        self.light_shadow = light_shadow
        self.dark_shadow = dark_shadow
        self.border_radius = border_radius
    
    def draw(self, surface):
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=self.border_radius)
        shadow_rect_light = pygame.Rect(self.rect.x-3, self.rect.y-3, self.rect.width, self.rect.height)
        pygame.draw.rect(surface, self.light_shadow, shadow_rect_light, border_radius=self.border_radius, width=3)
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
        
        self.text_surf = font.render(text, True, (50, 50, 50))
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)
    
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
    
    def draw(self, surface):
        is_pressed = self.pressed or (self.is_toggle and self.is_active)
        
        if is_pressed:
            pygame.draw.rect(surface, self.bg_color, 
                           pygame.Rect(self.rect.x+2, self.rect.y+2, self.rect.width-4, self.rect.height-4), 
                           border_radius=10)
            pygame.draw.rect(surface, self.accent_color, 
                           self.rect, border_radius=10, width=2)
            text_rect = self.text_surf.get_rect(center=(self.rect.centerx+1, self.rect.centery+1))
            surface.blit(self.text_surf, text_rect)
        else:
            pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=10)
            shadow_rect_light = pygame.Rect(self.rect.x-2, self.rect.y-2, self.rect.width, self.rect.height)
            pygame.draw.rect(surface, self.light_shadow, shadow_rect_light, border_radius=10, width=2)
            shadow_rect_dark = pygame.Rect(self.rect.x+2, self.rect.y+2, self.rect.width, self.rect.height)
            pygame.draw.rect(surface, self.dark_shadow, shadow_rect_dark, border_radius=10, width=2)
            surface.blit(self.text_surf, self.text_rect)

class NeumorphicInput:
    def __init__(self, x, y, width, height, bg_color, light_shadow, dark_shadow, 
                 placeholder, font, is_password=False, numeric_only=False, max_length=50, readonly=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = bg_color
        self.light_shadow = light_shadow
        self.dark_shadow = dark_shadow
        self.placeholder = placeholder
        self.font = font
        self.is_password = is_password
        self.numeric_only = numeric_only
        self.max_length = max_length
        self.readonly = readonly
        self.text = ""
        self.active = False
        
        self.cursor_visible = True
        self.cursor_timer = 0
    
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos) and not self.readonly
    
    def draw(self, surface):
        # Cor de fundo diferente se readonly
        bg_color = (220, 220, 220) if self.readonly else self.bg_color
        
        pygame.draw.rect(surface, bg_color, 
                       pygame.Rect(self.rect.x+2, self.rect.y+2, self.rect.width-4, self.rect.height-4), 
                       border_radius=10)
        
        shadow_rect_dark = pygame.Rect(self.rect.x-2, self.rect.y-2, self.rect.width, self.rect.height)
        pygame.draw.rect(surface, self.dark_shadow, shadow_rect_dark, border_radius=10, width=2)
        
        shadow_rect_light = pygame.Rect(self.rect.x+2, self.rect.y+2, self.rect.width, self.rect.height)
        pygame.draw.rect(surface, self.light_shadow, shadow_rect_light, border_radius=10, width=2)
        
        if self.active and not self.readonly:
            pygame.draw.line(surface, (120, 120, 255), 
                           (self.rect.x + 15, self.rect.y + self.rect.height - 8),
                           (self.rect.x + self.rect.width - 15, self.rect.y + self.rect.height - 8),
                           2)
        
        if self.text:
            if self.is_password:
                displayed_text = "*" * len(self.text)
            else:
                displayed_text = self.text
            text_color = (100, 100, 100) if self.readonly else (50, 50, 50)
            text_surface = self.font.render(displayed_text, True, text_color)
        else:
            text_surface = self.font.render(self.placeholder, True, (150, 150, 150))
        
        text_rect = text_surface.get_rect(midleft=(self.rect.x + 15, self.rect.y + self.rect.height // 2))
        surface.blit(text_surface, text_rect)
        
        if self.active and not self.readonly:
            self.cursor_timer += 1
            if self.cursor_timer >= 30:
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = 0
            
            if self.cursor_visible:
                cursor_x = text_rect.right + 2 if self.text else self.rect.x + 15
                pygame.draw.line(surface, (50, 50, 50),
                               (cursor_x, self.rect.y + 15),
                               (cursor_x, self.rect.y + self.rect.height - 15),
                               2)

class UserListItem:
    def __init__(self, x, y, width, height, bg_color, light_shadow, dark_shadow, 
                 user_data, font, is_selected=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = bg_color
        self.light_shadow = light_shadow
        self.dark_shadow = dark_shadow
        self.user_data = user_data
        self.font = font
        self.small_font = pygame.font.SysFont('Arial', 14)
        self.is_selected = is_selected
        
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
    
    def draw(self, surface):
        bg_color = (220, 230, 255) if self.is_selected else self.bg_color
        
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=10)
        shadow_rect_light = pygame.Rect(self.rect.x-2, self.rect.y-2, self.rect.width, self.rect.height)
        pygame.draw.rect(surface, self.light_shadow, shadow_rect_light, border_radius=10, width=2)
        shadow_rect_dark = pygame.Rect(self.rect.x+2, self.rect.y+2, self.rect.width, self.rect.height)
        pygame.draw.rect(surface, self.dark_shadow, shadow_rect_dark, border_radius=10, width=2)
        
        if self.is_selected:
            pygame.draw.rect(surface, COLORS.get("accent", (106, 130, 251)), 
                           self.rect, border_radius=10, width=2)
        
        margin = 10
        
        # RA
        ra_surf = self.small_font.render(f"RA: {self.user_data['RA']}", True, (100, 100, 100))
        ra_rect = ra_surf.get_rect(topleft=(self.rect.x + margin, self.rect.y + 5))
        surface.blit(ra_surf, ra_rect)
        
        # Nome
        name_surf = self.font.render(self.user_data['nome'], True, (50, 50, 50))
        name_rect = name_surf.get_rect(topleft=(self.rect.x + margin, self.rect.y + 25))
        surface.blit(name_surf, name_rect)
        
        # Tipo e informações específicas
        if self.user_data['tipo'] == 'student':
            info_text = f"Aluno - {self.user_data.get('serie', '')} {self.user_data.get('classe', '')}"
            type_color = COLORS.get("success", (75, 181, 67))
        else:
            info_text = f"Professor - {self.user_data.get('materia', '')}"
            type_color = COLORS.get("warning", (232, 181, 12))
        
        info_surf = self.small_font.render(info_text, True, type_color)
        info_rect = info_surf.get_rect(bottomleft=(self.rect.x + margin, self.rect.y + self.rect.height - 5))
        surface.blit(info_surf, info_rect)

class EditUserScreen:
    def __init__(self, screen, user_data):
        self.screen = screen
        self.running = True
        self.width, self.height = screen.get_size()
        self.user_data = user_data
        self.center_x = self.width // 2
        
        # Cores do design neumorfista
        self.bg_color = COLORS["background"]
        self.light_shadow = COLORS["light_shadow"]
        self.dark_shadow = COLORS["dark_shadow"]
        self.accent_color = COLORS["accent"]
        
        # Fontes
        self.title_font = pygame.font.SysFont('Arial', 32, bold=True)
        self.subtitle_font = pygame.font.SysFont('Arial', 20, bold=True)
        self.text_font = pygame.font.SysFont('Arial', 16)
        self.small_font = pygame.font.SysFont('Arial', 14)
        
        # Estado da aplicação
        self.current_filter = "Todos"
        self.selected_user = None
        self.selected_serie = None
        self.selected_classe = None
        self.selected_materia = None
        self.scroll_offset = 0
        self.max_visible_users = 4
        
        # Mensagem de feedback
        self.message = None
        self.message_timer = 0
        self.message_type = "info"
        
        # Dados simulados (em produção, viriam do banco)
        self.all_users = search_all_users_from_db(getConnection)
        
        self.filtered_users = self.all_users.copy()
        
        self.setup_ui()
        
    def setup_ui(self):
        # Painel principal
        self.main_panel = NeumorphicPanel(
            50, 30, 
            self.width - 100, self.height - 60, 
            self.bg_color, self.light_shadow, self.dark_shadow
        )
        
        # Painel de filtros
        self.filter_panel = NeumorphicPanel(
            70, 80, 
            self.width - 140, 60, 
            self.bg_color, self.light_shadow, self.dark_shadow,
            border_radius=15
        )
        
        # Painel da lista de usuários
        self.list_panel = NeumorphicPanel(
            70, 160, 
            self.width - 140, 200, 
            self.bg_color, self.light_shadow, self.dark_shadow,
            border_radius=15
        )
        
        # Botões de filtro
        filter_options = ["Todos", "Alunos", "Professores"]
        button_width = 120
        start_x = 100
        
        self.filter_buttons = []
        for i, option in enumerate(filter_options):
            button = NeumorphicButton(
                start_x + i * (button_width + 20), 95,
                button_width, 30,
                self.bg_color, self.light_shadow, self.dark_shadow,
                self.accent_color, option, self.text_font,
                is_toggle=True, is_active=(option == "Todos")
            )
            self.filter_buttons.append(button)
        
        # Botões de rolagem
        self.scroll_up_button = NeumorphicButton(
            self.width - 120, 180,
            30, 30,
            self.bg_color, self.light_shadow, self.dark_shadow,
            self.accent_color, "▲", self.small_font
        )
        
        self.scroll_down_button = NeumorphicButton(
            self.width - 120, 300,
            30, 30,
            self.bg_color, self.light_shadow, self.dark_shadow,
            self.accent_color, "▼", self.small_font
        )
        
        # Campos de edição (aparecem quando usuário selecionado)
        self.create_edit_form()
        
        # Botões de ação
        self.salvar_button = NeumorphicButton(
            200, self.height - 80,
            100, 35,
            self.bg_color, self.light_shadow, self.dark_shadow,
            COLORS["success"], "SALVAR", self.text_font
        )
        
        self.cancelar_button = NeumorphicButton(
            320, self.height - 80,
            100, 35,
            self.bg_color, self.light_shadow, self.dark_shadow,
            COLORS["warning"], "CANCELAR", self.text_font
        )
        
        self.voltar_button = NeumorphicButton(
            self.width - 150, self.height - 80,
            100, 35,
            self.bg_color, self.light_shadow, self.dark_shadow,
            (180, 180, 180), "VOLTAR", self.text_font
        )
    
    def create_edit_form(self):
        """Cria os campos do formulário de edição"""
        form_y = 380
        
        # Campo RA (readonly)
        self.ra_input = NeumorphicInput(
            100, form_y,
            150, 30,
            self.bg_color, self.light_shadow, self.dark_shadow,
            "RA", self.text_font,
            readonly=True
        )
        
        # Campo Nome
        self.nome_input = NeumorphicInput(
            270, form_y,
            200, 30,
            self.bg_color, self.light_shadow, self.dark_shadow,
            "Nome completo", self.text_font,
            max_length=100
        )
        
        # Campo Senha
        self.senha_input = NeumorphicInput(
            490, form_y,
            150, 30,
            self.bg_color, self.light_shadow, self.dark_shadow,
            "Nova senha", self.text_font,
            is_password=True, max_length=20
        )
        
        # Botões de série (para alunos)
        self.serie_buttons = []
        series = ["1 Ano", "2 Ano", "3 Ano"]
        for i, serie in enumerate(series):
            button = NeumorphicButton(
                100 + i * 90, form_y + 50,
                80, 25,
                self.bg_color, self.light_shadow, self.dark_shadow,
                self.accent_color, serie, self.small_font,
                is_toggle=True
            )
            self.serie_buttons.append(button)
        
        # Botões de classe (para alunos)
        self.classe_buttons = []
        classes = ["A", "B", "C", "D", "E"]
        for i, classe in enumerate(classes):
            button = NeumorphicButton(
                370 + i * 35, form_y + 50,
                30, 25,
                self.bg_color, self.light_shadow, self.dark_shadow,
                self.accent_color, classe, self.small_font,
                is_toggle=True
            )
            self.classe_buttons.append(button)
        
        # Botões de matéria (para professores)
        self.materia_buttons = []
        for i, materia in enumerate(SUBJECTS):
            row = i // 4
            col = i % 4
            button = NeumorphicButton(
                100 + col * 90, form_y + 50 + row * 30,
                80, 25,
                self.bg_color, self.light_shadow, self.dark_shadow,
                self.accent_color, materia[:6], self.small_font,
                is_toggle=True
            )
            self.materia_buttons.append(button)
    
    def apply_filter(self):
        """Aplica o filtro selecionado à lista de usuários"""
        if self.current_filter == "Todos":
            self.filtered_users = self.all_users.copy()
        elif self.current_filter == "Alunos":
            self.filtered_users = [u for u in self.all_users if u['tipo'] == 'student']
        elif self.current_filter == "Professores":
            self.filtered_users = [u for u in self.all_users if u['tipo'] == 'teacher']
        
        self.scroll_offset = 0
        self.selected_user = None
    
    def load_user_data(self, user):
        """Carrega os dados do usuário selecionado no formulário"""
        self.selected_user = user
        
        # Carregar dados básicos
        self.ra_input.text = str(user['RA'])
        self.nome_input.text = user['nome']
        self.senha_input.text = ""  # Senha sempre vazia para segurança
        
        # Resetar seleções
        self.selected_serie = None
        self.selected_classe = None
        self.selected_materia = None
        
        # Resetar botões
        for button in self.serie_buttons:
            button.is_active = False
        for button in self.classe_buttons:
            button.is_active = False
        for button in self.materia_buttons:
            button.is_active = False
        
        # Carregar dados específicos do tipo
        if user['tipo'] == 'student':
            self.selected_serie = user.get('serie')
            self.selected_classe = user.get('classe')
            
            # Ativar botões correspondentes
            series = ["1 Ano", "2 Ano", "3 Ano"]
            classes = ["A", "B", "C", "D", "E"]
            
            for i, serie in enumerate(series):
                if serie == self.selected_serie:
                    self.serie_buttons[i].is_active = True
                    
            for i, classe in enumerate(classes):
                if classe == self.selected_classe:
                    self.classe_buttons[i].is_active = True
        
        elif user['tipo'] == 'teacher':
            self.selected_materia = user.get('materia')
            
            # Ativar botão correspondente
            for i, materia in enumerate(SUBJECTS):
                if materia == self.selected_materia:
                    self.materia_buttons[i].is_active = True
    
    def validate_form(self):
        """Valida os dados do formulário de edição"""
        if not self.selected_user:
            return False, "Nenhum usuario selecionado"
        
        # Validar nome
        if not self.nome_input.text.strip():
            return False, "Nome e obrigatorio"
        
        if len(self.nome_input.text.strip()) < 3:
            return False, "Nome deve ter pelo menos 3 caracteres"
        
        # Validar senha (se preenchida)
        if self.senha_input.text and len(self.senha_input.text) < 4:
            return False, "Senha deve ter pelo menos 4 caracteres"
        
        # Validações específicas por tipo
        if self.selected_user['tipo'] == 'student':
            if not self.selected_serie:
                return False, "Selecione a serie do aluno"
            if not self.selected_classe:
                return False, "Selecione a classe do aluno"
        
        elif self.selected_user['tipo'] == 'teacher':
            if not self.selected_materia:
                return False, "Selecione a materia do professor"
        
        return True, "Formulario valido"
    
    def reload_all_users_from_db(self):
        print("AVISO: Implementar reload_all_users_from_db() para recarregar self.all_users do banco.")


    def save_user(self):
        # Salva as alterações do usuário editado no banco de dados.
        
        if not self.selected_user or 'RA' not in self.selected_user or 'tipo' not in self.selected_user:
            print("Erro: Nenhum usuário selecionado para editar ou dados de RA/tipo ausentes.")
            return False, "Nenhum usuário selecionado ou dados essenciais ausentes."
        fields_to_send_to_db = {}
        
        # Nome (sempre atualizado)
        novo_nome = self.nome_input.text.strip()
        if novo_nome: # Garante que o nome não está vazio
            fields_to_send_to_db["nome"] = novo_nome
        else:
            # self.show_ui_message("Erro", "O nome não pode estar vazio.")
            print("Erro: O nome não pode estar vazio.")
            return False, "O nome não pode estar vazio."

        # Senha (apenas se alterada/preenchida)
        if self.senha_input.text: # Não use .strip() aqui se uma senha com espaços for permitida
            fields_to_send_to_db["senha"] = self.senha_input.text
        
        # Campos específicos do tipo
        user_tipo = self.selected_user['tipo']
        if user_tipo == 'student':
            # Para alunos, a coluna no DB é 'turma', que é a combinação de série e classe
            if self.selected_serie and self.selected_classe: # Garante que ambos foram selecionados na UI
                turma_completa = f"{self.selected_serie} {self.selected_classe}"
                fields_to_send_to_db["turma"] = turma_completa
            else:
                # self.show_ui_message("Erro", "Série e Classe são obrigatórias para Aluno.")
                print("Erro: Série e Classe são obrigatórias para Aluno.")
                return False, "Série e Classe são obrigatórias para Aluno."
        elif user_tipo == 'teacher':
            if self.selected_materia: # Garante que a matéria foi selecionada
                fields_to_send_to_db["materia"] = self.selected_materia
            else:
                # self.show_ui_message("Erro", "Matéria é obrigatória para Professor.")
                print("Erro: Matéria é obrigatória para Professor.")
                return False, "Matéria é obrigatória para Professor."
        
        if not fields_to_send_to_db: # Se apenas RA e tipo foram preenchidos, mas nada para mudar
            # self.show_ui_message("Info", "Nenhum dado alterado.")
            print("Nenhum dado alterado.")
            return True, "Nenhum dado alterado." # Considera sucesso, pois não houve erro


        # --- CHAMADA REAL AO BANCO PARA ATUALIZAR ---
        user_ra_to_update = self.selected_user['RA']
        
        try:
            # Adapte 'self.get_connection' ao seu método/função real de obter conexão
            success_db, message_db = update_user_in_db(
                user_ra_to_update,
                user_tipo,
                fields_to_send_to_db,
                getConnection
            )
        except NameError as ne:
            # self.show_ui_message("Erro de Configuração", str(ne))
            print(f"Erro de Configuração: {ne}")
            return False, f"Erro de Configuração: {ne}"
        except Exception as e:
            # self.show_ui_message("Erro Inesperado", str(e))
            print(f"Erro Inesperado no Sistema: {e}")
            return False, f"Erro Inesperado no Sistema: {e}"

        # Processar o resultado
        if success_db:
            # self.show_ui_message("Sucesso", message_db)
            print(f"Sucesso no DB: {message_db}")
            
            # Atualizar a lista local self.all_users e self.filtered_users
            print("Recarregando lista de usuários após atualização...")
            self.reload_all_users_from_db() # Chama o método para recarregar self.all_users
            self.apply_filter() # Re-aplica os filtros da UI
            
            # Opcional: Atualizar self.selected_user com os dados que foram efetivamente salvos
            # Isso pode ser útil se a UI ainda exibe detalhes do usuário selecionado.
            # Você pode reconstruir o selected_user ou encontrar o usuário atualizado em self.all_users.
            # Ex:
            # for i, user in enumerate(self.all_users):
            # if user['RA'] == user_ra_to_update:
            # self.selected_user.update(user) # Atualiza com os dados do banco
            # break
            
        else:
            # self.show_ui_message("Erro de Atualização", message_db)
            print(f"Erro no DB ao atualizar usuário: {message_db}")

        return success_db, message_db
        
    
    def cancel_edit(self):
        """Cancela a edição atual"""
        if self.selected_user:
            self.load_user_data(self.selected_user)  # Recarregar dados originais
        self.message = "Edicao cancelada"
        self.message_type = "info"
        self.message_timer = 120
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                return {"action": "exit"}
                
            if event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Verificar cliques nos filtros
                filter_options = ["Todos", "Alunos", "Professores"]
                for i, button in enumerate(self.filter_buttons):
                    if button.is_clicked(mouse_pos):
                        self.current_filter = filter_options[i]
                        for j, other_button in enumerate(self.filter_buttons):
                            other_button.is_active = (j == i)
                        self.apply_filter()
                
                # Verificar cliques na rolagem
                if self.scroll_up_button.is_clicked(mouse_pos) and self.scroll_offset > 0:
                    self.scroll_offset -= 1
                
                if self.scroll_down_button.is_clicked(mouse_pos):
                    max_scroll = max(0, len(self.filtered_users) - self.max_visible_users)
                    if self.scroll_offset < max_scroll:
                        self.scroll_offset += 1
                
                # Verificar cliques na lista de usuários
                list_y = self.list_panel.rect.y + 10
                item_height = 45
                
                visible_users = self.filtered_users[self.scroll_offset:self.scroll_offset + self.max_visible_users]
                for i, user in enumerate(visible_users):
                    item_rect = pygame.Rect(
                        self.list_panel.rect.x + 10,
                        list_y + i * item_height,
                        self.list_panel.rect.width - 70,
                        item_height - 5
                    )
                    
                    if item_rect.collidepoint(mouse_pos):
                        self.load_user_data(user)
                        break
                
                # Se há usuário selecionado, verificar cliques no formulário
                if self.selected_user:
                    # Campos de entrada
                    if self.nome_input.is_clicked(mouse_pos):
                        self.nome_input.active = True
                        self.senha_input.active = False
                    elif self.senha_input.is_clicked(mouse_pos):
                        self.nome_input.active = False
                        self.senha_input.active = True
                    else:
                        self.nome_input.active = False
                        self.senha_input.active = False
                    
                    # Botões específicos do tipo
                    if self.selected_user['tipo'] == 'student':
                        # Série
                        series = ["1 Ano", "2 Ano", "3 Ano"]
                        for i, button in enumerate(self.serie_buttons):
                            if button.is_clicked(mouse_pos):
                                self.selected_serie = series[i]
                                for j, other_button in enumerate(self.serie_buttons):
                                    other_button.is_active = (j == i)
                        
                        # Classe
                        classes = ["A", "B", "C", "D", "E"]
                        for i, button in enumerate(self.classe_buttons):
                            if button.is_clicked(mouse_pos):
                                self.selected_classe = classes[i]
                                for j, other_button in enumerate(self.classe_buttons):
                                    other_button.is_active = (j == i)
                    
                    elif self.selected_user['tipo'] == 'teacher':
                        # Matéria
                        for i, button in enumerate(self.materia_buttons):
                            if button.is_clicked(mouse_pos):
                                self.selected_materia = SUBJECTS[i]
                                for j, other_button in enumerate(self.materia_buttons):
                                    other_button.is_active = (j == i)
                
                # Botões de ação
                if self.salvar_button.is_clicked(mouse_pos):
                    is_valid, message = self.validate_form()
                    if is_valid:
                        success, save_message = self.save_user()
                        if success:
                            self.message = save_message
                            self.message_type = "success"
                            self.message_timer = 180
                            self.selected_user = None  # Limpar seleção
                        else:
                            self.message = save_message
                            self.message_type = "error"
                            self.message_timer = 180
                    else:
                        self.message = message
                        self.message_type = "error"
                        self.message_timer = 180
                
                if self.cancelar_button.is_clicked(mouse_pos):
                    self.cancel_edit()
                
                if self.voltar_button.is_clicked(mouse_pos):
                    return {"action": "back_to_user_management"}
            
            # Entrada de texto
            if event.type == KEYDOWN:
                if self.nome_input.active:
                    if event.key == K_BACKSPACE:
                        self.nome_input.text = self.nome_input.text[:-1]
                    elif len(self.nome_input.text) < self.nome_input.max_length:
                        self.nome_input.text += event.unicode
                
                elif self.senha_input.active:
                    if event.key == K_BACKSPACE:
                        self.senha_input.text = self.senha_input.text[:-1]
                    elif len(self.senha_input.text) < self.senha_input.max_length:
                        self.senha_input.text += event.unicode
        
        return {"action": "none"}
    
    def update(self):
        # Atualizar timer de mensagem
        if self.message_timer > 0:
            self.message_timer -= 1
            if self.message_timer == 0:
                self.message = None
    
    def draw(self):
        self.screen.fill(self.bg_color)
        self.main_panel.draw(self.screen)
        self.filter_panel.draw(self.screen)
        self.list_panel.draw(self.screen)
        
        # Título
        title_text = self.title_font.render("Editar Usuarios", True, (60, 60, 60))
        title_rect = title_text.get_rect(center=(self.center_x, 50))
        self.screen.blit(title_text, title_rect)
        
        # Label dos filtros
        filter_label = self.small_font.render("Filtrar por:", True, (80, 80, 80))
        filter_rect = filter_label.get_rect(topleft=(80, 100))
        self.screen.blit(filter_label, filter_rect)
        
        # Botões de filtro
        for button in self.filter_buttons:
            button.draw(self.screen)
        
        # Lista de usuários
        if len(self.filtered_users) == 0:
            no_users_text = self.text_font.render("Nenhum usuario encontrado", True, (100, 100, 100))
            no_users_rect = no_users_text.get_rect(center=(self.list_panel.rect.centerx, self.list_panel.rect.centery))
            self.screen.blit(no_users_text, no_users_rect)
        else:
            list_y = self.list_panel.rect.y + 10
            item_height = 45
            
            visible_users = self.filtered_users[self.scroll_offset:self.scroll_offset + self.max_visible_users]
            for i, user in enumerate(visible_users):
                is_selected = self.selected_user and self.selected_user['RA'] == user['RA']
                
                user_item = UserListItem(
                    self.list_panel.rect.x + 10,
                    list_y + i * item_height,
                    self.list_panel.rect.width - 70,
                    item_height - 5,
                    self.bg_color,
                    self.light_shadow,
                    self.dark_shadow,
                    user,
                    self.text_font,
                    is_selected
                )
                user_item.draw(self.screen)
            
            # Botões de rolagem (se necessário)
            if len(self.filtered_users) > self.max_visible_users:
                self.scroll_up_button.draw(self.screen)
                self.scroll_down_button.draw(self.screen)
        
        # Formulário de edição (se usuário selecionado)
        if self.selected_user:
            # Painel do formulário
            form_panel = NeumorphicPanel(
                70, 370,
                self.width - 140, 120,
                self.bg_color, self.light_shadow, self.dark_shadow,
                border_radius=15
            )
            form_panel.draw(self.screen)
            
            # Labels
            ra_label = self.small_font.render("RA:", True, (80, 80, 80))
            self.screen.blit(ra_label, (100, 365))
            
            nome_label = self.small_font.render("Nome:", True, (80, 80, 80))
            self.screen.blit(nome_label, (270, 365))
            
            senha_label = self.small_font.render("Nova Senha:", True, (80, 80, 80))
            self.screen.blit(senha_label, (490, 365))
            
            # Campos
            self.ra_input.draw(self.screen)
            self.nome_input.draw(self.screen)
            self.senha_input.draw(self.screen)
            
            # Campos específicos do tipo
            if self.selected_user['tipo'] == 'student':
                serie_label = self.small_font.render("Serie:", True, (80, 80, 80))
                self.screen.blit(serie_label, (100, 425))
                
                classe_label = self.small_font.render("Classe:", True, (80, 80, 80))
                self.screen.blit(classe_label, (370, 425))
                
                for button in self.serie_buttons:
                    button.draw(self.screen)
                
                for button in self.classe_buttons:
                    button.draw(self.screen)
            
            elif self.selected_user['tipo'] == 'teacher':
                materia_label = self.small_font.render("Materia:", True, (80, 80, 80))
                self.screen.blit(materia_label, (100, 425))
                
                for button in self.materia_buttons:
                    button.draw(self.screen)
            
            # Botões de ação
            self.salvar_button.draw(self.screen)
            self.cancelar_button.draw(self.screen)
        
        # Sempre mostrar botão voltar
        self.voltar_button.draw(self.screen)
        
        # Instrução se nenhum usuário selecionado
        if not self.selected_user:
            instruction_text = self.text_font.render("Clique em um usuario da lista para editar", True, (120, 120, 120))
            instruction_rect = instruction_text.get_rect(center=(self.center_x, 450))
            self.screen.blit(instruction_text, instruction_rect)
        
        # Mensagem de feedback
        if self.message:
            color = {
                "success": COLORS["success"],
                "error": COLORS["error"],
                "info": (100, 100, 100)
            }.get(self.message_type, (100, 100, 100))
            
            message_surf = self.text_font.render(self.message, True, color)
            message_rect = message_surf.get_rect(center=(self.center_x, 520))
            self.screen.blit(message_surf, message_rect)
        
        # Info do usuário logado
        user_info = f"Logado como: {self.user_data['username']} (Professor)"
        user_surf = self.small_font.render(user_info, True, (120, 120, 120))
        user_rect = user_surf.get_rect(bottomright=(self.width - 20, self.height - 10))
        self.screen.blit(user_surf, user_rect)
        
        pygame.display.flip()
    
    def run(self):
        clock = pygame.time.Clock()
        
        while self.running:
            result = self.handle_events()
            
            if result["action"] != "none":
                self.running = False
                return result
            
            self.update()
            self.draw()
            clock.tick(60)
        
        return {"action": "exit"}