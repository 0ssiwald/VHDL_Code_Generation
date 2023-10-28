import pandas as pd
import math
from itertools import combinations


input_file = input(
    "Enter the filename of the Excel file with the truth table. (e.g. table.xlsx): ")

df = pd.read_excel(input_file)
number_of_rows = len(df)
number_of_inputs = int(math.log2(number_of_rows))


def truth_table_to_minterms(df):
    # Remove rows with 0 in the specified column
    df = df[df[df.columns[number_of_inputs]] == 1].copy()
    # Count the number of 1s in each row in the anz_inputs columns
    row_sums = df.iloc[:, :number_of_inputs].sum(axis=1)
    df['number_of_ones'] = row_sums
    # sort dataframe by the number of ones
    df = df.sort_values(by='number_of_ones')
    # Drop the original Output column using .loc
    df = df.drop(columns=df.columns[number_of_inputs])
    df = df.reset_index(drop=True)
    return df


def check_for_doubled_terms(result, merged_term):
    for j in range(len(result)):
        diff_count = 0
        for col in range(number_of_inputs):
            if merged_term.iloc[col] != result.iloc[j, col]:
                diff_count += 1
        if diff_count == 0:
            return True
    return False


def compare_terms_in_adjacent_groups(df):
    terms_got_minimized = False
    # Reset the indexes of the dataframe
    df = df.reset_index(drop=True)
    # New dataframe for results
    result = pd.DataFrame(columns=df.columns)
    for i in range(len(df)):
        # To add rows that cant be further minimized to the new dataframe
        term_can_be_minimized = False
        # if this is a term with one of the biggest value of number_of_ones
        if df.at[i, 'number_of_ones'] == df.at[len(df) - 1, 'number_of_ones']:
            # checks the terms backwards for terms that can be reduced to stop them from being copied to results
            for j in range(i, 0, -1):
                if abs(df.at[i, 'number_of_ones'] - df.at[j, 'number_of_ones']) == 1:
                    # Look if there is only one diffrence between rows
                    diff_count = 0
                    for col in range(number_of_inputs):
                        if df.iloc[i, col] != df.iloc[j, col]:
                            diff_count += 1
                    if diff_count == 1:
                        term_can_be_minimized = True
        else:
            for j in range(i + 1, len(df)):
                diff_count = 0
                block_flag = False
                # Compare adjesent rows if there is only 1 diffrence in the number of ones
                if abs(df.at[i, 'number_of_ones'] - df.at[j, 'number_of_ones']) == 1:
                    # Look if there is only one diffrence between rows
                    for col in range(number_of_inputs):
                        if df.iloc[i, col] != df.iloc[j, col]:
                            diff_count += 1
                            if df.iloc[i, col] == '-' or df.iloc[j, col] == '-':
                                block_flag = True
                    if diff_count == 1 and block_flag == False:
                        term_can_be_minimized = True
                        # Add row to new result dataframe
                        merged_term = df.loc[i].copy()
                        if 'included_terms' in df.columns:
                            merged_term['included_terms'] = merged_term['included_terms'] + \
                                f", {i}, {j}"
                        else:
                            merged_term['included_terms'] = f"{i}, {j}"
                        for col in range(number_of_inputs):
                            if df.iloc[i, col] != df.iloc[j, col]:
                                merged_term[df.columns[col]] = '-'
                        if not check_for_doubled_terms(result, merged_term):
                            terms_got_minimized = True
                            result = result.append(
                                merged_term, ignore_index=True)
        # If the term is completly minimized it gets still copied to the new dataframe
        if term_can_be_minimized == False:
            result = result.append(df.loc[i].copy())
    result = result.reset_index(drop=True)
    return result, terms_got_minimized


def eliminating_table(minterms, reduced_df):
    # Create an empty DataFrame with sequential column names
    eliminating_df = pd.DataFrame(columns=range(len(minterms)))
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


def print_minterms(selected_terms, reduced_df):
    dmf_string = ""
    dmf_string += "DMF = "
    for row in selected_terms:
        dmf_string += "( "
        for col in range(number_of_inputs):
            if reduced_df.iloc[row, col] == 0:
                dmf_string += f"not {reduced_df.columns[col]} and "
            elif reduced_df.iloc[row, col] == 1:
                dmf_string += f"{reduced_df.columns[col]} and "
        # removes the last "and "
        dmf_string = dmf_string[:-4]
        dmf_string += ") or "
    # removes the last " or "
    dmf_string = dmf_string[:-4]
    dmf_string += "\n\n"
    print(dmf_string)


print("\nThe Truthtable form the exel-file\n")
print(df)
minterms = truth_table_to_minterms(df)
print("\nMinterms sorted by the numbers of '1'\n")
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
selected_terms = reduce_eliminating_table(eliminating_df)
print_minterms(selected_terms, reduced_df)
