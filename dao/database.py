import os
import pg8000
from dotenv import load_dotenv

load_dotenv() # Carrega as variáveis de ambiente do arquivo .env

def get_db_connection():
    try:
        connection = pg8000.connect(
            host=os.environ.get('DB_HOST'),
            database=os.environ.get('DB_NAME'),
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASSWORD'),
            port=int(os.environ.get('DB_PORT'))
        )
        return connection
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

def execute_query(sql, params=None, fetch=False):
    connection = get_db_connection()
    if connection is None:
        return None
    response = None
    try:
        cursor = connection.cursor()
        cursor.execute(sql, params) if params else cursor.execute(sql)
        if fetch:
            results = cursor.fetchall()
            colunas = [col[0] for col in cursor.description]
            # Monta a resposta como uma lista de dicionários, onde cada dicionário representa uma linha do resultado
            response = [dict(zip(colunas, row)) for row in results]
        else:
            connection.commit()
            response = True
        cursor.close()
    except Exception as e:
        print(f"Erro ao executar a consulta: {e}"); connection.rollback()
        return None
    finally:
        connection.close()
    return response


def create_chamado(cliente, descricao, prioridade):
    sql = """
        INSERT INTO chamados (cliente, descricao, prioridade, status, statusfinal)
        VALUES (%s, %s, %s, %s, %s)
    """
    return execute_query(sql, (cliente, descricao, prioridade, 'Aberto', False))


def list_chamados():
    sql = """
        SELECT id, cliente, descricao, prioridade, status, statusfinal
        FROM chamados
        ORDER BY id DESC
    """
    return execute_query(sql, fetch=True)


def update_chamado_status(chamado_id, status, statusfinal):
    sql = """
        UPDATE chamados
        SET status = %s, statusfinal = %s
        WHERE id = %s
    """
    return execute_query(sql, (status, statusfinal, chamado_id))


def get_usuario_by_nome(nome):
    sql = """
        SELECT id, nome, senha
        FROM usuarios
        WHERE nome = %s
        LIMIT 1
    """
    results = execute_query(sql, (nome,), fetch=True)
    return results[0] if results else None