from typing import Optional, Callable

import akp.root
from akp.driver_shell import DriverShell
from akp.logger import LOGGER
from config.config import settings
from llm.chatgpt import ChatGPT
from llm.chatgpt_configuration import FLAGS


class ConsoleCommand:
    def __init__(self, name: str, func: Callable):
        self._name = name
        self._func = func

    def execute(self, *args, **kwargs):
        self._func(*args, **kwargs)

    def get_name(self):
        return self._name


def main():
    LOGGER.enable(settings.chatgpt.logging.enabled == 1)

    # while True:
    #     input_text = input("Введите команду: ")

    root = akp.root.get_project_root()

    driver_user_data = root / "browser/user_data1"
    # driver_extensions = (
    #     str(root / "browser/extensions/adguard/5.0.183_0"),
    #     str(root / "browser/extensions/hola/1.237.569_0")
    # )
    # driver_extensions_str = ", ".join(driver_extensions)
    driver: Optional[DriverShell.Selenium] = None

    chat_gpt_config_name = settings.chatgpt.configuration.name
    chat_gpt_person_name = settings.chatgpt.personalization.name
    chat_gpt_config: ChatGPT.ConfigurationTypes = getattr(ChatGPT.ConfigurationTypes, chat_gpt_config_name)
    chat_gpt_person: ChatGPT.PersonalizationTypes = getattr(ChatGPT.PersonalizationTypes, chat_gpt_person_name)

    try:
        chat_gpt_flag_incognito = chat_gpt_config.value.get_flag(FLAGS.FLAG_INCOGNITO_MODE)
        chat_gpt_flag_new_chat = chat_gpt_config.value.get_flag(FLAGS.FLAG_START_NEW_CHAT)

        driver = DriverShell.SeleniumBaseUC(user_data_dir=driver_user_data, headless=True, incognito=chat_gpt_flag_incognito)

        chat_gpt = ChatGPT(driver, enable_personalization=True)
        chat_gpt.set_config(chat_gpt_config)
        chat_gpt.set_personalization(chat_gpt_person)

        if chat_gpt.RPA.open_main_page():

            if chat_gpt_flag_new_chat:
                chat_gpt.RPA.new_chat()

            while True:
                prompt = input("Введите промт: ")
                if prompt == 'q':
                    break

                chat_gpt.RPA.send_prompt(prompt)
                print(f"Ответ: {chat_gpt.RPA.get_last_response(start_delay=1)}")

    except OSError:
        pass
    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    main()
