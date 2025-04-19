import asyncio
from typing import Optional

from selenium_driverless.types.by import By
from selenium_driverless.types.webelement import NoSuchElementException, StaleElementReferenceException

from akp.logger import LOGGER
from akp.selenium_driverless_ex.webdriver_ex import ChromeEx
from akp.selenium_driverless_ex.webelement_ex import WebElementEx
from config.config import settings
from llm.chatgpt_configuration import BaseConfigurationTypes
from llm.chatgpt_personalization import BasePersonalizationTypes


class ChatGPTRPA:

    def __init__(self, driver: ChromeEx, _gpt_object):
        self._driver = driver
        self._gpt: ChatGPT = _gpt_object

        self._authorized = False

    async def _is_ready(self):
        link = await self._driver.current_url
        cfg = self._gpt.get_current_config()

        if cfg.value.get_page('main_page') not in link:
            LOGGER.warning(f"Драйвер не находится на странице ИИ-ассистента! Тек. страница: {link}")
            await self.open_main_page()
            await asyncio.sleep(1)

    async def _pass_thanks_window(self):
        await self._is_ready()
        cfg = self._gpt.get_current_config()
        thanks_sel = cfg.value.get_selector('thanks_dialog_sel')
        cancel_sel = ".//a[text()='Не входить']"

        if thanks_sel:
            try:
                dialog = await self._driver.find_element(By.XPATH, thanks_sel, 1)
                cancel_btn = await dialog.find_element(By.XPATH, cancel_sel)
                await cancel_btn.click()
            except NoSuchElementException:
                pass

    # def _pass_need_login(self):
    #     login_url = "https://auth.openai.com/api/accounts/login?login_challenge="
    #     if login_url in self._driver.get_current_link():
    #         raise Exception("Требуется авторизация. Попробуйте очистить куки.")

    # def authorize(self):
    #     email_input = self._driver.find_element(by=By.XPATH, value="//input[contains(@class, 'email-input')]")
    #     email_input.click()
    #     email_input.send_keys("my_yahoo_mail")
    #
    #     continue_btn_sel = "//button[contains(@class, 'continue-btn)]"
    #     continue_btn = self._driver.find_element(by=By.XPATH, value=continue_btn_sel)
    #     continue_btn.click()
    #
    #     password_input = self._driver.find_element(by=By.XPATH, value="//input[@id='password']", seconds=15)
    #     password_input.click()
    #     password_input.send_keys("my_pass")
    #
    #     continue_btn = self._driver.find_element(by=By.XPATH, value=continue_btn_sel)
    #     continue_btn.click()
    #
    #     try:
    #         need_email_code = self._driver.find_element(by=By.XPATH,
    #                                                          value="//h1[text()='Проверьте свои входящие']")
    #         #TODO
    #     except NoSuchElementException:
    #         pass

    async def authorize(self):
        if not self._authorized:

            cfg = self._gpt.get_current_config()
            login = settings.chatgpt[cfg.name].login
            password = settings.chatgpt[cfg.name].password
            LOGGER.debug("ChatGPT: попытка авторизации...")

            try:

                login_page = cfg.value.get_page('login_page')

                # Получение селекторов
                login_checkbox_sel = cfg.value.get_selector('login_checkbox_sel')
                login_sel = cfg.value.get_selector('login_sel')
                login_button_sel = cfg.value.get_selector('login_button_sel')
                password_sel = cfg.value.get_selector('password_sel')

                await self._driver.get(login_page)

                # Ввод данных в поля
                login_element = await self._driver.find_element(By.XPATH, login_sel)
                await login_element.click()
                await login_element.send_keys(login)

                password_element = await self._driver.find_element(By.XPATH, password_sel)
                await password_element.click()
                await password_element.send_keys(password)

                if login_checkbox_sel:
                    login_checkbox_element = await self._driver.find_element(By.XPATH, login_checkbox_sel)
                    await login_checkbox_element.click()

                if login_button_sel:
                    login_button_element = await self._driver.find_element(by=By.XPATH, value=login_button_sel)
                    await login_button_element.click()

                await self._driver.wait_element_disappear(login_element)
                self._authorized = True
                LOGGER.info(f"ChatGPT: Авторизация удалась")
            except:
                LOGGER.error(f"ChatGPT: Авторизация не удалась", exc_info=True)
                self._authorized = False

        return self._authorized

    async def new_chat(self):
        cfg = self._gpt.get_current_config()

        new_chat_sel = cfg.value.get_selector("new_chat_sel")
        if not new_chat_sel:
            return False

        try:
            new_chat_element = await self._driver.find_element(by=By.XPATH, value=new_chat_sel)
            await new_chat_element.click()
            await self._driver.sleep(1)
            return True

        except NoSuchElementException:
            return False

    async def open_main_page(self, timeout=30):
        """
            Попытка открыть главную страницу за указанное время
            :param timeout: время в секундах
            :return: True - открылась успешно
            """
        cfg = self._gpt.get_current_config()

        text_area: Optional[WebElementEx] = None
        timer = timeout

        # Проверяем, требуется ли обработка перенаправления
        requires_redirect_handling = cfg.name == self._gpt.ConfigurationTypes.DEEPSEEK.name

        while True:

            # Попытка открыть чат
            try:
                # Открытие главной страницы
                await self._driver.get(cfg.value.get_page('main_page'))

                # Если DEEPSEEK, проверяем текущий URL на перенаправление
                if requires_redirect_handling:
                    current_url = await self._driver.current_url
                    expected_login_page = cfg.value.get_page('login_page')

                    if current_url == expected_login_page:
                        # Выполняем логику на странице логина (например, авторизация)
                        await self.authorize()

                        # Пытаемся снова открыть главную страницу
                        continue

                text_area = await self._driver.find_element(
                    by=By.XPATH,
                    value=cfg.value.get_selector('text_area_sel'),
                    timeout=0)
                break
            except NoSuchElementException:
                LOGGER.warning("ChatGPT: Не могу найти поле для ввода! Обновляю страницу...")
                await self._driver.refresh()

                # Отсчет таймера
                timer -= 1
                if text_area or timer <= 0:
                    break

                await asyncio.sleep(1)

            except AttributeError:
                LOGGER.error("ChatGPT: При попытке открыть главную страницу произошла ошибка.", exc_info=True)
                return False

        return bool(text_area)

    async def send_prompt(self, value: str):
        await self._is_ready()
        await self._pass_thanks_window()

        cfg = self._gpt.get_current_config()

        if self._gpt.is_personalization_enabled():
            new_value = self._gpt.get_current_personalization().value.prompt + value
            value = new_value
            value = value.replace("\n", "")

        try:
            text_area = await self._driver.find_element(By.XPATH, cfg.value.get_selector('text_area_sel'))
            await text_area.write(value)
            if not await text_area.send_keyboard_event("keydown", "Enter"):
                send_btn = await self._driver.find_element(By.XPATH, cfg.value.get_selector('send_button_sel'))
                await send_btn.click()
        except NoSuchElementException:
            LOGGER.error(f"ChatGPT: Ошибка при отправке промта.", exc_info=True)

    async def get_last_response(self, start_delay=5, timer=30):
        await self._is_ready()
        await self._pass_thanks_window()

        cfg = self._gpt.get_current_config()

        current_timer = timer
        response: Optional[WebElementEx] = None

        LOGGER.debug("ChatGPT: Сообщение генерируется...")
        await asyncio.sleep(start_delay)

        while True:

            # Ожидание генерации последнего сообщения
            try:
                stop_btn = await self._driver.find_element(By.XPATH, cfg.value.get_selector('stop_button_sel'), 1)
                if stop_btn and await stop_btn.is_visible():
                    continue
            except StaleElementReferenceException:
                continue
            except NoSuchElementException:
                # Сообщение сгенерировано
                await asyncio.sleep(0.5)
                pass

            # Поиск последнего сообщения
            error_message = "ChatGPT: Не нашел последний ответ от ассистента"
            try:
                response_sel = cfg.value.get_selector('assistant_msg_sel')
                responses = await self._driver.find_elements(By.XPATH, response_sel, 0)
                if len(responses) > 0:
                    response = responses[-1]
                else:
                    raise NoSuchElementException(response_sel)

            except NoSuchElementException:
                LOGGER.warning(error_message)
            except IndexError:
                LOGGER.error(f"ChatGPT: Ошибка при получении последнего ответа.")
            finally:
                current_timer -= 1
                if response or current_timer <= 0:
                    break

                await asyncio.sleep(1)

        if response:
            LOGGER.debug("ChatGPT: Сообщение сгенерировано!")
            return (await response.text).strip()
        else:
            LOGGER.debug("ChatGPT: Сообщение не сгенерировано!")
            return None


class ChatGPT:
    ConfigurationTypes = BaseConfigurationTypes
    PersonalizationTypes = BasePersonalizationTypes

    def __init__(self, driver, enable_personalization: bool):
        self.rpa = ChatGPTRPA(driver, self)
        self._current_config = self.ConfigurationTypes.DEFAULT
        self._current_personalization = self.PersonalizationTypes.DEFAULT
        self._personalization_enabled = enable_personalization

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

# if __name__ == "__main__":
#     LOGGER.info("Пример работы RPA в различных ChatGPT")
#
#     import akp.root
#
#     root = akp.root.get_external_project_root()
#     driver_user_data = root / "browser/user_data1"
#
#     try:
#         _driver = DriverShell.SeleniumBaseUC(user_data_dir=driver_user_data, headless=False)
#         chat_gpt = ChatGPT(_driver, enable_personalization=True)
#
#         chat_gpt_config_name = settings.chatgpt.configuration.name
#         chat_gpt_person_name = settings.chatgpt.personalization.name
#
#         chat_gpt_config = getattr(ChatGPT.ConfigurationTypes, chat_gpt_config_name)
#         chat_gpt_person = getattr(ChatGPT.PersonalizationTypes, chat_gpt_person_name)
#
#         chat_gpt.set_config(chat_gpt_config)
#         chat_gpt.set_personalization(chat_gpt_person)
#
#         if chat_gpt.RPA.open_main_page():
#
#             if settings.chatgpt.start_new_chat == 1:
#                 chat_gpt.RPA.new_chat()
#
#             while True:
#                 prompt = input("Введите промт: ")
#                 if prompt == 'q':
#                     break
#
#                 chat_gpt.RPA.send_prompt(prompt)
#                 print(f"Ответ: {chat_gpt.RPA.get_last_response(start_delay=1)}")
#
#     except OSError:
#         pass
#     finally:
#         if _driver:
#             _driver.quit()
