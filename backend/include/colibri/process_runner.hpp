#pragma once
#include <string>
#include <cstdio>
#include <array>

namespace colibri {
class ProcessRunner {
public:
    static std::string run(const std::string& cmd);
};
} // namespace colibri