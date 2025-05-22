import pygame
import csv
import os

class UpdateScreen:
    def __init__(self, screen):
        print("Iniciando UpdateScreen...")
        self.screen = screen
        self.running = True
        self.clock = pygame.time.Clock()

        # Cores
        self.LARANJA = (255, 153, 51)
        self.AZUL_CLARO = (0, 180, 200)
        self.PRETO = (0, 0, 0)
        self.BRANCO = (255, 255, 255)

        # Fontes
        self.fonte = pygame.font.SysFont('Courier New', 22)
        self.fonte_titulo = pygame.font.SysFont('Courier New', 36, bold=True)

        # Inputs
        self.inputs = [
            self.InputBox(100, 155, 160, 30),
            self.InputBox(270, 155, 120, 30),
            self.InputBox(400, 155, 120, 30),
            self.InputBox(530, 155, 120, 30),
            self.InputBox(660, 155, 90, 30)
        ]

        # Botões
        self.botao_atualizar = self.Botao(130, 380, 200, 40, 'Atualizar', self.atualizar)
        self.botao_cancelar = self.Botao(430, 380, 200, 40, 'Cancelar', self.cancelar)
        self.botao_sair = self.Botao(800 - 100, 20, 80, 30, 'Sair', self.voltar_menu)

        self.result = {"action": None}

    def atualizar(self):
        dados = [box.texto for box in self.inputs]
        if all(dados):
            # Carregar os dados do arquivo CSV
            if os.path.isfile("usuarios.csv"):
                with open("usuarios.csv", "r", newline='', encoding='utf-8') as f:
                    linhas = list(csv.reader(f))
                
                header = linhas[0]
                ra = dados[1]  # Vamos usar o RA para buscar o usuário a ser atualizado

                # Encontrar o índice da linha a ser atualizada
                linha_atualizada = False
                for i, linha in enumerate(linhas[1:], start=1):  # Começa em 1 para pular o cabeçalho
                    if linha[1] == ra:  # Verifica se o RA corresponde
                        linhas[i] = dados  # Atualiza a linha com os novos dados
                        linha_atualizada = True
                        break

                if linha_atualizada:
                    # Reescrever o arquivo com os dados atualizados
                    with open("usuarios.csv", "w", newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerows(linhas)
                    print("Dados atualizados com sucesso!")
                else:
                    print("Usuário com RA não encontrado para atualização.")

                # Limpar campos após atualizar
                for box in self.inputs:
                    box.texto = ''
                    box.txt_surface = self.fonte.render('', True, self.PRETO)
            else:
                print("Arquivo de usuários não encontrado!")
        else:
            print("Preencha todos os campos!")

    def cancelar(self):
        for box in self.inputs:
            box.texto = ''
            box.txt_surface = self.fonte.render('', True, self.PRETO)
        print("Atualização cancelada.")
        self.result["action"] = "back_to_menu"
        self.running = False

    def voltar_menu(self):
        print("Voltando para o menu principal...")
        self.result["action"] = "back_to_menu"
        self.running = False

    class InputBox:
        def __init__(self, x, y, w, h, texto=''):
            self.rect = pygame.Rect(x, y, w, h)
            self.texto = texto
            self.color = (255, 255, 255)
            self.txt_surface = pygame.font.SysFont('Courier New', 22).render(texto, True, (0, 0, 0))
            self.ativo = False

        def handle_event(self, evento):
            if evento.type == pygame.MOUSEBUTTONDOWN:
                self.ativo = self.rect.collidepoint(evento.pos)
            if evento.type == pygame.KEYDOWN and self.ativo:
                if evento.key == pygame.K_RETURN:
                    self.ativo = False
                elif evento.key == pygame.K_BACKSPACE:
                    self.texto = self.texto[:-1]
                else:
                    self.texto += evento.unicode
                self.txt_surface = pygame.font.SysFont('Courier New', 22).render(self.texto, True, (0, 0, 0))

        def draw(self, tela):
            pygame.draw.rect(tela, (255, 255, 255), self.rect)
            pygame.draw.rect(tela, (0, 0, 0), self.rect, 2)
            tela.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))

    class Botao:
        def __init__(self, x, y, w, h, texto, callback):
            self.rect = pygame.Rect(x, y, w, h)
            self.texto = texto
            self.callback = callback
            self.fonte = pygame.font.SysFont('Courier New', 22)

        def draw(self, tela):
            sombra_offset = 4
            pygame.draw.rect(tela, (0, 0, 0), self.rect.move(sombra_offset, sombra_offset))
            pygame.draw.rect(tela, (0, 180, 200), self.rect)
            texto_surface = self.fonte.render(self.texto, True, (0, 0, 0))
            tela.blit(texto_surface, (self.rect.centerx - texto_surface.get_width() // 2,
                                      self.rect.centery - texto_surface.get_height() // 2))

        def handle_event(self, evento):
            if evento.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(evento.pos):
                self.callback()

    def run(self):
        print("Executando UpdateScreen.run()...")
        while self.running:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.voltar_menu()
                for box in self.inputs:
                    box.handle_event(evento)
                self.botao_atualizar.handle_event(evento)
                self.botao_cancelar.handle_event(evento)
                self.botao_sair.handle_event(evento)

            self.screen.fill(self.BRANCO)
            pygame.draw.rect(self.screen, self.AZUL_CLARO, (10, 10, 780, 480), 20, border_radius=60)
            pygame.draw.rect(self.screen, self.LARANJA, (30, 30, 740, 440), 0, border_radius=40)

            titulo = self.fonte_titulo.render("Atualizar Usuário", True, self.PRETO)
            self.screen.blit(titulo, (800 // 2 - titulo.get_width() // 2, 60))

            colunas = ["Nome do Aluno", "RA", "Senha", "Ano", "Turma"]
            colunas_x = [90, 270, 400, 530, 660]
            for i, col in enumerate(colunas):
                texto = self.fonte.render(col, True, self.PRETO)
                self.screen.blit(texto, (colunas_x[i], 120))

            for box in self.inputs:
                box.draw(self.screen)

            self.botao_atualizar.draw(self.screen)
            self.botao_cancelar.draw(self.screen)
            self.botao_sair.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(30)

        return self.result

# Apenas para teste direto deste arquivo
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800, 500))
    update_screen = UpdateScreen(screen)
    result = update_screen.run()
    print(result)
    pygame.quit()