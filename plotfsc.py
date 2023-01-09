#!/usr/bin/env python3
"""
Plot FSC
Author: Ryan Feathers jrf296
Date: 01/09/2023
Generate an FSC plot in EPS format from a relion postprocess XML file
"""

import argparse
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET

# Set up the argument parser
parser = argparse.ArgumentParser()
parser.add_argument('--i', help='XML file containing the data')
parser.add_argument('--o', help='Output file for the plot')
args = parser.parse_args()

# Parse the XML file and extract the values
root = ET.parse(args.i).getroot()
resolution = []
correlation = []
for coordinate in root.findall('coordinate'):
    resolution.append(float(coordinate.find('x').text))
    correlation.append(float(coordinate.find('y').text))

# Generate the FSC plot
fig, ax = plt.subplots()
ax.plot(resolution, correlation)

# Add the horizontal dashed lines
ax.axhline(y=0.143, linestyle='--', color='green')
ax.axhline(y=0.5, linestyle='--', color='red')

# Set the axis labels
ax.set_xlabel('Resolution (1/Å)')
ax.set_ylabel('Correlation Coefficient')
ax.set_ylim(-0.1, 1.1)

# Save the plot in EPS format
fig.savefig(args.o, format='eps')
