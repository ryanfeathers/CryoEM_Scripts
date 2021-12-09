#!/usr/bin/env python
"""
Replace rlnImageName and rlnMicrographName paths 
Author: Ryan Feathers jrf296
Date: 12/09/2021
"""
import argparse
import starfile
import os.path


parser = argparse.ArgumentParser()
parser.add_argument('--i', type=str, required=True, help='input particle star file')
parser.add_argument('--p', type=str, required=True, help='input star file with new paths')
parser.add_argument('--o', type=str, required=True, help='output file name')                 
args = parser.parse_args()


optics = (starfile.read(args.i))['optics']
df = (starfile.read(args.i))['particles']

pdf = (starfile.read(args.p))['particles']


d = {}

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

sf = [optics, df]
starfile.write(sf, args.o)
	
