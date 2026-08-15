import sqlite3
import os
from datetime import datetime, timedelta

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

DB_NAME = "turni_guardiania.db"
GIORNI_SETTIMANA = ["Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"]

TURNI_STANDARD = {
    "Mattina": {"start": "06:00", "end": "14:00"},
    "Pomeriggio": {"start": "14:00", "end": "22:00"},
    "Notte": {"start": "22:00", "end": "06:00"},
    "Riposo": {"start": "00:00", "end": "00:00"}
}

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS turni (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            tipo_turno TEXT NOT NULL,
            ora_inizio TEXT NOT NULL,
            ora_fine TEXT NOT NULL,
            ore_lavorate REAL NOT NULL,
            note TEXT
        )
    """)
    conn.commit()
    conn.close()

def normalizza_data(valore_data):
    val_str = str(valore_data).strip()
    if val_str.isdigit() and len(val_str) == 5:
        dt = datetime(1899, 12, 30) + timedelta(days=int(val_str))
        return dt.strftime("%Y-%m-%d")
    if " " in val_str:
        val_str = val_str.split(" ")[0]
    try:
        dt = datetime.strptime(val_str, "%Y-%m-%d")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return val_str[:10]

def get_giorno_settimana(data_str):
    try:
        dt = datetime.strptime(data_str, "%Y-%m-%d")
        return GIORNI_SETTIMANA[dt.weekday()]
    except ValueError:
        return "---"

def calcola_ore(ora_inizio_str, ora_fine_str):
    if ora_inizio_str == ora_fine_str:
        return 0.0
    fmt = "%H:%M"
    t_start = datetime.strptime(ora_inizio_str, fmt)
    t_end = datetime.strptime(ora_fine_str, fmt)
    if t_end <= t_start:
        t_end += timedelta(days=1)
    diff = (t_end - t_start).total_seconds() / 3600.0
    return round(diff, 2)

def salva_turno(data_str, tipo, ora_in, ora_fi, note=""):
    data_norm = normalizza_data(data_str)
    ore = calcola_ore(ora_in, ora_fi)
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO turni (data, tipo_turno, ora_inizio, ora_fine, ore_lavorate, note)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (data_norm, tipo, ora_in, ora_fi, ore, note))
    conn.commit()
    conn.close()

def carica_turni(mese_filtro=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    if mese_filtro:
        cursor.execute("SELECT id, data, tipo_turno, ora_inizio, ora_fine, ore_lavorate, note FROM turni WHERE data LIKE ? ORDER BY data ASC, ora_inizio ASC", (f"{mese_filtro}%",))
    else:
        cursor.execute("SELECT id, data, tipo_turno, ora_inizio, ora_fine, ore_lavorate, note FROM turni ORDER BY data ASC, ora_inizio ASC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def elimina_turno(turno_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM turni WHERE id = ?", (turno_id,))
    conn.commit()
    conn.close()