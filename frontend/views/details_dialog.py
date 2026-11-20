import customtkinter as ctk
from theme import *
import os

class DetailsDialog(ctk.CTkToplevel):
    def __init__(self, master, lib):
        super().__init__(master)
        self.title(f"Detalles: {lib.name}")
        self.geometry("600x450")
        self.configure(fg_color=BG_DARK)
        self.grab_set()

        ctk.CTkLabel(self, text=lib.name, font=(FONT_FAMILY, 26, "bold"), text_color=MINT).pack(pady=(20, 4))
        ctk.CTkLabel(self, text=f"Versión {lib.version}", font=(FONT_FAMILY, 16), text_color=BLUE).pack(pady=(0, 20))

        info_frame = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=12)
        info_frame.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        ctk.CTkLabel(info_frame, text="RUTA DE INSTALACIÓN", font=(FONT_FAMILY, 11, "bold"), text_color=TEXT_DIM).pack(anchor="w", padx=20, pady=(15, 2))
        ctk.CTkLabel(info_frame, text=lib.path, font=(FONT_FAMILY, 12), text_color=TEXT, wraplength=520, justify="left").pack(anchor="w", padx=20)

        ctk.CTkLabel(info_frame, text="ENTORNO", font=(FONT_FAMILY, 11, "bold"), text_color=TEXT_DIM).pack(anchor="w", padx=20, pady=(15, 2))
        ctk.CTkLabel(info_frame, text=lib.environment, font=(FONT_FAMILY, 12), text_color=PURPLE).pack(anchor="w", padx=20)

        ctk.CTkLabel(info_frame, text="DEPENDENCIAS", font=(FONT_FAMILY, 11, "bold"), text_color=TEXT_DIM).pack(anchor="w", padx=20, pady=(15, 2))
        
        deps_text = "No se encontraron dependencias declaradas."
        try:
            metadata_path = os.path.join(lib.path, "METADATA")
            if os.path.exists(metadata_path):
                deps = []
                with open(metadata_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("Requires-Dist:"):
                            deps.append(line.replace("Requires-Dist:", "").split(";")[0].strip())
                if deps:
                    deps_text = "\n".join(deps[:10])
                    if len(deps) > 10:
                        deps_text += f"\n... y {len(deps)-10} más."
        except Exception:
            pass

        ctk.CTkLabel(info_frame, text=deps_text, font=(FONT_FAMILY, 12), text_color=TEXT, wraplength=520, justify="left").pack(anchor="w", padx=20)

        ctk.CTkButton(self, text="Cerrar", fg_color=MINT, text_color=BG_DARK, command=self.destroy).pack(pady=(0, 20))