import pandas as pd
import math  # for log
import sys  # for exit
input_file = input(
    "Enter the filename of the Excel file with the truth table. (e.g. table.xlsx): ")
vhdl_filename = input(
    "Enter the filename of the VHDL file (e.g. bool.vhd): ")
name_entity = input("Enter the entity name: ")
name_architecture = input("Enter the architecture name: ")
df = pd.read_excel(input_file)

number_of_rows = len(df)
number_of_inputs = int(math.log2(number_of_rows))
number_of_outputs = len(df.columns) - number_of_inputs

input_names = ""
for i in range(number_of_inputs):
    # df.columns acesses the names of the columns in the dataframe
    input_names += df.columns[i]
    if i < number_of_inputs - 1:
        input_names += ", "

output_names = ""
for i in range(number_of_outputs):
    output_names += df.columns[i + number_of_inputs]
    if i < number_of_outputs - 1:
        output_names += ", "

vhdl_code = f"""library ieee;
use ieee.std_logic_1164.all;

ENTITY {name_entity} IS
	PORT ({input_names}: IN std_logic;
            {output_names}: OUT std_logic);
END {name_entity};

ARCHITECTURE {name_architecture} OF {name_entity} IS
    SIGNAL var_input_vec : std_logic_vector({number_of_inputs - 1} DOWNTO 0);\n"""
if number_of_outputs > 1:
    vhdl_code += f"\tSIGNAL var_output_vec : std_logic_vector({number_of_outputs - 1} DOWNTO 0);\n"
vhdl_code += f"""\tBEGIN
    var_input_vec <= """
for i in range(number_of_inputs):
    vhdl_code += f"{df.columns[i]}"
    if i < number_of_inputs - 1:
        vhdl_code += " & "
    else:
        vhdl_code += ";\n"
vhdl_code += f"""\tPROCESS (var_input_vec)
        BEGIN\n"""

vhdl_code += f"\t\t\tCASE var_input_vec IS\n"
for i in range(len(df)):
    vhdl_code += f'\t\t\t\tWHEN "'
    for j in range(number_of_inputs):
        vhdl_code += str(df.iloc[i, j])
    vhdl_code += '" => '

    # all in one row if only one output
    if number_of_outputs == 1:
        vhdl_code += f"{df.columns[number_of_inputs]} <= '{df.iloc[i, number_of_inputs]}';\n"
    else:
        vhdl_code += 'var_output_vec <= "'
        for k in range(number_of_outputs):
            vhdl_code += str(df.iloc[i, k + number_of_inputs]) 
        vhdl_code += f'";\n'

if number_of_outputs == 1:
    vhdl_code += f"""\t\t\t\tWHEN OTHERS => {df.columns[number_of_inputs]} <= 'U';\n"""
else:
    vhdl_code += f'''\t\t\t\tWHEN OTHERS => var_output_vec <= "'''
    for k in range(number_of_outputs):
        vhdl_code += "U"
    vhdl_code += f'";\n'
vhdl_code += f"""\t\t\tEND CASE;
    END PROCESS;\n"""

if number_of_outputs > 1:
    vhdl_code += f"\t({output_names}) <= var_output_vec;\n"

vhdl_code += f"END {name_architecture};"

with open(vhdl_filename, "w") as vhdl_file:
    vhdl_file.write(vhdl_code)

while True:
    y_n = input(
        f"Create a testbench for {vhdl_filename}? (y/n): ")
    if y_n == 'y':
        break
    if y_n == 'n':
        sys.exit()

# This part is for the testbench
while True:
    y_n = input(
        f"Should other std_logic states like 'X' and 'U' be included in the testbench besides '1' and '0'? (y/n): ")
    if y_n == 'n':
        other_states = False
        break
    if y_n == 'y':
        other_states = input(
            f"Enter the additional states from this list of states (U, X, Z, W, L, H) seperated by ', ' (e.g. X, Z): ")
        other_states_list = other_states.split(', ')
        break


output_signal_names = ""
for i in range(number_of_outputs):
    output_signal_names += f"s_{df.columns[i + number_of_inputs]}"
    if i < number_of_outputs - 1:
        output_signal_names += ", "

vhdl_bench = f"""library ieee;
use ieee.std_logic_1164.all;

ENTITY tb_{name_entity} IS
END tb_{name_entity};

ARCHITECTURE tb_{name_architecture} OF tb_{name_entity} IS
    COMPONENT {name_entity} IS
        PORT ({input_names}: IN std_logic;
                {output_names}: OUT std_logic);
    END COMPONENT;

    SIGNAL s_input: STD_LOGIC_VECTOR({number_of_inputs - 1} DOWNTO 0);
    SIGNAL {output_signal_names}: STD_LOGIC;
    BEGIN
        dut: {name_entity} PORT MAP("""
for i in range(number_of_inputs):
    vhdl_bench += f"s_input({number_of_inputs - i - 1}), "
vhdl_bench += f"""{output_signal_names});
        PROCESS
        BEGIN\n"""

# This part to test the other states
if other_states != False:
    for state in range(len(other_states_list)):
        for other_state_pos in range(number_of_inputs):
            for row in range(len(df)):
                vhdl_bench += f'\t\t\t\ts_input <= "'
                for input in range(number_of_inputs):
                    if other_state_pos == input:
                        vhdl_bench += other_states_list[state]
                    else:
                        vhdl_bench += str(df.iloc[row, input])
                vhdl_bench += '"; WAIT FOR 1 NS;\n'

for i in range(len(df)):
    vhdl_bench += f'\t\t\t\ts_input <= "'
    for j in range(number_of_inputs):
        vhdl_bench += str(df.iloc[i, j])
    if i < len(df) - 1:
        vhdl_bench += '"; WAIT FOR 1 NS;\n'
    else:
        vhdl_bench += '"; WAIT;\n'
vhdl_bench += f"""\t\t\tEND PROCESS;
END tb_{name_architecture};"""

testbench_filename = "tb_" + vhdl_filename
with open(testbench_filename, "w") as vhdl_file:
    vhdl_file.write(vhdl_bench)
