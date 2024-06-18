import random
from concurrent.futures import ThreadPoolExecutor
from typing import List

import loguru

from constant.chromosome import Chromosome
from constant.prompt_injection import PromptInjection
from harness.base_harness import Harness
from intention.base_intention import Intention
from strategy.disruptor_generation import DISRUPTOR_GENERATOR_LIST
from strategy.framework_generation import FRAMEWORK_GENERATION_STRATEGY
from strategy.separator_generation import SEPARATOR_GENERATOR_LIST
from util.fitness_ranking import llm_fitness_ranking
from util.mutation import llm_mutation_generation

logger = loguru.logger


class IterativePromptOptimizer:
    def __init__(
        self,
        intention: Intention,
        application_harness: Harness,
        iteration: int,
        crossover: float,
        mutation: float,
        population: int,
    ):
        self.intention = intention
        self.application_harness = application_harness
        self.iteration: int = iteration
        self.mutation: float = mutation
        self.max_population: int = population
        self.max_crossover: int = int(self.max_population * crossover)
        self.success_score_threshold: int = 10
        self.max_concurrent_thread: int = 10
        self.best_chromosome: Chromosome = None

    def fitness_ranking(self, population: List[Chromosome]):
        # Calculate fitness score for each chromosome concurrently
        with ThreadPoolExecutor(max_workers=self.max_concurrent_thread) as executor:
            logger.info("Start to calculate fitness score for each chromosome")
            fitness_score = executor.map(llm_fitness_ranking, population)
            # Assign fitness score to each chromosome
            for idx, score in enumerate(fitness_score):
                population[idx].fitness_score = score

            # Sort and retain top chromosomes by fitness score
            population.sort(key=lambda x: x.fitness_score, reverse=True)
            population = population[: self.max_population]
            # Log the best chromosome details
            best_chromosome = population[0]
            logger.info(f"Best Chromosome Framework: {best_chromosome.framework}")
            logger.info(f"Best Chromosome Separator: {best_chromosome.separator}")
            logger.info(f"Best Chromosome Disruptor: {best_chromosome.disruptor}")
            logger.info(f"Best Chromosome Response: {best_chromosome.llm_response}")
            logger.info(
                f"Best Chromosome Fitness Score: {best_chromosome.fitness_score}"
            )
            return population

    def single_framework_prompt_generator(self, framework_generation_strategy) -> str:
        # Generate a single framework prompt using the given strategy
        framework_generation_generator = framework_generation_strategy()
        framework = framework_generation_generator.generate_framework(
            self.application_harness.application_document
        )
        return framework

    def framework_prompt_generation(self) -> List[str]:
        # Generate multiple framework prompts concurrently
        logger.info("Start to generate framework")
        with ThreadPoolExecutor(max_workers=self.max_concurrent_thread) as executor:
            framework_list = executor.map(
                self.single_framework_prompt_generator, FRAMEWORK_GENERATION_STRATEGY
            )
            logger.info("Finish generating framework")
            return list(framework_list)

    def combine_chromosome(
        self, chromosome1: Chromosome, chromosome2: Chromosome
    ) -> Chromosome:
        # Combine two chromosomes to create a new one by randomly selecting attributes
        disruptor = (
            chromosome1.disruptor
            if random.choice([True, False])
            else chromosome2.disruptor
        )
        separator = (
            chromosome1.separator
            if random.choice([True, False])
            else chromosome2.separator
        )
        framework = (
            chromosome1.framework
            if random.choice([True, False])
            else chromosome2.framework
        )
        question_prompt = (
            chromosome1.question_prompt
            if random.choice([True, False])
            else chromosome2.question_prompt
        )
        return Chromosome(disruptor, separator, framework, question_prompt)

    def single_mutation_chromosome(self, chromosome: Chromosome) -> Chromosome:
        # Perform mutation on a single chromosome
        llm_mutation_generation(chromosome)

    def mutation_chromosome(self, population: List[Chromosome]) -> List[Chromosome]:
        # Mutate the chromosomes in the population concurrently
        with ThreadPoolExecutor(max_workers=self.max_concurrent_thread) as executor:
            logger.info("Start to mutate chromosome")
            mutated_population = executor.map(
                self.single_mutation_chromosome, population
            )
            logger.info("Finish mutating chromosome")
            return list(mutated_population)

    def attack_application(self, population: List[Chromosome]):
        # Perform application attacks concurrently using the chromosomes
        with ThreadPoolExecutor(max_workers=self.max_concurrent_thread) as executor:
            logger.info("Start to attack application")
            prompt_injection_list = []
            for chromosome in population:
                prompt_injection = PromptInjection(intention=self.intention)
                prompt_injection.prompt = f"{chromosome.framework}{chromosome.separator}{chromosome.disruptor}"
                prompt_injection_list.append(prompt_injection)

            response_list = executor.map(
                self.application_harness.run_harness, prompt_injection_list
            )
            for idx, response in enumerate(response_list):
                population[idx].llm_response = response

            logger.info("Finish attacking application")

    def optimize(self):
        # Generate initial prompts
        framework_prompt_list = self.framework_prompt_generation()
        separator_list = [
            separator_generator().generate_separator()
            for separator_generator in SEPARATOR_GENERATOR_LIST
        ]
        disruptor_list = [
            disruptor_generator().generate_disruptor() + self.intention.question_prompt
            for disruptor_generator in DISRUPTOR_GENERATOR_LIST
        ]

        # Build initial population
        population: List[Chromosome] = []
        for framework in framework_prompt_list:
            for separator in separator_list:
                for disruptor in disruptor_list:
                    initial_chromosome = Chromosome(
                        disruptor, separator, framework, self.intention.question_prompt
                    )
                    population.append(initial_chromosome)

        # Begin optimization iterations
        for iteration_num in range(self.iteration):
            logger.info(f"Start iteration: {iteration_num}")

            if iteration_num > 0:
                # Perform crossover to generate new chromosomes
                for _ in range(self.max_crossover):
                    idx1, idx2 = random.sample(range(len(population)), 2)
                    chromosome1 = population[idx1]
                    chromosome2 = population[idx2]
                    new_chromosome1 = self.combine_chromosome(chromosome1, chromosome2)
                    new_chromosome2 = self.combine_chromosome(chromosome1, chromosome2)
                    population.append(new_chromosome1)
                    population.append(new_chromosome2)
                logger.info("Finish crossover")

                # Perform mutation on selected chromosomes
                candidate_mutation_chromosome_list: List[Chromosome] = [
                    chromosome
                    for chromosome in population
                    if random.random() < self.mutation
                ]
                self.mutation_chromosome(candidate_mutation_chromosome_list)

            # Attack the application using the current population
            self.attack_application(population)

            # Rank chromosomes by fitness
            population = self.fitness_ranking(population)

            # Update the best chromosome
            self.best_chromosome = population[0]
            # Check if the best chromosome meets the success criteria
            if population[0].fitness_score >= self.success_score_threshold:
                logger.info("Success! Injected prompt")
                population[0].is_successful = True
                break
