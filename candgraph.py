import networkx as nx
import pandas as pd
import numpy as np
from itertools import combinations
from collections import Counter, defaultdict
from scipy import sparse
import timeit

class CandidateGraph():

	def __init__(self, directed = False):
		self.candsdf = pd.read_csv('../data/combined_memlist_14.csv')
		if directed:
			self.G = nx.DiGraph()
		else:
			self.G = nx.Graph()

	def build_nodes(self, display_type=False):
		'''
		Create nodes for the graph from dataframe

		input: none
		'''
		#self.G.add_nodes_from(df.RecipID.unique())
		for _, row in self.candsdf.iterrows():
			attrs = {'party': row.Party, 'cluster':row.Cluster, 'community':row.Community}
			if display_type:
				attrs['type'] = "Politician"
			self.G.add_node(row.ID, attrs)

	def build_multinodes(self, contr_df, voting_df = None):
		'''
		input: dataframe, contributions table
		'''
		# First, build the candidate nodes
		self.build_nodes(display_type = True)
		# Then, build the donor nodes...
		self.G.add_nodes_from(contr_df.ContribID.unique(), type='Donor')
		# Finally, build the vote nodes
		if voting_df:
			pass

	def build_edges_donor2cand(self, df, weight_by_dollaramt = False):
		'''
		Create edges for the graph, weighted by contribution amt

		input: dataframe
		'''
		
		#for _, row in df.iterrows():
		pass

		

	def build_edges_from_mat(self, donmatrix, weight_by_dollaramt = False):
		'''
		alternate method to build edges, from a sparse matrix

		input: donmatrix, sparse matrix
		'''
		if not weight_by_dollaramt:
			weight = 1
		for i in range(donmatrix.shape[0]):
			if i % 5000 == 0:
				print "Done {} of {}".format(i, donmatrix.shape[0])
			# gets the indices for the row that are nonzero
			nz_indices = donmatrix.getrowview(i).nonzero()[1]
			if len(nz_indices) <= 1:
				continue
			for cand_id1, cand_id2 in (combinations(nz_indices, 2)):
				canda = self.candidates[cand_id1]
				candb = self.candidates[cand_id2]
				if weight_by_dollaramt:
					am1 = donmatrix[i, cand_id1]
					am2 = donmatrix[i, cand_id2]
					weight = (am1 + am2) / 2
				if self.G.has_edge(canda, candb):
					self.G.edge[canda][candb]['weight'] += weight
				else:
					self.G.add_edge(canda, candb, weight = weight)

	def build_directed_from_mat(self, donmatrix, weight_by_dollaramt = False):
		'''
		Docstrings are for wimps.
		'''
		if not weight_by_dollaramt:
			weight = 1
		for i in range(donmatrix.shape[0]):
			if i % 500 == 0:
				print "Done {} of {}".format(i, donmatrix.shape[0])
			# get indicies of the row that are nonzero
			nz_indices = donmatrix.getrowview(i).nonzero()[1]
			donor = self.donors[i]
			# gather edges into an ebunch
			for cand_indx in nz_indices:
				cand = self.candidates[cand_indx]
				if weight_by_dollaramt:
					weight = donmatrix[i, cand_indx]
				self.G.add_edge(donor, cand, weight = weight)

			

	def build_sparse_donor_matrix(self, df, correction = True):
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
			donor_mat[donor_id_to_indx[row.ContribID], cand_id_to_indx[row.RecipID]] += float(am)
		print "Built matrix in {} seconds.".format(timeit.default_timer() - start_time)
		return donor_mat

	def print_cand_name(self, c_id):
		'''
		'''
		subdf = self.candsdf[self.candsdf.ID == c_id]
		return subdf.iloc[0]

	def print_cand_names(self, c_ids):
		'''
		input: candidate ids as list
		'''
		df = pd.DataFrame()
		for cand in c_ids:
			subdf = self.candsdf[self.candsdf.ID == cand]
			df = pd.concat([df, subdf])
		return df

	def girvan_newman_step(self, G):
		'''
		input: graph G
		output: graph G (with additional connected component)

		Runs one step of the Girvan-Newman community detection algorith
		The graph will have one more connected component
		'''
		original_ncomp = nx.number_connected_components(G)
		ncomp = original_ncomp
		while ncomp == original_ncomp:
			bw = Counter(nx.edge_betweenness_centrality(G, weight = 'weight'))
			a,b = bw.most_common(1)[0][0]
			G.remove_edge(a,b)
			ncomp = nx.number_connected_components(G)
		return G

	def find_communities(G):
		'''
		input: graph G, int n (number of steps)
		output: list of lists
		Run G-N algorith on G for N steps; return resulting communities.
		'''
		G1 = G.copy()
		for i in xrange(n):
			girvan_newman_step(G1)
		return list(nx.connected_components(G1))

	def get_centralities(G):
		'''
		'''
		d = pd.DataFrame.from_dict(nx.degree_centrality(G), orient='index')
		b = pd.DataFrame.from_dict(nx.betweenness_centrality(G, weight=None), orient='index')
		bw = pd.DataFrame.from_dict(nx.betweenness_centrality(G, weight='weight'), orient='index')
		e = pd.DataFrame.from_dict(nx.eigenvector_centrality(G, weight=None), orient='index')
		ew = pd.DataFrame.from_dict(nx.eigenvector_centrality(G, weight='weight'), orient='index')
		df = pd.concat([d, b, bw, e, ew], axis = 1)
		df.columns = ['Degree', 'Betweenness', 'BetweennessW', 'Eigen', 'EigenW']

		# fill nas?
