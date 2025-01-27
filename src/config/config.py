import argparse

from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=['config/settings.yaml', 'config/.secrets.yaml'],
)

# `envvar_prefix` = export envvars with `export DYNACONF_FOO=bar`.
# `settings_files` = Load these files in the order.

parser = argparse.ArgumentParser(description="Переопределение настроек через аргументы командной строки")
parser.add_argument("--chatgpt.logging.enabled", choices=[0, 1], type=int, help="Включение/выключение логирования")
parser.add_argument("--chatgpt.configuration.name", type=str, help="Имя конфигурации")
parser.add_argument("--chatgpt.personalization.name", type=str, help="Имя персонализации")

args = parser.parse_args()

# Преобразование аргументов в словарь
cli_args = {key: value for key, value in vars(args).items() if value is not None}

# Обновление настроек на основе аргументов командной строки
settings.update(cli_args)
