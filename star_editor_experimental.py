
#!/usr/bin/env python3
"""
A gui for editing .star files - experimental, more features less stable
Author: Ryan Feathers jrf296
Date: 10/12/2023
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
    update_particle_count_label()

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
        search_string = search_entry.get()
        replace_string = replace_entry.get()
        selected_table = selected_table_var.get()
        sel_column = column_name_entry.get()
        wc = False
        if not search_string:
            print("Please provide the search string.", file=sys.stderr)
            return
        if "*" in search_string or "?" in search_string:
            search_string = search_string.replace("*", ".*")
            search_string = search_string.replace("?", ".?")
            wc = True
        else: wc = False
        global star_file_contents
        lines = star_file_contents.split('\n')
        
        # Convert star file contents to DataFrames
        dfs = star_to_dataframes(lines)
        
        # Fetch the DataFrame for the selected table
        df = dfs.get(f"data_{selected_table}")
        
        # Perform search and replace within the selected DataFrame
        if df is not None:
            if sel_column:
                column_name = f'_{sel_column}'
                if column_name in df.columns:
                    if wc:
                        search_pattern = re.compile(search_string)
                        df[column_name] = df[column_name].astype(str).apply(lambda x: search_pattern.sub(replace_string, x))
                    else:
                        df[column_name] = df[column_name].astype(str).str.replace(search_string, replace_string, regex=False)
            else:
                for column in df.columns:
                    if wc:
                        search_pattern = re.compile(search_string)
                        df[column] = df[column].astype(str).apply(lambda x: search_pattern.sub(replace_string, x))
                    else:
                        df[column] = df[column].astype(str).str.replace(search_string, replace_string, regex=False)
            # Update the modified DataFrame in the dictionary
            dfs[f"data_{selected_table}"] = df
        
        # Prepare the modified DataFrames for conversion back to star format
        optics_df = dfs.get("data_optics", None)
        particles_df = dfs.get("data_particles", None)
        
        # Convert the modified DataFrames back to star format
        star_content = df_to_star(optics_df, particles_df)
        star_file_contents = star_content
        
        bind_modified_event()
        display_textbox.delete("1.0", tk.END)
        display_textbox.insert("1.0", star_file_contents)
        display_textbox.edit_modified(False)
    
    modify_textbox_content(modify_contents)

def remove_particles_by_search_string():
    def modify_contents():
        unbind_modified_event()
        # Get the search string from the search_entry
        search_string = search_entry.get()
        # Split the content of the textbox into lines
        content_lines = display_textbox.get("1.0", tk.END).split('\n')
        # Assuming the particle table always starts after a line containing 'data_particles'
        in_particle_table = False
        new_content = []
        for line in content_lines:
            if 'data_particles' in line:
                in_particle_table = True
            if in_particle_table and search_string in line:
                # If search string is found in a line in the particle table, skip that line
                continue
            # Add lines to the new content
            new_content.append(line)
        bind_modified_event()
        # Join the lines and put them back in the textbox
        display_textbox.delete("1.0", tk.END)  # Clear current content
        display_textbox.insert("1.0", '\n'.join(new_content))
    modify_textbox_content(modify_contents)

def count_particles():
    global star_file_contents
    lines = star_file_contents.split('\n')
    data_particles_section = False
    rln_header_found = False
    particle_count = 0
    for line in lines:
        stripped_line = line.strip()  # Remove any leading/trailing whitespace
        if stripped_line.startswith("data_particles"):
            data_particles_section = True
            continue
        elif data_particles_section and stripped_line.startswith("_rln"):
            rln_header_found = True
            continue
        elif data_particles_section and rln_header_found and stripped_line:
            particle_count += 1
        elif stripped_line.startswith("data_"):  # If another data section begins, break out of the loop
            break
    return particle_count

def update_column_value():
    def modify_contents():
        unbind_modified_event()
        column_name = column_name_entry.get()
        new_value = new_value_entry.get()
        selected_table = selected_table_var.get()
        if not column_name or not new_value:
            print("Please provide both the column name and the new value.", file=sys.stderr)
            #return
        global star_file_contents
        # Split the file contents into lines
        lines = star_file_contents.split('\n')
        # Initialize loop index and column index
        loop_idx = -1
        column_index = -1
        data_section = ""
        # Initialize a flag to check if the table has multiple lines
        multiple_lines = False
        # Iterate over lines
        star = star_to_dataframes(lines)
        proper_column_name = "_" + column_name
        sel = 'data_'+selected_table
        if proper_column_name not in star[sel].columns:
            print("Column not present; adding column to "+selected_table)
            star[sel][proper_column_name] = pd.Series([0 for x in range(len(star[sel].index))])
            lines = star_file_contents.split('\n')
        if function_var.get():
            star = star_to_dataframes(lines)
            if selected_table == "optics":
                sel_star = star[sel]
                modified_df = user_func(sel_star, column_name, new_value)
                star_file_contents = df_to_star(modified_df, star[sel])
            else:
                sel_star = star[sel]
                modified_df = user_func(sel_star, column_name, new_value)
                star_file_contents = df_to_star(star[sel], modified_df)
        if not function_var.get():
            if "rln" in new_value:
                if not '_'+new_value in star[sel].columns:
                    print("cant find "+new_value+" to copy")
                    return
                print("copying values from "+"_"+new_value+" to "+proper_column_name)
                star[sel][proper_column_name] = star[sel]["_"+new_value]      
            else:
                star[sel][proper_column_name] = pd.Series([new_value for x in range(len(star[sel].index))])
        star_file_contents = df_to_star(star['data_optics'],star['data_particles'])
        lines = star_file_contents.split('\n')

        bind_modified_event()
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

def user_func(df, column, func):
    # Add an underscore to the column name to match the dataframe's format
    column = "_" + column
    # Ensure the column exists in the dataframe
    if column not in df.columns:
        print(f"Column '{column}' not found in dataframe columns.")
        return df
    # Attempt to convert all values in the column to float
    try:
        df[column] = df[column].astype(float)
    except ValueError:
        print(f"Column '{column}' contains values that cannot be converted to numeric.")
        return df
    # Check if the provided function is valid
    sample_value = 1
    try:
        eval(func.replace("x", str(sample_value)))
    except:
        print("The provided function is invalid.")
        return df
    # Apply the function to the dataframe column
    df[column] = df[column].apply(lambda x: eval(func.replace("x", str(x))))
    return df

def star_to_dataframes(lines):
    # Placeholder for data blocks
    data_blocks = {}
    current_block = None
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
    
    return dataframes

def df_to_star(optics_df, particles_df):
    def dataframe_to_star_section(df, section_name):
        # Construct header
        headers = df.columns
        header_string = "\n".join([f"{header} #{idx}" for idx, header in enumerate(headers, start=1)])
        
        # Convert data rows to string
        data_rows = []
        for _, row in df.iterrows():
            data_rows.append(" ".join(map(str, row.values)))
        
        return f"data_{section_name}\n\nloop_\n{header_string}\n" + "\n".join(data_rows) + "\n"

    # Convert each DataFrame to its respective STAR section if it's not None
    optics_star = dataframe_to_star_section(optics_df, "optics") if optics_df is not None else ""
    particles_star = dataframe_to_star_section(particles_df, "particles") if particles_df is not None else ""
    
    # Compile the full STAR file content
    star_content = f"{optics_star}\n{particles_star}\n"
    return star_content.strip()  # strip() to remove potential trailing newlines

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

def update_particle_count_label():
    content = display_textbox.get("1.0", tk.END)
    # Check if "data_particles" exists in the content
    if "data_particles" not in content:
        particle_count_label.config(text="Particle Count: Not Found")
        return
    try:
        particle_data = content.split("data_particles")[1]
        lines = particle_data.strip().splitlines()
        
        # Identify the line where the data starts by finding the last occurrence of the "#"
        # Then skip the blank lines to start counting from actual data
        data_start_index = next(i for i, line in reversed(list(enumerate(lines))) if "#" in line) + 1
        while not lines[data_start_index].strip():
            data_start_index += 1
        
        particle_count = len(lines) - data_start_index
        particle_count_label.config(text=f"Particle Count: {particle_count}")
    except Exception as e:
        print(f"Error updating particle count: {e}")
        particle_count_label.config(text="Particle Count: Error")


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
function_var = tk.BooleanVar(root, value=False) # Default: unchecked
function_checkbox = tk.Checkbutton(search_replace_frame, text="Function", variable=function_var)
function_checkbox.grid(row=1, column=4, padx=5)
# Create buttons for search and replace and update column value
search_and_replace_button = tk.Button(search_replace_frame, text="Search and Replace", command=search_and_replace)
search_and_replace_button.grid(row=2, column=0, columnspan=2, pady=10, padx=5, sticky="ew")
update_column_value_button = tk.Button(search_replace_frame, text="Update Column Value", command=update_column_value)
update_column_value_button.grid(row=2, column=2, columnspan=2, pady=10, padx=5, sticky="ew")
# Create a frame for buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=10)
# Create the "Remove Particles" button and place it in the appropriate frame
remove_particles_button = tk.Button(button_frame, text="Remove Particles", command=remove_particles_by_search_string)
remove_particles_button.grid(row=0, column=2, padx=(0, 10))  # Adjust column and padding as needed
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
#Particle counter
particle_count_label = tk.Label(root, text="Particle Count: 0")
particle_count_label.pack(pady=10)
# Textbox 
display_textbox = tk.Text(root, state=tk.NORMAL, wrap=tk.NONE)
display_textbox.pack(side="top", fill="both", expand=True, padx=0, pady=0)
# Create a horizontal scrollbar and link it to the Text widget
xscrollbar = tk.Scrollbar(root, orient=tk.HORIZONTAL, command=display_textbox.xview)
xscrollbar.pack(side=tk.BOTTOM, fill=tk.X)
display_textbox['xscrollcommand'] = xscrollbar.set

def unbind_modified_event():
    display_textbox.unbind("<<Modified>>")
    update_particle_count_label()

def bind_modified_event():
    display_textbox.bind("<<Modified>>", on_text_modified)

def on_text_modified(event):
    if not in_manual_edit_mode:  # Only proceed if in manual edit mode
        update_particle_count_label()
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
