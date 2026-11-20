#include "colibri/version_manager.hpp"
#include <sstream>
#include <algorithm>
#include <map>

namespace colibri {

std::vector<int> VersionManager::parse_semver(const std::string& v) {
    std::vector<int> out;
    std::stringstream ss(v);
    std::string tok;
    while (std::getline(ss, tok, '.')) {
        try {
            // Limpiar caracteres no numéricos (ej: 1.2.3rc1 -> 1.2.3)
            std::string num;
            for (char c : tok) {
                if (std::isdigit(c)) num += c;
                else break;
            }
            if (!num.empty()) out.push_back(std::stoi(num));
            else out.push_back(0);
        } catch (...) { out.push_back(0); }
    }
    return out;
}

int VersionManager::compare_semver(const std::string& a, const std::string& b) {
    auto va = parse_semver(a), vb = parse_semver(b);
    size_t n = std::max(va.size(), vb.size());
    for (size_t i = 0; i < n; ++i) {
        int x = i < va.size() ? va[i] : 0;
        int y = i < vb.size() ? vb[i] : 0;
        if (x < y) return -1;
        if (x > y) return 1;
    }
    return 0;
}

bool VersionManager::is_newer(const std::string& candidate, const std::string& current) {
    return compare_semver(candidate, current) > 0;
}

std::vector<std::string> VersionManager::sort_versions(std::vector<std::string> versions) {
    std::sort(versions.begin(), versions.end(), [](const std::string& a, const std::string& b) {
        return compare_semver(a, b) > 0; // Descendente
    });
    return versions;
}

std::vector<std::pair<LibraryInfo, std::string>> VersionManager::detect_outdated(const std::vector<LibraryInfo>& libs) {
    std::map<std::string, std::string> latest_versions;
    std::vector<std::pair<LibraryInfo, std::string>> outdated;

    // 1. Encontrar la versión más alta por nombre de librería
    for (const auto& lib : libs) {
        if (latest_versions.find(lib.name) == latest_versions.end() || 
            is_newer(lib.version, latest_versions[lib.name])) {
            latest_versions[lib.name] = lib.version;
        }
    }

    // 2. Comparar cada librería con la más alta encontrada
    for (const auto& lib : libs) {
        if (latest_versions[lib.name] != lib.version) {
            outdated.push_back({lib, latest_versions[lib.name]});
        }
    }
    return outdated;
}
} // namespace colibri