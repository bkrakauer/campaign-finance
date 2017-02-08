import pandas as pd
import csv
import pdb
import sys

def parse_cols(infn, outfile = "test.txt"):
	'''
	input: filenames as strings
	output: none
	writes cleaned file (with | delimiter) to disk
	'''

	with open(infn) as f:
		contents = f.readlines()
	outfile = open(outfile, "w")
	for i, line in enumerate(contents):
		newline = []
		buffer_ = ""
		col_flag = False
		for char in line:
			if not ((char == ",") and (buffer_ == "")):
				# don't add to the buffer if we're a comma starting an entry 
				buffer_ += char
			if char == "|":
				if not col_flag:
					#mark that we're beginning an entry!
					col_flag = True
				else:
					#mark that we're done with an entry!
					col_flag = False
					buffer_ = buffer_.replace("|", "")
					newline.append(buffer_) 
					buffer_ = ""
		#if len(newline) != 21:
		#	print "Warning: line {} has {} entries!".format(i, len(newline))
		outfile.write(",".join(newline) + "\n") 
		#wait = raw_input()
	outfile.close()


if __name__ == "__main__":
	infn = sys.argv[1]
	outfn = sys.argv[2]
	parse_cols(infn, outfn)