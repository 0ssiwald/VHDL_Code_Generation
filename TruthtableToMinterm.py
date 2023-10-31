import pandas as pd
import math
from itertools import combinations


def truth_table_to_minterms(df, is_a_dnf):
    if is_a_dnf:
        remove_from_rows = 0
    else:
        remove_from_rows = 1
     # Add an empty column 'is_a_dont_care'
    df['is_a_dont_care'] = False
    # Remove rows with 0 in the specified column (take 0 and dont cares)
    df = df[df[df.columns[number_of_inputs]] != remove_from_rows].copy()
    for row in range(len(df)):
        if df.iloc[row, number_of_inputs] != 1 and df.iloc[row, number_of_inputs] != 0:
            df.iloc[row, number_of_inputs + 1] = True
    # Count the number of 1s in each row in the anz_inputs columns
    row_sums = df.iloc[:, : number_of_inputs].sum(axis=1)
    df['number_of_ones'] = row_sums
    # sort dataframe by the number of ones
    df = df.sort_values(by='number_of_ones')
    # Drop the original Output column using
    df = df.drop(columns=df.columns[number_of_inputs])
    df = df.reset_index(drop=True)
    return df


def check_for_doubled_terms(result, merged_term):
    for j in range(len(result)):
        diff_count = 0
        for col in range(number_of_inputs):
            if merged_term[df.columns[col]] != result[j][df.columns[col]]:
                diff_count += 1
        if diff_count == 0:
            return True
    return False


def compare_terms_in_adjacent_groups(df):
    terms_got_minimized = False

    # Remove the is_a_dont_care column
    if 'is_a_dont_care' in df.columns:
        df = df.drop(columns='is_a_dont_care')
    # Add an empty column 'is_a_dont_care'
    if 'included_terms' not in df.columns:
        df['included_terms'] = ''
    # Reset the indexes of the dataframe
    df = df.reset_index(drop=True)

    # New dataframe for results
    result_data = []

    for i in range(len(df)):
        term_can_be_minimized = False

        if df.at[i, 'number_of_ones'] == df.at[len(df) - 1, 'number_of_ones']:
            # Check for terms that can be reduced
            for j in range(i, 0, -1):
                if abs(df.at[i, 'number_of_ones'] - df.at[j, 'number_of_ones']) == 1:
                    diff_count = 0
                    block_flag = False

                    for col in range(number_of_inputs):
                        if df.iloc[i, col] != df.iloc[j, col]:
                            diff_count += 1
                            if df.iloc[i, col] == '-' or df.iloc[j, col] == '-':
                                block_flag = True

                    if diff_count == 1 and not block_flag:
                        term_can_be_minimized = True
        else:
            for j in range(i + 1, len(df)):
                diff_count = 0
                block_flag = False

                if abs(df.at[i, 'number_of_ones'] - df.at[j, 'number_of_ones']) == 1:
                    for col in range(number_of_inputs):
                        if df.iloc[i, col] != df.iloc[j, col]:
                            diff_count += 1
                            if df.iloc[i, col] == '-' or df.iloc[j, col] == '-':
                                block_flag = True

                    if diff_count == 1 and not block_flag:
                        term_can_be_minimized = True
                        merged_term = df.loc[i].copy()
                        merged_term['included_terms'] = f"{i} {j} " + \
                            merged_term['included_terms']
                        for col in range(number_of_inputs):
                            if df.iloc[i, col] != df.iloc[j, col]:
                                merged_term[df.columns[col]] = '-'

                        if not check_for_doubled_terms(result_data, merged_term):
                            terms_got_minimized = True
                            result_data.append(pd.Series(merged_term))

        if not term_can_be_minimized:
            # Convert row to dictionary
            result_data.append(pd.Series(df.loc[i]))

    result = pd.DataFrame(result_data, columns=df.columns)
    return result, terms_got_minimized


def eliminating_table(minterms, reduced_df):
   # remove the dont_care rows
    minterms = minterms.loc[~minterms['is_a_dont_care']].copy()
    # Create an empty DataFrame with the colum names == the indexes of the minterms
    eliminating_df = pd.DataFrame(columns=minterms.index)
    for _ in range(len(reduced_df)):
        eliminating_df.loc[len(eliminating_df)] = '' * len(minterms)
    for i in range(len(reduced_df)):
        for j in range(len(minterms)):
            diff_count = 0
            for col in range(number_of_inputs):
                if not (reduced_df.iloc[i, col] == minterms.iloc[j, col] or reduced_df.iloc[i, col] == '-'):
                    diff_count += 1
            if diff_count == 0:
                eliminating_df.iloc[i, j] = 'X'
    return eliminating_df


def visulize_selected_terms(df, selected_row):
    columns_with_x = list()
    for col in range(df.shape[1]):
        if df.iloc[selected_row, col] == 'X':
            columns_with_x.append(col)
        else:
            df.iloc[selected_row, col] = '='
    # iterates to draw the colums that get removed by the selection
    for col in range(df.shape[1]):
        for index, row in df.iterrows():
            if col in columns_with_x and df.iloc[index, col] != 'X' and df.iloc[index, col] != '=':
                df.iloc[index, col] = '-'
    print(df)
    print("\n")
    return


def reduce_eliminating_table(df):
    # List of the still required columns
    required_columns = list(df.columns)
    # result_df = pd.DataFrame(columns=df.columns)
    selected_rows = list()
    while required_columns:
        max_x_count = 0
        best_row = None
        for index, row in df.iterrows():
            x_count = sum(1 for col in required_columns if row[col] == 'X')
            if x_count >= max_x_count:
                max_x_count = x_count
                best_row = row
                best_row_index = index
        if best_row is not None:
            # result_df = result_df.append(best_row, ignore_index=True)
            selected_rows.append(best_row_index)
            # copy because iterating through a list were items are getting removed leads to errors
            columns_copy = required_columns.copy()
            for col in columns_copy:
                if best_row[col] == 'X':
                    required_columns.remove(col)
            visulize_selected_terms(df, best_row_index)
        else:
            break
    return selected_rows


def print_minterms(selected_terms, reduced_df, is_a_dnf):
    if is_a_dnf:
        logic1 = "and"
        logic2 = "or"
        truth_value = 1
        inverted_truth_value = 0
        min_string = "DMF = "
    else:
        logic1 = "or"
        logic2 = "and"
        truth_value = 0
        inverted_truth_value = 1
        min_string = "KMF = "

    for row in selected_terms:
        min_string += "( "
        for col in range(number_of_inputs):
            if reduced_df.iloc[row, col] == truth_value:
                min_string += f"{reduced_df.columns[col]} {logic1} "
            elif reduced_df.iloc[row, col] == inverted_truth_value:
                min_string += f"not {reduced_df.columns[col]} {logic1} "
        # removes the last "and "
        min_string = min_string[:-4]
        min_string += f") {logic2} "
    # removes the last " or "
    min_string = min_string[:-4]
    min_string += "\n\n"
    print(min_string)


input_file = input(
    "Enter the filename of the Excel file with the truth table. (e.g. table.xlsx): ")
while True:
    y_n = input(
        f"Should the result be a disjunctive minimal form (DMF)? (y/n): ")
    if y_n == 'y':
        print("Performing Quine-McCluskey algorithm with DNF...\n")
        is_a_dnf = True
        break
    if y_n == 'n':
        print("Performing Quine-McCluskey algorithm with KNF...\n")
        is_a_dnf = False
        break

df = pd.read_excel(input_file)
number_of_rows = len(df)
number_of_inputs = int(math.log2(number_of_rows))


print("\nThe Truthtable form the exel-file\n")
print(df)
if is_a_dnf:
    print("\nMinterms sorted by the numbers of '1'\n")
else:
    print("\nMinterms sorted by the numbers of '0'\n")
minterms = truth_table_to_minterms(df, is_a_dnf)
print(minterms)
print("\nReducing the terms: \n")
reduced_df = minterms
terms_got_minimized = True
while terms_got_minimized == True:
    reduced_df, terms_got_minimized = compare_terms_in_adjacent_groups(
        reduced_df)
    if terms_got_minimized == True:
        print(reduced_df)
        print("\n")
print("\nSelecting terms: \n")
eliminating_df = eliminating_table(minterms, reduced_df)
print(eliminating_df)
print("\n")
selected_terms = reduce_eliminating_table(eliminating_df)
print_minterms(selected_terms, reduced_df, is_a_dnf)
