import customtkinter as ctk
from theme import *
import threading

class DashboardView(ctk.CTkFrame):
    def __init__(self, master, scanner_py, scanner_cpp):
        super().__init__(master, fg_color="transparent")
        self.scanner_py = scanner_py
        self.scanner_cpp = scanner_cpp
        
        ctk.CTkLabel(self, text="Bienvenido a Colibrí", font=(FONT_FAMILY, 32, "bold"), text_color=MINT).pack(anchor="w", padx=40, pady=(40, 4))
        ctk.CTkLabel(self, text="Detecta, gestiona y mueve tus librerías de Python y C++.", font=(FONT_FAMILY, 15), text_color=TEXT_DIM).pack(anchor="w", padx=40)

        stats = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=16)
        stats.pack(fill="x", padx=40, pady=30)

        self.lbl_envs, self.lbl_py, self.lbl_cpp = None, None, None

        for i, (label, color) in enumerate([("Entornos", BLUE), ("Librerías Python", MINT), ("Librerías C++", PURPLE)]):
            card = ctk.CTkFrame(stats, fg_color="transparent")
            card.pack(side="left", expand=True, fill="both", padx=20, pady=20)
            val_lbl = ctk.CTkLabel(card, text="...", font=(FONT_FAMILY, 34, "bold"), text_color=color)
            val_lbl.pack()
            ctk.CTkLabel(card, text=label, font=(FONT_FAMILY, 13), text_color=TEXT_DIM).pack()
            
            if i == 0: self.lbl_envs = val_lbl
            elif i == 1: self.lbl_py = val_lbl
            elif i == 2: self.lbl_cpp = val_lbl

        # Lanzar carga automática en segundo plano al abrir el Dashboard
        threading.Thread(target=self._load_stats, daemon=True).start()

    def _load_stats(self):
        # Escanear Python
        envs_py = self.scanner_py.discover_environments()
        libs_py = []
        for env in envs_py:
            libs_py.extend(self.scanner_py.scan_environment(env))
            
        # Escanear C++
        envs_cpp = self.scanner_cpp.discover_environments()
        libs_cpp = []
        for env in envs_cpp:
            libs_cpp.extend(self.scanner_cpp.scan_environment(env))

        total_envs = len(envs_py) + len(envs_cpp)

        # Actualizar UI de forma segura
        self.after(0, lambda: self.lbl_envs.configure(text=str(total_envs)))
        self.after(0, lambda: self.lbl_py.configure(text=str(len(libs_py))))
        self.after(0, lambda: self.lbl_cpp.configure(text=str(len(libs_cpp))))