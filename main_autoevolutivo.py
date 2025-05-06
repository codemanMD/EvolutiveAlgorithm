import sys
import os

# Add the algortimoevolutivo directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'algortimoevolutivo'))

from evolutionary_algorithm_v2 import EvolutionaryAlgorithm
# We will integrate other modules later

def main():
    """
    Main function to run the autoevolutivo algorithm.
    """
    print("Starting the AutoEvolutivo Algorithm...")

    # Initialize and run the evolutionary algorithm
    # Parameters like population_size, generations, etc., can be configured
    # or passed as arguments later.
    ea = EvolutionaryAlgorithm(population_size=50, generations=100)
    ea.run_evolutionary_algorithm()

    print("AutoEvolutivo Algorithm finished.")

if __name__ == "__main__":
    main()
