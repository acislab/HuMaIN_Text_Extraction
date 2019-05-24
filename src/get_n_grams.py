#!/usr/bin/env python3
##########################################################################################
# Developer: Icaro Alzuru         Project: HuMaIN (http://humain.acis.ufl.edu)
# Description: 
#   Generates the n-gram of words for the .txt files in a directory. 
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

import argparse, os, sys
import pandas as pd
import numpy as np

def get_ngrams( s, n):
	""" Returns a list with the possible concatenation of words with a size of n
	"""
	min_n = 2*n - 1
	s_lw = s.lower()
	tokens_list = [token for token in s_lw.split(" ") if token.strip() != ""]
	ngrams = zip(*[tokens_list[i:] for i in range(n)])
	ngrams = [ gram for gram in ngrams if len(''.join(gram))>min_n ]

	return ngrams

#----------------------------------------------------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
	""" Generates the n-gram of words for the .txt files in a directory. 
	"""
	parser = argparse.ArgumentParser("Generates the n-gram of words for the .txt files in a directory. ")
	parser.add_argument('-d', '--dir', action="store", required=True, help="Directory where the text files are located.")
	parser.add_argument('-n', '--n', action="store", required=True, help="Number of words in the grams.")
	parser.add_argument('-o', '--output', action="store", required=True, help="Path and filename of the tsv file which will store the n-grams.")
	args = parser.parse_args()

	# Arguments Validations
	if ( not os.path.isdir( args.dir ) ):
		print('Error: The directory with the text files was not found.\n')
		parser.print_help()
		sys.exit(1)

	n = 0
	try:
		n = int(args.n)
		if (n<1) or (n>5):
			print('Error: n must be an integer value between 1 and 5.\n')
			parser.print_help()
			sys.exit(2)
	except:
		print('Error: n must be an integer value between 1 and 5.\n')
		parser.print_help()
		sys.exit(2)

	# Create the lists of files to process
	files_list = list()
	for root, dirs, filenames in os.walk( args.dir ):
		files_list = list(f for f in filenames if f.endswith('.txt'))

	ngrams_dict = {}
	for filename in files_list:
		path_filename = args.dir + "/" + filename

		with open( path_filename ) as f: 
			lines = [line.rstrip('\n') for line in f]
			for line in lines:
				ngrams_list = get_ngrams( line, n )
				for ngram in ngrams_list:
					try:
						n_ngram = ngrams_dict[ ngram ]
						ngrams_dict[ ngram ] = n_ngram + 1
					except KeyError:
						ngrams_dict[ ngram ] = 1

	# 
	with open( args.output, "w+" ) as f: 
		for ngram in list( ngrams_dict.keys() ):
			n_ngram = ngrams_dict[ ngram ]
			s = " ".join(ngram)
			f.write( s+ "\t" + str(n_ngram) + "\n")
