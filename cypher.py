# cypher.py
import os
import secrets
import string
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

def genera_chiave(master_password: str, salt: bytes) -> bytes:
    """Deriva una chiave sicura a 256-bit dalla Master Password."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600_000,  # Standard elevato per rallentare attacchi bruteforce
    )
    return kdf.derive(master_password.encode())

def cifra_password(chiave: bytes, password_chiaro: str) -> bytes:
    """Cifra la password usando AES-GCM (criptazione autenticata con tag)."""
    iv = os.urandom(12)  # Genera un vettore di inizializzazione casuale
    encryptor = Cipher(
        algorithms.AES(chiave),
        modes.GCM(iv)
    ).encryptor()
    
    testo_cifrato = encryptor.update(password_chiaro.encode()) + encryptor.finalize()
    # Uniamo IV, Tag e Testo Cifrato in un unico blocco binario per il database
    return iv + encryptor.tag + testo_cifrato

def decifra_password(chiave: bytes, dati_cifrati: bytes) -> str:
    """Decifra il blocco binario estraendo IV, Tag e stringa cifrata."""
    iv = dati_cifrati[:12]
    tag = dati_cifrati[12:28]
    testo_cifrato = dati_cifrati[28:]
    
    decryptor = Cipher(
        algorithms.AES(chiave),
        modes.GCM(iv, tag)
    ).decryptor()
    
    return (decryptor.update(testo_cifrato) + decryptor.finalize()).decode()

def genera_password_casuale(lunghezza: int = 16) -> str:
    """Genera una password crittograficamente sicura utilizzando la libreria secrets."""
    if lunghezza < 8:
        lunghezza = 8
        
    alfabeto = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{}|;:,.<>?"
    # Assicuriamo la presenza di almeno un carattere per tipo per renderla robusta
    while True:
        password = "".join(secrets.choice(alfabeto) for _ in range(lunghezza))
        if (any(c.islower() for c in password)
                and any(c.isupper() for c in password)
                and any(c.isdigit() for c in password)
                and any(c in "!@#$%^&*()-_=+[]{}|;:,.<>?" for c in password)):
            return password