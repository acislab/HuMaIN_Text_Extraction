#!/usr/bin/env python3
##########################################################################################
# Developer: Icaro Alzuru         Project: HuMaIN (http://humain.acis.ufl.edu)
# Description: 
#   Makes the probability file consistent with the text file.
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
from Bio import pairwise2

# pip3 install biopython
#----------------------------------------------------------------------------------------------------------------------------------------------------------------
def align(s1, s2):
	l_s1 = list(s1)
	l_s2 = list(s2)

	r_aln = pairwise2.align.globalmx( l_s1, l_s2, 1, -1, gap_char=['-'], one_alignment_only=True)

	text_aligned = ""
	symbols_aligned = ""

	# Adaptation to pairwise2.align.globalmx
	alignment = []
	for aln in r_aln:
		# Convert lists back into strings
		a = ''.join(aln[0])
		b = ''.join(aln[1])

		new_aln = (a, b) + aln[2:]
		alignment.append(new_aln)

	n = len(alignment)
	if n < 1:
		print("ERROR: No alignment found for " + filename + "\n")
		return "", ""
	elif n == 1:
		text_aligned = alignment[0][0]
		symbols_aligned = alignment[0][1]
	else:
		max_score = alignment[0][2]
		max_i = 0
		i = 1
		while i < n:
			if max_score < alignment[i][2]:
				max_score = alignment[i][2]
				max_i = i
			i = i + 1
		text_aligned = alignment[max_i][0]
		symbols_aligned = alignment[max_i][1]

	return(text_aligned, symbols_aligned)

# python3 ../ALOT/fix_prob_text_dir.py -sd ./gr_lines_tesseract -dd gr_tesseract_fixed > report_tesseract_fixed.txt
#----------------------------------------------------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
	""" Makes the probability file consistent with the text file.
	"""
	parser = argparse.ArgumentParser("Makes the probability file consistent with the text file.")
	parser.add_argument('-sd', '--srcdir', action="store", required=True, help="Directory where the text and probability files are located.")
	parser.add_argument('-dd', '--dstdir', action="store", required=True, help="Directory where the new or corrected text and probability files will be saved.")
	args = parser.parse_args()

	# Arguments Validations
	if ( not os.path.isdir( args.srcdir ) ):
		print('Error: The directory with the text and prob files was not found.\n')
		parser.print_help()
		sys.exit(1)

	if not os.path.exists( args.dstdir ):
		try:
			os.makedirs( args.dstdir )  
		except:
			print('Error: The destination directory was not found and could not be created.\n')
			parser.print_help()
			sys.exit(2)

	# Create the lists of files to process
	files_list = list()
	for root, dirs, filenames in os.walk( args.srcdir ):
		files_list = list(f for f in filenames if f.endswith('.txt'))

	# Process each text file
	j = 0
	for filename in files_list:
		b_error_found = False
		txt_path_filename = args.srcdir + "/" + filename
		prob_path_filename = args.srcdir + "/" + (filename[:-4] + ".prob")

		###########################################################
		# Load the text file in a list
		text_string = ""
		f_text = None
		with open( txt_path_filename ) as f_text:
			lines = [line.rstrip('\n').rstrip(' ') for line in f_text]

		i = 0
		while i < len(lines):
			if i == 0:
				text_string = lines[i]
			else:
				text_string += " " + lines[i]
			i = i + 1
	
		# Empty file validation
		if text_string.strip() == "": 
			print("INFO: " + filename + " was empty.")
			continue

		text_list = list( text_string )
		##########################################################
		# Load the probability file in two lists
		symbols_list = []
		prob_list = []
		f_prob = None
		with open( prob_path_filename ) as f_prob: 
			for line in f_prob:
				try:
					symbol, prob = line.rstrip('\n').split("\t")
					if symbol != '':
						if len(symbol) > 1:
							for c in symbol:
								symbols_list.append( c )
								prob_list.append( float(prob) )
						else:
							symbols_list.append( symbol )
							prob_list.append( float(prob) )
				except:
					break

		size_text_list = len(text_list)
		size_symbols_list = len(symbols_list)
		symbols_string = ''.join( symbols_list )

		new_text = text_string
		new_symbols_list = symbols_list
		new_prob_list = prob_list

		# If the strings are different
		if (size_text_list != size_symbols_list) or (text_string != symbols_string):
			new_text = ""
			new_symbols_list = []
			new_prob_list = []

			# Align the contents
			text_aligned, symbols_aligned = align( text_string, symbols_string )

			if text_string == "":
				b_error_found = True

			len_text_string = len(text_string)
			len_symbols_list = len(symbols_list)

			i_aligned = 0
			i_orig_txt = 0
			i_orig_sym = 0
			while i_aligned < len(text_aligned):
				# We need to check consistency in the alignment process
				if i_orig_txt < len_text_string:
					if (text_aligned[i_aligned] != text_string[i_orig_txt] and text_aligned[i_aligned] != '-'):
						print("ERROR: Mismatch between the original and the aligned text (" + txt_path_filename + ").")
						print("Original: " + text_string[i_orig_txt] + ", position " + str(i_orig_txt) + ".")
						print("Aligned: " + text_aligned[i_aligned] + ", position " + str(i_aligned) + ".\n")
						b_error_found = True
						break
				if i_orig_sym < len_symbols_list:
					if (symbols_aligned[i_aligned] != symbols_list[i_orig_sym] and symbols_aligned[i_aligned] != '-'):
						print("ERROR: Mismatch between the original and the aligned probability text (" + txt_path_filename + ").")
						print("Original: " + str(symbols_list[i_orig_sym]) + ", position " + str(i_orig_sym) + ".")
						print("Aligned: " + str(symbols_aligned[i_aligned]) + ", position " + str(i_aligned) + ".\n")
						b_error_found = True
						break

				# If both lists point to the same value
				if text_aligned[i_aligned] == symbols_aligned[i_aligned]:
					# Special cases with hyphen (-) the character used to indicate differences
					# Hyphen in the original text file, nothing in the original probabilities file => both with hyphen in the aligned strings
					if  i_orig_txt < len_text_string and text_string[i_orig_txt] == '-' and (i_orig_sym >= len_symbols_list or symbols_list[i_orig_sym] != '-'):
						# Eliminate that hyphen, because we do not have its probability
						i_orig_txt += 1
					# Hyphen in the original probabilities file, nothing in the original text file => both with hyphen in the aligned strings
					elif i_orig_sym < len_symbols_list and symbols_list[i_orig_sym] == '-' and (i_orig_txt >= len_text_string or text_string[i_orig_txt] != '-'):
						# Add the hyphen found in the probabilities files
						new_text = new_text + '-'
						new_symbols_list.append( '-' )
						new_prob_list.append( prob_list[i_orig_sym] )
						i_orig_sym += 1

					# Common case: a hyphen or other symbol was found in the original text file and in the original probabilities file
					else:
						# Insert the symbol and probability in the new lists
						new_text = new_text + text_aligned[i_aligned]
						new_symbols_list.append( text_aligned[i_aligned] )
						new_prob_list.append( prob_list[i_orig_sym] )
						i_orig_txt += 1
						i_orig_sym += 1

				# A character in aligned text that does not exist in the probability file
				elif (symbols_aligned[i_aligned] == '-'):
					# A space is fine, because the prob file did not consider them
					if (text_aligned[i_aligned] == ' '):
						# We add the value to the new probability file
						new_text = new_text + ' '
						new_symbols_list.append( ' ' )
						new_prob_list.append( 0.9 ) # Uncertain value
					
					# Something else than a space: ommit because we do not know the probability
					# else:
					#	pass
					i_orig_txt += 1

				# The prob file contains something that is not in the text or there is a mismatch
				# We accept the prob symbol, because contains a probability
				else:
					new_text = new_text + symbols_aligned[i_aligned]
					new_symbols_list.append( symbols_aligned[i_aligned] )
					new_prob_list.append( prob_list[i_orig_sym] )

					if text_aligned[i_aligned] != '-':
						i_orig_txt += 1
					i_orig_sym += 1					
					
				i_aligned += 1

		# ----------------------------------------------------------------------------------
		if not b_error_found:
			# Save the new text and probability files
			new_txt_path_filename = args.dstdir + "/" + filename
			new_prob_path_filename = args.dstdir + "/" + (filename[:-4] + ".prob")

			# Replace 2 spaces by one single space and create final strings
			final_text = ""
			final_prob = ""
			i = 0
			prev_symbol = ''
			while i < len(new_symbols_list):
				if new_symbols_list[i] != ' ' or prev_symbol != ' ':  # Filter the double spaces
					print
					if (new_text[i] != new_symbols_list[i]): # Error:
						print("Error: inconsistency in the computed result for file " + filename)
						sys.exit(-5)
					
					final_text += new_symbols_list[i]
					final_prob += new_symbols_list[i] + "\t" + str(new_prob_list[i]) + "\n"
					prev_symbol = new_symbols_list[i]
				i = i + 1

			f_new_txt = None
			with open( new_txt_path_filename, "w+" ) as f_new_txt:
				f_new_txt.write( final_text )

			f_new_prob = None
			with open( new_prob_path_filename, "w+" ) as f_new_prob:
				f_new_prob.write( final_prob )

			j = j + 1
	print("Total modified files: " + str(j))
