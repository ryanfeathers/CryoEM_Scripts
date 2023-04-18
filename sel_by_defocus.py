#!/usr/bin/env python
"""
Replace rlnImageName and rlnMicrographName paths 
Author: Ryan Feathers jrf296
Date: 12/09/2021
WORK IN PROGRESS
"""
import argparse
import starfile
import pandas as pd
from tqdm import tqdm



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--i', type=str, required=True, help='input particle star file')
    parser.add_argument('--p', type=str, required=True, help='input star file with selected particles')
    parser.add_argument('--o', type=str, required=True, help='output file name')
    parser.add_argument('--dp', type=int, default=2, help='number of decimal places to consider when comparing defocus values')
    args = parser.parse_args()

    original = (starfile.read(args.i))['particles']
    sel = (starfile.read(args.p))['particles']

    # Create a set of tuples for the rlnDefocusU and rlnDefocusV values in the sel dataframe
    sel_tuples = set(tuple(map(lambda x: round(x, args.dp), row[['rlnDefocusU', 'rlnDefocusV']])) for _, row in sel.iterrows())
    sel_tuples2 = set(tuple(map(lambda x: round(x, args.dp), row[['rlnDefocusV', 'rlnDefocusU']])) for _, row in sel.iterrows())

    # Create a list of rows to keep
    rows_to_keep = []
    for _, row in tqdm(original.iterrows(), total=len(original), desc='Matching particles'):
        tup = tuple(map(lambda x: round(x, args.dp), row[['rlnDefocusU', 'rlnDefocusV']]))
        if tup in sel_tuples or tup in sel_tuples2:
            rows_to_keep.append(row)

    # Check if no particles selected
    if rows_to_keep:
    	print(str(len(rows_to_keep))+' particles selected')

    	
    else:
    	print('No matches found')
    	quit()	
    selected_rows = pd.concat(rows_to_keep, axis=1)
    selected_df = selected_rows.transpose()

    # Create a new dataframe with only the selected rows
    #selected_df = original.loc[rows_to_keep]

    # Write the selected dataframe to the output file
    starfile.write(selected_df, args.o, overwrite=True)


if __name__ == '__main__':
    main()
