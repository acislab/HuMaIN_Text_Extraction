#!/usr/bin/env python
##########################################################################################
# Developer: Icaro Alzuru         Project: HuMaIN (http://humain.acis.ufl.edu)
# Description: 
#   Run tesseract over all the images of an specified folder.
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

import sys, os, argparse, re
import multiprocessing
from tesserocr import PyTessBaseAPI, RIL, iterate_level

CORES_N = multiprocessing.cpu_count() - 1
IMGS_DIR = ""
CONF_DIR = ""
TEXT_DIR = ""
##############################################################################################################################################################
def tesseract( filename ):
	# OCR - use the Tesseract API through Cython and PyTesseract
	with PyTessBaseAPI() as api:
		pathFilename = IMGS_DIR + "/" + filename

		label_text = ""
		ri = None
		try:
			# Set the image 
			api.SetImageFile( pathFilename )			
			# Run and verify the recognition process
			label_text = api.GetUTF8Text()
			label_text = label_text[:-1]		
			api.SetVariable("save_blob_choices", "T")
			api.Recognize()
			ri = api.GetIterator()
		except:
			return

		conf_text = ""
		# Iterate over each of the symbols of the file 
		level = RIL.SYMBOL
		for r in iterate_level(ri, level):
			try:
				symbol = r.GetUTF8Text(level)
				conf = 0.01 * r.Confidence(level)

				# We only save non-break symbols
				if (symbol not in ['\n','\r','\t','\f']):
					conf_text += symbol + "\t" + str(conf) + "\n"
			except:
				continue

		if len(conf_text) > 0:
			basename = filename[:-4]
			# Write all the characters and their Confidence in the probabilities file
			conf_pathFilename = CONF_DIR + "/" + basename + ".prob"
			with open(conf_pathFilename, "w") as f:
				f.write( conf_text.encode('utf-8') )

			# Write the recognized text line in the text file
			text_pathFilename = TEXT_DIR + "/" + basename + ".txt"
			with open(text_pathFilename, "w") as f:
				f.write( label_text.encode('utf-8') )

##############################################################################################################################################################
if __name__ == '__main__':
	""" Run tesseract over all the images of an specified folder.
	"""
	parser = argparse.ArgumentParser("Run tesseract over all the images of an specified folder.")
	parser.add_argument('-id', '--imgs_dir', action="store", required=True, help="Input folder, where jpg images are stored.")
	parser.add_argument('-td', '--text_dir', action="store", required=True, help="Folder where text files will be stored.")
	parser.add_argument('-cd', '--conf_dir', action="store", required=True, help="Folder where confidence files will be stored.")
	args = parser.parse_args()

	# Arguments Validations
	if ( not os.path.isdir( args.imgs_dir ) ):
		print('Error: The directory of the jpg files was not found.\n')
		parser.print_help()
		sys.exit(1)

	if not os.path.exists( args.text_dir ):
		try:
			os.makedirs( args.text_dir )  
		except:
			print('Error: The directory for the text files was not found and could not be created.\n')
			parser.print_help()
			sys.exit(2)

	if not os.path.exists( args.conf_dir ):
		try:
			os.makedirs( args.conf_dir )  
		except:
			print('Error: The directory for the confidence files was not found and could not be created.\n')
			parser.print_help()
			sys.exit(3)

	IMGS_DIR = args.imgs_dir
	TEXT_DIR = args.text_dir
	CONF_DIR = args.conf_dir

	# Create the list of files to process
	filename_list = list()
	for root, dirs, filenames in os.walk( IMGS_DIR ):
		filename_list = list(f for f in filenames if f.endswith('.jpg'))

	# Pool handler
	p = multiprocessing.Pool( CORES_N )
	p.map( tesseract, filename_list )
