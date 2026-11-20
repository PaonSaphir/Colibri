#include "colibri/library_mover.hpp"
#include <filesystem>
#include <stdexcept>
#include "colibri/process_runner.hpp"

namespace fs = std::filesystem;

namespace colibri {

MovePlan LibraryMover::plan_move(const LibraryInfo& lib, const std::string& dest_env_path) {
    MovePlan plan;
    plan.has_conflicts = false;
    plan.total_bytes = 0;

    fs::path src = lib.path;
    if (!fs::exists(src)) {
        plan.warnings.push_back("El origen no existe: " + src.string());
        plan.has_conflicts = true;
        return plan;
    }

    // Calcular la ruta de destino correcta (dentro de Lib/site-packages si es Windows)
    fs::path dest_env(dest_env_path);
    fs::path final_dest;
    
#ifdef _WIN32
    if (fs::exists(dest_env / "Lib")) {
        final_dest = dest_env / "Lib" / "site-packages" / src.filename();
    } else {
        final_dest = dest_env / src.filename();
    }
#else
    // En Linux/Mac buscar lib/python3.x/site-packages
    final_dest = dest_env / src.filename(); // Simplificado para el ejemplo
#endif
    
    MoveStep step;
    step.source = src.string();
    step.destination = final_dest.string();
    step.will_overwrite = fs::exists(final_dest);
    
    if (step.will_overwrite) {
        plan.warnings.push_back("El destino ya contiene una carpeta con este nombre.");
        plan.has_conflicts = true;
    }

    plan.steps.push_back(step);
    return plan;
}

bool LibraryMover::execute_move(const MovePlan& plan) {
    if (plan.has_conflicts) throw std::runtime_error("No se puede ejecutar: hay conflictos.");
    
    for (const auto& step : plan.steps) {
        try {
            fs::create_directories(fs::path(step.destination).parent_path());
            fs::rename(step.source, step.destination);
        } catch (...) {
            // Fallback si es otra unidad de disco
            fs::copy(step.source, step.destination, fs::copy_options::recursive);
            fs::remove_all(step.source);
        }
    }
    return true;
}

bool LibraryMover::copy_library(const LibraryInfo& lib, const std::string& dest_env_path) {
    fs::path src = lib.path;
    fs::path dst = fs::path(dest_env_path) / src.filename();
    if (fs::exists(dst)) throw std::runtime_error("El destino ya existe.");
    fs::copy(src, dst, fs::copy_options::recursive);
    return true;
}

bool LibraryMover::create_venv(const std::string& path, const std::string& python_exe) {
    try {
        fs::create_directories(path);
        std::string cmd = "\"" + python_exe + "\" -m venv \"" + path + "\"";
        ProcessRunner::run(cmd);
        return fs::exists(fs::path(path) / "pyvenv.cfg");
    } catch (...) { return false; }
}

} // namespace colibri