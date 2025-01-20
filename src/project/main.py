from typing import Optional

import akp.root
from akp.driver_shell import DriverShell
from akp.logger import LOGGER
from project.chatgpt import ChatGPT


def main():
    LOGGER.enable(False)
    root = akp.root.get_project_root()

    driver_user_data = root / "browser/user_data1"
    # driver_extensions = (
    #     str(root / "browser/extensions/adguard/5.0.183_0"),
    #     str(root / "browser/extensions/hola/1.237.569_0")
    # )
    # driver_extensions_str = ", ".join(driver_extensions)

    driver: Optional[DriverShell.Selenium] = None
    try:
        driver = DriverShell.SeleniumBaseUC(user_data_dir=driver_user_data)
        driver.execute_cdp_cmd('Network.enable', {})

        # Блокируем запросы по URL
        blocked_url = 'api.openai.com'
        driver.execute_cdp_cmd('Network.setBlockedURLs', {'urls': [blocked_url]})
        chat_gpt = ChatGPT(driver)

        if chat_gpt.RPA.open_main_page():

            # chat_gpt.RPA.send_prompt("Привет, меня зовут Даниил")
            # print(f"Ответ: {chat_gpt.RPA.get_last_response()}")
            #
            # chat_gpt.RPA.send_prompt("Я получил к тебе доступ через RPA и VPN")
            # print(f"Ответ: {chat_gpt.RPA.get_last_response()}")

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
            driver.driver.delete_all_cookies()
            driver.quit()


if __name__ == "__main__":
    main()
