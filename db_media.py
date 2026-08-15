import sqlite3

DB_NAME = "media_tracker.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS media (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titolo TEXT NOT NULL,
            tipo TEXT CHECK(tipo IN ('Anime', 'Manga')),
            stato TEXT CHECK(stato IN ('In corso', 'Completato', 'Pianificato', 'In pausa')),
            progresso INTEGER DEFAULT 0,
            totale INTEGER DEFAULT 0,
            voto INTEGER DEFAULT 0,
            note TEXT,
            url TEXT
        )
    """)
    
    # Migrazione automatica se le colonne non esistono nei DB già creati
    cursor.execute("PRAGMA table_info(media)")
    columns = [col[1] for col in cursor.fetchall()]
    if "totale" not in columns:
        cursor.execute("ALTER TABLE media ADD COLUMN totale INTEGER DEFAULT 0")
    if "url" not in columns:
        cursor.execute("ALTER TABLE media ADD COLUMN url TEXT DEFAULT ''")

    conn.commit()
    conn.close()

def salva_media(titolo, tipo, stato, progresso=0, totale=0, voto=0, note="", url=""):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO media (titolo, tipo, stato, progresso, totale, voto, note, url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (titolo, tipo, stato, int(progresso), int(totale), int(voto), note, url))
    conn.commit()
    conn.close()

def aggiorna_media_completo(media_id, titolo, tipo, stato, progresso, totale, voto, note, url):
    """Aggiorna tutti i parametri di una scheda compresi note e URL."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE media 
        SET titolo = ?, tipo = ?, stato = ?, progresso = ?, totale = ?, voto = ?, note = ?, url = ?
        WHERE id = ?
    """, (titolo, tipo, stato, int(progresso), int(totale), int(voto), note, url, media_id))
    conn.commit()
    conn.close()

def carica_media(tipo_filtro=None, stato_filtro=None, ricerca=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    query = "SELECT id, titolo, tipo, stato, progresso, totale, voto, note, url FROM media WHERE 1=1"
    params = []

    if tipo_filtro and tipo_filtro != "Tutti":
        query += " AND tipo = ?"
        params.append(tipo_filtro)

    if stato_filtro and stato_filtro != "Tutti":
        query += " AND stato = ?"
        params.append(stato_filtro)

    if ricerca:
        query += " AND titolo LIKE ?"
        params.append(f"%{ricerca}%")

    query += " ORDER BY titolo ASC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows

def aggiorna_progresso(media_id, delta):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT progresso, totale FROM media WHERE id = ?", (media_id,))
    row = cursor.fetchone()
    if row:
        prog, tot = row
        nuovo_prog = max(0, prog + delta)
        if tot > 0 and nuovo_prog > tot:
            nuovo_prog = tot
        cursor.execute("UPDATE media SET progresso = ? WHERE id = ?", (nuovo_prog, media_id))
    conn.commit()
    conn.close()

def elimina_media(media_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM media WHERE id = ?", (media_id,))
    conn.commit()
    conn.close()