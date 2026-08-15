# database.py
import sqlite3
import os

DB_NAME = "password_manager.db"

def inizializza_db() -> tuple:
    """
    Crea le tabelle se non esistono e recupera o genera il Master Salt e la Sentinella.
    Ritorna (master_salt, sentinel_cifrata).
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Crea la tabella config per il Salt
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS config (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            master_salt BLOB NOT NULL
        )
    ''')
    
    # Crea la tabella per la Sentinella di verifica della Master Password
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS verifica (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            sentinel_cifrata BLOB NOT NULL
        )
    ''')
    
    # Crea la tabella per memorizzare i dati degli account
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS credenziali (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            servizio TEXT NOT NULL UNIQUE,
            username TEXT NOT NULL,
            dati_cifrati BLOB NOT NULL
        )
    ''')
    
    # Recupera o genera il Salt
    cursor.execute("SELECT master_salt FROM config WHERE id = 1")
    row_salt = cursor.fetchone()
    
    if row_salt is None:
        master_salt = os.urandom(16)
        cursor.execute("INSERT INTO config (id, master_salt) VALUES (1, ?)", (master_salt,))
        conn.commit()
        sentinel_cifrata = None
    else:
        master_salt = row_salt[0]
        # Recupera la sentinella cifrata se esiste
        cursor.execute("SELECT sentinel_cifrata FROM verifica WHERE id = 1")
        row_sentinel = cursor.fetchone()
        sentinel_cifrata = row_sentinel[0] if row_sentinel else None
        
    conn.close()
    return master_salt, sentinel_cifrata

def salva_sentinella(blocco_cifrato: bytes):
    """Salva il dato di test cifrato (sentinella) per verificare gli accessi futuri."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO verifica (id, sentinel_cifrata)
        VALUES (1, ?)
    ''', (blocco_cifrato,))
    conn.commit()
    conn.close()

def salva_credenziale(servizio: str, username: str, dati_cifrati: bytes):
    """Inserisce o aggiorna una credenziale nel database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT OR REPLACE INTO credenziali (servizio, username, dati_cifrati)
            VALUES (?, ?, ?)
        ''', (servizio.lower(), username, dati_cifrati))
        conn.commit()
        print(f"[✓] Credenziale per '{servizio}' salvata con successo.")
    except sqlite3.Error as e:
        print(f"[-] Errore SQLite: {e}")
    finally:
        conn.close()

def recupera_credenziale(servizio: str) -> tuple:
    """Trova una credenziale in base al nome del servizio."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT username, dati_cifrati FROM credenziali WHERE servizio = ?
    ''', (servizio.lower(),))
    row = cursor.fetchone()
    conn.close()
    return row