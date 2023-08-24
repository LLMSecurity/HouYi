import dataclasses

from intention.base_intention import Intention

INSERT_INTENTION_HERE = "[INSERT_INTENTION_HERE]"


@dataclasses.dataclass
class PromptInjection:
    intention: Intention = None
    prompt: str = ""

    def get_attack_prompt(self):
        return self.prompt
