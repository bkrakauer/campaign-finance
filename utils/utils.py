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

def load_committees(fn):
	'''
	input: filename as string (csv)
	output: dataframe
	'''
	colnames = "Year XID ContribID RecipID Amount Date A B C D".split()
	df_ctes = pd.read_csv(fn, names=colnames, header=None, delimiter=",", error_bad_lines=False)
	blanks = (df_ctes.ContribID.str.strip() == '') | (df_ctes.RecipID.str.strip() == '')
	df_ctes = df_ctes[~blanks]
	df_ctes = df_ctes[df_ctes.RecipID.str[0] == 'N'] # this subsets us to candidates

	#calculate "amount" column
	#df_ctes['Amount'] = df_ctes.AmtDate.apply(parse_amt, args=(True,))
	return df_ctes

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

def subset_by_amt(df, min_contributions):
	'''
	Subset list to only inlcude donors with enough contributions
	'''
	donor_counter = Counter(df.ContribID)
	donors = [donor for donor in donor_counter.keys() if donor_counter[donor] > min_contributions]
	df = df[df.ContribID.isin(donors)]
	return df

def subset_to_winners(df, winnersdf):
	'''
	input: dataframe (contributions)
		   dataframe (includes winners only)
    output: dataframe (df subsetted to winners only)
	'''
	winners = winnersdf.ID
	msk = df.RecipID.isin(winners)
	return df[msk]

def add_ids_to_votes(row, mems):
	'''
	Input: Series, row of voting data
	       Dataframe, member info
	Output: str, Member ID
	'''
	subdf = mems[(mems.LastName == row.LastName) & (mems.State == row.State)]
	if len(subdf) != 1:
		#print "falling back on firstnames...", row
		subdf = subdf[(mems.FirstName == row.FirstName)]
		return subdf.ID.iloc[0]
	else:
		#print "Matched!"
		return subdf.ID.iloc[0] 

def add_clusters_to_votingdf(membersdf, votingdf):
	'''
	Input: Dataframe, dataframe (members list and voting records)
	Output: Dataframe (voting list with added col for group)
	'''
	id_to_cluster = {id_: gr for id_, gr in membersdf.Cluster.iteritems()}
	votingdf['Cluster'] = votingdf.ID.apply(lambda x: id_to_cluster[x])
	return votingdf


if __name__ == "__main__":
	fn = sys.argv[1]
	candlistfn = sys.argv[2]
	df = load_indivs(fn)
	df = subset_to_winners(df, candlistfn)
	