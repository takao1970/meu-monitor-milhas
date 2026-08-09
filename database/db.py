import hashlib
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATABASE_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS promocoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hash_url TEXT UNIQUE NOT NULL,
    url TEXT,
    titulo TEXT NOT NULL,
    programa_origem TEXT,
    programa_destino TEXT,
    bonus_max REAL,
    cpm_calculado REAL,
    data_descoberta TEXT NOT NULL,
    enviado_telegram BOOLEAN NOT NULL DEFAULT 0
);
"""

MIGRACAO_ADICIONAR_URL = "ALTER TABLE promocoes ADD COLUMN url TEXT;"


@contextmanager
def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_connection() as conn:
        conn.execute(SCHEMA)
        colunas = [row["name"] for row in conn.execute("PRAGMA table_info(promocoes)")]
        if "url" not in colunas:
            conn.execute(MIGRACAO_ADICIONAR_URL)


def gerar_hash_url(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


def promocao_ja_processada(url: str) -> bool:
    hash_url = gerar_hash_url(url)
    with get_connection() as conn:
        row = conn.execute(
            "SELECT 1 FROM promocoes WHERE hash_url = ?", (hash_url,)
        ).fetchone()
    return row is not None


def salvar_promocao(
    url: str,
    titulo: str,
    programa_origem: str = None,
    programa_destino: str = None,
    bonus_max: float = None,
    cpm_calculado: float = None,
    enviado_telegram: bool = False,
) -> int:
    hash_url = gerar_hash_url(url)
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO promocoes (
                hash_url, url, titulo, programa_origem, programa_destino,
                bonus_max, cpm_calculado, data_descoberta, enviado_telegram
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                hash_url,
                url,
                titulo,
                programa_origem,
                programa_destino,
                bonus_max,
                cpm_calculado,
                datetime.now(timezone.utc).isoformat(),
                enviado_telegram,
            ),
        )
        return cursor.lastrowid


def marcar_como_enviado(promocao_id: int):
    with get_connection() as conn:
        conn.execute(
            "UPDATE promocoes SET enviado_telegram = 1 WHERE id = ?",
            (promocao_id,),
        )


def listar_promocoes():
    """Retorna todas as promoções, com as viáveis (CPM calculado) primeiro
    em ordem crescente de CPM, seguidas das demais por data mais recente."""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT * FROM promocoes
            ORDER BY
                CASE WHEN cpm_calculado IS NULL THEN 1 ELSE 0 END,
                cpm_calculado ASC,
                data_descoberta DESC
            """
        ).fetchall()
        return [dict(row) for row in rows]


if __name__ == "__main__":
    init_db()
    print(f"Banco de dados inicializado em: {DATABASE_PATH}")
