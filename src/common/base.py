# src/common/base.py

from src.common import config_manager, config_editor

def get_wrap_names() -> list:
    """
    Возвращает список всех доступных обёрток (конфигов).
    Использует list_config() из config_manager.
    """
    return config_manager.list_config()

def get_fuzz_cmd(wrap_name: str) -> str:
    """
    Возвращает команду для запуска фаззинга (fuzz_cmd) для заданной обёртки.
    Читает поле "fuzz.fuzz_cmd" через read_config_field() из config_editor.
    """
    return config_editor.read_config_field(wrap_name, "fuzz.fuzz_cmd")

def get_cov_cmd(wrap_name: str) -> str:
    """
    Возвращает команду для сбора покрытия (coverage_cmd) для заданной обёртки.
    Читает поле "coverage.coverage_cmd" через read_config_field().
    """
    return config_editor.read_config_field(wrap_name, "coverage.coverage_cmd")

def get_build_cmd(wrap_name: str) -> str:
    """
    Возвращает команду для сборки (build_cmd) для заданной обёртки.
    Читает поле "build.build_cmd" через read_config_field().
    """
    return config_editor.read_config_field(wrap_name, "build.build_cmd")

