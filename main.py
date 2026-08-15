import customtkinter as ctk
from gui_turni import TurniFrame
from gui_passwords import PasswordManagerFrame
from gui_media import MediaTrackerFrame

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Personal Workspace Dashboard")
        self.geometry("1100x700")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- SIDEBAR DI NAVIGAZIONE ---
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        lbl_logo = ctk.CTkLabel(self.sidebar, text="Workspace", font=ctk.CTkFont(size=20, weight="bold"))
        lbl_logo.pack(padx=20, pady=(20, 10))

        btn_turni = ctk.CTkButton(self.sidebar, text="📅 Turni Lavoro", command=self.show_turni)
        btn_turni.pack(padx=20, pady=10)

        btn_media = ctk.CTkButton(self.sidebar, text="📖 Anime & Manga", command=self.show_media)
        btn_media.pack(padx=20, pady=10)

        btn_passwords = ctk.CTkButton(self.sidebar, text="🔑 Password Manager", command=self.show_passwords)
        btn_passwords.pack(padx=20, pady=10)

        # --- AREA CONTENUTO CENTRALE ---
        self.main_area = ctk.CTkFrame(self, corner_radius=0)
        self.main_area.grid(row=0, column=1, sticky="nsew")
        self.main_area.grid_rowconfigure(0, weight=1)
        self.main_area.grid_columnconfigure(0, weight=1)

        # Avvio sulla scheda Turni
        self.show_turni()

    def clear_main_area(self):
        for w in self.main_area.winfo_children():
            w.destroy()

    def show_turni(self):
        self.clear_main_area()
        frame = TurniFrame(self.main_area)
        frame.grid(row=0, column=0, sticky="nsew")

    def show_media(self):
        self.clear_main_area()
        frame = MediaTrackerFrame(self.main_area)
        frame.grid(row=0, column=0, sticky="nsew")

    def show_passwords(self):
        self.clear_main_area()
        frame = PasswordManagerFrame(self.main_area)
        frame.grid(row=0, column=0, sticky="nsew")

if __name__ == "__main__":
    app = App()
    app.mainloop()