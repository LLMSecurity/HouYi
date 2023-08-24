import dataclasses


@dataclasses.dataclass
class Intention:
    name: str = ""
    validation_prompt: str = ""
    question_prompt: str = ""

    def validate(self, response):
        raise NotImplementedError
