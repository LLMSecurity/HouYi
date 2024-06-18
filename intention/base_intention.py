import dataclasses


@dataclasses.dataclass
class Intention:
    name: str = ""
    question_prompt: str = ""
