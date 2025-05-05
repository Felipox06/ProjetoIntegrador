# main.py
# -*- coding: utf-8 -*-

import pygame
import sys
import os
from pygame.locals import *

# Verificar existência de pastas essenciais
if not os.path.exists("screens"):
    os.makedirs("screens")

# Configurações básicas
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Cores no formato RGB
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

# Definições para o jogo
SUBJECTS = [
    "Matematica", 
    "Fisica", 
    "Biologia", 
    "Quimica", 
    "Historia", 
    "Geografia", 
    "Portugues"
]

GRADE_LEVELS = ["1 Ano", "2 Ano", "3 Ano"]
DIFFICULTY_LEVELS = ["Facil", "Medio", "Dificil"]
CHECKPOINT_INTERVALS = 5
TOTAL_QUESTIONS = 15

# Atualizar o arquivo config.py com todas as configurações necessárias
with open("config.py", "w", encoding="utf-8") as f:
    f.write("# -*- coding: utf-8 -*-\n\n")  # Adiciona a declaração de codificação
    f.write(f"SCREEN_WIDTH = {SCREEN_WIDTH}\n")
    f.write(f"SCREEN_HEIGHT = {SCREEN_HEIGHT}\n\n")
    
    f.write("COLORS = {\n")
    for key, value in COLORS.items():
        f.write(f"    \"{key}\": {value},\n")
    f.write("}\n\n")
    
    f.write(f"# Configuracoes de jogo\n")
    f.write(f"CHECKPOINT_INTERVALS = {CHECKPOINT_INTERVALS}  # A cada 5 perguntas\n")
    f.write(f"TOTAL_QUESTIONS = {TOTAL_QUESTIONS}  # Total de 15 perguntas por jogo\n\n")
    
    f.write("# Niveis de dificuldade\n")
    f.write(f"DIFFICULTY_LEVELS = {DIFFICULTY_LEVELS}\n\n")
    
    f.write("# Series (anos escolares)\n")
    f.write(f"GRADE_LEVELS = {GRADE_LEVELS}\n\n")
    
    f.write("# Materias disponiveis\n")
    f.write("SUBJECTS = [\n")
    for subject in SUBJECTS:
        f.write(f"    \"{subject}\",\n")
    f.write("]\n")

print("Arquivo config.py criado com sucesso!")

# Importar as telas
try:
    from screens.teacher.question_editor import QuestionEditor
    from screens.login_screen import LoginScreen
    print("Login Screen importada com sucesso!")
    from screens.menu_screen import MenuScreen
    print("Menu Screen importada com sucesso!")
    from screens.game_config_screen import GameConfigScreen
    print("Game Config Screen importada com sucesso!")
    from screens.quiz_screen import QuizScreen
    print("Quiz Screen importada com sucesso!")
except Exception as e:
    print(f"Erro ao importar telas: {e}")
    sys.exit(1)

def main():
    # Inicializar o pygame
    pygame.init()
    
    # Configurar a janela
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Quiz do Milhao - Ensino Medio")
    
    # Controle de navegação entre telas
    current_screen = None
    next_screen = "login"
    user_data = None
    game_config = None
    
    # Dados do usuário simulados (para teste sem banco de dados)
    student_data = {
        "money": 0,
        "games_played": 0,
        "last_game_date": ""
    }
    
    # Loop principal
    running = True
    while running:
        if next_screen == "login":
            current_screen = LoginScreen(screen)
            result = current_screen.run()
            
            if result["action"] == "login_success":
                user_data = {
                    "user_type": result["user_type"],
                    "username": result["username"]
                }
                next_screen = "menu"
            else:
                running = False
                
        elif next_screen == "menu":
            current_screen = MenuScreen(screen, user_data)
            result = current_screen.run()
            
            if result["action"] == "play_game":
                next_screen = "game_config"
            elif result["action"] == "show_ranking":
                print("Mostrando ranking...")
                next_screen = "menu"  # Temporário: volta para o menu
            elif result["action"] == "show_profile":
                print("Mostrando perfil...")
                next_screen = "menu"  # Temporário: volta para o menu
            elif result["action"] == "manage_students" and user_data["user_type"] == "teacher":
                print("Gerenciando alunos...")
                next_screen = "menu"  # Temporário: volta para o menu
            elif result["action"] == "edit_questions" and user_data["user_type"] == "teacher":
                print("Mudando para tela de edição de perguntas")
                next_screen = "question_editor"
                question_editor = QuestionEditor(screen, user_data)
            elif result["action"] == "show_history" and user_data["user_type"] == "student":
                print("Mostrando histórico de jogos...")
                next_screen = "menu"  # Temporário: volta para o menu
            elif result["action"] == "logout":
                next_screen = "login"
                user_data = None
            else:
                running = False
                
        elif next_screen == "game_config":
            current_screen = GameConfigScreen(screen, user_data)
            result = current_screen.run()
            
            if result["action"] == "start_game":
                game_config = {
                    "subject": result["subject"],
                    "grade": result["grade"]
                }
                next_screen = "quiz"
            elif result["action"] == "back_to_menu":
                next_screen = "menu"
            else:
                running = False
                
        elif next_screen == "quiz":
            current_screen = QuizScreen(screen, user_data, game_config)
            result = current_screen.run()
            
            if result["action"] == "back_to_menu":
                # Atualizar dados do jogador com o dinheiro ganho (simulando banco de dados)
                if "money_earned" in result and user_data["user_type"] == "student":
                    student_data["money"] += result["money_earned"]
                    student_data["games_played"] += 1
                    
                    # Em um caso real, aqui seria feita a atualização no banco de dados MySQL
                    print(f"Jogo finalizado! Dinheiro ganho: R$ {result['money_earned']:,}")
                    print(f"Total de dinheiro acumulado: R$ {student_data['money']:,}")
                
                next_screen = "menu"
            else:
                running = False
        
        elif next_screen == "question_editor":
            result = question_editor.run()
        
            if result["action"] == "back_to_menu":
              print("Voltando para o menu a partir do editor de perguntas")
              next_screen = "menu"
              # Opcionalmente, pode mostrar uma mensagem de sucesso se a pergunta foi salva
            
            elif result["action"] == "question_saved":
                print("Questão salva")
            
        else:
           running = "False"
    # Encerrar o pygame
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()