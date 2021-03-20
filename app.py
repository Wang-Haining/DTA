import os

import dash
import dash_core_components as dcc
import dash_html_components as html

import pandas as pd
import networkx as nx
# import plotly.express as px
import plotly.graph_objects as go


##################

def visualdta(io='IM-conv.txt'):
    """

    """
    # read in data
    df = pd.read_csv(io, sep='\t', lineterminator='\r')
    # construct a graph
    graph = nx.Graph()
    # infer x, y coordinates from data
    node_x = []
    node_y = []
    # used to holds nodes' attributes
    nodes = {}

    for idx, row in df.iterrows():
        # root
        if idx == 0:
            cur_x = 1
            cur_y = df.Proposition.count()
        # tree
        else:
            cur_x = nodes[row['Responds To']][0] + row.Distance
            cur_y = df.Proposition.count() - idx
        node_x.append(cur_x)
        # should be more robust
        node_y.append(cur_y)
        nodes.update({row.Proposition: [cur_x, cur_y]})
    # add nodes to graph with its desired position
    for (node, xy) in zip(nodes.keys(), list(zip(node_x, node_y))):
        graph.add_node(node, pos=(xy[0], xy[1]))

    # add nodes' other attributes
    # should fill in n/a TODO
    for node in nodes.keys():
        for attr in list(df.columns):
            graph.nodes[node][attr] = df[df.Proposition == node][attr]

    # find edges and dotted edges
    # don't know how to incorporate dotted edges TODO
    # use edge attributes (https://networkx.org/documentation/stable/tutorial.html)
    edges = []
    #     edges_dotted = []
    for idx1, row1 in df.iterrows():
        for idx2, row2 in df.iterrows():
            if row1.Proposition == row2['Responds To'] and row2['Dotted Line'] in [0, 'yes', 'y', 'Yes', 'YES', 'Y']:
                graph.add_edge(row1.Proposition, row2.Proposition, dotted=False)
            #                 edges.append((row1.Proposition, row2.Proposition))
            elif row1.Proposition == row2['Responds To'] and row2['Dotted Line'] in [1, 'no', 'n', 'No', 'NO', 'N']:
                graph.add_edge(row1.Proposition, row2.Proposition, dotted=True)
            #                 edges_dotted.append((row1.Proposition, row2.Proposition))
            else:
                # should raise some error to guide users TODO
                pass

    graph.add_edges_from(edges)

    edge_x = []
    edge_y = []
    for edge in graph.edges():
        x0, y0 = graph.nodes[edge[0]]['pos']
        x1, y1 = graph.nodes[edge[1]]['pos']
        edge_x.append(x0)
        edge_x.append(x1)
        #     edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
    #     edge_y.append(None)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            # colorscale options
            # 'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
            # 'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
            # 'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
            colorscale='Viridis',
            reversescale=True,
            color=[],
            size=10,
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            ),
            line_width=2))

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title='Visual-DTA',
                        titlefont_size=16,
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20, l=5, r=5, t=40),
                        annotations=[dict(
                            text="Python code: <a href='hhttps://github.com/Wang-Haining/VisualDTA'> https://github.com/Wang-Haining/VisualDTA/</a>",
                            showarrow=False,
                            xref="paper", yref="paper",
                            x=0.005, y=-0.002)],
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
    return fig

##################


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

# app.layout = html.Div([
#     html.H2('VisualDTA'),
#     dcc.Dropdown(
#         id='dropdown',
#         options=[{'label': i, 'value': i} for i in ['.csv', '.xlsx']],
#         value='csv'
#     ),
#     html.Div(id='display-value')
# ])

app.layout = html.Div([
    dcc.Graph(figure=visualdta())
])


# @app.callback(dash.dependencies.Output('display-value', 'children'),
#               [dash.dependencies.Input('dropdown', 'value')])
# def display_value(value):
#     return 'You have selected "{}"'.format(value)

if __name__ == '__main__':
    app.run_server(debug=True)




# import os
#
# import dash
# import dash_core_components as dcc
# import dash_html_components as html
#
# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#
# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
#
# server = app.server
#
# app.layout = html.Div([
#     html.H2('VisualDTA'),
#     dcc.Dropdown(
#         id='dropdown',
#         options=[{'label': i, 'value': i} for i in ['.csv', '.xlsx']],
#         value='csv'
#     ),
#     html.Div(id='display-value')
# ])
#
# @app.callback(dash.dependencies.Output('display-value', 'children'),
#               [dash.dependencies.Input('dropdown', 'value')])
# def display_value(value):
#     return 'You have selected "{}"'.format(value)
#
# if __name__ == '__main__':
#     app.run_server(debug=True)