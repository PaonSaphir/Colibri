import customtkinter as ctk
from theme import *

class EnvironmentsView(ctk.CTkFrame):
    def __init__(self, master, scanner_py, scanner_cpp):
        super().__init__(master, fg_color="transparent")
        
        ctk.CTkLabel(self, text="Entornos detectados", font=(FONT_FAMILY, 26, "bold"), text_color=MINT).pack(anchor="w", padx=32, pady=(28, 16))
        
        body = ctk.CTkScrollableFrame(self, fg_color=BG_DARK)
        body.pack(fill="both", expand=True, padx=32, pady=(0, 24))

        # Cargar síncronamente para prueba rápida
        for env in scanner_py.discover_environments():
            self._env_card(body, env, BLUE)
        for env in scanner_cpp.discover_environments():
            self._env_card(body, env, PURPLE)

    def _env_card(self, parent, env, color):
        card = ctk.CTkFrame(parent, fg_color=SURFACE, corner_radius=12)
        card.pack(fill="x", pady=6)
        ctk.CTkLabel(card, text=f"● {env.name}", text_color=color, font=(FONT_FAMILY, 15, "bold")).pack(anchor="w", padx=16, pady=(10, 0))
        ctk.CTkLabel(card, text=env.root_path, text_color=TEXT_DIM, font=(FONT_FAMILY, 12)).pack(anchor="w", padx=16, pady=(0, 10))