import sqlite3

DB_NAME = "todo_projects.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS task (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titolo TEXT NOT NULL,
            categoria TEXT CHECK(categoria IN ('To-Do', 'Idea Progetto')),
            priorita TEXT CHECK(priorita IN ('Alta', 'Media', 'Bassa')),
            stato TEXT CHECK(stato IN ('Da fare', 'In corso', 'Completato')),
            descrizione TEXT,
            data_creazione DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def salva_task(titolo, categoria, priorita, stato, descrizione=""):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO task (titolo, categoria, priorita, stato, descrizione)
        VALUES (?, ?, ?, ?, ?)
    """, (titolo, categoria, priorita, stato, descrizione))
    conn.commit()
    conn.close()

def aggiorna_task_completo(task_id, titolo, categoria, priorita, stato, descrizione):
    """Aggiorna tutti i parametri di un task esistente."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE task 
        SET titolo = ?, categoria = ?, priorita = ?, stato = ?, descrizione = ?
        WHERE id = ?
    """, (titolo, categoria, priorita, stato, descrizione, task_id))
    conn.commit()
    conn.close()

def carica_task(categoria_filtro=None, priorita_filtro=None, stato_filtro=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    query = "SELECT id, titolo, categoria, priorita, stato, descrizione FROM task WHERE 1=1"
    params = []

    if categoria_filtro and categoria_filtro != "Tutti":
        query += " AND categoria = ?"
        params.append(categoria_filtro)

    if priorita_filtro and priorita_filtro != "Tutte":
        query += " AND priorita = ?"
        params.append(priorita_filtro)

    if stato_filtro and stato_filtro != "Tutti":
        query += " AND stato = ?"
        params.append(stato_filtro)

    query += " ORDER BY CASE priorita WHEN 'Alta' THEN 1 WHEN 'Media' THEN 2 WHEN 'Bassa' THEN 3 END, id DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows

def aggiorna_stato_task(task_id, nuovo_stato):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE task SET stato = ? WHERE id = ?", (nuovo_stato, task_id))
    conn.commit()
    conn.close()

def elimina_task(task_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM task WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()