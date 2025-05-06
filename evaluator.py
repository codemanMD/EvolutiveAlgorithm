import subprocess
import time
import sys
import ast

def run_tests(code, test_cases, function_name="my_function", timeout=1):
    """
    Runs test cases on the given code in a sandboxed environment.

    Args:
        code (str): The Python code string to test.
        test_cases (list): A list of tuples, where each tuple is (input_args, expected_output).
                           input_args should be a tuple of arguments for the function.
        function_name (str): The name of the function to test within the code.
        timeout (int): The maximum time in seconds to allow the code execution.

    Returns:
        int: The number of test cases passed.
    """
    passed_tests = 0
    for inputs, expected_output in test_cases:
        # Create a script to execute the code and test case
        # The script will read inputs and expected output from stdin
        script = f"""
{code}
import sys
import json

try:
    # Read inputs and expected output from stdin
    data = json.load(sys.stdin)
    inputs = data['inputs']
    expected_output = data['expected_output']

    # Check if the function exists
    if '{function_name}' not in locals():
        print(f"EXECUTION_ERROR: Function '{function_name}' not found")
        sys.exit(1) # Function not found

    # Get the function object
    func = locals()['{function_name}']

    # Execute the function with the given inputs
    result = func(*inputs)

    # Compare the result with the expected output
    if result == expected_output:
        print("TEST_PASSED")
    else:
        print("TEST_FAILED")
        # Optionally print actual vs expected for failed tests
        # print(f"TEST_FAILED: Expected {{expected_output}}, Got {{result}}")

except Exception as e:
    # Print any exceptions for debugging
    print(f"EXECUTION_ERROR: {{e}}")
    sys.exit(1) # Indicate failure
"""
        try:
            # Prepare data to send via stdin
            test_data = json.dumps({'inputs': inputs, 'expected_output': expected_output})

            # Execute the code in a subprocess with a timeout, sending data via stdin
            process = subprocess.Popen(
                [sys.executable, "-c", script],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate(input=test_data, timeout=timeout)

            if process.returncode != 0:
                # Script exited with an error (syntax, function not found, or caught exception)
                print(f"Test execution failed for inputs {inputs}:")
                if stdout: # stdout might contain the EXECUTION_ERROR message
                    print(stdout.strip())
                if stderr: # stderr might contain syntax errors or other system errors
                    print(stderr.strip())
            elif "TEST_PASSED" in stdout:
                passed_tests += 1
            elif "TEST_FAILED" in stdout:
                print(f"Test failed for inputs {inputs}: Expected {expected_output}, Got result different from expected.") # Avoid printing actual result from stdout unless the script is modified to print it on failure
            else:
                # Unexpected output from the script
                print(f"Unexpected output during test for inputs {inputs}: {stdout.strip()}")
                if stderr:
                    print(stderr.strip())


        except subprocess.TimeoutExpired:
            process.kill()
            print(f"Test execution timed out for inputs {inputs}")
        except Exception as e:
            print(f"An unexpected error occurred during test execution for inputs {inputs}: {e}")

    return passed_tests

def run_simulation(code, timeout=1):
    """
    Runs a simulation to evaluate the code's performance in a sandboxed environment.
    This is a placeholder and can be expanded for more complex simulations.

    Args:
        code (str): The Python code string to simulate.
        timeout (int): The maximum time in seconds to allow the code execution.

    Returns:
        float: A score based on the simulation (currently just checks for successful execution).
    """
    try:
        # Execute the code in a subprocess with a timeout
        start_time = time.time()
        process = subprocess.Popen([sys.executable, "-c", code], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            stdout, stderr = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            print(f"Simulation timed out")
            return 0.0
        except Exception as e:
            print(f"Simulation failed: {e}")
            return 0.0

        end_time = time.time()
        execution_time = end_time - start_time

        if process.returncode != 0:
            print(f"Simulation failed with error: {stderr.strip()}")
            return 0.0

        # Simple reward based on successful execution (can be improved)
        return 1.0

    except Exception as e:
        print(f"An unexpected error occurred during simulation: {e}")
        return 0.0

def evaluate_code(code, test_cases=None, function_name="my_function"):
    """
    Evaluates the performance of the given code using tests and simulation.

    Args:
        code (str): The Python code string to evaluate.
        test_cases (list, optional): A list of test cases for the code. Defaults to a simple test for a conditional function.
        function_name (str): The name of the function to test within the code.

    Returns:
        float: The overall fitness score.
    """
    if test_cases is None:
        # Default test cases for a function that returns a-b if a>b, else a+b
        test_cases = [
            ((5, 3), 2),  # a > b, should return a - b
            ((3, 5), 8),  # a <= b, should return a + b
            ((5, 5), 10), # a <= b, should return a + b
            ((0, 0), 0),  # a <= b, should return a + b
            ((10, 4), 6)  # a > b, should return a - b
        ]

    # Run tests and get the number of passed tests
    passed_tests = run_tests(code, test_cases, function_name)

    # Run simulation (currently just checks for execution)
    simulation_score = run_simulation(code)

    # Combine results: prioritize passing tests, then consider simulation score
    # A simple scoring mechanism: 1 point for each passed test + simulation score (0 or 1)
    # This can be made more sophisticated based on the specific problem.
    fitness_score = passed_tests + simulation_score

    return fitness_score

if __name__ == "__main__":
    # Example usage with the new default test cases:
    code_to_test = """
def my_function(a, b):
    if a > b:
        return a - b
    else:
        return a + b
"""
    score = evaluate_code(code_to_test)
    print(f"Score for conditional function: {score}")

    code_to_test_fail = """
def my_function(a, b):
    return a + b # Incorrect for some test cases
"""
    score_fail = evaluate_code(code_to_test_fail)
    print(f"Score for add function (expecting conditional): {score_fail}")

    code_syntax_error = """
def my_function(a, b)
    return a + b # Missing colon
"""
    score_syntax = evaluate_code(code_syntax_error)
    print(f"Score for syntax error: {score_syntax}")
