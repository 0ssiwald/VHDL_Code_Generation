import pandas as pd
import math  # für log
import sys  # für exit
# I have a truth table as a pandas dataframe in python. Can you implement the Quine McCluskey Algorithm to get the min terms?
input_file = input(
    "Geben Sie den Dateinamen der Excel-Datei mit der Turthtable ein (z.B table.xlsx): ")
vhdl_filename = input(
    "Geben Sie den Dateinamen der zu erstellenden VHDL Datei ein (z.B bool.vhd): ")
name_entity = input("Geben Sie den Namen der Entity ein: ")
name_architecture = input("Geben Sie den Namen der Architecture ein: ")
# Lese die Excel-Datei ein
df = pd.read_excel(input_file)

anz_rows = len(df)
anz_inputs = int(math.log2(anz_rows))
anz_outputs = len(df.columns) - anz_inputs

input_names = ""
for i in range(anz_inputs):
    # df.columns acesses the names of the columns in the dataframe
    input_names += df.columns[i]
    if i < anz_inputs - 1:
        input_names += ", "

output_names = ""
for i in range(anz_outputs):
    output_names += df.columns[i + anz_inputs]
    if i < anz_outputs - 1:
        output_names += ", "

vhdl_code = f"""library ieee;
use ieee.std_logic_1164.all;

ENTITY {name_entity} IS
	PORT ({input_names}: IN std_logic;
            {output_names}: OUT std_logic);
END {name_entity};

ARCHITECTURE {name_architecture} OF {name_entity} IS
    BEGIN
        PROCESS ({input_names})
            VARIABLE var_input_vec : std_logic_vector({anz_inputs - 1} DOWNTO 0);
            BEGIN
            var_input_vec := """
for i in range(anz_inputs):
    vhdl_code += f"{df.columns[i]}"
    if i < anz_inputs - 1:
        vhdl_code += " & "
    else:
        vhdl_code += ";\n"
vhdl_code += f"\t\t\tCASE var_input_vec IS\n"
for i in range(len(df)):
    vhdl_code += f'\t\t\t\tWHEN "'
    for j in range(anz_inputs):
        vhdl_code += str(df.iloc[i, j])

    vhdl_code += '" => '
    # alles in einer Zeile bei nur einem output
    if anz_outputs > 1:
        vhdl_code += f'\n'
    for k in range(anz_outputs):
        if anz_outputs > 1:
            vhdl_code += f"\t\t\t\t\t"
        vhdl_code += f"{df.columns[anz_inputs + k]} <= '{df.iloc[i, anz_inputs + k]}';\n"
vhdl_code += f"""\t\t\t\tWHEN OTHERS => {df.columns[anz_inputs]} <= 'U';
            END CASE;
        END PROCESS;
END {name_architecture};"""

with open(vhdl_filename, "w") as vhdl_file:
    vhdl_file.write(vhdl_code)

while True:
    create_testbench = input(
        f"Soll für {vhdl_filename} eine testbench erstellt werden? (y/n): ")
    if create_testbench == 'y':
        break
    if create_testbench == 'n':
        sys.exit()

# Ab hier Testbench
output_signal_names = ""
for i in range(anz_outputs):
    output_signal_names += f"s_{df.columns[i + anz_inputs]}"
    if i < anz_outputs - 1:
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

    SIGNAL s_input: STD_LOGIC_VECTOR({anz_inputs - 1} DOWNTO 0);
    SIGNAL {output_signal_names}: STD_LOGIC;
    BEGIN
        dut: {name_entity} PORT MAP("""
for i in range(anz_inputs):
    vhdl_bench += f"s_input({anz_inputs - i - 1}), "
vhdl_bench += f"""{output_signal_names});
        PROCESS
        BEGIN\n"""
for i in range(len(df)):
    vhdl_bench += f'\t\t\t\ts_input <= "'
    for j in range(anz_inputs):
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
