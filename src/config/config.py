import click
from dynaconf import Dynaconf

# Загружаем конфигурацию из файлов
settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=['config/settings.yaml', 'config/.secrets.yaml'],
)

