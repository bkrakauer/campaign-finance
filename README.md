# Democracy Dollars: An Investigation of the Influence of Money in Congress

## Introduction
This project is an attempt to make use of campaign finance data to generate insights about the ideology and voting behavior of membes of Congress. I used data from campaign contributions (both from individuals and from committees) to cluster candidates into groups based on the similarity of their sources and amounts of campaign contributions, and determine whether membership in these groups determine anything about voting behavior. I then developed graphs of politicians and donors to determine whether we can determine anything about their behavior from these networks.

## Clustering

![TSNE Plot](https://github.com/bkrakauer/campaign-finance/raw/master/images/tsne-similarity.png)

This plot is a representation of the clusters that were discovered in the campaign finance data. Note how many clusters appear to be relatively homogeneous by party; these clusters tend to form ideologically consistent groupings of representatives, and representatives generally vote with their clusters 90% of the time or more. A large clutser, however, remains mixed; this cluster seems to represent politicians in leadership positions, and who have a broader (and more consistent) base of financial support. It is impossible to draw conclusions about the ideology or voting behavior of this large, heterogeneous cluster.

To create these clusters, I built a sparse matrix with each column representing a donor, and each row representating a candidate. I then reduced the dimensionality of this data in several ways, including Non-negative Matrix Factorization and subsetting the matrix to only include donors who have donated to a large number of politicians. I then created a second matrix that represented the pairwise cosine similarity of candidates to one another; the above plot is a TSNE representation of this matrix into two dimensions. An interactive version of this plot which shows the identities of each politician is also available.

## Network

![Candidate-Candidate Network](https://github.com/bkrakauer/campaign-finance/raw/master/images/graph1.png)

I then used this data to create graphs to represent the relations between and among politicians. Above is a force-directed (Fruchterman-Reingold) graph where the nodes represent politicians (color-coded by party), and the edges between nodes are weighted by the mean contributions from a donor or committee who has given to both candidates.

![Donor-Candidate Network](https://github.com/bkrakauer/campaign-finance/raw/master/images/graph2.png)

Above is another force-directed graph; this is a directed graph where the grey nodes are contributors, and the red and blue nodes are politicians. In this graph, we can see that not only do the Democrats and Republicans naturally separate from one another, but we can begin to see some separations within the parties, which will allow for a more fine-grained analysis.

## Future Work

Further analysis of these networks could reveal communities within the parties. I have already begun this analysis, using both Louvain as well as Girvan-Newman community detection.

We can also use facts about centrality to determine the behavior of politicians. For example, I have determined that Eigenvector centrality can be used to predict the percentage of time a politician votes with her party (p-value approaches zero).

## Data Sources

OpenSecrets

Propublica

Federal Election Commission

## Contact
bkrakauer@gmail.com
