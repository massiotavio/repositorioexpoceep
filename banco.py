"""Banco de dados do ranking (SQLite, já vem com o Python: nada novo para instalar).
Arquivo: ranking.db, ao lado deste arquivo. Na primeira execução importa o ranking.json antigo."""
import json, os, sqlite3, threading

PASTA = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_DB = os.path.join(PASTA, "ranking.db")
ARQUIVO_JSON_ANTIGO = os.path.join(PASTA, "ranking.json")
_trava = threading.Lock()

def _conectar():
    con = sqlite3.connect(ARQUIVO_DB, timeout=10)
    con.row_factory = sqlite3.Row
    return con

def iniciar_banco():
    with _trava, _conectar() as con:
        con.execute("PRAGMA journal_mode=WAL")      # gravação segura contra queda de energia
        con.execute("""CREATE TABLE IF NOT EXISTS ranking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            grupo TEXT NOT NULL,
            tempo INTEGER NOT NULL CHECK (tempo >= 0),
            criado_em TEXT NOT NULL DEFAULT (datetime('now','localtime')))""")
        con.execute("CREATE INDEX IF NOT EXISTS idx_tempo ON ranking(tempo)")
        vazio = con.execute("SELECT COUNT(*) FROM ranking").fetchone()[0] == 0
        if vazio and os.path.exists(ARQUIVO_JSON_ANTIGO):   # importa o ranking.json antigo (uma vez só)
            try:
                with open(ARQUIVO_JSON_ANTIGO, encoding="utf-8") as f:
                    for r in json.load(f):
                        con.execute("INSERT OR IGNORE INTO ranking(id,grupo,tempo) VALUES(?,?,?)",
                                    (int(r["id"]), str(r["grupo"])[:24], int(r["tempo"])))
            except (OSError, ValueError, KeyError, TypeError):
                pass

def adicionar(grupo, tempo):
    """Salva um resultado e devolve o id novo."""
    with _trava, _conectar() as con:
        return con.execute("INSERT INTO ranking(grupo,tempo) VALUES(?,?)", (grupo, int(tempo))).lastrowid

def listar(limite=20):
    with _conectar() as con:
        linhas = con.execute("SELECT id,grupo,tempo FROM ranking ORDER BY tempo ASC, id ASC LIMIT ?", (limite,)).fetchall()
    return [dict(l) for l in linhas]

def apagar(id_):
    with _trava, _conectar() as con:
        return con.execute("DELETE FROM ranking WHERE id=?", (int(id_),)).rowcount

def limpar():
    with _trava, _conectar() as con:
        return con.execute("DELETE FROM ranking").rowcount
