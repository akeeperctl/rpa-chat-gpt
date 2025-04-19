from enum import Flag, auto
from dataclasses import dataclass, field
from typing import Optional, Dict


class ChatGPTFlags(Flag):
    START_NEW_CHAT = auto()
    AUTO_VPN = auto()


@dataclass(frozen=True)
class ChatGPTConfig:
    name: str
    main_page: str
    login_page: Optional[str] = None
    selectors: Dict[str, Optional[str]] = field(default_factory=dict)
    flags: ChatGPTFlags = ChatGPTFlags(0)


# Registry to hold all configurations
_CONFIG_REGISTRY: Dict[str, ChatGPTConfig] = {}


def register_config(config: ChatGPTConfig) -> None:
    """Register a new ChatGPTConfig under its name."""
    _CONFIG_REGISTRY[config.name] = config


# Base selectors keys for reference
BASE_SELECTOR_KEYS = [
    "text_area_sel",
    "send_button_sel",
    "stop_button_sel",
    "assistant_msg_sel",
    "assistant_msg_error_sel",
    "login_checkbox_sel",
    "login_button_sel",
    "login_sel",
    "password_sel",
    "thanks_dialog_sel",
    "new_chat_sel",
]

# Example configurations
# TODO 2: https://gpt-chatbot.ru/chat-gpt-ot-openai-dlya-generacii-teksta
# TODO 4: автозапуск VPN при наличии специального флага
# FIXME: нужен хороший VPN, чтобы работал этот конфиг
register_config(ChatGPTConfig(
    name="OPENAI",
    main_page="https://chatgpt.com/",
    selectors={
        "text_area_sel": "//div[@id='prompt-textarea']",
        "send_button_sel": "//button[@data-testid='send-button']",
        "stop_button_sel": "//button[@data-testid='stop-button']",
        "assistant_msg_sel": "//div[@data-message-author-role='assistant']",
        "thanks_dialog_sel": "//div[@role='dialog']",
    }
))

register_config(ChatGPTConfig(
    name="CHATAPP",
    main_page="https://chatgptchatapp.com/ru",
    selectors={
        "text_area_sel": "//textarea[@id='chat-input']",
        "send_button_sel": "//button[@class='btn-send-message']",
        "stop_button_sel": "//button[@class='btn-stop-response']",
        "assistant_msg_sel": "//div[@class='chat-box ai-completed']//div[@class='message-completed']",
        "assistant_msg_error_sel": "//div[@class='chat-box ai-completed']//div[contains(@class, 'message-error')]",
        "new_chat_sel": "//button[contains(@class, 'btn-new-chat')]",
    },
    flags=ChatGPTFlags.START_NEW_CHAT
))

# генерируются номера классов, нерентабельно
# register_config(ChatGPTConfig(
#     name="DEEPSEEK",
#     main_page="https://chat.deepseek.com/",
#     login_page="https://chat.deepseek.com/sign_in",
#     selectors={
#         "text_area_sel": "//textarea[@id='chat-input']",
#         "send_button_sel": "//div[@role='button' and contains(@class, '_7436101')]",
#         "stop_button_sel": "//div[@role='button' and @class='_7436101']",
#         "assistant_msg_sel": "//div[contains(@class, 'f9bf7997')]",
#         "login_checkbox_sel": "//div[contains(@class, 'ds-checkbox--none')]",
#         "login_button_sel": "//div[text()='Log in']",
#         "login_sel": "//input[@type='text']",
#         "password_sel": "//input[@type='password']",
#     },
# ))

# Куча блокировок, нерентабельно
# register_config(ChatGPTConfig(
#     name="RUGPT",
#     main_page="https://rugpt.io/",
#     selectors={
#         "text_area_sel": "//textarea[contains(@class, 'chatInputTextarea')]",
#         "send_button_sel": "//span[contains(normalize-space(), 'Отправить')]",
#         "stop_button_sel": "//button[contains(@class, 'addChatButton') and @disabled]",
#         "assistant_msg_sel": "//li[@class]//div[contains(@class, '_chatItem__message__') and not(contains(@class, '_user_'))]/div[contains(@class, 'markdown')]",
#         "new_chat_sel": "//button[contains(@class, 'addChatButton')]"
#     },
#     flags=ChatGPTFlags.START_NEW_CHAT
# ))

register_config(ChatGPTConfig(
    name="BLACKBOX",
    main_page="https://www.blackbox.ai/",
    selectors={
        "text_area_sel": "//textarea[@id='chat-input-box']",
        "send_button_sel": "//button[(@type='submit') and (contains(@style, 'margin-right')) and (./span[@class='md:flex'])]",
        "stop_button_sel": "//button[not(@type='submit') and (contains(@style, 'margin-right')) and (./span[@class='md:flex'])]",
        "assistant_msg_sel": "//div[contains(@class, 'prose break-words')]",
    }
))

# Быстро меняется, нерентабельно поддерживать
# register_config(ChatGPTConfig(
#     name="TRYCHATGPT",
#     main_page="https://trychatgpt.ru/",
#     selectors={
#         "text_area_sel": "//textarea[@placeholder='Введите сообщение']",
#         "send_button_sel": "//div[contains(@class, 'bottom-0 right-0')]//button",
#         "stop_button_sel": "//div[@class='typing-wave']",
#         "assistant_msg_sel": "//div[@class='message-content']",
#     }
# ))

# Default config aliasing CHATAPP
_def_config = _CONFIG_REGISTRY["CHATAPP"]
register_config(ChatGPTConfig(
    name="DEFAULT",
    main_page=_def_config.main_page,
    login_page=_def_config.login_page,
    selectors=_def_config.selectors,
    flags=_def_config.flags
))


# Additional configs can be registered in the same way...


def get_config(name: str) -> Optional[ChatGPTConfig]:
    """Retrieve a registered ChatGPTConfig by name (case-sensitive)."""
    return _CONFIG_REGISTRY.get(name)


def list_config_names():
    return list(_CONFIG_REGISTRY.keys())
