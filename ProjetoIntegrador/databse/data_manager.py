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

def search_ranking_data_from_db(get_connection_func, serie_filter=None):
    # Busca os dados dos alunos do banco de dados para o ranking
    connection = None
    cursor = None
    lista_alunos_ranking = []

    # Nomes das colunas da sua tabela alunos
    col_ra = "aluno_RA"
    col_nome = "nome_aluno"
    col_turma = "turma"
    col_pontuacao = "pont_total"

    try:
        connection = getConnection() # Chama a função de conexão passada
        if not connection:
            print("Erro (data_manager): Não foi possível conectar ao banco.")
            return lista_alunos_ranking
        
        cursor = connection.cursor()
        query_sql = f"SELECT {col_ra}, {col_nome}, {col_turma}, {col_pontuacao} FROM alunos"
        params = []
        valid_series_filters = ["1º Ano", "2º Ano", "3º Ano"]

        if serie_filter and serie_filter in valid_series_filters:
            query_sql += f" WHERE {col_turma} LIKE %s"
            params.append(f"{serie_filter}%")
        
        query_sql += f" ORDER BY {col_pontuacao} DESC"

        if params:
            cursor.execute(query_sql, params)
        else:
            cursor.execute(query_sql)
        
        resultados_db = cursor.fetchall()

        for linha_db in resultados_db:
            ra, nome, turma_completa, pontuacao = linha_db
            partes_turma = turma_completa.split()
            serie_para_exibicao = " ".join(partes_turma[:2]) if len(partes_turma) >= 2 else turma_completa
            
            aluno_dict = {
                "ra": ra,
                "name": nome,
                "series": serie_para_exibicao,
                "score": float(pontuacao) if pontuacao is not None else 0.0
                # O campo "games_played" foi removido conforme sua solicitação
            }
            lista_alunos_ranking.append(aluno_dict)

    except mysql.connector.Error as err:
        print(f"Erro (data_manager) ao buscar ranking: {err}")
    except Exception as e:
        print(f"Erro inesperado (data_manager): {e}")
    finally:
        if cursor:
            try:
                cursor.close()
            except mysql.connector.Error as cur_err:
                print(f"Erro (data_manager) ao fechar cursor: {cur_err}")
        if connection and connection.is_connected():
            try:
                connection.close()
            except mysql.connector.Error as con_err:
                print(f"Erro (data_manager) ao fechar conexão: {con_err}")
            
    return lista_alunos_ranking

def delete_class_from_db(class_id_to_delete, getConnection):
    # Exclui uma turma do banco de dados com base no seu ID.
    connection = None
    cursor = None
    rows_affected = 0

    # Nome da tabela e da coluna de ID 
    table_name = "turmas"
    id_column_name = "id_turma"

    try:
        connection = getConnection()
        if not connection:
            return False, "Falha ao obter conexão com o banco de dados."
        
        cursor = connection.cursor()

        sql_delete_class = f"DELETE FROM {table_name} WHERE {id_column_name} = %s"
        
        # Para depuração:
        # print(f"SQL: {sql_delete_class}")
        # print(f"ID para deletar: {class_id_to_delete}")

        cursor.execute(sql_delete_class, (class_id_to_delete,))
        connection.commit()
        rows_affected = cursor.rowcount # Verifica quantas linhas foram afetadas

        if rows_affected > 0:
            return True, f"Turma ID {class_id_to_delete} excluída com sucesso."
        else:
            return False, f"Nenhuma turma encontrada com o ID {class_id_to_delete} para excluir."

    except mysql.connector.Error as err:
        # Erros de integridade referencial (FK constraints) podem acontecer aqui
        if connection:
            try:
                connection.rollback()
            except mysql.connector.Error as rb_err:
                print(f"Erro (delete_class_from_db) durante o rollback: {rb_err}")
        return False, f"Erro de banco de dados ao excluir turma ID {class_id_to_delete}: {err}"
    except Exception as e:
        if connection:
            try:
                connection.rollback()
            except mysql.connector.Error as rb_err:
                print(f"Erro (delete_class_from_db) durante o rollback (exceção genérica): {rb_err}")
        return False, f"Ocorreu um erro inesperado ao excluir turma ID {class_id_to_delete}: {e}"
    finally:
        if cursor:
            try:
                cursor.close()
            except mysql.connector.Error: pass # Silencioso ou log mínimo
        if connection and connection.is_connected():
            try:
                connection.close()
            except mysql.connector.Error: pass # Silencioso ou log mínimo

def delete_user_from_db(user_ra, user_type, getConnection):
    # Exclui um usuário (aluno ou professor) do banco de dados.
    connection = None
    cursor = None
    rows_affected = 0

    table_name = ""
    id_column_name = ""

    if user_type == "Aluno":
        table_name = "alunos"
        id_column_name = "aluno_RA"
    elif user_type == "Professor":
        table_name = "professores"
        id_column_name = "prof_RA"
    else:
        return False, f"Tipo de usuário desconhecido: {user_type}"

    try:
        connection = getConnection()
        if not connection:
            return False, "Falha ao obter conexão com o banco de dados."
        
        cursor = connection.cursor()

        sql_delete_user = f"DELETE FROM {table_name} WHERE {id_column_name} = %s"
        
        # Para depuração:
        # print(f"SQL: {sql_delete_user}")
        # print(f"RA para deletar: {user_ra} (Tipo: {user_type})")

        cursor.execute(sql_delete_user, (user_ra,))
        connection.commit()
        rows_affected = cursor.rowcount

        if rows_affected > 0:
            return True, f"{user_type} RA {user_ra} excluído(a) com sucesso."
        else:
            # Isso pode acontecer se o usuário já foi deletado ou o RA/tipo não existe.
            return False, f"Nenhum {user_type.lower()} encontrado com RA {user_ra} para excluir."

    except mysql.connector.Error as err:
        # Lidar com erros de FK aqui se necessário (err.errno pode dar pistas)
        if connection:
            try:
                connection.rollback()
            except mysql.connector.Error as rb_err:
                print(f"Erro (delete_user_from_db) durante o rollback: {rb_err}")
        return False, f"Erro de banco de dados ao excluir {user_type.lower()} RA {user_ra}: {err}"
    except Exception as e:
        if connection:
            try:
                connection.rollback()
            except mysql.connector.Error as rb_err:
                print(f"Erro (delete_user_from_db) durante o rollback (exceção genérica): {rb_err}")
        return False, f"Ocorreu um erro inesperado ao excluir {user_type.lower()} RA {user_ra}: {e}"
    finally:
        if cursor:
            try:
                cursor.close()
            except mysql.connector.Error: pass 
        if connection and connection.is_connected():
            try:
                connection.close()
            except mysql.connector.Error: pass


def search_all_users_from_db(get_connection_func):
    # Busca todos os usuários (alunos e professores) do banco de dados.
    all_users_list = []
    connection = None
    cursor = None

    # Nomes das tabelas e colunas
    # Tabela Alunos
    table_alunos = "alunos"
    col_aluno_ra = "aluno_RA"
    col_aluno_nome = "nome_aluno"
    col_aluno_turma = "turma"  # Ex: "1º Ano A", "3º Ano B"
    col_aluno_senha = "senha_aluno"

    # Tabela Professores
    table_professores = "professores"
    col_prof_ra = "prof_RA"
    col_prof_nome = "nome_prof"
    col_prof_materia = "materia" 
    col_prof_senha = "senha_prof"


    try:
        connection = getConnection()
        if not connection:
            print("Erro (fetch_all_users): Falha ao obter conexão com o banco.")
            return all_users_list
        
        cursor = connection.cursor()

        # Buscar Alunos
        sql_alunos = f"SELECT {col_aluno_ra}, {col_aluno_nome}, {col_aluno_turma}, {col_aluno_senha} FROM {table_alunos}"
        cursor.execute(sql_alunos)
        alunos_db = cursor.fetchall()

        for aluno_row in alunos_db:
            ra, nome, turma_completa, senha = aluno_row
            
            # Processar turma_completa para obter serie e classe
            partes_turma = turma_completa.split()
            serie_aluno = ""
            classe_aluno = ""
            if len(partes_turma) >= 2: # Espera pelo menos "Xº Ano"
                serie_aluno = f"{partes_turma[0]} {partes_turma[1]}" # Ex: "1º Ano"
                if len(partes_turma) > 2:
                    classe_aluno = " ".join(partes_turma[2:]) # Pega o resto como classe, ex: "A" ou "A Matutino"
            else: # Caso inesperado, usa a turma completa como série
                serie_aluno = turma_completa


            aluno_dict = {
                "RA": ra,
                "nome": nome,
                "tipo": "Aluno",
                "serie": serie_aluno, # Ex: "1º Ano" (ou "1 Ano" se normalizado acima)
                "classe": classe_aluno, # Ex: "A"
                "senha": senha
            }
            all_users_list.append(aluno_dict)

        # Buscar Professores

        sql_professores = f"SELECT {col_prof_ra}, {col_prof_nome}, {col_prof_materia}, {col_prof_senha} FROM {table_professores}"
        cursor.execute(sql_professores)
        professores_db = cursor.fetchall()

        for prof_row in professores_db:
            ra, nome, materia_db, senha = prof_row
            professor_dict = {
                "RA": ra,
                "nome": nome,
                "tipo": "Professor",
                "materia": materia_db,
                "senha": senha
            }
            all_users_list.append(professor_dict)

    except mysql.connector.Error as err:
        print(f"Erro (fetch_all_users) de banco de dados: {err}")
    except Exception as e:
        print(f"Erro inesperado (fetch_all_users): {e}")
    finally:
        if cursor:
            try:
                cursor.close()
            except mysql.connector.Error: pass
        if connection and connection.is_connected():
            try:
                connection.close()
            except mysql.connector.Error: pass
            
    return all_users_list


def update_class_in_db(class_id, new_class_data, getConnection):
    # Atualiza os dados de uma turma existente no banco de dados.
    connection = None
    cursor = None
    rows_affected = 0

    # Nomes da tabela e colunas (ajuste se os nomes no seu banco forem diferentes)
    table_name = "turmas"
    id_column_name = "id_turma"
    col_nome = "nome_turma"
    col_serie = "serie_turma"
    col_periodo = "periodo_turma"
    col_ano = "ano_letivo"

    try:
        connection = getConnection()
        if not connection:
            return False, "Falha ao obter conexão com o banco de dados."
        
        cursor = connection.cursor()

        # Montar a query UPDATE dinamicamente com base nos dados fornecidos
        # Para este exemplo, vamos assumir que todos os campos de new_class_data são para serem atualizados
        sql_update_class = f"""
            UPDATE {table_name}
            SET {col_nome} = %s, 
                {col_serie} = %s, 
                {col_periodo} = %s, 
                {col_ano} = %s
            WHERE {id_column_name} = %s
        """
        
        valores_para_update = (
            new_class_data.get('nome_turma'),
            new_class_data.get('serie_turma'),
            new_class_data.get('periodo_turma'),
            new_class_data.get('ano_letivo'),
            class_id 
        )

        # Para depuração:
        # print(f"SQL UPDATE: {sql_update_class}")
        # print(f"Valores para UPDATE: {valores_para_update}")

        cursor.execute(sql_update_class, valores_para_update)
        connection.commit()
        rows_affected = cursor.rowcount

        if rows_affected > 0:
            return True, f"Turma ID {class_id} atualizada com sucesso."
        else:
            # Isso pode acontecer se o ID não existir ou se os dados novos forem idênticos aos existentes.
            return False, f"Nenhuma turma encontrada com o ID {class_id} para atualizar, ou os dados não foram alterados."

    except mysql.connector.Error as err:
        if connection:
            try:
                connection.rollback()
            except mysql.connector.Error as rb_err:
                print(f"Erro (update_class_in_db) durante o rollback: {rb_err}")
        return False, f"Erro de banco de dados ao atualizar turma ID {class_id}: {err}"
    except Exception as e:
        if connection:
            try:
                connection.rollback()
            except mysql.connector.Error as rb_err:
                print(f"Erro (update_class_in_db) durante o rollback (exceção genérica): {rb_err}")
        return False, f"Ocorreu um erro inesperado ao atualizar turma ID {class_id}: {e}"
    finally:
        if cursor:
            try:
                cursor.close()
            except mysql.connector.Error: pass
        if connection and connection.is_connected():
            try:
                connection.close()
            except mysql.connector.Error: pass

def delete_question_from_db(question_id_to_delete, getConnection):

    # Exclui uma questão do banco de dados com base no seu ID.
    connection = None
    cursor = None
    rows_affected = 0

    # Nome da tabela e da coluna de ID (ajuste se necessário)
    table_name = "questoes"
    id_column_name = "id_questao"

    try:
        connection = getConnection()
        if not connection:
            return False, "Falha ao obter conexão com o banco de dados."
        
        cursor = connection.cursor()

        sql_delete_question = f"DELETE FROM {table_name} WHERE {id_column_name} = %s"
        
        # print(f"DEBUG SQL (delete_question): {sql_delete_question}") # Para depuração
        # print(f"DEBUG ID para deletar: {question_id_to_delete}")    # Para depuração

        cursor.execute(sql_delete_question, (question_id_to_delete,))
        connection.commit()
        rows_affected = cursor.rowcount

        if rows_affected > 0:
            return True, f"Questão ID {question_id_to_delete} excluída com sucesso."
        else:
            return False, f"Nenhuma questão encontrada com o ID {question_id_to_delete} para excluir."

    except mysql.connector.Error as err:
        if connection:
            try:
                connection.rollback()
            except mysql.connector.Error as rb_err:
                print(f"Erro (delete_question_from_db) durante o rollback: {rb_err}")
        return False, f"Erro de banco de dados ao excluir questão ID {question_id_to_delete}: {err}"
    except Exception as e:
        if connection:
            try:
                connection.rollback()
            except mysql.connector.Error as rb_err:
                print(f"Erro (delete_question_from_db) durante o rollback (exceção genérica): {rb_err}")
        return False, f"Ocorreu um erro inesperado ao excluir questão ID {question_id_to_delete}: {e}"
    finally:
        if cursor:
            try:
                cursor.close()
            except mysql.connector.Error: pass
        if connection and connection.is_connected():
            try:
                connection.close()
            except mysql.connector.Error: pass

def update_question_in_db(question_id, question_update_data, getConnection):
    # Atualiza uma questão existente no banco de dados.
    connection = None
    cursor = None
    rows_affected = 0

    # Nomes das tabelas e colunas de lookup - AJUSTE SE NECESSÁRIO!
    tabela_materias = "materias"
    col_id_materia_lookup = "id_materia"
    col_nome_materia_lookup = "nome_materia"

    tabela_dificuldades = "dificuldades"
    col_id_dificuldade_lookup = "id_dificuldade"
    col_nome_dificuldade_lookup = "nome_dificuldade"

    # Nomes da tabela e colunas de 'questoes' - AJUSTE SE NECESSÁRIO!
    tbl_q = "questoes"
    col_q_id_where = "id_questao" # Para a cláusula WHERE
    col_q_id_materia = "id_materia"
    col_q_serie = "serie"
    col_q_id_dificuldade = "id_dificuldade"
    col_q_enunciado = "enunciado"
    col_q_alt1 = "alternativa_1"
    col_q_alt2 = "alternativa_2"
    col_q_alt3 = "alternativa_3"
    col_q_alt4 = "alternativa_4"
    col_q_idx_correta = "indice_alternativa_correta"
    col_q_explicacao = "explicacao" # Mapeado do 'hint'

    try:
        connection = getConnection()
        if not connection:
            return False, "Falha ao obter conexão com o banco de dados."
        cursor = connection.cursor()

        # 1. Obter id_materia da tabela de lookup
        nome_materia_nova = question_update_data.get('subject_name')
        sql_find_materia = f"SELECT {col_id_materia_lookup} FROM {tabela_materias} WHERE {col_nome_materia_lookup} = %s"
        cursor.execute(sql_find_materia, (nome_materia_nova,))
        resultado_materia = cursor.fetchone()
        if not resultado_materia:
            return False, f"Matéria '{nome_materia_nova}' não encontrada para atualização."
        id_materia_db = resultado_materia[0]

        # 2. Obter id_dificuldade da tabela de lookup
        nome_dificuldade_nova = question_update_data.get('difficulty_name')
        sql_find_dificuldade = f"SELECT {col_id_dificuldade_lookup} FROM {tabela_dificuldades} WHERE {col_nome_dificuldade_lookup} = %s"
        cursor.execute(sql_find_dificuldade, (nome_dificuldade_nova,))
        resultado_dificuldade = cursor.fetchone()
        if not resultado_dificuldade:
            return False, f"Dificuldade '{nome_dificuldade_nova}' não encontrada para atualização."
        id_dificuldade_db = resultado_dificuldade[0]

        # 3. Preparar outros dados
        serie_nova = question_update_data.get('serie')
        enunciado_novo = question_update_data.get('enunciado')
        opcoes_novas = question_update_data.get('options_list', [])
        indice_correta_novo = question_update_data.get('correct_option_index')
        explicacao_nova = question_update_data.get('explicacao') # Mapeado do 'hint'

        if len(opcoes_novas) != 4:
            return False, "A questão deve ter exatamente 4 alternativas para atualização."
        
        alt1, alt2, alt3, alt4 = opcoes_novas[0], opcoes_novas[1], opcoes_novas[2], opcoes_novas[3]

        # 4. Montar e executar o UPDATE
        sql_update_questao = f"""
            UPDATE {tbl_q}
            SET 
                {col_q_id_materia} = %s, 
                {col_q_serie} = %s, 
                {col_q_id_dificuldade} = %s,
                {col_q_enunciado} = %s,
                {col_q_alt1} = %s,
                {col_q_alt2} = %s,
                {col_q_alt3} = %s,
                {col_q_alt4} = %s,
                {col_q_idx_correta} = %s,
                {col_q_explicacao} = %s
            WHERE {col_q_id_where} = %s
        """
        valores_update = (
            id_materia_db, serie_nova, id_dificuldade_db, enunciado_novo,
            alt1, alt2, alt3, alt4,
            indice_correta_novo, explicacao_nova,
            question_id # Para a cláusula WHERE
        )

        cursor.execute(sql_update_questao, valores_update)
        connection.commit()
        rows_affected = cursor.rowcount

        if rows_affected > 0:
            return True, f"Questão ID {question_id} atualizada com sucesso."
        else:
            # Pode acontecer se o ID não existir ou se os dados novos forem idênticos aos existentes.
            return False, f"Nenhuma questão encontrada com ID {question_id} para atualizar, ou os dados não foram alterados."

    except mysql.connector.Error as err:
        if connection: connection.rollback()
        return False, f"Erro de banco de dados ao atualizar questão ID {question_id}: {err}"
    except IndexError:
        if connection: connection.rollback()
        return False, "Erro ao processar alternativas para atualização: número incorreto de opções."
    except Exception as e:
        if connection: connection.rollback()
        return False, f"Erro inesperado ao atualizar questão ID {question_id}: {e}"
    finally:
        if cursor: cursor.close()
        if connection and connection.is_connected(): connection.close()


def update_user_in_db(user_ra, user_type, fields_to_update, getConnection):
    # Atualiza os dados de um usuário (aluno ou professor) no banco de dados.
    connection = None
    cursor = None
    
    if not fields_to_update: # Nenhum campo para atualizar
        return False, "Nenhum dado fornecido para atualização."

    table_name = ""
    id_column_name = ""
    column_map = {} # Mapeia chaves do dict para nomes de colunas no DB

    if user_type == "Aluno":
        table_name = "alunos"
        id_column_name = "aluno_RA"
        column_map = {
            "nome": "nome_aluno",
            "turma": "turma", # Assumindo que 'turma' é a coluna no DB para Alunos
            "senha": "senha_aluno"
        }
    elif user_type == "Professor":
        table_name = "professores"
        id_column_name = "prof_RA"
        column_map = {
            "nome": "nome_prof",
            "materia": "materia", # Usuário confirmou 'materia' sem acento no DB
            "senha": "senha_prof"
        }
    else:
        return False, f"Tipo de usuário desconhecido: {user_type}"

    set_clauses = []
    sql_values = []

    for key, value in fields_to_update.items():
        db_column = column_map.get(key)
        if db_column: # Se a chave do dicionário tem um mapeamento de coluna válido
            set_clauses.append(f"{db_column} = %s")
            sql_values.append(value)
        # else: Ignora chaves não mapeadas ou loga um aviso

    if not set_clauses:
        return False, "Nenhum campo válido para atualização foi fornecido."

    sql_values.append(user_ra) # Adiciona o RA para a cláusula WHERE

    try:
        connection = getConnection()
        if not connection:
            return False, "Falha ao obter conexão com o banco de dados."
        
        cursor = connection.cursor()

        sql_update_user = f"UPDATE {table_name} SET {', '.join(set_clauses)} WHERE {id_column_name} = %s"
        
        # Para depuração:
        # print(f"SQL UPDATE: {sql_update_user}")
        # print(f"Valores para UPDATE: {tuple(sql_values)}")

        cursor.execute(sql_update_user, tuple(sql_values))
        connection.commit()
        rows_affected = cursor.rowcount

        if rows_affected > 0:
            return True, f"{user_type} RA {user_ra} atualizado(a) com sucesso."
        else:
            return False, f"Nenhum {user_type.lower()} encontrado com RA {user_ra}, ou os dados não foram alterados."

    except mysql.connector.Error as err:
        if connection: connection.rollback()
        return False, f"Erro de BD ao atualizar {user_type.lower()} RA {user_ra}: {err}"
    except Exception as e:
        if connection: connection.rollback()
        return False, f"Erro inesperado ao atualizar {user_type.lower()} RA {user_ra}: {e}"
    finally:
        if cursor: cursor.close()
        if connection and connection.is_connected(): connection.close()