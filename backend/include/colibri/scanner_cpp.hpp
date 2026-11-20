#pragma once
#include <vector>
#include "types.hpp"

namespace colibri {
class ScannerCpp {
public:
    std::vector<EnvironmentInfo> discover_environments();
    std::vector<LibraryInfo> scan_environment(const EnvironmentInfo& env);
};
} // namespace colibri