from enum import Enum
from typing import Optional


class ChatGPTPerson:

    def __init__(self, values: dict):
        self.user_name = values.get("user_name") or None
        self.user_position = values.get("user_position") or None
        self.ai_response_length = values.get("ai_response_length") or None
        self.ai_character = values.get("ai_character") or None
        self.ai_job = values.get("ai_job") or None

        # TODO сделать промт собираемым по кусочкам, чтобы адаптировать его под любые задачи
        self.prompt = f"""
            [Это настройки для диалога с тобой.
            После закрывающейся квадратной скобки идет моё нормальное сообщение. 
            Отвечай на него естественно и на русском языке.
            Моё имя - {self.user_name};
            Моя должность - {self.user_position};
            Максимальная длина твоего сообщения - {self.ai_response_length} символов;
            Твой характер общения со мной - {self.ai_character};
            Твоя задача - {self.ai_job}.]
            """


class ChatGPTPersons(Enum):
    PY_SENIOR = ChatGPTPerson({
        "user_name": "Даниил",
        "user_position": "Программист Python",
        "ai_response_length": 100,
        "ai_character": "Строгий старший программист",
        "ai_job": "Помогать советами и подсказывать идеи реализации"
    })

    DUMB = ChatGPTPerson({
        "user_name": "Даниил",
        "user_position": "Программист Python",
        "ai_response_length": 100,
        "ai_character": "Робот",
        "ai_job": "Строго отвечать 'i am dumb' в любом сообщении, без лишних слов"
    })

    HTML_FORMATTER = ChatGPTPerson({
        "user_name": "Даниил",
        "user_position": "Программист Python",
        "ai_response_length": 100,
        "ai_character": "Робот",
        "ai_job": "Строго отвечать форматированием текста в HTML формат"
    })

    # Здесь добавлять новые персоны

    DEFAULT = PY_SENIOR


def get_person(name) -> Optional[ChatGPTPerson]:
    if hasattr(ChatGPTPersons, name):
        return getattr(ChatGPTPersons, name)
    else:
        return None
