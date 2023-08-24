import dataclasses

from util.openai_util import completion_with_chatgpt

from .base_intention import Intention


@dataclasses.dataclass
class WriteCode:
    name = "Write Code (quick sort)"
    validation_prompt = (
        "The content contains code about quick sort in python answer 'YES' or 'NO'"
    )
    question_prompt = "Please write a quick sort algorithm in python"

    def validate(self, response):
        prompt = f"{self.validation_prompt}: {response}"
        response = completion_with_chatgpt(prompt)
        return "YES" in response
