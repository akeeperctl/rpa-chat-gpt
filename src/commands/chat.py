from typing import Optional

import click
import asyncio

from akp.logger import LOGGER
from config.config import settings, apply_cli_settings
from llm.chatgpt import ChatGPT
from llm.chatgpt_config import list_config_names
from llm.chatgpt_person import list_person_names, get_person
from utils import start_driver

_CHAT_GPT_INSTANCE: Optional[ChatGPT] = None

_COMMANDS = {
    '-q': (lambda: _cmd_exit(_CHAT_GPT_INSTANCE), "Выход из чата."),
    '--quit': (lambda: _cmd_exit(_CHAT_GPT_INSTANCE), "Выход из чата."),
    '--exit': (lambda: _cmd_exit(_CHAT_GPT_INSTANCE), "Выход из чата."),
    '--help': (lambda: _cmd_show_help(_CHAT_GPT_INSTANCE), "Показать доступные команды."),
    '-h': (lambda: _cmd_show_help(_CHAT_GPT_INSTANCE), "Показать доступные команды."),
    '--person': (lambda: _cmd_change_person(_CHAT_GPT_INSTANCE), "Изменить текущую персону."),
}


def _cmd_change_person(chatgpt: ChatGPT):
    click.echo(f"Текущая персона: {chatgpt.get_person().name}")

    person_names = list_person_names()
    click.echo("Доступные персоны:")
    for idx, name in enumerate(person_names, 1):
        click.echo(f"  {idx}. {name} ({get_person(name).ai_character})")

    choice = click.prompt("Введите номер новой персоны", type=int)
    if 1 <= choice <= len(person_names):
        new_person = person_names[choice - 1]
        settings.update({"chatgpt.person.name": new_person})
        chatgpt.set_person(new_person)
        click.echo(f"Персона изменена на: {new_person}")
    else:
        click.echo("Неверный выбор.")

    return None


def _cmd_exit(chatgpt: ChatGPT):
    click.echo("Выход из чата.")
    return 'exit'


def _cmd_show_help(chatgpt: ChatGPT):
    click.echo("Доступные команды:")
    for cmd, (func, description) in _COMMANDS.items():
        click.echo(f"  {cmd.ljust(12)} {description}")
    return None


@click.command()
@click.option("--chatgpt-log", type=int, help="Включить лог (0/1)")
@click.option("--chatgpt-config-name", type=click.Choice(list_config_names()), help="Имя конфигурации")
@click.option("--chatgpt-person-name", type=click.Choice(list_person_names()), help="Имя персонализации")
def chat(chatgpt_log, chatgpt_config_name, chatgpt_person_name):
    """Интерактивный режим чата"""
    apply_cli_settings(chatgpt_log, chatgpt_config_name, chatgpt_person_name)
    LOGGER.enable(settings.chatgpt.logging.enabled == 1)
    asyncio.run(run_chat())


async def run_chat():
    global _CHAT_GPT_INSTANCE

    driver = await start_driver()
    chat_gpt = _CHAT_GPT_INSTANCE = ChatGPT(driver, True,
                                            config_name=settings.chatgpt.config.name,
                                            person_name=settings.chatgpt.person.name)

    try:
        if await chat_gpt.rpa.open_main_page():

            config_name = chat_gpt.get_config().name
            person_name = chat_gpt.get_person().name
            config_main_page = chat_gpt.get_config().main_page
            person_ai_character = chat_gpt.get_person().ai_character

            click.echo(f"Конфигурация: {config_name} ({config_main_page})\n"
                       f"Персона: {person_name} ({person_ai_character})")

            while True:
                prompt = click.prompt("Введите промт")
                command = prompt.strip().lower()
                if command in _COMMANDS:
                    result = _COMMANDS[command][0]()
                    if result == 'exit':
                        break
                    continue

                # Обработка обычного промта
                await chat_gpt.rpa.send_prompt(prompt)
                response = await chat_gpt.rpa.get_last_response(start_delay=1)
                click.echo(f"Ответ: {response}")

    finally:
        if driver:
            await driver.quit(clean_dirs=False)
