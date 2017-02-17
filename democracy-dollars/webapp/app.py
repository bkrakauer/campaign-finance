from flask import Flask, request, render_template
import pandas as pd
import cPickle as pickle
import mpld3
import matplotlib.pyplot as plt
from mpld3 import plugins
from unidecode import unidecode

app = Flask(__name__)

homepage = '''
<html>
<body>
<h2> Hey dar! </h2>
<a href="/submit">A link!</a>
</body>
</html>
'''

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

# home page
@app.route('/')
def index():
    '''
    Displays index template
    '''
    winnersdf, memberlist = pickle.load(open('winnersdf_cands.pkl', 'r'))
    lastnames = [unicode(x, errors='replace') for x in winnersdf.LastName]
    firstnames = [unicode(x, errors='replace') for x in winnersdf.FirstName]
    names = zip(firstnames, lastnames)
    names = [str(i) + ': ' +n[0] + ' ' + n[1] for i, n in enumerate(names)]
    return render_template('index.html', politicians = names)


@app.route('/show_tsne', methods=['POST'])
def show_tsne():
    '''
    Displays mpld3 plot of selected canddiate in similarity space

    input: results from form
    '''
    pol = (str(request.form['politician']))
    polnum = int(pol.split()[0][:-1])
    mtrx = pickle.load(open('tsne_matrix.pkl', 'r'))
    winnersdf, memberlist = pickle.load(open('winnersdf_cands.pkl', 'r'))
    winnersdf.iloc[polnum, 3] = 'S' # change the party label to 'S'
    party_seq = [winnersdf.loc[cand].Party for cand in memberlist]
    fig, tooltip = interactive_plot(mtrx, winnersdf, memberlist, party_seq)
    plugins.connect(fig, tooltip)
    graph = mpld3.fig_to_html(fig=fig)
    return graph


def interactive_plot(tsm, winnersdf, memberlist, party_seq = []):
    '''
    Produces an mpld3 plot that displays the entry number of the politician
    
    input: numpy matrix, dataframe of candidates and ids, list of member ids
    output: none

    '''
    party_colors = {'D': 'b', 'I': 'b', 'R': 'r', 'S': 'g'}
    colorseq = [party_colors[x] for x in party_seq]
    fig, ax = plt.subplots()
    ax.grid(True, alpha=.5)
    labels = []
    for i, member in enumerate(memberlist):
        label = winnersdf[["LastName", "Party"]].loc[member].to_frame()
        label.columns = ["Row {}".format(i)]
        labels.append(label.to_html())
    points = ax.scatter(tsm[:,0], tsm[:,1], c = colorseq)
    tooltip = plugins.PointHTMLTooltip(points, labels, css=css)
    return fig, tooltip

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
