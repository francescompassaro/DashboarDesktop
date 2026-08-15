import customtkinter as ctk
from datetime import datetime
import db_turni

class TurniFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        db_turni.init_db()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- PANNELLO SINISTRO: FORM INSERIMENTO ---
        self.form_frame = ctk.CTkFrame(self, width=280)
        self.form_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(self.form_frame, text="Nuovo Turno", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)

        # Data
        ctk.CTkLabel(self.form_frame, text="Data (AAAA-MM-GG):").pack(anchor="w", padx=15)
        self.entry_data = ctk.CTkEntry(self.form_frame)
        self.entry_data.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_data.pack(fill="x", padx=15, pady=(0, 10))

        # Preset Turno
        ctk.CTkLabel(self.form_frame, text="Tipo Turno:").pack(anchor="w", padx=15)
        self.combo_tipo = ctk.CTkOptionMenu(
            self.form_frame, 
            values=["Mattina (06-14)", "Pomeriggio (14-22)", "Notte (22-06)", "Riposo", "Personalizzato"],
            command=self.on_tipo_change
        )
        self.combo_tipo.pack(fill="x", padx=15, pady=(0, 10))

        # Orari Custom
        self.entry_ora_in = ctk.CTkEntry(self.form_frame, placeholder_text="Ora Inizio (06:00)")
        self.entry_ora_in.pack(fill="x", padx=15, pady=5)
        self.entry_ora_fi = ctk.CTkEntry(self.form_frame, placeholder_text="Ora Fine (14:00)")
        self.entry_ora_fi.pack(fill="x", padx=15, pady=5)

        # Note
        self.entry_note = ctk.CTkEntry(self.form_frame, placeholder_text="Note opzionali")
        self.entry_note.pack(fill="x", padx=15, pady=10)

        # Bottone Salva
        btn_salva = ctk.CTkButton(self.form_frame, text="Salva Turno", command=self.aggiungi_turno, fg_color="green")
        btn_salva.pack(fill="x", padx=15, pady=10)

        # Statistiche sintetiche
        self.lbl_stats = ctk.CTkLabel(self.form_frame, text="", font=ctk.CTkFont(size=12))
        self.lbl_stats.pack(pady=10)

        # --- PANNELLO DESTRO: TABELLA E FILTRI ---
        self.list_frame = ctk.CTkFrame(self)
        self.list_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.list_frame.grid_rowconfigure(1, weight=1)
        self.list_frame.grid_columnconfigure(0, weight=1)

        # Filtro Mese
        self.filter_frame = ctk.CTkFrame(self.list_frame)
        self.filter_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(self.filter_frame, text="Filtro Mese (AAAA-MM):").pack(side="left", padx=10)
        self.entry_filtro = ctk.CTkEntry(self.filter_frame, width=120)
        self.entry_filtro.insert(0, datetime.now().strftime("%Y-%m"))
        self.entry_filtro.pack(side="left", padx=5)
        
        btn_filtra = ctk.CTkButton(self.filter_frame, text="Filtra", width=80, command=self.aggiorna_lista)
        btn_filtra.pack(side="left", padx=5)

        btn_tutti = ctk.CTkButton(self.filter_frame, text="Tutti", width=60, command=self.mostra_tutti)
        btn_tutti.pack(side="left", padx=5)

        # Area Scrollabile
        self.scrollable_list = ctk.CTkScrollableFrame(self.list_frame)
        self.scrollable_list.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Impostazione default form e primo caricamento
        self.on_tipo_change("Mattina (06-14)")
        self.aggiorna_lista()

    def on_tipo_change(self, choice):
        if "Mattina" in choice:
            self.entry_ora_in.delete(0, 'end'); self.entry_ora_in.insert(0, "06:00")
            self.entry_ora_fi.delete(0, 'end'); self.entry_ora_fi.insert(0, "14:00")
        elif "Pomeriggio" in choice:
            self.entry_ora_in.delete(0, 'end'); self.entry_ora_in.insert(0, "14:00")
            self.entry_ora_fi.delete(0, 'end'); self.entry_ora_fi.insert(0, "22:00")
        elif "Notte" in choice:
            self.entry_ora_in.delete(0, 'end'); self.entry_ora_in.insert(0, "22:00")
            self.entry_ora_fi.delete(0, 'end'); self.entry_ora_fi.insert(0, "06:00")
        elif "Riposo" in choice:
            self.entry_ora_in.delete(0, 'end'); self.entry_ora_in.insert(0, "00:00")
            self.entry_ora_fi.delete(0, 'end'); self.entry_ora_fi.insert(0, "00:00")

    def aggiungi_turno(self):
        data = self.entry_data.get()
        tipo = self.combo_tipo.get()
        ora_in = self.entry_ora_in.get()
        ora_fi = self.entry_ora_fi.get()
        note = self.entry_note.get()

        if data and ora_in and ora_fi:
            db_turni.salva_turno(data, tipo, ora_in, ora_fi, note)
            self.entry_note.delete(0, 'end')
            self.aggiorna_lista()

    def mostra_tutti(self):
        self.entry_filtro.delete(0, 'end')
        self.aggiorna_lista()

    def aggiorna_lista(self):
        for w in self.scrollable_list.winfo_children():
            w.destroy()

        mese = self.entry_filtro.get().strip() or None
        rows = db_turni.carica_turni(mese)

        tot_ore = 0.0
        tot_turni = 0
        tot_riposi = 0
        tot_compenso = 0.0

        for r in rows:
            t_id, dt, tipo, o_in, o_fi, ore, note = r
            giorno_sett = db_turni.get_giorno_settimana(dt)
            
            # Calcolo del compenso per il singolo turno
            compenso_turno = db_turni.calcola_compenso_turno(dt, tipo, o_in, o_fi, ore, note)
            
            card = ctk.CTkFrame(self.scrollable_list)
            card.pack(fill="x", padx=5, pady=3)

            orario = "RIPOSO" if ore == 0 else f"{o_in}-{o_fi}"
            txt = f"{giorno_sett} {dt} | {orario} ({ore}h)"
            if ore > 0:
                txt += f" - {compenso_turno:.2f} €"
            txt += f" | {tipo}"
            if note: txt += f" [{note}]"

            lbl = ctk.CTkLabel(card, text=txt, anchor="w")
            lbl.pack(side="left", padx=10, fill="x", expand=True)

            btn_del = ctk.CTkButton(card, text="X", width=30, fg_color="red", command=lambda id_=t_id: self.elimina(id_))
            btn_del.pack(side="right", padx=5)

            if ore > 0:
                tot_ore += ore
                tot_turni += 1
                tot_compenso += compenso_turno
            else:
                tot_riposi += 1

        # Aggiornamento del riepilogo in basso nel pannello sinistro
        self.lbl_stats.configure(
            text=f"Turni: {tot_turni} | Riposi: {tot_riposi}\n"
                 f"Ore Totali: {tot_ore:.1f} h\n"
                 f"Stima Compenso: {tot_compenso:.2f} €"
        )