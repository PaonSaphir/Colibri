#include "colibri/scanner_cpp.hpp"
#include <filesystem>
#include <fstream>
#include <sstream>
#include <regex>
#include <algorithm>

namespace fs = std::filesystem;

namespace colibri {

// Helper para leer un archivo de texto completo
static std::string read_file(const fs::path& path) {
    std::ifstream f(path);
    if (!f.is_open()) return "";
    std::stringstream buffer;
    buffer << f.rdbuf();
    return buffer.str();
}

// Helper para buscar un patrón regex
static std::string find_regex(const std::string& text, const std::string& pattern) {
    std::regex re(pattern);
    std::smatch match;
    if (std::regex_search(text, match, re) && match.size() > 1) {
        return match[1].str();
    }
    return "";
}

std::vector<EnvironmentInfo> ScannerCpp::discover_environments() {
    std::vector<EnvironmentInfo> envs;
    
    // 1. VCPKG
    if (const char* v = getenv("VCPKG_ROOT"); v && fs::exists(v)) {
        envs.push_back({"vcpkg", v, Language::Cpp, PackageManager::Vcpkg});
    } else {
        // Buscar en rutas comunes si no está en el PATH
        std::vector<std::string> common_vcpkg = {
            "C:/vcpkg", "C:/dev/vcpkg", 
            std::string(getenv("USERPROFILE") ? getenv("USERPROFILE") : "") + "/vcpkg"
        };
        for (const auto& p : common_vcpkg) {
            if (fs::exists(p)) {
                envs.push_back({"vcpkg", p, Language::Cpp, PackageManager::Vcpkg});
                break;
            }
        }
    }
    
    // 2. CONAN
    const char* home = getenv("USERPROFILE");
    if (!home) home = getenv("HOME");
    if (home) {
        std::string conan2 = std::string(home) + "/.conan2";
        std::string conan1 = std::string(home) + "/.conan";
        if (fs::exists(conan2)) {
            envs.push_back({"conan2", conan2, Language::Cpp, PackageManager::Conan});
        } else if (fs::exists(conan1)) {
            envs.push_back({"conan1", conan1, Language::Cpp, PackageManager::Conan});
        }
    }

    // 3. SISTEMA (Compiladores)
#ifdef _WIN32
    // Visual Studio
    std::vector<std::string> vs_paths = {
        "C:/Program Files/Microsoft Visual Studio/2022/Community/VC/Tools/MSVC",
        "C:/Program Files/Microsoft Visual Studio/2022/Professional/VC/Tools/MSVC",
        "C:/Program Files/Microsoft Visual Studio/2022/Enterprise/VC/Tools/MSVC",
        "C:/Program Files (x86)/Microsoft Visual Studio/2019/Community/VC/Tools/MSVC"
    };
    for (const auto& p : vs_paths) {
        if (fs::exists(p)) {
            envs.push_back({"Visual Studio", p, Language::Cpp, PackageManager::System});
            break;
        }
    }
    // MinGW
    if (fs::exists("C:/msys64/mingw64/include")) {
        envs.push_back({"MinGW64", "C:/msys64/mingw64/include", Language::Cpp, PackageManager::System});
    }
#else
    envs.push_back({"sistema", "/usr/include", Language::Cpp, PackageManager::System});
#endif
    return envs;
}

std::vector<LibraryInfo> ScannerCpp::scan_environment(const EnvironmentInfo& env) {
    std::vector<LibraryInfo> libs;
    fs::path root = fs::path(env.root_path);

    if (env.manager == PackageManager::Vcpkg) {
        // vcpkg guarda las libs en installed/<triplet>/share/<pkg>/
        fs::path installed = root / "installed";
        if (!fs::exists(installed)) return libs;

        // Buscar la carpeta del triplet (x64-windows, x64-linux, etc.)
        for (const auto& triplet : fs::directory_iterator(installed)) {
            fs::path share = triplet.path() / "share";
            if (!fs::exists(share)) continue;
            
            for (const auto& pkg : fs::directory_iterator(share)) {
                if (!pkg.is_directory()) continue;
                std::string pkg_name = pkg.path().filename().string();
                
                // --- NUEVO: Filtrar herramientas internas de vcpkg ---
                if (pkg_name == "pkgconfig" || 
                    pkg_name == "vcpkg-cmake" || 
                    pkg_name == "vcpkg-cmake-config" ||
                    pkg_name == "vcpkg-get-python-packages" ||
                    pkg_name == "vcpkg-msbuild" ||
                    pkg_name == "vcpkg-msbuild-build" ||
                    pkg_name == "vcpkg-tool-meson") {
                    continue; 
                }
                
                LibraryInfo info;
                info.name = pkg.path().filename().string();
                info.path = pkg.path().string();
                info.environment = env.name;
                info.language = Language::Cpp;
                info.manager = PackageManager::Vcpkg;
                info.managed = false;
                
                // Intentar leer la versión de vcpkg.spdx.json o CONTROL
                fs::path spdx = pkg.path() / "vcpkg.spdx.json";
                fs::path control = pkg.path() / "CONTROL";
                
                if (fs::exists(spdx)) {
                    std::string content = read_file(spdx);
                    // Buscar "versionInfo": "1.2.3" de forma manual, sin regex complejas
                    size_t pos = content.find("\"versionInfo\"");
                    if (pos != std::string::npos) {
                        size_t start = content.find("\"", pos + 13);
                        size_t end = content.find("\"", start + 1);
                        if (start != std::string::npos && end != std::string::npos) {
                            info.version = content.substr(start + 1, end - start - 1);
                        }
                    }
                } else if (fs::exists(control)) {
                    std::string content = read_file(control);
                    size_t pos = content.find("Version:");
                    if (pos != std::string::npos) {
                        size_t start = content.find_first_not_of(" \t", pos + 8);
                        size_t end = content.find_first_of("\r\n", start);
                        info.version = content.substr(start, end - start);
                    }
                }
                
                if (info.version.empty()) info.version = "unknown";
                libs.push_back(info);
            }
        }
    } 
    else if (env.manager == PackageManager::Conan) {
        // Conan 2 guarda los paquetes en <home>/p/<hash>/p/
        fs::path p_dir = root / "p";
        if (!fs::exists(p_dir)) return libs;
        
        for (const auto& hash_dir : fs::directory_iterator(p_dir)) {
            fs::path pkg_dir = hash_dir.path() / "p";
            if (!fs::exists(pkg_dir)) continue;
            
            for (const auto& d : fs::directory_iterator(pkg_dir)) {
                if (!d.is_directory()) continue;
                
                LibraryInfo info;
                info.name = d.path().filename().string();
                info.path = d.path().string();
                info.environment = env.name;
                info.language = Language::Cpp;
                info.manager = PackageManager::Conan;
                info.managed = false;
                
                // Conan guarda metadatos en conaninfo.txt o conanmanifest.txt
                fs::path info_file = hash_dir.path() / "conaninfo.txt";
                if (fs::exists(info_file)) {
                    std::string content = read_file(info_file);
                    info.version = find_regex(content, R"(version=([^\r\n]+))");
                }
                if (info.version.empty()) info.version = "unknown";
                libs.push_back(info);
            }
        }
    }
    else {
        // Sistema (Visual Studio / MinGW)
        if (!fs::exists(root)) return libs;
        
        // En VS, buscamos carpetas de versiones
        if (env.name == "Visual Studio") {
            for (const auto& ver : fs::directory_iterator(root)) {
                if (ver.is_directory()) {
                    LibraryInfo info;
                    info.name = "MSVC Toolchain " + ver.path().filename().string();
                    info.version = ver.path().filename().string();
                    info.path = ver.path().string();
                    info.environment = env.name;
                    info.language = Language::Cpp;
                    info.manager = PackageManager::System;
                    info.managed = false;
                    libs.push_back(info);
                }
            }
        } else {
            // MinGW o sistema: listar carpetas de primer nivel
            for (const auto& d : fs::directory_iterator(root)) {
                if (d.is_directory()) {
                    LibraryInfo info;
                    info.name = d.path().filename().string();
                    info.version = "system";
                    info.path = d.path().string();
                    info.environment = env.name;
                    info.language = Language::Cpp;
                    info.manager = PackageManager::System;
                    info.managed = false;
                    libs.push_back(info);
                }
            }
        }
    }

    return libs;
}

} // namespace colibri