from databse.db_connector import getConnection
import mysql.connector
from config import TOTAL_QUESTIONS, CHECKPOINT_INTERVALS
from datetime import datetime

def add_user_to_database(user_data, getConnection):
    connection = None; cursor = None
    ra = user_data.get('RA'); nome = user_data.get('nome'); senha = user_data.get('senha')
    tipo_usuario = user_data.get('tipo')

    tbl_alunos = "alunos"; col_al_ra = "aluno_RA"; col_al_nome = "nome_aluno"; 
    col_al_turma = "turma"; col_al_senha = "senha_aluno"; col_al_pont_total = "pont_total"
    tbl_prof = "professores"; col_pr_ra = "prof_RA"; col_pr_nome = "nome_prof"; 
    col_pr_senha = "senha_prof"; col_pr_fk_id_materia = "id_materia" # FK em professores

    try:
        connection = getConnection()
        if not connection: return False, "Não foi possível estabelecer conexão"
        cursor = connection.cursor()

        if tipo_usuario == 'student':
            turma = user_data.get('turma'); pont_total = 0 
            sql = f"""INSERT INTO {tbl_alunos} ({col_al_ra}, {col_al_nome}, {col_al_turma}, {col_al_senha}, {col_al_pont_total})
                      VALUES (%s, %s, %s, %s, %s)"""
            values = (ra, nome, turma, senha, pont_total)
        elif tipo_usuario == 'teacher':
            materia_nome_ui = user_data.get('materia') 
            id_materia_db = get_materia_id_by_name(materia_nome_ui, getConnection)
            if id_materia_db is None:
                return False, f"Matéria '{materia_nome_ui}' não encontrada para o professor."
            sql = f"""INSERT INTO {tbl_prof} ({col_pr_ra}, {col_pr_nome}, {col_pr_senha}, {col_pr_fk_id_materia})
                      VALUES (%s, %s, %s, %s)"""
            values = (ra, nome, senha, id_materia_db)
        else:
            return False, f"Tipo de usuário '{tipo_usuario}' desconhecido"
            
        cursor.execute(sql, values); connection.commit()
        display_tipo = "Aluno" if tipo_usuario == "student" else "Professor" if tipo_usuario == "teacher" else tipo_usuario
        return True, f"Usuário {nome} (RA: {ra}) cadastrado com sucesso como {display_tipo}!"
    except mysql.connector.Error as err:
        if connection: connection.rollback()
        if err.errno == 1062: return False, f"Erro: RA '{ra}' já existe."
        return False, f"Erro de BD (add_user): {err}"
    except Exception as e:
        if connection: connection.rollback()
        return False, f"Erro inesperado (add_user): {e}"
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

    if user_type == "student":
        table_name = "alunos"
        id_column_name = "aluno_RA"
        column_map = {
            "nome": "nome_aluno",
            "turma": "turma", # Assumindo que 'turma' é a coluna no DB para Alunos
            "senha": "senha_aluno"
        }
    elif user_type == "teacher":
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

def delete_user_from_db(user_ra, user_type, getConnection):
    # Exclui um usuário (aluno ou professor) do banco de dados.
    connection = None
    cursor = None
    rows_affected = 0

    table_name = ""
    id_column_name = ""

    if user_type == "student":
        table_name = "alunos"
        id_column_name = "aluno_RA"
    elif user_type == "teacher":
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

def add_question_db(dados_questao, getConnection):
    # Adiciona uma nova questão ao banco de dados.
    connection = None; cursor = None
    # Nomes conforme seu SQL e ERD
    tbl_q = "questoes"; col_q_id_materia_fk = "id_materia"; col_q_id_dificuldade_fk = "id_dificuldade"
    col_q_id_serie_fk = "id_serie"; col_q_enunciado = "enunciado"; col_q_explicacao = "explicacao"
    col_q_alt1 = "alternativa_1"; col_q_alt2 = "alternativa_2"; col_q_alt3 = "alternativa_3"; col_q_alt4 = "alternativa_4"
    col_q_idx_correta = "indice_alternativa_correta"

    try:
        connection = getConnection()
        if not connection: return False, "Falha ao obter conexão."
        cursor = connection.cursor()

        nome_materia = dados_questao.get('subject')
        id_materia_db = get_materia_id_by_name(nome_materia, getConnection)
        if id_materia_db is None: return False, f"Matéria '{nome_materia}' não encontrada."

        nome_dificuldade = dados_questao.get('difficulty')
        id_dificuldade_db = get_difficulty_id_by_name(nome_dificuldade, getConnection)
        if id_dificuldade_db is None: return False, f"Dificuldade '{nome_dificuldade}' não encontrada."

        nome_serie = dados_questao.get('grade') # Nome da série vindo da UI
        id_serie_db = get_serie_id_by_name(nome_serie, getConnection)
        if id_serie_db is None: return False, f"Série '{nome_serie}' não encontrada."

        enunciado = dados_questao.get('text'); opcoes = dados_questao.get('options', [])
        idx_correta = dados_questao.get('correct_option')
        explicacao_texto = dados_questao.get('explanation') # UI envia 'explanation', DB tem 'explicacao'

        if len(opcoes) != 4: return False, "São necessárias 4 alternativas."
        a1, a2, a3, a4 = opcoes[0], opcoes[1], opcoes[2], opcoes[3]

        sql = f"""INSERT INTO {tbl_q} (
                    {col_q_id_materia_fk}, {col_q_id_dificuldade_fk}, {col_q_id_serie_fk}, 
                    {col_q_enunciado}, {col_q_explicacao}, {col_q_alt1}, {col_q_alt2}, 
                    {col_q_alt3}, {col_q_alt4}, {col_q_idx_correta}
                  ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        valores = (id_materia_db, id_dificuldade_db, id_serie_db, enunciado, explicacao_texto,
                   a1, a2, a3, a4, idx_correta)
        
        cursor.execute(sql, valores); connection.commit()
        return True, "Questão cadastrada com sucesso!"
    except mysql.connector.Error as err:
        if connection: connection.rollback()
        return False, f"Erro de BD (add_questao): {err}"
    except IndexError:
        if connection: connection.rollback()
        return False, "Erro (add_questao) ao processar alternativas: são necessárias 4."
    except Exception as e:
        if connection: connection.rollback()
        return False, f"Erro inesperado (add_questao): {e}"
    finally:
        if cursor: cursor.close()
        if connection and connection.is_connected(): connection.close()

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
    connection = None; cursor = None;
    
    tbl_q = "questoes"; col_q_id_where = "id_questao"
    col_q_id_materia_fk = "id_materia"; col_q_id_dificuldade_fk = "id_dificuldade"
    col_q_id_serie_fk = "id_serie"; col_q_enunciado = "enunciado"; col_q_explicacao = "explicacao"
    col_q_alt1 = "alternativa_1"; col_q_alt2 = "alternativa_2"; col_q_alt3 = "alternativa_3"; col_q_alt4 = "alternativa_4"
    col_q_idx_correta = "indice_alternativa_correta"

    try:
        connection = getConnection()
        if not connection: return False, "Falha ao obter conexão."
        cursor = connection.cursor()
        
        set_parts = []; sql_values = []

        # Nomes de matéria, dificuldade e série são recebidos da UI, precisamos dos IDs
        if 'subject' in question_update_data: # A UI envia 'subject' (nome)
            id_m_db = get_materia_id_by_name(question_update_data['subject'], getConnection)
            if id_m_db is None: return False, f"Matéria '{question_update_data['subject']}' não encontrada."
            set_parts.append(f"{col_q_id_materia_fk} = %s"); sql_values.append(id_m_db)

        if 'grade' in question_update_data: # A UI envia 'grade' (nome da série)
            id_s_db = get_serie_id_by_name(question_update_data['grade'], getConnection)
            if id_s_db is None: return False, f"Série '{question_update_data['grade']}' não encontrada."
            set_parts.append(f"{col_q_id_serie_fk} = %s"); sql_values.append(id_s_db)
        
        if 'difficulty' in question_update_data: # A UI envia 'difficulty' (nome)
            id_d_db = get_difficulty_id_by_name(question_update_data['difficulty'], getConnection)
            if id_d_db is None: return False, f"Dificuldade '{question_update_data['difficulty']}' não encontrada."
            set_parts.append(f"{col_q_id_dificuldade_fk} = %s"); sql_values.append(id_d_db)

        # Mapear chaves do dict da UI para colunas do DB
        direct_mapping_keys = { 
            "text": col_q_enunciado, 
            "correct_option": col_q_idx_correta, # UI envia 'correct_option' (índice)
            "explanation": col_q_explicacao # UI envia 'explanation' (ou 'hint'), DB tem 'explicacao'
        }
        for ui_key, db_col in direct_mapping_keys.items():
            if ui_key in question_update_data:
                set_parts.append(f"{db_col} = %s"); sql_values.append(question_update_data[ui_key])
        
        if 'options' in question_update_data: # UI envia 'options' (lista)
            opcoes = question_update_data['options']
            if len(opcoes) == 4:
                alt_cols = [col_q_alt1, col_q_alt2, col_q_alt3, col_q_alt4]
                for i in range(4):
                    set_parts.append(f"{alt_cols[i]} = %s"); sql_values.append(opcoes[i])
            else: return False, "Para atualizar, são necessárias 4 alternativas."

        if not set_parts: return True, "Nenhum dado fornecido para atualizar a questão."
        sql_values.append(question_id) # ID da questão para o WHERE
        sql_update = f"UPDATE {tbl_q} SET {', '.join(set_parts)} WHERE {col_q_id_where} = %s"
        
        cursor.execute(sql_update, tuple(sql_values)); connection.commit()
        rows_affected = cursor.rowcount
        if rows_affected > 0: return True, f"Questão ID {question_id} atualizada."
        else: return False, f"Questão ID {question_id} não encontrada ou dados não alterados."
    except mysql.connector.Error as err:
        if connection: connection.rollback()
        return False, f"Erro de BD (update_questao): {err}"
    except Exception as e:
        if connection: connection.rollback()
        return False, f"Erro inesperado (update_questao): {e}"
    finally:
        if cursor: cursor.close()
        if connection and connection.is_connected(): connection.close()

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

def search_ranking_data_from_db(getConnection, serie_filter=None):
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
        connection = getConnection() 
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

def search_all_users_from_db(getConnection):
    # Busca todos os usuários (alunos e professores) do banco de dados.
    all_users_list = []
    connection = None; cursor = None;

    tbl_alunos = "alunos"; col_al_ra = "aluno_RA"; col_al_nome = "nome_aluno"; 
    col_al_turma = "turma"; col_al_senha = "senha_aluno"
    
    tbl_prof = "professores"; col_pr_ra = "prof_RA"; col_pr_nome = "nome_prof"; 
    col_pr_senha = "senha_prof"; col_pr_fk_id_materia = "id_materia" # FK em professores
    
    tbl_materias = "materias"; col_mat_id_pk = "id_materia"; col_mat_nome = "nome_materia"
    
    try:
        connection = getConnection() # Usa o parâmetro
        if not connection:
            print("Erro (search_all_users): Falha ao obter conexão.")
            return all_users_list
        
        cursor = connection.cursor(dictionary=True) 

        # Alunos
        sql_alunos = f"SELECT {col_al_ra} AS RA, {col_al_nome} AS nome, {col_al_turma} AS turma_completa, {col_al_senha} AS senha FROM {tbl_alunos}"
        cursor.execute(sql_alunos)
        alunos_db = cursor.fetchall()
        for aluno_data in alunos_db:
            partes_turma = aluno_data["turma_completa"].split()
            serie_aluno = f"{partes_turma[0]} {partes_turma[1]}" if len(partes_turma) >= 2 else aluno_data["turma_completa"]
            classe_aluno = " ".join(partes_turma[2:]) if len(partes_turma) > 2 else ""
            all_users_list.append({
                "RA": aluno_data["RA"], "nome": aluno_data["nome"], "tipo": "student",
                "serie": serie_aluno, "classe": classe_aluno, "senha": aluno_data["senha"]
            })

        # Professores
        sql_professores = f"""
            SELECT p.{col_pr_ra} AS RA, p.{col_pr_nome} AS nome, 
                   p.{col_pr_senha} AS senha, m.{col_mat_nome} AS materia
            FROM {tbl_prof} p
            LEFT JOIN {tbl_materias} m ON p.{col_pr_fk_id_materia} = m.{col_mat_id_pk}"""
        cursor.execute(sql_professores)
        professores_db = cursor.fetchall()
        for prof_data in professores_db:
            all_users_list.append({
                "RA": prof_data["RA"], "nome": prof_data["nome"], "tipo": "teacher",
                "materia": prof_data["materia"], "senha": prof_data["senha"]
            })
    except mysql.connector.Error as err: print(f"Erro de BD (search_all_users): {err}")
    except Exception as e: print(f"Erro inesperado (search_all_users): {e}")
    finally:
        if cursor: cursor.close()
        if connection and connection.is_connected(): connection.close()
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


def get_materia_id_by_name(materia_name_to_find, getConnection): 
    """
    Busca o ID de uma matéria (id_materia) na tabela 'materias' 
    com base no nome da matéria (nome_materia).
    """
    connection = None
    cursor = None
    materia_id = None

    db_table_materias = "materias"
    db_col_id_materia = "id_materia"
    db_col_nome_materia = "nome_materia"

    try:
        connection = getConnection() 
        if not connection:
            print(f"Erro (get_materia_id_by_name): Falha ao obter conexão.")
            return None
        
        cursor = connection.cursor()
        query = f"SELECT {db_col_id_materia} FROM {db_table_materias} WHERE {db_col_nome_materia} = %s"
        cursor.execute(query, (materia_name_to_find,))
        result = cursor.fetchone()
        
        if result:
            materia_id = result[0]
            
    except mysql.connector.Error as err:
        print(f"Erro de BD (get_materia_id_by_name) ao buscar matéria '{materia_name_to_find}': {err}")
    except Exception as e:
        print(f"Erro inesperado (get_materia_id_by_name) ao buscar matéria '{materia_name_to_find}': {e}")
    finally:
        if cursor: cursor.close()
        if connection and connection.is_connected(): connection.close()
    return materia_id

def get_difficulty_id_by_name(difficulty_name_to_find, getConnection):
    """
    Busca o ID de uma dificuldade (id_dificuldade) na tabela 'dificuldades'
    com base no nome da dificuldade (nome_dificuldade).
    """
    connection = None
    cursor = None
    difficulty_id = None

    db_table_dificuldades = "dificuldades" 
    db_col_id_dificuldade = "id_dificuldade"
    db_col_nome_dificuldade = "nome_dificuldade"

    try:
        connection = getConnection() 
        if not connection:
            print(f"Erro (get_difficulty_id_by_name): Falha ao obter conexão.")
            return None
            
        cursor = connection.cursor()
        query = f"SELECT {db_col_id_dificuldade} FROM {db_table_dificuldades} WHERE {db_col_nome_dificuldade} = %s"
        cursor.execute(query, (difficulty_name_to_find,))
        result = cursor.fetchone()
        
        if result:
            difficulty_id = result[0]
            
    except mysql.connector.Error as err:
        print(f"Erro de BD (get_difficulty_id_by_name) ao buscar dificuldade '{difficulty_name_to_find}': {err}")
    except Exception as e:
        print(f"Erro inesperado (get_difficulty_id_by_name) ao buscar dificuldade '{difficulty_name_to_find}': {e}")
    finally:
        if cursor: cursor.close()
        if connection and connection.is_connected(): connection.close()
    return difficulty_id

def get_serie_id_by_name(serie_name_to_find, getConnection): # NOVA FUNÇÃO AUXILIAR
    """
    Busca o ID de uma série (id_serie) na tabela 'serie'
    com base no nome da série (nome_serie).
    """
    connection = None
    cursor = None
    serie_id = None

    db_table_serie = "serie" 
    db_col_id_serie = "id_serie"
    db_col_nome_serie = "nome_serie"

    try:
        connection = getConnection() 
        if not connection:
            print(f"Erro (get_serie_id_by_name): Falha ao obter conexão.")
            return None
            
        cursor = connection.cursor()
        query = f"SELECT {db_col_id_serie} FROM {db_table_serie} WHERE {db_col_nome_serie} = %s"
        cursor.execute(query, (serie_name_to_find,))
        result = cursor.fetchone()
        
        if result:
            serie_id = result[0]
            
    except mysql.connector.Error as err:
        print(f"Erro de BD (get_serie_id_by_name) ao buscar série '{serie_name_to_find}': {err}")
    except Exception as e:
        print(f"Erro inesperado (get_serie_id_by_name) ao buscar série '{serie_name_to_find}': {e}")
    finally:
        if cursor: cursor.close()
        if connection and connection.is_connected(): connection.close()
    return serie_id

def search_questions_for_quiz(subject_name, grade_name, difficulty_name, connection):
    quiz_questions = []

    # Nomes de tabelas e colunas conforme seu script SQL
    tbl_q = "questoes"
    col_q_id = "id_questao"; col_q_enunciado = "enunciado"; col_q_fk_materia = "id_materia"
    col_q_fk_serie = "id_serie"; col_q_fk_dificuldade = "id_dificuldade"
    col_q_alt1 = "alternativa_1"; col_q_alt2 = "alternativa_2"; col_q_alt3 = "alternativa_3"
    col_q_alt4 = "alternativa_4"; col_q_idx_correta = "indice_alternativa_correta"
    col_q_explicacao = "explicacao"

    def _format_db_row_to_question_dict(db_row):
        # Função para transformar uma linha do banco em um dicionário de questão.
        return {
            "id": db_row["id"],
            "text": db_row["text"],
            "options": [db_row["opt1"], db_row["opt2"], db_row["opt3"], db_row["opt4"]],
            "correct_option": db_row["correct_option"],
            "hint": db_row["hint"],
            "difficulty_id": db_row["difficulty_id"]
        }

    try:
        connection = getConnection()
        if not connection:
            print("Erro (search_questions): Falha ao obter conexão.")
            return quiz_questions
        
        cursor = connection.cursor(dictionary=True)

        # 1. Obter IDs de matéria e série
        subject_id = get_materia_id_by_name(subject_name, getConnection)
        grade_id = get_serie_id_by_name(grade_name, getConnection)

        if subject_id is None or grade_id is None:
            print(f"Erro: Matéria '{subject_name}' ou Série '{grade_name}' não encontradas no banco.")
            return []

        # SQL base para selecionar os campos
        sql_select_base = f"""
            SELECT 
                {col_q_id} AS id, {col_q_enunciado} AS text, 
                {col_q_alt1} AS opt1, {col_q_alt2} AS opt2, 
                {col_q_alt3} AS opt3, {col_q_alt4} AS opt4,
                {col_q_idx_correta} AS correct_option, 
                {col_q_explicacao} AS hint,
                {col_q_fk_dificuldade} AS difficulty_id
            FROM {tbl_q}"""

        if difficulty_name != "Automatico":
            difficulty_id = get_difficulty_id_by_name(difficulty_name, getConnection)
            if difficulty_id is None:
                print(f"Erro: Dificuldade '{difficulty_name}' não encontrada.")
                return []

            print(f"DEBUG (data_manager): Buscando {TOTAL_QUESTIONS} questões de dificuldade ID: {difficulty_id}")
            
            sql_query = f"""
                {sql_select_base}
                WHERE {col_q_fk_materia} = %s AND {col_q_fk_serie} = %s AND {col_q_fk_dificuldade} = %s
                ORDER BY RAND() 
                LIMIT %s
            """
            cursor.execute(sql_query, (subject_id, grade_id, difficulty_id, TOTAL_QUESTIONS))
            results = cursor.fetchall()
            for row in results:
                quiz_questions.append(_format_db_row_to_question_dict(row))

        else: # difficulty_name == "Automatico"
            print(f"DEBUG (data_manager): Buscando questões no modo Automático.")
            
            difficulty_ids_map = {
                "Facil": get_difficulty_id_by_name("Facil", getConnection),
                "Medio": get_difficulty_id_by_name("Medio", getConnection),
                "Dificil": get_difficulty_id_by_name("Dificil", getConnection)
            }
            
            for diff_name, diff_id in difficulty_ids_map.items():
                if diff_id is not None:
                    print(f"DEBUG (data_manager): Buscando {CHECKPOINT_INTERVALS} questões de dificuldade '{diff_name}' (ID: {diff_id})")
                    sql_query_tier = f"""
                        {sql_select_base}
                        WHERE {col_q_fk_materia} = %s AND {col_q_fk_serie} = %s AND {col_q_fk_dificuldade} = %s
                        ORDER BY RAND() 
                        LIMIT %s
                    """
                    cursor.execute(sql_query_tier, (subject_id, grade_id, diff_id, CHECKPOINT_INTERVALS))
                    results_tier = cursor.fetchall()
                    for row in results_tier:
                        quiz_questions.append(_format_db_row_to_question_dict(row))
                else:
                    print(f"AVISO (data_manager): ID para dificuldade '{diff_name}' não encontrado. Pulando esta faixa.")

    except mysql.connector.Error as err:
        print(f"Erro de banco de dados (search_questions_for_quiz): {err}")
    except Exception as e:
        print(f"Erro inesperado (search_questions_for_quiz): {e}")
    finally:
        if cursor: cursor.close()
        if connection and connection.is_connected(): connection.close()
            
    return quiz_questions

def record_game_session(player_ra, game_materia_id, game_serie_id, game_score, connection):
   
    # Registra o resultado de uma sessão de jogo e atualiza os totais do aluno.

    connection = None
    cursor = None
    
    # Nomes das tabelas e colunas (confira com seu SQL)
    tbl_estatisticas = "estatisticas_jogos"
    tbl_alunos = "alunos"
    col_al_total_jogos = "total_jogos" # Nome da coluna que você confirmou
    col_al_pont_total = "pont_total"
    col_al_ra_where = "aluno_RA"
    
    try:
        # Usa a função que foi passada como argumento para obter a conexão
        connection = getConnection() 
        if not connection:
            return False, "Falha ao obter conexão com o banco de dados."
        
        cursor = connection.cursor()
        
        print("\n--- DEBUG (record_game_session): INICIANDO TRANSAÇÃO ---")
        
        # 1. Inserir na tabela estatisticas_jogos
        sql_insert_game = """
            INSERT INTO estatisticas_jogos 
            (aluno_RA, id_materia, id_serie, pontuacao_obtida_jogo)
            VALUES (%s, %s, %s, %s)
        """
        game_data = (player_ra, game_materia_id, game_serie_id, game_score)
        
        print(f"DEBUG: Executando INSERT em '{tbl_estatisticas}' com dados: {game_data}")
        cursor.execute(sql_insert_game, game_data)
        # O cursor.rowcount nos diz se a linha foi inserida com sucesso. Deve ser 1.
        print(f"  -> Linhas afetadas pelo INSERT: {cursor.rowcount}")

        # 2. Atualizar a tabela alunos
        sql_update_aluno = f"""
            UPDATE {tbl_alunos}
            SET 
                {col_al_pont_total} = {col_al_pont_total} + %s,
                {col_al_total_jogos} = {col_al_total_jogos} + 1
            WHERE {col_al_ra_where} = %s
        """
        aluno_update_data = (game_score, player_ra)

        print(f"DEBUG: Executando UPDATE em '{tbl_alunos}' com dados: {aluno_update_data}")
        cursor.execute(sql_update_aluno, aluno_update_data)
        # O cursor.rowcount aqui também deve ser 1.
        print(f"  -> Linhas afetadas pelo UPDATE: {cursor.rowcount}")

        print("DEBUG: Executando commit da transação...")
        connection.commit() # Confirma as duas operações no banco
        print("--- DEBUG: TRANSAÇÃO CONCLUÍDA COM SUCESSO ---")

        return True, "Resultado do jogo registrado com sucesso."

    except mysql.connector.Error as err:
        if connection:
            print(f"ERRO de banco de dados ({err.errno}): {err}. Fazendo rollback...")
            connection.rollback()
        return False, f"Erro ao registrar jogo: {err}"
    except Exception as e:
        if connection:
            print(f"ERRO inesperado: {e}. Fazendo rollback...")
            connection.rollback()
        return False, f"Erro inesperado ao registrar jogo: {e}"
    finally:
        if cursor: cursor.close()
        if connection and connection.is_connected(): connection.close()


def fetch_player_history_and_stats(player_ra, getConnection, limit=5):
    # Busca as estatísticas gerais de um aluno e seu histórico de jogos recentes.

    connection = None
    cursor = None
    
    try:
        connection = getConnection()
        if not connection:
            print("Erro (fetch_history): Falha ao obter conexão.")
            return None
            
        cursor = connection.cursor(dictionary=True) # Retorna resultados como dicionários

        # Busca estatísticas gerais da tabela alunos
        stats = {}
        sql_stats = "SELECT pont_total, total_jogos FROM alunos WHERE aluno_RA = %s"
        cursor.execute(sql_stats, (player_ra,))
        stats_result = cursor.fetchone()
        
        if stats_result:
            stats = {
                "total_score": stats_result.get("pont_total", 0),
                "total_games": stats_result.get("total_jogos", 0)
            }
        else:
            return None # Aluno não encontrado

        # 2. Buscar histórico de jogos recentes
        history = []
        sql_history = """
            SELECT 
                ej.data_jogo, 
                m.nome_materia, 
                s.nome_serie, 
                ej.pontuacao_obtida_jogo
            FROM 
                estatisticas_jogos ej
            JOIN 
                materias m ON ej.id_materia = m.id_materia
            JOIN
                serie s ON ej.id_serie = s.id_serie
            WHERE 
                ej.aluno_RA = %s 
            ORDER BY 
                ej.data_jogo DESC 
            LIMIT %s
        """
        cursor.execute(sql_history, (player_ra, limit))
        history_results = cursor.fetchall()

        for game in history_results:
            history.append({
                "date": game.get("data_jogo"), # Será um objeto datetime
                "subject": game.get("nome_materia"),
                "grade": game.get("nome_serie"),
                "score": game.get("pontuacao_obtida_jogo")
            })

        return {"summary_stats": stats, "recent_games": history}

    except mysql.connector.Error as err:
        print(f"Erro de banco de dados (fetch_history): {err}")
    except Exception as e:
        print(f"Erro inesperado (fetch_history): {e}")
    finally:
        if cursor: cursor.close()
        if connection and connection.is_connected(): connection.close()
    
    return None

def verify_user_credentials_from_db(input_ra, input_password, selected_user_type, getConnection):
    """
    Verifica as credenciais de login no banco para o tipo de usuário especificado.
    Retorna um dicionário com os dados do usuário em caso de sucesso.
    """
    connection = None
    cursor = None
    user_data = None

    # Nomes das tabelas e colunas (CONFIRA COM SEU SCRIPT SQL!)
    tbl_alunos = "alunos"; col_al_ra = "aluno_RA"; col_al_nome = "nome_aluno"; 
    col_al_senha = "senha_aluno"; col_al_turma = "turma"
    
    tbl_prof = "professores"; col_pr_ra = "prof_RA"; col_pr_nome = "nome_prof"; 
    col_pr_senha = "senha_prof"; col_pr_fk_materia = "id_materia" # FK em professores
    
    tbl_materias = "materias"; col_mat_id_pk = "id_materia"; col_mat_nome = "nome_materia"

    # ALERTA DE SEGURANÇA: Esta função compara senhas em texto plano.
    # É altamente recomendável usar hashing de senhas em aplicações reais.

    try:
        connection = getConnection()
        if not connection:
            print("Erro (verify_credentials): Falha ao obter conexão.")
            return None
        
        cursor = connection.cursor(dictionary=True) # Retorna resultados como dicionários

        if selected_user_type == "student":
            sql_query = f"SELECT {col_al_ra} AS RA, {col_al_nome} AS nome, {col_al_senha} AS senha_db, {col_al_turma} AS turma FROM {tbl_alunos} WHERE {col_al_ra} = %s"
            cursor.execute(sql_query, (input_ra,))
            db_result = cursor.fetchone()

            if db_result and db_result["senha_db"] == input_password:
                user_data = {
                    "RA": db_result["RA"],
                    "nome": db_result["nome"],
                    "tipo": "student",
                    "turma": db_result["turma"]
                }
        elif selected_user_type == "teacher":
            sql_query = f"""
                SELECT 
                    p.{col_pr_ra} AS RA, p.{col_pr_nome} AS nome, 
                    p.{col_pr_senha} AS senha_db, m.{col_mat_nome} AS materia 
                FROM {tbl_prof} p
                LEFT JOIN {tbl_materias} m ON p.{col_pr_fk_materia} = m.{col_mat_id_pk}
                WHERE p.{col_pr_ra} = %s
            """
            cursor.execute(sql_query, (input_ra,))
            db_result = cursor.fetchone()

            if db_result and db_result["senha_db"] == input_password:
                user_data = {
                    "RA": db_result["RA"],
                    "nome": db_result["nome"],
                    "tipo": "teacher",
                    "materia": db_result["materia"]
                }
        else:
            print(f"Erro (verify_credentials): Tipo de usuário desconhecido '{selected_user_type}'")
            return None 

    except mysql.connector.Error as err:
        print(f"Erro de banco de dados (verify_credentials): {err}")
    except Exception as e:
        print(f"Erro inesperado (verify_credentials): {e}")
    finally:
        if cursor: cursor.close()
        if connection and connection.is_connected(): connection.close()
            
    return user_data