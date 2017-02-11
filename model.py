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
		self.candsdf = pd.read_csv('../data/combined_memlist_14.csv')

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
		return (kmc.predict(self.cand_sim_matrix), kmc.score(self.cand_sim_matrix))

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


	def build_sparse_donor_matrix(self, df, correction = False):
		'''
		Input: DataFrame, as contribiution df
		output: sparse lil matrix, rows = donors, cols = candidates
		'''
		df = df[["ContribID", "RecipID", "Amount"]]
		start_time = timeit.default_timer()
		self.donors = df.ContribID.unique()
		self.candidates = df.RecipID.unique()
		donor_id_to_indx = {donor: pos for pos, donor in enumerate(self.donors)}
		cand_id_to_indx = {cand: pos for pos, cand in enumerate(self.candidates)}
		donor_mat = sparse.lil_matrix((len(self.donors), len(self.candidates)))
		for _, row in df.iterrows():
			am = float(row.Amount)
			if correction:
				if am > 2600:
					am = 2600
				elif am < 0:
					am = 0
			else:
				donor_mat[donor_id_to_indx[row.ContribID], cand_id_to_indx[row.RecipID]] += am
		print "Built matrix in {} seconds.".format(timeit.default_timer() - start_time)
		return donor_mat
	

	def print_cand_names(self, c_ids):
		'''
		input: candidate ids as list
		output: dataframe, subsetted to candidate id
		'''
		df = pd.DataFrame()
		for cand in c_ids:
			subdf = self.candsdf[self.candsdf.ID == cand]
			df = pd.concat([df, subdf])
		return df


