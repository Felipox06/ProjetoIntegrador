from databse.db_connector import getConnection
import mysql.connector


def add_user_to_database(user_data, getConnection):
    connection = None
    cursor = None


    ra = user_data.get('RA')
    nome = user_data.get('nome')
    senha = user_data.get('senha')
    tipo_usuario = user_data.get('tipo')


    try:
        connection = getConnection()
        if not connection:
            return False, "Não foi possível estabelecer conexão"
        cursor = connection.cursor()


        if tipo_usuario == 'Aluno':
            turma = user_data.get('turma')
            pont_total = 0


            sql = """INSERT INTO alunos
                     (aluno_RA, nome_aluno, turma, senha_aluno, pont_total)
                     VALUES (%s, %s, %s, %s, %s)"""
            values = (ra, nome, turma, senha, pont_total)
        elif tipo_usuario == 'Professor':
            materia = user_data.get('materia')


            sql = """INSERT INTO professores
                     (prof_RA, nome_prof, senha_prof, materia)
                     VALUES (%s, %s, %s, %s)"""
            values = (ra, nome, senha, materia)
        else:
            return False, f"Tipo de usuário '{tipo_usuario}' desconhecido"
           
        print(f"SQL: {sql}")
        print(f"Valores: {values}")


        cursor.execute(sql, values)
        connection.commit()


        return True, f"Usuário {nome} (RA: {ra}) cadastrado com sucesso como {tipo_usuario}!"


    except mysql.connector.Error as err:
        if connection:
            try:
                connection.rollback() # Desfaz a transação em caso de erro
            except mysql.connector.Error as rb_err:
                print(f"Erro durante o rollback: {rb_err}")
       
        # Trata erro de RA duplicado (código 1062 para MySQL)
        if err.errno == 1062:
            return False, f"Erro ao cadastrar: O RA '{ra}' já existe no sistema."
        # Outros erros de banco
        return False, f"Erro de banco de dados ao cadastrar {nome} (RA: {ra}): {err}"
    except Exception as e:
        # Captura qualquer outra exceção inesperada
        if connection:
            try:
                connection.rollback()
            except mysql.connector.Error as rb_err:
                print(f"Erro durante o rollback (exceção genérica): {rb_err}")
        return False, f"Ocorreu um erro inesperado durante o cadastro de {nome} (RA: {ra}): {e}"
    finally:
        if cursor:
            try:
                cursor.close()
            except mysql.connector.Error as cur_err:
                print(f"Erro ao fechar o cursor: {cur_err}")
        if connection and connection.is_connected():
            try:
                connection.close()
            except mysql.connector.Error as con_err:
                print(f"Erro ao fechar a conexão: {con_err}")
