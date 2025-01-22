import time
import traceback
from typing import Optional

from selenium.common import NoSuchElementException, StaleElementReferenceException, ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from akp.driver_shell import DriverShell
from akp.logger import LOGGER


class ChatGPTConfiguration:
    def __init__(self, values: dict):
        self.main_page = values["main_page"]
        self.text_area_sel = values["text_area_sel"]
        self.send_button_sel = values["send_button_sel"]
        self.stop_button_sel = values["stop_button_sel"]
        self.assistant_msg_sel = values["assistant_msg_sel"]
        self.thanks_dialog_sel = values["thanks_dialog_sel"]


class ChatGPTPersonalization:

    def __init__(self, values: dict):
        self.user_name = values["user_name"]
        self.user_position = values["user_position"]
        self.ai_response_length = values["ai_response_length"]
        self.ai_character = values["ai_character"]
        self.ai_job = values["ai_job"]

        self.prompt = f"""
            [Это настройки для диалога с тобой. 
            После закрывающейся квадратной скобки идет моё нормальное сообщение. 
            Отвечай на него естественно.
            Моё имя - {self.user_name};
            Моя должность - {self.user_position};
            Максимальная длина твоего сообщения - {self.ai_response_length} символов;
            Твой характер общения со мной - {self.ai_character};
            Твоя задача - {self.ai_job}.]
            """


class ChatGPT:

    def __init__(self, driver: DriverShell.Selenium, enable_personalization: bool):
        self.RPA = self._RPA(driver, self)
        self._current_config = self.get_configs().openai_chatgpt
        self._current_personalization = self.get_personalizations().default
        self._personalization_enabled = enable_personalization

    class _Personalizations:
        default = ChatGPTPersonalization({
            "user_name": "Даниил",
            "user_position": "Программист Python",
            "ai_response_length": 100,
            "ai_character": "Строгий старший программист",
            "ai_job": "Помогать советами и подсказывать идеи реализации"
        })

    class _Configurations:

        # FIXME: нужен хороший VPN, чтобы работал этот конфиг
        openai_chatgpt = ChatGPTConfiguration({
            "main_page": "https://chatgpt.com/",
            "text_area_sel": "//div[@id='prompt-textarea']",
            "send_button_sel": "//button[@data-testid='send-button']",
            "stop_button_sel": "//button[@data-testid='stop-button']",
            "assistant_msg_sel": "//div[@data-message-author-role='assistant']",
            "thanks_dialog_sel": "//div[@role='dialog']"
        })

        chatapp_chatgpt = ChatGPTConfiguration({
            "main_page": "https://chatgptchatapp.com/ru",
            "text_area_sel": "//textarea[@id='chat-input']",
            "send_button_sel": "//button[@class='btn-send-message']",
            "stop_button_sel": "//button[@class='btn-stop-response']",
            "assistant_msg_sel": "//div[@class='chat-box ai-completed']",
            "thanks_dialog_sel": None
        })

        # TODO:
        # https://chat.deepseek.com/
        # https://www.blackbox.ai/
        # https://gpt-chatbot.ru/chat-gpt-ot-openai-dlya-generacii-teksta

    class _RPA:

        def __init__(self, driver: DriverShell.Selenium, _gpt_object):
            self.driver = driver
            self.gpt: ChatGPT = _gpt_object

            self._fetch_saved = False

        def _is_ready(self):
            link = self.driver.get_current_link()
            if self.gpt.main_page not in link:
                LOGGER.warning(f"Драйвер не находится на странице ИИ-ассистента! Тек. страница: {link}")
                self.open_main_page()
                time.sleep(1)

        def _pass_thanks_window(self):
            self._is_ready()

            if self.gpt.thanks_dialog_sel:
                try:
                    dialog = self.driver.find_element(by=By.XPATH, value=self.gpt.thanks_dialog_sel, seconds=1)
                    cancel_btn = dialog.find_element(by=By.XPATH, value=".//a[text()='Не входить']")
                    cancel_btn.click()
                except NoSuchElementException:
                    pass

        def _pass_need_login(self):
            login_url = "https://auth.openai.com/api/accounts/login?login_challenge="
            if login_url in self.driver.get_current_link():
                raise Exception("Требуется авторизация. Попробуйте очистить куки.")

        # def authorize(self):
        #     email_input = self.driver.find_element(by=By.XPATH, value="//input[contains(@class, 'email-input')]")
        #     email_input.click()
        #     email_input.send_keys("my_yahoo_mail")
        #
        #     continue_btn_sel = "//button[contains(@class, 'continue-btn)]"
        #     continue_btn = self.driver.find_element(by=By.XPATH, value=continue_btn_sel)
        #     continue_btn.click()
        #
        #     password_input = self.driver.find_element(by=By.XPATH, value="//input[@id='password']", seconds=15)
        #     password_input.click()
        #     password_input.send_keys("my_pass")
        #
        #     continue_btn = self.driver.find_element(by=By.XPATH, value=continue_btn_sel)
        #     continue_btn.click()
        #
        #     try:
        #         need_email_code = self.driver.find_element(by=By.XPATH,
        #                                                          value="//h1[text()='Проверьте свои входящие']")
        #         #TODO
        #     except NoSuchElementException:
        #         pass

        def open_main_page(self, timer=30):
            """
            Попытка открыть главную страницу за указанное время
            :param timer: время в секундах
            :return: True - открылась успешно
            """

            text_area: Optional[WebElement] = None

            current_timer = timer

            while True:

                # Попытка открыть чат
                try:
                    self.driver.go_to_page_if_different(self.gpt.main_page, log=False)
                    text_area = self.driver.find_element(by=By.XPATH, value=self.gpt.text_area_sel, seconds=0)
                except NoSuchElementException:
                    self.driver.driver.refresh()
                finally:

                    # Отсчет таймера
                    current_timer -= 1
                    if text_area or current_timer <= 0:
                        break

                    time.sleep(1)

            result = False if not text_area else True
            return result

        def send_prompt(self, value: str):
            self._is_ready()
            self._pass_thanks_window()
            self._pass_need_login()

            if self.gpt.is_personalization_enabled():
                new_value = self.gpt.get_current_personalization().prompt + value
                value = new_value
                value = value.replace("\n", "")

            try:
                text_area = self.driver.find_element(by=By.XPATH, value=self.gpt.text_area_sel)
                text_area.click()
                text_area.send_keys(value)

                send_btn = self.driver.find_element(by=By.XPATH, value=self.gpt.send_button_sel)
                self.driver.scroll_to_elem(send_btn)
                send_btn.click()
            except (NoSuchElementException, ElementNotInteractableException):
                LOGGER.error(f"Ошибка в отправке промта...")

        def get_last_response(self, start_delay=5, timer=30):
            self._is_ready()
            self._pass_thanks_window()
            self._pass_need_login()

            current_timer = timer
            response: Optional[WebElement] = None

            time.sleep(start_delay)

            while True:

                # Ожидание генерации последнего сообщения
                try:
                    stop_btn = self.driver.find_element(by=By.XPATH, value=self.gpt.stop_button_sel, seconds=1)
                    if stop_btn and stop_btn.is_displayed():
                        continue
                except StaleElementReferenceException:
                    continue
                except NoSuchElementException:
                    # Сообщение сгенерировано
                    time.sleep(0.5)
                    pass

                # Поиск последнего сообщения
                try:
                    responses = self.driver.find_elements(by=By.XPATH,
                                                          value=self.gpt.assistant_msg_sel,
                                                          elem_name="Ответы от ассистента",
                                                          seconds=0)

                    response = responses[-1]
                except NoSuchElementException:
                    LOGGER.warning("Не нашел последнего сообщения от ассистента")
                except IndexError:
                    LOGGER.error(f"Ошибка при получении последнего сообщения: {traceback.format_exc()}")
                finally:
                    current_timer -= 1
                    if response or current_timer <= 0:
                        break

                    time.sleep(1)

            if response:
                return response.text.strip()
            else:
                return None

    def is_personalization_enabled(self):
        return self._personalization_enabled

    def enable_personalization(self, enable: bool):
        self._personalization_enabled = enable

    def get_personalizations(self):
        return self._Personalizations

    def set_personalization(self, persona: ChatGPTPersonalization):
        self._current_personalization = persona

    def get_current_personalization(self):
        return self._current_personalization

    def get_configs(self):
        return self._Configurations

    def set_config(self, configuration: ChatGPTConfiguration):
        """Установить текущую конфигурацию."""
        self._current_config = configuration

    def get_current_config(self):
        """Получить текущий набор переменных."""
        return self._current_config

    @property
    def main_page(self):
        return self._current_config.main_page

    @property
    def text_area_sel(self):
        return self._current_config.text_area_sel

    @property
    def send_button_sel(self):
        return self._current_config.send_button_sel

    @property
    def assistant_msg_sel(self):
        return self._current_config.assistant_msg_sel

    @property
    def thanks_dialog_sel(self):
        return self._current_config.thanks_dialog_sel

    @property
    def stop_button_sel(self):
        return self._current_config.stop_button_sel
