#!/usr/bin/env python3
##########################################################################################
# Developer: Icaro Alzuru         Project: HuMaIN (http://humain.acis.ufl.edu)
# Description: 
#   Opens, resizes, and saves, using opencv, the jpg found files in a directory.
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
import cv2 as cv
import multiprocessing

CORES_N = multiprocessing.cpu_count() - 1
SRC_DIR = ""
DST_DIR = ""
PERCENT = 71.0

#----------------------------------------------------------------------------------------------------------------------------------------------------------------
def resizeImg ( filename ):
	""" Opens a png file and saves it with a different size, in a differnt folder. 
	"""
	src_filename = SRC_DIR + "/" + filename
	dst_filename = DST_DIR + "/" + filename
	# Load the image
	image = cv.imread( src_filename, cv.IMREAD_UNCHANGED)
	# New size
	width = int(image.shape[1] * PERCENT / 100.0)
	height = int(image.shape[0] * PERCENT / 100.0)
	# Resize
	image = cv.resize( image, (width, height))
	# Find the barcodes in the image and decode them
	cv.imwrite( dst_filename, image, [int(cv.IMWRITE_JPEG_QUALITY), 100])

#----------------------------------------------------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
	""" Opens, resizes, and saves, using opencv, the jpg found files in a directory. 
	"""
	parser = argparse.ArgumentParser("Opens and saves, using opencv, the png found files in a directory.")
	parser.add_argument('-i', '--input', action="store", required=True, help="Directory where the png images are located.")
	parser.add_argument('-o', '--output', action="store", required=True, help="Directory where the new version of the images will be saved.")
	args = parser.parse_args()

	# Arguments Validations
	if ( not os.path.isdir( args.input ) ):
		print('Error: The directory of the png files was not found.\n')
		parser.print_help()
		sys.exit(1)

	if not os.path.exists( args.output ):
		try:
			os.makedirs( args.output )  
		except:
			print('Error: The destination directory was not found and could not be created.\n')
			parser.print_help()
			sys.exit(2)

	SRC_DIR = args.input
	DST_DIR = args.output

	# Create the list of files to process
	filename_list = list()
	for root, dirs, filenames in os.walk( SRC_DIR ):
		filename_list = list(f for f in filenames if f.endswith('.jpg'))

	# Pool handler
	p = multiprocessing.Pool( CORES_N )
	p.map( resizeImg, filename_list )
