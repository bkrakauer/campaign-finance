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

def build_donor_matrix(df):
	'''
	input: Dataframe of campaign contributios
	output: matrix of contributors x donors (eventually)

	side effect: writes a pickle file of the dictionary
	'''

	df = df[["ContribID", "RecipID", "Amount"]]
	donors = df.ContribID.unique()
	candidates = df.RecipID.unique()
	cand_dict = {}
	total = len(candidates)
	for i, candidate in enumerate(candidates):
		print "Computing {} of {}...".format(i, total)
		subdf = df[df.RecipID == candidate].groupby('RecipID').sum()
		cand_dict[candidate] = [subdf.loc[donor].Amount if donor in subdf.index else 0 for donor in donors]
	pickle.dump(cand_dict, open("cand_dict.pkl", "w"))

	# for i, donor in enumerate(donors):
 #    for j, candidate in enumerate(candidates):
 #        amt = np.sum(indiv_14[(indiv_14.ContribID == donor) & (indiv_14.RecipID == candidate)].Amount)
 #        if amt > 0:
 #            cont_matrix[i][j] = amt
        

if __name__ == "__main__":
	fn = sys.argv[1]
	df = load_indivs(fn)
	build_donor_matrix(df)
