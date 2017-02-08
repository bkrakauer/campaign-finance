import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import sys
import json
import pdb


headers = {'X-API-Key': ''}

def build_member_list(session, cong, df_wids):
	'''
	Input: Number of congress (as string)
	Output: Dictionary, keys are IDs and values are name, state, and party
	'''
	pols = {}
	url = "https://api.propublica.org/congress/v1/{}/{}/members.json".format(session, cong)
	r = requests.get(url, headers = headers)
	print r.status_code
	j = json.loads(r.content)
	for i, member in enumerate(j['results'][0]['members']):
		fname = member['first_name']
		lname = member['last_name']
		state = member['state']
		party = member['party']
		#votes_w_party = member['votes_with_party_pct']
		m_id = get_member_id(fname, lname, state, party, df_wids)
		pols[i] = [m_id, fname, lname, state, party]
	df = pd.DataFrame.from_dict(pols, orient="index")
	df.columns = ["ID", "FirstName", "LastName", "State", "Party"]
	return df


def get_id_df(year):
	'''
	Loads dataframe containing candidate ID's
	input: year, two digits 
	output: dataframe
	'''
	fn = "../data/cands" + str(year) + ".txt"
	candsdf = pd.read_csv(fn, header=None, error_bad_lines=False, warn_bad_lines=False)
	candsdf = candsdf[[2,3,4]]
	candsdf.columns = ["ID", "Name", "Party"]
	candsdf.ID = candsdf.ID.str.replace("|", "")
	candsdf.Name = candsdf.Name.str.replace("|", "")
	candsdf.Party = candsdf.Party.str.replace("|", "")
	candsdf['SplitName'] = candsdf.Name.apply(lambda x: x.split()[:-1])
	return candsdf

def get_member_id(fname, lname, state, party, df_wids):
	'''
	'''
	msk = df_wids.SplitName.apply(lambda x: fname in x and lname in x)
	if np.sum(msk) < 1:
		try:
			print "{} {} from {} {} not found; ".format(fname,lname, party, state)
		except UnicodeEncodeError:
			print "Unicode Error ...."
			#print "Error decoding {} {}".format(fname, lname).decode("utf8", errors='ignore')
		msk = df_wids.SplitName.apply(lambda x: lname in x)
	try:
		m_df = df_wids[msk]# .iloc[0].ID
		print m_df
		print "Enter the index of the entry to select for", fname, lname, state, party
		indx = raw_input().strip()
		try:
			indx = int(indx)
		except:
			indx = 0
		m_id = m_df.iloc[indx].ID
		return m_id
	except IndexError:
		return None

if __name__ == "__main__":
	year = sys.argv[1]
	session = sys.argv[2]
	cong = sys.argv[3]
	out_filename = sys.argv[4]
	cand_df = get_id_df(year)
	df = build_member_list(session, cong, cand_df)
	df.to_csv(out_filename, encoding = 'utf-8')



