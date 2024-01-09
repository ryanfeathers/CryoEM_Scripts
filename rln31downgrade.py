#!/usr/bin/env python3
"""
Script to downgrade relion31 format for M
Author: Ryan Feathers rf2366
Date: 01/08/2024
"""
import os
import starfile
import argparse
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument('--i', type=str, required=True, help='input relion 3.1 subtomo star file')           
args = parser.parse_args()

df = starfile.read(args.i)

#check if df is a dictionary
def is_dict(star):
    if star != type(dict):
        print(str(star)+'does not have both data_optics and data_particles tables')
        return False
    else:
        return True

angpix = df['optics']['rlnImagePixelSize'].iloc[0]

#Copy pixel size, Cs, and voltage to particle table
def optics2particles(df):
    specified_columns = ['rlnImagePixelSize', 'rlnSphericalAberration', 'rlnVoltage']

    optics = df['optics']
    particles = df['particles']

    for column in specified_columns:
        if column in optics.columns:
            # Get the value from the optics dataframe
            value = optics[column].iloc[0]
            
            # Assign this value to a new column in the particles dataframe
            particles[column] = value
        else:
            print(f"Column '{column}' not found in optics dataframe.")
    
    df['particles'] = particles

    return df
#Divide rlnOriginAngst by Angpix to convert to rlnOrigin and rename
def divide_columns_by_angpix_and_rename(df, angpix):
    columns_to_process = {
        'rlnOriginXAngst': 'rlnOriginX',
        'rlnOriginYAngst': 'rlnOriginY',
        'rlnOriginZAngst': 'rlnOriginZ'
    }

    particles = df['particles']

    for old_column, new_column in columns_to_process.items():
        if old_column in particles.columns:
            # Divide the column values by angpix and rename the column
            particles[new_column] = particles[old_column] / angpix
            particles.drop(columns=[old_column], inplace=True)
        else:
            print(f"Column '{old_column}' not found in particles dataframe.")
    
    df['particles'] = particles

    return df

combined_renamed_origins = divide_columns_by_angpix_and_rename(optics2particles(df), angpix)
filename = str(args.i)
base, ext = os.path.splitext(filename)
new_filename = f"{base}_downgraded{ext}"
starfile.write(combined_renamed_origins['particles'], new_filename )
