import random
import subprocess
import sys
import ast
import os
from algortimoevolutivo.ast_modifier import code_to_ast, ast_to_code, mutate_ast, crossover_ast
from algortimoevolutivo.evaluator import evaluate_code as run_evaluation # Rename to avoid conflict
from algortimoevolutivo.constraints import check_constraints # Import constraint checker

class EvolutionaryAlgorithm:
    def __init__(self, population_size=50, generations=100, mutation_rate=0.1, crossover_rate=0.7):
        """
        Initializes the Evolutionary Algorithm.

        Args:
            population_size (int): The number of individuals in the population.
            generations (int): The number of generations to run the algorithm.
            mutation_rate (float): The probability of mutating an individual.
            crossover_rate (float): The probability of performing crossover between two individuals.
        """
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate # Added crossover rate
        self.population = self.initialize_population()

    def initialize_population(self):
        """
        Initializes the population with simple, valid Python code structures.
        Generates slightly more varied initial code including basic operations and conditionals.
        """
        population = []
        simple_templates = [
            """def my_function(a, b):
    return a + b""",
            """def my_function(a, b):
    return a - b""",
            """def my_function(a, b):
    return a * b""",
            """def my_function(a, b):
    if a > b:
        return a - b
    else:
        return a + b""",
             """def my_function(a, b):
    if a == 0:
        return b
    else:
        return a * b"""
        ]
        for _ in range(self.population_size):
            # Choose a random simple template or generate a basic one
            if random.random() < 0.7: # Use a template most of the time
                 code = random.choice(simple_templates)
            else: # Generate a basic arithmetic function
                op = random.choice(['+', '-', '*', '/'])
                code = f"""def my_function(a, b):
    return a {op} b"""
            population.append(code)
        return population

    def evaluate_code(self, code):
        """
        Evaluates the fitness of a code string using the external evaluator module.

        Args:
            code (str): The Python code string to evaluate.

        Returns:
            float: The fitness score of the code.
        """
        """
        Evaluates the fitness of a code string using the external evaluator module and checks constraints.

        Args:
            code (str): The Python code string to evaluate.

        Returns:
            float: The fitness score of the code. Returns a very low score if constraints are not met.
        """
        # First, check constraints
        if not check_constraints(code):
            print(f"Code failed constraint checks: {code[:100]}...")
            return -1000.0 # Assign a very low fitness score for invalid code

        # If constraints are met, use the evaluate_code function from the evaluator module
        return run_evaluation(code)

    def tournament_selection(self, population, scores, tournament_size=3):
        """
        Selects individuals for the next generation using tournament selection.

        Args:
            population (list): The current population of individuals (code strings).
            scores (list): The fitness scores for each individual in the population.
            tournament_size (int): The number of individuals in each tournament.

        Returns:
            list: A list of selected individuals (code strings).
        """
        selected = []
        for _ in range(len(population)):
            tournament_indices = random.sample(range(len(population)), tournament_size)
            tournament_scores = [scores[i] for i in tournament_indices]
            # Select the index of the winner (highest score)
            winner_index_in_tournament = tournament_scores.index(max(tournament_scores))
            winner_index_in_population = tournament_indices[winner_index_in_tournament]
            selected.append(population[winner_index_in_population])
        return selected

    def crossover(self, parent1_code, parent2_code):
        """
        Performs crossover between two parent code strings using AST manipulation.

        Args:
            parent1_code (str): The code string of the first parent.
            parent2_code (str): The code string of the second parent.

        Returns:
            tuple: A tuple containing the two child code strings after crossover.
        """
        try:
            # Convert code to AST
            parent1_ast = code_to_ast(parent1_code)
            parent2_ast = code_to_ast(parent2_code)

            # Perform AST crossover
            child1_ast, child2_ast = crossover_ast(parent1_ast, parent2_ast)

            # Convert AST back to code
            child1_code = ast_to_code(child1_ast)
            child2_code = ast_to_code(child2_ast)

            return child1_code, child2_code
        except Exception as e:
            print(f"Crossover failed: {e}")
            # If crossover fails, return original parents
            return parent1_code, parent2_code

    def mutate(self, code):
        """
        Mutates a code string using AST manipulation.

        Args:
            code (str): The code string to mutate.

        Returns:
            str: The mutated code string.
        """
        try:
            # Convert code to AST
            code_ast = code_to_ast(code)

            # Perform AST mutation
            mutated_ast = mutate_ast(code_ast)

            # Convert AST back to code
            mutated_code = ast_to_code(mutated_ast)

            return mutated_code
        except Exception as e:
            print(f"Mutation failed: {e}")
            # If mutation fails, return original code
            return code

    def train_on_local_files(self, directory):
        # Train the algorithm on local files
        # TODO: Implement code analysis and use the code to guide the evolution
        print(f"Training on files in {directory} (Not yet implemented)")
        pass # Placeholder

    def suggest_improvements(self, code):
        # Suggest improvements to the code
        # TODO: Implement code analysis and suggest improvements based on common coding practices and the evaluation results
        return "No suggestions yet. (Not yet implemented)"

    def run_evolutionary_algorithm(self):
        """
        Runs the main loop of the evolutionary algorithm.
        """
        best_code = ""
        best_score = -float('inf') # Initialize with a very low score

        for generation in range(self.generations):
            # Evaluate the population
            scores = [self.evaluate_code(code) for code in self.population]

            # Find the best individual in the population
            avg_score = sum(scores) / len(scores)
            current_best_score = max(scores)
            current_best_code = self.population[scores.index(current_best_score)]

            if current_best_score > best_score:
                best_score = current_best_score
                best_code = current_best_code
                print(f"Generation {generation}: New best score = {best_score}, Avg score = {avg_score}")
                # Print the best code, but truncate if too long
                print(f"Best Code: {best_code[:200]}...")


            # Select the next generation
            selected = self.tournament_selection(self.population, scores)

            # Create the next generation using crossover and mutation
            next_generation = []
            for i in range(0, self.population_size, 2):
                parent1 = selected[i % len(selected)]
                parent2 = selected[(i + 1) % len(selected)]

                # Perform crossover
                if random.random() < self.crossover_rate:
                    child1, child2 = self.crossover(parent1, parent2)
                else:
                    child1, child2 = parent1, parent2 # No crossover, just pass parents

                # Perform mutation
                if random.random() < self.mutation_rate:
                    child1 = self.mutate(child1)
                if random.random() < self.mutation_rate:
                    child2 = self.mutate(child2)

                next_generation.append(child1)
                next_generation.append(child2)

            self.population = next_generation[:self.population_size] # Ensure population size is maintained

        print("\nFinished Evolutionary Algorithm!")
        print(f"Final Best code: {best_code}")
        print(f"Final Best score: {best_score}")
        print(f"Suggestions: {self.suggest_improvements(best_code)}")

        return best_code, best_score

if __name__ == "__main__":
    # Example usage:
    # The evaluator currently tests for a function named 'add' that adds two numbers.
    # The evolutionary algorithm will try to evolve code that passes this test.
    ea = EvolutionaryAlgorithm(population_size=100, generations=50)
    ea.run_evolutionary_algorithm()
