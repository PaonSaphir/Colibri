import customtkinter as ctk
from PIL import Image
import os
import tkinter as tk
import colibri_core as core
from theme import *
from views.dashboard_view import DashboardView
from views.libraries_view import LibrariesView
from views.environments_view import EnvironmentsView
from views.settings_view import SettingsView

class ColibriApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Colibrí · Gestor de Librerías")
        self.geometry("1180x720")
        self.configure(fg_color=BG_DARK)

        # --- CARGA DEL LOGO (Única fuente de verdad) ---
        png_path = os.path.join("assets", "colibri_temp.png")
        
        if os.path.exists(png_path):
            try:
                self.logo_image = Image.open(png_path)
            except Exception as e:
                print(f"Error cargando imagen: {e}")
                self.logo_image = None
        else:
            self.logo_image = None

        # --- EL TRUCO DEFINITIVO PARA EL ICONO DE LA VENTANA ---
        if self.logo_image:
            try:
                # 1. Convertir a PhotoImage nativo de Tkinter
                self.window_icon = tk.PhotoImage(file=png_path)
                
                # 2. Usar wm_iconphoto en lugar de iconphoto (salta la restricción de CTk)
                self.wm_iconphoto(True, self.window_icon)
                
                # 3. Hack extra: llamar directamente al gestor de ventanas de Tk
                self.tk.call('wm', 'iconphoto', self._w, self.window_icon)
            except Exception as e:
                print(f"Aviso icono ventana: {e}")

        # Backend en C++
        self.scanner_py = core.ScannerPython()
        self.scanner_cpp = core.ScannerCpp()
        self.mover = core.LibraryMover()

        self._build_sidebar()
        self._build_content()
        self.show_view("dashboard")

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=220, fg_color=SURFACE, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        # --- LOGO EN LA BARRA LATERAL ---
        if self.logo_image:
            img_sidebar = ctk.CTkImage(light_image=self.logo_image, size=(55, 55))
            logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
            logo_frame.pack(pady=(30, 40))
            ctk.CTkLabel(logo_frame, image=img_sidebar, text="").pack(side="left", padx=(0, 10))
            ctk.CTkLabel(logo_frame, text="Colibrí", font=(FONT_FAMILY, 24, "bold"), text_color=MINT).pack(side="left")
        else:
            ctk.CTkLabel(self.sidebar, text="🐦 Colibrí", font=(FONT_FAMILY, 26, "bold"), text_color=MINT).pack(pady=(30, 40))

        # --- BOTONES DEL MENÚ ---
        items = [
            ("Dashboard", "dashboard", MINT),
            ("Librerías", "libraries", BLUE),
            ("Entornos", "environments", PURPLE),
            ("Configuración", "settings", TEXT_DIM)
        ]

        for label, key, color in items:
            btn = ctk.CTkButton(self.sidebar, text=label, fg_color="transparent", hover_color=SURFACE_2,
                                text_color=color, anchor="w", font=(FONT_FAMILY, 14),
                                command=lambda k=key: self.show_view(k))
            btn.pack(fill="x", padx=16, pady=4)

    def _build_content(self):
        self.content = ctk.CTkFrame(self, fg_color=BG_DARK, corner_radius=0)
        self.content.pack(side="right", fill="both", expand=True)

    def show_view(self, key):
        for w in self.content.winfo_children():
            w.destroy()

        if key == "libraries":
            LibrariesView(self.content, self.scanner_py, self.scanner_cpp, self.mover).pack(fill="both", expand=True)
        elif key == "environments":
            EnvironmentsView(self.content, self.scanner_py, self.scanner_cpp).pack(fill="both", expand=True)
        elif key == "settings":
            SettingsView(self.content).pack(fill="both", expand=True)
        else:
            DashboardView(self.content, self.scanner_py, self.scanner_cpp).pack(fill="both", expand=True)