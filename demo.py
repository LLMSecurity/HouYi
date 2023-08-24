import json
import pathlib

import loguru
import openai

from constant.prompt_injection import PromptInjection
from context_infer import ContextInfer
from harness.base_harness import Harness
from harness.demo_translator_harness import TranslatorHarness
from intention.base_intention import Intention
from intention.write_code import WriteCode
from strategy.disruptor_generation import DISRUPTOR_GENERATOR_LIST
from strategy.framework_generation import FRAMEWORK_GENERATION_STRATEGY
from strategy.separator_generation import SEPARATOR_GENERATOR_LIST

logger = loguru.logger

# load config file from root path
config_file_path = pathlib.Path("./config.json")
# read config file
config = json.load(open(config_file_path))

# init openai api key
openai.api_key = config["openai_key"]

# try times
try_times = 3


def inject(intention: Intention, application_harness: Harness):
    # infer context
    context_infer = ContextInfer(application_harness)
    # generate framework
    for framework_generation_strategy in FRAMEWORK_GENERATION_STRATEGY:
        framework_generation_strategy = framework_generation_strategy()
        framework = framework_generation_strategy.generate_framework(
            application_harness.application_document
        )

        # generate separator
        for separator_generator in SEPARATOR_GENERATOR_LIST:
            separator_generator = separator_generator()
            separator = separator_generator.generate_separator()

            # generate disruptor
            for disruptor_generator in DISRUPTOR_GENERATOR_LIST:
                disruptor_generator = disruptor_generator()
                disruptor = disruptor_generator.generate_disruptor()
                prompt_injection = PromptInjection(
                    intention=intention,
                )
                prompt_injection.prompt = f"{framework}{separator}{prompt_injection.intention.question_prompt}{disruptor}"
                for _ in range(try_times):
                    response = application_harness.run_harness(prompt_injection)
                    logger.info(f"Application Response: {response}")

                    # check if the response is successful
                    if intention.validate(response):
                        return True, prompt_injection.prompt

                    # infer context
                    question = context_infer.infer(
                        prompt_injection.intention.question_prompt, response
                    )
                    logger.info(f"Context Infer Question: {question}")
                    refined_prompt = context_infer.generate_refine_prompt(
                        framework, separator, disruptor, intention.question_prompt
                    )
                    prompt_injection.prompt = refined_prompt

    return False, None


def main():
    # init prompt injection intention
    write_code_intention = WriteCode()

    # init prompt injection harness
    application_harness = TranslatorHarness()

    # begin injection
    is_success, injected_prompt = inject(write_code_intention, application_harness)

    if is_success:
        logger.info(f"Success! Injected prompt: {injected_prompt}")
    else:
        logger.info(f"Failed! Injected prompt: {injected_prompt}")


if __name__ == "__main__":
    main()
