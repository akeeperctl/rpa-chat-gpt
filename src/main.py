import asyncio

from selenium_driverless import webdriver

import akp.root
from akp.logger import LOGGER
from akp.selenium_driverless_ex import webdriver_ex
from config.config import settings
from llm.chatgpt import ChatGPT
from llm.chatgpt_configuration import FLAGS, get_configuration

ROOT = akp.root.get_external_project_root()


async def start_driver():
    browser_path = ROOT / "browser"
    extensions_dir = browser_path / "extensions"
    extensions = [
        extensions_dir / "adguard"
    ]

    options = webdriver.ChromeOptions()
    [options.add_extension(i) for i in extensions]
    options.user_data_dir = browser_path / "user_data1"
    options.headless = True

    driver = await webdriver_ex.ChromeEx(options=options)
    return driver


async def main_async():
    LOGGER.enable(settings.chatgpt.logging.enabled == 1)

    driver = await start_driver()

    chat_gpt_config_name = settings.chatgpt.configuration.name
    chat_gpt_person_name = settings.chatgpt.personalization.name
    chat_gpt_config = get_configuration(chat_gpt_config_name)
    chat_gpt_person: ChatGPT.PersonalizationTypes = get_configuration(chat_gpt_person_name)

    try:
        chat_gpt_flag_new_chat = chat_gpt_config.get_flag(FLAGS.FLAG_START_NEW_CHAT)
        chat_gpt = ChatGPT(driver, True, config=chat_gpt_config, person=chat_gpt_person)

        if await chat_gpt.rpa.open_main_page():
            if chat_gpt_flag_new_chat:
                await chat_gpt.rpa.new_chat()

            LOGGER.info(f"Загружен {chat_gpt_config_name}, {chat_gpt_person.value.ai_character}")

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


def main():
    result = asyncio.run(main_async())
    return result


if __name__ == "__main__":
    main()
