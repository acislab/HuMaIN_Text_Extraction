#!/usr/bin/env python
##########################################################################################
# Developer: Icaro Alzuru         Project: HuMaIN (http://humain.acis.ufl.edu)
# Description: 
#   Compares the text files of two directories using the Damerau-Levenshtein similarity.
#
##########################################################################################
# Copyright 2019    Advanced Computing and Information Systems (ACIS) Lab - UF
#                   (https://www.acis.ufl.edu/)
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
# http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
##########################################################################################

import sys, os, argparse
import pandas as pd

from pyxdameraulevenshtein import normalized_damerau_levenshtein_distance

# ----------------------------------------------------------------------------------
def compare_DL( filename1, filename2 ):
	# Sanity check
	if not os.path.isfile(filename1):
		print('\nERROR: First source file ' + filename1 + ' was not found.\n')
		return(-3)
	if not os.path.isfile(filename2):
		print('\nERROR: Second source file ' + filename2 + ' was not found.\n')
		return(-4)	

	# Read the content of the first file
	text1 = ""
	f1 = None
	with open( filename1 ) as f1:
		lines1 = [line.rstrip('\n') for line in f1]
	for line in lines1:
		text1 += line + ' '
	text1 = text1[:-1]

	# Read the content of the second file
	text2 = ""
	f2 = None
	with open( filename2 ) as f2:
		lines2 = [line.rstrip('\n') for line in f2]
	for line in lines2:
		text2 += line + ' '
	text2 = text2[:-1]
	
	sim = 1.0 - normalized_damerau_levenshtein_distance( text1, text2 )
	return( sim )

# Use: python3 ../ALOT/fulltext_similarity_DL_dir.py -d1 ./biocolls/digi_13297227/fulltext -d2 ./fulltext/digi_13297227_google -o DL_comparison/digi_13297227_google.csv
# ----------------------------------------------------------------------------------
if __name__ == '__main__':
	""" Compares the text files of two directories using the Damerau-Levenshtein similarity.
	"""
	# Read arguments
	parser = argparse.ArgumentParser("Compares the text files of two directories using the Damerau-Levenshtein similarity.")
	parser.add_argument('-d1','--dir1',action="store", required=True, help="First directory.")
	parser.add_argument('-d2','--dir2',action="store", required=True, help="Second directory.")
	parser.add_argument('-o','--output',action="store", required=True, help="Path + filename of the csv file which will store the output.")
	args = parser.parse_args()

	# Sanity check
	if not os.path.isdir( args.dir1 ):
		print('\nERROR: First directory ' + args.dir1 + ' was not found.\n')
		parser.print_help()
		sys.exit(-1)
	if not os.path.isdir( args.dir2 ):
		print('\nERROR: Second directory ' + args.dir2 + ' was not found.\n')
		parser.print_help()
		sys.exit(-2)
		
	# Create the lists of files to process
	files_list = list()
	for root, dirs, filenames in os.walk( args.dir1 ):
		files_list = list(f for f in filenames if f.endswith('.txt'))

	# Process each text file
	with open( args.output, 'w+') as f_out:
		for filename in files_list:
			path_filename_1 = args.dir1 + '/' + filename
			path_filename_2 = args.dir2 + '/' + filename
			sim = compare_DL( path_filename_1, path_filename_2 )
			if sim >= 0.0:
				f_out.write(filename + ',' + str(sim) + '\n')
