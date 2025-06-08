import pygame
import sys
import os
from pygame.locals import *
from databse.data_manager import record_game_session
from databse.db_connector import getConnection

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
    "accent": (27, 185, 185),
    "text": (60, 60, 60),
    "success": (75, 181, 67),
    "warning": (251, 164, 31),
    "error": (232, 77, 77),
    "black": (0, 0, 0),
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
    from screens.teacher.remove_user_screen import RemoveUserScreen
    from screens.teacher.edit_user_screen import EditUserScreen
    from screens.teacher.add_user_screen import AddUserScreen
    from screens.teacher.user_management_screen import UserManagementScreen
    from screens.teacher.class_create_screen import ClassCreateScreen
    from screens.teacher.class_edit_screen import ClassEditScreen
    from screens.teacher.class_remove_screen import ClassRemoveScreen
    from screens.teacher.class_management_screen import ClassManagementScreen
    from screens.teacher.ranking_screen import RankingScreen
    from screens.teacher.question_edit_screen import QuestionEditScreen
    from screens.teacher.question_remove_screen import QuestionRemoveScreen
    from screens.teacher.question_management_screen import QuestionManagementScreen
    from screens.student.game_history import GameHistoryScreen
    from screens.teacher.question_creator import QuestionEditor
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
    user_data = None      # Esta variável guardará os dados do usuário logado
    game_config = None
    
    # O dicionário 'student_data' simulado não é mais necessário aqui
    
    # Loop principal
    running = True
    while running:
        if next_screen == "login":
            current_screen = LoginScreen(screen)
            result = current_screen.run()
            if result.get("action") == "login_success":
                dados_do_login = result.get("user_data")

                if dados_do_login:
                    user_data = {
                        "RA": dados_do_login.get("RA"),
                        "username": dados_do_login.get("nome"),
                        "user_type": dados_do_login.get("tipo"),
                    }
                    
                    print(f"Login bem-sucedido! Usuário: {user_data.get('username')}, Tipo: {user_data.get('user_type')}")
                    next_screen = "menu"
                else:
                    print("Erro: Login retornou sucesso, mas dados do usuário ausentes.")       
            elif result.get("action") == "login_failed":
                print("Tentativa de login falhou. Permanecendo na tela de login.")
                pass
            
            else: 
                print(f"Ação da tela de login não foi 'login_success' ou 'login_failed': {result.get('action')}. Encerrando.")
                running = False
                
        elif next_screen == "menu":
            if not user_data:
                print("ERRO: Tentando acessar menu sem usuário logado. Voltando para login.")
                next_screen = "login"
                continue

            # Agora user_data é o dicionário correto e é passado para a MenuScreen
            current_screen = MenuScreen(screen, user_data)
            result = current_screen.run()
            
            # Usar .get() aqui é mais seguro e evita que o jogo quebre
            if result.get("action") == "play_game":
                next_screen = "game_config"
            elif result.get("action") == "show_ranking" and user_data.get("user_type") == "teacher":
                print("Mostrando ranking...")
                next_screen = "ranking_screen" 
            elif result.get("action") == "manage_users" and user_data.get("user_type") == "teacher":
                print("Gerenciando alunos...")
                next_screen = "manage_users"
            elif result.get("action") == "manage_questions" and user_data.get("user_type") == "teacher":
                print("Mudando para tela de gerenciamento de perguntas")
                next_screen = "question_management"
            elif result.get("action") == "show_history" and user_data.get("user_type") == "student":
                print("Mostrando histórico de jogos...")
                next_screen = "game_history"
            elif result.get("action") == "manage_classes" and user_data.get("user_type") == "teacher":
                print("Mudando para tela de gerenciamento de turmas")
                next_screen = "class_management"
            elif result.get("action") == "logout":
                next_screen = "login"
                user_data = None # Limpa os dados do usuário ao fazer logout
            else:
                running = False
                
        elif next_screen == "manage_users":
            current_screen = UserManagementScreen(screen, user_data)
            result = current_screen.run()
    
            if result.get("action") == "add_users":
                next_screen = "add_users"
            elif result.get("action") == "edit_users":
                next_screen = "edit_users"
            elif result.get("action") == "remove_users":
                next_screen = "remove_users"
            elif result.get("action") == "back_to_menu":
                next_screen = "menu"
            elif result.get("action") == "exit":
                running = False

        elif next_screen == "remove_users":
            print("Carregando tela de remover usuários...")
            current_screen = RemoveUserScreen(screen, user_data)
            result = current_screen.run()

            if result.get("action") == "back_to_user_management":
                next_screen = "manage_users"
            elif result.get("action") == "exit":
                running = False

        elif next_screen == "edit_users":
            print("Carregando tela de editar usuários...")
            current_screen = EditUserScreen(screen, user_data)
            result = current_screen.run()

            if result.get("action") == "back_to_user_management":
                next_screen = "manage_users"
            elif result.get("action") == "exit":
                running = False

        elif next_screen == "add_users":
            current_screen = AddUserScreen(screen, user_data)
            result = current_screen.run()

            if result.get("action") == "back_to_user_management":
                next_screen = "manage_users"
            elif result.get("action") == "exit":
                running = False
        
        elif next_screen == "class_management":
            current_screen = ClassManagementScreen(screen, user_data)
            result = current_screen.run()
    
            if result.get("action") == "create_class":
                print("Criando nova turma...")
                next_screen = "create_class"
            elif result.get("action") == "edit_class":
                print("Editando turma existente...")
                next_screen = "edit_class"
            elif result.get("action") == "remove_class":
                print("Removendo turma...")
                next_screen = "remove_class"
            elif result.get("action") == "back_to_menu":
                next_screen = "menu"
            else:
                running = False
        
        elif next_screen == "create_class":
            current_screen = ClassCreateScreen(screen, user_data)
            result = current_screen.run()
    
            if result.get("action") == "class_saved" or result.get("action") == "back_to_menu":
                next_screen = "class_management"
            else:
                running = False

        elif next_screen == "edit_class":
            current_screen = ClassEditScreen(screen, user_data)
            result = current_screen.run()
    
            if result.get("action") == "back_to_menu":
                next_screen = "class_management"
            else:
                running = False

        elif next_screen == "remove_class":
            current_screen = ClassRemoveScreen(screen, user_data)
            result = current_screen.run()
    
            if result.get("action") == "back_to_menu":
                next_screen = "class_management"
            else:
                running = False
        
        elif next_screen == "ranking_screen":
            current_screen = RankingScreen(screen, user_data)
            result = current_screen.run()
    
            if result.get("action") == "back_to_menu":
                next_screen = "menu"
            else:
                running = False

        elif next_screen == "question_management":
            current_screen = QuestionManagementScreen(screen, user_data)
            result = current_screen.run()
        
            if result.get("action") == "create_question":
                next_screen = "question_creator"
            elif result.get("action") == "edit_question":
                next_screen = "question_edit"
            elif result.get("action") == "remove_question":
                next_screen = "question_remove"
            elif result.get("action") == "back_to_menu":
                next_screen = "menu"
            else:
                running = False

        elif next_screen == "question_creator":
            current_screen = QuestionEditor(screen, user_data)
            result = current_screen.run()
    
            if result.get("action") == "question_saved" or result.get("action") == "back_to_menu":
                next_screen = "question_management"
            else:
                running = False

        elif next_screen == "question_edit":
            current_screen = QuestionEditScreen(screen, user_data)
            result = current_screen.run()
    
            if result.get("action") == "edit_selected_question":
                question_to_edit = result["question"]
                current_screen = QuestionEditor(screen, user_data, question_to_edit)
                result = current_screen.run()
                next_screen = "question_edit"
            elif result.get("action") == "back_to_menu":
                next_screen = "question_management"
            else:
                running = False

        elif next_screen == "question_remove":
            current_screen = QuestionRemoveScreen(screen, user_data)
            result = current_screen.run()
    
            if result.get("action") == "back_to_menu":
                next_screen = "question_management"
            else:
                running = False
        
        elif next_screen == "game_history":
            current_screen = GameHistoryScreen(screen, user_data)  
            result = current_screen.run()      

            if result.get("action") == "back_to_menu":
                next_screen = "menu"
            else:
                running = False

        elif next_screen == "game_config":
            current_screen = GameConfigScreen(screen, user_data)
            result = current_screen.run()
            
            if result.get("action") == "start_game":
                game_config = result.get("game_settings")
                if game_config:
                    next_screen = "quiz"
                else:
                    print("Falha ao obter configurações do jogo. Permanecendo na tela.")
            elif result.get("action") == "back_to_menu":
                next_screen = "menu"
            else:
                running = False
                
        elif next_screen == "quiz":
            if not (user_data and game_config):
                print("ERRO CRÍTICO (main.py): Tentando iniciar quiz sem user_data ou game_config.")
                next_screen = "login"
                continue

            current_screen = QuizScreen(screen, user_data, game_config)
            result = current_screen.run()

            print("\n--- DEBUG: FIM DO QUIZ ---")
            print(f"Resultado retornado pela QuizScreen: {result}")
            print(f"Dados do usuário no momento: {user_data}")
            if user_data:
                print(f"Tipo do usuário: '{user_data.get('user_type')}'")
            print("--------------------------\n")
            
            if result.get("action") == "back_to_menu":
                if "money_earned" in result and user_data.get("user_type") == "student":
                    
                    # 1. Coleta todos os dados necessários para salvar a sessão do jogo
                    player_ra = user_data.get("RA")
                    score_this_game = result.get("money_earned")
                    materia_id = game_config.get("subject_id")
                    serie_id = game_config.get("grade_id")
                    
                    print(f"Jogo finalizado! Pontuação obtida: R$ {score_this_game:,}. Registrando no banco de dados...")

                    # 2. Verifica se todos os dados necessários existem antes de chamar o banco
                    if all([player_ra, materia_id is not None, serie_id is not None, score_this_game is not None]):
                        try:
                            # 3. Chama a função do data_manager para salvar o resultado
                            was_successful, message = record_game_session(
                                player_ra=player_ra,
                                game_materia_id=materia_id,
                                game_serie_id=serie_id,
                                game_score=score_this_game,
                                connection=getConnection # Passa a função de conexão
                            )

                            if was_successful:
                                print(f"DB: {message}")
                            else:
                                print(f"ERRO AO SALVAR O JOGO NO BANCO: {message}")
                        except Exception as e:
                            print(f"ERRO INESPERADO ao tentar salvar o jogo: {e}")
                    else:
                        # Este print ajuda a diagnosticar se algum dado está faltando
                        print("AVISO: Faltam dados para registrar a sessão do jogo no banco.")
                        print(f"  RA: {player_ra}, Matéria ID: {materia_id}, Série ID: {serie_id}, Score: {score_this_game}")

                next_screen = "menu"
            else:
                running = False


    # Encerrar o pygame
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()