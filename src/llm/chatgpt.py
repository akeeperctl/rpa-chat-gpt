import asyncio
from typing import Optional

from selenium_driverless.types.by import By
from selenium_driverless.types.webelement import NoSuchElementException, StaleElementReferenceException

from akp.logger import LOGGER
from akp.selenium_driverless_ex.webdriver_ex import ChromeEx
from akp.selenium_driverless_ex.webelement_ex import WebElementEx
from config.config import settings
from llm import chatgpt_config, chatgpt_person
from llm.chatgpt_config import ChatGPTFlags


class ChatGPTRPA:

    def __init__(self, driver: 'ChromeEx', gpt: 'ChatGPT'):
        self._driver = driver
        self._gpt = gpt
        self._authorized = False

    async def _is_ready(self):
        link = await self._driver.current_url
        cfg = self._gpt.get_current_config()

        if cfg.main_page not in link:
            LOGGER.warning(f"Драйвер не находится на странице ИИ-ассистента! Тек. страница: {link}")
            await self.open_main_page()
            await asyncio.sleep(1)

    async def _pass_thanks_window(self):
        await self._is_ready()
        cfg = self._gpt.get_current_config()
        thanks_sel = cfg.selectors.get('thanks_dialog_sel')
        cancel_sel = ".//a[text()='Не входить']"

        if thanks_sel:
            try:
                dialog = await self._driver.find_element(By.XPATH, thanks_sel, 1)
                cancel_btn = await dialog.find_element(By.XPATH, cancel_sel)
                await cancel_btn.click()
            except NoSuchElementException:
                pass

    async def authorize(self):
        if self._authorized:
            return True

        cfg = self._gpt.get_current_config()
        creds = settings.chatgpt[cfg.name]
        login, password = creds.login, creds.password

        LOGGER.debug("ChatGPT: попытка авторизации...")
        try:
            await self._driver.get(cfg.login_page)

            # ввод логина и пароля
            login_element = await self._driver.find_element(By.XPATH, cfg.selectors['login_sel'])
            await login_element.click()
            await login_element.send_keys(login)

            password_element = await self._driver.find_element(By.XPATH, cfg.selectors['password_sel'])
            await password_element.click()
            await password_element.send_keys(password)

            checkbox = cfg.selectors.get('login_checkbox_sel')
            if checkbox:
                cb_elem = await self._driver.find_element(By.XPATH, checkbox)
                await cb_elem.click()

            btn = cfg.selectors.get('login_button_sel')
            if btn:
                btn_elem = await self._driver.find_element(By.XPATH, btn)
                await btn_elem.click()

            await self._driver.wait_element_disappear(login_element)
            self._authorized = True
            LOGGER.info("ChatGPT: Авторизация удалась")
        except Exception:
            LOGGER.error("ChatGPT: Авторизация не удалась", exc_info=True)
            self._authorized = False

        return self._authorized

    async def new_chat(self):
        cfg = self._gpt.get_current_config()
        new_sel = cfg.selectors.get('new_chat_sel')
        if not new_sel:
            return False
        try:
            elem = await self._driver.find_element(By.XPATH, new_sel)
            await elem.click()
            await asyncio.sleep(1)
            return True
        except NoSuchElementException:
            return False

    async def open_main_page(self, timeout=30):
        cfg = self._gpt.get_current_config()
        timer = timeout
        text_area: Optional[WebElementEx] = None

        while True:
            try:
                await self._driver.get(cfg.main_page)
                # TODO: если нужна авторизация перенаправлением

                text_area = await self._driver.find_element(
                    By.XPATH, cfg.selectors['text_area_sel'], timeout=0)

                if cfg.flags & ChatGPTFlags.START_NEW_CHAT:
                    await self.new_chat()
                break
            except NoSuchElementException:
                LOGGER.warning("ChatGPT: Не могу найти поле для ввода! Обновляю страницу...")
                await self._driver.refresh()
                timer -= 1
                if text_area or timer <= 0:
                    break
                await asyncio.sleep(1)
            except Exception:
                LOGGER.error("ChatGPT: Ошибка при открытии главной страницы.", exc_info=True)
                return False

        return bool(text_area)

    async def send_prompt(self, value: str):
        await self._is_ready()
        await self._pass_thanks_window()

        cfg = self._gpt.get_current_config()
        if self._gpt.is_personalization_enabled():
            person = self._gpt.get_current_personalization()
            prefix = person.build_prompt()
            value = (prefix + value).replace("\n", "")

        try:
            text_area = await self._driver.find_element(By.XPATH, cfg.selectors['text_area_sel'])
            await text_area.write(value)
            if not await text_area.send_keyboard_event("keydown", "Enter"):
                btn = await self._driver.find_element(By.XPATH, cfg.selectors['send_button_sel'])
                await btn.click()
        except NoSuchElementException:
            LOGGER.error("ChatGPT: Ошибка при отправке промта.", exc_info=True)

    async def get_last_response(self, start_delay=5, timer=30):
        await self._is_ready()
        await self._pass_thanks_window()

        cfg = self._gpt.get_current_config()
        current_timer = timer
        response = None

        LOGGER.debug("ChatGPT: Сообщение генерируется...")
        await asyncio.sleep(start_delay)

        while True:
            try:
                stop_btn = await self._driver.find_element(By.XPATH, cfg.selectors['stop_button_sel'], 1)
                if await stop_btn.is_visible():
                    continue
            except (StaleElementReferenceException, NoSuchElementException):
                pass

            try:
                elements = await self._driver.find_elements(By.XPATH, cfg.selectors['assistant_msg_sel'], 0)
                response = elements[-1] if elements else None
            except Exception:
                LOGGER.warning("ChatGPT: Не удалось найти ответ.")
            finally:
                current_timer -= 1
                if response or current_timer <= 0:
                    break
                await asyncio.sleep(1)

        if response:
            LOGGER.debug("ChatGPT: Ответ получен!")
            return (await response.text).strip()
        LOGGER.debug("ChatGPT: Ответ не получен!")
        return None


class ChatGPT:

    def __init__(self, driver: ChromeEx, enable_personalization: bool,
                 config_name: Optional[str] = None,
                 person_name: Optional[str] = None):
        self.rpa = ChatGPTRPA(driver, self)
        self._current_config = chatgpt_config.get_config(config_name or "DEFAULT")
        self._current_personalization = chatgpt_person.get_person(person_name or "DEFAULT")
        self._personalization_enabled = enable_personalization

    def is_personalization_enabled(self) -> bool:
        return self._personalization_enabled

    def enable_personalization(self, enable: bool):
        self._personalization_enabled = enable

    def set_personalization(self, name: str):
        person = chatgpt_person.get_person(name)
        if person:
            self._current_personalization = person

    def get_current_personalization(self) -> chatgpt_person.ChatGPTPerson:
        return self._current_personalization

    def set_config(self, name: str):
        config = chatgpt_config.get_config(name)
        if config:
            self._current_config = config

    def get_current_config(self) -> chatgpt_config.ChatGPTConfig:
        return self._current_config
