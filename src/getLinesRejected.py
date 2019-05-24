#!/usr/bin/env python3
##########################################################################################
# Developer: Icaro Alzuru         Project: HuMaIN (http://humain.acis.ufl.edu)
# Description: 
#   Rejects those lines which were only recognize by one OCR engine and their average 
# character probability is low (less than 0.4). The files also need to have 4 characters 
# or more for not being rejected.
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

#----------------------------------------------------------------------------------------------------------------------------------------------------------------
def getConfidence( probPathFilename ):
	""" Given a probabilities file: .prob, returns the number of symbols 
	and their average confidence.

	:type probPathFilename: string
	:param probPathFilename: 
	"""
	# Read file
	lines = []		# List of lines of the file
	with open( probPathFilename ) as f:
		lines = [line.rstrip() for line in f]

	# Compute the summation of the uncertainty
	sum = 0.0
	n = 0
	text = ""
	for line in lines:
		words = line.split('\t')
		if words[0] != ' ':
			text = text + words[0]
			if ( len(words) > 1 ):		
				sum = sum + float(words[1])
				n = n + 1

	if n == 0:
		return "", 0, 0.0
	else: 
		return text, n, sum/n

#----------------------------------------------------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
	""" Rejects those lines which were only recognize by one OCR engine and their average character probability is low (less than 0.4) 
	"""
	parser = argparse.ArgumentParser("Rejects those lines which were only recognize by one OCR engine and their average character probability is low (less than 0.7)")
	parser.add_argument('-i0', '--input0', action="store", required=True, help="Directory where the original images are located.")
	parser.add_argument('-i1', '--input1', action="store", required=True, help="Directory where the first probability files are located.")
	parser.add_argument('-i2', '--input2', action="store", required=True, help="Directory where the second group of probability files are located.")
	parser.add_argument('-i3', '--input3', action="store", required=True, help="Directory where the third group of probability files are located.")
	parser.add_argument('-o', '--output', action="store", required=True, help="Path and filename of the text file which will store the result and confidence in both directories.")
	args = parser.parse_args()

	# Arguments Validations
	if ( not os.path.isdir( args.input0 ) ):
		print('Error: The directory with the original lines was not found.\n')
		parser.print_help()
		sys.exit(1)

	if ( not os.path.isdir( args.input1 ) ):
		print('Error: The first directory of probability files was not found.\n')
		parser.print_help()
		sys.exit(1)

	if ( not os.path.isdir( args.input2 ) ):
		print('Error: The second directory of probability files was not found.\n')
		parser.print_help()
		sys.exit(1)

	if ( not os.path.isdir( args.input3 ) ):
		print('Error: The third directory of probability files was not found.\n')
		parser.print_help()
		sys.exit(1)

	# Create the lists of files to process
	files_list0 = list()
	for root, dirs, filenames in os.walk( args.input0 ):
		files_list0 = list(f[:-4] + ".prob" for f in filenames if f.endswith('.jpg'))
	n0 = len(files_list0)

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

	files_set0 = set( files_list0 )
	files_set1 = set( files_list1 )
	files_set2 = set( files_list2 )
	files_set3 = set( files_list3 )

	# Set of files with no value extracted in any OCR
	files_set_no_file = files_set0 - files_set1 - files_set2 - files_set3
	files_list_no_file = list(files_set_no_file)
	files_list_no_file.sort()
	
	# Set of probabilities files only present in the directory 1
	files_set_1_only = files_set1 - files_set2 - files_set3
	files_list_1_only = list(files_set_1_only)
	files_list_1_only.sort()

	# Set of probabilities files only present in the directory 2
	files_set_2_only = files_set2 - files_set1 - files_set3
	files_list_2_only = list(files_set_2_only)
	files_list_2_only.sort()

	# Set of probabilities files only present in the directory 3
	files_set_3_only = files_set3 - files_set1 - files_set2
	files_list_3_only = list(files_set_3_only)
	files_list_3_only.sort()

	with open(args.output, 'w') as f:
		i = 0
		while i<len(files_list_no_file):
			filename = files_list_no_file[i]
			s = filename + "\t0\t-1\t-1\t-1\t?\n"
			f.write( s )
			i = i + 1

		i = 0
		while i<len(files_list_1_only):
			filename = files_list_1_only[i]
			s1, l1, a1 = getConfidence( args.input1 + "/" + filename )
			if a1 < 0.7 or l1 < 4:
				s = filename + "\t" + str(l1) + "\t" + str(a1) + "\t-1\t-1\t" + s1 + "\n"
				f.write( s )
			i = i + 1

		i = 0
		while i<len(files_list_2_only):
			filename = files_list_2_only[i]
			s2, l2, a2 = getConfidence( args.input2 + "/" + filename )
			if a2 < 0.7 or l2 < 4:
				s = filename + "\t" + str(l2) + "\t-1\t" + str(a2) + "\t-1\t" + s2 + "\n"
				f.write( s )
			i = i + 1

		i = 0
		while i<len(files_list_3_only):
			filename = files_list_3_only[i]
			s3, l3, a3 = getConfidence( args.input3 + "/" + filename )
			if a3 < 0.7 or l3 < 4:
				s = filename + "\t" + str(l3) + "\t-1\t-1\t" + str(a3) + "\t" + s3 + "\n"
				f.write( s )
			i = i + 1
