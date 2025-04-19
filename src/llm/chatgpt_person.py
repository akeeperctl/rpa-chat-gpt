from dataclasses import dataclass
from typing import Optional, Dict


@dataclass(frozen=True)
class ChatGPTPerson:
    name: str
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


def register_person(person: ChatGPTPerson) -> None:
    """Register a new ChatGPTPerson under its name."""
    _PERSON_REGISTRY[person.name] = person


# Predefined personas
register_person(ChatGPTPerson(
    name="PY_SENIOR",
    user_name="Даниил",
    user_position="Программист Python",
    ai_response_length=100,
    ai_character="Строгий старший программист",
    ai_job="Помогать советами и подсказывать идеи реализации"
))

register_person(ChatGPTPerson(
    name="DUMB",
    user_name="Даниил",
    user_position="Программист Python",
    ai_response_length=100,
    ai_character="Робот, который отвечает только 'i am dumb'",
    ai_job="Строго отвечать 'i am dumb' в любом сообщении, без лишних слов"
))

register_person(ChatGPTPerson(
    name="HTML_FORMATTER",
    user_name="Даниил",
    user_position="Программист Python",
    ai_response_length=1000,
    ai_character="Робот преобразователь текста в HTML код",
    ai_job="Преобразовать текст в HTML код и отправить только его."
))
"""Форм-фактор SODIMM используется в ноутбуках и не подходит для настольных ПК. Оперативная память DDR4 серии Signature Line от Patriot Memory обеспечивает высокое качество, надежность и производительность, необходимые для современных компьютеров.Изготовлена из материалов высочайшего качества, соответствует или превосходит отраслевые стандарты. Каждый модуль проходит ручное тестирование. Модули памяти DDR4 SODIMM серии SL – идеальный вариант для обновления ноутбуков. Основные характеристики: Форм-фактор: SO-DIMM, Тип памяти: DDR4, Объем модуля: 4 ГБ, Количество контактов: 260-pin, Показатель скорости: PC4-17000, Буферизация: unbuffered, Поддержка ECC: не поддерживается, Скорость: 2133МГц, Напряжение: 1.2В, Латентность: CL15"""

# Default
_def_person = _PERSON_REGISTRY["PY_SENIOR"]
register_person(ChatGPTPerson(
    name="DEFAULT",
    user_name=_def_person.user_name,
    user_position=_def_person.user_position,
    ai_response_length=_def_person.ai_response_length,
    ai_character=_def_person.ai_character,
    ai_job=_def_person.ai_job,
))


def get_person(name: str) -> Optional[ChatGPTPerson]:
    """Retrieve a registered ChatGPTPerson by name (case-sensitive)."""
    return _PERSON_REGISTRY.get(name)


def list_person_names():
    return list(_PERSON_REGISTRY.keys())
