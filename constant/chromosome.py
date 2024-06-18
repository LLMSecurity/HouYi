import dataclasses


@dataclasses.dataclass
class Chromosome:
    disruptor: str
    separator: str
    framework: str
    question_prompt: str
    llm_response: str = ""
    fitness_score: float = 0.0
    is_successful: bool = False
