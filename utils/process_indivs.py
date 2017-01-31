import pandas as pd
import csv
import pdb
import sys

def load_file(fn, outname = "test.txt"):
	'''
	input: filename as string
	output: boolean (on success)

	(NOTE: This function is deprecated!)
	'''
	with open(fn) as f:
		contents = f.readlines()
	f = open(outname, 'w')
	for line in contents:
		line = line.split('|,|')
		#if len(line) < 17:
			#print "Not enough cols!"
			#pdb.set_trace()
		line[0] = line[0][1:] #stips off the leading pipe
		spl7 = line[7].split(',') # this line is actually realcode, date, amount
		if spl7 == ['CAPITOLA']:
			print [a + "\n" for a in line]
		# consider dropping this line if we can't get minimal info....
		line[7] = spl7[0] #over-write the over-loaded line with realcode
		line[6] = spl7[1] # over-write ultorg with with date
		line[1] = spl7[2] #over-write FEC-ID with amount
		outline = "\t".join(line) + "\n" #makes this a tsv
		f.write(outline)
	f.close()
	return True

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
					buffer_.replace("|", "")
					newline.append(buffer_[1:-1]) # maybe change this instead of top if?
					buffer_ = ""
		#if len(newline) != 21:
		#	print "Warning: line {} has {} entries!".format(i, len(newline))
		outfile.write("|".join(newline) + "\n") 
		#wait = raw_input()
	outfile.close()


if __name__ == "__main__":
	infn = sys.argv[1]
	outfn = sys.argv[2]
	parse_cols(infn, outfn)