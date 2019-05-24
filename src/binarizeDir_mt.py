#!/usr/bin/env python3
##########################################################################################
# Developer: Icaro Alzuru         Project: HuMaIN (http://humain.acis.ufl.edu)
# Description: 
#   Using OCROPY, this script binarizes the jpg images in a folder 
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
import multiprocessing

# DIR_OCROPY = 
CORES_N = multiprocessing.cpu_count()

if __name__ == '__main__':
	""" MAIN 
	"""
	parser = argparse.ArgumentParser("Using OCROPY, this script binarizes the jpg images in a folder")
	parser.add_argument('-if', '--input_folder', action="store", required=True, help="Directory with the jpg files to be binarized.")
	parser.add_argument('-of', '--output_folder', action="store", required=True, help="Directory where the binarized images will be saved.")
	args = parser.parse_args()

	# Arguments Validations
	if ( not os.path.isdir( args.input_folder ) ):
		print('Error: The directory of the jpg files was not found.\n')
		parser.print_help()
		sys.exit(1)

	if not os.path.exists( args.output_folder ):
		try:
			os.makedirs(args.output_folder)  
		except:
			print('Error: The destination directory was not found and could not be created.\n')
			parser.print_help()
			sys.exit(2)	

	for root, dirs, filenames in os.walk( args.input_folder ):
		files = list(f for f in filenames if f.endswith('.jpg'))
		# commands = [DIR_OCROPY + "/ocropus-nlbin -n " + args.input_folder + "/" + f + " -o " + args.output_folder + "/" + f[:-4] for f in files]
		commands = ["ocropus-nlbin -n " + args.input_folder + "/" + f + " -o " + args.output_folder + "/" + f[:-4] for f in files]

		processes = (Popen(cmd, shell=True) for cmd in commands)
		running_processes = list(islice(processes, CORES_N))  # start new processes
		while running_processes:
			for i, process in enumerate(running_processes):
				if process.poll() is not None:  # the process has finished
					running_processes[i] = next(processes, None)  # start new process
					if running_processes[i] is None: # no new processes
						del running_processes[i]
						break
