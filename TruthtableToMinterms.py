import pandas as pd
import math
from itertools import combinations

# For test
input_file = "table.xlsx"
# input_file = input(
#    "Geben Sie den Dateinamen der Excel-Datei mit der Turthtable ein (z.B table.xlsx): ")

# Lese die Excel-Datei ein
df = pd.read_excel(input_file)
anz_rows = len(df)
anz_inputs = int(math.log2(anz_rows))


# function to convert a Pandas DataFrame into a list of minterms
def truth_table_to_minterms(df):
    minterms = []
    for index, row in df.iterrows():
        if row[anz_inputs] == 1:  # works at the moment only for one output
            minterms.append(index)
    return minterms


# Group minterms by the number of '1's in their binary representation
def group_minterms(minterms):
    groups = {}
    for minterm in minterms:
        num_ones = bin(minterm).count('1')
        if num_ones not in groups:
            groups[num_ones] = []
        groups[num_ones].append(minterm)
    return groups


# Compares twp terms and if there is only one diffrence it returns true
def compare_two_terms(row1, row2):
    number_of_diffrences = 0
    pos_of_diffrence = -1
    for i in range(anz_inputs):
        if df.iloc[row1, i] != df.iloc[row2, i]:
            number_of_diffrences += 1
            pos_of_diffrence = i
    if number_of_diffrences == 1:
        return pos_of_diffrence
    else:
        return False


def compare_terms_in_adjacent_groups(groups):
    result = {}
    keys = list(groups.keys())
    keys.sort()

    for i in range(len(keys) - 1):
        key1, key2 = keys[i], keys[i + 1]
        values1 = groups[key1]
        values2 = groups[key2]
        for value1 in values1:
            for value2 in values2:
                compare_two_terms(value1, value2)

    return result


def quine_mccluskey(groups):
    prime_implicants = []
    while groups:
        new_groups = {}
        used_minterms = set()
        group_keys = list(groups.keys())
        group_keys.sort()

        for i in range(len(group_keys) - 1):
            current_group = group_keys[i]
            next_group = group_keys[i + 1]

            for m1 in groups[current_group]:
                for m2 in groups[next_group]:
                    if bin(m1 ^ m2).count('1') == 1:
                        used_minterms.add(m1)
                        used_minterms.add(m2)
                        merged_minterm = m1 & m2
                        if merged_minterm not in new_groups:
                            new_groups[bin(merged_minterm).count('1')] = []
                        new_groups[bin(merged_minterm).count(
                            '1')].append(merged_minterm)

        prime_implicants.extend(used_minterms)
        groups = {key: value for key,
                  value in groups.items() if key not in new_groups}
        if not groups:
            break
        groups = new_groups

    return prime_implicants

# Step 4: Convert the minimized terms back to the original variable representation


def get_minimal_terms(prime_implicants):

    minimal_terms = []
    for implicant in prime_implicants:
        minimal_term = []
        for i in range(len(bin(implicant)) - 2):
            if (implicant >> i) & 1:
                minimal_term.append(f'A{i}')
            else:
                minimal_term.append(f"A{i}'")
        minimal_terms.append(''.join(minimal_term))
    return minimal_terms


minterms = truth_table_to_minterms(df)
groups = group_minterms(minterms)
prime_implicants = quine_mccluskey(groups)
minimal_terms = get_minimal_terms(prime_implicants)

print(df)
print(minterms)
print(groups)
print(prime_implicants)
print(minimal_terms)
