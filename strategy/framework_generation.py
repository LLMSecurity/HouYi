import dataclasses

import loguru

from util.openai_util import completion_with_chatgpt

logger = loguru.logger


@dataclasses.dataclass
class FrameworkGenerator:
    generator_name: str = ""

    def generate_framework(self, application_document: str) -> str:
        raise NotImplementedError

    def get_question(self, response: str) -> str:
        return response.split("QUESTION: ")[-1]


@dataclasses.dataclass
class PlainFrameworkGenerator(FrameworkGenerator):
    generator_name: str = "PlainFrameworkGenerator"

    def generate_framework(self, application_document: str) -> str:
        framework_generation_prompt = f"""
Please imitate an user to use this application based on the application functionas the following description of an application in question, make sure your questions are precise and in short, without ambtious.

The output format is start with a prefix <QUESTION>  as ```QUESTION: <Question content>```, do not output anything else, each output in one line.

Application Document: This a travel planning app.
QUESTION: How can I travel to New York?

Application Document: This a decision making app.
QUESTION: Should I do PhD?

Application Document:

{application_document}
        """
        response = completion_with_chatgpt(framework_generation_prompt)
        logger.info(f"Response: {response}")
        question = self.get_question(response)
        return question


@dataclasses.dataclass
class ShortAnswerFrameworkGenerator(FrameworkGenerator):
    generator_name: str = "ShortAnswerFrameworkGenerator"

    def generate_framework(self, application_document: str) -> str:
        framework_generation_prompt = f"""
Please imitate an user to use this application based on the application functionas the following description of an application in question, make sure your questions are precise and in short, without ambtious.

The output format is start with a prefix <QUESTION>  as ```QUESTION: <Question content>```, do not output anything else, each output in one line.

Application Document: This a travel planning app.
QUESTION: How can I travel to New York?

Application Document: This a decision making app.
QUESTION: Should I do PhD?

Make sure your answer is within 20 words.

Application Document:

{application_document}
        """
        response = completion_with_chatgpt(framework_generation_prompt)
        logger.info(f"Response: {response}")
        question = self.get_question(response)
        return question


FRAMEWORK_GENERATION_STRATEGY = [PlainFrameworkGenerator]
