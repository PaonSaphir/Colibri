import customtkinter as ctk
from theme import *
from views.move_dialog import MoveDialog
from views.install_dialog import InstallDialog
from views.details_dialog import DetailsDialog  # <-- Nuevo panel
import threading
import json
import sys
import os
from tkinter import filedialog

class LibrariesView(ctk.CTkFrame):
    def __init__(self, master, scanner_py, scanner_cpp, mover):
        super().__init__(master, fg_color="transparent")
        self.scanner_py = scanner_py
        self.scanner_cpp = scanner_cpp
        self.mover = mover
        self.all_libraries = [] 

        top = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=12)
        top.pack(fill="x", padx=24, pady=(24, 12))

        self.lang_var = ctk.StringVar(value="Python")
        ctk.CTkSegmentedButton(top, values=["Python", "C++"], variable=self.lang_var,
                               selected_color=MINT, selected_hover_color=MINT_LIGHT,
                               command=lambda _: self.refresh()).pack(side="left", padx=12, pady=12)

        # Buscador
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self._on_search)
        self.search_entry = ctk.CTkEntry(top, placeholder_text="🔍 Buscar...", 
                                         textvariable=self.search_var, width=150, fg_color=SURFACE_2)
        self.search_entry.pack(side="left", padx=12)

        # Filtro por entorno
        self.env_filter_var = ctk.StringVar(value="Todos los entornos")
        self.env_filter_menu = ctk.CTkOptionMenu(top, values=["Todos los entornos"], 
                                                 variable=self.env_filter_var, fg_color=PURPLE,
                                                 command=lambda _: self._on_search())
        self.env_filter_menu.pack(side="left", padx=12)

        ctk.CTkButton(top, text="🔄 Escanear", fg_color=BLUE, hover_color="#3A79C4", command=self.refresh).pack(side="right", padx=12)
        ctk.CTkButton(top, text="📥 Exportar", fg_color=PURPLE, hover_color="#8E44AD", command=self.export_inventory).pack(side="right", padx=12)

        self.scroll = ctk.CTkScrollableFrame(self, fg_color=BG_DARK)
        self.scroll.pack(fill="both", expand=True, padx=24, pady=(0, 24))

    def refresh(self):
        for w in self.scroll.winfo_children():
            w.destroy()
        
        ctk.CTkLabel(self.scroll, text="Escaneando...", text_color=TEXT_DIM).pack(pady=20)
        threading.Thread(target=self._scan_bg, daemon=True).start()

    def _scan_bg(self):
        if self.lang_var.get() == "Python":
            envs = self.scanner_py.discover_environments()
            scanner = self.scanner_py
        else:
            envs = self.scanner_cpp.discover_environments()
            scanner = self.scanner_cpp

        new_libs = []
        env_names = set()
        for env in envs:
            env_names.add(env.name)
            new_libs.extend(scanner.scan_environment(env))

        # Actualizar menú de entornos
        options = ["Todos los entornos"] + sorted(list(env_names))
        self.after(0, lambda: self.env_filter_menu.configure(values=options))
        
        if self.env_filter_var.get() not in options:
            self.env_filter_var.set("Todos los entornos")

        self.after(0, lambda: self._render_libs(new_libs))

    def _on_search(self, *args):
        query = self.search_var.get().lower()
        selected_env = self.env_filter_var.get()
        
        filtered = []
        for lib in self.all_libraries:
            if query not in lib.name.lower():
                continue
            if selected_env != "Todos los entornos" and lib.environment != selected_env:
                continue
            filtered.append(lib)
            
        self._draw_table(filtered)

    def _render_libs(self, libs):
        self.all_libraries = libs
        self._on_search()

    def _draw_table(self, libs):
        for w in self.scroll.winfo_children():
            w.destroy()
            
        if not libs:
            ctk.CTkLabel(self.scroll, text="No se encontraron librerías.", text_color=TEXT_DIM).pack(pady=20)
            return

        libs = sorted(libs, key=lambda x: x.name.lower())
        
        latest_versions = {}
        for lib in self.all_libraries:
            if lib.name not in latest_versions or lib.version > latest_versions[lib.name]:
                latest_versions[lib.name] = lib.version

        for lib in libs:
            is_outdated = lib.version != latest_versions[lib.name]
            row_color = SURFACE_2 if is_outdated else SURFACE
            
            row = ctk.CTkFrame(self.scroll, fg_color=row_color, corner_radius=8)
            row.pack(fill="x", pady=2)

            color_name = ERROR if is_outdated else TEXT
            
            # El nombre ahora es un botón clickeable para ver Detalles
            name_btn = ctk.CTkButton(row, text=lib.name, width=260, anchor="w", 
                                     fg_color="transparent", hover_color=SURFACE, 
                                     text_color=color_name, font=(FONT_FAMILY, 13),
                                     command=lambda l=lib: DetailsDialog(self, l))
            name_btn.pack(side="left", padx=10, pady=6)
            
            version_text = lib.version + (" ⚠️" if is_outdated else "")
            ctk.CTkLabel(row, text=version_text, width=100, anchor="w", text_color=ERROR if is_outdated else BLUE).pack(side="left", padx=10)
            
            ctk.CTkLabel(row, text=lib.environment, width=150, anchor="w", text_color=PURPLE).pack(side="left", padx=10)

            ctk.CTkButton(row, text="Mover…", width=80, fg_color=MINT, hover_color=MINT_LIGHT, text_color=BG_DARK,
                          command=lambda l=lib: self._open_move(l)).pack(side="right", padx=5, pady=4)

            if is_outdated:
                ctk.CTkButton(row, text="Actualizar", width=90, fg_color=ERROR, hover_color="#C0392B",
                              command=lambda l=lib, v=latest_versions[lib.name]: self._open_install(l, v)).pack(side="right", padx=5)

    def _open_move(self, lib):
        MoveDialog(self, lib, self.mover, self.scanner_py, self.scanner_cpp)

    def _open_install(self, lib, latest_version):
        python_exe = sys.executable
        
        if '\\Lib\\' in lib.path:
            env_root = lib.path.split('\\Lib\\')[0]
            if os.path.exists(os.path.join(env_root, "python.exe")):
                python_exe = os.path.join(env_root, "python.exe")
            elif os.path.exists(os.path.join(env_root, "Scripts", "python.exe")):
                python_exe = os.path.join(env_root, "Scripts", "python.exe")
                
        if lib.environment == "python-global":
            python_exe = sys.executable

        InstallDialog(self, lib.name, latest_version, python_exe)

    def export_inventory(self):
        if not self.all_libraries:
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if not file_path: return
        
        data = [{"name": l.name, "version": l.version, "path": l.path, "environment": l.environment} for l in self.all_libraries]
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)