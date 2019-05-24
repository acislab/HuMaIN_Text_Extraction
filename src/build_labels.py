#!/usr/bin/env python3
##########################################################################################
# Developer: Icaro Alzuru         Project: HuMaIN (http://humain.acis.ufl.edu)
# Description: 
#   Using the final .txt files, after executing the Text Extraction process, this 
# program rebuilds the transcribed text for the images. 
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
import glob

#----------------------------------------------------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
	""" Using the final .txt files, after executing the Text Extraction process, this program rebuilds the transcribed text for the images.
	"""
	parser = argparse.ArgumentParser("Using the final .txt files, after executing the Text Extraction process, this program rebuilds the transcribed text for the images.")
	parser.add_argument('-r', '--reference', action="store", required=True, help="Directory with the original .jpg files of the collection.")
	parser.add_argument('-i', '--input', action="store", required=True, help="Directory where the .txt and .prob files are located.")
	parser.add_argument('-o', '--output', action="store", required=True, help="Destination directory where the labels will be copied.")
	args = parser.parse_args()

	# Arguments Validations
	if ( not os.path.isdir( args.reference ) ):
		print('Error: The directory of .jpg files was not found.\n')
		parser.print_help()
		sys.exit(-1)

	if ( not os.path.isdir( args.input ) ):
		print('Error: The input directory of probability and text files was not found.\n')
		parser.print_help()
		sys.exit(-2)

	if not os.path.exists( args.output ):
		try:
			os.makedirs( args.output )  
		except:
			print('Error: The destination directory was not found and could not be created.\n')
			parser.print_help()
			sys.exit(-3)

	# Create the list of jpg files to process
	filename_list = list()
	for root, dirs, filenames in os.walk( args.reference ):
		filename_list = list(f for f in filenames if f.endswith('.jpg'))

	# Execution
	for filename in filename_list:
		basename = filename[:-4]
		# List of text files generated for the image
		lines_list = glob.glob( args.input + "/" + basename + "*.txt")
		lines_list.sort()

		# Construction of the label
		label = ""
		i = 0  
		while i<len(lines_list):
			line_filename = lines_list[i]
			with open(lines_list[i]) as f_line:
				label += f_line.read() + "\n"
			i = i + 1
		if len(label)>0:
			label = label[:-1]
		
		label_filename = args.output + "/" + basename + ".txt"
		with open( label_filename, "w+") as f_label:
			f_label.write( label )
