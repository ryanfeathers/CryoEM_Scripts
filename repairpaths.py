#!/usr/bin/env python
"""
Replace rlnImageName and rlnMicrographName paths 
Author: Ryan Feathers jrf296
Date: 12/21/2021
"""
import argparse
import starfile
import os.path
import re
import pandas as pd


parser = argparse.ArgumentParser()
parser.add_argument('--i', type=str, required=True, help='input particle star file')
parser.add_argument('--p', type=str, required=False, help='input star file with new paths')
parser.add_argument('--o', type=str, required=True, help='output file name')   
parser.add_argument('--nouid', nargs='?', const=1, type=int, help = 'removeuid')              
args = parser.parse_args()


od = (starfile.read(args.i))
df = od['particles']
d = {}


if args.nouid == 1:
	print("\nRemoving UIDs")
	pat = re.compile("[0-9]{21}_")
	df['rlnMicrographName'] = df['rlnMicrographName'].str.replace(pat, "", regex=True)
	df['rlnImageName'] = df['rlnImageName'].str.replace(pat, "", regex=True)

elif args.p is not None:

	print("Replacing paths of "+str(args.i)+" with paths from "+str(args.p))

	pdf = (starfile.read(args.p))['particles']

	for index, row in pdf.iterrows():
		c = list(zip((format(row['rlnCoordinateX'], '.5f'),format(row['rlnCoordinateY'], '.5f'), row['rlnImageName'],row['rlnMicrographName'])))
		d[str(c[0:2])] = c[2:]

	for index, row in df.iterrows():

		n = list(zip((format(row['rlnCoordinateX'], '.5f'),format(row['rlnCoordinateY'], '.5f'))))
		np = d[str(n)] #sets np to a list of rlnImageName and rlnMicrographName
		rip = str(np[0])
		rmn = str(np[1])
		df.at[index, 'rlnImageName'] = rip.strip('(),\'')
		df.at[index, 'rlnMicrographName'] = rmn.strip('(),\'')

od['particles'] = df
print("Writing new starfile\n")
starfile.write(od, args.o, overwrite=True) #Starfile update force_loop is default
	


