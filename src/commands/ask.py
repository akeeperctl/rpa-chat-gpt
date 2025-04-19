import asyncio
import json

import click

from akp.logger import LOGGER
from config.config import apply_cli_settings, settings
from llm.chatgpt import ChatGPT
from llm.chatgpt_config import list_config_names
from llm.chatgpt_person import list_person_names
from utils import start_driver


@click.command()
@click.option("--chatgpt-log", type=int, help="Включить лог (0/1)")
@click.option("--chatgpt-config-name", type=click.Choice(list_config_names()), help="Имя конфигурации")
@click.option("--chatgpt-person-name", type=click.Choice(list_person_names()), help="Имя персонализации")
@click.option("--prompt", required=True, help="Промт, на который GPT должен ответить")
def ask(chatgpt_log, chatgpt_config_name, chatgpt_person_name, prompt):
    """Получить ответ от GPT и вывести JSON"""
    apply_cli_settings(chatgpt_log, chatgpt_config_name, chatgpt_person_name)
    LOGGER.enable(settings.chatgpt.logging.enabled == 1)
    result = asyncio.run(run_prompt(prompt))
    click.echo(json.dumps(result, ensure_ascii=False, indent=2))


async def run_prompt(prompt: str) -> dict:
    driver = await start_driver()
    chat_gpt = ChatGPT(driver, True,
                       config_name=settings.chatgpt.config.name,
                       person_name=settings.chatgpt.person.name)

    response = None
    try:
        if await chat_gpt.rpa.open_main_page():
            await chat_gpt.rpa.send_prompt(prompt)
            response = await chat_gpt.rpa.get_last_response(start_delay=1)
    finally:
        await driver.quit(clean_dirs=False)

    return {
        "config": settings.chatgpt.config.name,
        "person": settings.chatgpt.person.name,
        "prompt": prompt,
        "response": response
    }
