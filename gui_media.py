import customtkinter as ctk
from tkinter import messagebox
import webbrowser
import db_media

class DettagliMediaWindow(ctk.CTkToplevel):
    """Finestra popup/scheda per modificare i dettagli di un singolo Anime/Manga."""
    def __init__(self, master, media_data, on_save_callback):
        super().__init__(master)
        self.media_id, titolo, tipo, stato, progresso, totale, voto, note, url = media_data
        self.on_save_callback = on_save_callback

        self.title(f"Scheda: {titolo}")
        self.geometry("480x630")
        self.resizable(False, False)

        self.transient(master)
        self.grab_set()

        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(frame, text="Dettagli Opera", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(0, 10))

        # Titolo
        ctk.CTkLabel(frame, text="Titolo:").pack(anchor="w", padx=10)
        self.entry_titolo = ctk.CTkEntry(frame)
        self.entry_titolo.insert(0, titolo)
        self.entry_titolo.pack(fill="x", padx=10, pady=(0, 10))

        # Link URL Lettura / Visione
        ctk.CTkLabel(frame, text="Link URL (Sito di Lettura / Streaming):").pack(anchor="w", padx=10)
        self.entry_url = ctk.CTkEntry(frame, placeholder_text="https://...")
        if url:
            self.entry_url.insert(0, url)
        self.entry_url.pack(fill="x", padx=10, pady=(0, 10))

        # Tipo e Stato
        row1 = ctk.CTkFrame(frame, fg_color="transparent")
        row1.pack(fill="x", padx=10, pady=(0, 10))

        col_tipo = ctk.CTkFrame(row1, fg_color="transparent")
        col_tipo.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(col_tipo, text="Tipo:").pack(anchor="w")
        self.combo_tipo = ctk.CTkOptionMenu(col_tipo, values=["Manga", "Anime"])
        self.combo_tipo.set(tipo)
        self.combo_tipo.pack(fill="x")

        col_stato = ctk.CTkFrame(row1, fg_color="transparent")
        col_stato.pack(side="right", fill="x", expand=True, padx=(5, 0))
        ctk.CTkLabel(col_stato, text="Stato:").pack(anchor="w")
        self.combo_stato = ctk.CTkOptionMenu(col_stato, values=["In corso", "Pianificato", "Completato", "In pausa"])
        self.combo_stato.set(stato)
        self.combo_stato.pack(fill="x")

        # Progresso vs Totale vs Voto
        row2 = ctk.CTkFrame(frame, fg_color="transparent")
        row2.pack(fill="x", padx=10, pady=(0, 10))

        col_prog = ctk.CTkFrame(row2, fg_color="transparent")
        col_prog.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(col_prog, text="Progresso Corrente:").pack(anchor="w")
        self.entry_progresso = ctk.CTkEntry(col_prog)
        self.entry_progresso.insert(0, str(progresso))
        self.entry_progresso.pack(fill="x")

        col_tot = ctk.CTkFrame(row2, fg_color="transparent")
        col_tot.pack(side="left", fill="x", expand=True, padx=(5, 5))
        ctk.CTkLabel(col_tot, text="Totale Cap./Ep.:").pack(anchor="w")
        self.entry_totale = ctk.CTkEntry(col_tot, placeholder_text="0 = In corso")
        self.entry_totale.insert(0, str(totale) if totale > 0 else "")
        self.entry_totale.pack(fill="x")

        col_voto = ctk.CTkFrame(row2, fg_color="transparent")
        col_voto.pack(side="right", fill="x", expand=True, padx=(5, 0))
        ctk.CTkLabel(col_voto, text="Voto (0-10):").pack(anchor="w")
        self.combo_voto = ctk.CTkOptionMenu(col_voto, values=[str(i) for i in range(11)])
        self.combo_voto.set(str(voto))
        self.combo_voto.pack(fill="x")

        # Box Note Multilinea
        ctk.CTkLabel(frame, text="Note & Impressioni:").pack(anchor="w", padx=10)
        self.txt_note = ctk.CTkTextbox(frame, height=100)
        if note:
            self.txt_note.insert("1.0", note)
        self.txt_note.pack(fill="both", expand=True, padx=10, pady=(0, 15))

        # Bottoni Salva / Annulla
        btn_box = ctk.CTkFrame(frame, fg_color="transparent")
        btn_box.pack(fill="x", padx=10)

        btn_salva = ctk.CTkButton(btn_box, text="Salva Modifiche", fg_color="green", command=self.salva)
        btn_salva.pack(side="right", padx=5)

        btn_annulla = ctk.CTkButton(btn_box, text="Annulla", fg_color="gray", command=self.destroy)
        btn_annulla.pack(side="right", padx=5)

    def salva(self):
        nuovo_titolo = self.entry_titolo.get().strip()
        nuovo_url = self.entry_url.get().strip()
        nuovo_tipo = self.combo_tipo.get()
        nuovo_stato = self.combo_stato.get()
        
        prog_raw = self.entry_progresso.get().strip()
        tot_raw = self.entry_totale.get().strip()
        
        nuovo_voto = int(self.combo_voto.get())
        nuove_note = self.txt_note.get("1.0", "end-1c").strip()

        if not nuovo_titolo:
            messagebox.showwarning("Attenzione", "Il titolo è obbligatorio!", parent=self)
            return

        nuovo_progresso = int(prog_raw) if prog_raw.isdigit() else 0
        nuovo_totale = int(tot_raw) if tot_raw.isdigit() else 0

        db_media.aggiorna_media_completo(
            self.media_id, nuovo_titolo, nuovo_tipo, nuovo_stato, nuovo_progresso, nuovo_totale, nuovo_voto, nuove_note, nuovo_url
        )

        self.on_save_callback()
        self.destroy()


class MediaTrackerFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        db_media.init_db()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- PANNELLO SINISTRO: INSERIMENTO RAPIDO ---
        self.form_frame = ctk.CTkFrame(self, width=260)
        self.form_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(self.form_frame, text="Aggiungi Titolo", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)

        self.entry_titolo = ctk.CTkEntry(self.form_frame, placeholder_text="Titolo")
        self.entry_titolo.pack(fill="x", padx=15, pady=5)

        self.entry_url = ctk.CTkEntry(self.form_frame, placeholder_text="Link URL Lettura (opzionale)")
        self.entry_url.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(self.form_frame, text="Tipo:").pack(anchor="w", padx=15)
        self.combo_tipo = ctk.CTkOptionMenu(self.form_frame, values=["Manga", "Anime"])
        self.combo_tipo.pack(fill="x", padx=15, pady=(0, 5))

        ctk.CTkLabel(self.form_frame, text="Stato:").pack(anchor="w", padx=15)
        self.combo_stato = ctk.CTkOptionMenu(self.form_frame, values=["In corso", "Pianificato", "Completato", "In pausa"])
        self.combo_stato.pack(fill="x", padx=15, pady=(0, 5))

        self.entry_totale = ctk.CTkEntry(self.form_frame, placeholder_text="Totale Cap./Ep. (opzionale)")
        self.entry_totale.pack(fill="x", padx=15, pady=5)

        btn_salva = ctk.CTkButton(self.form_frame, text="Aggiungi in Libreria", fg_color="green", command=self.aggiungi_media)
        btn_salva.pack(fill="x", padx=15, pady=15)

        # --- PANNELLO DESTRO: FILTRI E LISTA ---
        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.right_frame.grid_rowconfigure(1, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        self.filter_frame = ctk.CTkFrame(self.right_frame)
        self.filter_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.entry_search = ctk.CTkEntry(self.filter_frame, placeholder_text="Cerca titolo...")
        self.entry_search.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        self.entry_search.bind("<KeyRelease>", lambda event: self.carica_lista())

        self.combo_filtro_tipo = ctk.CTkOptionMenu(
            self.filter_frame, values=["Tutti", "Anime", "Manga"], width=90, command=lambda _: self.carica_lista()
        )
        self.combo_filtro_tipo.pack(side="left", padx=5)

        self.combo_filtro_stato = ctk.CTkOptionMenu(
            self.filter_frame, values=["Tutti", "In corso", "Pianificato", "Completato", "In pausa"], width=110, command=lambda _: self.carica_lista()
        )
        self.combo_filtro_stato.pack(side="left", padx=5)

        self.scroll_list = ctk.CTkScrollableFrame(self.right_frame)
        self.scroll_list.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.carica_lista()

    def aggiungi_media(self):
        titolo = self.entry_titolo.get().strip()
        url = self.entry_url.get().strip()
        tipo = self.combo_tipo.get()
        stato = self.combo_stato.get()
        tot_raw = self.entry_totale.get().strip()

        if not titolo:
            messagebox.showwarning("Attenzione", "Il titolo è obbligatorio!")
            return

        totale = int(tot_raw) if tot_raw.isdigit() else 0

        db_media.salva_media(titolo, tipo, stato, progresso=0, totale=totale, voto=0, note="", url=url)
        self.entry_titolo.delete(0, 'end')
        self.entry_url.delete(0, 'end')
        self.entry_totale.delete(0, 'end')
        self.carica_lista()

    def carica_lista(self):
        for w in self.scroll_list.winfo_children():
            w.destroy()

        search = self.entry_search.get().strip()
        f_tipo = self.combo_filtro_tipo.get()
        f_stato = self.combo_filtro_stato.get()

        rows = db_media.carica_media(f_tipo, f_stato, search)

        for media_data in rows:
            media_id, titolo, tipo, stato, progresso, totale, voto, note, url = media_data

            card = ctk.CTkFrame(self.scroll_list)
            card.pack(fill="x", padx=5, pady=4)

            lbl_title = ctk.CTkLabel(card, text=f"[{tipo.upper()}] {titolo}", font=ctk.CTkFont(size=14, weight="bold"))
            lbl_title.pack(side="left", padx=10)

            unita = "Cap." if tipo == "Manga" else "Ep."
            tot_str = f"/{totale}" if totale > 0 else ""
            info_txt = f"{unita} {progresso}{tot_str} | {stato}"
            
            if voto > 0: info_txt += f" | ★ {voto}/10"
            if note: info_txt += " 📝"

            lbl_info = ctk.CTkLabel(card, text=info_txt, text_color="gray")
            lbl_info.pack(side="left", padx=10)

            btn_del = ctk.CTkButton(card, text="✕", width=25, fg_color="#C0392B", command=lambda m_id=media_id: self.elimina(m_id))
            btn_del.pack(side="right", padx=5, pady=5)

            btn_edit = ctk.CTkButton(
                card, text="⚙️ Scheda / Note", width=110, 
                command=lambda data=media_data: self.apri_scheda_dettaglio(data)
            )
            btn_edit.pack(side="right", padx=5, pady=5)

            # Pulsante Apri URL se il link è specificato
            if url:
                btn_url = ctk.CTkButton(
                    card, text="🔗 Leggi", width=70, fg_color="#27AE60",
                    command=lambda u=url: self.apri_link(u)
                )
                btn_url.pack(side="right", padx=5, pady=5)

            btn_plus = ctk.CTkButton(card, text="+1", width=35, command=lambda m_id=media_id: self.modifica_progresso(m_id, 1))
            btn_plus.pack(side="right", padx=2, pady=5)

    def apri_link(self, link_url):
        if not link_url.startswith("http://") and not link_url.startswith("https://"):
            link_url = "https://" + link_url
        webbrowser.open(link_url)

    def apri_scheda_dettaglio(self, media_data):
        DettagliMediaWindow(self.winfo_toplevel(), media_data, on_save_callback=self.carica_lista)

    def modifica_progresso(self, media_id, delta):
        db_media.aggiorna_progresso(media_id, delta)
        self.carica_lista()

    def elimina(self, media_id):
        db_media.elimina_media(media_id)
        self.carica_lista()