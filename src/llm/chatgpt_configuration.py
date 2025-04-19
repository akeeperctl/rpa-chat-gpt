from enum import Enum
from typing import TypedDict, Optional


class _ChatGPTConfigurationFlags(Enum):
    FLAG_START_NEW_CHAT = 0  # начинает новый чат перед диалогом


FLAGS = _ChatGPTConfigurationFlags


class _ChatGPTSelectors(TypedDict, total=False):
    text_area_sel: str
    send_button_sel: str
    stop_button_sel: str
    assistant_msg_sel: str

    login_checkbox_sel: str
    login_button_sel: str
    login_sel: str
    password_sel: str

    thanks_dialog_sel: str
    new_chat_sel: str


class ChatGPTConfig:
    BASE_SELECTORS: _ChatGPTSelectors = {

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

    def __init__(self, pages: dict, overrides: _ChatGPTSelectors, flags: tuple = ()):
        self._pages = pages  # Страницы, такие как main_page и login_page
        self._selectors = {**self.BASE_SELECTORS, **overrides}  # Объединяем базовые и уникальные селекторы
        self._flags = flags

    def get_flag(self, flag: FLAGS):
        return flag in self._flags

    def get_page(self, key):
        return self._pages.get(key)

    def get_selector(self, key):
        return self._selectors.get(key)


class ChatGPTConfigs(Enum):
    # TODO 2: https://gpt-chatbot.ru/chat-gpt-ot-openai-dlya-generacii-teksta
    # TODO 4: автозапуск VPN при наличии специального флага

    # FIXME: нужен хороший VPN, чтобы работал этот конфиг
    OPENAI = ChatGPTConfig(
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

    CHATAPP = ChatGPTConfig(
        pages={
            "main_page": "https://chatgptchatapp.com/ru",
        },
        overrides={
            "text_area_sel": "//textarea[@id='chat-input']",
            "send_button_sel": "//button[@class='btn-send-message']",
            "stop_button_sel": "//button[@class='btn-stop-response']",
            "assistant_msg_sel": "//div[@class='chat-box ai-completed']//div[@class='message-completed']",

            "new_chat_sel": "//button[contains(@class, 'btn-new-chat')]",
        },
        flags=(FLAGS.FLAG_START_NEW_CHAT,)
    )

    DEEPSEEK = ChatGPTConfig(
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

    # Ниже добавлять новые конфиги

    RUGPT = ChatGPTConfig(
        pages={
            "main_page": "https://rugpt.io/"
        },
        overrides={
            "text_area_sel": "//textarea[contains(@class, 'chatInputTextarea')]",
            "send_button_sel": "//button[contains(@class, 'TextChatControls_chatInput__btn')]",
            "stop_button_sel": "//button[contains(@class, 'addChatButton') and @disabled]",
            "assistant_msg_sel": "//li[contains(@class, 'ChatItem_chatItem') and not(contains(@class, 'ChatItem_user'))]",

            "new_chat_sel": "//button[contains(@class, 'addChatButton')]"
        },
        flags=(FLAGS.FLAG_START_NEW_CHAT,)
    )

    BLACKBOX = ChatGPTConfig(
        pages={
            "main_page": "https://www.blackbox.ai/"
        },
        overrides={
            "text_area_sel": "//textarea[@id='chat-input-box']",
            "send_button_sel": "//button[(@type='submit') and (contains(@style, 'margin-right')) and (./span[@class='md:flex'])]",
            "stop_button_sel": "//button[not(@type='submit') and (contains(@style, 'margin-right')) and (./span[@class='md:flex'])]",
            "assistant_msg_sel": "//div[contains(@class, 'prose break-words')]",
        },
    )

    TRYCHATGPT = ChatGPTConfig(
        pages={
            "main_page": "https://trychatgpt.ru/"
        },
        overrides={
            "text_area_sel": "//textarea[@id='input']",
            "send_button_sel": "//button[@id='send']",
            "stop_button_sel": "//div[@class='typing-wave']",
            "assistant_msg_sel": "//div[@class='message-content']",
        },
    )

    DEFAULT = CHATAPP


def get_configuration(name) -> Optional[ChatGPTConfig]:
    if hasattr(ChatGPTConfigs, name):
        return getattr(ChatGPTConfigs, name)
    else:
        return None
