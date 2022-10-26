#!/usr/bin/env python3
"""
Search and replace 
Author: Ryan Feathers jrf296
Date: 10/26/2022

Search and replace or delete strings and write out filename_mod.txt
"""


import os

#prompt user for file name
file_name = input("Enter a file name: ")
#get file extension
file_extension = file_name.split('.')[-1]
#get file name without extension
file_name_no_extension = file_name.split('.')[0]
#create output file name
output_file_name = file_name_no_extension + '_mod.' + file_extension

#check if file exists
if os.path.isfile(file_name):
    #prompt user for search string
    search_string = input("Enter a string to search for: ")
    #prompt user for replace string
    replace_string = input("Enter a string to replace with or leave blank to delete: ")
    #if replace string is blank
    if replace_string == '':
        #prompt user to specify if search term should be deleted or if the entire line should be deleted
        delete_string = input("Delete search term or entire line? (s/l): ")
        while not delete_string:
            delete_string = input("Delete search term or entire line? (s/l): ")
    else: delete_string = False


    #set found flag to false
    found = False
    #open file for reading
    with open(file_name, 'r') as f:
        #read file into a list
        lines = f.readlines()

    #open file for writing
    with open(output_file_name, 'w') as f:
        #loop through list
        for line in lines:
            #if search string is in line
            if search_string in line:
                #set found flag to true
                found = True
                if delete_string is False:
                    line = line.replace(search_string, replace_string)
                #if search term should be deleted
                elif delete_string == 's':
                    #replace search string with nothing
                    line = line.replace(search_string, '')
                #if entire line should be deleted
                elif delete_string == 'l':
                    #skip line
                    continue
                #if user input is invalid
                else:
                    print("Invalid input")
            #write line to file
            f.write(line)
    #if search string was not found
    if not found:
        #print message
        print("Search string not found")
else:
    print("File does not exist")