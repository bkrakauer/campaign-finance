from sklearn.manifold import TSNE
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mpld3
from mpld3 import plugins


def run_TSNE(X, party_seq):
	'''
	Generates TSNE plot from matrix 
	input: X: numpy matrix
		   party_seq: list of party membership of candidates

	output: matplotlib axes

	party_seq = [dfwinners.loc[cand].Party for cand in c.candidates]
	'''
	plt.style.use('fivethirtyeight')
	party_colors = {"D": "blue", "I": "blue", "R": "red"}
	tsm = TSNE(n_components = 2)
	tsm = tsm.fit_transform(X)
	plt.scatter(tsm[:,0], tsm[:,1], c=[party_colors[x] for x in party_seq])
	plt.title('Candidate - Candidate Similarity')
	plt.show()

def simple_interactive_plot(X, candidates, memberlist, party_seq = []):
	'''
	Produces an mpld3 plot that displays the entry number of the politician

	input: numpy matrix, list of candidates, dataframe of members and ids
	output: none

	'''
	party_colors = {"D": "blue", "I": "blue", "R": "red"}
	tsm = TSNE(n_components = 2)
	tsm = tsm.fit_transform(X)
	fig, ax = plt.subplots()
	ax.grid(True, alpha=.5)
	labels = []
	for i, member in enumerate(candidates):
		c_id = str(i)
		c_name = memberlist.loc[member].LastName
		labels.append(c_id + " " + c_name)
	points = ax.plot(tsm[:,0], tsm[:,1], 'o', color = 'b')
	tooltip = plugins.PointHTMLTooltip(points[0], labels)
	plugins.connect(fig, tooltip)
	#mpld3.show()
	return fig, tooltip

def interactive_plot(X, candidates, memberlist, party_seq = []):
    '''
    Produces an mpld3 plot that displays the entry number of the politician

    input: numpy matrix, list of candidates, dataframe of members and ids
    output: none

    '''
    party_colors = {"D": 'b', "I": 'b', "R": 'r'}
    colorseq = [party_colors[x] for x in party_seq]
    tsm = TSNE(n_components = 2)
    tsm = tsm.fit_transform(X)
    fig, ax = plt.subplots()
    ax.grid(True, alpha=.5)
    labels = []
    for i, member in enumerate(candidates):
        label = memberlist[["LastName", "Party"]].loc[member].to_frame()
        label.columns = ["Row {}".format(i)]
        labels.append(label.to_html())
    points = ax.plot(tsm[:,0], tsm[:,1], 'o', color = 'b')
    tooltip = plugins.PointHTMLTooltip(points[0], labels, css=css)
    plugins.connect(fig, tooltip)
    return fig, tooltip

css = '''
table
{
  border-collapse: collapse;
}
th
{
  color: #ffffff;
  background-color: #000000;
}
td
{
  background-color: #cccccc;
}
table, th, td
{
  font-family:Arial, Helvetica, sans-serif;
  text-align: right;
}
'''