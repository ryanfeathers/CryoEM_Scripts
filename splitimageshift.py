#!/usr/bin/env python3
"""
split imageshift groups
Author: Ryan Feathers jrf296
Date: 12/29/2021
"""

import argparse
import starfile

parser = argparse.ArgumentParser()
parser.add_argument('--i', type=str, required=True, help='input particle star file')
args = parser.parse_args()

#change the selection criteria here
imsh = ["X+0Y-1-0","X+1Y+1-0","X+1Y-1-0","X+0Y+1-0","X+1Y+0-0","X+0Y+0-0" \
,"X-1Y+0-0","X-1Y+1-0","X-1Y-1-0"]

try:
	f = open(args.i)

except IOError:
	print("File not accessible")

finally:
	f.close()

od = (starfile.read(args.i))
df = od['particles']

for i in imsh:
	contain_values = df[df['rlnMicrographName'].str.contains(i,regex=False)]
	od['particles'] = df
	print("Writing new starfile\n"+i+".star")
	starfile.write(od, "group_"+i+".star", overwrite=True)
