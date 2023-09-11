
#!/usr/bin/env python3
"""
A gui for editing .star files - experimental
Author: Ryan Feathers jrf296
Date: 9/5/2023
"""

import tkinter as tk
from tkinter import filedialog
import re
import sys
import pandas as pd
import os

# Create the main window
root = tk.Tk()
root.title("star file editor")

# Create a function to open the file browser and select a .star file
def open_file():
    # Use the filedialog module to open the file browser
    filepath = filedialog.askopenfilename(initialdir=os.getcwd(),title="Select a .star file", filetypes=(("star files", "*.star"), ("all files", "*.*")))
    if not filepath:  # If no file is selected, return
        return
    with open(filepath, "r") as f:
        # Read the contents of the .star file and store it in a variable
        global star_file_contents
        star_file_contents = f.read()
    unbind_modified_event()
    # Clear the text box and insert new contents
    display_textbox.config(state=tk.NORMAL)  # Temporarily enable for editing
    display_textbox.delete("1.0", tk.END)
    display_textbox.insert("1.0", star_file_contents)
    display_textbox.edit_modified(False)
    # Reset the edit mode based on the checkbox
    toggle_edit_mode()
    bind_modified_event()
    global manual_edits_made
    manual_edits_made=False

# Create a function to save the .star file
def save_file():
    global star_file_contents
    # Update star_file_contents from the textbox content if manual edits were made
    if manual_edits_made:
        star_file_contents = display_textbox.get("1.0", tk.END)
    # Use the filedialog module to open the save file dialog
    filepath = filedialog.asksaveasfilename(title="Save .star file", defaultextension=".star", filetypes=(("star files","*.star"),("all files","*.*")))
    # If a filepath was provided, save the .star file to that location
    if filepath:
        with open(filepath, "w") as f:
            f.write(star_file_contents)

# Create a function to remove the UID from the .star file
def remove_uid():
    def modify_contents():
        unbind_modified_event()
    # Define pattern
        pattern = re.compile(r'\d{21}'+"_")
        global star_file_contents
        result = pattern.sub('',star_file_contents)
        star_file_contents = result
        # Update the text box with the updated .star file contents
        display_textbox.delete("1.0", tk.END)
        display_textbox.insert("1.0", star_file_contents)
        display_textbox.edit_modified(False)
    modify_textbox_content(modify_contents)

def search_and_replace():
    def modify_contents():
        unbind_modified_event()
        # Get the search string and replace string from the text boxes
        search_string = search_entry.get()
        replace_string = replace_entry.get()
        selected_table = selected_table_var.get()
        if not search_string:
            print("Please provide the search string.", file=sys.stderr)
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
        bind_modified_event()
        # Update the star file contents
        star_file_contents = "\n".join(lines)
        # Update the text box with the updated .star file contents
        display_textbox.delete("1.0", tk.END)
        display_textbox.insert("1.0", star_file_contents)
        display_textbox.edit_modified(False)
    modify_textbox_content(modify_contents)
    
def update_column_value():
    def modify_contents():
        unbind_modified_event()
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
                multiple_lines = True
            elif multiple_lines and loop_idx != -1 and column_index != -1 and not line.strip():
                break
        bind_modified_event()
        # Update the star file contents
        star_file_contents = "\n".join(lines)
        # Update the text box with the updated .star file contents
        display_textbox.delete("1.0", tk.END)
        display_textbox.insert("1.0", star_file_contents)
        display_textbox.edit_modified(False)
    modify_textbox_content(modify_contents)

def toggle_edit_mode():
    global star_file_contents, in_manual_edit_mode
    if edit_mode_var.get():
        # Edit mode ON
        display_textbox.config(state=tk.NORMAL)
        in_manual_edit_mode = True
        bind_modified_event()
    else:
        # Edit mode OFF (read-only mode)
        in_manual_edit_mode = False
        display_textbox.config(state=tk.DISABLED)
        star_file_contents = display_textbox.get("1.0", tk.END)  # Update the content of the global variable
        unbind_modified_event()

def setup_textbox_tags():
    display_textbox.tag_configure("modified", background="gray")

def modify_textbox_content(callback):
    """
    Temporarily set the Text widget to NORMAL, call the provided callback to modify the contents,
    then reset the widget to its original state.
    """
    global in_manual_edit_mode
    original_state = display_textbox['state']
    in_manual_edit_mode = False  # Disable manual edit mode
    display_textbox.config(state=tk.NORMAL)
    callback()
    display_textbox.config(state=original_state)
    in_manual_edit_mode = edit_mode_var.get()  # Restore the manual edit mode status

def star_to_dataframes(lines):
    # Placeholder for data blocks
    data_blocks = {}
    current_block = None
    columns = []
    for line in lines:
        line = line.strip()
        if line.startswith("data_"):
            current_block = line
            data_blocks[current_block] = {'headers': [], 'rows': []}
        elif line.startswith("_rln"):
            data_blocks[current_block]['headers'].append(line.split()[0])
        elif current_block and line and not line.startswith("loop_") and not line.startswith("#"):
            data_blocks[current_block]['rows'].append(line.split())
    # Convert each data block to a dataframe
    dataframes = {}
    for block, content in data_blocks.items():
        dataframes[block] = pd.DataFrame(content['rows'], columns=content['headers'])
    return dataframes.get("data_optics", None), dataframes.get("data_particles", None)

def df_to_star(optics_df, particles_df):
    def dataframe_to_star_section(df, section_name):
        # Construct header
        headers = df.columns
        header_string = "\n".join([f"{header} #{idx}" for idx, header in enumerate(headers, start=1)])
        
        # Convert data rows to string
        data_rows = []
        for _, row in df.iterrows():
            data_rows.append(" ".join(map(str, row.values)))
        
        return f"data_{section_name}\n\nloop_\n{header_string}\n\n" + "\n".join(data_rows) + "\n"

    # Convert each DataFrame to its respective STAR section
    optics_star = dataframe_to_star_section(optics_df, "optics")
    particles_star = dataframe_to_star_section(particles_df, "particles")
    # Compile the full STAR file content
    star_content = f"{optics_star}\n{particles_star}\n"
    return star_content

def split_by_column():
    # Get the column name from the entry widget
    column_name = '_'+split_column_name_entry.get()
    if column_name == '_rlnGroupNumber' and regroup_var.get() == True:
        print("Please select either regroup or split by rlnGroupNumber")
        return
    if not column_name:
        print("Please provide the column name.", file=sys.stderr)
        return
    # Load the particles into a dataframe 
    lines = star_file_contents.split('\n')
    optics_df, particles_df = star_to_dataframes(lines)
    if not column_name in particles_df.columns:
        print(f"Column '{column_name}' not found in DataFrame.")
        return
    # Use the filedialog module to open a directory selection dialog
    output_folder = filedialog.askdirectory(initialdir=os.getcwd(),title="Select a folder to save split files")
    if not output_folder:
        return
    if not regroup_var.get():
        unique_values = particles_df[column_name].unique()
        for value in unique_values:
            subset_df = particles_df[particles_df[column_name] == value]
            # convert the subset_df back to .star format
            substar = df_to_star(optics_df,subset_df)
            #save the subset
            filename = f"split_{column_name}_{value}.star"
            with open(os.path.join(output_folder, filename), "w") as f:
                f.write(substar)
        print(f"Files split based on column '{column_name}' and saved to '{output_folder}'.")
    elif '_rlnGroupNumber' in particles_df.columns:
        print("rlnGroupNumber will be overwritten")
        group_counter = 1
        recombine = []    
        unique_values = particles_df[column_name].unique()
        for value in unique_values:
            # Create a copy of the subset
            subset_df = particles_df[particles_df[column_name] == value].copy()
            # Assign the current group_counter value to rlnGroupNumber using .loc
            subset_df.loc[:, '_rlnGroupNumber'] = group_counter
            if not recombine_var.get():
                substar = df_to_star(optics_df, subset_df)
                #save the subset
                filename = f"split{column_name}_{group_counter}.star"
                with open(os.path.join(output_folder, filename), "w") as f:
                    f.write(substar)
            elif recombine_var.get:
                recombine.append(subset_df)
            group_counter = group_counter + 1
        if recombine_var:
            comb_regroup = df_to_star(optics_df,pd.concat(recombine))
            filename = f"regrouped{column_name}.star"
            with open(os.path.join(output_folder, filename), "w") as f:
                f.write(comb_regroup)
    elif not '_rlnGroupNumber' in particles_df.columns:
        print('not implemented yet - _rlnGroupNumber not present, adding new column')

# Create a frame for column split
split_frame = tk.Frame(root)
split_frame.pack(pady=10)

# Create split column name label and entry
split_column_name_label = tk.Label(split_frame, text="Split Column Name:")
split_column_name_label.grid(row=0, column=0, padx=(0, 10))
split_column_name_entry = tk.Entry(split_frame)
split_column_name_entry.grid(row=0, column=1, padx=(0, 10))

# Create a button to split based on column value
split_column_button = tk.Button(split_frame, text="Split by Column Value", command=split_by_column)
split_column_button.grid(row=0, column=2, padx=(0, 10))

# Add checkbox to regroup
regroup_var = tk.BooleanVar(root, value=False) # Default: no regrouping
toggle_regroup_button = tk.Checkbutton(split_frame, text="Regroup", variable=regroup_var)
toggle_regroup_button.grid(row=0, column=3, padx=1)

# Add checkbox to recombine
recombine_var = tk.BooleanVar(root, value=False) # Default: no recombining
toggle_recombine_button = tk.Checkbutton(split_frame, text="Recombine", variable=recombine_var)
toggle_recombine_button.grid(row=0, column=4, padx=1)

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

# Create search and replace label and entry
search_label = tk.Label(search_replace_frame, text="Search:", anchor="e")
search_label.grid(row=0, column=0, padx=5, ipadx=2, ipady=2, sticky="e")
search_entry = tk.Entry(search_replace_frame)
search_entry.grid(row=0, column=1, padx=5, ipadx=2, ipady=2)
replace_label = tk.Label(search_replace_frame, text="Replace:", anchor="e")
replace_label.grid(row=1, column=0, padx=5, ipadx=2, ipady=2, sticky="e")
replace_entry = tk.Entry(search_replace_frame)
replace_entry.insert(0, "")  
replace_entry.grid(row=1, column=1, padx=5, ipadx=2, ipady=2)
#Create update column value entry and labels
column_name_label = tk.Label(search_replace_frame, text="Column Name:", anchor="e")
column_name_label.grid(row=0, column=2, padx=5, ipadx=2, ipady=2, sticky="e")
column_name_entry = tk.Entry(search_replace_frame)
column_name_entry.grid(row=0, column=3, padx=5, ipadx=2, ipady=2)
new_value_label = tk.Label(search_replace_frame, text="New Value:", anchor="e")
new_value_label.grid(row=1, column=2, padx=5, ipadx=2, ipady=2, sticky="e")
new_value_entry = tk.Entry(search_replace_frame)
new_value_entry.grid(row=1, column=3, padx=5, ipadx=2, ipady=2)
# Create buttons for search and replace and update column value
search_and_replace_button = tk.Button(search_replace_frame, text="Search and Replace", command=search_and_replace)
search_and_replace_button.grid(row=2, column=0, columnspan=2, pady=10, padx=5, sticky="ew")
update_column_value_button = tk.Button(search_replace_frame, text="Update Column Value", command=update_column_value)
update_column_value_button.grid(row=2, column=2, columnspan=2, pady=10, padx=5, sticky="ew")
# Create a frame for buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=10)
# Add checkbox to toggle edit mode
edit_mode_var = tk.BooleanVar(root, value=False) # Default: editing disabled
toggle_edit_button = tk.Checkbutton(button_frame, text="Edit Manually", variable=edit_mode_var, command=toggle_edit_mode)
toggle_edit_button.grid(row=0, column=4, padx=(0, 10))
# Create a button to open the file browser and load the .star file
open_file_button = tk.Button(button_frame, text="Open .star file", command=open_file)
open_file_button.grid(row=0, column=0, padx=(0, 10))
# Create a button to remove the UID from the .star file
remove_uid_button = tk.Button(button_frame, text="Remove UID", command=remove_uid)
remove_uid_button.grid(row=0, column=1, padx=(0, 10))
# Create a button to save the .star file
save_file_button = tk.Button(button_frame, text="Save .star file", command=save_file)
save_file_button.grid(row=0, column=3, padx=(0, 10))
# Textbox 
display_textbox = tk.Text(root, state=tk.NORMAL)
display_textbox.pack(side="top", fill="both", expand=True, padx=0, pady=0)

def unbind_modified_event():
    display_textbox.unbind("<<Modified>>")

def bind_modified_event():
    display_textbox.bind("<<Modified>>", on_text_modified)

def on_text_modified(event):
    if not in_manual_edit_mode:  # Only proceed if in manual edit mode
        return
    global manual_edits_made
    # Change background color for the line that was edited
    current_line = display_textbox.index(tk.INSERT).split('.')[0]
    # Add the tag for the modified line
    display_textbox.tag_add("modified", f"{current_line}.0", f"{current_line}.end+1c")
    display_textbox.tag_configure("modified", background="gray")
    setup_textbox_tags()
    manual_edits_made = True
    # Reset the <<Modified>> flag
    display_textbox.edit_modified(False)

# Start the main event loop
root.mainloop()
