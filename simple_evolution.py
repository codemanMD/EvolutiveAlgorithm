
import random
import subprocess
import sys

def generate_code():
    # Generate a simple function that adds two numbers
    return "def add(a, b):\n    return a + b"

def evaluate_code(code, timeout=1):
    try:
        # Create a complete Python script
        script = f"""
{code}
if __name__ == '__main__':
    result = add(5, 3)
    print(result)
"""

        # Execute the code in a subprocess with a timeout
        print(f"Generated script: {script}")
        process = subprocess.Popen([sys.executable, "-c", script], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            stdout, stderr = process.communicate(timeout=timeout)  # Timeout after specified seconds
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            print(f"Execution timed out")
            print(f"Stdout: {stdout}")
            print(f"Stderr: {stderr}")
            return 0  # Return 0 if execution times out
        except Exception as e:
            print(f"Execution failed: {e}")
            print(f"Stdout: {stdout}")
            print(f"Stderr: {stderr}")
            return 0  # Return 0 if execution fails

        if process.returncode != 0:
            print(f"Execution failed with error: {stderr}")
            print(f"Stdout: {stdout}")
            print(f"Stderr: {stderr}")
            return 0  # Return 0 if execution returns an error

        # Check if the output is 8
        if stdout.strip() == "8":
            return 1  # Return 1 if the output is 8
        else:
            return 0  # Return 0 otherwise

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return 0  # Return 0 if any unexpected error occurs

def tournament_selection(population, scores, tournament_size=3):
    # Select individuals for the next generation using tournament selection
    selected = []
    for _ in range(len(population)):
        tournament_indices = random.sample(range(len(population)), tournament_size)
        tournament_scores = [scores[i] for i in tournament_indices]
        winner_index = tournament_indices[tournament_scores.index(max(tournament_scores))]
        selected.append(population[winner_index])
    return selected

def crossover(parent1, parent2):
    # Perform single-point crossover
    index = random.randint(1, len(parent1) - 1)
    child1 = parent1[:index] + parent2[index:]
    child2 = parent2[:index] + parent1[index:]
    return child1, child2

import ast

def mutate(code, mutation_rate=0.01):
    # Mutate the code using AST manipulation
    try:
        tree = ast.parse(code)

        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp):
                if random.random() < mutation_rate:
                    # Change the operator
                    operators = [ast.Add, ast.Sub, ast.Mult, ast.Div]
                    new_operator = random.choice(operators)
                    node.op = new_operator()
            elif isinstance(node, ast.Name):
                if random.random() < mutation_rate:
                    # Change the variable name
                    node.id = "x" if node.id == "a" else "a"

        mutated_code = ast.unparse(tree)
        return mutated_code
    except SyntaxError:
        # If the code is invalid, return it unchanged
        return code

def run_evolutionary_algorithm(population_size=50, generations=100):
    # Run the evolutionary algorithm
    population = [generate_code() for _ in range(population_size)]
    best_code = ""
    best_score = 0

    for generation in range(generations):
        # Evaluate the population
        scores = [evaluate_code(code) for code in population]

        # Find the best individual in the population
        if max(scores) > best_score:
            best_score = max(scores)
            best_code = population[scores.index(max(scores))]
            print(f"Generation {generation}: Best score = {best_score}")

        # Select the next generation
        selected = tournament_selection(population, scores)

        # Create the next generation using crossover and mutation
        next_generation = []
        for i in range(0, population_size, 2):
            parent1 = selected[i % len(selected)]
            parent2 = selected[(i + 1) % len(selected)]
            child1, child2 = crossover(parent1, parent2)
            child1 = mutate(child1)
            child2 = mutate(child2)
            next_generation.append(child1)
            next_generation.append(child2)

        population = next_generation

    print("Finished!")
    print(f"Best code: {best_code}")
    print(f"Best score: {best_score}")

    return best_code, best_score

if __name__ == "__main__":
    run_evolutionary_algorithm()
