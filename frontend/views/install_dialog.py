import customtkinter as ctk
from theme import *
import subprocess
import sys

class InstallDialog(ctk.CTkToplevel):
    def __init__(self, master, lib_name, version, python_exe):
        super().__init__(master)
        self.title(f"Instalar/Actualizar {lib_name}")
        self.geometry("450x350")
        self.configure(fg_color=BG_DARK)
        self.grab_set()
        
        self.lib_name = lib_name
        self.version = version
        self.python_exe = python_exe
        
        ctk.CTkLabel(self, text=f"{lib_name} v{version}", font=(FONT_FAMILY, 20, "bold"), text_color=MINT).pack(pady=(20, 10))
        ctk.CTkLabel(self, text="Selecciona el gestor de paquetes para actualizar:", text_color=TEXT).pack(pady=(0, 10))
        
        # Selector de gestor
        self.manager_var = ctk.StringVar(value="uv")
        self.seg_button = ctk.CTkSegmentedButton(self, values=["pip", "uv"], variable=self.manager_var, 
                                                 selected_color=BLUE, selected_hover_color="#3A79C4")
        self.seg_button.pack(pady=10)
        
        # Botón de instalar
        self.btn = ctk.CTkButton(self, text="Instalar / Actualizar", fg_color=MINT, text_color=BG_DARK, hover_color=MINT_LIGHT, command=self._do_install)
        self.btn.pack(pady=20)
        
        self.status = ctk.CTkLabel(self, text="", text_color=TEXT_DIM, wraplength=400)
        self.status.pack(pady=10)

    def _do_install(self):
        manager = self.manager_var.get()
        self.btn.configure(state="disabled", text="Instalando...")
        self.status.configure(text=f"Actualizando en {self.python_exe}...", text_color=BLUE)
        self.update()
        
        # Construimos el comando asegurando que apunte al entorno correcto
        if manager == "uv":
            # uv instalará en el entorno que le indiquemos con el python.exe
            cmd = f'cmd /c uv pip install --python "{self.python_exe}" --upgrade {self.lib_name}'
        else:
            cmd = f"\"{self.python_exe}\" -m pip install --upgrade {self.lib_name}"
            
        try:
            process = subprocess.run(cmd, shell=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            if process.returncode == 0:
                self.status.configure(text=f"✅ {self.lib_name} actualizado en este entorno.", text_color=MINT)
            else:
                error_msg = process.stderr if process.stderr else process.stdout
                self.status.configure(text=f"❌ Error:\n{error_msg[:150]}...", text_color=ERROR)
        except Exception as e:
            self.status.configure(text=f"❌ Error crítico: {e}", text_color=ERROR)
            
        self.btn.configure(state="normal", text="Cerrar", command=self.destroy)
