#pragma once
#include <vector>
#include "types.hpp"

namespace colibri {
class ScannerPython {
public:
    std::vector<EnvironmentInfo> discover_environments();
    std::vector<LibraryInfo> scan_environment(const EnvironmentInfo& env);
private:
    std::string locate_package(const EnvironmentInfo& env, const std::string& pkg);
};
} // namespace colibri