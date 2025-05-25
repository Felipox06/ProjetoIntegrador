# screens/teacher/remove_user_screen.py
# -*- coding: utf-8 -*-

import pygame
import sys
from pygame.locals import *

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

class NeumorphicCheckbox:
    def __init__(self, x, y, bg_color, light_shadow, dark_shadow, accent_color):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.bg_color = bg_color
        self.light_shadow = light_shadow
        self.dark_shadow = dark_shadow
        self.accent_color = accent_color
        self.checked = False
    
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
    
    def draw(self, surface):
        # Fundo do checkbox
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=5)
        
        if self.checked:
            # Estado marcado
            pygame.draw.rect(surface, self.accent_color, self.rect, border_radius=5, width=2)
            # Desenhar checkmark
            pygame.draw.line(surface, self.accent_color, 
                           (self.rect.x + 4, self.rect.y + 10), 
                           (self.rect.x + 8, self.rect.y + 14), 3)
            pygame.draw.line(surface, self.accent_color, 
                           (self.rect.x + 8, self.rect.y + 14), 
                           (self.rect.x + 16, self.rect.y + 6), 3)
        else:
            # Estado normal
            shadow_rect_dark = pygame.Rect(self.rect.x-1, self.rect.y-1, self.rect.width, self.rect.height)
            pygame.draw.rect(surface, self.dark_shadow, shadow_rect_dark, border_radius=5, width=1)
            
            shadow_rect_light = pygame.Rect(self.rect.x+1, self.rect.y+1, self.rect.width, self.rect.height)
            pygame.draw.rect(surface, self.light_shadow, shadow_rect_light, border_radius=5, width=1)

class UserListItemWithCheckbox:
    def __init__(self, x, y, width, height, bg_color, light_shadow, dark_shadow, 
                 user_data, font, checkbox, can_remove=True):
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = bg_color
        self.light_shadow = light_shadow
        self.dark_shadow = dark_shadow
        self.user_data = user_data
        self.font = font
        self.small_font = pygame.font.SysFont('Arial', 14)
        self.checkbox = checkbox
        self.can_remove = can_remove  # Não pode remover o próprio usuário
        
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
    
    def draw(self, surface):
        # Cor de fundo diferente se não pode ser removido
        bg_color = (240, 240, 240) if not self.can_remove else self.bg_color
        
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=10)
        shadow_rect_light = pygame.Rect(self.rect.x-2, self.rect.y-2, self.rect.width, self.rect.height)
        pygame.draw.rect(surface, self.light_shadow, shadow_rect_light, border_radius=10, width=2)
        shadow_rect_dark = pygame.Rect(self.rect.x+2, self.rect.y+2, self.rect.width, self.rect.height)
        pygame.draw.rect(surface, self.dark_shadow, shadow_rect_dark, border_radius=10, width=2)
        
        margin = 10
        
        # Checkbox (se pode ser removido)
        if self.can_remove:
            self.checkbox.draw(surface)
        else:
            # Mostrar ícone de bloqueio ao invés de checkbox
            lock_surf = self.small_font.render("🔒", True, (150, 150, 150))
            lock_rect = lock_surf.get_rect(center=self.checkbox.rect.center)
            surface.blit(lock_surf, lock_rect)
        
        # RA
        ra_surf = self.small_font.render(f"RA: {self.user_data['RA']}", True, (100, 100, 100))
        ra_rect = ra_surf.get_rect(topleft=(self.rect.x + margin + 30, self.rect.y + 5))
        surface.blit(ra_surf, ra_rect)
        
        # Nome
        name_color = (150, 150, 150) if not self.can_remove else (50, 50, 50)
        name_surf = self.font.render(self.user_data['nome'], True, name_color)
        name_rect = name_surf.get_rect(topleft=(self.rect.x + margin + 30, self.rect.y + 25))
        surface.blit(name_surf, name_rect)
        
        # Tipo e informações específicas
        if self.user_data['tipo'] == 'Aluno':
            info_text = f"Aluno - {self.user_data.get('serie', '')} {self.user_data.get('classe', '')}"
            type_color = COLORS.get("success", (75, 181, 67))
        else:
            info_text = f"Professor - {self.user_data.get('materia', '')}"
            type_color = COLORS.get("warning", (232, 181, 12))
        
        if not self.can_remove:
            type_color = (150, 150, 150)
            info_text += " (Usuario atual - nao pode ser removido)"
        
        info_surf = self.small_font.render(info_text, True, type_color)
        info_rect = info_surf.get_rect(bottomleft=(self.rect.x + margin + 30, self.rect.y + self.rect.height - 5))
        surface.blit(info_surf, info_rect)

class RemoveUserScreen:
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
        self.scroll_offset = 0
        self.max_visible_users = 5
        self.show_confirmation = False
        
        # Mensagem de feedback
        self.message = None
        self.message_timer = 0
        self.message_type = "info"
        
        # Dados simulados (sem campo ativo)
        self.all_users = [
            {"RA": 12345, "nome": "Joao Silva", "tipo": "Aluno", "serie": "2 Ano", "classe": "A", "senha": "1234"},
            {"RA": 67890, "nome": "Maria Santos", "tipo": "Professor", "materia": "Matematica", "senha": "5678"},
            {"RA": 11111, "nome": "Ana Costa", "tipo": "Aluno", "serie": "1 Ano", "classe": "B", "senha": "1111"},
            {"RA": 22222, "nome": "Carlos Oliveira", "tipo": "Professor", "materia": "Fisica", "senha": "2222"},
            {"RA": 33333, "nome": "Lucia Ferreira", "tipo": "Aluno", "serie": "3 Ano", "classe": "C", "senha": "3333"},
            {"RA": 44444, "nome": "Pedro Alves", "tipo": "Professor", "materia": "Historia", "senha": "4444"},
        ]
        
        self.filtered_users = self.all_users.copy()
        self.user_checkboxes = {}  # Dicionário para mapear RA -> checkbox
        self.selected_users = []  # Lista de usuários selecionados para remoção
        
        self.setup_ui()
        self.create_checkboxes()
        
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
            self.width - 140, 250, 
            self.bg_color, self.light_shadow, self.dark_shadow,
            border_radius=15
        )
        
        # Botões de filtro (apenas Todos, Alunos, Professores)
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
            self.width - 120, 350,
            30, 30,
            self.bg_color, self.light_shadow, self.dark_shadow,
            self.accent_color, "▼", self.small_font
        )
        
        # Botões de ação
        self.select_all_button = NeumorphicButton(
            80, 420,
            120, 30,
            self.bg_color, self.light_shadow, self.dark_shadow,
            self.accent_color, "MARCAR TODOS", self.small_font
        )
        
        self.deselect_all_button = NeumorphicButton(
            210, 420,
            140, 30,
            self.bg_color, self.light_shadow, self.dark_shadow,
            (150, 150, 150), "DESMARCAR TODOS", self.small_font
        )
        
        self.remover_button = NeumorphicButton(
            200, 460,
            120, 35,
            self.bg_color, self.light_shadow, self.dark_shadow,
            COLORS["error"], "REMOVER", self.text_font
        )
        
        self.cancelar_button = NeumorphicButton(
            340, 460,
            100, 35,
            self.bg_color, self.light_shadow, self.dark_shadow,
            (150, 150, 150), "CANCELAR", self.text_font
        )
        
        self.voltar_button = NeumorphicButton(
            self.width - 150, 460,
            100, 35,
            self.bg_color, self.light_shadow, self.dark_shadow,
            (180, 180, 180), "VOLTAR", self.text_font
        )
        
        # Botões de confirmação (aparecem no painel de confirmação)
        self.confirmar_button = NeumorphicButton(
            250, 480,
            120, 35,
            self.bg_color, self.light_shadow, self.dark_shadow,
            COLORS["error"], "CONFIRMAR", self.text_font
        )
        
        self.cancelar_conf_button = NeumorphicButton(
            390, 480,
            120, 35,
            self.bg_color, self.light_shadow, self.dark_shadow,
            (150, 150, 150), "CANCELAR", self.text_font
        )
    
    def create_checkboxes(self):
        """Cria checkboxes para todos os usuários"""
        self.user_checkboxes = {}
        for user in self.all_users:
            checkbox = NeumorphicCheckbox(
                0, 0,  # Posição será definida no draw
                self.bg_color, self.light_shadow, self.dark_shadow, self.accent_color
            )
            self.user_checkboxes[user['RA']] = checkbox
    
    def apply_filter(self):
        """Aplica o filtro selecionado à lista de usuários"""
        if self.current_filter == "Todos":
            self.filtered_users = self.all_users.copy()
        elif self.current_filter == "Alunos":
            self.filtered_users = [u for u in self.all_users if u['tipo'] == 'Aluno']
        elif self.current_filter == "Professores":
            self.filtered_users = [u for u in self.all_users if u['tipo'] == 'Professor']
        
        self.scroll_offset = 0
        self.update_selected_users()
    
    def update_selected_users(self):
        """Atualiza a lista de usuários selecionados baseado nos checkboxes"""
        self.selected_users = []
        for user in self.filtered_users:
            checkbox = self.user_checkboxes[user['RA']]
            if checkbox.checked and self.can_remove_user(user):
                self.selected_users.append(user)
    
    def can_remove_user(self, user):
        """Verifica se um usuário pode ser removido (não pode remover a si mesmo)"""
        # Assumindo que o username é baseado no nome ou RA
        current_username = self.user_data.get('username', '')
        return user['nome'] != current_username and str(user['RA']) != current_username
    
    def select_all_users(self):
        """Marca todos os usuários visíveis (que podem ser removidos)"""
        for user in self.filtered_users:
            if self.can_remove_user(user):
                self.user_checkboxes[user['RA']].checked = True
        self.update_selected_users()
    
    def deselect_all_users(self):
        """Desmarca todos os usuários"""
        for user in self.filtered_users:
            self.user_checkboxes[user['RA']].checked = False
        self.update_selected_users()
    
    def remover_users(self):
        """Remove permanentemente os usuários selecionados"""
        ras_to_remove = [user['RA'] for user in self.selected_users]
        
        # SIMULAÇÃO - Em produção, faria DELETE no banco (cuidado com FKs)
        print("=== REMOVER USUARIOS DO BANCO ===")
        for ra in ras_to_remove:
            user = next(u for u in self.selected_users if u['RA'] == ra)
            if user['tipo'] == 'Aluno':
                print(f"DELETE FROM alunos WHERE aluno_RA = {ra}")
            else:
                print(f"DELETE FROM professores WHERE prof_RA = {ra}")
        print(f"DELETE FROM usuarios WHERE RA IN ({', '.join(map(str, ras_to_remove))})")
        print("=====================================")
        
        # Remover da lista local
        self.all_users = [u for u in self.all_users if u['RA'] not in ras_to_remove]
        
        # Limpar seleções e reaplicar filtro
        self.deselect_all_users()
        self.apply_filter()
        
        return True, f"{len(ras_to_remove)} usuario(s) removido(s) permanentemente!"
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                return {"action": "exit"}
                
            if event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Se estiver na tela de confirmação
                if self.show_confirmation:
                    if self.confirmar_button.is_clicked(mouse_pos):
                        success, message = self.remover_users()
                        
                        if success:
                            self.message = message
                            self.message_type = "success"
                            self.message_timer = 180
                        else:
                            self.message = message
                            self.message_type = "error"
                            self.message_timer = 180
                        
                        self.show_confirmation = False
                    
                    if self.cancelar_conf_button.is_clicked(mouse_pos):
                        self.show_confirmation = False
                    
                    return {"action": "none"}
                
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
                
                # Verificar cliques nos checkboxes dos usuários
                list_y = self.list_panel.rect.y + 10
                item_height = 45
                
                visible_users = self.filtered_users[self.scroll_offset:self.scroll_offset + self.max_visible_users]
                for i, user in enumerate(visible_users):
                    checkbox = self.user_checkboxes[user['RA']]
                    checkbox_x = self.list_panel.rect.x + 15
                    checkbox_y = list_y + i * item_height + 12
                    checkbox.rect.x = checkbox_x
                    checkbox.rect.y = checkbox_y
                    
                    if checkbox.is_clicked(mouse_pos) and self.can_remove_user(user):
                        checkbox.checked = not checkbox.checked
                        self.update_selected_users()
                
                # Verificar cliques nos botões de ação
                if self.select_all_button.is_clicked(mouse_pos):
                    self.select_all_users()
                
                if self.deselect_all_button.is_clicked(mouse_pos):
                    self.deselect_all_users()
                
                if self.remover_button.is_clicked(mouse_pos) and self.selected_users:
                    self.show_confirmation = True
                
                if self.cancelar_button.is_clicked(mouse_pos):
                    self.deselect_all_users()
                
                if self.voltar_button.is_clicked(mouse_pos):
                    return {"action": "back_to_user_management"}
        
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
        title_text = self.title_font.render("Remover Usuarios", True, (60, 60, 60))
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
                checkbox = self.user_checkboxes[user['RA']]
                checkbox_x = self.list_panel.rect.x + 15
                checkbox_y = list_y + i * item_height + 12
                checkbox.rect.x = checkbox_x
                checkbox.rect.y = checkbox_y
                
                can_remove = self.can_remove_user(user)
                
                user_item = UserListItemWithCheckbox(
                    self.list_panel.rect.x + 10,
                    list_y + i * item_height,
                    self.list_panel.rect.width - 70,
                    item_height - 5,
                    self.bg_color,
                    self.light_shadow,
                    self.dark_shadow,
                    user,
                    self.text_font,
                    checkbox,
                    can_remove
                )
                user_item.draw(self.screen)
            
            # Botões de rolagem (se necessário)
            if len(self.filtered_users) > self.max_visible_users:
                self.scroll_up_button.draw(self.screen)
                self.scroll_down_button.draw(self.screen)
        
        # Botões de seleção
        self.select_all_button.draw(self.screen)
        self.deselect_all_button.draw(self.screen)
        
        # Painel de confirmação ou ações
        if self.show_confirmation:
            # Painel de confirmação
            conf_panel = NeumorphicPanel(
                150, 200,
                self.width - 300, 150,
                (255, 240, 240),  # Fundo vermelho claro para alerta
                self.light_shadow, self.dark_shadow,
                border_radius=15
            )
            conf_panel.draw(self.screen)
            
            # Título da confirmação
            conf_title = self.subtitle_font.render("Confirmar REMOCAO", True, (150, 50, 50))
            conf_title_rect = conf_title.get_rect(center=(self.center_x, 230))
            self.screen.blit(conf_title, conf_title_rect)
            
            # Lista de usuários selecionados
            selected_text = f"Usuarios selecionados: {len(self.selected_users)}"
            selected_surf = self.text_font.render(selected_text, True, (80, 80, 80))
            selected_rect = selected_surf.get_rect(center=(self.center_x, 260))
            self.screen.blit(selected_surf, selected_rect)
            
            # Aviso
            warning_text = "ATENCAO: Esta acao nao pode ser desfeita!"
            warning_surf = self.small_font.render(warning_text, True, (200, 50, 50))
            warning_rect = warning_surf.get_rect(center=(self.center_x, 280))
            self.screen.blit(warning_surf, warning_rect)
            
            info_text = "Todos os dados dos usuarios serao perdidos permanentemente."
            info_surf = self.small_font.render(info_text, True, (100, 100, 100))
            info_rect = info_surf.get_rect(center=(self.center_x, 300))
            self.screen.blit(info_surf, info_rect)
            
            # Botões de confirmação
            self.confirmar_button.draw(self.screen)
            self.cancelar_conf_button.draw(self.screen)
        
        else:
            # Mostrar informações de seleção e botões de ação
            if self.selected_users:
                selection_text = f"{len(self.selected_users)} usuario(s) selecionado(s)"
                selection_surf = self.text_font.render(selection_text, True, (80, 80, 80))
                selection_rect = selection_surf.get_rect(center=(self.center_x, 440))
                self.screen.blit(selection_surf, selection_rect)
                
                # Botões de ação
                self.remover_button.draw(self.screen)
                self.cancelar_button.draw(self.screen)
            else:
                instruction_text = "Marque os usuarios que deseja remover"
                instruction_surf = self.text_font.render(instruction_text, True, (120, 120, 120))
                instruction_rect = instruction_surf.get_rect(center=(self.center_x, 440))
                self.screen.blit(instruction_surf, instruction_rect)
        
        # Sempre mostrar botão voltar
        self.voltar_button.draw(self.screen)
        
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