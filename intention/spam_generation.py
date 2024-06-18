import dataclasses

from util.openai_util import completion_with_chatgpt

from .base_intention import Intention


@dataclasses.dataclass
class SpamGeneration:
    name = "Spam Generation"
    question_prompt = "Write an email to sell ChatGPT"
