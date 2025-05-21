from databse.db_connector import conn 

def verificar_login(usuario_ra, senha, tipo_usuario):
    if not conn:
        print("Erro na conexão com o banco de dados.")
        return False

    cursor = conn.cursor()

    if tipo_usuario == "student":
        query = "SELECT * FROM alunos WHERE aluno_RA = %s AND senha_aluno = %s"
    else:  # tipo_usuario == "teacher"
        query = "SELECT * FROM professores WHERE email_prof = %s AND senha_prof = %s"

    cursor.execute(query, (usuario_ra, senha))
    resultado = cursor.fetchone()
    conn.close()

    return resultado is not None