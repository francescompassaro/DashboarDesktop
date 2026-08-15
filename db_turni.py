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
PAGA_BASE = 7.50

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



def calcola_compenso_turno(data_str, tipo_turno, ora_in, ora_fi, ore, note=""):
    """
    Calcola il compenso economico per un turno applicando le maggiorazioni:
    - Paga base: 7.50 €/h
    - Straordinario diurno: +20% (9.00 €/h)
    - Notturno ordinario (22-06): +30% (9.75 €/h)
    - Notturno straordinario (22-06): +40% (10.50 €/h)
    - Festivo / Domenicale: +40% (10.50 €/h)
    """
    if ore <= 0:
        return 0.0

    dt = datetime.strptime(data_str, "%Y-%m-%d")
    is_domenica_o_festivo = dt.weekday() == 6 or "festivo" in note.lower()
    is_notturno = (ora_in == "22:00" and ora_fi == "06:00") or "notte" in tipo_turno.lower()
    is_straordinario = "straordinario" in note.lower() or "straordinario" in tipo_turno.lower()

    # Calcolo della tariffa oraria applicata
    maggiorazione = 0.0

    if is_domenica_o_festivo:
        maggiorazione = 0.40  # +40% Domenicale/Festivo
    elif is_notturno:
        if is_straordinario:
            maggiorazione = 0.40  # +40% Notturno Straordinario
        else:
            maggiorazione = 0.30  # +30% Notturno Ordinario
    elif is_straordinario:
        maggiorazione = 0.20  # +20% Straordinario Diurno

    paga_oraria_effettiva = PAGA_BASE * (1 + maggiorazione)
    return round(ore * paga_oraria_effettiva, 2)