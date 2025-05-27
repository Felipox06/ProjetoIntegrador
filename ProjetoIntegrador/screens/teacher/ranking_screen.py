# screens/teacher/ranking_screen.py
# -*- coding: utf-8 -*-

import pygame
import sys
from pygame.locals import *
from databse.data_manager import search_ranking_data_from_db
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

class StudentRankItem:
    def __init__(self, x, y, width, height, bg_color, light_shadow, dark_shadow, 
                 rank, student_name, ra, series, score, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = bg_color
        self.light_shadow = light_shadow
        self.dark_shadow = dark_shadow
        self.rank = rank
        self.student_name = student_name
        self.ra = ra
        self.series = series
        self.score = score
        self.font = font
        self.small_font = pygame.font.SysFont('Arial', font.get_height() - 4)
        
        # Determinar cor de fundo com base na posição (podium)
        if rank == 1:
            self.bg_color = (255, 246, 200)  # Dourado para primeiro
        elif rank == 2:
            self.bg_color = (240, 240, 245)  # Prateado para segundo
        elif rank == 3:
            self.bg_color = (245, 220, 180)  # Bronze para terceiro
    
    def draw(self, surface):
        # Desenhar fundo
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=10)
        
        # Desenhar sombras neumórficas
        shadow_rect_light = pygame.Rect(self.rect.x-2, self.rect.y-2, self.rect.width, self.rect.height)
        pygame.draw.rect(surface, self.light_shadow, shadow_rect_light, border_radius=10, width=2)
        
        shadow_rect_dark = pygame.Rect(self.rect.x+2, self.rect.y+2, self.rect.width, self.rect.height)
        pygame.draw.rect(surface, self.dark_shadow, shadow_rect_dark, border_radius=10, width=2)
        
        # Desenhar textos com margens e colunas
        margin = 15
        center_y = self.rect.y + (self.rect.height // 2)
        
        # Posição/ranking
        rank_color = (220, 180, 0) if self.rank <= 3 else (80, 80, 80)
        rank_text = f"#{self.rank}"
        rank_surf = self.font.render(rank_text, True, rank_color)
        rank_rect = rank_surf.get_rect(midleft=(self.rect.x + margin, center_y))
        surface.blit(rank_surf, rank_rect)
        
        # Nome do aluno
        name_x = self.rect.x + 60
        name_text = self.student_name
        name_surf = self.font.render(name_text, True, (60, 60, 60))
        name_rect = name_surf.get_rect(midleft=(name_x, center_y))
        surface.blit(name_surf, name_rect)
        
        # RA do aluno (Registro Acadêmico)
        ra_x = name_x + 220
        ra_text = f"RA: {self.ra}"
        ra_surf = self.small_font.render(ra_text, True, (100, 100, 100))
        ra_rect = ra_surf.get_rect(midleft=(ra_x, center_y))
        surface.blit(ra_surf, ra_rect)
        
        # Série
        series_x = ra_x + 120
        series_text = f"Série: {self.series}"
        series_surf = self.small_font.render(series_text, True, (100, 100, 100))
        series_rect = series_surf.get_rect(midleft=(series_x, center_y))
        surface.blit(series_surf, series_rect)
        
        # Jogos jogados
        
        # Pontuação (à direita)
        score_text = f"R$ {self.score:,}"
        score_color = (50, 150, 50)  # Verde para pontuação
        score_surf = self.font.render(score_text, True, score_color)
        score_rect = score_surf.get_rect(midright=(self.rect.right - margin, center_y))
        surface.blit(score_surf, score_rect)

class RankingScreen:
    def __init__(self, screen, user_data):
        self.screen = screen
        self.running = True
        self.width, self.height = screen.get_size()
        self.user_data = user_data  # Contém user_type (teacher) e username
        self.center_x = self.width // 2  # Salvar center_x como atributo da classe
        
        # Cores do design neumorfista
        self.bg_color = COLORS["background"]
        self.light_shadow = COLORS["light_shadow"]
        self.dark_shadow = COLORS["dark_shadow"]
        self.accent_color = COLORS["accent"]
        
        # Usar fonte padrão do sistema
        self.title_font = pygame.font.SysFont('Arial', 36, bold=True)
        self.subtitle_font = pygame.font.SysFont('Arial', 24, bold=True)
        self.text_font = pygame.font.SysFont('Arial', 18)
        self.small_font = pygame.font.SysFont('Arial', 14)
        
        # Estado de rolagem
        self.scroll_offset = 0
        self.max_items_visible = 8  # Número de alunos visíveis por vez
        
        # Estado de filtragem
        self.filter_by_series = None
        self.filter_by_name = ""
        self.show_filters = False
        
        # Criar elementos de UI
        self.setup_ui()
        
        # Carregar dados dos alunos
        self.students = self.load_students()
        self.filtered_students = self.students
        
    def setup_ui(self):
        center_x = self.center_x
        
        # Painel principal
        self.main_panel = NeumorphicPanel(
            center_x - 350, 20, 
            700, 560, 
            self.bg_color, self.light_shadow, self.dark_shadow
        )
        
        # Painel de cabeçalho/filtros
        self.header_panel = NeumorphicPanel(
            center_x - 330, 70, 
            660, 60, 
            self.bg_color, self.light_shadow, self.dark_shadow,
            border_radius=15
        )
        
        # Botão para mostrar/esconder filtros
        self.toggle_filters_button = NeumorphicButton(
            center_x + 235, 85,
            100, 30,
            self.bg_color, self.light_shadow, self.dark_shadow,
            self.accent_color, "FILTROS", self.small_font,
            is_toggle=True
        )
        
        # Botões para filtrar por série (inicialmente ocultos)
        self.series_buttons = []
        btn_width = 80
        btn_height = 30
        btn_x_start = center_x - 200
        btn_y = 85
        
        for i, series in enumerate(["1º Ano", "2º Ano", "3º Ano"]):
            btn_x = btn_x_start + i * (btn_width + 10)
            button = NeumorphicButton(
                btn_x, btn_y,
                btn_width, btn_height,
                self.bg_color, self.light_shadow, self.dark_shadow,
                self.accent_color, series, self.small_font,
                is_toggle=True
            )
            self.series_buttons.append(button)
        
        # Botão para limpar filtros (inicialmente oculto)
        self.clear_filters_button = NeumorphicButton(
            center_x + 120, 85,
            100, 30,
            self.bg_color, self.light_shadow, self.dark_shadow,
            COLORS.get("warning", (232, 181, 12)), "LIMPAR", self.small_font
        )
        
        # Painel da lista de alunos
        self.list_panel = NeumorphicPanel(
            center_x - 330, 140, 
            660, 370, 
            self.bg_color, self.light_shadow, self.dark_shadow,
            border_radius=15
        )
        
        # Botões de rolagem
        self.scroll_up_button = NeumorphicButton(
            center_x + 290, 200,
            35, 35,
            self.bg_color, self.light_shadow, self.dark_shadow,
            self.accent_color, "▲", self.text_font
        )
        
        self.scroll_down_button = NeumorphicButton(
            center_x + 290, 410,
            35, 35,
            self.bg_color, self.light_shadow, self.dark_shadow,
            self.accent_color, "▼", self.text_font
        )
        
        # Botão para voltar ao menu
        self.back_button = NeumorphicButton(
            center_x - 75, 520,
            150, 40,
            self.bg_color, self.light_shadow, self.dark_shadow,
            (232, 77, 77),  # Vermelho para botão de voltar
            "VOLTAR", self.text_font
        )
        
    def load_students(self, serie_filter=None): 
        # Carrega os dados dos alunos para o ranking, utilizando a função do data_manager.

        # A lista mock_students é removida.
        # A ordenação com sorted() é removida (o DB já ordena).
        try:
            # Chama a função importada, passando o método de obter conexão
            # da instância atual (self.getConnection) e o filtro.
            students_list = search_ranking_data_from_db(getConnection, serie_filter=serie_filter)
            return students_list
        except NameError as ne:
            # Isso pode acontecer se fetch_ranking_data_from_db não for importada corretamente
            print(f"Erro em RankingScreen: Função 'fetch_ranking_data_from_db' não encontrada. Verifique a importação. ({ne})")
            return [] # Retorna lista vazia em caso de erro de importação
        except Exception as e:
            # Captura outros erros que podem ocorrer na chamada
            print(f"Erro inesperado em RankingScreen ao tentar carregar estudantes: {e}")
            return [] # Retorna lista vazia
    
    def apply_filters(self):
        # Aplicar filtro por série
        filtered = self.students
        
        if self.filter_by_series:
            filtered = [s for s in filtered if s["series"] == self.filter_by_series]
            
        # Aplicar filtro por nome (se implementado)
        if self.filter_by_name:
            filtered = [s for s in filtered if self.filter_by_name.lower() in s["name"].lower()]
            
        self.filtered_students = filtered
        self.scroll_offset = 0  # Reset da rolagem
    
    def clear_filters(self):
        # Limpar todos os filtros
        self.filter_by_series = None
        
        # Resetar botões de série
        for button in self.series_buttons:
            button.is_active = False
            
        # Mostrar todos os alunos
        self.filtered_students = self.students
        self.scroll_offset = 0
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Verificar clique no botão de mostrar/esconder filtros
                if self.toggle_filters_button.is_clicked(mouse_pos):
                    self.toggle_filters_button.is_active = not self.toggle_filters_button.is_active
                    self.show_filters = self.toggle_filters_button.is_active
                
                # Se os filtros estiverem visíveis, verificar cliques neles
                if self.show_filters:
                    # Verificar cliques nos botões de série
                    for i, button in enumerate(self.series_buttons):
                        if button.is_clicked(mouse_pos):
                            # Toggle do botão
                            button.is_active = not button.is_active
                            
                            # Atualizar filtro
                            series_options = ["1º Ano", "2º Ano", "3º Ano"]
                            self.filter_by_series = series_options[i] if button.is_active else None
                            
                            # Desativar outros botões se este foi ativado
                            if button.is_active:
                                for j, other_button in enumerate(self.series_buttons):
                                    if j != i:
                                        other_button.is_active = False
                            
                            # Aplicar filtros
                            self.apply_filters()
                            break
                    
                    # Verificar clique no botão de limpar filtros
                    if self.clear_filters_button.is_clicked(mouse_pos):
                        self.clear_filters_button.pressed = True
                        self.clear_filters()
                
                # Verificar cliques nos botões de rolagem
                if self.scroll_up_button.is_clicked(mouse_pos) and self.scroll_offset > 0:
                    self.scroll_up_button.pressed = True
                    self.scroll_offset -= 1
                
                if self.scroll_down_button.is_clicked(mouse_pos) and self.scroll_offset < len(self.filtered_students) - self.max_items_visible:
                    self.scroll_down_button.pressed = True
                    self.scroll_offset += 1
                
                # Verificar rolagem com roda do mouse
                if event.button == 4 and self.list_panel.rect.collidepoint(mouse_pos):  # Rolar para cima
                    if self.scroll_offset > 0:
                        self.scroll_offset -= 1
                        
                elif event.button == 5 and self.list_panel.rect.collidepoint(mouse_pos):  # Rolar para baixo
                    if self.scroll_offset < len(self.filtered_students) - self.max_items_visible:
                        self.scroll_offset += 1
                
                # Verificar clique no botão VOLTAR
                if self.back_button.is_clicked(mouse_pos):
                    self.back_button.pressed = True
                    return {"action": "back_to_menu"}
        
        return {"action": "none"}
    
    def update(self):
        # Resetar estado dos botões
        self.clear_filters_button.pressed = False
        self.back_button.pressed = False
        self.scroll_up_button.pressed = False
        self.scroll_down_button.pressed = False
    
    def draw(self):
        center_x = self.center_x
        # Limpa a tela com a cor de fundo
        self.screen.fill(self.bg_color)
        
        # Desenha o painel principal
        self.main_panel.draw(self.screen)
        
        # Desenha o título
        title_text = self.title_font.render("Ranking de Alunos", True, (60, 60, 60))
        title_rect = title_text.get_rect(center=(self.width // 2, 45))
        self.screen.blit(title_text, title_rect)
        
        # Desenha o painel de cabeçalho
        self.header_panel.draw(self.screen)
        
        # Desenha o botão de toggle para filtros
        self.toggle_filters_button.draw(self.screen)
        
        # Se os filtros estiverem visíveis, desenha os controles de filtro
        if self.show_filters:
            # Desenha os botões de filtro por série
            for button in self.series_buttons:
                button.draw(self.screen)
            
            # Desenha o botão de limpar filtros
            self.clear_filters_button.draw(self.screen)
            
            # Texto explicativo
            filter_text = self.small_font.render("Filtrar por série:", True, (80, 80, 80))
            filter_rect = filter_text.get_rect(midleft=(center_x - 280, self.header_panel.rect.centery))
            self.screen.blit(filter_text, filter_rect)
        else:
            # Texto sobre o total de alunos
            total_text = self.text_font.render(f"Total de alunos: {len(self.filtered_students)}", True, (80, 80, 80))
            total_rect = total_text.get_rect(midleft=(center_x - 280, self.header_panel.rect.centery))
            self.screen.blit(total_text, total_rect)
        
        # Desenha o painel da lista
        self.list_panel.draw(self.screen)
        
        # Desenha os alunos filtrados
        if len(self.filtered_students) == 0:
            # Mensagem se não houver alunos
            no_students_text = self.text_font.render("Nenhum aluno encontrado", True, (100, 100, 100))
            no_students_rect = no_students_text.get_rect(center=(self.list_panel.rect.centerx, self.list_panel.rect.centery))
            self.screen.blit(no_students_text, no_students_rect)
        else:
            # Desenha os alunos visíveis
            start_y = self.list_panel.rect.y + 20
            item_height = 60
            item_spacing = 10
            
            visible_students = self.filtered_students[self.scroll_offset:self.scroll_offset + self.max_items_visible]
            for i, student in enumerate(visible_students):
                item_y = start_y + i * (item_height + item_spacing)
                
                # Calcular a posição no ranking (considerando o scroll_offset)
                rank = i + 1 + self.scroll_offset
                
                student_item = StudentRankItem(
                    self.list_panel.rect.x + 20,
                    item_y,
                    self.list_panel.rect.width - 80,
                    item_height,
                    self.bg_color,
                    self.light_shadow,
                    self.dark_shadow,
                    rank,
                    student["name"],
                    student["ra"],
                    student["series"],
                    student["score"],
                    self.text_font
                )
                student_item.draw(self.screen)
            
            # Desenha indicadores de rolagem se houver mais itens
            if len(self.filtered_students) > self.max_items_visible:
                self.scroll_up_button.draw(self.screen)
                self.scroll_down_button.draw(self.screen)
                
                # Indicador de posição da rolagem
                total_items = len(self.filtered_students)
                progress_height = 100
                progress_rect = pygame.Rect(
                    self.scroll_up_button.rect.centerx - 2,
                    self.scroll_up_button.rect.bottom + 10,
                    4,
                    progress_height
                )
                pygame.draw.rect(self.screen, (200, 200, 200), progress_rect, border_radius=2)
                
                # Indicador de posição atual
                if total_items > 0:
                    indicator_height = max(20, progress_height / total_items * self.max_items_visible)
                    indicator_pos = (self.scroll_offset / max(1, total_items - self.max_items_visible)) * (progress_height - indicator_height)
                    indicator_rect = pygame.Rect(
                        progress_rect.x - 1,
                        progress_rect.y + indicator_pos,
                        6,
                        indicator_height
                    )
                    pygame.draw.rect(self.screen, self.accent_color, indicator_rect, border_radius=3)
        
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