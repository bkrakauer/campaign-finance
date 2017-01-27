import pandas as pd
import numpy as np
from scipy import sparse
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans

class CampaignFinModel():
	def __init__(self, year = 2014):
		self.year = year

	def fit(self, df):
		'''
		input: DataFrame, in format of contributions for one year
		Computes similarity matrix
		'''
		s_donation_matrix = self.build_sparse_donor_matrix(df)
		print "Built Donation Matrix..."
		self.n_donors, self.n_cands = s_donation_matrix.shape
		self.cand_sim_matrix = cosine_similarity(s_donation_matrix.T)
		print "Built Candidate Similarity Matrix..."
		# sort each candidate by the index of whoever's most similar to them...
		self.sorted_sims = np.argsort(self.cand_sim_matrix, 1)

	def cluster(self, n_clusters = 5):
		'''
		input: int, number of clusters
		output: tuple of kmeans clusters and score
		'''
		kmc = KMeans(n_clusters = n_clusters)
		kmc.fit(self.cand_sim_matrix)
		return (kmc.predict(self.cand_sim_matrix), kmc.score)

	def build_sparse_donor_matrix(self, df):
		'''
		Input: DataFrame, as contribiution df
		output: sparse lil matrix, rows = donors, cols = candidates
		'''
		df = df[["ContribID", "RecipID", "Amount"]]
		self.donors = df.ContribID.unique()
		self.candidates = df.RecipID.unique()
		donor_id_to_indx = {donor: pos for pos, donor in enumerate(self.donors)}
		cand_id_to_indx = {cand: pos for pos, cand in enumerate(self.candidates)}
		donor_mat = sparse.lil_matrix((len(self.donors), len(self.candidates)))
		for _, row in df.iterrows():
			donor_mat[donor_id_to_indx[row.ContribID], cand_id_to_indx[row.RecipID]] += row.Amount
		# make it a df?
		return donor_mat

	def get_candidate_name(self, indx):
		'''
		'''
		cand_id = self.candidates[indx]
		candsdf = pd.read_csv('data/cands14.txt', header=None, error_bad_lines=False, warn_bad_lines=False)
		cand_id = "|" + cand_id + "|"
		return candsdf[candsdf[2] == cand_id][3]




'''
1. Pick n candidates randomly to be centroids.
2. Assign each candidate to "nearest" centroid -- 
    that is, the centroid with the greatest pairwise similarity score 
3. Pick a new centroid (candidate or point) as the "midpoint" somehowsomehow. 
'''