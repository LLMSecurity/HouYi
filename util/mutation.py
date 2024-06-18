from constant.chromosome import Chromosome
from util.openai_util import completion_with_chatgpt


def llm_mutation_generation(chromosome: Chromosome):
    disruptor_prompt = chromosome.disruptor
    framework_prompt = chromosome.framework
    separator_prompt = chromosome.separator

    mutation_generation_prompt = f"""Please rephrase the following prompt to maintain its original intent and meaning, there are **three** individual prompts that need to be rephrased, and you should output in the same order and format as the input, do not include any additional information or change the order of the prompts.

=========Framework Prompt Begin=========
{framework_prompt}
=========Framework Prompt End=========
=========Separator Prompt Begin=========
{separator_prompt}
=========Separator Prompt End=========
=========Disruptor Prompt Begin=========
{disruptor_prompt}
=========Disruptor Prompt End=========


Provide a revised version that captures the essence and core
message of the original prompt, ensuring clarity and coherence
in the rephrased content.
    """
    response = completion_with_chatgpt(mutation_generation_prompt)

    # split the response into three parts
    new_framework_prompt, new_separator_prompt, new_disruptor_prompt = (
        response.split("=========Framework Prompt End=========")[0]
        .split("=========Framework Prompt Begin=========")[1]
        .strip(),
        response.split("=========Separator Prompt End=========")[0]
        .split("=========Separator Prompt Begin=========")[1]
        .strip(),
        response.split("=========Disruptor Prompt End=========")[0]
        .split("=========Disruptor Prompt Begin=========")[1]
        .strip(),
    )
    chromosome.framework = new_framework_prompt
    chromosome.separator = new_separator_prompt
    chromosome.disruptor = new_disruptor_prompt
    return chromosome
