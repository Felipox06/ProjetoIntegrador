# screens/teacher/class_create_screen.py
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

class ClassCreateScreen:
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
        self.success_color = COLORS.get("success", (75, 181, 67))
        
        # Usar fonte padrão do sistema
        self.title_font = pygame.font.SysFont('Arial', 32, bold=True)
        self.subtitle_font = pygame.font.SysFont('Arial', 24, bold=True)
        self.text_font = pygame.font.SysFont('Arial', 18)
        self.small_font = pygame.font.SysFont('Arial', 14)
        
        # Estado do formulário
        self.selected_grade = None
        self.selected_shift = None
        self.error_message = None
        self.success_message = None
        self.message_timer = 0
        
        # Criar elementos de UI
        self.setup_ui()
        
    def setup_ui(self):
        # Painel principal
        self.main_panel = NeumorphicPanel(
            self.center_x - 350, 20, 
            700, 560, 
            self.bg_color, self.light_shadow, self.dark_shadow
        )
        
        # Painel do formulário
        self.form_panel = NeumorphicPanel(
            self.center_x - 300, 70, 
            600, 440, 
            self.bg_color, self.light_shadow, self.dark_shadow,
            border_radius=15
        )
        
        # Campo para nome da turma
        self.class_name_input = NeumorphicInput(
            self.center_x - 250, 130,
            500, 50,
            self.bg_color, self.light_shadow, self.dark_shadow,
            "Nome da Turma (ex: 3º Ano A)", self.text_font
        )
        
        # Botões para série (ano)
        self.grade_buttons = []
        btn_width = 120
        btn_height = 40
        btn_x_start = self.center_x - 250
        btn_y = 230
        
        for i, grade in enumerate(["1º Ano", "2º Ano", "3º Ano"]):
            btn_x = btn_x_start + i * (btn_width + 20)
            button = NeumorphicButton(
                btn_x, btn_y,
                btn_width, btn_height,
                self.bg_color, self.light_shadow, self.dark_shadow,
                self.accent_color, grade, self.text_font,
                is_toggle=True, is_active=False
            )
            self.grade_buttons.append(button)
        
        # Botões para turno
        self.shift_buttons = []
        btn_width = 120
        btn_x_start = self.center_x - 250
        btn_y = 320
        
        for i, shift in enumerate(["Manhã", "Tarde", "Noite"]):
            btn_x = btn_x_start + i * (btn_width + 20)
            button = NeumorphicButton(
                btn_x, btn_y,
                btn_width, btn_height,
                self.bg_color, self.light_shadow, self.dark_shadow,
                self.accent_color, shift, self.text_font,
                is_toggle=True, is_active=False
            )
            self.shift_buttons.append(button)
        
        # Campo para ano letivo
        self.year_input = NeumorphicInput(
            self.center_x - 250, 400,
            500, 50,
            self.bg_color, self.light_shadow, self.dark_shadow,
            "Ano Letivo (ex: 2025)", self.text_font,
            is_numeric=True, max_length=4
        )
        
        # Botões para salvar e cancelar
        button_width = 150
        button_height = 50
        button_y = 520
        
        # Botão CANCELAR à esquerda
        self.cancel_button = NeumorphicButton(
            self.center_x - button_width - 20, button_y,
            button_width, button_height,
            self.bg_color, self.light_shadow, self.dark_shadow,
            COLORS.get("error", (232, 77, 77)), "CANCELAR", self.subtitle_font
        )
        
        # Botão SALVAR à direita
        self.save_button = NeumorphicButton(
            self.center_x + 20, button_y,
            button_width, button_height,
            self.bg_color, self.light_shadow, self.dark_shadow,
            self.success_color, "SALVAR", self.subtitle_font
        )
        
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
    
    def prepare_class_data(self):
        """Preparar dados da turma para salvar no banco de dados"""
        class_data = {
            "name": self.class_name_input.text.strip(),
            "grade": self.selected_grade,
            "shift": self.selected_shift,
            "year": int(self.year_input.text),
            "teacher": self.user_data["username"]  # Professor que criou a turma
        }
        return class_data
    
    def save_class(self):
        """Salvar a turma no banco de dados (simulação)"""
        is_valid, message = self.validate_form()
        if not is_valid:
            # Mostrar mensagem de erro
            self.error_message = message
            self.message_timer = 180  # 3 segundos a 60 FPS
            print(f"Erro ao salvar: {message}")
            return False
        
        # Preparar dados da turma
        class_data = self.prepare_class_data()
        
        # Simulação de salvamento (para futura integração com o banco de dados)
        # Na implementação real, aqui seria a chamada ao modelo para salvar no banco
        print(f"Turma salva com sucesso: {class_data}")
        
        # Exibir mensagem de sucesso
        self.success_message = "Turma criada com sucesso!"
        self.message_timer = 120  # 2 segundos a 60 FPS
        
        # Limpar o formulário após salvar
        self.clear_form()
        
        return True
    
    def clear_form(self):
        """Limpar todos os campos do formulário"""
        # Limpar campos de texto
        self.class_name_input.text = ""
        self.year_input.text = ""
        
        # Limpar seleções
        self.selected_grade = None
        self.selected_shift = None
        
        # Resetar botões de toggle
        for button in self.grade_buttons:
            button.is_active = False
            
        for button in self.shift_buttons:
            button.is_active = False
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
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
                    saved = self.save_class()
                    if saved:
                        # Só retornamos para o menu após alguns frames, para mostrar a mensagem de sucesso
                        if not self.success_message:
                            return {"action": "class_saved"}
                
                # Verificar clique no botão CANCELAR
                if self.cancel_button.is_clicked(mouse_pos):
                    self.cancel_button.pressed = True
                    # Retornar diretamente para o menu
                    return {"action": "back_to_menu"}
            
            # Lidar com entrada de texto
            if event.type == KEYDOWN:
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
        self.save_button.pressed = False
        self.cancel_button.pressed = False
        
        # Atualizar temporizador de mensagens
        if self.message_timer > 0:
            self.message_timer -= 1
            if self.message_timer == 0:
                self.error_message = None
                self.success_message = None
                
                # Se a mensagem de sucesso acabou de desaparecer, retornar ao menu
                if self.success_message:
                    return {"action": "class_saved"}
        
        return {"action": "none"}
    
    def draw(self):
        # Limpa a tela com a cor de fundo
        self.screen.fill(self.bg_color)
        
        # Desenha o painel principal
        self.main_panel.draw(self.screen)
        
        # Desenha o título
        title_text = self.title_font.render("Criar Nova Turma", True, (60, 60, 60))
        title_rect = title_text.get_rect(center=(self.center_x, 45))
        self.screen.blit(title_text, title_rect)
        
        # Desenha o painel do formulário
        self.form_panel.draw(self.screen)
        
        # Desenha os rótulos dos campos
        name_label = self.subtitle_font.render("Nome da Turma:", True, (60, 60, 60))
        name_rect = name_label.get_rect(topleft=(self.class_name_input.rect.x, self.class_name_input.rect.y - 30))
        self.screen.blit(name_label, name_rect)
        
        grade_label = self.subtitle_font.render("Série:", True, (60, 60, 60))
        grade_rect = grade_label.get_rect(topleft=(self.grade_buttons[0].rect.x, self.grade_buttons[0].rect.y - 30))
        self.screen.blit(grade_label, grade_rect)
        
        shift_label = self.subtitle_font.render("Turno:", True, (60, 60, 60))
        shift_rect = shift_label.get_rect(topleft=(self.shift_buttons[0].rect.x, self.shift_buttons[0].rect.y - 30))
        self.screen.blit(shift_label, shift_rect)
        
        year_label = self.subtitle_font.render("Ano Letivo:", True, (60, 60, 60))
        year_rect = year_label.get_rect(topleft=(self.year_input.rect.x, self.year_input.rect.y - 30))
        self.screen.blit(year_label, year_rect)
        
        # Desenha os campos de entrada
        self.class_name_input.draw(self.screen)
        self.year_input.draw(self.screen)
        
        # Desenha os botões de série
        for button in self.grade_buttons:
            button.draw(self.screen)
        
        # Desenha os botões de turno
        for button in self.shift_buttons:
            button.draw(self.screen)
        
        # Desenha os botões de salvar e cancelar
        self.save_button.draw(self.screen)
        self.cancel_button.draw(self.screen)
        
        # Desenha mensagens de erro ou sucesso, se existirem
        if self.error_message:
            error_surf = self.text_font.render(self.error_message, True, COLORS.get("error", (232, 77, 77)))
            error_rect = error_surf.get_rect(center=(self.center_x, self.height - 480))
            self.screen.blit(error_surf, error_rect)
        
        if self.success_message:
            success_surf = self.text_font.render(self.success_message, True, COLORS.get("success", (75, 181, 67)))
            success_rect = success_surf.get_rect(center=(self.center_x, self.height - 480))
            self.screen.blit(success_surf, success_rect)
        
        # Atualiza a tela
        pygame.display.flip()
    
    def run(self):
        while self.running:
            result = self.handle_events()
            
            # Se recebemos uma ação de navegação, retornamos imediatamente
            if result["action"] != "none":
                return result
            
            # Atualizamos o estado da tela e verificamos se há novas ações
            update_result = self.update()
            if update_result["action"] != "none":
                return update_result
            
            # Desenhamos a tela
            self.draw()
            
            # Controlamos a taxa de quadros
            pygame.time.Clock().tick(60)
        
        # Retorno no caso de sair do loop por outros meios
        return {"action": "exit"}