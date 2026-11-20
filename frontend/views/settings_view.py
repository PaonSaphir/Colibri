import customtkinter as ctk
from theme import *

class SettingsView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        ctk.CTkLabel(self, text="Configuración", font=(FONT_FAMILY, 26, "bold"), text_color=MINT).pack(anchor="w", padx=32, pady=(28, 16))
        
        card = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=12)
        card.pack(fill="x", padx=32, pady=10)
        
        ctk.CTkLabel(card, text="Tema de la aplicación", text_color=TEXT).pack(anchor="w", padx=16, pady=(16, 8))
        ctk.CTkOptionMenu(card, values=["Dark", "Light"], fg_color=BLUE).pack(anchor="w", padx=16, pady=(0, 16))