import itertools

nested_list = [[1, 2], [3, 4], [5, 6]]

# Senza *: chiamerebbe chain con un solo argomento (una lista di liste)
# itertools.chain(nested_list) non restituirebbe il risultato corretto.

# Con *: spacchetta nested_list, quindi chiamerà chain con 3 argomenti separati (le 3 sottoliste).
flattened_list = list(itertools.chain(*nested_list))

print(type(*nested_list))


print(flattened_list)  # Output: [1, 2, 3, 4, 5, 6]
