from databse.db_connector import conn 
from random import shuffle
from models.question import Question
# Função para Verificação do login
def verificar_login(usuario_ra, senha, tipo_usuario):
    if not conn:
        print("Erro na conexão com o banco de dados.")
        return False

    cursor = conn.cursor()

    if tipo_usuario == "student":
        query = "SELECT * FROM alunos WHERE aluno_RA = %s AND senha_aluno = %s"
    else:
        query = "SELECT * FROM professores WHERE email_prof = %s AND senha_prof = %s"

    cursor.execute(query, (usuario_ra, senha))
    resultado = cursor.fetchone()
    conn.close()

    return resultado is not None


# Função para Buscar o id da matéria no banco de dados
def get_id_materia_by_nome(nome_materia):
    if not conn:
        print("Erro na conexão com o banco de dados.")
        return None

    cursor = conn.cursor()
    cursor.execute("SELECT id_materia FROM materias WHERE nome_materia = %s", (nome_materia,))
    resultado = cursor.fetchone()
    conn.close()

    if resultado:
        return resultado[0]
    return None


# Função para Buscar questões para o quiz
def get_questions_from_db(id_materia: int, total=15):
    if not conn:
        print("Erro na conexão com o banco de dados.")
        return []

    cursor = conn.cursor(dictionary=True)

    # Define número por dificuldade
    distrib = {"fácil": 5, "média": 5, "difícil": 5}
    all_questions = []

    for dificuldade, qtd in distrib.items():
        query = """
        SELECT q.id_questao, q.enunciado_questao, q.dicas, d.nome_dificuldade
        FROM questoes q
        JOIN dificuldades d ON q.id_dificuldade = d.id_dificuldade
        WHERE d.nome_dificuldade = %s AND q.id_materia = %s
        ORDER BY RAND()
        LIMIT %s
        """
        cursor.execute(query, (dificuldade, id_materia, qtd))
        questoes = cursor.fetchall()

        for q in questoes:
            # Busca alternativas da questão
            cursor.execute("""
                SELECT letra, texto_alt, correta
                FROM alternativas
                WHERE id_questao = %s
                ORDER BY letra ASC
            """, (q["id_questao"],))
            alternativas = cursor.fetchall()

            options = [alt["texto_alt"] for alt in alternativas]
            correct_index = next(
                (i for i, alt in enumerate(alternativas) if alt["correta"]), None
            )

            if correct_index is None or len(options) < 4:
                continue  # Pula se não for uma pergunta válida

            all_questions.append(
                Question(
                    text=q["enunciado_questao"],
                    options=options,
                    correct_option=correct_index,
                    difficulty=dificuldade,
                )
            )

    shuffle(all_questions)
    conn.close()
    return all_questions[:total]