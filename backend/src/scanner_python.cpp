#include <iostream>
#include "colibri/scanner_python.hpp"
#include "colibri/process_runner.hpp"
#include <filesystem>
#include <regex>
#include <cstdlib>
#include <algorithm>
#include <set>
#include <sstream>

namespace fs = std::filesystem;

namespace colibri {

// Helper para limpiar strings
static std::string clean_str(std::string s) {
    s.erase(std::remove(s.begin(), s.end(), '\r'), s.end());
    s.erase(std::remove(s.begin(), s.end(), '\n'), s.end());
    // Quitar comillas si las hay
    if (!s.empty() && s.front() == '"') s.erase(0, 1);
    if (!s.empty() && s.back() == '"') s.pop_back();
    return s;
}

std::vector<EnvironmentInfo> ScannerPython::discover_environments() {
    std::vector<EnvironmentInfo> envs;
    std::set<std::string> seen_paths; // Para no duplicar

    // 1. TRUCO DE WINDOWS: Buscar todos los python.exe registrados
    // En Windows usamos "where python", en Linux/Mac "which -a python3"
    std::string cmd_where;
#ifdef _WIN32
    cmd_where = "where python 2>nul";
#else
    cmd_where = "which -a python3 python 2>/dev/null";
#endif

    std::string raw_paths = ProcessRunner::run(cmd_where);
    std::stringstream ss(raw_paths);
    std::string line;

    while (std::getline(ss, line)) {
        line = clean_str(line);
        if (line.empty() || line.find("WindowsApps") != std::string::npos) continue; // Ignorar el falso de Microsoft Store

        fs::path exe_path(line);
        if (!fs::exists(exe_path)) continue;

        fs::path root_path = exe_path.parent_path(); // Quitar "python.exe"
        
        // Si estamos en un venv (Windows), el exe está en root. En Linux está en root/bin
        if (root_path.filename() == "bin" || root_path.filename() == "Scripts") {
            root_path = root_path.parent_path();
        }

        // Si es el Python global, la raíz real suele ser un nivel más arriba en Windows
        std::string env_name = root_path.filename().string();
        if (env_name == "Python314" || env_name == "Python311" || env_name == "pythoncore-3.14-64") {
             env_name = "python-global";
        }

        // Verificar si es un venv
        bool is_venv = fs::exists(root_path / "pyvenv.cfg");
        if (is_venv) {
            // Si es un venv, el nombre de la carpeta es el nombre del entorno
            env_name = root_path.filename().string();
        }

        if (seen_paths.find(root_path.string()) == seen_paths.end()) {
            seen_paths.insert(root_path.string());
            envs.push_back({env_name, root_path.string(), Language::Python, PackageManager::Pip});
        }
    }

    // 2. Fallback: Si no encontró nada (ej. PATH roto), usar el comando python directo
    if (envs.empty()) {
        std::string python_exe = clean_str(ProcessRunner::run("python -c \"import sys; print(sys.executable)\" 2>&1"));
        if (!python_exe.empty() && python_exe.find("Error") == std::string::npos) {
            fs::path root = fs::path(python_exe).parent_path();
            if (root.filename() == "bin" || root.filename() == "Scripts") root = root.parent_path();
            envs.push_back({"python-global", root.string(), Language::Python, PackageManager::Pip});
        }
    }

    // 3. Buscar a mano el venv_prueba por si acaso "where" no lo detecta
    std::vector<std::string> local_venvs = {"../venv_prueba", "venv_prueba"};
    for (const auto& v : local_venvs) {
        fs::path venv_path(v);
        if (fs::exists(venv_path) && fs::exists(venv_path / "pyvenv.cfg")) {
            std::string abs_path = fs::absolute(venv_path).string();
            if (seen_paths.find(abs_path) == seen_paths.end()) {
                envs.push_back({venv_path.filename().string(), abs_path, Language::Python, PackageManager::Pip});
            }
        }
    }

    return envs;
}

std::vector<LibraryInfo> ScannerPython::scan_environment(const EnvironmentInfo& env) {
    std::vector<LibraryInfo> libs;
    fs::path root = fs::path(env.root_path);

    // Buscar las combinaciones posibles de dónde están las librerías
    std::vector<fs::path> candidates = {
        root / "Lib" / "site-packages",
        root / "lib" / "site-packages",
        root,
        root / "Lib",
        root / "lib"
    };

    fs::path site_packages;
    for (const auto& c : candidates) {
        if (fs::exists(c)) {
            for (const auto& entry : fs::directory_iterator(c)) {
                if (entry.path().filename().string().find(".dist-info") != std::string::npos) {
                    site_packages = c;
                    break;
                }
            }
        }
        if (!site_packages.empty()) break;
    }

    if (site_packages.empty()) return libs;

    // Leer las librerías
    for (const auto& dir : fs::directory_iterator(site_packages)) {
        std::string name = dir.path().filename().string();
        if (name.find(".dist-info") != std::string::npos) {
            LibraryInfo info;
            // Separar nombre y versión (ej: "colorama-0.4.6.dist-info")
            // Buscamos el último guion antes de la versión
            size_t ext_pos = name.find(".dist-info");
            if (ext_pos != std::string::npos) {
                std::string base = name.substr(0, ext_pos); // "colorama-0.4.6"
                size_t dash_pos = base.find_last_of('-');
                if (dash_pos != std::string::npos) {
                    info.name = base.substr(0, dash_pos); // "colorama"
                    info.version = base.substr(dash_pos + 1); // "0.4.6"
                } else {
                    info.name = base;
                    info.version = "unknown";
                }
            } else {
                info.name = name;
                info.version = "unknown";
            }
            
            // Limpieza extra: algunas librerías usan "_" en el dist-info (ej: charset_normalizer)
            // pero su nombre real usa "-"
            // Esto es un detalle cosmético, lo dejamos así por ahora.
            
            info.path = dir.path().string();
            info.environment = env.name;
            info.language = Language::Python;
            info.manager = PackageManager::Pip;
            info.managed = false;
            libs.push_back(info);
        }
    }

    return libs;
}

std::string ScannerPython::locate_package(const EnvironmentInfo& env, const std::string& pkg) {
    // Ya no lo usamos, lo dejamos por compatibilidad
    return "";
}

} // namespace colibri