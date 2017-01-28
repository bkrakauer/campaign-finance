import pandas as pd
import numpy as np
from scipy import sparse
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import NMF
import timeit

class CampaignFinModel():
	def __init__(self, year = 2014):
		self.year = year
		fn = "data/cands" + str(year - 2000) + ".txt"
		self.candsdf = pd.read_csv(fn, header=None, error_bad_lines=False, warn_bad_lines=False)

	def fit(self, df):
		'''
		input: DataFrame, in format of contributions for one year
		Computes similarity matrix
		'''
		self.s_donation_matrix = self.build_sparse_donor_matrix(df)
		print "Built Donation Matrix..."
		#self.n_donors, self.n_cands = s_donation_matrix.shape
		self.cand_sim_matrix = cosine_similarity(self.s_donation_matrix.T)
		print "Built Candidate Similarity Matrix..."
		# sort each candidate by the index of whoever's most similar to them...
		#self.sorted_sims = np.argsort(self.cand_sim_matrix, 1)

	def kmcluster(self, n_clusters = 5):
		'''
		input: int, number of clusters
		output: tuple of kmeans clusters and score
		'''
		kmc = KMeans(n_clusters = n_clusters)
		kmc.fit(self.cand_sim_matrix)
		return (kmc.predict(self.cand_sim_matrix), kmc.score)

	def dbcluster(self, X, eps = .5, min_samples = 20):
		'''
		Input: epsilon, min samples (ints)
		Output: series of predictions from dbscan
		'''
		dbc = DBSCAN(eps = eps, min_samples = min_samples)
		return pd.Series(dbc.fit_predict(X))

	def run_nmf(self, n_components = 5, source = "similarity"):
		'''
		Input: number of clusters (int), donation or similarity mat (str)
		Output: Resulting matrix with NMF reduction
		Given some number of custers
		'''
		#first, eliminate negative values
		nmf = NMF(n_components = n_components)
		if source == "donation":
			pos_donation_matrix = self.s_donation_matrix[self.s_donation_matrix < 0] = 0
			return nmf.fit_transform(self.s_donation_matrix)
		else:
			pos_cand_sim_matrix = self.cand_sim_matrix + 1
			return nmf.fit_transform(pos_cand_sim_matrix)

		# We can topic model with :
		#nmf_sim_res = pd.Series([np.argmax(nmf_sim[i,:]) for i in xrange(nmf_sim.shape[0])])


	def build_sparse_donor_matrix(self, df, binary = False, correction = True):
		'''
		Input: DataFrame, as contribiution df
		output: sparse lil matrix, rows = donors, cols = candidates

		Also consider a version that just adds ones, instead of amt!!
		'''
		df = df[["ContribID", "RecipID", "Amount"]]
		start_time = timeit.default_timer()
		self.donors = df.ContribID.unique()
		self.candidates = df.RecipID.unique()
		donor_id_to_indx = {donor: pos for pos, donor in enumerate(self.donors)}
		cand_id_to_indx = {cand: pos for pos, cand in enumerate(self.candidates)}
		donor_mat = sparse.lil_matrix((len(self.donors), len(self.candidates)))
		for _, row in df.iterrows():
			am = row.Amount
			if correction and (not binary):
				if am > 2600:
					am = 2600
				elif am < 0:
					am = 0
			if binary:
				donor_mat[donor_id_to_indx[row.ContribID], cand_id_to_indx[row.RecipID]] = 1
			else:	
				donor_mat[donor_id_to_indx[row.ContribID], cand_id_to_indx[row.RecipID]] += row.Amount
		# Try a version that adds through subsetting by unique candidates...
		print "Built matrix in {} seconds.".format(timeit.default_timer() - start_time)
		# Iterrows run: 308/314 seconds.
		return donor_mat

	def get_candidate_name(self, indx):
		'''
		Input: index, as integer
		Output: Name of candidate
		'''
		cand_id = self.candidates[indx]
		cand_id = "|" + cand_id + "|"
		return self.candsdf[self.candsdf[2] == cand_id][3]




'''
1. Pick n candidates randomly to be centroids.
2. Assign each candidate to "nearest" centroid -- 
    that is, the centroid with the greatest pairwise similarity score 
3. Pick a new centroid (candidate or point) as the "midpoint" somehowsomehow.

Try NMF, offset by some scalar to get positive values 
'''