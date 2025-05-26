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


def adicionar_questao_db(dados_questao, getConnection):
    # Adiciona uma nova questão ao banco de dados.
    connection = None
    cursor = None

    # Nomes das tabelas e colunas de lookup - AJUSTE SE NECESSÁRIO!
    # Exemplo:
    tabela_materias = "materias"
    col_id_materia = "id_materia"
    col_nome_materia = "nome_materia"

    tabela_dificuldades = "dificuldades"
    col_id_dificuldade = "id_dificuldade"
    col_nome_dificuldade = "nome_dificuldade"

    try:
        connection = getConnection()
        if not connection:
            return False, "Falha ao obter conexão com o banco de dados."
        cursor = connection.cursor()

        # 1. Obter id_materia da tabela de lookup
        nome_materia_selecionada = dados_questao.get('subject')
        sql_find_materia = f"SELECT {col_id_materia} FROM {tabela_materias} WHERE {col_nome_materia} = %s"
        cursor.execute(sql_find_materia, (nome_materia_selecionada,))
        resultado_materia = cursor.fetchone()
        if not resultado_materia:
            return False, f"Matéria '{nome_materia_selecionada}' não encontrada na base de dados."
        id_materia_db = resultado_materia[0]

        # 2. Obter id_dificuldade da tabela de lookup
        nome_dificuldade_selecionada = dados_questao.get('difficulty')
        sql_find_dificuldade = f"SELECT {col_id_dificuldade} FROM {tabela_dificuldades} WHERE {col_nome_dificuldade} = %s"
        cursor.execute(sql_find_dificuldade, (nome_dificuldade_selecionada,))
        resultado_dificuldade = cursor.fetchone()
        if not resultado_dificuldade:
            return False, f"Dificuldade '{nome_dificuldade_selecionada}' não encontrada na base de dados."
        id_dificuldade_db = resultado_dificuldade[0]

        # 3. Preparar os dados restantes para a tabela 'questoes'
        serie_texto = dados_questao.get('grade')
        enunciado_texto = dados_questao.get('text')
        opcoes_lista = dados_questao.get('options', []) # Default para lista vazia para segurança
        indice_correta = dados_questao.get('correct_option')
        explicacao_texto = dados_questao.get('explanation')

        # Validação do número de opções (idealmente já feita antes, mas uma segurança extra)
        if len(opcoes_lista) != 4:
            return False, "A questão deve ter exatamente 4 alternativas."
        
        alternativa_1 = opcoes_lista[0]
        alternativa_2 = opcoes_lista[1]
        alternativa_3 = opcoes_lista[2]
        alternativa_4 = opcoes_lista[3]

        # 4. Inserir na tabela 'questoes'
        sql_insert_questao = """
            INSERT INTO questoes (
                id_materia, serie, id_dificuldade, enunciado,
                alternativa_1, alternativa_2, alternativa_3, alternativa_4,
                indice_alternativa_correta, explicacao
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        valores_questao = (
            id_materia_db, serie_texto, id_dificuldade_db, enunciado_texto,
            alternativa_1, alternativa_2, alternativa_3, alternativa_4,
            indice_correta, explicacao_texto
        )

        cursor.execute(sql_insert_questao, valores_questao)
        connection.commit()

        return True, "Questão cadastrada com sucesso!"

    except mysql.connector.Error as err:
        if connection:
            try:
                connection.rollback()
            except mysql.connector.Error as rb_err:
                print(f"Erro durante o rollback: {rb_err}")
        return False, f"Erro de banco de dados ao cadastrar questão: {err}"
    except IndexError:
        # Este erro pode ocorrer se dados_questao['options'] não tiver 4 elementos
        # e a validação anterior falhar ou não existir.
        if connection:
            try:
                connection.rollback()
            except mysql.connector.Error as rb_err:
                print(f"Erro durante o rollback (IndexError): {rb_err}")
        return False, "Erro ao processar alternativas: número incorreto de opções fornecidas."
    except Exception as e:
        if connection:
            try:
                connection.rollback()
            except mysql.connector.Error as rb_err:
                print(f"Erro durante o rollback (exceção genérica): {rb_err}")
        return False, f"Ocorreu um erro inesperado ao cadastrar questão: {e}"
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


def adicionar_turma_db(dados_turma, funcao_get_conexao):
    # Adiciona uma nova turma ao banco de dados.
    connection = None
    cursor = None

    # Extrair dados do dicionário
    nome = dados_turma.get('name')
    serie = dados_turma.get('grade')
    periodo = dados_turma.get('shift')
    ano = dados_turma.get('year') 

    try:
        connection = funcao_get_conexao()
        if not connection:
            return False, "Falha ao obter conexão com o banco de dados."
        cursor = connection.cursor()

        sql_insert_turma = """
            INSERT INTO turmas (nome_turma, serie_turma, periodo_turma, ano_letivo)
            VALUES (%s, %s, %s, %s)
        """
        valores_turma = (nome, serie, periodo, ano)

        # Para depuração, você pode imprimir a query e os valores:
        cursor.execute(sql_insert_turma, valores_turma)
        connection.commit()

        return True, f"Turma '{nome}' ({serie} - {periodo} / {ano}) cadastrada com sucesso!"

    except mysql.connector.Error as err:
        if connection:
            try:
                connection.rollback()
            except mysql.connector.Error as rb_err:
                print(f"Erro durante o rollback: {rb_err}")
        
        # Trata erro de entrada duplicada (código 1062 para MySQL)
        # se você adicionou a restrição UNIQUE na tabela
        if err.errno == 1062:
            return False, f"Erro ao cadastrar: A turma '{nome}' ({serie} - {periodo} / {ano}) já existe."
        # Outros erros de banco
        return False, f"Erro de banco de dados ao cadastrar turma: {err}"
    except Exception as e:
        # Captura qualquer outra exceção inesperada
        if connection:
            try:
                connection.rollback()
            except mysql.connector.Error as rb_err:
                print(f"Erro durante o rollback (exceção genérica): {rb_err}")
        return False, f"Ocorreu um erro inesperado ao cadastrar turma: {e}"
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