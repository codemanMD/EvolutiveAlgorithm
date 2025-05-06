from algortimoevolutivo.ast_modifier import code_to_ast, ast_to_code, mutate_ast, crossover_ast
from algortimoevolutivo.evaluator import evaluate_code
from algortimoevolutivo.constraints import check_constraints
import random

class EvolutionaryAlgorithm:
    def __init__(self, initial_code, population_size=10, generations=100):
        self.initial_code = initial_code
        self.population_size = population_size
        self.generations = generations
        self.population = []

    def initialize_population(self):
        """
        Initializes the population with variations of the initial code.
        """
        initial_ast = code_to_ast(self.initial_code)
        self.population = [mutate_ast(initial_ast) for _ in range(self.population_size)]

    def evolve(self):
        """
        Runs the evolutionary algorithm for a fixed number of generations.
        """
        self.initialize_population()

        for generation in range(self.generations):
            print(f"Generation {generation+1}/{self.generations}")

            # Evaluate the population
            fitness_scores = []
            for individual in self.population:
                code = ast_to_code(individual)
                if check_constraints(code):
                    fitness = evaluate_code(code)
                    fitness_scores.append((fitness, individual))
                else:
                    fitness_scores.append((0.0, individual)) # Assign a fitness of 0 to individuals that violate constraints

            fitness_scores.sort(key=lambda x: x[0], reverse=True)

            # Select parents (simple truncation selection)
            num_parents = self.population_size // 2
            parents = [individual for fitness, individual in fitness_scores[:num_parents]]

            # Create next generation through crossover and mutation
            next_generation = []
            while len(next_generation) < self.population_size:
                parent1 = random.choice(parents)
                parent2 = random.choice(parents)

                # Crossover
                child1, child2 = crossover_ast(parent1, parent2)

                # Mutate
                next_generation.append(mutate_ast(child1))
                if len(next_generation) < self.population_size:
                    next_generation.append(mutate_ast(child2))

            self.population = next_generation

        # Return the best individual
        best_individual = max([(evaluate_code(ast_to_code(individual)), individual) for individual in self.population], key=lambda x: x[0])[1]
        return ast_to_code(best_individual)

if __name__ == "__main__":
    # Example usage
    initial_code = """
def add(a, b):
    return a + b
"""
    ea = EvolutionaryAlgorithm(initial_code)
    best_code = ea.evolve()
    print("Best evolved code:")
    print(best_code)
