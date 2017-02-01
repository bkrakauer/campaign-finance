import pandas as pd
import cPickle as pickle
from collections import Counter
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

	#calcuate "amount" columns.
	df_inds['Amount'] = df_inds.DateAmt.apply(parse_amt)

	return df_inds

def parse_amt(col, committee = False):
	'''
	Input: a string (in particular, an entry of the date/amount col)
	Output: Amount donated as int
	Splits the string, finds the amount column, and returns it as int
	(Plus some error handling for bad rows)
	'''
	position = 1
	if committee:
		position = 0
	amt = 0
	if isinstance(col, str):
		da = col.split(',')
		try:
			amt = int(da[position])
		except ValueError:
			print "Value error when converting {} to int".format(da[position])
			return amt
	else:
		print "Warning: couldn't split on", col
	return amt

def subset_by_amt(df, min_contributions):
	'''
	Subset list to only inlcude donors with enough contributions
	'''
	donor_counter = Counter(df.ContribID)
	donors = [donor for donor in donor_counter.keys() if donor_counter[donor] > min_contributions]
	df = df[df.ContribID.isin(donors)]
	return df

def subset_to_winners(df, candlistfn):
	win_df = pd.read_csv(candlistfn)
	winners = win_df.ID
	msk = df.RecipID.isin(winners)
	return df[msk]


if __name__ == "__main__":
	fn = sys.argv[1]
	candlistfn = sys.argv[2]
	df = load_indivs(fn)
	df = subset_to_winners(df, candlistfn)
	