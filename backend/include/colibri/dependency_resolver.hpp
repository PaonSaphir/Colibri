#pragma once
#include <vector>
#include "types.hpp"
namespace colibri {
class DependencyResolver {
public:
    std::vector<LibraryInfo> find_orphans(const std::vector<LibraryInfo>& libs) { return {}; }
};
}