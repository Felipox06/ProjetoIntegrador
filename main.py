import pygame
import sys
import os
from pygame.locals import *

from screens.student.stats_screen import ScoreScreen
from screens.teacher.register_screen import RegisterScreen
from screens.teacher.question_editor import QuestionEditor
from screens.login_screen import LoginScreen
from screens.menu_screen import MenuScreen
from screens.game_config_screen import GameConfigScreen
from screens.quiz_screen import QuizScreen
from screens.teacher.manage_user_menu_screen import ManageUserMenuScreen
from screens.teacher.remove_user_screen import RemoveUserScreen
from screens.teacher.update_screen import UpdateScreen 
# Verificar existência de pastas essenciais
if not os.path.exists("screens"):
    os.makedirs("screens")

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

COLORS = {
    "background": (30, 180, 195),
    "light_shadow": (255, 255, 255),
    "dark_shadow": (20, 140, 150),
    "accent": (251, 164, 31),
    "text": (0, 0, 0),
    "black": (0, 0, 0),
    "success": (75, 181, 67),
    "warning": (232, 181, 12),
    "error": (232, 77, 77)
}

SUBJECTS = [
    "Matematica", "Fisica", "Biologia", "Quimica", 
    "Historia", "Geografia", "Portugues"
]
GRADE_LEVELS = ["1 Ano", "2 Ano", "3 Ano"]
DIFFICULTY_LEVELS = ["Facil", "Medio", "Dificil"]
CHECKPOINT_INTERVALS = 5
TOTAL_QUESTIONS = 15

with open("config.py", "w", encoding="utf-8") as f:
    f.write("# -*- coding: utf-8 -*-\n\n")
    f.write(f"SCREEN_WIDTH = {SCREEN_WIDTH}\n")
    f.write(f"SCREEN_HEIGHT = {SCREEN_HEIGHT}\n\n")
    f.write("COLORS = {\n")
    for key, value in COLORS.items():
        f.write(f"    \"{key}\": {value},\n")
    f.write("}\n\n")
    f.write("# Configuracoes de jogo\n")
    f.write(f"CHECKPOINT_INTERVALS = {CHECKPOINT_INTERVALS}\n")
    f.write(f"TOTAL_QUESTIONS = {TOTAL_QUESTIONS}\n\n")
    f.write("# Niveis de dificuldade\n")
    f.write(f"DIFFICULTY_LEVELS = {DIFFICULTY_LEVELS}\n\n")
    f.write("# Series (anos escolares)\n")
    f.write(f"GRADE_LEVELS = {GRADE_LEVELS}\n\n")
    f.write("# Materias disponiveis\n")
    f.write("SUBJECTS = [\n")
    for subject in SUBJECTS:
        f.write(f"    \"{subject}\",\n")
    f.write("]\n")

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Quiz do Milhao - Ensino Medio")

    current_screen = None
    next_screen = "login"
    user_data = None
    game_config = None

    student_data = {
        "money": 0,
        "games_played": 0,
        "last_game_date": ""
    }

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
                next_screen = "menu"
            elif result["action"] == "show_profile":
                next_screen = "menu"
            elif result["action"] == "manage_students" and user_data["user_type"] == "teacher":
                next_screen = "manage_user_menu"
            elif result["action"] == "edit_questions" and user_data["user_type"] == "teacher":
                next_screen = "question_editor"
                question_editor = QuestionEditor(screen, user_data)
            elif result["action"] == "show_history" and user_data["user_type"] == "student":
                next_screen = "menu"
            elif result["action"] == "show_score" and user_data["user_type"] == "student":
                next_screen = "score_screen"
            elif result["action"] == "logout":
                next_screen = "login"
                user_data = None
            else:
                running = False

        elif next_screen == "manage_user_menu":
            current_screen = ManageUserMenuScreen(screen)
            result = current_screen.run()

            if result["action"] == "add_user":
                next_screen = "register_screen"
            elif result["action"] == "remove_user":
                current_screen = RemoveUserScreen(screen)
                remove_result = current_screen.run()
                next_screen = "manage_user_menu" if remove_result["action"] == "back_to_menu" else "menu"
            elif result["action"] == "update_user":
                print("Abrindo tela de atualização de usuário...")
                current_screen = UpdateScreen(screen)
                update_result = current_screen.run()
                next_screen = "manage_user_menu" if update_result["action"] == "back_to_menu" else "menu"
            elif result["action"] == "back_to_menu":
                next_screen = "menu"
            else:
                running = False

        elif next_screen == "register_screen":
            current_screen = RegisterScreen(screen)
            result = current_screen.run()
            next_screen = "menu" if result["action"] == "back_to_menu" else None

        elif next_screen == "game_config":
            current_screen = GameConfigScreen(screen, user_data)
            result = current_screen.run()
            if result["action"] == "start_game":
                game_config = {
                    "subject": result["subject"],
                    "grade": result["grade"],
                    "difficulty": result["difficulty"]
                }
                next_screen = "quiz"
            elif result["action"] == "back_to_menu":
                next_screen = "menu"

        elif next_screen == "quiz":
            current_screen = QuizScreen(screen, user_data, game_config)
            result = current_screen.run()
            if result["action"] == "back_to_menu":
                if "money_earned" in result and user_data["user_type"] == "student":
                    student_data["money"] += result["money_earned"]
                    student_data["games_played"] += 1
                    print(f"Jogo finalizado! Dinheiro ganho: R$ {result['money_earned']:,}")
                    print(f"Total de dinheiro acumulado: R$ {student_data['money']:,}")
                next_screen = "menu"

        elif next_screen == "question_editor":
            result = question_editor.run()
            if result["action"] == "back_to_menu":
                next_screen = "menu"

        elif next_screen == "score_screen":
            current_screen = ScoreScreen(player_id=1, game_results={"score": 100})
            result = current_screen.run()
            next_screen = "menu" if result == "menu" else None

        else:
            running = False

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
