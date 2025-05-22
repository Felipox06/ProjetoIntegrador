from databse.db_connector import getConnection
from random import shuffle
from models.question import Question
# Função para verificação do login
def verificar_login(usuario_ra, senha, tipo_usuario):
    conn = getConnection()
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

# Função para pegar o iD da série
def get_id_serie_by_nome(nome_serie):
    conn = getConnection()
    cursor = conn.cursor()
    # Ajuste esta query para sua tabela de séries (ex: 'series') e colunas (ex: 'id_serie', 'nome_serie')
    cursor.execute(
        "SELECT id_serie FROM series WHERE LOWER(nome_serie) = LOWER(%s)", 
        (nome_serie,)
    )
    resultado = cursor.fetchone()
    conn.close()
    if resultado:
        return resultado[0]
    print(f"❌ Série '{nome_serie}' não encontrada no banco.")
    return None

# Função para pegar o id da dificuldade
def get_id_dificuldade_by_nome(nome_dificuldade):
    conn = getConnection()
    cursor = conn.cursor()
    # Ajuste esta query para sua tabela de dificuldades e colunas
    cursor.execute(
        "SELECT id_dificuldade FROM dificuldades WHERE LOWER(nome_dificuldade) = LOWER(%s)", 
        (nome_dificuldade,)
    )
    resultado = cursor.fetchone()
    conn.close()
    if resultado:
        return resultado[0]
    print(f"❌ Dificuldade '{nome_dificuldade}' não encontrada no banco.")
    return None

# Função para Buscar o id da matéria no banco de dados
def get_id_materia_by_nome(nome_materia):
    conn = getConnection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id_materia FROM materias WHERE LOWER(nome_materia) = LOWER(%s)",
        (nome_materia,)
    )
    resultado = cursor.fetchone()
    conn.close()
    if resultado:
        return resultado[0]
    print(f"❌ Matéria '{nome_materia}' não encontrada no banco.")
    return None


# Função para Buscar questões para o quiz
def get_questions_from_db(id_materia: int, id_dificuldade: int, id_serie:int, total=15):
    conn = getConnection()
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
        WHERE d.nome_dificuldade = %s AND q.id_materia = %s AND q.id_serie = %s
        ORDER BY RAND()
        LIMIT %s
        """
        cursor.execute(query, (dificuldade, id_materia, id_serie, qtd))
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
                    hint=q["dicas"]
                )
            )

    shuffle(all_questions)
    conn.close()
    return all_questions[:total]