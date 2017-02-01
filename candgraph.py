import networkx as nx
import pandas as pd
import numpy as np
from itertools import combinations
from collections import defaultdict
from scipy import sparse
import timeit
import pdb

class CandidateGraph():
	def __init__(self, min_connections = 10):
		self.min_connections = min_connections
		self.candsdf = pd.read_csv('data/combined_memlist_14.csv')
		self.G = nx.Graph()

	def build_nodes(self, df):
		'''
		Create nodes for the graph based on donors

		input: dataframe
		'''
		self.G.add_nodes_from(df.RecipID.unique())

	def build_edges(self, df, weight_by_dollaramt = False):
		'''
		Create edges for the graph, weighted by number of co-contributors

		input: dataframe
		'''


		# PANDAS/NUMPY VERSION:
		# cand_pairs = combinations(df.RecipID.unique(), 2)
		# for canda, candb in cand_pairs:
		# 	canda_donors = df[df.RecipID == canda].ContribID.unique()
		# 	candb_donors = df[df.RecipID == candb].ContribID.unique()
		# 	overlap = np.intersect1d(canda_donors, candb_donors).shape[0]
		# 	if overlap > 0:
		# 		print 'Adding Edge!', overlap
		# 		self.G.add_edge(canda, candb, weight = overlap)
			
		# SET VERSION:

		# canda_donors = set(df[df.RecipID == canda].ContribID)
		# candb_donors = set(df[df.RecipID == candb].ContribID)
		# overlap = len(canda_donors.intersection(candb_donors))
		# self.G.add_edge(canda, candb, weight=overlap)

		# By donor:
		total = len(df.ContribID.unique())
		for i, donor in enumerate(df.ContribID.unique()):
			if i % 1000 == 0:
				print '{} % complete!'.format(i * 1.0 / total)
			if weight_by_dollaramt:
				subdf = df[df.ContribID == donor]
			recipients = df[df.ContribID == donor].RecipID.unique()
			if len(recipients > 1):
				cand_pairs = combinations(recipients, 2)
				for canda, candb in cand_pairs:
					if weight_by_dollaramt:
						to_canda = np.sum(subdf[subdf.RecipID == canda].Amount)
						to_candb = np.sum(subdf[subdf.RecipID == candb].Amount)
						wt = np.mean([to_canda, to_candb])
					else:
						wt = 1
					if self.G.has_edge(canda, candb):
						self.G.edge[canda][candb]['weight'] += wt
					else:
						self.G.add_edge(canda, candb, weight = wt)

	def build_edges_from_mat(self, donmatrix, weight_by_dollaramt = False):
		'''
		alternate method to build edges, from a sparse matrix

		input: donmatrix, sparse matrix
		'''
		for i in range(donmatrix.shape[0]):
			if i % 500 == 0:
				print "Done {} of {}".format(i, donmatrix.shape[0])
			# gets the indices for the row that are nonzero
			nz_indices = donmatrix.getrowview(i).nonzero()[1]
			if len(nz_indices) <= 1:
				continue
			for cand_id1, cand_id2 in (combinations(nz_indices, 2)):
				canda = self.candidates[cand_id1]
				candb = self.candidates[cand_id2]
				if self.G.has_edge(canda, candb):
					self.G.edge[canda][candb]['weight'] += 1
				else:
					self.G.add_edge(canda, candb, weight = 1)

			

	def build_sparse_donor_matrix(self, df, binary = False, correction = True):
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
			am = row.Amount
			if correction:
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

	def print_cand_name(self, c_id):
		'''
		'''
		subdf = self.candsdf[self.candsdf.ID == c_id]
		return subdf.FirstName + ' ' + subdf.LastName + ', ' + subdf.State
