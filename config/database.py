import os
import streamlit as st
from supabase import create_client
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env (ambiente local)
load_dotenv()

def limpar_env(var_name, default=""):
    val = os.getenv(var_name)
    if not val:
        try:
            val = st.secrets.get(var_name, default)
        except Exception:
            val = default
    if val:
        return str(val).strip().strip('"').strip("'")
    return default

def get_supabase_client():
    url = limpar_env("SUPABASE_URL")
    key = limpar_env("SUPABASE_KEY")
    return create_client(url, key)