import numpy as np
from collections import defaultdict, Counter

class BCluster(object):

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
		print "Centroids initialized:"
		for i, cent in enumerate(init_centroids):
			self.centroids[i] = cent
		print self.centroids
		for i in xrange(self.iters):
			assignments = self._assign_points(X)
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
		centroid_pos = self.centroids.values()
		for i in xrange(X.shape[0]):
			distances = X[i][centroid_pos]
			print "Distances:", distances
			print "Assigning to:", np.argmax(distances)
			assignments.append(np.argmax(distances))
			a = raw_input().strip()
			if a == "c":
				break
		print "Returning Assignments:"
		print Counter(assignments)
		return np.array(assignments)

	def _move_centroids(self, X, assignments):
		'''
		input: X, 2d array
			    Assignments, 1d array
		output: new_centroids, dictionary
		'''
		new_centroids = {}
		#for i, centroid in enumerate(centroid):
		for i in range(self.n_clusters):
			cluster = X[assignments == i]
			avg_sims = [np.mean(row) for row in cluster]
			print "CLUSTER", i
			print "Greatest sim:", np.max(avg_sims)
			print "At index:", np.argmax(avg_sims)
			new_centroids[i] = np.argmax(avg_sims)
		print "Returning new centroids:"
		print new_centroids
		return new_centroids

		
