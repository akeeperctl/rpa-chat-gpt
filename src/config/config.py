import click
from dynaconf import Dynaconf

# Загружаем конфигурацию из файлов
settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=['config/settings.yaml', 'config/.secrets.yaml'],
)


def apply_cli_settings(chatgpt_log, chatgpt_config_name, chatgpt_person_name):
    cli_args = {}

    if chatgpt_log is not None:
        cli_args["chatgpt.logging.enabled"] = chatgpt_log

    if chatgpt_config_name:
        cli_args["chatgpt.config.name"] = chatgpt_config_name

    if chatgpt_person_name:
        cli_args["chatgpt.person.name"] = chatgpt_person_name

    settings.update(cli_args)
