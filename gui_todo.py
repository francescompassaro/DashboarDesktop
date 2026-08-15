import customtkinter as ctk
from tkinter import messagebox
import db_todo

class DettagliTaskWindow(ctk.CTkToplevel):
    """Finestra popup/scheda per modificare i dettagli ed estendere le note di un Task o Progetto."""
    def __init__(self, master, task_data, on_save_callback):
        super().__init__(master)
        self.task_id, titolo, categoria, priorita, stato, descrizione = task_data
        self.on_save_callback = on_save_callback

        self.title(f"Scheda: {titolo}")
        self.geometry("480x550")
        self.resizable(False, False)

        self.transient(master)
        self.grab_set()

        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(frame, text="Dettagli Attività", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(0, 10))

        # Titolo
        ctk.CTkLabel(frame, text="Titolo Task / Progetto:").pack(anchor="w", padx=10)
        self.entry_titolo = ctk.CTkEntry(frame)
        self.entry_titolo.insert(0, titolo)
        self.entry_titolo.pack(fill="x", padx=10, pady=(0, 10))

        # Categoria, Priorità e Stato su 3 colonne
        row_opt = ctk.CTkFrame(frame, fg_color="transparent")
        row_opt.pack(fill="x", padx=10, pady=(0, 10))

        # Categoria
        col_cat = ctk.CTkFrame(row_opt, fg_color="transparent")
        col_cat.pack(side="left", fill="x", expand=True, padx=(0, 3))
        ctk.CTkLabel(col_cat, text="Tipo:").pack(anchor="w")
        self.combo_categoria = ctk.CTkOptionMenu(col_cat, values=["To-Do", "Idea Progetto"])
        self.combo_categoria.set(categoria)
        self.combo_categoria.pack(fill="x")

        # Priorità
        col_prio = ctk.CTkFrame(row_opt, fg_color="transparent")
        col_prio.pack(side="left", fill="x", expand=True, padx=(3, 3))
        ctk.CTkLabel(col_prio, text="Priorità:").pack(anchor="w")
        self.combo_priorita = ctk.CTkOptionMenu(col_prio, values=["Alta", "Media", "Bassa"])
        self.combo_priorita.set(priorita)
        self.combo_priorita.pack(fill="x")

        # Stato
        col_stato = ctk.CTkFrame(row_opt, fg_color="transparent")
        col_stato.pack(side="right", fill="x", expand=True, padx=(3, 0))
        ctk.CTkLabel(col_stato, text="Stato:").pack(anchor="w")
        self.combo_stato = ctk.CTkOptionMenu(col_stato, values=["Da fare", "In corso", "Completato"])
        self.combo_stato.set(stato)
        self.combo_stato.pack(fill="x")

        # Box Descrizione / Note Multilinea
        ctk.CTkLabel(frame, text="Descrizione / Note Estese:").pack(anchor="w", padx=10)
        self.txt_desc = ctk.CTkTextbox(frame, height=160)
        if descrizione:
            self.txt_desc.insert("1.0", descrizione)
        self.txt_desc.pack(fill="both", expand=True, padx=10, pady=(0, 15))

        # Bottoni Salva / Annulla
        btn_box = ctk.CTkFrame(frame, fg_color="transparent")
        btn_box.pack(fill="x", padx=10)

        btn_salva = ctk.CTkButton(btn_box, text="Salva Modifiche", fg_color="green", command=self.salva)
        btn_salva.pack(side="right", padx=5)

        btn_annulla = ctk.CTkButton(btn_box, text="Annulla", fg_color="gray", command=self.destroy)
        btn_annulla.pack(side="right", padx=5)

    def salva(self):
        nuovo_titolo = self.entry_titolo.get().strip()
        nuova_cat = self.combo_categoria.get()
        nuova_prio = self.combo_priorita.get()
        nuovo_stato = self.combo_stato.get()
        nuova_desc = self.txt_desc.get("1.0", "end-1c").strip()

        if not nuovo_titolo:
            messagebox.showwarning("Attenzione", "Il titolo è obbligatorio!", parent=self)
            return

        db_todo.aggiorna_task_completo(
            self.task_id, nuovo_titolo, nuova_cat, nuova_prio, nuovo_stato, nuova_desc
        )

        self.on_save_callback()
        self.destroy()


class TodoFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        db_todo.init_db()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- PANNELLO SINISTRO: INSERIMENTO ---
        self.form_frame = ctk.CTkFrame(self, width=280)
        self.form_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(self.form_frame, text="Nuova Attività / Idea", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)

        self.entry_titolo = ctk.CTkEntry(self.form_frame, placeholder_text="Titolo Task o Progetto")
        self.entry_titolo.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(self.form_frame, text="Tipo:").pack(anchor="w", padx=15)
        self.combo_categoria = ctk.CTkOptionMenu(self.form_frame, values=["To-Do", "Idea Progetto"])
        self.combo_categoria.pack(fill="x", padx=15, pady=(0, 5))

        ctk.CTkLabel(self.form_frame, text="Priorità:").pack(anchor="w", padx=15)
        self.combo_priorita = ctk.CTkOptionMenu(self.form_frame, values=["Alta", "Media", "Bassa"])
        self.combo_priorita.set("Media")
        self.combo_priorita.pack(fill="x", padx=15, pady=(0, 5))

        ctk.CTkLabel(self.form_frame, text="Note / Dettagli:").pack(anchor="w", padx=15)
        self.txt_desc = ctk.CTkTextbox(self.form_frame, height=100)
        self.txt_desc.pack(fill="x", padx=15, pady=(0, 10))

        btn_salva = ctk.CTkButton(self.form_frame, text="Aggiungi Task", fg_color="green", command=self.aggiungi_task)
        btn_salva.pack(fill="x", padx=15, pady=10)

        # --- PANNELLO DESTRO: FILTRI E LISTA ---
        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.right_frame.grid_rowconfigure(1, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        # FILTRI
        self.filter_frame = ctk.CTkFrame(self.right_frame)
        self.filter_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.combo_f_cat = ctk.CTkOptionMenu(self.filter_frame, values=["Tutti", "To-Do", "Idea Progetto"], command=lambda _: self.carica_lista())
        self.combo_f_cat.pack(side="left", padx=5, pady=5)

        self.combo_f_prio = ctk.CTkOptionMenu(self.filter_frame, values=["Tutte", "Alta", "Media", "Bassa"], command=lambda _: self.carica_lista())
        self.combo_f_prio.pack(side="left", padx=5, pady=5)

        self.combo_f_stato = ctk.CTkOptionMenu(self.filter_frame, values=["Tutti", "Da fare", "In corso", "Completato"], command=lambda _: self.carica_lista())
        self.combo_f_stato.pack(side="left", padx=5, pady=5)

        self.scroll_list = ctk.CTkScrollableFrame(self.right_frame)
        self.scroll_list.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.carica_lista()

    def aggiungi_task(self):
        titolo = self.entry_titolo.get().strip()
        cat = self.combo_categoria.get()
        prio = self.combo_priorita.get()
        desc = self.txt_desc.get("1.0", "end-1c").strip()

        if not titolo:
            messagebox.showwarning("Attenzione", "Il titolo è obbligatorio!")
            return

        db_todo.salva_task(titolo, cat, prio, stato="Da fare", descrizione=desc)
        self.entry_titolo.delete(0, 'end')
        self.txt_desc.delete("1.0", "end")
        self.carica_lista()

    def carica_lista(self):
        for w in self.scroll_list.winfo_children():
            w.destroy()

        f_cat = self.combo_f_cat.get()
        f_prio = self.combo_f_prio.get()
        f_stato = self.combo_f_stato.get()

        rows = db_todo.carica_task(f_cat, f_prio, f_stato)

        colori_prio = {"Alta": "🔴", "Media": "🟡", "Bassa": "🟢"}

        for task_data in rows:
            t_id, titolo, cat, prio, stato, desc = task_data

            card = ctk.CTkFrame(self.scroll_list)
            card.pack(fill="x", padx=5, pady=4)

            prio_icon = colori_prio.get(prio, "⚪")
            txt_titolo = f"{prio_icon} [{cat.upper()}] {titolo}"
            lbl_title = ctk.CTkLabel(card, text=txt_titolo, font=ctk.CTkFont(size=14, weight="bold"))
            lbl_title.pack(side="left", padx=10)

            if desc:
                lbl_desc = ctk.CTkLabel(card, text=f"({desc[:25]}...)" if len(desc) > 25 else f"({desc})", text_color="gray")
                lbl_desc.pack(side="left", padx=5)

            # Pulsante Elimina
            btn_del = ctk.CTkButton(card, text="✕", width=25, fg_color="#C0392B", command=lambda id_=t_id: self.elimina(id_))
            btn_del.pack(side="right", padx=5, pady=5)

            # Pulsante Apri Scheda / Modifica Dettagli
            btn_edit = ctk.CTkButton(
                card, text="⚙️ Scheda / Note", width=110, 
                command=lambda data=task_data: self.apri_scheda_dettaglio(data)
            )
            btn_edit.pack(side="right", padx=5, pady=5)

            # Dropdown modifica stato veloce
            opt_stato = ctk.CTkOptionMenu(
                card, values=["Da fare", "In corso", "Completato"], width=110,
                command=lambda val, id_=t_id: self.cambia_stato(id_, val)
            )
            opt_stato.set(stato)
            opt_stato.pack(side="right", padx=5, pady=5)

    def apri_scheda_dettaglio(self, task_data):
        DettagliTaskWindow(self.winfo_toplevel(), task_data, on_save_callback=self.carica_lista)

    def cambia_stato(self, task_id, nuovo_stato):
        db_todo.aggiorna_stato_task(task_id, nuovo_stato)
        self.carica_lista()

    def elimina(self, task_id):
        db_todo.elimina_task(task_id)
        self.carica_lista()