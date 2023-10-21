import pandas as pd
from itertools import product

anz = int(input("Geben Sie die Anzahl an Inputs ein (z.B. 4): "))
input_names = []
for i in range(anz):
    name = input(f"Geben Sie den Namen für Input {i+1} ein: ")
    input_names.append(name)

# Erzeugen aller möglichen Kombinationen der Variablenwerte
truth_table = list(product([0, 1], repeat=anz))
df = pd.DataFrame(truth_table, columns=input_names)

# Speichern des DataFrames in eine Excel-Datei
output_file = input(
    "Geben Sie den Dateinamen für die Excel-Datei an (z.B. 'truth_table.xlsx'): ")
df.to_excel(output_file, index=False)

print(f'Die Wahrheitstabelle wurde in "{output_file}" gespeichert.')
