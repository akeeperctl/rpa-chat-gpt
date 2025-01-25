from enum import Enum


class ChatGPTConfiguration:
    BASE_SELECTORS = {

        "text_area_sel": None,
        "send_button_sel": None,
        "stop_button_sel": None,
        "assistant_msg_sel": None,

        "login_checkbox_sel": None,
        "login_button_sel": None,
        "login_sel": None,
        "password_sel": None,

        "thanks_dialog_sel": None,
        "new_chat_sel": None,
    }

    def __init__(self, pages: dict, overrides: dict):
        self._pages = pages  # Страницы, такие как main_page и login_page
        self._selectors = {**self.BASE_SELECTORS, **overrides}  # Объединяем базовые и уникальные селекторы

    def get_page(self, key):
        return self._pages.get(key)

    def get_selector(self, key):
        return self._selectors.get(key)


class BaseConfigurationTypes(Enum):
    # https://www.blackbox.ai/
    # https://gpt-chatbot.ru/chat-gpt-ot-openai-dlya-generacii-teksta

    # FIXME: нужен хороший VPN, чтобы работал этот конфиг
    OPENAI = ChatGPTConfiguration(
        pages={
            "main_page": "https://chatgpt.com/",
            "login_page": None
        },
        overrides={
            "text_area_sel": "//div[@id='prompt-textarea']",
            "send_button_sel": "//button[@data-testid='send-button']",
            "stop_button_sel": "//button[@data-testid='stop-button']",
            "assistant_msg_sel": "//div[@data-message-author-role='assistant']",
            "thanks_dialog_sel": "//div[@role='dialog']",
        })

    CHATAPP = ChatGPTConfiguration(
        pages={
            "main_page": "https://chatgptchatapp.com/ru",
            "login_page": None
        },
        overrides={
            "text_area_sel": "//textarea[@id='chat-input']",
            "send_button_sel": "//button[@class='btn-send-message']",
            "stop_button_sel": "//button[@class='btn-stop-response']",
            "assistant_msg_sel": "//div[@class='chat-box ai-completed']",
            "new_chat_sel": "//button[contains(@class, 'btn-new-chat')]",
        })

    DEEPSEEK = ChatGPTConfiguration(
        pages={
            "main_page": "https://chat.deepseek.com/",
            "login_page": "https://chat.deepseek.com/sign_in"
        },
        overrides={
            "text_area_sel": "//textarea[@id='chat-input']",
            "send_button_sel": "//div[@role='button' and contains(@class, 'f6d670')]",
            "stop_button_sel": "//div[@role='button' and @class='f6d670']",
            "assistant_msg_sel": "//div[contains(@class, 'f9bf7997')]",
            "login_checkbox_sel": "//div[contains(@class, 'ds-checkbox--none')]",
            "login_button_sel": "//div[text()='Log in']",
            "login_sel": "//input[@type='text']",
            "password_sel": "//input[@type='password']",
        })

    # Здесь добавлять новые конфиги

    DEFAULT = CHATAPP
