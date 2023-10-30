import pandas as pd
from itertools import product

number_of_inputs = int(input("Enter the number of inputs (e.g. 4): "))
input_names = []
for i in range(number_of_inputs):
    name = input(f"Enter a name for input {i+1}: ")
    input_names.append(name)

# Create all combinations for the inputs
truth_table = list(product([0, 1], repeat=number_of_inputs))
df = pd.DataFrame(truth_table, columns=input_names)

# Save as exel file
output_file = input(
    "Enter a filename for the exel file (e.g. 'truth_table.xlsx'): ")
df.to_excel(output_file, index=False)
