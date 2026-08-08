import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

EMAIL_REMETENTE = os.getenv("EMAIL_REMETENTE", "")
EMAIL_SENHA_APP = os.getenv("EMAIL_SENHA_APP", "")
EMAIL_DESTINATARIO = os.getenv("EMAIL_DESTINATARIO", "")

CPM_MAXIMO_ALERTA = float(os.getenv("CPM_MAXIMO_ALERTA", "20.0"))

RSS_FEEDS = [url.strip() for url in os.getenv("RSS_FEEDS", "").split(",") if url.strip()]

DATABASE_PATH = os.getenv("DATABASE_PATH", "milhas_monitor.db")

CLAUDE_MODEL = "claude-haiku-4-5"
