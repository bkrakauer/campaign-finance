from __future__ import division
import pandas as pd
from scipy.stats import mode
import numpy as np
import pdb

def get_votes_with_group_full(dfs):
	'''
	input: list of dataframes
	output: dataframe 
	'''
	vwpavg = pd.concat(dfs, axis = 1)
	vwpavg['combined'] = vwpavg.apply(lambda x: np.mean(x), axis=1)
	return [vwpavg.combined]


def get_votes_with_group_yr(df, type_of_group = "Party"):
	'''
	Calculates the percent of time in which a candidate votes with her group

	input: roll call vote dataframe
	output: dictionary of politicians: vote pct
	'''
	maxbill = df.Billnum.max()
	votingrates = {}
	voting_results = group_voting_by_bill(df, type_of_group)
	for cand_id, subdf in df.groupby('ID'):
		group = subdf[type_of_group].iloc[0]
		results = []
		if np.isnan(group):
			continue
		#some one-off code to handle independents who caucaus with D
		if group == "I":
			group = "D"
		for bill in xrange(maxbill + 1):
			billdf = subdf[subdf.Billnum == bill]
			if billdf.shape[0] != 0:
				vote = billdf.Vote.iloc[0]
				if vote == voting_results.get(bill, {}).get(group):
					results.append(1)
				else:
					results.append(0)
			else:
				results.append(np.nan)
		votingrates[cand_id] = results
	resultsdf = pd.DataFrame.from_dict(votingrates, orient="index")
	resultsdf["pct"] = resultsdf.apply(lambda row: np.mean(row), axis=1)
	return resultsdf["pct"]

def group_voting_by_bill(df, type_of_group = "Party"):
	'''
	Calculates, for each bill, how each group (e.g. party or cluster) voted

	input: roll call vote dataframe
	output: dictionary of dictionaries, of which key is billnum and vals are party votes
	'''

	colname = type_of_group
	results = {}
	bills = df.Billnum.unique()
	for bill in bills:
		billresults = {}
		subdf = df[df.Billnum == bill]
		#How did each group vote?
		groups = sorted(subdf[colname].unique())
		for i, group in enumerate(groups):
			if np.isnan(group):
				continue
			groupdf = subdf[subdf[colname] == group]
			groupmode, _ = mode(groupdf.Vote)
			billresults[i] = groupmode[0]
		results[bill] = {gr: result for gr, result in billresults.iteritems()}

	return results