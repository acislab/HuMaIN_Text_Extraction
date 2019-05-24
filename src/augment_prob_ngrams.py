#!/usr/bin/env python3
##########################################################################################
# Developer: Icaro Alzuru         Project: HuMaIN (http://humain.acis.ufl.edu)
# Description: 
#   Using the n-gram files, augment the confidence of the probability files.
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

path_filename_2g = "/home/user/digi_13297227/H-MaTE/2_gram.tsv"
path_filename_1g = "/home/user/digi_13297227/H-MaTE/1_gram.tsv"
#
# python3 ../ALOT/augment_prob_ngrams.py -sd ./gr_google_fixed -dd gr_google_augmented > report_google_augmented.txt
# 
# Run first the fix of the google directory:
#       python3 fix_prob_txt_dir.py -sd ./gr_lines_google -dd gr_google_fixed > report_google_fixed.txt
#----------------------------------------------------------------------------------------------------------------------------------------------------------------
def get_ngrams( s, n):
	""" Returns a list with the possible concatenation of words with a size of n
	"""
	tokens_list = [token for token in s.split(" ") if token.strip() != ""]
	ngrams = zip(*[tokens_list[i:] for i in range(n)])
	return ngrams
#----------------------------------------------------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
	""" Using the n-gram files, augment the confidence of the probability files. 
	"""
	parser = argparse.ArgumentParser("Using the n-gram files, augment the confidence of the probability files.")
	parser.add_argument('-sd', '--srcdir', action="store", required=True, help="Directory where the probability files are located.")
	parser.add_argument('-dd', '--dstdir', action="store", required=True, help="Directory where the new augmented probability files will be saved.")
	args = parser.parse_args()

	# Arguments Validations
	if ( not os.path.isdir( args.srcdir ) ):
		print('Error: The directory with the text and prob files was not found.\n')
		parser.print_help()
		sys.exit(-1)

	if not os.path.exists( args.dstdir ):
		try:
			os.makedirs( args.dstdir )  
		except:
			print('Error: The destination directory was not found and could not be created.\n')
			parser.print_help()
			sys.exit(-2)

	# Load the 2-gram, and 1-gram files in memory
	df_2g = None
	df_1g = None
	try: 
		df_2g = pd.read_csv( path_filename_2g, sep='\t', header=None, names=['gram', 'n'], engine="python", error_bad_lines=False)
		df_1g = pd.read_csv( path_filename_1g, sep='\t', header=None, names=['gram', 'n'], engine="python", error_bad_lines=False)
	except Exception as e:
		print('Error: There was an error loading one of the n-gram files\n' + str(e) + "\n")
		sys.exit(-3)

	# Delete those gram which repeat less than 2 times
	df_2g = df_2g[df_2g.n > 1]
	df_1g = df_1g[df_1g.n > 2]

	# Create dictionaries for each n-gram to accelerate the lookup
	dict_2g = {}
	for index, row in df_2g.iterrows():
		dict_2g[ row['gram'] ] = int(row['n'])

	dict_1g = {}
	for index, row in df_1g.iterrows():
		dict_1g[ row['gram'] ] = int(row['n'])

	# Create the lists of files to process
	files_list = list()
	for root, dirs, filenames in os.walk( args.srcdir ):
		files_list = list(f for f in filenames if f.endswith('.txt'))

	# Process each text file
	j = 0
	for filename in files_list:
		basename = filename[:-4]
		prob_path_filename = args.srcdir + "/" + basename + ".prob"

		# Load the probability file in two lists
		symbols_list = []
		prob_list = []
		f_prob = None
		with open( prob_path_filename ) as f_prob: 
			for line in f_prob:
				try:
					symbol, prob = line.rstrip('\n').split("\t")

					symbols_list.append( symbol )
					prob_list.append( float(prob) )
				except:
					break

		size_symbols_list = len(symbols_list)
		symbols_string = ''.join( symbols_list )

		# Validate the load of the symbols
		if size_symbols_list == 0:
			print("Warning: " + prob_path_filename + " is an empty file.\n")
			continue

		b_changed = False
		########################### 2-grams #########################
		# Get the possible 2-grams (case-sensitive)
		ngrams_list = get_ngrams( symbols_string, 2 )
		# Process each gram
		for ngram in ngrams_list:
			try:
				s = " ".join(ngram)
				s_lwr = s.lower()
				n_ngram = dict_2g[ s_lwr ]
				# It was found: the 2-gram exists!
				# Search the position of the gram in the string
				pos_found = symbols_string.find( s )
				if ( pos_found < 0 ):
					print("Error: " + s + " not found in probability file " + prob_path_filename + "\n")
					sys.exit(-6)

				size_s = len(s)
				while (pos_found >= 0) and (pos_found < size_symbols_list):
					max_pos = pos_found + size_s
					# Check that its is a complete word, not only part of it
					if max_pos == size_symbols_list or symbols_list[max_pos] == ' ':
						# Update the probabilities
						i = pos_found
						while i < max_pos:
							prob_list[i] = prob_list[i] + 3
							i = i + 1
						b_changed = True
					pos_found = symbols_string.find( s, max_pos )
			except KeyError:
				continue

		########################### 1-gram #########################
		# Get the possible 1-gram (case-sensitive)
		ngrams_list = get_ngrams( symbols_string, 1 )
		# Process each gram
		for ngram in ngrams_list:
			try:
				s = " ".join(ngram)
				s_lwr = s.lower()
				n_ngram = dict_1g[ s_lwr ]
				# It was found: the 1-gram exists!
				# Search the position of the gram in the string
				pos_found = symbols_string.find( s )
				if ( pos_found < 0 ):
					print("Error: " + s + " not found in probability file " + prob_path_filename + "\n")
					sys.exit(-7)

				size_s = len(s)
				while (pos_found >= 0) and (pos_found < size_symbols_list):
					max_pos = pos_found + size_s
					# Check that its is a complete word, not only part of it
					if max_pos == size_symbols_list or symbols_list[max_pos] == ' ':
						# Update the probabilities
						i = pos_found
						while i < max_pos:
							prob_list[i] = prob_list[i] + 1
							i = i + 1
						b_changed = True
					pos_found = symbols_string.find( s, max_pos )
			except KeyError:
				continue

		# Create a new probability file in the destination directory
		new_prob_path_filename = args.dstdir + "/" + basename + ".prob"

		s_to_save = ""
		i = 0
		while i < len(symbols_list):
			s_to_save += symbols_list[i] + "\t" + str(prob_list[i]) + "\n"
			i = i + 1

		new_f_prob = None
		with open( new_prob_path_filename, "w+" ) as new_f_prob: 
			new_f_prob.write(s_to_save)

		if (b_changed):
			j = j + 1			

	print("Probability augmented in " + str(j) + " files.")
