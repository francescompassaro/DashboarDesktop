import customtkinter as ctk
from tkinter import messagebox
import cypher
import database

class PasswordManagerFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        # Inizializzazione DB e recupero Salt e Sentinella
        self.salt, self.sentinel_cifrata = database.inizializza_db()
        self.chiave_derivata = None
        self.SENTINEL_TEXT = "sentinella_di_verifica_sistema_sicuro"

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Mostra la schermata di Login/Configurazione all'avvio
        self.build_login_ui()

    # --- SCHERMATA DI SBLOCCO / CONFIGURAZIONE ---
    def build_login_ui(self):
        self.clear_frame()

        self.login_card = ctk.CTkFrame(self, width=400)
        self.login_card.place(relx=0.5, rely=0.5, anchor="center")

        titolo = "Configurazione Master Password" if self.sentinel_cifrata is None else "Sblocco Vault Password"
        ctk.CTkLabel(self.login_card, text=titolo, font=ctk.CTkFont(size=20, weight="bold")).pack(padx=20, pady=(20, 10))

        if self.sentinel_cifrata is None:
            ctk.CTkLabel(self.login_card, text="Imposta una Master Password forte.\nSe la perdi, le tue password saranno perse!", text_color="orange").pack(padx=20, pady=5)
            
            self.entry_mp1 = ctk.CTkEntry(self.login_card, show="*", placeholder_text="Master Password", width=250)
            self.entry_mp1.pack(padx=20, pady=5)

            self.entry_mp2 = ctk.CTkEntry(self.login_card, show="*", placeholder_text="Conferma Master Password", width=250)
            self.entry_mp2.pack(padx=20, pady=(5, 15))

            btn_login = ctk.CTkButton(self.login_card, text="Inizializza Vault", command=self.inizializza_vault)
            btn_login.pack(padx=20, pady=(0, 20))
        else:
            ctk.CTkLabel(self.login_card, text="Inserisci la tua Master Password per accedere:").pack(padx=20, pady=5)

            self.entry_mp1 = ctk.CTkEntry(self.login_card, show="*", placeholder_text="Master Password", width=250)
            self.entry_mp1.pack(padx=20, pady=(5, 15))
            self.entry_mp1.bind("<Return>", lambda event: self.sblocca_vault())

            btn_login = ctk.CTkButton(self.login_card, text="Sblocca", command=self.sblocca_vault)
            btn_login.pack(padx=20, pady=(0, 20))

    def inizializza_vault(self):
        mp1 = self.entry_mp1.get()
        mp2 = self.entry_mp2.get()

        if not mp1:
            messagebox.showwarning("Attenzione", "La password non può essere vuota.")
            return
        if mp1 != mp2:
            messagebox.showerror("Errore", "Le password non coincidono.")
            return

        self.chiave_derivata = cypher.genera_chiave(mp1, self.salt)
        sentinel_nuova = cypher.cifra_password(self.chiave_derivata, self.SENTINEL_TEXT)
        database.salva_sentinella(sentinel_nuova)
        
        self.build_dashboard_ui()

    def sblocca_vault(self):
        mp = self.entry_mp1.get()
        if not mp:
            return

        chiave_tentativa = cypher.genera_chiave(mp, self.salt)
        try:
            testo_sbloccato = cypher.decifra_password(chiave_tentativa, self.sentinel_cifrata)
            if testo_sbloccato == self.SENTINEL_TEXT:
                self.chiave_derivata = chiave_tentativa
                self.build_dashboard_ui()
                return
        except Exception:
            pass
        
        messagebox.showerror("Accesso Negato", "Master Password errata!")

    # --- SCHERMATA PRINCIPALE DASHBOARD ---
    def build_dashboard_ui(self):
        self.clear_frame()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # PANNELLO SINISTRO: INSERIMENTO E GENERATORE
        self.left_frame = ctk.CTkFrame(self, width=300)
        self.left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(self.left_frame, text="Aggiungi Credenziale", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)

        self.entry_servizio = ctk.CTkEntry(self.left_frame, placeholder_text="Servizio (es. GitHub)")
        self.entry_servizio.pack(fill="x", padx=15, pady=5)

        self.entry_username = ctk.CTkEntry(self.left_frame, placeholder_text="Username / Email")
        self.entry_username.pack(fill="x", padx=15, pady=5)

        self.entry_password = ctk.CTkEntry(self.left_frame, placeholder_text="Password", show="*")
        self.entry_password.pack(fill="x", padx=15, pady=5)

        btn_gen = ctk.CTkButton(self.left_frame, text="⚡ Genera Password Forte", fg_color="purple", command=self.genera_e_imposta_pass)
        btn_gen.pack(fill="x", padx=15, pady=5)

        btn_salva = ctk.CTkButton(self.left_frame, text="Salva Credenziale", fg_color="green", command=self.salva_credenziale)
        btn_salva.pack(fill="x", padx=15, pady=(15, 10))

        # PANNELLO DESTRO: RICERCA E LISTA CREDENZIALI
        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.right_frame.grid_rowconfigure(1, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        # BARRA DI RICERCA
        self.search_frame = ctk.CTkFrame(self.right_frame)
        self.search_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.entry_search = ctk.CTkEntry(self.search_frame, placeholder_text="Cerca servizio...")
        self.entry_search.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        self.entry_search.bind("<KeyRelease>", lambda event: self.carica_lista())

        # LISTA SCROLLABILE
        self.scroll_list = ctk.CTkScrollableFrame(self.right_frame)
        self.scroll_list.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.carica_lista()

    def genera_e_imposta_pass(self):
        nuova_pass = cypher.genera_password_casuale(16)
        self.entry_password.delete(0, 'end')
        self.entry_password.insert(0, nuova_pass)

    def salva_credenziale(self):
        servizio = self.entry_servizio.get().strip()
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()

        if not servizio or not username or not password:
            messagebox.showwarning("Attenzione", "Compila tutti i campi!")
            return

        dati_cifrati = cypher.cifra_password(self.chiave_derivata, password)
        database.salva_credenziale(servizio, username, dati_cifrati)

        self.entry_servizio.delete(0, 'end')
        self.entry_username.delete(0, 'end')
        self.entry_password.delete(0, 'end')
        self.carica_lista()

    def carica_lista(self):
        for w in self.scroll_list.winfo_children():
            w.destroy()

        query_filtro = self.entry_search.get().strip().lower() if hasattr(self, 'entry_search') else ""

        # Query diretta al DB per recuperare tutti i servizi
        import sqlite3
        conn = sqlite3.connect(database.DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT servizio, username, dati_cifrati FROM credenziali ORDER BY servizio ASC")
        rows = cursor.fetchall()
        conn.close()

        for servizio, username, dati_cifrati in rows:
            if query_filtro and query_filtro not in servizio.lower():
                continue

            card = ctk.CTkFrame(self.scroll_list)
            card.pack(fill="x", padx=5, pady=3)

            lbl_info = ctk.CTkLabel(card, text=f"{servizio.capitalize()} ({username})", font=ctk.CTkFont(weight="bold"))
            lbl_info.pack(side="left", padx=10)

            # Bottoni Azione
            btn_copy = ctk.CTkButton(
                card, text="📋 Copia Pass", width=90, 
                command=lambda d=dati_cifrati: self.copia_password(d)
            )
            btn_copy.pack(side="right", padx=5, pady=5)

            btn_show = ctk.CTkButton(
                card, text="👁️ Mostra", width=70, fg_color="gray",
                command=lambda s=servizio, u=username, d=dati_cifrati: self.mostra_password(s, u, d)
            )
            btn_show.pack(side="right", padx=5, pady=5)

    def copia_password(self, dati_cifrati):
        try:
            pwd = cypher.decifra_password(self.chiave_derivata, dati_cifrati)
            self.clipboard_clear()
            self.clipboard_append(pwd)
            messagebox.showinfo("Successo", "Password copiata negli appunti!")
        except Exception:
            messagebox.showerror("Errore", "Impossibile decifrare la password.")

    def mostra_password(self, servizio, username, dati_cifrati):
        try:
            pwd = cypher.decifra_password(self.chiave_derivata, dati_cifrati)
            messagebox.showinfo(f"{servizio.capitalize()}", f"Username: {username}\nPassword: {pwd}")
        except Exception:
            messagebox.showerror("Errore", "Impossibile decifrare la password.")

    def clear_frame(self):
        for w in self.winfo_children():
            w.destroy()