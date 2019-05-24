#!/usr/bin/env python3
##########################################################################################
# Developer: Icaro Alzuru         Project: HuMaIN (http://humain.acis.ufl.edu)
# Description: 
#   Generates the file with the accepted or known lines: When the three OCRs generate the 
# same value or when only two generate the same value and have a confidence > 0.9.
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
import argparse, io, os, sys
from Bio import pairwise2

# python3 ../ALOT/accept_from_ngrams.py -i1 ./gr_ocropus_fixed/ -i2 ./gr_tesseract_fixed -i3 ./gr_google_fixed -d accepted
#----------------------------------------------------------------------------------------------------------------------------------------------------------------
fname_ocropus_stats = "/home/user/digi_13297227/H-MaTE/ocropus_symbols_stats.txt" # OCR 1
fname_tesseract_stats = "/home/user/digi_13297227/H-MaTE/tesseract_symbols_stats.txt" # OCR 2
fname_google_stats = "/home/user/digi_13297227/H-MaTE/google_symbols_stats.txt" # OCR 3
ocropus_stats = {}
tesseract_stats = {}
google_stats = {}
#----------------------------------------------------------------------------------------------------------------------------------------------------------------
def align(s1, p1, s2, p2):
	""" Aligns the text and probability files of two strings. Returns their aligned versions.
	"""
	l_s1 = list(s1)
	l_s2 = list(s2)

	# r_aln = pairwise2.align.globalmx( l_s1, l_s2, 1, -1, gap_char=['#'], one_alignment_only=True)
	r_aln = pairwise2.align.globalms(l_s1, l_s2, 1, -1, -1, -1, gap_char=['#']) # match, non-identical character, gap-open, extending gap

	s1_aligned = ""
	s2_aligned = ""

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
		print("ERROR: No alignment found for " + s1 + " and " + s2 + "\n")
		return "", [], "", []
	elif n == 1:
		s1_aligned = alignment[0][0]
		s2_aligned = alignment[0][1]
	else:
		max_score = alignment[0][2]
		max_i = 0
		i = 1
		while i < n:
			if max_score < alignment[i][2]:
				max_score = alignment[i][2]
				max_i = i
			i = i + 1
		s1_aligned = alignment[max_i][0]
		s2_aligned = alignment[max_i][1]

	# Alignment of the probabilities of the first string
	i_o = 0
	i_a = 0
	p1_aligned = []
	size_s1 = len(s1)
	while i_a < len(s1_aligned):
		if (i_o < size_s1):
			if s1[i_o] == s1_aligned[i_a]:
				p1_aligned.append( p1[i_o] )
				i_o = i_o + 1
			elif s1_aligned[i_a] == '#':
				p1_aligned.append( -1.0 )
			else:
				print("ERROR: First string's symbols " + s1[i_o] + " and " + s1_aligned[i_a] + " do not match\n")
				return "", [], "", []
		elif s1_aligned[i_a] == '#':
			p1_aligned.append( -1.0 )
		else:
			print("ERROR: First string's symbols do not match with its aligned version\n")
			return "", [], "", []
		i_a = i_a + 1

	# Alignment of the probabilities of the second string
	i_o = 0
	i_a = 0
	p2_aligned = []
	size_s2 = len(s2)
	while i_a < len(s2_aligned):
		if i_o < size_s2:
			if s2[i_o] == s2_aligned[i_a]:
				p2_aligned.append( p2[i_o] )
				i_o = i_o + 1
			elif s2_aligned[i_a] == '#':
				p2_aligned.append( -1.0 )
			else:
				print("ERROR: Second string's symbols " + s2[i_o] + " and " + s2_aligned[i_a] + " do not match\n")
				return "", [], "", []
		elif s2_aligned[i_a] == '#':
			p2_aligned.append( -1.0 )
		else:
			print("ERROR: Second string's symbols do not match with its aligned version\n")
			return "", [], "", []
		i_a = i_a + 1

	return(s1_aligned, p1_aligned, s2_aligned, p2_aligned)

#----------------------------------------------------------------------------------------------------------------------------------------------------------------
def loadProbFile( probPathFilename ):
	""" Reads the probability file and returns a list with the symbols and a list with the probabilities.
	"""
	symbols_list = []
	prob_list = []
	with open( probPathFilename ) as f_prob: 
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

	return symbols_list, prob_list

#----------------------------------------------------------------------------------------------------------------------------------------------------------------
def loadStatsFile( t ):
	""" Reads the average, median, standard deviation, and number of repetitions of a stats files of the OCRs.
	"""
	with open( fname_ocropus_stats ) as f_o: 
		for line in f_o:
			n = 0
			symbol, mean, median, stddev, n = line.rstrip('\n').split("\t")
			if int(n) >= t:
				ocropus_stats[ symbol ] = [float(mean), float(stddev)]

	with open( fname_tesseract_stats ) as f_t: 
		for line in f_t:
			n = 0
			symbol, mean, median, stddev, n = line.rstrip('\n').split("\t")
			if int(n) >= t:
				tesseract_stats[ symbol ] = [float(mean), float(stddev)]

	with open( fname_google_stats ) as f_g: 
		for line in f_g:
			n = 0
			symbol, mean, median, stddev, n = line.rstrip('\n').split("\t")
			if int(n) >= t:
				google_stats[ symbol ] = [float(mean), float(stddev)]

#----------------------------------------------------------------------------------------------------------------------------------------------------------------
def getHigherProb( c1, p1, c2, p2, dict_stats1, dict_stats2 ):
	# Initialization of the zscores (This is used as a threshold)
	# If there is a # and x with zscore < -1, we will accept # => no character will be written
	zscore1 = -1.0
	zscore2 = -1.0

	# Lookup mean1 and stddev1
	mean1 = -1.0
	stddev1 = -1.0
	if not(c1 == '#' and p1 == -1.0):
		try:
			mean1, stddev1 = dict_stats1[ c1 ]
		except KeyError:
			pass
	
	# Lookup mean2 and stddev2
	mean2 = -1.0
	stddev2 = -1.0
	if not(c2 == '#' and p2 == -1.0):
		try:
			mean2, stddev2 = dict_stats2[ c2 ]
		except KeyError:
			pass

	# Computation of the zscores
	if stddev1 != 0 and mean1 != -1:
		zscore1 = (p1 - mean1)/stddev1
	if stddev2 != 0 and mean2 != -1:
		zscore2 = (p2 - mean2)/stddev2

	# Return the maximum
	if zscore1 > zscore2 and mean1 != -1:
		return(c1, p1)
	else:
		return(c2, p2)
		
#----------------------------------------------------------------------------------------------------------------------------------------------------------------
def getHigherProb3( c1, p1, c2, p2, c3, p3, dict1, dict2, dict3 ):
	# Initialization of the zscores (This is used as a threshold)
	# If there is a # and zscore1 and zscore2 are less than -1, we will accept # => no character will be written
	zscore1 = -1.0
	zscore2 = -1.0
	zscore3 = -1.0

	# We search the mean and standard deviation for the symbols in their correspondent OCRs
	mean1 = -1.0
	stddev1 = -1.0
	if not(c1 == '#' and p1 == -1.0):
		try:
			mean1, stddev1 = dict1[ c1 ]
		except KeyError:
			pass

	mean2 = -1.0
	stddev2 = -1.0
	if not(c2 == '#' and p2 == -1.0):
		try:
			mean2, stddev2 = dict2[ c2 ]
		except KeyError:
			pass

	mean3 = -1.0
	stddev3 = -1.0
	if not(c3 == '#' and p3 == -1.0):
		try:
			mean3, stddev3 = dict3[ c3 ]
		except KeyError:
			pass

	# Computation of the zscores
	if stddev1 != 0 and mean1 != -1:
		zscore1 = (p1 - mean1)/stddev1
	if stddev2 != 0 and mean2 != -1:
		zscore2 = (p2 - mean2)/stddev2
	if stddev3 != 0 and mean3 != -1:
		zscore3 = (p3 - mean3)/stddev3
	# Looking up the maximum
	max_c = c1
	max_p = p1
	max_zscore = zscore1
	if zscore2 >= max_zscore:
		max_c = c2
		max_p = p2
		max_zscore = zscore2
	if zscore3 >= max_zscore:
		max_c = c3
		max_p = p3
		max_zscore = zscore3

	# Return the best value
	return(max_c, max_p)

#----------------------------------------------------------------------------------------------------------------------------------------------------------------
def consensus( s1_aligned, p1_aligned, s2_aligned, p2_aligned, dict_stats1, dict_stats2 ):
	""" From the aligned strings and probabilities of two results, it generates a consensus result, which can include 
	some undecided characters."""
	if len(s1_aligned) == 0 or len(s2_aligned) == 0 or len(s1_aligned) != len(s2_aligned):
		return [], []
	
	s12 = []
	p12 = []
	i = 0
	while i<len(s1_aligned):
		if s1_aligned[i] == s2_aligned[i]:  # Consensus reach
			# Add the character
			s12.append( s1_aligned[i] )
			if p1_aligned[i] > 1.0 and p2_aligned[i] > 1.0: # Both in n-grams
				p12.append( 10.0 )
			elif p1_aligned[i] > 1.0 or p2_aligned[i] > 1.0: # Only one in n-gram
				p12.append( 5.0 )
			elif zGreaterTo( s1_aligned[i], p1_aligned[i], dict_stats1, 0.5 ) and zGreaterTo( s2_aligned[i], p2_aligned[i], dict_stats2, 0.5 ): # Good confidence
				p12.append( 2.0 )
			else: 	# The character was not recognized in any n-gram (Some risk)
				p12.append( 1.0 )
		else: # No consensus: different characters found. Return the one with the highest zscore
			w_c, w_p = getHigherProb( s1_aligned[i], p1_aligned[i], s2_aligned[i], p2_aligned[i], dict_stats1, dict_stats2 )
			if not(w_c == '#' and w_p == -1.0):
				s12.append( w_c )
				p12.append( w_p )
		i = i + 1

	return s12, p12

#----------------------------------------------------------------------------------------------------------------------------------------------------------------
def consensus_3( s1_aligned, p1_aligned, s2_aligned, p2_aligned, dict_stats1, dict_stats2 ):
	""" From the aligned strings and probabilities of two results, it generates a consensus result, which can include 
	some undecided characters."""
	if len(s1_aligned) == 0 or len(s2_aligned) == 0 or len(s1_aligned) != len(s2_aligned):
		return [], []
	
	s12 = []
	p12 = []
	i = 0
	while i<len(s1_aligned):
		if s1_aligned[i] == s2_aligned[i]:  # Consensus reach
			# Add the character
			s12.append( s1_aligned[i] )
			if p1_aligned[i] > 1.0 and p2_aligned[i] > 1.0: # Both in n-grams
				p12.append( 10.0 )
			elif p1_aligned[i] > 1.0 or p2_aligned[i] > 1.0: # Only one in n-gram
				p12.append( 5.0 )
			elif zGreaterTo( s1_aligned[i], p1_aligned[i], dict_stats1, 0.5 ) and zGreaterTo( s2_aligned[i], p2_aligned[i], dict_stats2, 0.5 ): # Good confidence
				p12.append( 2.0 )
			else: 	# The character was not recognized in any n-gram (Some risk)
				p12.append( 1.0 )
		else: # No consensus: different characters found. Return the one with the highest zscore
			if s2_aligned[i] != '#':
				s12.append( s2_aligned[i] )
				p12.append( p2_aligned[i] )
		i = i + 1

	return s12, p12

#----------------------------------------------------------------------------------------------------------------------------------------------------------------
def consensus12( o_s_aligned, o_p_aligned, t_s_aligned, t_p_aligned, dict_stats1, dict_stats2 ):
	""" From the aligned strings and probabilities of two results, it generates a consensus result, which can include 
	some undecided characters."""
	if len(o_s_aligned) == 0 or len(t_s_aligned) == 0 or len(o_s_aligned) != len(t_s_aligned):
		return [], []
	
	s12 = []
	p12 = []
	i = 0
	while i<len(o_s_aligned):
		if o_s_aligned[i] == t_s_aligned[i]:  # Consensus reach
			if o_p_aligned[i] > 1.0 and t_p_aligned[i] > 1.0: # Both in n-grams
				s12.append( o_s_aligned[i] )
				p12.append( 10.0 )
			elif o_p_aligned[i] > 1.0 or t_p_aligned[i] > 1.0: # Only one in n-gram
				s12.append( o_s_aligned[i] )
				p12.append( 5.0 )
			else: 	# The character was not recognized in any n-gram (Some risk)
				# w_c, w_p = getHigherProb( o_s_aligned[i], o_p_aligned[i], t_s_aligned[i], t_p_aligned[i], dict_stats1, dict_stats2 )
				s12.append( [t_s_aligned[i], o_s_aligned[i]] )
				p12.append( [t_p_aligned[i], o_p_aligned[i]] )
		else: # We prefer the Tesseract's output because generates less garbage
			s12.append( [t_s_aligned[i], o_s_aligned[i]] )
			p12.append( [t_p_aligned[i], o_p_aligned[i]] )
		i = i + 1

	return s12, p12

#----------------------------------------------------------------------------------------------------------------------------------------------------------------
def zGreaterTo( c1, p1, dict1, t ):
	mean1 = -1.0
	stddev1 = -1.0
	try:
		mean1, stddev1 = dict1[ c1 ]
	except KeyError:
		pass

	# Not found
	if mean1 < 0:
		return False

	# High probability
	if mean1 > p1:
		zscore1 = (p1 - mean1)/stddev1
		if zscore1 >= t:
			return True
	return False

#----------------------------------------------------------------------------------------------------------------------------------------------------------------
def consensus3( s12_aligned, p12_aligned, s3_aligned, p3_aligned ):
	""" Given the aligned 12 and 3 strings, creates a new string and probability result from the consensus of 1,2, and 3.
	"""
	if len(s12_aligned) == 0 or len(s3_aligned) == 0 or len(s12_aligned) != len(s3_aligned):
		return [], []

	s123 = []
	p123 = []
	i = 0

	while i<len(s12_aligned):
		if len(s12_aligned[i]) > 1: # Multivalued (there are two options): There was no consensus

			if s12_aligned[i][0] == s3_aligned[i] and s12_aligned[i][1] == s3_aligned[i]: # Good chances of being correct
				s123.append( s12_aligned[i][0] )
				p123.append( 3.0 )

			elif s12_aligned[i][0] == s3_aligned[i]:  # Match Tesseract - Google
				if s12_aligned[i][0] != '#':
					if (p12_aligned[i][0] < 1.0 and p3_aligned[i] >= 1.0) or (p12_aligned[i][0] >= 1.0 and p3_aligned[i] < 1.0) or (p12_aligned[i][0] >= 1.0 and p3_aligned[i] >= 1.0): # Good consensus
						s123.append( s12_aligned[i][0] )
						p123.append( 5.0 )
					else: # Both probabilities are less than 1.0, but the characters are the same
						# If both OCR have high confidence
						if zGreaterTo( s12_aligned[i][0], p12_aligned[i][0], tesseract_stats, 0.5 ) and zGreaterTo( s3_aligned[i], p3_aligned[i], google_stats, 0.5 ):
							s123.append( s12_aligned[i][0] )
							p123.append( 2.0 )
						else:  # The character will be accepted, but the string will be rejected (probability <= 1.0)
							s123.append( s12_aligned[i][0] )
							p123.append( p12_aligned[i][0] )

			elif s12_aligned[i][1] == s3_aligned[i]: # Match OCRopus - Google
				if s12_aligned[i][1] != '#':
					if (p12_aligned[i][1] < 1.0 and p3_aligned[i] >= 1.0) or (p12_aligned[i][1] >= 1.0 and p3_aligned[i] < 1.0) or (p12_aligned[i][1] >= 1.0 and p3_aligned[i] >= 1.0): # Good consensus
						s123.append( s12_aligned[i][1] )
						p123.append( 5.0 )
					else: # Both probabilities are less than 1.0, but the characters are the same
						# If both OCR have high confidence
						if zGreaterTo( s12_aligned[i][1], p12_aligned[i][1], ocropus_stats, 0.5 ) and zGreaterTo( s3_aligned[i], p3_aligned[i], google_stats, 0.5 ):
							s123.append( s12_aligned[i][1] )
							p123.append( 2.0 )
						else:  # The character will be accepted, but the string will be rejected (probability <= 1.0)
							s123.append( s12_aligned[i][1] )
							p123.append( 1.0 )

			elif s12_aligned[i][1] == s12_aligned[i][0]: # Match OCRopus - Tesseract
				if s3_aligned[i] != '#':
					# If both OCR have high confidence
					if zGreaterTo( s12_aligned[i][1], p12_aligned[i][1], ocropus_stats, 0.5 ) and zGreaterTo( s12_aligned[i][0], p12_aligned[i][0], ocropus_stats, 0.5 ):
						s123.append( s12_aligned[i][1] )
						p123.append( 1.0 )
					else:
						s123.append( s3_aligned[i] )
						p123.append( p3_aligned[i] )

					# if (p12_aligned[i][1] < 1.0 and p12_aligned[i][0] >= 1.0) or (p12_aligned[i][1] >= 1.0 and p12_aligned[i][0] < 1.0) or (p12_aligned[i][1] >= 1.0 and p12_aligned[i][0] >= 1.0): # Good consensus
					# 	s123.append( s12_aligned[i][1] )
					# 	p123.append( 5.0 )
					# else: # Both probabilities are less than 1.0, but the characters are the same
					# 	# If both OCR have high confidence
					# 	if zGreaterTo( s12_aligned[i][1], p12_aligned[i][1], ocropus_stats, 0.5 ) and zGreaterTo( s12_aligned[i][0], p12_aligned[i][0], ocropus_stats, 0.5 ):
					# 		s123.append( s12_aligned[i][1] )
					# 		p123.append( 2.0 )
					# 	else:  # The character will be accepted, but the string will be rejected (probability <= 1.0)
					# 		s123.append( s12_aligned[i][1] )
					# 		p123.append( 1.0 )	
			else: # There was not match: 3 different characters.
				if s3_aligned[i] != '#':
					s123.append( s3_aligned[i] )
					p123.append( p3_aligned[i] )
				# w_c, w_p = '#', -1.0
				# w_c, w_p = getHigherProb3( s12_aligned[i][1], p12_aligned[i][1], s12_aligned[i][0], p12_aligned[i][0], s3_aligned[i], p3_aligned[i], ocropus_stats, tesseract_stats, google_stats )
				# if not(w_c == '#' and w_p == -1.0):
				# 	s123.append( w_c )
				# 	p123.append( w_p )
							
		elif len(s12_aligned[i]) == 1: # There was previously consensus between OCRopus and Tesseract
			if p12_aligned[i] > 1.0: # The symbol belonged to n-grams, just accept (Consensus had already been reached)
				s123.append( s12_aligned[i] )
				p123.append( p12_aligned[i] )
			elif s12_aligned[i] == '#': # New symbol in Google that did not existed in OCRopus nor Tesseract
				s123.append( s3_aligned[i] )
				p123.append( p3_aligned[i] )
			else: # Error: It should not be univalued
				print(s12_aligned[i])
				print(i)
				print('Error: Unexpected symbol in consensus3.py: ' + s12_aligned[i] + '.\n')
				return ([], [])

		else:
			print('Error: Unexpected empty character in consensus3.py.\n')
			return ([], [])

		i = i + 1
	return s123, p123

#----------------------------------------------------------------------------------------------------------------------------------------------------------------
def verify_and_save(s_list, p_list, pathAccept, filename, pathReject):
	if len(s_list) != len(p_list):
		print("ERROR: s_list and p_list have different length in verify_and_save().\n")
		return

	accept_line = True
	s_text = ""
	s_prob = ""	
	j = 0
	while j < len(p_list):
		if p_list[j] < 1.0:  
			accept_line = False

		s_text += s_list[j]
		s_prob += s_list[j] + "\t" + str(p_list[j]) + "\n"
		j = j + 1

	if accept_line: # We are confident that all the extracted in the line is correct
		s_prob = s_prob[:-1]

		# We write the accepted results to disk
		text_PathFilename = pathAccept + "/" + filename[:-5] + ".txt"
		prob_PathFilename = pathAccept + "/" + filename
		f_t = None
		with open( text_PathFilename, "w+" ) as f_t:
			f_t.write( s_text )
		f_p = None
		with open( prob_PathFilename, "w+" ) as f_p:
			f_p.write( s_prob )
	else:
		if len(s_prob)>1:
			s_prob = s_prob[:-1]

		# We write the accepted results to disk
		text_PathFilename = pathReject + "/" + filename[:-5] + ".txt"
		prob_PathFilename = pathReject + "/" + filename
		f_t = None
		with open( text_PathFilename, "w+" ) as f_t:
			f_t.write( s_text )
		f_p = None
		with open( prob_PathFilename, "w+" ) as f_p:
			f_p.write( s_prob )

# python3 ../ALOT/accept_from_ngrams.py -i1 ./gr_ocropus_fixed/ -i2 ./gr_tesseract_fixed -i3 ./gr_google_fixed -d accepted
#----------------------------------------------------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
	""" Generates the file with the accepted or known lines: When the three OCRs generate the same value or when only two generate the same value and have a confidence > 0.9. 
	"""
	parser = argparse.ArgumentParser("Generates the file with the accepted or known lines: When the three OCRs generate the same value or when only two generate the same value and have a confidence > 0.9.")
	parser.add_argument('-i1', '--input1', action="store", required=True, help="Directory where the OCRopus probability files are located.")
	parser.add_argument('-i2', '--input2', action="store", required=True, help="Directory where the Tesseract probability files are located.")
	parser.add_argument('-i3', '--input3', action="store", required=True, help="Directory where the Google probability files are located.")
	parser.add_argument('-da', '--dstdir_a', action="store", required=True, help="Directory where the accepted text and probability files will be saved.")
	parser.add_argument('-dr', '--dstdir_r', action="store", required=True, help="Directory where the rejected text and probability files will be saved.")
	args = parser.parse_args()

	# Arguments Validations
	if ( not os.path.isdir( args.input1 ) ):
		print('Error: The first directory of probability files was not found.\n')
		parser.print_help()
		sys.exit(-1)

	if ( not os.path.isdir( args.input2 ) ):
		print('Error: The second directory of probability files was not found.\n')
		parser.print_help()
		sys.exit(-2)

	if ( not os.path.isdir( args.input3 ) ):
		print('Error: The third directory of probability files was not found.\n')
		parser.print_help()
		sys.exit(-3)

	if not os.path.exists( args.dstdir_a ):
		try:
			os.makedirs( args.dstdir_a )  
		except:
			print('Error: The destination directory was not found and could not be created.\n')
			parser.print_help()
			sys.exit(-4)

	if not os.path.exists( args.dstdir_r ):
		try:
			os.makedirs( args.dstdir_r )  
		except:
			print('Error: The destination directory was not found and could not be created.\n')
			parser.print_help()
			sys.exit(-5)

	# Create the lists of files to process
	files_list1 = list()
	for root, dirs, filenames in os.walk( args.input1 ):
		files_list1 = list(f for f in filenames if f.endswith('.prob'))
	n1 = len(files_list1)

	files_list2 = list()
	for root, dirs, filenames in os.walk( args.input2 ):
		files_list2 = list(f for f in filenames if f.endswith('.prob'))
	n2 = len(files_list2)

	files_list3 = list()
	for root, dirs, filenames in os.walk( args.input3 ):
		files_list3 = list(f for f in filenames if f.endswith('.prob'))
	n3 = len(files_list3)

	files_set1 = set( files_list1 )
	files_set2 = set( files_list2 )
	files_set3 = set( files_list3 )

	# Set of probabilities files present or common in the three directories
	files_set123 = files_set1 & files_set2 & files_set3
	files_list123 = list(files_set123)
	files_list123.sort()

	# Set of probabilities files only present in the directories 1 and 2
	files_set12 = (files_set1 & files_set2) - files_set3
	files_list12 = list(files_set12)
	files_list12.sort()

	# Set of probabilities files only present in the directories 1 and 3
	files_set13 = (files_set1 & files_set3) - files_set2
	files_list13 = list(files_set13)
	files_list13.sort()

	# Set of probabilities files only present in the directories 2 and 3
	files_set23 = (files_set2 & files_set3) - files_set1
	files_list23 = list(files_set23)
	files_list23.sort()

	################################################################################################
	# Load the stats per symbol files, for the three OCRs (adds only the symbols with 10 or more ocurrences)
	loadStatsFile( 10 )

	################################################################################################
	# 									ACCEPTANCE PROCESS
	################################################################################################

	######################################### 1 2 3 ################################################
	# OCRopus, Tesseract, and Google Cloud Platform (GCP) OCR
	######################################### 1 2 3 ################################################
	# files_list123 = [ 'EMEC609939_Stigmus_sp_006.prob' ]
	i = 0
	while i<len(files_list123):
		filename = files_list123[i]
		s1, p1 = [], []
		s1, p1 = loadProbFile( args.input1 + "/" + filename )
		s2, p2 = [], []
		s2, p2 = loadProbFile( args.input2 + "/" + filename )
		s3, p3 = [], []
		s3, p3 = loadProbFile( args.input3 + "/" + filename )

		n1 = len(s1)
		n2 = len(s2)
		n3 = len(s3)

		if n1 < 1: # OCRopus generated just an empty file
			files_list23.append( filename )
			continue
		if n2 < 1: # Tesseract generated just an empty file
			files_list13.append( filename )
			continue
		if n3 < 1: # Google generated just an empty file
			files_list12.append( filename )
			continue			

		#########################
		# OCRopus and Tesseract #
		#########################
		# Align the OCRopus and Tesseract results
		s1_aligned, p1_aligned, s2_aligned, p2_aligned = "", [], "", []
		s1_aligned, p1_aligned, s2_aligned, p2_aligned = align(s1, p1, s2, p2)

		if s1_aligned == "":
			print("ERROR: File " + filename + ". It was not possible to make the alignment with OCRs 1 and 2.")
			i = i + 1
			continue

		# Generate the consensus of the first and second aligned results
		# If no consensus, the Tesseract's result goes first
		s12, p12 = [], []
		s12, p12 = consensus12( s1_aligned, p1_aligned, s2_aligned, p2_aligned, ocropus_stats, tesseract_stats )

		##########
		# Google #
		##########
		# We create auxiliar s12 and p12 structures to be able to make the alignment with s3 and p3
		s12_aux = ""
		p12_aux = []
		j = 0 			
		while j < len(s12):
			if len( s12[j] ) > 1:  # Multivalued: pick the Tesseract character
				s12_aux = s12_aux + s12[j][0]
				p12_aux.append( p12[j][0] )
			else:
				s12_aux = s12_aux + s12[j]
				p12_aux.append( p12[j] )
			j = j + 1

		# Align the s12_aux and the third results
		s12_aux_aligned, p12_aux_aligned, s3_aligned, p3_aligned = "", [], "", []
		s12_aux_aligned, p12_aux_aligned, s3_aligned, p3_aligned = align(s12_aux, p12_aux, s3, p3)
		if len(s12_aux_aligned) < 1:
			print("ERROR: File " + filename + ". It was not possible to do the alignment of OCRs 12 and 3.")
			i = i + 1
			continue

		# Create the s12_aligned and the p12_aligned: include the multivalued symbols (OCRopus) that were previously deleted
		s12_aligned = []
		p12_aligned = []
		s12_size = len(s12)
		b_error = False
		j = 0
		j_o = 0
		while j < len(s12_aux_aligned):
			#print(s12[j_o], s12_aux_aligned[j])
			if j_o<s12_size and len(s12[j_o]) > 1: # Multivalued
				if s12_aux_aligned[j] == s12[j_o][0]:
					s12_aligned.append( s12[j_o] )
					p12_aligned.append( p12[j_o] )
					j_o = j_o + 1
				elif s12_aux_aligned[j] ==  '#':
					s12_aligned.append( '#' )
					p12_aligned.append( p12_aux_aligned[j] )
				else: 
					print("ERROR: The s12_aux_aligned string has an unmatched and non # symbol. Filename: " + filename + "\n")
					b_error = True
					break

			elif j_o<s12_size: # Univalued
				if s12_aux_aligned[j] == s12[j_o]:
					s12_aligned.append( s12[j_o] )
					p12_aligned.append( p12[j_o] )
					j_o = j_o + 1
				elif s12_aux_aligned[j] ==  '#':
					s12_aligned.append( '#' )
					p12_aligned.append( p12_aux_aligned[j] )
				else: 
					print("ERROR: The s12_aux_aligned string has an unmatched non # symbol. Filename: " + filename + "\n")
					b_error = True
					break

			else: # No more symbols in s12
				if s12_aux_aligned[j] == '#':
					s12_aligned.append( '#' )
					p12_aligned.append( p12_aux_aligned[j] )
				else:
					print("ERROR: The s12_aux_aligned string has more values than expected. Filename: " + filename + "\n")
					b_error = True
					break
			j = j + 1

		# Check if there was some problem
		if b_error:
			i = i + 1
			continue

		# Generate the consensus of the first/second and the third aligned results
		s123, p123 = [], []
		s123, p123 = consensus3( s12_aligned, p12_aligned, s3_aligned, p3_aligned )
		if len(s123) == 0: # Something failed
			print("WARNING: File " + filename + ". It was not possible to reach consensus between OCRs 12 and 3.")
			i = i + 1
			continue

		# Check if all the probability are equal or greater than 1.0 and saves the new text and probability files
		verify_and_save( s123, p123, args.dstdir_a, filename, args.dstdir_r )

		i = i + 1

	######################################### 1 2 ################################################
	# OCRopus and Tesseract
	######################################### 1 2 ################################################	
	i = 0
	while i<len(files_list12):
		# Read & load the content of the text and probability files
		filename = files_list12[i]
		s1, p1 = [], []
		s1, p1 = loadProbFile( args.input1 + "/" + filename )
		s2, p2 = [], []
		s2, p2 = loadProbFile( args.input2 + "/" + filename )

		n1 = len(s1)
		n2 = len(s2)

		# Validate the content: Check if it is different to empty
		if n1 < 1: # OCRopus generated just an empty file
			print("WARNING: OCRopus' output for line " + filename + " is empty or could not be read.")
			if n2 < 1: # Tesseract's output is also empty
				print("ERROR: No OCR provided any result for line " + filename + ".")
			else:
				# The answer will be the Tesseract's response (no consensus)
				verify_and_save( s2, p2, args.dstdir_a, filename, args.dstdir_r )
			i = i + 1
			continue
		if n2 < 1: # Tesseract generated just an empty file
			print("WARNING: Tesseract's output for line " + filename + " is empty or could not be read.")
			# The answer will be the OCRopus' response (no consensus)
			verify_and_save( s1, p1, args.dstdir_a, filename, args.dstdir_r )
			i = i + 1
			continue

		# Align the OCRopus and Tesseract results
		s1_aligned, p1_aligned, s2_aligned, p2_aligned = "", [], "", []
		s1_aligned, p1_aligned, s2_aligned, p2_aligned = align(s1, p1, s2, p2)
		if s1_aligned == "":
			print("ERROR: File " + filename + ". It was not possible to make the alignment between OCRopus' and Tesseract's results.")
			i = i + 1
			continue		

		# Generate the consensus of the first and second aligned results
		s12, p12 = [], []
		s12, p12 = consensus( s1_aligned, p1_aligned, s2_aligned, p2_aligned, ocropus_stats, tesseract_stats )
		
		if len(s12) == 0: # Something failed
			print("WARNING: File " + filename + ". It was not possible to reach consensus between OCRs 1 and 2.")
			i = i + 1
			continue

		# Check if all the probability are equal or greater than 1.0 and saves the new text and probability files
		verify_and_save( s12, p12, args.dstdir_a, filename, args.dstdir_r )

		i = i + 1

	######################################### 1 3 ################################################
	# OCRopus and Google
	######################################### 1 3 ################################################	
	i = 0
	while i<len(files_list13):
		# Read & load the content of the text and probability files
		filename = files_list13[i]
		s1, p1 = [], []
		s1, p1 = loadProbFile( args.input1 + "/" + filename )
		s3, p3 = [], []
		s3, p3 = loadProbFile( args.input3 + "/" + filename )

		n1 = len(s1)
		n3 = len(s3)

		# Validate the content: Check if it is different to empty
		if n1 < 1: # OCRopus generated just an empty file
			print("WARNING: OCRopus' output for line " + filename + " is empty or could not be read.")
			if n3 < 1: # Google's output is also empty
				print("ERROR: No OCR provided any result for line " + filename + ".")
			else:
				# The answer will be the Google's response (no consensus)
				verify_and_save( s3, p3, args.dstdir_a, filename, args.dstdir_r )
			i = i + 1
			continue
		if n3 < 1: # Google generated just an empty file
			print("WARNING: Google's output for line " + filename + " is empty or could not be read.")
			# The answer will be the OCRopus' response (no consensus)
			verify_and_save( s1, p1, args.dstdir_a, filename, args.dstdir_r )
			i = i + 1
			continue

		# Align the OCRopus and Google results
		s1_aligned, p1_aligned, s3_aligned, p3_aligned = "", [], "", []
		s1_aligned, p1_aligned, s3_aligned, p3_aligned = align(s1, p1, s3, p3)

		if s1_aligned == "":
			print("ERROR: File " + filename + ". It was not possible to make the alignment between OCRopus' and Google's results.")
			i = i + 1
			continue		

		# Generate the consensus of the first and second aligned results
		s13, p13 = [], []
		s13, p13 = consensus_3( s1_aligned, p1_aligned, s3_aligned, p3_aligned, ocropus_stats, google_stats )

		if len(s13) == 0: # Something failed
			print("WARNING: File " + filename + ". It was not possible to reach consensus between OCRopus and GCP OCR.")
			i = i + 1
			continue

		# Check if all the probability are equal or greater than 1.0 and saves the new text and probability files
		verify_and_save( s13, p13, args.dstdir_a, filename, args.dstdir_r )

		i = i + 1

	######################################### 2 3 ################################################
	# Tesseract and Google
	######################################### 2 3 ################################################	
	i = 0
	while i<len(files_list23):
		# Read & load the content of the text and probability files
		filename = files_list23[i]
		s2, p2 = [], []
		s2, p2 = loadProbFile( args.input2 + "/" + filename )
		s3, p3 = [], []
		s3, p3 = loadProbFile( args.input3 + "/" + filename )

		n2 = len(s2)
		n3 = len(s3)

		# Validate the content: Check if it is different to empty
		if n2 < 1: # Tessetact generated just an empty file
			print("WARNING: Tesseract's output for line " + filename + " is empty or could not be read.")
			if n3 < 1: # Google's output is also empty
				print("ERROR: No OCR provided any result for line " + filename + ".")
			else:
				# The answer will be the Google's response (no consensus)
				verify_and_save( s3, p3, args.dstdir_a, filename, args.dstdir_r )
			i = i + 1
			continue
		if n3 < 1: # Google generated just an empty file
			print("WARNING: Google's output for line " + filename + " is empty or could not be read.")
			# The answer will be the Tesseract's response (no consensus)
			verify_and_save( s2, p2, args.dstdir_a, filename, args.dstdir_r )
			i = i + 1
			continue

		# Align the Tesseract and Google results
		s2_aligned, p2_aligned, s3_aligned, p3_aligned = "", [], "", []
		s2_aligned, p2_aligned, s3_aligned, p3_aligned = align(s2, p2, s3, p3)
		if s2_aligned == "":
			print("ERROR: File " + filename + ". It was not possible to make the alignment between Tesseract's and Google's results.")
			i = i + 1
			continue		

		# Generate the consensus of the first and second aligned results
		s23, p23 = [], []
		s23, p23 = consensus_3( s2_aligned, p2_aligned, s3_aligned, p3_aligned, tesseract_stats, google_stats )
		
		if len(s23) == 0: # Something failed
			print("WARNING: File " + filename + ". It was not possible to reach consensus between Tesseract and GCP OCR.")
			i = i + 1
			continue

		# Check if all the probability are equal or greater than 1.0 and saves the new text and probability files
		verify_and_save( s23, p23, args.dstdir_a, filename, args.dstdir_r )

		i = i + 1
