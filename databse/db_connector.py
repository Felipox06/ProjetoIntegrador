import os
import mysql.connector
from pathlib import Path
from dotenv import load_dotenv


# Carrega configurações de .env e gerencia conexões MySQL.
dotenv_path = Path(__file__).resolve().parents[1] / '.env'
load_dotenv(dotenv_path=dotenv_path)




HOST = os.getenv('HOST')
PORT = os.getenv('PORT')
MYSQL_DATABASE = os.getenv('DATABASE')
MYSQL_USERNAME = os.getenv('USER')
MYSQL_PASSWORD = os.getenv('DB_PASSWORD')


# Estas impressões são para fins de depuração e podem ser removidas em produção.
print(f"HOST={HOST}")
print(f"PORT={PORT}")
print(f"USER={MYSQL_USERNAME}")
print(f"PASSWORD={MYSQL_PASSWORD}")
print(f"DATABASE={MYSQL_DATABASE}")


# Estabelece e retorna uma conexão com o banco de dados MySQL.
def getConnection():
    return mysql.connector.connect(
        host=os.getenv('HOST'),
        port=int(os.getenv('PORT')),
        user=os.getenv('USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DATABASE'),
        ssl_ca=os.getenv('SSL_CA')
    )
