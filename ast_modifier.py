import ast
import astor
import random

def code_to_ast(code):
    """
    Converts Python code to an Abstract Syntax Tree (AST).
    Handles potential parsing errors.
    """
    try:
        return ast.parse(code)
    except SyntaxError as e:
        print(f"Syntax error parsing code to AST: {e}")
        return None # Return None if parsing fails

def ast_to_code(ast_node):
    """
    Converts an AST node to Python code.
    Handles potential conversion errors.
    """
    try:
        return astor.to_source(ast_node)
    except Exception as e:
        print(f"Error converting AST to code: {e}")
        return "" # Return empty string if conversion fails

def mutate_ast(ast_node):
    """
    Mutates an AST node with various strategies.
    """
    if ast_node is None:
        return None

    # Create a list of potential mutation operations
    mutation_ops = []

    # Mutate: change a constant value
    mutation_ops.append(lambda node: isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and setattr(node, 'value', node.value + random.randint(-5, 5)))

    # Mutate: change the operator of a binary operation
    operators = [ast.Add(), ast.Sub(), ast.Mult(), ast.Div(), ast.Mod()] # Added Modulo
    mutation_ops.append(lambda node: isinstance(node, ast.BinOp) and setattr(node, 'op', random.choice(operators)))

    # Mutate: change the name of a variable (simple renaming)
    mutation_ops.append(lambda node: isinstance(node, ast.Name) and node.id not in ['a', 'b'] and setattr(node, 'id', node.id + str(random.randint(0, 9)))) # Avoid changing function arguments for now

    # Mutate: swap operands in a binary operation
    mutation_ops.append(lambda node: isinstance(node, ast.BinOp) and setattr(node, 'left', node.right) or setattr(node, 'right', node.left)) # This needs careful handling of return value

    # Mutate: add a simple return statement (if not already present)
    mutation_ops.append(lambda node: isinstance(node, ast.FunctionDef) and not any(isinstance(body_item, ast.Return) for body_item in node.body) and node.body.append(ast.parse("return None").body[0]))

    # Mutate: remove a statement (if more than one)
    mutation_ops.append(lambda node: isinstance(node, ast.FunctionDef) and len(node.body) > 1 and node.body.pop(random.randint(0, len(node.body) - 1)))

    # Apply a random mutation operation to a random node
    successful_mutation = False
    attempts = 0
    while not successful_mutation and attempts < 10: # Try a few times
        chosen_op = random.choice(mutation_ops)
        # Walk the AST and try to apply the mutation
        for node in ast.walk(ast_node):
            try:
                if chosen_op(node): # If the mutation was applicable and successful
                    successful_mutation = True
                    break # Apply only one mutation per call
            except Exception:
                pass # Ignore errors during mutation attempt
        attempts += 1

    return ast_node

def crossover_ast(ast_node1, ast_node2):
    """
    Performs crossover between two AST nodes.
    Swaps a random statement between two function definitions if available.
    """
    if ast_node1 is None or ast_node2 is None:
        return ast_node1, ast_node2

    func_defs1 = [node for node in ast.walk(ast_node1) if isinstance(node, ast.FunctionDef)]
    func_defs2 = [node for node in ast.walk(ast_node2) if isinstance(node, ast.FunctionDef)]

    if func_defs1 and func_defs2:
        # Choose a random function definition from each node
        func1 = random.choice(func_defs1)
        func2 = random.choice(func_defs2)

        if func1.body and func2.body:
            # Choose a random statement from each function body
            stmt1_index = random.randint(0, len(func1.body) - 1)
            stmt2_index = random.randint(0, len(func2.body) - 1)

            # Swap the statements
            func1.body[stmt1_index], func2.body[stmt2_index] = func2.body[stmt2_index], func1.body[stmt1_index]

    return ast_node1, ast_node2

# TODO: Implement more sophisticated genetic operators (mutation, crossover)
# Consider type checking and semantic validity during genetic operations.
