# screens/teacher/add_user_screen.py
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

# Classes para componentes de UI neumórficos
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
                 placeholder, font, is_password=False, numeric_only=False, max_length=50):
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = bg_color
        self.light_shadow = light_shadow
        self.dark_shadow = dark_shadow
        self.placeholder = placeholder
        self.font = font
        self.is_password = is_password
        self.numeric_only = numeric_only
        self.max_length = max_length
        self.text = ""
        self.active = False
        
        self.cursor_visible = True
        self.cursor_timer = 0
    
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
    
    def draw(self, surface):
        pygame.draw.rect(surface, self.bg_color, 
                       pygame.Rect(self.rect.x+2, self.rect.y+2, self.rect.width-4, self.rect.height-4), 
                       border_radius=10)
        
        shadow_rect_dark = pygame.Rect(self.rect.x-2, self.rect.y-2, self.rect.width, self.rect.height)
        pygame.draw.rect(surface, self.dark_shadow, shadow_rect_dark, border_radius=10, width=2)
        
        shadow_rect_light = pygame.Rect(self.rect.x+2, self.rect.y+2, self.rect.width, self.rect.height)
        pygame.draw.rect(surface, self.light_shadow, shadow_rect_light, border_radius=10, width=2)
        
        if self.active:
            pygame.draw.line(surface, (120, 120, 255), 
                           (self.rect.x + 15, self.rect.y + self.rect.height - 8),
                           (self.rect.x + self.rect.width - 15, self.rect.y + self.rect.height - 8),
                           2)
        
        if self.text:
            if self.is_password:
                displayed_text = "*" * len(self.text)
            else:
                displayed_text = self.text
            text_surface = self.font.render(displayed_text, True, (50, 50, 50))
        else:
            text_surface = self.font.render(self.placeholder, True, (150, 150, 150))
        
        text_rect = text_surface.get_rect(midleft=(self.rect.x + 15, self.rect.y + self.rect.height // 2))
        surface.blit(text_surface, text_rect)
        
        if self.active:
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

class AddUserScreen:
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
        
        # Estado do formulário
        self.selected_user_type = None
        self.selected_serie = None
        self.selected_classe = None
        self.selected_materia = None
        
        # Mensagem de feedback
        self.message = None
        self.message_timer = 0
        self.message_type = "info"  # "success", "error", "info"
        
        # Dados simulados para verificar RA único
        self.existing_ras = [12345, 67890, 11111, 22222]  # Simula RAs já cadastrados
        
        self.setup_ui()
        
    def setup_ui(self):
        # Painel principal
        self.main_panel = NeumorphicPanel(
            self.center_x - 380, 30, 
            760, 540, 
            self.bg_color, self.light_shadow, self.dark_shadow
        )
        
        # Campos de entrada
        self.ra_input = NeumorphicInput(
            self.center_x - 150, 80,
            300, 40,
            self.bg_color, self.light_shadow, self.dark_shadow,
            "RA (somente numeros)", self.text_font,
            numeric_only=True, max_length=8
        )
        
        self.nome_input = NeumorphicInput(
            self.center_x - 150, 140,
            300, 40,
            self.bg_color, self.light_shadow, self.dark_shadow,
            "Nome completo", self.text_font,
            max_length=100
        )
        
        self.senha_input = NeumorphicInput(
            self.center_x - 150, 200,
            300, 40,
            self.bg_color, self.light_shadow, self.dark_shadow,
            "Senha inicial", self.text_font,
            is_password=True, max_length=20
        )
        
        # Botões de tipo de usuário
        self.aluno_button = NeumorphicButton(
            self.center_x - 120, 260,
            100, 35,
            self.bg_color, self.light_shadow, self.dark_shadow,
            self.accent_color, "ALUNO", self.text_font,
            is_toggle=True
        )
        
        self.professor_button = NeumorphicButton(
            self.center_x + 20, 260,
            100, 35,
            self.bg_color, self.light_shadow, self.dark_shadow,
            self.accent_color, "PROFESSOR", self.text_font,
            is_toggle=True
        )
        
        # Botões de série (para alunos)
        self.serie_buttons = []
        series = ["1 Ano", "2 Ano", "3 Ano"]
        for i, serie in enumerate(series):
            button = NeumorphicButton(
                self.center_x - 150 + i * 100, 320,
                90, 30,
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
                self.center_x - 120 + i * 50, 370,
                40, 30,
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
                self.center_x - 200 + col * 100, 320 + row * 35,
                90, 30,
                self.bg_color, self.light_shadow, self.dark_shadow,
                self.accent_color, materia[:6], self.small_font,
                is_toggle=True
            )
            self.materia_buttons.append(button)
        
        # Botões de ação
        self.salvar_button = NeumorphicButton(
            self.center_x - 250, 500,
            120, 40,
            self.bg_color, self.light_shadow, self.dark_shadow,
            COLORS["success"], "SALVAR", self.text_font
        )
        
        self.limpar_button = NeumorphicButton(
            self.center_x - 60, 500,
            120, 40,
            self.bg_color, self.light_shadow, self.dark_shadow,
            self.accent_color, "LIMPAR", self.text_font
        )
        
        self.voltar_button = NeumorphicButton(
            self.center_x + 130, 500,
            120, 40,
            self.bg_color, self.light_shadow, self.dark_shadow,
            (180, 180, 180), "VOLTAR", self.text_font
        )
    
    def validate_form(self):
        """Valida todos os campos do formulário"""
        # Validar RA
        if not self.ra_input.text.strip():
            return False, "RA e obrigatorio"
        
        try:
            ra = int(self.ra_input.text)
            if ra in self.existing_ras:
                return False, "RA ja existe no sistema"
        except ValueError:
            return False, "RA deve conter apenas numeros"
        
        # Validar nome
        if not self.nome_input.text.strip():
            return False, "Nome e obrigatorio"
        
        if len(self.nome_input.text.strip()) < 3:
            return False, "Nome deve ter pelo menos 3 caracteres"
        
        # Validar senha
        if not self.senha_input.text.strip():
            return False, "Senha e obrigatoria"
        
        if len(self.senha_input.text) < 4:
            return False, "Senha deve ter pelo menos 4 caracteres"
        
        # Validar tipo de usuário
        if not self.selected_user_type:
            return False, "Selecione o tipo de usuario"
        
        # Validações específicas por tipo
        if self.selected_user_type == "Aluno":
            if not self.selected_serie:
                return False, "Selecione a serie do aluno"
            if not self.selected_classe:
                return False, "Selecione a classe do aluno"
        
        elif self.selected_user_type == "Professor":
            if not self.selected_materia:
                return False, "Selecione a materia do professor"
        
        return True, "Formulario valido"
    
    def save_user(self):
        """Simula salvamento do usuário (preparado para integração com banco)"""
        # Preparar dados do usuário
        user_data = {
            "RA": int(self.ra_input.text),
            "nome": self.nome_input.text.strip(),
            "senha": self.senha_input.text,
            "tipo": self.selected_user_type
        }
        
        # Adicionar dados específicos do tipo
        if self.selected_user_type == "Aluno":
            user_data["serie"] = self.selected_serie
            user_data["classe"] = self.selected_classe
            user_data["turma"] = f"{self.selected_serie} {self.selected_classe}"
        else:
            user_data["materia"] = self.selected_materia
        
        # SIMULAÇÃO - Em produção, aqui faria a inserção no banco
        print("=== DADOS PARA INSERIR NO BANCO ===")
        print(f"RA: {user_data['RA']}")
        print(f"Nome: {user_data['nome']}")
        print(f"Senha: {user_data['senha']}")
        print(f"Tipo: {user_data['tipo']}")
        
        if user_data['tipo'] == 'Aluno':
            print(f"Serie: {user_data['serie']}")
            print(f"Classe: {user_data['classe']}")
            print(f"Turma: {user_data['turma']}")
        else:
            print(f"Materia: {user_data['materia']}")
        
        print("=====================================")
        
        # Simular inserção bem-sucedida
        self.existing_ras.append(user_data['RA'])  # Adicionar à lista de RAs existentes
        
        return True, f"Usuario {user_data['nome']} cadastrado com sucesso!"
    
    def clear_form(self):
        """Limpa todos os campos do formulário"""
        self.ra_input.text = ""
        self.nome_input.text = ""
        self.senha_input.text = ""
        
        self.selected_user_type = None
        self.selected_serie = None
        self.selected_classe = None
        self.selected_materia = None
        
        # Resetar botões
        self.aluno_button.is_active = False
        self.professor_button.is_active = False
        
        for button in self.serie_buttons:
            button.is_active = False
        
        for button in self.classe_buttons:
            button.is_active = False
            
        for button in self.materia_buttons:
            button.is_active = False
        
        # Resetar inputs ativos
        self.ra_input.active = False
        self.nome_input.active = False
        self.senha_input.active = False
        
        self.message = "Formulario limpo"
        self.message_type = "info"
        self.message_timer = 120
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                return {"action": "exit"}
                
            if event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Verificar cliques nos campos de entrada
                if self.ra_input.is_clicked(mouse_pos):
                    self.ra_input.active = True
                    self.nome_input.active = False
                    self.senha_input.active = False
                elif self.nome_input.is_clicked(mouse_pos):
                    self.ra_input.active = False
                    self.nome_input.active = True
                    self.senha_input.active = False
                elif self.senha_input.is_clicked(mouse_pos):
                    self.ra_input.active = False
                    self.nome_input.active = False
                    self.senha_input.active = True
                else:
                    self.ra_input.active = False
                    self.nome_input.active = False
                    self.senha_input.active = False
                
                # Verificar cliques nos botões de tipo
                if self.aluno_button.is_clicked(mouse_pos):
                    self.selected_user_type = "Aluno"
                    self.aluno_button.is_active = True
                    self.professor_button.is_active = False
                
                if self.professor_button.is_clicked(mouse_pos):
                    self.selected_user_type = "Professor"
                    self.professor_button.is_active = True
                    self.aluno_button.is_active = False
                
                # Verificar cliques nos botões de série (só se for aluno)
                if self.selected_user_type == "Aluno":
                    series = ["1 Ano", "2 Ano", "3 Ano"]
                    for i, button in enumerate(self.serie_buttons):
                        if button.is_clicked(mouse_pos):
                            self.selected_serie = series[i]
                            for j, other_button in enumerate(self.serie_buttons):
                                other_button.is_active = (j == i)
                
                    # Verificar cliques nos botões de classe
                    classes = ["A", "B", "C", "D", "E"]
                    for i, button in enumerate(self.classe_buttons):
                        if button.is_clicked(mouse_pos):
                            self.selected_classe = classes[i]
                            for j, other_button in enumerate(self.classe_buttons):
                                other_button.is_active = (j == i)
                
                # Verificar cliques nos botões de matéria (só se for professor)
                if self.selected_user_type == "Professor":
                    for i, button in enumerate(self.materia_buttons):
                        if button.is_clicked(mouse_pos):
                            self.selected_materia = SUBJECTS[i]
                            for j, other_button in enumerate(self.materia_buttons):
                                other_button.is_active = (j == i)
                
                # Verificar cliques nos botões de ação
                if self.salvar_button.is_clicked(mouse_pos):
                    is_valid, message = self.validate_form()
                    if is_valid:
                        success, save_message = self.save_user()
                        if success:
                            self.message = save_message
                            self.message_type = "success"
                            self.message_timer = 180
                            self.clear_form()
                        else:
                            self.message = save_message
                            self.message_type = "error"
                            self.message_timer = 180
                    else:
                        self.message = message
                        self.message_type = "error"
                        self.message_timer = 180
                
                if self.limpar_button.is_clicked(mouse_pos):
                    self.clear_form()
                
                if self.voltar_button.is_clicked(mouse_pos):
                    return {"action": "back_to_user_management"}
            
            # Lidar com entrada de texto
            if event.type == KEYDOWN:
                if self.ra_input.active:
                    if event.key == K_BACKSPACE:
                        self.ra_input.text = self.ra_input.text[:-1]
                    elif event.unicode.isdigit() and len(self.ra_input.text) < self.ra_input.max_length:
                        self.ra_input.text += event.unicode
                
                elif self.nome_input.active:
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
        
        # Título
        title_text = self.title_font.render("Adicionar Usuario", True, (60, 60, 60))
        title_rect = title_text.get_rect(center=(self.center_x, 55))
        self.screen.blit(title_text, title_rect)
        
        # Labels dos campos
        ra_label = self.small_font.render("RA:", True, (80, 80, 80))
        self.screen.blit(ra_label, (self.center_x - 190, 85))
        
        nome_label = self.small_font.render("Nome:", True, (80, 80, 80))
        self.screen.blit(nome_label, (self.center_x - 190, 145))
        
        senha_label = self.small_font.render("Senha:", True, (80, 80, 80))
        self.screen.blit(senha_label, (self.center_x - 190, 205))
        
        tipo_label = self.small_font.render("Tipo de Usuario:", True, (80, 80, 80))
        self.screen.blit(tipo_label, (self.center_x - 120, 245))
        
        # Desenhar campos de entrada
        self.ra_input.draw(self.screen)
        self.nome_input.draw(self.screen)
        self.senha_input.draw(self.screen)
        
        # Desenhar botões de tipo
        self.aluno_button.draw(self.screen)
        self.professor_button.draw(self.screen)
        
        # Desenhar campos específicos baseado no tipo selecionado
        if self.selected_user_type == "Aluno":
            # Labels e botões de série
            serie_label = self.small_font.render("Serie:", True, (80, 80, 80))
            self.screen.blit(serie_label, (self.center_x - 150, 305))
            
            for button in self.serie_buttons:
                button.draw(self.screen)
            
            # Labels e botões de classe
            classe_label = self.small_font.render("Classe:", True, (80, 80, 80))
            self.screen.blit(classe_label, (self.center_x - 120, 355))
            
            for button in self.classe_buttons:
                button.draw(self.screen)
        
        elif self.selected_user_type == "Professor":
            # Labels e botões de matéria
            materia_label = self.small_font.render("Materia:", True, (80, 80, 80))
            self.screen.blit(materia_label, (self.center_x - 200, 305))
            
            for button in self.materia_buttons:
                button.draw(self.screen)
        
        # Desenhar botões de ação
        self.salvar_button.draw(self.screen)
        self.limpar_button.draw(self.screen)
        self.voltar_button.draw(self.screen)
        
        # Desenhar mensagem de feedback
        if self.message:
            color = {
                "success": COLORS["success"],
                "error": COLORS["error"],
                "info": (100, 100, 100)
            }.get(self.message_type, (100, 100, 100))
            
            message_surf = self.text_font.render(self.message, True, color)
            message_rect = message_surf.get_rect(center=(self.center_x, 470))
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