import customtkinter as ctk

# Importazione dei 4 moduli GUI
from gui_turni import TurniFrame
from gui_passwords import PasswordManagerFrame
from gui_media import MediaTrackerFrame
from gui_todo import TodoFrame

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class WorkspaceApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Personal Workspace Dashboard")
        self.geometry("1150x720")

        # Configurazione griglia (Sidebar a sinistra, Contenuto a destra)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- SIDEBAR DI NAVIGAZIONE ---
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        lbl_logo = ctk.CTkLabel(
            self.sidebar, 
            text="Workspace", 
            font=ctk.CTkFont(size=22, weight="bold")
        )
        lbl_logo.pack(padx=20, pady=(25, 15))

        # Bottoni di navigazione
        self.btn_turni = ctk.CTkButton(
            self.sidebar, text="📅 Turni Lavoro", anchor="w", command=self.show_turni
        )
        self.btn_turni.pack(fill="x", padx=15, pady=8)

        self.btn_media = ctk.CTkButton(
            self.sidebar, text="📖 Anime & Manga", anchor="w", command=self.show_media
        )
        self.btn_media.pack(fill="x", padx=15, pady=8)

        self.btn_todo = ctk.CTkButton(
            self.sidebar, text="📌 To-Do & Progetti", anchor="w", command=self.show_todo
        )
        self.btn_todo.pack(fill="x", padx=15, pady=8)

        self.btn_passwords = ctk.CTkButton(
            self.sidebar, text="🔑 Password Manager", anchor="w", command=self.show_passwords
        )
        self.btn_passwords.pack(fill="x", padx=15, pady=8)

        # --- AREA CONTENUTO CENTRALE ---
        self.main_area = ctk.CTkFrame(self, corner_radius=0)
        self.main_area.grid(row=0, column=1, sticky="nsew")
        self.main_area.grid_rowconfigure(0, weight=1)
        self.main_area.grid_columnconfigure(0, weight=1)

        # Avvio sulla scheda Turni
        self.show_turni()

    def clear_main_area(self):
        """Pulisce la vista centrale prima di caricare una nuova scheda."""
        for widget in self.main_area.winfo_children():
            widget.destroy()

    def show_turni(self):
        self.clear_main_area()
        frame = TurniFrame(self.main_area)
        frame.grid(row=0, column=0, sticky="nsew")

    def show_media(self):
        self.clear_main_area()
        frame = MediaTrackerFrame(self.main_area)
        frame.grid(row=0, column=0, sticky="nsew")

    def show_todo(self):
        self.clear_main_area()
        frame = TodoFrame(self.main_area)
        frame.grid(row=0, column=0, sticky="nsew")

    def show_passwords(self):
        self.clear_main_area()
        frame = PasswordManagerFrame(self.main_area)
        frame.grid(row=0, column=0, sticky="nsew")

if __name__ == "__main__":
    app = WorkspaceApp()
    app.mainloop()