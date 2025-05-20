# screens/student/score_screen.py
import sys
import os
from pathlib import Path
import pygame
from pygame.locals import *

# Correção de imports e debug
print("[DEBUG] Iniciando score_screen.py...")
try:
    # Adiciona o diretório pai ao path
    current_dir = Path(__file__).parent
    project_root = current_dir.parent.parent
    sys.path.append(str(project_root))
    print(f"[DEBUG] Projeto root: {project_root}")
except Exception as e:
    print(f"[DEBUG] Erro ao configurar path: {e}")

class SimpleButton:
    def __init__(self, x, y, width, height, bg_color, text, font, text_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = bg_color
        self.text = text
        self.font = font
        self.text_color = text_color
        self.pressed = False
        
        # Verifica se o font é válido
        if font:
            self.text_surface = font.render(text, True, text_color)
            self.text_rect = self.text_surface.get_rect(center=self.rect.center)
        else:
            print("[ERRO] Font inválido no SimpleButton")

    def is_clicked(self, pos):
        if self.rect.collidepoint(pos):
            self.pressed = True
            return True
        return False

    def draw(self, screen):
        try:
            # Desenha botão retangular com fundo amarelo
            if self.pressed:
                color = tuple(max(0, c - 30) for c in self.bg_color)
            else:
                color = self.bg_color
            
            # Sombra (sem alpha por compatibilidade)
            shadow_color = (50, 50, 50)
            shadow_rect = self.rect.copy()
            shadow_rect.x += 3
            shadow_rect.y += 3
            pygame.draw.rect(screen, shadow_color, shadow_rect, border_radius=5)
            
            # Botão principal
            pygame.draw.rect(screen, color, self.rect, border_radius=5)
            pygame.draw.rect(screen, (50, 50, 50), self.rect, 2, border_radius=5)
            
            # Texto do botão
            if hasattr(self, 'text_surface'):
                screen.blit(self.text_surface, self.text_rect)
        except Exception as e:
            print(f"[ERRO] Erro ao desenhar botão: {e}")

class ScoreScreen:
    def __init__(self, player_id=1, game_results=None, width=800, height=600):
        print("[DEBUG] Inicializando ScoreScreen...")
        
        # Inicializa pygame primeiro
        try:
            pygame.init()
            print("[DEBUG] Pygame inicializado com sucesso")
        except Exception as e:
            print(f"[ERRO] Falha ao inicializar pygame: {e}")
            raise
        
        # Configura a tela
        try:
            self.screen = pygame.display.set_mode((width, height))
            pygame.display.set_caption("Show do Milhão - Pontuação")
            print("[DEBUG] Tela criada com sucesso")
        except Exception as e:
            print(f"[ERRO] Falha ao criar tela: {e}")
            raise
        
        # Inicializa clock
        self.clock = pygame.time.Clock()
        
        # Carrega fontes com fallback
        try:
            self.font_title = pygame.font.Font(None, 52)
            self.font_table_header = pygame.font.Font(None, 26)
            self.font_table_data = pygame.font.Font(None, 24)
            self.font_logo = pygame.font.Font(None, 20)
            print("[DEBUG] Fontes carregadas com sucesso")
        except Exception as e:
            print(f"[ERRO] Falha ao carregar fontes: {e}")
            # Fallback para fonte padrão
            self.font_title = pygame.font.get_default_font()
            self.font_table_header = pygame.font.get_default_font()
            self.font_table_data = pygame.font.get_default_font()
            self.font_logo = pygame.font.get_default_font()
        
        # Variáveis de controle
        self.running = True
        self.player_id = player_id
        self.game_results = game_results or {}

        # Cores da interface
        self.ORANGE_COLOR = (255, 152, 51)
        self.TURQUOISE_COLOR = (64, 199, 216)
        self.TEXT_BLACK = (35, 35, 35)
        self.LINE_COLOR = (80, 80, 80)
        self.BUTTON_BLACK = (35, 35, 35)
        self.YELLOW_COLOR = (255, 215, 0)  # Cor amarela para os botões

        # Dados placeholder
        self.matches_data = []
        
        try:
            self._setup_ui()
            print("[DEBUG] Interface configurada com sucesso")
        except Exception as e:
            print(f"[ERRO] Falha ao configurar interface: {e}")
            raise

    def _setup_ui(self):
        """Configura a interface"""
        try:
            # Botão casa (agora retangular e amarelo)
            self.home_button = SimpleButton(
                30, 30, 80, 40,
                self.YELLOW_COLOR, "Sair", self.font_table_header, (0, 0, 0)
            )
            
            # Botão configurações (agora retangular e amarelo)
            self.settings_button = SimpleButton(
                30, 530, 80, 40,
                self.YELLOW_COLOR, "SET", self.font_table_header, (0, 0, 0)
            )

            # Renderiza textos (logo removido)
            self.title_text = self.font_title.render("Pontuação", True, self.TEXT_BLACK)
            
            print("[DEBUG] Elementos UI criados com sucesso")
        except Exception as e:
            print(f"[ERRO] Erro ao criar elementos UI: {e}")
            raise

    def _draw_background(self):
        """Desenha o fundo"""
        try:
            # Fundo laranja
            self.screen.fill(self.ORANGE_COLOR)
            
            # Área turquesa central
            turquoise_rect = pygame.Rect(10, 10, 780, 580)
            pygame.draw.rect(self.screen, self.TURQUOISE_COLOR, turquoise_rect, border_radius=30)
        except Exception as e:
            print(f"[ERRO] Erro ao desenhar fundo: {e}")

    def _draw_logo(self):
        """Desenha o logo (removido conforme solicitado)"""
        # Logo removido - função mantida para compatibilidade
        pass

    def _draw_table(self):
        """Desenha a tabela de pontuação"""
        try:
            # Posições da tabela
            table_x = 130
            table_y = 260
            table_width = 540
            
            # Larguras das colunas
            col_widths = [135, 135, 180, 90]
            headers = ["Partida", "Acertos", "Total de Perguntas", "PoliCoins"]
            
            # Desenha cabeçalho
            current_x = table_x
            for header, width in zip(headers, col_widths):
                header_surface = self.font_table_header.render(header, True, self.TEXT_BLACK)
                text_x = current_x + (width - header_surface.get_width()) // 2
                self.screen.blit(header_surface, (text_x, table_y))
                current_x += width
            
            # Linha horizontal do cabeçalho
            pygame.draw.line(self.screen, self.LINE_COLOR, 
                            (table_x, table_y + 35), 
                            (table_x + table_width, table_y + 35), 2)
            
            # Linhas verticais
            current_x = table_x
            for i in range(5):
                pygame.draw.line(self.screen, self.LINE_COLOR, 
                                (current_x, table_y), 
                                (current_x, table_y + 160), 2)
                if i < 4:
                    current_x += col_widths[i]
                    
            # Linhas horizontais para dados (vazias por enquanto)
            for i in range(1, 6):
                y_pos = table_y + 35 + i * 25
                pygame.draw.line(self.screen, self.LINE_COLOR, 
                                (table_x, y_pos), 
                                (table_x + table_width, y_pos), 1)
                                
        except Exception as e:
            print(f"[ERRO] Erro ao desenhar tabela: {e}")

    def handle_events(self):
        """Gerencia eventos"""
        try:
            for event in pygame.event.get():
                if event.type == QUIT:
                    print("[DEBUG] Evento QUIT detectado")
                    self.running = False
                    return "quit"
                
                if event.type == MOUSEBUTTONDOWN:
                    if self.home_button.is_clicked(event.pos):
                        print("[DEBUG] Botão HOME clicado")
                        self.running = False
                        return "menu"
                    
                    if self.settings_button.is_clicked(event.pos):
                        print("[DEBUG] Botão SETTINGS clicado")
                        return "settings"
                
                if event.type == MOUSEBUTTONUP:
                    self.home_button.pressed = False
                    self.settings_button.pressed = False
                
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        print("[DEBUG] ESC pressionado")
                        self.running = False
                        return "menu"
        except Exception as e:
            print(f"[ERRO] Erro ao processar eventos: {e}")
        
        return None

    def draw(self):
        """Desenha todos os elementos na tela"""
        try:
            # Fundo
            self._draw_background()
            
            # Logo
            self._draw_logo()
            
            # Título
            title_rect = self.title_text.get_rect(center=(400, 90))
            self.screen.blit(self.title_text, title_rect)
            
            # Tabela
            self._draw_table()
            
            # Botões
            self.home_button.draw(self.screen)
            self.settings_button.draw(self.screen)

            # Atualiza a tela
            pygame.display.flip()
        except Exception as e:
            print(f"[ERRO] Erro ao desenhar tela: {e}")

    def run(self):
        """Loop principal"""
        print("[DEBUG] Iniciando loop principal...")
        
        try:
            while self.running:
                result = self.handle_events()
                if result:
                    print(f"[DEBUG] Retornando: {result}")
                    return result
                
                self.draw()
                self.clock.tick(60)
                
            print("[DEBUG] Loop encerrado normalmente")
            return "menu"
            
        except Exception as e:
            print(f"[ERRO] Erro no loop principal: {e}")
            import traceback
            traceback.print_exc()
            return "error"
        finally:
            pygame.quit()
            print("[DEBUG] Pygame finalizado")

# Teste principal
if __name__ == "__main__":
    print("="*50)
    print("INICIANDO TESTE DA TELA DE PONTUAÇÃO")
    print("="*50)
    
    try:
        # Testa se pygame está instalado
        import pygame
        print(f"[INFO] Pygame versão: {pygame.version.ver}")
        
        # Cria e executa a tela
        print("[INFO] Criando ScoreScreen...")
        score_screen = ScoreScreen(player_id=1)
        
        print("[INFO] Executando tela...")
        result = score_screen.run()
        
        print(f"[INFO] Tela encerrada com resultado: {result}")
        
    except ImportError:
        print("[ERRO] Pygame não está instalado!")
        print("Execute: pip install pygame")
        
    except Exception as e:
        print(f"[ERRO] Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        print("="*50)
        print("TESTE FINALIZADO")
        print("="*50)