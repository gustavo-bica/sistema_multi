import os
import ssl
import socket
import pymysql
from supabase import create_client
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

def limpar_env(var_name, default=""):
    val = os.getenv(var_name, default)
    if val:
        return val.strip().strip('"').strip("'")
    return default

def get_db_connection():
    # SSL totalmente permissivo para contornar a verificação de tráfego
    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE

    host = limpar_env("MYSQL_HOST")
    user = limpar_env("MYSQL_USER")
    password = limpar_env("MYSQL_PASSWORD")
    database = limpar_env("MYSQL_DB")
    port = int(limpar_env("MYSQL_PORT", "27933"))

    # Configuração de socket para burlar o reset imediato [WinError 10054]
    try:
        sock = socket.create_connection((host, port), timeout=10)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        
        return pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port,
            ssl=ssl_ctx,
            sock=sock,
            connect_timeout=15,
            cursorclass=pymysql.cursors.DictCursor
        )
    except Exception:
        # Fallback de conexão direta sem socket pré-criado
        return pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port,
            ssl=ssl_ctx,
            connect_timeout=20,
            cursorclass=pymysql.cursors.DictCursor
        )

def get_supabase_client():
    url = limpar_env("SUPABASE_URL")
    key = limpar_env("SUPABASE_KEY")
    return create_client(url, key)