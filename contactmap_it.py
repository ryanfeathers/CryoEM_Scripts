#!/usr/bin/env python
"""
Pdb contact map 
Author: Ryan Feathers jrf296
Date: 08/25/2022
"""
import argparse
import os.path
import pandas as pd
import csv
import Bio.PDB
import numpy
from Bio.PDB import PDBParser, PDBIO
def calc_residue_dist(residue_one, residue_two) :
    """Returns the C-alpha distance between two residues"""
    diff_vector  = residue_one["CA"].coord - residue_two["CA"].coord
    return numpy.sqrt(numpy.sum(diff_vector * diff_vector))

def calc_dist_matrix(chain_one, chain_two) :
    """Returns a matrix of C-alpha distances between two chains"""
    answer = numpy.zeros((len(chain_one), len(chain_two)), float)
    for row, residue_one in enumerate(chain_one) :
        for col, residue_two in enumerate(chain_two) :
            answer[row, col] = calc_residue_dist(residue_one, residue_two)
    return answer

parser = argparse.ArgumentParser()
#parser.add_argument('--i', type=str, required=True, help='input file')
parser.add_argument('--o', type=str, required=False, help='output file name')                 
args = parser.parse_args()

#makes a list of files for iterative use
path ='./'
files = os.listdir(path)
pdb_l = []
scores = []

for i in files:
	if 'pdb' in str(i):
		pdb_l.append(i) 
for i in pdb_l:
	pdb_code = i
	pdb_filename = i


	chain_ids = []
	pdb = PDBParser().get_structure(pdb_code, pdb_filename)

	for chain in pdb.get_chains():
		chain_ids.append(chain.get_id())
	
	if len(chain_ids) > 2:
		print("There are more than 2 chains in the model")	



	structure = Bio.PDB.PDBParser().get_structure(pdb_code, pdb_filename)
	model = structure[0]

	dist_matrix = calc_dist_matrix(model[str(chain_ids[0])], model[str(chain_ids[1])])
	contact_map = dist_matrix < 12

	df = pd.DataFrame(dist_matrix)

	contacts = []
	cutoff = 12

	for i in range(df.shape[0]): #iterate over rows
	    for j in range(df.shape[1]): #iterate over columns
	        value = df.at[i, j] #get cell value
	        if value <= cutoff:
	        	contacts.append([i+1,j+1,value])

	#this is not perfect, reversing drop dups from B to A gives different results
	scores =[]
	contacts_matrix = pd.DataFrame(contacts)
	if contacts_matrix.empty:
		scores.append([str(pdb_filename),' '+ 'contacts = '+'0'])
		print(str(pdb_filename),' '+ 'contacts = '+'0')
	else:
		contacts_matrix.columns = ['ChainA','ChainB','Distance']
		contacts_matrix = contacts_matrix.sort_values('Distance',ignore_index=True)
		contacts_matrix = contacts_matrix.drop_duplicates('ChainA', keep='first', ignore_index=True)
		contacts_matrix = contacts_matrix.drop_duplicates('ChainB', keep='first', ignore_index=True)
		scores.append([str(pdb_filename),' '+ 'contacts = '+str(len(contacts_matrix.index))])
		print(str(pdb_filename),' '+ 'contacts = '+str(len(contacts_matrix.index)))

#still need to scores.sort based on len(scores[1])

 
	# opening the csv file in 'w+' mode
file = open('scores.csv', 'w+', newline ='')
 
	# writing the data into the file
with file:   
	write = csv.writer(file)
	write.writerows(scores)





# for i, row in contacts_matrixA.iterrows():
# 	pair = [row['ChainA'],row['ChainB']]
# 	dis = row['Distance']
# 	for i, row in contacts_matrixB.iterrows():
# 		pair2 = [row['ChainA'],row['ChainB']]
# 		if pair == pair2 and row['Distance'] < dis:
# 			dis = row['Distance']
# 	#row['Distance'] = dis		


#		if contacts_matrixB['ChainA'] == contacts_matrixA['ChainA']
#			if contacts_matrixA[Distance] > contacts_matrixB['Distance']:
#				contacts_matrixA['Distance'] = contacts_matrixB['Distance']




#contacts_matrix = contacts_matrix.groupby(['ChainA','ChainB'])['Distance'].min().reset_index()

#print(contacts_matrixB)
#print(contacts_matrixA)
#with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
#	print(contacts_matrix)



#print(len(contacts_matrix[0].value_counts()))
#print(len(contacts_matrix[1].value_counts()))
#print("There are "+str(len(contacts))+" residues <= "+str(cutoff)+" Angstroms")

#print(contacts)
