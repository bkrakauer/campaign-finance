import networkx as nx
import pandas as pd
import numpy as np
from itertools import combinations

class CandidateGraph():
	def __init__(self, min_connections = 10):
		self.min_connections = min_connections
		self.G = nx.Graph()

	def build_nodes(self, df):
		'''
		Create nodes for the graph based on donors

		input: dataframe
		'''
		self.G.add_nodes_from(df.RecipID.unique())

	def build_edges(self, df):
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
			recipients = df[df.ContribID == donor].RecipID.unique()
			if len(recipients > 1):
				cand_pairs = combinations(recipients, 2)
				for canda, candb in cand_pairs:
					if self.G.has_edge(canda, candb):
						self.G.edge[canda][candb]['weight'] += 1
					else:
						self.G.add_edge(canda, candb, weight = 1)

	def print_cand_name(self, cand_df):
		'''
		'''
		return cand_df[cand_df[2] == '|' + node.format() + '|'][3].values