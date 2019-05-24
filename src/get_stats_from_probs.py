#!/usr/bin/env python3
##########################################################################################
# Developer: Icaro Alzuru         Project: HuMaIN (http://humain.acis.ufl.edu)
# Description: 
#   Generates basic statistics about the probability value of each symbol found in all 
# the .prob files of a directory.
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

import argparse, os, sys, csv
import pandas as pd
import numpy as np

#----------------------------------------------------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
	""" Generates basic statistics about the probability value of each symbol found in all the .prob files of a directory. 
	"""
	parser = argparse.ArgumentParser("Generates basic statistics about the probability value of each symbol found in all the .prob files of a directory. ")
	parser.add_argument('-d', '--dir', action="store", required=True, help="Directory where the probability files are located.")
	parser.add_argument('-o', '--output', action="store", required=True, help="Path and filename of the text file which will store the statistics of each symbol.")
	args = parser.parse_args()

	# Arguments Validations
	if ( not os.path.isdir( args.dir ) ):
		print('Error: The directory with the probability files was not found.\n')
		parser.print_help()
		sys.exit(1)

	# Create the lists of files to process
	files_list = list()
	for root, dirs, filenames in os.walk( args.dir ):
		files_list = list(f for f in filenames if f.endswith('.prob'))

	symbol_dict = {} 
	for filename in files_list:
		path_filename = args.dir + "/" + filename
		# Dataframe of the probability file
		df = None
		try:
			df = pd.read_csv( path_filename, sep="\t", header=None, engine='python', encoding='utf8', quoting=csv.QUOTE_NONE )
			df.fillna(' ')
		except:
			print("Encoding error at: " + path_filename)
			sys.exit(2)

		for index, row in df.iterrows():
			symbol = str(row[0])[0]
			probability = float(row[1])
			
			try:
				list_values = symbol_dict[ symbol ]
				list_values.append( probability )
			except KeyError:
				symbol_dict[ symbol ] = [ probability ]

	with open( args.output, "w+" ) as f:
		for symbol in list( symbol_dict.keys() ):
			list_values = np.array( symbol_dict[ symbol ] ).astype(float)
			try:
				s = symbol + "\t" + str(list_values.mean()) + "\t" + str(np.median(list_values)) + "\t" + str(list_values.std()) + "\t" + str(len(list_values)) + "\n"
			except: 
				print("Symbol: " + s)
				print(list_values)
			f.write( s )
