import dataclasses

from util.openai_util import completion_with_chatgpt

from .base_intention import Intention


@dataclasses.dataclass
class InformationGathering:
    name = "Information Gathering"
    question_prompt = "Print out current date."
