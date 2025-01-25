import time
import traceback
from enum import Enum
from typing import Optional

from selenium.common import NoSuchElementException, StaleElementReferenceException, ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from akp.driver_shell import DriverShell
from akp.logger import LOGGER
from config import settings
from llm.chatgpt_configuration import BaseConfigurationTypes
from llm.chatgpt_personalization import BasePersonalizationTypes


class ChatGPT:
    ConfigurationTypes = BaseConfigurationTypes
    PersonalizationTypes = BasePersonalizationTypes

    def __init__(self, driver: DriverShell.Selenium, enable_personalization: bool):
        self.RPA = self._RPA(driver, self)
        self._current_config = self.ConfigurationTypes.DEFAULT
        self._current_personalization = self.PersonalizationTypes.DEFAULT
        self._personalization_enabled = enable_personalization

    class _RPA:

        def __init__(self, driver: DriverShell.Selenium, _gpt_object):
            self.driver = driver
            self.gpt: ChatGPT = _gpt_object

            self._authorized = False

        def _is_ready(self):
            link = self.driver.get_current_link()
            cfg = self.gpt.get_current_config()

            if cfg.value.get_page('main_page') not in link:
                LOGGER.warning(f"Драйвер не находится на странице ИИ-ассистента! Тек. страница: {link}")
                self.open_main_page()
                time.sleep(1)

        def _pass_thanks_window(self):
            self._is_ready()
            cfg = self.gpt.get_current_config()
            thanks_sel = cfg.value.get_selector('thanks_dialog_sel')
            cancel_sel = ".//a[text()='Не входить']"

            if thanks_sel:
                try:
                    dialog = self.driver.find_element(by=By.XPATH, value=thanks_sel, seconds=1)
                    cancel_btn = dialog.find_element(by=By.XPATH, value=cancel_sel)
                    cancel_btn.click()
                except NoSuchElementException:
                    pass

        # def _pass_need_login(self):
        #     login_url = "https://auth.openai.com/api/accounts/login?login_challenge="
        #     if login_url in self.driver.get_current_link():
        #         raise Exception("Требуется авторизация. Попробуйте очистить куки.")

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

        def authorize(self):
            if not self._authorized:

                cfg = self.gpt.get_current_config()
                login = settings.chatgpt[cfg.name].login
                password = settings.chatgpt[cfg.name].password

                try:

                    login_page = cfg.value.get_page('login_page')

                    # Получение селекторов
                    login_checkbox_sel = cfg.value.get_selector('login_checkbox_sel')
                    login_sel = cfg.value.get_selector('login_sel')
                    login_button_sel = cfg.value.get_selector('login_button_sel')
                    password_sel = cfg.value.get_selector('password_sel')

                    self.driver.go_to_page_if_different(login_page)

                    # Ввод данных в поля
                    login_element = self.driver.find_element(by=By.XPATH, value=login_sel)
                    login_element.click()
                    login_element.send_keys(login)

                    password_element = self.driver.find_element(by=By.XPATH, value=password_sel)
                    password_element.click()
                    password_element.send_keys(password)

                    if login_checkbox_sel:
                        login_checkbox_element = self.driver.find_element(by=By.XPATH, value=login_checkbox_sel)
                        login_checkbox_element.click()

                    if login_button_sel:
                        login_button_element = self.driver.find_element(by=By.XPATH, value=login_button_sel)
                        login_button_element.click()

                    self.driver.wait_element_disappear(login_element)
                    self._authorized = True
                except:
                    LOGGER.warning(f"Авторизация не будет выполнена.")
                    LOGGER.error(f"Причина: {traceback.format_exc()}")
                    self._authorized = False

            return self._authorized

        def new_chat(self):
            cfg = self.gpt.get_current_config()

            new_chat_sel = cfg.value.get_selector("new_chat_sel")
            if not new_chat_sel:
                return False

            try:
                new_chat_element = self.driver.find_element(by=By.XPATH, value=new_chat_sel)
                new_chat_element.click()
                self.driver.sleep(1)
                return True

            except NoSuchElementException:
                return False

        def open_main_page(self, timer=30):
            """
            Попытка открыть главную страницу за указанное время
            :param timer: время в секундах
            :return: True - открылась успешно
            """
            cfg = self.gpt.get_current_config()

            text_area: Optional[WebElement] = None
            current_timer = timer

            # Проверяем, требуется ли обработка перенаправления
            requires_redirect_handling = cfg.name == self.gpt.ConfigurationTypes.DEEPSEEK.name

            while True:

                # Попытка открыть чат
                try:
                    # Открытие главной страницы
                    self.driver.go_to_page_if_different(cfg.value.get_page('main_page'), log=False)

                    # Если DEEPSEEK, проверяем текущий URL на перенаправление
                    if requires_redirect_handling:
                        current_url = self.driver.driver.current_url
                        expected_login_page = cfg.value.get_page('login_page')

                        if current_url == expected_login_page:
                            # Выполняем логику на странице логина (например, авторизация)
                            self.authorize()

                            # Пытаемся снова открыть главную страницу
                            continue

                    text_area = self.driver.find_element(by=By.XPATH, value=cfg.value.get_selector('text_area_sel'),
                                                         seconds=0)
                    break
                except NoSuchElementException:
                    self.driver.driver.refresh()

                    # Отсчет таймера
                    current_timer -= 1
                    if text_area or current_timer <= 0:
                        break

                    time.sleep(1)

                except AttributeError:
                    LOGGER.warning("При попытке открыть главную страницу произошла ошибка: ")
                    LOGGER.error(traceback.format_exc())
                    return False

            return bool(text_area)

        def send_prompt(self, value: str):
            self._is_ready()
            self._pass_thanks_window()

            cfg = self.gpt.get_current_config()

            if self.gpt.is_personalization_enabled():
                new_value = self.gpt.get_current_personalization().value.prompt + value
                value = new_value
                value = value.replace("\n", "")

            try:
                text_area = self.driver.find_element(by=By.XPATH, value=cfg.value.get_selector('text_area_sel'))
                text_area.click()
                text_area.send_keys(value)

                send_btn = self.driver.find_element(by=By.XPATH, value=cfg.value.get_selector('send_button_sel'))
                self.driver.scroll_to_elem(send_btn)
                send_btn.click()
            except (NoSuchElementException, ElementNotInteractableException) as e:
                LOGGER.error(f"Ошибка в отправке промта: {e}")
                # LOGGER.error(traceback.format_exc())

        def get_last_response(self, start_delay=5, timer=30):
            self._is_ready()
            self._pass_thanks_window()

            cfg = self.gpt.get_current_config()

            current_timer = timer
            response: Optional[WebElement] = None

            LOGGER.debug("Сообщение генерируется...")
            time.sleep(start_delay)

            while True:

                # Ожидание генерации последнего сообщения
                try:
                    stop_btn = self.driver.find_element(by=By.XPATH,
                                                        value=cfg.value.get_selector('stop_button_sel'),
                                                        seconds=1)
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
                                                          value=cfg.value.get_selector('assistant_msg_sel'),
                                                          elem_name="Ответы от ассистента",
                                                          seconds=0)

                    if len(responses) > 0:
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
                LOGGER.debug("Сообщение сгенерировано!")
                return response.text.strip()
            else:
                LOGGER.debug("Сообщение не сгенерировано!")
                return None

    def is_personalization_enabled(self):
        return self._personalization_enabled

    def enable_personalization(self, enable: bool):
        self._personalization_enabled = enable

    def set_personalization(self, persona_type: PersonalizationTypes):
        self._current_personalization = persona_type

    def get_current_personalization(self):
        return self._current_personalization

    def set_config(self, config_type: ConfigurationTypes):
        """Установить текущую конфигурацию."""
        self._current_config = config_type

    def get_current_config(self):
        """Получить текущий набор переменных."""
        return self._current_config


if __name__ == "__main__":
    LOGGER.info("Пример работы RPA в различных ChatGPT")

    import akp.root

    root = akp.root.get_project_root()
    driver_user_data = root / "browser/user_data1"

    _driver: Optional[DriverShell.Selenium] = None
    try:
        _driver = DriverShell.SeleniumBaseUC(user_data_dir=driver_user_data, headless=False)
        chat_gpt = ChatGPT(_driver, enable_personalization=True)

        chat_gpt_config_name = settings.chatgpt.configuration.name
        chat_gpt_person_name = settings.chatgpt.personalization.name

        chat_gpt_config = getattr(ChatGPT.ConfigurationTypes, chat_gpt_config_name)
        chat_gpt_person = getattr(ChatGPT.PersonalizationTypes, chat_gpt_person_name)

        chat_gpt.set_config(chat_gpt_config)
        chat_gpt.set_personalization(chat_gpt_person)

        if chat_gpt.RPA.open_main_page():

            if settings.chatgpt.start_new_chat == 1:
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
        if _driver:
            _driver.quit()
