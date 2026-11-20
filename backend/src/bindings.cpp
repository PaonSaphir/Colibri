#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "colibri/types.hpp"
#include "colibri/scanner_python.hpp"
#include "colibri/scanner_cpp.hpp"
#include "colibri/library_mover.hpp"
#include "colibri/version_manager.hpp"

namespace py = pybind11;
using namespace colibri;

PYBIND11_MODULE(colibri_core, m) {
    m.doc() = "Colibri core - Gestor inteligente de librerías";

    py::enum_<Language>(m, "Language")
        .value("Python", Language::Python)
        .value("Cpp", Language::Cpp);

    py::enum_<PackageManager>(m, "PackageManager")
        .value("Pip", PackageManager::Pip)
        .value("Vcpkg", PackageManager::Vcpkg)
        .value("Conan", PackageManager::Conan)
        .value("System", PackageManager::System);

    py::class_<LibraryInfo>(m, "LibraryInfo")
        .def_readonly("name", &LibraryInfo::name)
        .def_readonly("version", &LibraryInfo::version)
        .def_readonly("path", &LibraryInfo::path)
        .def_readonly("environment", &LibraryInfo::environment)
        .def_readonly("language", &LibraryInfo::language)
        .def_readonly("managed", &LibraryInfo::managed)
        .def_readonly("dependencies", &LibraryInfo::dependencies);

    py::class_<EnvironmentInfo>(m, "EnvironmentInfo")
        .def_readonly("name", &EnvironmentInfo::name)
        .def_readonly("root_path", &EnvironmentInfo::root_path)
        .def_readonly("language", &EnvironmentInfo::language)
        .def_readonly("manager", &EnvironmentInfo::manager);

    py::class_<MovePlan>(m, "MovePlan")
        .def_readonly("has_conflicts", &MovePlan::has_conflicts)
        .def_readonly("warnings", &MovePlan::warnings)
        .def_readonly("steps", &MovePlan::steps)
        .def_readonly("total_bytes", &MovePlan::total_bytes);

    py::class_<ScannerPython>(m, "ScannerPython")
        .def(py::init<>())
        .def("discover_environments", &ScannerPython::discover_environments)
        .def("scan_environment", &ScannerPython::scan_environment);

    py::class_<ScannerCpp>(m, "ScannerCpp")
        .def(py::init<>())
        .def("discover_environments", &ScannerCpp::discover_environments)
        .def("scan_environment", &ScannerCpp::scan_environment);

    // Aquí estaba el error: usamos el namespace correcto y cerramos bien las comillas
    py::class_<colibri::LibraryMover>(m, "LibraryMover")
        .def(py::init<>())
        .def("plan_move", &colibri::LibraryMover::plan_move)
        .def("execute_move", &colibri::LibraryMover::execute_move)
        .def("copy_library", &colibri::LibraryMover::copy_library)
        .def("create_venv", &colibri::LibraryMover::create_venv);

    py::class_<VersionManager>(m, "VersionManager")
        .def(py::init<>())
        .def_static("compare_semver", &VersionManager::compare_semver)
        .def_static("is_newer", &VersionManager::is_newer);
}