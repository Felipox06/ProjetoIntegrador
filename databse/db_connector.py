import os
import mysql.connector
from pathlib import Path
from dotenv import load_dotenv

dotenv_path = Path(__file__).resolve().parents[1] / '.env'
load_dotenv(dotenv_path=dotenv_path)


HOST = os.getenv('HOST')
PORT = os.getenv('PORT')
MYSQL_DATABASE = os.getenv('DATABASE')
MYSQL_USERNAME = os.getenv('USER')
MYSQL_PASSWORD = os.getenv('DB_PASSWORD')

print(f"HOST={HOST}")
print(f"PORT={PORT}")
print(f"USER={MYSQL_USERNAME}")
print(f"PASSWORD={MYSQL_PASSWORD}")
print(f"DATABASE={MYSQL_DATABASE}")


def getConnection():
    try: 
        conn = mysql.connector.connect(
            host=HOST,
            port=int(PORT),
            user=MYSQL_USERNAME, 
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )
        print('Conexão bem sucedida!!')
        return conn
        
    except mysql.connector.Error as err:
        print(f'Erro ao conectar ao banco de dados: {err}')


