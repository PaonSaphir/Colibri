#pragma once
#include <string>
#include <vector>

namespace colibri {

enum class Language { Python, Cpp };
enum class PackageManager { Pip, Vcpkg, Conan, System, Unknown };

struct LibraryInfo {
    std::string name;
    std::string version;
    std::string path;
    std::string environment;
    Language language;
    PackageManager manager;
    bool managed;
    std::vector<std::string> dependencies;
};

struct EnvironmentInfo {
    std::string name;
    std::string root_path;
    Language language;
    PackageManager manager;
};

struct MoveStep {
    std::string source;
    std::string destination;
    uintmax_t size_bytes;
    bool will_overwrite;
};

struct MovePlan {
    std::vector<MoveStep> steps;
    uintmax_t total_bytes;
    std::vector<std::string> warnings;
    bool has_conflicts;
};

} // namespace colibri