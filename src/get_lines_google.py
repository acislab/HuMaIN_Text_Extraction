#!/usr/bin/env python
##########################################################################################
# Developer: Icaro Alzuru         Project: HuMaIN (http://humain.acis.ufl.edu)
# Description: 
#   Given an image, it uses the Google Cloud Vision API output to extract the text in lines. 
# In a folder, the cropped lines in jpg format, as well as their correspond extracted text.
# In a summary output file, the list of cropped lines and their coordinated are stored.
# PRE-REQUISITE: (Google Credentials). Run something like the following to indicate the user 
# and project that will be used in the Google Cloud:
#       export GOOGLE_APPLICATION_CREDENTIALS="/home/user/Google/credential_file.json"
#       (Install the Google Cloud Vision python libraries)
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
from enum import Enum
from google.cloud import vision
from google.cloud.vision import types
from PIL import Image
breaks = vision.enums.TextAnnotation.DetectedBreak.BreakType

#----------------------------------------------------------------------------------------------------------------------------------------------------------------
def crop_save(  img_path_filename, lines_boxes, lines_texts, lines_probs, filename, basename, output_dir_name ):
	""" Crop and save the image for each line, its text files, and its probabilities files. It also returns the bbox statistics.
	"""
	# Read the image
	image = Image.open( img_path_filename )
	# Get image's  size
	width, height = image.size

	i = 0
	text_local = ""
	text_global = ""
	while i < len(lines_boxes):
		##################################################################################################
		# Left Upper Corner
		x1 = lines_boxes[i][0]
		x1 = x1 - 8
		if x1 < 0:
			x1 = 0

		y1 = lines_boxes[i][1]
		y1 = y1 - 1
		if y1 < 0:
			y1 = 0

		# Right Lower Corner
		x2 = lines_boxes[i][2]
		x2 = x2 + 10
		if x2 > (width - 1):
			x2 = width - 1

		y2 = lines_boxes[i][3]
		y2 = y2 + 1
		if y2 > (height - 1):
			y2 = height - 1

		# Crop the block and save it
		n_line = "%03d" % (i+1)
		line_filename = output_dir_name + "/" + basename + "_" + n_line + ".jpg"		

		img_cropped = image.crop( (x1, y1, x2, y2) )
		img_cropped.save( line_filename, 'JPEG', quality = 100 )

		##################################################################################################
		# Create the information about the cropped line for the local and global text files
		text_line = basename + "_" + n_line + ".jpg\t" + str(x1) + "\t" + str(y1) + "\t" + str(x2) + "\t" + str(y2) + "\t" + ''.join(lines_texts[i]) + "\n"
		text_local += text_line
		text_global += filename + "\t" + text_line

		##################################################################################################
		# Creation of the text and probability file for each line
		j = 0
		content_text_file = ""
		content_prob_file = ""
		while j<len(lines_texts[i]):
			content_text_file += lines_texts[i][j]
			content_prob_file += lines_texts[i][j] + '\t' + str(lines_probs[i][j]) + '\n'
			j = j + 1
		# Write to disk the text file
		text_filename = output_dir_name + "/" + basename + "_" + n_line + ".txt"
		with open( text_filename, "w+" ) as f_text:
			f_text.write( content_text_file )
		# Write to disk the probabilities file
		prob_filename = output_dir_name + "/" + basename + "_" + n_line + ".prob"
		with open( prob_filename, "w+" ) as f_prob:
			f_prob.write( content_prob_file )

		i = i + 1

	return( text_local, text_global )

#----------------------------------------------------------------------------------------------------------------------------------------------------------------
def process_paragraph( paragraph ):
	""" The function will return lists of bounding boxes, lines' text, and lines' probabilities
	"""
	# Lists of bounding boxes, text, and probabilities
	line_box_list = []
	line_text_list = []
	line_prob_list = []

	# Line under processing
	current_line_text = []
	current_line_prob = []
	# Bounding box temporary variables
	x1 = 100000
	y1 = 100000
	x2 = 0
	y2 = 0

	for word in paragraph.words:
		for symbol in word.symbols:
			# x1, y1 (Left upper corner)
			if symbol.bounding_box.vertices[0].x < x1:
				x1 = symbol.bounding_box.vertices[0].x
			if symbol.bounding_box.vertices[0].y < y1:
				y1 = symbol.bounding_box.vertices[0].y
			if symbol.bounding_box.vertices[1].y < y1: 
				y1 = symbol.bounding_box.vertices[1].y
			if symbol.bounding_box.vertices[3].x < x1:
				x1 = symbol.bounding_box.vertices[3].x
			# x2, y2 (right lower corner)
			if symbol.bounding_box.vertices[2].x > x2:
				x2 = symbol.bounding_box.vertices[2].x
			if symbol.bounding_box.vertices[2].y > y2:
				y2 = symbol.bounding_box.vertices[2].y
			if symbol.bounding_box.vertices[1].x > x2:
				x2 = symbol.bounding_box.vertices[1].x
			if symbol.bounding_box.vertices[3].y > y2:
				y2 = symbol.bounding_box.vertices[3].y

			current_line_text.append( symbol.text )
			current_line_prob.append( symbol.confidence )
			# Check for blank spaces
			if symbol.property.detected_break.type in [ breaks.SPACE, breaks.SURE_SPACE ]:
				current_line_text.append( ' ' )
				current_line_prob.append( 0.95 )
			# Check for new lines
			if symbol.property.detected_break.type in [ breaks.EOL_SURE_SPACE, breaks.HYPHEN, breaks.LINE_BREAK ]:
				line_box_list.append( [x1, y1, x2, y2] )
				line_text_list.append( current_line_text )
				line_prob_list.append( current_line_prob )
				# Line under processing
				current_line_text = []
				current_line_prob = []
				# Bounding box temporary variables
				x1 = 100000
				y1 = 100000
				x2 = 0
				y2 = 0

	return( line_box_list, line_text_list, line_prob_list )

#----------------------------------------------------------------------------------------------------------------------------------------------------------------
def process_image( img_path_filename, output_dir_name, output_path_filename):
	""" Crop the text paragraphs and save the information about the cropped files
	"""
	########################### Google OCR #############################
	client = vision.ImageAnnotatorClient()

	lines_boxes_img = []
	lines_texts_img = []
	lines_probs_img = []

	# Path + Base name for the block files
	filename = img_path_filename.split('/')[-1]
	basename = filename.split('.')[0]

	content = None
	with io.open( img_path_filename, 'rb' ) as image_file:
		content = image_file.read()

	try:
		# Process image and recognize its parts and text
		image = types.Image( content=content )
		response = client.document_text_detection(image=image)
		document = response.full_text_annotation

		fulltext_path_filename = output_dir_name + "/" + basename + ".txt"	
		# Save all the extracted text in a text file
		with open( fulltext_path_filename,'w') as f:
			f.write( response.full_text_annotation.text )

		# Collect the lines, their probabilities, and their bounding boxes
		for page in document.pages:
			for block in page.blocks:
				for paragraph in block.paragraphs:
					# Divide the paragraph in lines and get its lines, bounding boxes, and symbols' probabilities
					lines_boxes_par, lines_texts_par, lines_probs_par = process_paragraph( paragraph )
					# Extend the line lists
					lines_boxes_img.extend( lines_boxes_par )
					lines_texts_img.extend( lines_texts_par )
					lines_probs_img.extend( lines_probs_par )
	except Exception as e:
		print("Error: " + img_path_filename + ", " + str(e))
		return

	# Crop and save the image for each paragraph, its text files, and its probabilities files. It also returns the bbox statistics.
	text_local, text_global = "", ""
	text_local, text_global = crop_save( img_path_filename, lines_boxes_img, lines_texts_img, lines_probs_img, filename, basename, output_dir_name )

	# Save the bounding box information in the local and in the global file
	if text_global != "":
		# Save the data of the lines in the local text file
		with open(output_dir_name + "/" + basename + "_lines.csv", "w+") as f:
			f.write( text_local )

		# Save the data of the lines in the global text file
		with open(output_path_filename, "a+") as f:
			f.write( text_global )

#----------------------------------------------------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
	""" Extract the lines from a image (jpg) file using Google Cloud Text Detection.
	"""
	parser = argparse.ArgumentParser("Extract the lines from a image (jpg) file using Google Cloud Text Detection.")
	parser.add_argument('-if', '--input_file', action="store", required=True, help="Path + Filename of the jpg image to crop in blocks.")
	parser.add_argument('-od', '--output_dir', action="store", required=True, help="Directory where the images of the cropped blocks will be saved.")
	parser.add_argument('-of', '--output_file', action="store", required=True, help="Path + Filename of the text file which will save the coordinates of the cropped lines.")
	args = parser.parse_args()

	# Arguments Validations
	if ( not os.path.isfile( args.input_file ) ):
		print("Error: The image (" + args.input_file + ") file was not found.\n")
		parser.print_help()
		sys.exit(1)

	if not os.path.exists( args.output_dir ):
		try:
			os.makedirs( args.output_dir )  
		except:
			print('Error: The destination directory was not found and could not be created.\n')
			parser.print_help()
			sys.exit(2)

	# Crop the blocks and save the information about the cropped files
	process_image(args.input_file, args.output_dir, args.output_file)
