import db_connector 

if not None:
    cursor = conn.cursor()

    cursor.execute("INSERT INTO usuarios (nome_usuario, senha_usuario, tipo_usuario) VALUES(%s, %s, %s);", 
                 ("Rafael Gamero", "1542", "Aluno"))

    conn.commit()
    print("Dados inseridos com sucesso.")

    cursor.execute("SELECT * FROM usuarios;")
    for row in cursor.fetchall():
        print(row)

    cursor.close()
conn.close()