#pragma once
#include <string>
#include "types.hpp"

namespace colibri {
class LibraryMover {
public:
    MovePlan plan_move(const LibraryInfo& lib, const std::string& dest_env_path);
    bool execute_move(const MovePlan& plan);
    bool copy_library(const LibraryInfo& lib, const std::string& dest_env_path);
    
    // --- NUEVA LÍNEA ---
    bool create_venv(const std::string& path, const std::string& python_exe);
};
} // namespace colibri