import os

import dash
import dash_core_components as dcc
import dash_html_components as html

import numpy as np
import pandas as pd
import networkx as nx
# import plotly.express as px
import plotly.graph_objects as go


##################

def visualdta(dir='dta.xlsx'):
    """

    """
    # read in data
    # df = pd.read_csv(dir, sep='\t', lineterminator='\r')
    df = pd.read_excel(dir)
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
            # deal with the P and T situation
            if not row['Responds To'] in ['n/a', 'N/A', 'na', 'NA', '', np.nan, 'unknown', 'UNKNOWN']:
                try:
                    # for propositions coded with pure number
                    cur_x = nodes[int(row['Responds To'])][0] + row.Distance
                except:
                    # in case of string proposition
                    cur_x = nodes[row['Responds To']][0] + row.Distance
                cur_y = df.Proposition.count() - idx
            else:
                # deal with the [B]reak situation
                # conveniently set the current point four units to the root
                cur_x = nodes[0][0] + row.Distance
                cur_y = df.Proposition.count() - idx

        node_x.append(cur_x)
        node_y.append(cur_y)
        nodes.update({row.Proposition: [cur_x, cur_y]})

    for (node, xy) in zip(nodes.keys(), list(zip(node_x, node_y))):
        graph.add_node(node, pos=(xy[0], xy[1]))

    # use df to trace positions
    df['pos'] = pd.Series(list(nodes.values()))

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
                # should raise some error to guide users [@TODO]
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

    node_trace_T = go.Scatter(
        # first entry + all T
        x=[df.iloc[0:1].pos[0][0]] + [x for [x, y] in df[df['Relation Type'] == 'T'].pos],
        y=[df.iloc[0:1].pos[0][1]] + [y for [x, y] in df[df['Relation Type'] == 'T'].pos],
        name='Narrowly on-topic (T)',
        mode='markers',
        hoverinfo='text',
        #     hovertext=annotations,
        marker=dict(
            showscale=False,
            #         colorscale='Viridis',
            #         reversescale=True,
            color='blue',
            size=8,
            line_width=2))

    node_trace_P = go.Scatter(
        # first entry + all T
        x=[x for [x, y] in df[df['Relation Type'] == 'P'].pos],
        y=[x for [x, y] in df[df['Relation Type'] == 'P'].pos],
        name='Parallel Shift (P)',
        mode='markers',
        hoverinfo='text',
        #     hovertext=annotations,
        marker=dict(
            showscale=False,
            #         colorscale='Viridis',
            #         reversescale=True,
            color='red',
            size=8,
            line_width=2))

    node_trace_B = go.Scatter(
        # first entry + all T
        x=[x for [x, y] in df[df['Relation Type'] == 'B'].pos],
        y=[x for [x, y] in df[df['Relation Type'] == 'B'].pos],
        name='Break (B)',
        mode='markers',
        hoverinfo='text',
        #     hovertext=annotations,
        marker=dict(
            showscale=False,
            #         colorscale='Viridis',
            #         reversescale=True,
            color='green',
            size=8,
            line_width=2))

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        name="responds to",
        line=dict(width=2, color='#888'),
        hoverinfo='none',
        mode='lines')

    # hoverlables = []

    annotations = [dict(
        x=df.iloc[i].pos[0],
        y=df.iloc[i].pos[1],
        hovertext=df.iloc[i].Speaker,
        xanchor='right',
        yanchor='bottom',
        text=df.iloc[i].Text,
        visible=True,
        showarrow=False)
        for i in range(df.shape[0])]

    fig = go.Figure(data=[edge_trace, node_trace_T, node_trace_P, node_trace_B],
                    layout=go.Layout(
                        title='Visual-DTA: A Demo',
                        titlefont_size=20,
                        showlegend=True,
                        hovermode='closest',
                        margin=dict(b=20, l=5, r=5, t=40),
                        annotations=annotations,
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=True),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=True))
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