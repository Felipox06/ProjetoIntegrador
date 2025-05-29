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
            
            if result.get("action") == "login_success":
                # 1. Obtenha o dicionário INTERNO com os dados do usuário
                dados_do_login_bem_sucedido = result.get("user_data")

                if dados_do_login_bem_sucedido:
                    # 2. AGORA, ATUALIZE a variável 'user_data' do escopo da função main()
                    #    Esta 'user_data' será passada para a MenuScreen e outras telas.
                    #    A MenuScreen espera as chaves "user_type" e "username".
                    #    Os dados do login vêm com "tipo" e "nome". Precisamos mapeá-los.
                    user_data = {
                        "RA": dados_do_login_bem_sucedido.get("RA"),
                        "username": dados_do_login_bem_sucedido.get("nome"),  # Mapeia 'nome' para 'username'
                        "user_type": dados_do_login_bem_sucedido.get("tipo"), # Mapeia 'tipo' para 'user_type'
                        # Adicione outros campos de dados_do_login_bem_sucedido que você queira
                        # que fiquem disponíveis em user_data para outras telas.
                        # Ex: "turma": dados_do_login_bem_sucedido.get("turma") se for aluno
                        #     "materia": dados_do_login_bem_sucedido.get("materia") se for professor
                    }
                    
                    # Se a MenuScreen e outras telas forem adaptadas para usar "RA", "nome", "tipo" diretamente,
                    # você poderia simplesmente fazer:
                    # user_data = dados_do_login_bem_sucedido
                    
                    print(f"Login bem-sucedido! Usuário: {user_data.get('username')}, Tipo: {user_data.get('user_type')}")
                    next_screen = "menu" 
                else:
                    print("Erro: Login retornou sucesso, mas dados do usuário não encontrados.")
                    next_screen = "login" # Ou tratar como um erro mais sério
            
            elif result.get("action") == "login_failed":
                # A tela de login já deve ter definido uma mensagem de erro interna (self.error_message)
                # Aqui, apenas garantimos que o jogo não avance.
                print("Tentativa de login falhou. Permanecendo na tela de login.")
                # Não mudar next_screen, ou explicitamente:
                # next_screen = "login" 
                pass # Permanece no loop, a tela de login será redesenhada com a mensagem de erro dela

            else: # Outras ações como fechar a janela do LoginScreen
                action_returned = result.get("action", "desconhecida")
                print(f"Ação da tela de login: '{action_returned}'. Encerrando ou tratando.")
                if action_returned == "exit" or action_returned is None: # Exemplo
                     running = False
                # Se não for uma ação de saída conhecida, pode ser um bug ou você pode querer voltar ao login
                # else:
                #     next_screen = "login"

        elif next_screen == "menu":
            # Agora, 'user_data' que é passado para MenuScreen conterá o dicionário
            # com as chaves "username" e "user_type" como a MenuScreen espera.
            if user_data: # Garante que user_data não é None antes de ir para o menu
                current_screen = MenuScreen(screen, user_data) 
                result = current_screen.run()
                
                # Processar o resultado da MenuScreen. Atenção aqui também:
                # Se MenuScreen espera user_data['user_type'], e você está usando user_data['tipo']
                # no 'user_data' global, você precisará ser consistente.
                # No código acima, eu fiz user_data ter 'user_type' e 'username'
                # para ser compatível com o que MenuScreen espera.
                if result.get("action") == "play_game":
                    next_screen = "game_config"
                elif result.get("action") == "show_ranking" and user_data.get("user_type") == "teacher": # Usando .get()
                    print("Mostrando ranking...")
                    next_screen = "ranking_screen" 
                # ... continue adaptando as verificações em main.py para usar as chaves corretas ...
                elif result.get("action") == "logout":
                    user_data = None # Limpa os dados do usuário ao fazer logout
                    next_screen = "login"
                else: # Ação desconhecida ou para sair
                    running = False
            else:
                # Se user_data for None (ex: login falhou e não foi tratado para sair), volta ao login
                print("Tentando acessar o menu sem usuário logado. Redirecionando para login.")
                next_screen = "login"
                
        elif next_screen == "menu":
            current_screen = MenuScreen(screen, user_data)
            result = current_screen.run()
            
            if result["action"] == "play_game":
                next_screen = "game_config"
            elif result["action"] == "show_ranking" and user_data["user_type"] == "teacher":
                print("Mostrando ranking...")
                next_screen = "ranking_screen" 
            elif result["action"] == "manage_users" and user_data["user_type"] == "teacher":
                print("Gerenciando alunos...")
                next_screen = "manage_users"
            elif result["action"] == "manage_questions" and user_data["user_type"] == "teacher":
                print("Mudando para tela de gerenciamento de perguntas")
                next_screen = "question_management"
            elif result["action"] == "show_history" and user_data["user_type"] == "student":
                print("Mostrando histórico de jogos...")
                next_screen = "game_history"
            elif result["action"] == "manage_classes" and user_data["user_type"] == "teacher":
              print("Mudando para tela de gerenciamento de turmas")
              next_screen = "class_management"
            elif result["action"] == "logout":
                next_screen = "login"
                user_data = None
            else:
                running = False
                
        elif next_screen == "manage_users":
         current_screen = UserManagementScreen(screen, user_data)
         result = current_screen.run()
    
         if result["action"] == "add_users":
               next_screen = "add_users"
         elif result["action"] == "edit_users":
             next_screen = "edit_users"
         elif result["action"] == "remove_users":
              next_screen = "remove_users"
         elif result["action"] == "back_to_menu":
              next_screen = "menu"
         elif result["action"] == "exit":
                running = False

        elif next_screen == "remove_users":
          print("Carregando tela de remover usuários...")
          current_screen = RemoveUserScreen(screen, user_data)
          result = current_screen.run()

          if result["action"] == "back_to_user_management":
            next_screen = "manage_users"
          elif result["action"] == "exit":
            running = False

        elif next_screen == "edit_users":
         print("Carregando tela de editar usuários...")
         current_screen = EditUserScreen(screen, user_data)
         result = current_screen.run()

         if result["action"] == "back_to_user_management":
            next_screen = "manage_users"
         elif result["action"] == "exit":
            running = False

        elif next_screen == "add_users":
           current_screen = AddUserScreen(screen, user_data)
           result = current_screen.run()

           if result["action"] == "back_to_user_management":
              next_screen = "manage_users"
           elif result["action"] == "exit":
              running = False
        
        elif next_screen == "class_management":
            current_screen = ClassManagementScreen(screen, user_data)
            result = current_screen.run()
    
            if result["action"] == "create_class":
                print("Criando nova turma...")
                next_screen = "create_class"  # Precisaremos implementar esta tela depois
            elif result["action"] == "edit_class":
                print("Editando turma existente...")
                next_screen = "edit_class"    # Precisaremos implementar esta tela depois
            elif result["action"] == "remove_class":
             print("Removendo turma...")
             next_screen = "remove_class"  # Precisaremos implementar esta tela depois
            elif result["action"] == "back_to_menu":
                next_screen = "menu"
            else:
                running = False
        elif next_screen == "create_class":
         current_screen = ClassCreateScreen(screen, user_data)
         result = current_screen.run()
    
         if result["action"] == "class_saved" or result["action"] == "back_to_menu":
              next_screen = "class_management"
         else:
            running = False

        elif next_screen == "edit_class":
         current_screen = ClassEditScreen(screen, user_data)
         result = current_screen.run()
    
         if result["action"] == "back_to_menu":
           next_screen = "class_management"
         else:
           running = False

        elif next_screen == "remove_class":
           current_screen = ClassRemoveScreen(screen, user_data)
           result = current_screen.run()
    
           if result["action"] == "back_to_menu":
                next_screen = "class_management"
           else:
                running = False
                
                
        elif next_screen == "ranking_screen":
          current_screen = RankingScreen(screen, user_data)
          result = current_screen.run()
    
          if result["action"] == "back_to_menu":
             next_screen = "menu"
          else:
             running = False

        elif next_screen == "question_management":
          current_screen = QuestionManagementScreen(screen, user_data)
          result = current_screen.run()
        
          if result["action"] == "create_question":
              next_screen = "question_creator"  # Usa o editor existente para criação
          elif result["action"] == "edit_question":
              next_screen = "question_edit"  # Precisaria criar essa tela
          elif result["action"] == "remove_question":
              next_screen = "question_remove"  # Precisaria criar essa tela
          elif result["action"] == "back_to_menu":
              next_screen = "menu"
          else:
              running = False

        elif next_screen == "question_creator":
        # Cria uma nova instância do editor
          current_screen = QuestionEditor(screen, user_data)
          result = current_screen.run()
    
          if result["action"] == "question_saved" or result["action"] == "back_to_menu":
         # Após salvar ou cancelar, volta para a tela de gerenciamento
             next_screen = "question_management"
          else:
             running = False


        elif next_screen == "question_edit":
          current_screen = QuestionEditScreen(screen, user_data)
          result = current_screen.run()
    
          if result["action"] == "edit_selected_question":
           # Abrir o editor com a questão selecionada para edição
           question_to_edit = result["question"]
           current_screen = QuestionEditor(screen, user_data, question_to_edit)
           result = current_screen.run()
           # Voltar para a tela de edição após salvar/cancelar
           next_screen = "question_edit"
          elif result["action"] == "back_to_menu":
           next_screen = "question_management"
          else:
            running = False

        elif next_screen == "question_remove":
          current_screen = QuestionRemoveScreen(screen, user_data)
          result = current_screen.run()
    
          if result["action"] == "back_to_menu":
           next_screen = "question_management"
          else:
           running = False
     
        elif next_screen == "game_history":
            current_screen = GameHistoryScreen(screen, user_data)  
            result = current_screen.run()      

            if result["action"] == "back_to_menu":
               next_screen = "menu"
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

    # Encerrar o pygame
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()