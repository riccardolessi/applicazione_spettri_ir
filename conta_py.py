# import os

# def conta_file_py():
#     directory = os.path.dirname(os.path.abspath(__file__))
#     count = sum(1 for root, _, files in os.walk(directory) for file in files if file.endswith(".py"))
#     print(count)

# conta_file_py()

import ast
code = "one_plus_two = 1 + 2"

tree = ast.parse(code)

print(ast.dump(tree, indent = 4))
