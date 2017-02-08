import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import sys
import json
import pdb


headers = {'X-API-Key': ''}

def build_member_list(cong):
	'''
	Input: Number of congress (as string)
	Output: Dictionary, keys are IDs and values are name, state, and party
	'''
	reps = {}
	url = "https://api.propublica.org/congress/v1/{}/house/members.json".format(cong)
	r = requests.get(url, headers = headers)
	j = json.loads(r.content)
	for member in j['results'][0]['members']:
		fname = member['first_name']
		lname = member['last_name']
		state = member['state']
		party = member['party']
		m_id = member['id']
		reps[m_id] = [fname, lname, state, party]
	return reps


def get_one_byapi(year, url, billnum, members):
	'''
	Input: Year, url, bill number: strings
	       Members: dictionary
	Output: 2d-list of results for one bill
	'''
	print "Getting results for {}...".format(billnum)
	r = requests.get(url, headers = headers)
	if r.status_code != 200:
		print "Failure!"
		print r.status_code
		return None
	escaped_content = r.content.replace("\\&", "") # json can't handle ampersands
	escaped_content = escaped_content.replace("\r", "")
	escaped_content = escaped_content.replace("\n;", "")
	j = json.loads(escaped_content)
	if not 'results' in j:
		return None
	votes = j['results']['votes']['vote']['positions']
	results = []
	for vote in votes:
		#pdb.set_trace()
		m_id = vote['member_id'] 
		fname = members[m_id][0]
		lname = members[m_id][1]
		state = members[m_id][2]
		party = members[m_id][3]
		vote = vote['vote_position']
		results.append([year, fname, lname, state, party, vote, billnum])
	return results


def run_loop(cong, session, year, maxbill, members):
	''' 
	input: congress number, session number, year, number of bills for session; all as strings
	        members dataframe
	output: dataframe of year's results
	'''
	vote_list = []
	url = "https://api.propublica.org/congress/v1/{}/house/sessions/{}/votes/".format(cong, session)
	for i in range(1, int(maxbill)+1):
		billnum = str(i)
		vote_url = url + billnum + ".json"
		bill_results = get_one_byapi(year, vote_url, billnum, members)
		if bill_results:
			vote_list.extend(bill_results)
	r_df = pd.DataFrame(vote_list, columns = ["Year", "FirstName", "LastName", "State", "Party", "Vote", "Billnum"])
	return r_df

if __name__ == "__main__":
	year = sys.argv[1]
	cong = sys.argv[2]
	session = sys.argv[3]
	maxbill = sys.argv[4]
	politicians = build_member_list(cong)
	df = run_loop(cong, session, year, maxbill, politicians)
	out_filename = year + "_housealt_rv.csv"
	df.to_csv(out_filename, encoding = 'utf-8')



