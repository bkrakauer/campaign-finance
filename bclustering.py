import numpy as np
from collections import defaultdict

class BCluster(obect):

'''
1. Pick n candidates randomly to be centroids.
2. Assign each candidate to "nearest" centroid -- 
    that is, the centroid with the greatest pairwise similarity score 
3. Pick a new centroid (candidate or point) as the "midpoint" -- 
    for each cluster, pick every candidate and calculate the average (squared?)
    cosine similarity. 
'''

	def __init__(self, iters = 100, n_clusters = 5, error = 'squared'):
		self.iters = iters
		self.n_clusters = n_clusters
		self.error = error

	def fit(self, X):
		'''
		Input: X, a square cosine similarity matrix
		'''
		# initialize centroids randomly
		self.centroids = {}
		init_centroids = np.random.choice(range(X.shape[0]), size = self.n_clusters)
		for i, cent in enumerate(init_centroids):
			self.centroids[i] = cent
		for i in xrange(self.iters):
			assignments = self._assign_points(X, clusters)
			new_centroids = self._move_centroids(X, assignments)
			if new_centroids == self.centroids:
				break
			else:
				self.centroids = new_centroids

	def _assign_points(self, X):
		'''
		input: X, 2d np array
				clusters, dictionary
		output: assignments, 1d array
		For each centroid, calculates list
		'''
		assignments = []
		centroid_pos = self.centoids.values()
		for i in xrange(X.shape[0]):
			distances = X[i][centroid_pos]
			assignments.append(np.argmax(distances))
		return np.array(assignments)

	def _move_centroids(self, X, assignments):
		'''
		input: X, 2d array
			    Assignments, 1d array
		output: new_centroids, dictionary
		'''
		new_centroids = {}
		for i, centroid in enunerate(centroid):
			cluster = X[assignments == i]
			avg_sims = [np.mean(row) for row in cluster]
			new_centroids[i] = np.argmax(avg_sims)
		return new_centroids

		
