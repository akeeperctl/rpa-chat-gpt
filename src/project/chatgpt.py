import time
import traceback
from typing import Optional

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from akp.driver_shell import DriverShell
from akp.logger import LOGGER


class ChatGPT:

    def __init__(self, driver_shell: DriverShell.Selenium):
        self.RPA = self._RPA(driver_shell, self)
        self._current_config = self.get_configs().openai_chatgpt

    class _Configurations:
        openai_chatgpt = {
            "main_page": "https://chatgpt.com/",
            "text_area_sel": "//div[@id='prompt-textarea']",
            "send_btn_sel": "//button[@data-testid='send-button']",
            "last_assistant_msg_sel": "//div[@data-message-author-role='assistant']",
            "thanks_dialog_sel": "//div[@role='dialog']"
        }

    class _RPA:

        def __init__(self, driver_shell: DriverShell.Selenium, _gpt_object):
            self.driver_shell = driver_shell
            self.gpt: ChatGPT = _gpt_object

            self._fetch_saved = False

        def _is_ready(self):
            link = self.driver_shell.get_current_link()
            if self.gpt.main_page not in link:
                LOGGER.warning(f"Драйвер не находится на странице ИИ-ассистента! Тек. страница: {link}")
                self.open_main_page()
                time.sleep(1)

        def _pass_thanks_window(self):
            self._is_ready()

            if self.gpt.thanks_dialog_sel:
                try:
                    dialog = self.driver_shell.find_element(by=By.XPATH, value=self.gpt.thanks_dialog_sel, seconds=1)
                    cancel_btn = dialog.find_element(by=By.XPATH, value=".//a[text()='Не входить']")
                    cancel_btn.click()
                except NoSuchElementException:
                    pass

        def _pass_need_login(self):
            login_url = "https://auth.openai.com/api/accounts/login?login_challenge="
            if login_url in self.driver_shell.get_current_link():
                raise Exception("Требуется авторизация. Попробуйте очистить куки.")

        def authorize(self):
            email_input = self.driver_shell.find_element(by=By.XPATH, value="//input[contains(@class, 'email-input')]")
            email_input.click()
            email_input.send_keys("my_yahoo_mail")

            continue_btn_sel = "//button[contains(@class, 'continue-btn)]"
            continue_btn = self.driver_shell.find_element(by=By.XPATH, value=continue_btn_sel)
            continue_btn.click()

            password_input = self.driver_shell.find_element(by=By.XPATH, value="//input[@id='password']", seconds=15)
            password_input.click()
            password_input.send_keys("my_pass")

            continue_btn = self.driver_shell.find_element(by=By.XPATH, value=continue_btn_sel)
            continue_btn.click()

            try:
                need_email_code = self.driver_shell.find_element(by=By.XPATH, value="//h1[text()='Проверьте свои входящие']")
                #TODO
            except NoSuchElementException:
                pass

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
                    self.driver_shell.go_to_page_if_different(self.gpt.main_page, log=False)
                    text_area = self.driver_shell.find_element(by=By.XPATH, value=self.gpt.text_area_sel, seconds=0)
                    #self._save_fetch()
                    #self._enable_fetch(False)
                except NoSuchElementException:
                    self.driver_shell.driver.refresh()
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
            #self._enable_fetch(True)

            text_area = self.driver_shell.find_element(by=By.XPATH, value=self.gpt.text_area_sel)
            text_area.click()
            text_area.send_keys(value)

            send_btn = self.driver_shell.find_element(by=By.XPATH, value=self.gpt.send_btn_sel)
            send_btn.click()

        def get_last_response(self, start_delay=5, timer=30):
            self._is_ready()
            self._pass_thanks_window()
            self._pass_need_login()
            #self._enable_fetch(True)

            current_timer = timer
            response: Optional[WebElement] = None

            time.sleep(start_delay)

            while True:

                # Ожидание генерации последнего сообщения
                try:
                    stop_btn = self.driver_shell.find_element(by=By.XPATH,
                                                              value="//button[@data-testid='stop-button']",
                                                              seconds=0)
                    continue
                except NoSuchElementException:
                    # Сообщение сгенерировано
                    time.sleep(0.5)
                    pass

                # Поиск последнего сообщения
                try:
                    responses = self.driver_shell.find_elements(by=By.XPATH,
                                                                value=self.gpt.last_assistant_msg_sel,
                                                                elem_name="Последний ответ от ассистента",
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

    def get_configs(self):
        return self._Configurations

    def set_config(self, config_name):
        """Установить текущую конфигурацию."""
        if hasattr(self._Configurations, config_name):
            self._current_config = getattr(self._Configurations, config_name)
        else:
            raise ValueError(f"Configuration '{config_name}' not found.")

    def get_current_config(self):
        """Получить текущий набор переменных."""
        return self._current_config

    @property
    def main_page(self):
        return self._current_config["main_page"]

    @property
    def text_area_sel(self):
        return self._current_config["text_area_sel"]

    @property
    def send_btn_sel(self):
        return self._current_config["send_btn_sel"]

    @property
    def last_assistant_msg_sel(self):
        return self._current_config["last_assistant_msg_sel"]

    @property
    def thanks_dialog_sel(self):
        return self._current_config["thanks_dialog_sel"]
