cmake_minimum_required(VERSION 3.18)
project(colibri_core LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_subdirectory(backend/third_party/pybind11)

pybind11_add_module(colibri_core
    backend/src/scanner_python.cpp
    backend/src/scanner_cpp.cpp
    backend/src/version_manager.cpp
    backend/src/library_mover.cpp
    backend/src/process_runner.cpp
    backend/src/dependency_resolver.cpp
    backend/src/logger.cpp
    backend/src/bindings.cpp
)

target_include_directories(colibri_core PRIVATE backend/include)