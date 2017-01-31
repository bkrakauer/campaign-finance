import pandas as pd
import cPickle as pickle
import sys

def load_indivs(fn):
	'''
	input: filename as string (csv)
	output: dataframe 

	Loads dataframe and separates out the amount contributed column
	'''
	colnames = "Year XID ContribID Name RecipID Org UltOrg RealCode DateAmt Street City State Zip RecipCode Type CmteID OtherID Gender Microfilm Occupation Employer Source".split()
	df_inds = pd.read_csv(fn, names = colnames, header=None, delimiter='|', error_bad_lines=False)

	# eliminate rows with missing data for recip or candidate info
	blanks = (df_inds.ContribID.str.strip() == '') | (df_inds.RecipID.str.strip() == '')
	df_inds = df_inds[~blanks]
	df_inds = df_inds[df_inds.RecipID.str[0] == 'N'] # this subsets us to candidates
	df_inds['Amount'] = df_inds.DateAmt.apply(parse_amt)

	return df_inds

def parse_amt(col):
	'''
	Input: a string (in particular, an entry of the date/amount col)
	Output: Amount donated as int
	Splits the string, finds the amount column, and returns it as int
	(Plus some error handling for bad rows)
	'''
	amt = 0
	if isinstance(col, str):
		da = col.split(',')
		try:
			amt = int(da[1])
		except ValueError:
			print "Value error when converting {} to int".format(da[1])
			return amt
	else:
		print "Warning: couldn't split on", col
	return amt

def load_from_pickle(fn):
	'''
	input: filename as string
	output: dataframe

	Loads (cleaned) dataframe as pickle file
	'''
	df = pickle.load(open(fn, 'r'))
	return df

if __name__ == "__main__":
	fn = sys.argv[1]
	df = load_indivs(fn)
	#df2 = build_donor_matrix(df)
	#sparse_dm = build_matrix_pt(df)
	sparse_dm = build_sparse_donor_matrix(df) 