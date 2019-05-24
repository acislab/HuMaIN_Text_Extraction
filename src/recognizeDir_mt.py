#!/usr/bin/env python
##########################################################################################
# Developer: Icaro Alzuru         Project: HuMaIN (http://humain.acis.ufl.edu)
# Description: 
#   Using OCROPY, runs the recognition script on the binarized images of a folder.
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
from subprocess import Popen
from itertools import islice

DIR_OCROPY = "/home/user/ocropy"
N_THREADS = 6

#----------------------------------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------------------------
def txtRecognize_folder( images_dir, models_dir, model_filename, with_prob ):
	for root, dirs, filenames in os.walk( images_dir ):
		files = list(f for f in filenames if f.endswith('.png'))
		commands = []
		command = 'export PYTHONIOENCODING="UTF-8";export OCROPUS_DATA=' + models_dir + ";"
		if with_prob:
			commands = [ command + DIR_OCROPY + "/ocropus-rpred -n --probabilities -q -m " + model_filename + " " + images_dir + "/" + f for f in files ]
		else:
			commands = [ command + DIR_OCROPY + "/ocropus-rpred -n -q -m " + model_filename + " " + images_dir + "/" + f for f in files ]

		processes = (Popen(cmd, shell=True) for cmd in commands)
		running_processes = list(islice(processes, N_THREADS))  # start new processes
		while running_processes:
			for i, process in enumerate(running_processes):
				if process.poll() is not None:  # the process has finished
					running_processes[i] = next(processes, None)  # start new process
					if running_processes[i] is None: # no new processes
						del running_processes[i]
						break
						
#----------------------------------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
	""" MAIN """
	parser = argparse.ArgumentParser("Using OCROPY, runs the recognition script on the binarized images of a folder")
	parser.add_argument('-if', '--images_folder', action="store", required=True, help="Directory with the .bin.png files to be recognized.")
	parser.add_argument('-mf', '--model_folder', action="store", required=True, help="Directory where the OCR model is stored.")
	parser.add_argument('-mn', '--model_name', action="store", required=True, help="Filename of the OCR model to use during the recognition process.")
	parser.add_argument('-p', '--probabilities', action="store", required=True, help="Include the probabilities file or not: True or False.")	
	args = parser.parse_args()

	# Arguments Validations
	if ( not os.path.isdir( args.images_folder ) ):
		print('Error: The directory of the .bin.png files was not found.\n')
		parser.print_help()
		sys.exit(1)
	if ( not os.path.isdir( args.model_folder ) ):
		print('Error: The directory of the model was not found.\n')
		parser.print_help()
		sys.exit(2)
	if ( not os.path.isfile( args.model_folder + "/" + args.model_name) ):
		print('Error: The model file was not found.\n')
		parser.print_help()
		sys.exit(3)
	if ( args.probabilities != "True" ) and ( args.probabilities != "False" ):
		print('Error: The probabilities values must be True or False.\n')
		parser.print_help()
		sys.exit(4)

	with_prob = False
	if args.probabilities == "True":
		with_prob = True
		
	txtRecognize_folder( args.images_folder, args.model_folder, args.model_name, with_prob )

