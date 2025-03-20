import os
import ast
import tokenize
from datetime import datetime

def count_functions_reactives_and_comments(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        # Legge il codice
        code = file.read()

        # Parse il codice tramite AST per le funzioni
        tree = ast.parse(code)

        # Conta il numero di funzioni
        num_functions = len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)])

        # Conta il numero di righe di codice non vuote
        num_lines = len([line for line in code.splitlines() if line.strip()])

        # Conta il numero di commenti
        num_comments = code.count("#")

        # Conta il numero di reactive e altri costrutti Shiny
        num_reactives = code.count("@reactive")
        num_renders = code.count("@render")

        return num_functions, num_lines, num_comments, num_reactives, num_renders

def analyze_directory(directory_path):
    results = {}

    # Itera attraverso tutti i file .py nella directory
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                num_functions, num_lines, num_comments, num_reactives, num_renders = count_functions_reactives_and_comments(file_path)
                results[file_path] = {
                    'functions': num_functions,
                    'lines': num_lines,
                    'comments': num_comments,
                    'reactives': num_reactives,
                    'renders': num_renders
                }

    return results

def write_results_to_file(results):
    # Ottieni la data odierna in formato YYYY-MM-DD
    today_date = datetime.today().strftime('%Y-%m-%d-%H-%M-%S')
    file_name = f'output_{today_date}.txt'

    # Scrivi i risultati nel file
    with open(file_name, 'w', encoding='utf-8') as file:
        for file_path, data in results.items():
            file.write(f"File: {file_path}\n")
            file.write(f"  Numero di funzioni: {data['functions']}\n")
            file.write(f"  Numero di righe di codice (non vuote): {data['lines']}\n")
            file.write(f"  Numero di commenti: {data['comments']}\n")
            file.write(f"  Numero di reactive: {data['reactives']}\n")
            file.write(f"  Numero di render: {data['renders']}\n")
            file.write("\n")

    print(f"I risultati sono stati scritti nel file: {file_name}")

# Impostare la directory da analizzare
directory_path = './'  # Sostituisci con il tuo percorso
results = analyze_directory(directory_path)

# Scrivi i risultati nel file di output
write_results_to_file(results)
