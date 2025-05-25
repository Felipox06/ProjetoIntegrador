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
        "accent": (27, 185, 185),
        "text": (60, 60, 60),
        "success": (75, 181, 67),
        "warning": (251, 164, 31),
        "error": (232, 77, 77),
        "black": (0, 0, 0),
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
        # Desenhar borda preta fina
        pygame.draw.rect(surface, (0, 0, 0), self.rect, width=1, border_radius=self.border_radius)


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

            # Borda preta fina ao redor do botão
            pygame.draw.rect(surface, (0, 0, 0), self.rect, 
            width=1, border_radius=10)
            
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
        bg_color = (255, 220, 220) if self.is_selected else self.bg_color  # Vermelho claro para remoção
        
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=10)
        
        # Sombras neumórficas
        shadow_rect_light = pygame.Rect(self.rect.x-2, self.rect.y-2, self.rect.width, self.rect.height)
        pygame.draw.rect(surface, self.light_shadow, shadow_rect_light, border_radius=10, width=2)
        
        shadow_rect_dark = pygame.Rect(self.rect.x+2, self.rect.y+2, self.rect.width, self.rect.height)
        pygame.draw.rect(surface, self.dark_shadow, shadow_rect_dark, border_radius=10, width=2)
        
        # Adicionar borda especial se selecionado
        if self.is_selected:
            pygame.draw.rect(surface, COLORS.get("error", (232, 77, 77)), 
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

class ConfirmationDialog:
    def __init__(self, x, y, width, height, bg_color, light_shadow, dark_shadow, 
                 text, font, text_font):
        self.panel = NeumorphicPanel(x, y, width, height, bg_color, light_shadow, dark_shadow)
        self.text = text
        self.font = font
        self.text_font = text_font
        
        # Botões
        button_width = 120
        button_height = 40
        button_y = y + height - 60
        
        self.confirm_button = NeumorphicButton(
            x + width//2 - button_width - 10, button_y,
            button_width, button_height,
            bg_color, light_shadow, dark_shadow,
            COLORS.get("error", (232, 77, 77)),
            "CONFIRMAR", text_font
        )
        
        self.cancel_button = NeumorphicButton(
            x + width//2 + 10, button_y,
            button_width, button_height,
            bg_color, light_shadow, dark_shadow,
            (100, 100, 100),
            "CANCELAR", text_font
        )
    
    def handle_events(self, event, mouse_pos):
        if event.type == MOUSEBUTTONDOWN:
            if self.confirm_button.is_clicked(mouse_pos):
                self.confirm_button.pressed = True
                return "confirm"
            
            if self.cancel_button.is_clicked(mouse_pos):
                self.cancel_button.pressed = True
                return "cancel"
        
        return None
    
    def update(self):
        self.confirm_button.pressed = False
        self.cancel_button.pressed = False
    
    def draw(self, surface):
        # Desenhar painel de fundo semi-transparente
        overlay = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Preto com 50% de opacidade
        surface.blit(overlay, (0, 0))
        
        # Desenhar o painel do diálogo
        self.panel.draw(surface)
        
        # Desenhar título
        title_surf = self.font.render("Confirmação", True, COLORS.get("error", (232, 77, 77)))
        title_rect = title_surf.get_rect(midtop=(self.panel.rect.centerx, self.panel.rect.y + 20))
        surface.blit(title_surf, title_rect)
        
        # Desenhar texto
        text_surf = self.text_font.render(self.text, True, (50, 50, 50))
        text_rect = text_surf.get_rect(center=(self.panel.rect.centerx, self.panel.rect.centery - 20))
        surface.blit(text_surf, text_rect)
        
        # Desenhar botões
        self.confirm_button.draw(surface)
        self.cancel_button.draw(surface)

class ClassRemoveScreen:
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
        
        # Estado do diálogo de confirmação
        self.show_confirmation = False
        
        # Estado de mensagem
        self.message = None
        self.message_timer = 0
        
        # Para rolagem na lista
        self.scroll_offset = 0
        self.max_items_visible = 6  # Número de turmas visíveis por vez
        
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
            660, 430, 
            self.bg_color, self.light_shadow, self.dark_shadow,
            border_radius=15
        )
        
        # Botões de rolagem para a lista
        self.scroll_up_button = NeumorphicButton(
            self.center_x + 290, 120,
            35, 35,
            self.bg_color, self.light_shadow, self.dark_shadow,
            self.accent_color, "▲", self.text_font
        )
        
        self.scroll_down_button = NeumorphicButton(
            self.center_x + 290, 410,
            35, 35,
            self.bg_color, self.light_shadow, self.dark_shadow,
            self.accent_color, "▼", self.text_font
        )
        
        # Botão para remover a turma selecionada
        self.remove_button = NeumorphicButton(
            self.center_x - 75, 520,
            150, 40,
            self.bg_color, self.light_shadow, self.dark_shadow,
            COLORS.get("error", (232, 77, 77)),  # Vermelho para remover
            "REMOVER", self.text_font
        )
        
        # Botão para voltar ao menu
        self.back_button = NeumorphicButton(
            self.center_x - 250, 520,
            150, 40,
            self.bg_color, self.light_shadow, self.dark_shadow,
            (100, 100, 100),  # Cinza para botão de voltar
            "VOLTAR", self.text_font
        )
        
        # Diálogo de confirmação
        self.confirmation_dialog = ConfirmationDialog(
            self.center_x - 200, self.center_x - 100,
            400, 200,
            self.bg_color, self.light_shadow, self.dark_shadow,
            "Tem certeza que deseja excluir esta turma?",
            self.subtitle_font, self.text_font
        )
        
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
            {
                "id": 7,
                "name": "3º Ano C",
                "grade": "3º Ano",
                "shift": "Noite",
                "year": 2025,
                "teacher": "Professor Silva"
            },
            {
                "id": 8,
                "name": "2º Ano C",
                "grade": "2º Ano",
                "shift": "Noite",
                "year": 2025,
                "teacher": "Professor Silva"
            },
        ]
        return classes
    
    def remove_class(self):
        """Remover a turma selecionada"""
        if not self.selected_class:
            return False
        
        # Remover da lista local (simulação)
        self.classes = [c for c in self.classes if c["id"] != self.selected_class["id"]]
        
        # Simulação de remoção do banco de dados
        print(f"Turma removida: {self.selected_class}")
        
        # Mensagem de sucesso
        self.message = f"Turma '{self.selected_class['name']}' removida com sucesso!"
        self.message_timer = 180  # 3 segundos
        
        # Reset da seleção
        self.selected_class = None
        
        return True
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            
            # Se o diálogo de confirmação estiver aberto, processar apenas seus eventos
            if self.show_confirmation:
                result = self.confirmation_dialog.handle_events(event, pygame.mouse.get_pos())
                if result == "confirm":
                    self.remove_class()
                    self.show_confirmation = False
                elif result == "cancel":
                    self.show_confirmation = False
                continue
                
            if event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
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
                
                # Verificar cliques nos botões de rolagem
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
                
                # Verificar clique no botão REMOVER
                if self.remove_button.is_clicked(mouse_pos) and self.selected_class:
                    self.remove_button.pressed = True
                    # Mostrar diálogo de confirmação
                    self.show_confirmation = True
                
                # Verificar clique no botão VOLTAR
                if self.back_button.is_clicked(mouse_pos):
                    self.back_button.pressed = True
                    return {"action": "back_to_menu"}
        
        return {"action": "none"}
    
    def update(self):
        # Resetar estado dos botões
        self.remove_button.pressed = False
        self.back_button.pressed = False
        self.scroll_up_button.pressed = False
        self.scroll_down_button.pressed = False
        
        # Atualizar diálogo de confirmação
        if self.show_confirmation:
            self.confirmation_dialog.update()
        
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
        title_text = self.title_font.render("Remover Turmas", True, (60, 60, 60))
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
        
        # Desenha o botão de remover (ativo apenas se uma turma estiver selecionada)
        if self.selected_class:
            self.remove_button.draw(self.screen)
        else:
            # Versão desativada do botão
            disabled_button = NeumorphicButton(
                self.remove_button.rect.x, self.remove_button.rect.y,
                self.remove_button.rect.width, self.remove_button.rect.height,
                self.bg_color, self.light_shadow, self.dark_shadow,
                (180, 180, 180),  # Cinza para botão desativado
                "REMOVER", self.text_font
            )
            disabled_button.draw(self.screen)
            
            # Mensagem de dica
            hint_text = self.small_font.render("Selecione uma turma para remover", True, (120, 120, 120))
            hint_rect = hint_text.get_rect(midtop=(self.remove_button.rect.centerx, self.remove_button.rect.bottom + 5))
            self.screen.blit(hint_text, hint_rect)
        
        # Desenha o botão de voltar
        self.back_button.draw(self.screen)
        
        # Desenha mensagem de feedback, se houver
        if self.message:
            message_color = COLORS.get("success", (75, 181, 67))
            message_surf = self.text_font.render(self.message, True, message_color)
            message_rect = message_surf.get_rect(midbottom=(self.center_x, self.height - 10))
            self.screen.blit(message_surf, message_rect)
        
        # Desenha o diálogo de confirmação se estiver aberto
        if self.show_confirmation:
            self.confirmation_dialog.draw(self.screen)
        
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