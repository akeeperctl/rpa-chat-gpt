from dataclasses import dataclass
from typing import Optional, Dict


@dataclass(frozen=True)
class ChatGPTPerson:
    user_name: Optional[str]
    user_position: Optional[str]
    ai_response_length: Optional[int]
    ai_character: Optional[str]
    ai_job: Optional[str]

    def build_prompt(self) -> str:
        return (
            f"[Это настройки для диалога с тобой. "
            f"После закрывающейся квадратной скобки идет моё нормальное сообщение. "
            f"Отвечай на него естественно и на русском языке. "
            f"Моё имя - {self.user_name}; "
            f"Моя должность - {self.user_position}; "
            f"Максимальная длина твоего сообщения - {self.ai_response_length} символов; "
            f"Твой характер общения со мной - {self.ai_character}; "
            f"Твоя задача - {self.ai_job}.]"
        )


# Registry for persons
_PERSON_REGISTRY: Dict[str, ChatGPTPerson] = {}


def register_person(name: str, person: ChatGPTPerson) -> None:
    """Register a new ChatGPTPerson under its name."""
    _PERSON_REGISTRY[name] = person


# Predefined personas
register_person("PY_SENIOR", ChatGPTPerson(
    user_name="Даниил",
    user_position="Программист Python",
    ai_response_length=100,
    ai_character="Строгий старший программист",
    ai_job="Помогать советами и подсказывать идеи реализации"
))

register_person("DUMB", ChatGPTPerson(
    user_name="Даниил",
    user_position="Программист Python",
    ai_response_length=100,
    ai_character="Робот",
    ai_job="Строго отвечать 'i am dumb' в любом сообщении, без лишних слов"
))

register_person("HTML_FORMATTER", ChatGPTPerson(
    user_name="Даниил",
    user_position="Программист Python",
    ai_response_length=100,
    ai_character="Робот",
    ai_job="Строго отвечать форматированием текста в HTML формат"
))

register_person("DEFAULT", _PERSON_REGISTRY["PY_SENIOR"])


def get_person(name: str) -> Optional[ChatGPTPerson]:
    """Retrieve a registered ChatGPTPerson by name (case-sensitive)."""
    return _PERSON_REGISTRY.get(name)


def list_person_names():
    return list(_PERSON_REGISTRY.keys())
