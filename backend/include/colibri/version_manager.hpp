#pragma once
#include <string>
#include <vector>
#include "types.hpp"

namespace colibri {
class VersionManager {
public:
    static std::vector<int> parse_semver(const std::string& v);
    static int compare_semver(const std::string& a, const std::string& b);
    static bool is_newer(const std::string& candidate, const std::string& current);
    static std::vector<std::string> sort_versions(std::vector<std::string> versions);
    static std::vector<std::pair<LibraryInfo, std::string>> detect_outdated(const std::vector<LibraryInfo>& libs);
};
} // namespace colibri