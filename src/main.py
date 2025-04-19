import asyncio

import click
from selenium_driverless import webdriver

import akp.root
from akp.logger import LOGGER
from akp.selenium_driverless_ex import webdriver_ex
from config.config import settings
from llm.chatgpt import ChatGPT
from llm.chatgpt_config import list_config_names, get_config
from llm.chatgpt_person import list_person_names, get_person

ROOT = akp.root.get_external_project_root()

# Динамически формируем подсказки к --help
CONFIG_NAMES = list_config_names()
PERSON_NAMES = list_person_names()


async def start_driver():
    browser_path = ROOT / "browser"
    extensions_dir = browser_path / "extensions"
    extensions = [
        extensions_dir / "adguard"
    ]

    options = webdriver.ChromeOptions()
    [options.add_extension(i) for i in extensions]
    options.user_data_dir = browser_path / "user_data1"
    options.headless = False

    driver = await webdriver_ex.ChromeEx(options=options)
    return driver


async def main_async():
    LOGGER.enable(settings.chatgpt.logging.enabled == 1)

    driver = await start_driver()
    config_name = settings.chatgpt.configuration.name
    person_name = settings.chatgpt.personalization.name

    try:
        chat_gpt = ChatGPT(driver, True, config_name=config_name, person_name=person_name)

        if await chat_gpt.rpa.open_main_page():
            LOGGER.info(f"Загружен {config_name}, {person_name}")

            while True:
                prompt = input("Введите промт: ")
                if prompt == 'q':
                    break

                await chat_gpt.rpa.send_prompt(prompt)
                print(f"Ответ: {await chat_gpt.rpa.get_last_response(start_delay=1)}")

    except OSError:
        pass
    finally:
        if driver:
            await driver.quit(clean_dirs=False)

    return 0


@click.command()
@click.option(
    "--chatgpt-log",
    type=int,
    help=f"Включение/выключение логирования (0/1)")
@click.option(
    "--chatgpt-config-name",
    type=click.Choice(CONFIG_NAMES),
    help=f"Имя конфигурации.")
@click.option(
    "--chatgpt-person-name",
    type=click.Choice(PERSON_NAMES),
    help=f"Имя персонализации.")
def main(chatgpt_log, chatgpt_config_name, chatgpt_person_name):
    # Собираем непустые аргументы в словарь и применяем
    cli_args = {}

    if chatgpt_log is not None:
        cli_args["chatgpt.logging.enabled"] = chatgpt_log

    if chatgpt_config_name:
        cli_args["chatgpt.configuration.name"] = chatgpt_config_name

    if chatgpt_person_name:
        cli_args["chatgpt.personalization.name"] = chatgpt_person_name

    # Обновляем настройки
    settings.update(cli_args)

    config_name = settings.chatgpt.configuration.name
    person_name = settings.chatgpt.personalization.name
    log_enabled = bool(settings.chatgpt.logging.enabled)

    result = None

    try:
        config_main_page = get_config(config_name).main_page
        person_ai_character = get_person(person_name).ai_character

        # Пример вывода, чтобы проверить, что всё применилось
        click.echo(f"Текущая конфигурация: {config_name} {config_main_page}")
        click.echo(f"Текущая персонализация: {person_name} ({person_ai_character})")
        click.echo(f"Логирование включено: {log_enabled}")

        result = asyncio.run(main_async())
    except AttributeError:
        LOGGER.enable(True)
        LOGGER.error("При применении настроек произошла ошибка.", exc_info=True)

    return result


if __name__ == "__main__":
    main()
