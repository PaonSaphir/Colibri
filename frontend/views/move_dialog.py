import customtkinter as ctk
from theme import *

# Importación segura para evitar alertas en VS Code
try:
    import colibri_core as core
except ImportError:
    core = None

class MoveDialog(ctk.CTkToplevel):
    def __init__(self, master, lib, mover, scanner_py, scanner_cpp):
        super().__init__(master)
        self.lib = lib
        self.mover = mover
        
        self.title(f"Gestionar {self.lib.name}")
        self.geometry("550x400")
        self.configure(fg_color=BG_DARK)
        self.grab_set()

        ctk.CTkLabel(self, text=f"{self.lib.name} v{self.lib.version}", font=(FONT_FAMILY, 22, "bold"), text_color=MINT).pack(pady=(20, 4))
        
        # Mostrar la ruta recortada por si es muy larga
        path_text = self.lib.path if self.lib.path else "Desconocida"
        ctk.CTkLabel(self, text=f"Ruta actual: {path_text}", font=(FONT_FAMILY, 11), text_color=TEXT_DIM, wraplength=500).pack(pady=(0, 20))
        
        # Filtrar estrictamente por lenguaje usando el string, no el Enum (evita errores)
        is_python = "Python" in str(self.lib.language) or self.lib.language == 0
        if is_python:
            envs = scanner_py.discover_environments()
        else:
            envs = scanner_cpp.discover_environments()
            
        # Diccionario {nombre_entorno: ruta_completa_del_entorno}
        self.envs_dict = {e.name: e.root_path for e in envs if e.name != lib.environment}
        
        if not self.envs_dict:
            ctk.CTkLabel(self, text="❌ No hay otros entornos disponibles para mover.", text_color=ERROR, font=(FONT_FAMILY, 14)).pack(pady=20)
            return

        ctk.CTkLabel(self, text="Selecciona el entorno destino:", text_color=TEXT).pack(anchor="w", padx=40)
        self.env_var = ctk.StringVar(value=list(self.envs_dict.keys())[0])
        
        ctk.CTkOptionMenu(self, values=list(self.envs_dict.keys()), variable=self.env_var, fg_color=BLUE).pack(fill="x", padx=40, pady=(4, 20))

        self.btn = ctk.CTkButton(self, text="Simular y Mover", fg_color=MINT, text_color=BG_DARK, hover_color=MINT_LIGHT, command=self._do_move)
        self.btn.pack(pady=10)

        self.status = ctk.CTkLabel(self, text="", text_color=TEXT_DIM, wraplength=500)
        self.status.pack(pady=10)

    def _do_move(self):
        dest_name = self.env_var.get()
        dest_path = self.envs_dict[dest_name]

        try:
            self.status.configure(text="⏳ Calculando plan de movimiento (Dry-run)...", text_color=BLUE)
            self.update()
            
            # 1. Planificar
            plan = self.mover.plan_move(self.lib, dest_path)
            
            if plan.has_conflicts:
                warn = "\n".join(plan.warnings)
                self.status.configure(text=f"⚠️ No se puede mover:\n{warn}", text_color=ERROR)
                return

            # 2. Ejecutar
            self.btn.configure(state="disabled", text="Moviendo archivos...")
            self.status.configure(text="📦 Moviendo archivos...", text_color=MINT)
            self.update()
            
            success = self.mover.execute_move(plan)
            
            if success:
                self.status.configure(text="✅ ¡Librería movida con éxito!", text_color=MINT)
                self.after(2000, self.destroy)
        except Exception as e:
            self.status.configure(text=f"❌ Error del motor C++:\n{e}", text_color=ERROR)
            self.btn.configure(state="normal", text="Simular y Mover")