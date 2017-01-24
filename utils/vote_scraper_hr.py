import requests
from bs4 import BeautifulSoup
import pandas as pd
import sys

'''
Quick and dirty scraper for House website.
To do: implelement multithreading
       generalize!
'''

BASEURL = "http://clerk.house.gov/evs/"


def get_one_rc(url, year, billnum):
	'''
	Input: url (string), billnum (string with leading zeros)
	Output: 2d list of voting results for one bill

	Generates list of votes for one bill
	'''
	url = BASEURL + str(year) + "/roll" + billnum + ".xml"
	print "Getting results for {}...".format(billnum)
	r = requests.get(url)
	if r.status_code == 200:
		r = r.content
	else:
		print "Error", year, billnum, r.status_code
		return None
	s = BeautifulSoup(r, 'html.parser')
	results = []
	votes = s.find_all("recorded-vote")
	for record in votes:
		name = record.legislator.string
		state = record.legislator["state"]
		party = record.legislator["party"]
		vote = record.vote.string
		results.append([year, name, state, party, vote, billnum])
	return results

def run_loop(year = 2014, maxbill = 564):
	'''
	Input: maxbill number for a session, as strings
	Output: dataframe 

	Generates dataframe of voting behavior for a legislatibe sessions
	'''
	vote_list = []
	for i in range(1, int(maxbill)+1):
		billnum = "%03d" %(i)
		vote_list.extend(get_one_rc(BASEURL, year, billnum))
	r_df = pd.DataFrame(vote_list, columns = ["Year", "Name", "State", "Party", "Vote", "Billnum"])
	return r_df

if __name__ == "__main__":
	year = sys.argv[1]
	maxbill = sys.argv[2]
	outfilename = sys.argv[1] + "_house_rv.csv"
	df = run_loop(year, maxbill)
	df.to_csv(outfilename, encoding = 'utf-8')



