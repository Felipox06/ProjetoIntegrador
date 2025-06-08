# screens/student/game_history.py
# -*- coding: utf-8 -*-

import pygame
import sys
from pygame.locals import *
from databse.data_manager import fetch_player_history_and_stats
from databse.db_connector import getConnection

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

# Classes para elementos de UI neumórficos
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

# Componente para exibir itens na lista de histórico
class HistoryItem:
    def __init__(self, x, y, width, height, bg_color, light_shadow, dark_shadow, 
                 date, subject, grade, score, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = bg_color
        self.light_shadow = light_shadow
        self.dark_shadow = dark_shadow
        self.date = date
        self.subject = subject
        self.grade = grade
        self.score = score
        self.font = font
    
    def draw(self, surface):
        # Fundo do item
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=10)
        
        # Sombras neumórficas
        shadow_rect_light = pygame.Rect(self.rect.x-2, self.rect.y-2, self.rect.width, self.rect.height)
        pygame.draw.rect(surface, self.light_shadow, shadow_rect_light, border_radius=10, width=2)
        
        shadow_rect_dark = pygame.Rect(self.rect.x+2, self.rect.y+2, self.rect.width, self.rect.height)
        pygame.draw.rect(surface, self.dark_shadow, shadow_rect_dark, border_radius=10, width=2)
        
        # Desenhar textos
        margin = 20
        text_y = self.rect.y + (self.rect.height // 2) - 10
        
        # Data
        date_surf = self.font.render(self.date, True, (80, 80, 80))
        date_rect = date_surf.get_rect(topleft=(self.rect.x + margin, text_y))
        surface.blit(date_surf, date_rect)
        
        # Matéria e Série
        subject_surf = self.font.render(f"{self.subject} - {self.grade}", True, (60, 60, 60))
        subject_rect = subject_surf.get_rect(midtop=(self.rect.centerx, text_y))
        surface.blit(subject_surf, subject_rect)
        
        # Pontuação
        score_surf = self.font.render(f"R$ {self.score:,}", True, (50, 120, 50))
        score_rect = score_surf.get_rect(topright=(self.rect.right - margin, text_y))
        surface.blit(score_surf, score_rect)

class GameHistoryScreen:
    def __init__(self, screen, user_data):
        self.screen = screen
        self.running = True
        self.width, self.height = screen.get_size()
        self.user_data = user_data  # Contém user_type (student) e username
        
        # Cores do design neumorfista
        self.bg_color = COLORS["background"]
        self.light_shadow = COLORS["light_shadow"]
        self.dark_shadow = COLORS["dark_shadow"]
        self.accent_color = COLORS["accent"]
        
        # Usar fonte padrão do sistema
        self.title_font = pygame.font.SysFont('Arial', 36, bold=True)
        self.subtitle_font = pygame.font.SysFont('Arial', 24, bold=True)
        self.text_font = pygame.font.SysFont('Arial', 18)
        self.small_font = pygame.font.SysFont('Arial', 16)
        
        # Criar elementos de UI
        self.setup_ui()
        
        # Carregar dados do histórico
        self.load_history_data()
        
        # Para rolagem na lista
        self.scroll_offset = 0
        self.max_items_visible = 8
        
    def setup_ui(self):
        center_x = self.width // 2
        
        # Painel principal
        self.main_panel = NeumorphicPanel(
            center_x - 350, 50, 
            700, 500, 
            self.bg_color, self.light_shadow, self.dark_shadow
        )
        
        # Painel de estatísticas
        self.stats_panel = NeumorphicPanel(
            center_x - 300, 110, 
            600, 120, 
            self.bg_color, self.light_shadow, self.dark_shadow,
            border_radius=15
        )
        
        # Painel de lista de histórico
        self.history_panel = NeumorphicPanel(
            center_x - 300, 250, 
            600, 220, 
            self.bg_color, self.light_shadow, self.dark_shadow,
            border_radius=15
        )
        
        # Botões de rolagem
        self.scroll_up_button = NeumorphicButton(
            center_x + 320, 310,
            40, 40,
            self.bg_color, self.light_shadow, self.dark_shadow,
            self.accent_color, "▲", self.text_font
        )
        
        self.scroll_down_button = NeumorphicButton(
            center_x + 320, 370,
            40, 40,
            self.bg_color, self.light_shadow, self.dark_shadow,
            self.accent_color, "▼", self.text_font
        )
        
        # Botão para voltar ao menu
        self.back_button = NeumorphicButton(
            center_x - 75, 490,
            150, 40,
            self.bg_color, self.light_shadow, self.dark_shadow,
            (232, 77, 77),  # Vermelho para botão de voltar
            "VOLTAR", self.text_font
        )
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Verificar clique no botão de voltar
                if self.back_button.is_clicked(mouse_pos):
                    self.back_button.pressed = True
                    return {"action": "back_to_menu"}
                
                # Verificar cliques nos botões de rolagem
                if self.scroll_up_button.is_clicked(mouse_pos):
                    self.scroll_up_button.pressed = True
                    # max(0, ...) impede que o offset fique negativo
                    self.scroll_offset = max(0, self.scroll_offset - 1)
                    
                if self.scroll_down_button.is_clicked(mouse_pos):
                    self.scroll_down_button.pressed = True
                    # Calcula o offset máximo para não rolar além do final da lista
                    max_offset = max(0, len(self.history_items) - self.max_items_visible)
                    self.scroll_offset = min(max_offset, self.scroll_offset + 1)
                
                # Verificar rolagem com roda do mouse na área do histórico
                # (Assumindo que self.history_panel existe e tem um .rect)
                if self.history_panel.rect.collidepoint(mouse_pos):
                    if event.button == 4:  # Rolar para cima
                        self.scroll_offset = max(0, self.scroll_offset - 1)
                    elif event.button == 5:  # Rolar para baixo
                        max_offset = max(0, len(self.history_items) - self.max_items_visible)
                        self.scroll_offset = min(max_offset, self.scroll_offset + 1)
        
        return {"action": "none"}
        
    def load_history_data(self):
        """
        Carrega as estatísticas gerais e o histórico de jogos recentes
        do jogador logado a partir do banco de dados.
        """
        # Inicializar com valores padrão/vazios
        self.student_stats = {
            "money_total": 0,
            "games_played": 0,
        }
        self.history_items = [] # Começa com a lista de histórico vazia

        # 1. Obter o RA do jogador logado a partir de self.user_data
        player_ra = self.user_data.get("RA")
        if not player_ra:
            print("ERRO (GameHistoryScreen): Não foi possível encontrar o RA do usuário logado.")
            return # Interrompe o carregamento

        print(f"GameHistoryScreen: Buscando histórico e estatísticas para o RA: {player_ra}")
        
        # 2. Chamar a função do data_manager para buscar todos os dados
        all_data = None
        try:
            # Lembre-se de importar fetch_player_history_and_stats do seu data_manager.py
            all_data = fetch_player_history_and_stats(
                player_ra, 
                getConnection, 
                limit=5
            )
        except NameError as ne:
            print(f"Erro de Configuração (GameHistoryScreen): Função não encontrada. Verifique os imports. {ne}")
        except Exception as e:
            print(f"Erro inesperado (GameHistoryScreen) ao carregar histórico: {e}")

        # 3. Preencher os atributos da classe com os dados retornados
        if all_data:
            # Preenche os dados do resumo (Dinheiro Total, Jogos Realizados)
            summary = all_data.get("summary_stats", {})
            self.student_stats["money_total"] = summary.get('total_score', 0)
            self.student_stats["games_played"] = summary.get('total_games', 0)
            
            # Preenche e formata a lista de histórico para exibição
            recent_games_from_db = all_data.get("recent_games", [])
            for game_log in recent_games_from_db:
                # O dicionário 'game_log' tem as chaves: "date", "subject", "grade", "score"
                # vindas da função fetch_player_history_and_stats
                
                # Formatar a data (que vem como objeto datetime do banco)
                date_object = game_log.get("date")
                formatted_date = date_object.strftime("%d/%m/%Y") if date_object else "Data Inválida"
                
                # Monta o dicionário no formato que sua UI espera
                ui_item = {
                    "date": formatted_date,
                    "subject": game_log.get("subject", "N/A"),
                    "grade": game_log.get("grade", "N/A"),
                    "score": game_log.get("score", 0)
                }
                self.history_items.append(ui_item)
            
            print(f"GameHistoryScreen: Dados carregados. {self.student_stats['games_played']} jogos no total. Exibindo os {len(self.history_items)} mais recentes.")
        else:
            print("AVISO (GameHistoryScreen): Nenhum dado de histórico ou estatísticas encontrado para este jogador.")
            # self.student_stats e self.history_items permanecerão com os valores padrão (0 e lista vazia)
    
    def update(self):
        # Redefinir estado dos botões
        self.back_button.pressed = False
        self.scroll_up_button.pressed = False
        self.scroll_down_button.pressed = False
    
    def draw(self):
        # Limpa a tela com a cor de fundo
        self.screen.fill(self.bg_color)
        
        # Desenha o painel principal
        self.main_panel.draw(self.screen)
        
        # Desenha o título
        title_text = self.title_font.render("Histórico de Jogos", True, (60, 60, 60))
        title_rect = title_text.get_rect(center=(self.width // 2, 85))
        self.screen.blit(title_text, title_rect)
        
        # Desenha o painel de estatísticas
        self.stats_panel.draw(self.screen)
        
        # Desenha as estatísticas
        stats_y = 125
        line_height = 30
        
        stats_text = [
            f"Dinheiro Total: R$ {self.student_stats['money_total']:,}",
            f"Jogos Realizados: {self.student_stats['games_played']}",
        ]
        
        for i, text in enumerate(stats_text):
            surf = self.text_font.render(text, True, (60, 60, 60))
            rect = surf.get_rect(midleft=(self.stats_panel.rect.x + 30, stats_y + i * line_height))
            self.screen.blit(surf, rect)
        
        # Desenha o painel de histórico
        self.history_panel.draw(self.screen)
        
        # Desenha o cabeçalho da lista
        header_y = self.history_panel.rect.y + 15
        
        date_header = self.small_font.render("Data", True, (100, 100, 100))
        date_rect = date_header.get_rect(topleft=(self.history_panel.rect.x + 20, header_y))
        self.screen.blit(date_header, date_rect)
        
        subject_header = self.small_font.render("Matéria - Série", True, (100, 100, 100))
        subject_rect = subject_header.get_rect(midtop=(self.history_panel.rect.centerx, header_y))
        self.screen.blit(subject_header, subject_rect)
        
        score_header = self.small_font.render("Pontuação", True, (100, 100, 100))
        score_rect = score_header.get_rect(topright=(self.history_panel.rect.right - 20, header_y))
        self.screen.blit(score_header, score_rect)
        
        # Desenha uma linha separadora
        pygame.draw.line(
            self.screen, 
            (200, 200, 200), 
            (self.history_panel.rect.x + 15, header_y + 25),
            (self.history_panel.rect.right - 15, header_y + 25),
            1
        )
        
        # Desenha os itens do histórico (com rolagem)
        item_height = 40
        item_spacing = 5
        start_y = header_y + 35
        
        visible_items = self.history_items[self.scroll_offset:self.scroll_offset + self.max_items_visible]
        
        for i, item in enumerate(visible_items):
            item_y = start_y + i * (item_height + item_spacing)
            
            # Só desenhar se estiver visível dentro do painel
            if item_y < self.history_panel.rect.bottom - 20:
                history_item = HistoryItem(
                    self.history_panel.rect.x + 15,
                    item_y,
                    self.history_panel.rect.width - 80,  # Deixa espaço para os botões de rolagem
                    item_height,
                    self.bg_color,
                    self.light_shadow,
                    self.dark_shadow,
                    item["date"],
                    item["subject"],
                    item["grade"],
                    item["score"],
                    self.small_font
                )
                history_item.draw(self.screen)
        
        # Desenha os botões de rolagem
        if len(self.history_items) > self.max_items_visible:
            self.scroll_up_button.draw(self.screen)
            self.scroll_down_button.draw(self.screen)
        
        # Desenha o botão de voltar
        self.back_button.draw(self.screen)
        
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