
#!/usr/bin/env python3
"""
A gui for editing .star files - work in progress
Author: Ryan Feathers jrf296
Date: 12/08/2022
"""

import tkinter as tk
from tkinter import filedialog
import re
import sys

# Create the main window
root = tk.Tk()
root.title("star file editor")

# Create a function to open the file browser and select a .star file
def open_file():
    # Use the filedialog module to open the file browser
    filepath = filedialog.askopenfilename(title="Select a .star file", filetypes=(("star files","*.star"),("all files","*.*")))
    
    # If a file was selected, open it and load its contents into memory
    if filepath:
        with open(filepath, "r") as f:
            # Read the contents of the .star file and store it in a variable
            global star_file_contents
            star_file_contents = f.read()
            
            # Perform operations on the .star file here, if desired
            
            # Clear the text box
            display_textbox.delete("1.0", tk.END)
            
            # Insert the selected lines into the text box
            display_textbox.insert("1.0", star_file_contents)

# Create a function to save the .star file
def save_file():
    # Use the filedialog module to open the save file dialog
    filepath = filedialog.asksaveasfilename(title="Save .star file", defaultextension=".star", filetypes=(("star files","*.star"),("all files","*.*")))
    
    # If a filepath was provided, save the .star file to that location
    if filepath:
        with open(filepath, "w") as f:
            # Write the contents of the .star file to the specified filepath
            f.write(star_file_contents)

# Create a function to remove the UID from the .star file
def remove_uid():
    # Define pattern
    pattern = re.compile(r'\d{16}')
    global star_file_contents
    result = pattern.sub('',star_file_contents)
    star_file_contents = result
    # Update the text box with the updated .star file contents
    display_textbox.delete("1.0", tk.END)
    display_textbox.insert("1.0", star_file_contents)

def search_and_replace():
    # Get the search string and replace string from the text boxes
    search_string = search_entry.get()
    replace_string = replace_entry.get()
    selected_table = selected_table_var.get()

    if not search_string or not replace_string:
        print("Please provide both the search string and the replace string.", file=sys.stderr)
        return

    global star_file_contents

    # Split the file contents into lines
    lines = star_file_contents.split('\n')

    # Initialize the loop index and data_section
    loop_idx = -1
    data_section = ""

    # Initialize a flag to check if we are in the selected table
    in_selected_table = False

    # Iterate over lines to find the selected table and replace the search string
    for i, line in enumerate(lines):
        if line.startswith("data_"):
            data_section = line.split("_")[-1].strip()
            in_selected_table = (selected_table == data_section)
        elif line.startswith("loop_") and in_selected_table:
            loop_idx = i
        elif loop_idx != -1 and in_selected_table and line.strip() and not line.startswith("_"):
            lines[i] = line.replace(search_string, replace_string)
        elif not in_selected_table and loop_idx != -1:
            break

    # Update the star file contents
    star_file_contents = "\n".join(lines)

    # Update the text box with the updated .star file contents
    display_textbox.delete("1.0", tk.END)
    display_textbox.insert("1.0", star_file_contents)


def update_column_value():
    column_name = column_name_entry.get()
    new_value = new_value_entry.get()
    selected_table = selected_table_var.get()

    if not column_name or not new_value:
        print("Please provide both the column name and the new value.", file=sys.stderr)
        return

    global star_file_contents

    # Split the file contents into lines
    lines = star_file_contents.split('\n')

    # Initialize loop index and column index
    loop_idx = -1
    column_index = -1
    data_section = ""

    # Initialize a flag to check if the table has multiple lines
    multiple_lines = False

    # Iterate over lines to find the column index
    for i, line in enumerate(lines):
        if line.startswith("data_"):
            data_section = line.split("_")[-1].strip()
        elif line.startswith("loop_"):
            loop_idx = i
        elif line.startswith("_" + column_name + " #") and (selected_table == data_section):
            column_index = int(line.split("#")[-1].strip()) - 1
        elif loop_idx != -1 and column_index != -1 and line.strip() and not line.startswith("_"):
            tokens = line.split()
            tokens[column_index] = new_value
            lines[i] = " ".join(tokens)

            # Set the multiple_lines flag to True
            multiple_lines = True
        elif multiple_lines and loop_idx != -1 and column_index != -1 and not line.strip():
            break

    # Update the star file contents
    star_file_contents = "\n".join(lines)

    # Update the text box with the updated .star file contents
    display_textbox.delete("1.0", tk.END)
    display_textbox.insert("1.0", star_file_contents)

# Create a StringVar for the selected table
selected_table_var = tk.StringVar(root)
selected_table_var.set("optics")  # Set the default value

# Create a drop-down menu to select the table
table_options = ["optics", "particles"]
table_menu = tk.OptionMenu(root, selected_table_var, *table_options)
table_menu.pack()

# Create a frame for search and replace
search_replace_frame = tk.Frame(root)
search_replace_frame.pack(pady=10)

# Create search label and entry
search_label = tk.Label(search_replace_frame, text="Search:")
search_label.grid(row=0, column=0, padx=(0, 10))
search_entry = tk.Entry(search_replace_frame)
search_entry.grid(row=0, column=1, padx=(0, 10))

# Create replace label and entry
replace_label = tk.Label(search_replace_frame, text="Replace:")
replace_label.grid(row=1, column=0, padx=(0, 10))
replace_entry = tk.Entry(search_replace_frame)
replace_entry.grid(row=1, column=1, padx=(0, 10))

# Create a frame for column name and new value
update_frame = tk.Frame(root)
update_frame.pack(pady=10)

# Create column name label and entry
column_name_label = tk.Label(update_frame, text="Column Name:")
column_name_label.grid(row=0, column=0, padx=(0, 10))
column_name_entry = tk.Entry(update_frame)
column_name_entry.grid(row=0, column=1, padx=(0, 10))

# Create new value label and entry
new_value_label = tk.Label(update_frame, text="New Value:")
new_value_label.grid(row=1, column=0, padx=(0, 10))
new_value_entry = tk.Entry(update_frame)
new_value_entry.grid(row=1, column=1, padx=(0, 10))

# Create a button to update column value
update_column_value_button = tk.Button(update_frame, text="Update Column Value", command=update_column_value)
update_column_value_button.grid(row=2, columnspan=2, pady=10)

# Create a frame for buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

# Create a button to open the file browser and load the .star file
open_file_button = tk.Button(button_frame, text="Open .star file", command=open_file)
open_file_button.grid(row=0, column=0, padx=(0, 10))

# Create a button to remove the UID from the .star file
remove_uid_button = tk.Button(button_frame, text="Remove UID", command=remove_uid)
remove_uid_button.grid(row=0, column=1, padx=(0, 10))

# Create a button to search and replace
search_and_replace_button = tk.Button(button_frame, text="Search and Replace", command=search_and_replace)
search_and_replace_button.grid(row=0, column=2, padx=(0, 10))

# Create a button to save the .star file
save_file_button = tk.Button(button_frame, text="Save .star file", command=save_file)
save_file_button.grid(row=0, column=3, padx=(0, 10))

display_textbox = tk.Text(root)
display_textbox.pack(side="top", fill="both", expand=True, padx=0, pady=0)

# Start the main event loop
root.mainloop()
