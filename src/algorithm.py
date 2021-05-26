"""
Author: Haining Wang hw56@indiana.edu
"""

import io
import base64
import warnings
import numpy as np
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
warnings.simplefilter("ignore")

# reduced fool-proof
UNKNOWN = ['n/a', 'N/A', 'na', 'NA', '', np.nan, 'unknown', 'UNKNOWN', '?', '??', "???"]
YES = [1, 'yes', 'y', 'Yes', 'YES', 'Y']
NO = [0, 'no', 'n', 'No', 'NO', 'N']


class DTA(object):
    """
    DTA class is used to do the heavy lifting on https://visual-dta.herokuapp.com/.
    """

    def __init__(self, df):
        # construct a dataframe to hold user input
        self.df = df
        # construct a graph
        self.graph = nx.Graph()
        # hold nodes' position
        self.nodes = {}
        # edges
        # self.edges = []
        # self.edges_dotted = []
        self.edge_x = []
        self.edge_y = []
        self.edge_dotted_x = []
        self.edge_dotted_y = []


    # def read_in_uploaded(self, contents, filename):
    #     """
    #     TODO
    #     Supports reading in three formats:
    #         Comma-separated values(.csv)
    #         tab-delimited text (.txt), and
    #         excel (.xlsx).
    #
    #     :param filename:
    #     :param contents:
    #     :return: a pd.DataFrame instance
    #     """
    # # def parse_data_upload(contents, filename):
    #     content_type, content_string = contents.split(',')
    #     decoded = base64.b64decode(content_string)
    #     try:
    #         if "csv" in filename:
    #             # Assume that the user uploaded a CSV or TXT file
    #             self.df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
    #         elif "xls" in filename:
    #             # Assume that the user uploaded an excel file
    #             self.df = pd.read_excel(io.BytesIO(decoded))
    #         elif "txt" or "tsv" in filename:
    #             # Assume that the user upl, delimiter = r'\s+'oaded an excel file
    #             self.df = pd.read_csv(io.StringIO(decoded.decode("utf-8")), delimiter=r"\s+")
    #     except:
    #         pass
    #
    # def read_in_demo(self,
    #                  filepath='./samples/BiliBili_comments.xlsx',
    #                  filename='BiliBili_comments.xlsx'):
    #     """
    #     TODO
    #     Supports reading in three formats: Comma-separated values(.csv),tab-delimited text (.txt), and excel (.xlsx).
    #     :param filename:
    #     :param filepath:
    #     :return: a pd.DataFrame instance
    #     """
    #     try:
    #         if 'xlsx' in filename:
    #             self.df = pd.read_excel(filepath)
    #
    #         elif 'txt' in filename:
    #             self.df = pd.read_csv(filepath, delimiter='\t')
    #
    #         elif 'csv' in filename:
    #             self.df = pd.read_csv(filepath, delimiter=',')
    #     except:
    #         pass

    # def check_feed_back(self):
    #     """
    #     Check:
    #         1.heading spelling: Distance, Proposition
    #         2. distance can only have number (int or float), space and comma can be detected and removed
    #             proposition can take any string and number, space can be detected and removed, we encourage to use
    #             string and integer.
    #         3. fixed coding tag, and tag's corresponding distance
    #     Two mode? informative or showcase
    #     :return:
    #     """
    #     pass

    def process_nodes(self):
        # calculates x, y coordinates from data
        node_x = []
        node_y = []

        for idx, row in self.df.iterrows():
            # root, root should starts from x==0, suggested by SCH
            if idx == 0:
                cur_x = 0
                cur_y = self.df.Proposition.count()
            # tree
            else:
                # deal with the P and T situation
                # cur_x' calculation is subjective to position (whether is the first point) and
                # 'Responds To' value
                # TODO: ROBUST ('Responds To')
                if not row['Responds To'] in UNKNOWN:
                    try:
                        # for propositions coded with pure number
                        cur_x = self.nodes[int(row['Responds To'])][0] + row.Distance
                    except:
                        # in case of string proposition
                        cur_x = self.nodes[row['Responds To']][0] + row.Distance
                else:
                    # deal with the [B]reak situation
                    # conveniently set the current point four units to the root
                    cur_x = self.nodes[0][0] + 4
                cur_y = self.df.Proposition.count() - idx

            node_x.append(cur_x)
            node_y.append(cur_y)
            self.nodes.update({row.Proposition: [cur_x, cur_y]})

        for node in self.df.Proposition:
            self.graph.add_node(node, pos=(self.nodes[node]))

        # for (node, xy) in zip(self.nodes.keys(), list(zip(node_x, node_y))):
        #     graph.add_node(node, pos=(xy[0], xy[1]))

        # use df to trace positions
        self.df['Pos'] = pd.Series(list(self.nodes.values()))

    # def process_edges(self):
    #     """
    #     TODO: FUNCTION: how to tell dotted lines apart from normal lines
    #     Finds edges and dotted edges
    #     :return:
    #     """
    #     for idx1, row1 in self.df.iterrows():
    #         for idx2, row2 in self.df.iterrows():
    #             if row1.Proposition == row2['Responds To'] and row2['Dotted Line'] in NO:
    #                 self.edges.append([row1.Proposition, row2.Proposition])
    #                 # self.graph.add_edge(row1.Proposition, row2.Proposition, dotted=True)
    #             #                 edges.append((row1.Proposition, row2.Proposition))
    #             elif row1.Proposition == row2['Responds To'] and row2['Dotted Line'] in YES:
    #                 self.edges_dotted.append([row1.Proposition, row2.Proposition])
    #                 # self.graph.add_edge(row1.Proposition, row2.Proposition, dotted=False)
    #             #                 edges_dotted.append((row1.Proposition, row2.Proposition))
    #             else:
    #                 # TODO: ROBUST
    #                 # should raise some error to guide users
    #                 pass
    #
    #     flatten_edges_lookup = [node for node_pairs in self.edges for node in node_pairs]
    #     flatten_edges_dotted_lookup = [node for node_pairs in self.edges_dotted for node in node_pairs]
    #
    #     self.edge_x = [i for s in [self.nodes[node] for node in flatten_edges_lookup] for i in s]
    #     self.edge_y = [i for s in [self.nodes[node] for node in flatten_edges_lookup] for i in s]
    #     self.edge_x_dotted = [i for s in [self.nodes[node] for node in flatten_edges_dotted_lookup] for i in s]
    #     self.edge_y_dotted = [i for s in [self.nodes[node] for node in flatten_edges_dotted_lookup] for i in s]
    #     # self.edge_y_dotted = [self.df[self.df.Proposition == node].Pos.values for node in flatten_edges_dotted_lookup]
    #     # self.graph.add_edges_from(self.edges)
    #
    #     #
    #     #
    #     # edge_x = []
    #     # edge_y = []
    #     # for edge in self.graph.edges():
    #     #     x0, y0 = self.graph.nodes[edge[0]]['pos']
    #     #     x1, y1 = self.graph.nodes[edge[1]]['pos']
    #     #     edge_x.append(x0)
    #     #     edge_x.append(x1)
    #     #     edge_x.append(None)
    #     #     edge_y.append(y0)
    #     #     edge_y.append(y1)
    #     #     edge_y.append(None)

    def process_edges(self):
        """
        TODO: FUNCTION: how to tell dotted lines apart from normal lines
        Finds edges and dotted edges
        :return:
        """
        for idx1, row1 in self.df.iterrows():
            for idx2, row2 in self.df.iterrows():
                if row1.Proposition == row2['Responds To'] and row2['Dotted Line'] in NO:
                    # self.edges.append([row1.Proposition, row2.Proposition])
                    self.graph.add_edge(row1.Proposition, row2.Proposition, dotted=False)
                #                 edges.append((row1.Proposition, row2.Proposition))
                elif row1.Proposition == row2['Responds To'] and row2['Dotted Line'] in YES:
                    # self.edges_dotted.append([row1.Proposition, row2.Proposition])
                    self.graph.add_edge(row1.Proposition, row2.Proposition, dotted=True)
                #                 edges_dotted.append((row1.Proposition, row2.Proposition))
                else:
                    # TODO: ROBUST
                    # should raise some error to guide users
                    pass

        for edgeTuple_dottedDict in list(self.graph.edges.data()):
            x0, y0 = self.graph.nodes[edgeTuple_dottedDict[:2][0]]['pos']
            x1, y1 = self.graph.nodes[edgeTuple_dottedDict[:2][1]]['pos']
            if not edgeTuple_dottedDict[2]['dotted']:
                self.edge_x.append(x0)
                self.edge_x.append(x1)
                self.edge_x.append(None)
                self.edge_y.append(y0)
                self.edge_y.append(y1)
                self.edge_y.append(None)
            else:
                self.edge_dotted_x.append(x0)
                self.edge_dotted_x.append(x1)
                self.edge_dotted_x.append(None)
                self.edge_dotted_y.append(y0)
                self.edge_dotted_y.append(y1)
                self.edge_dotted_y.append(None)
            # x0, y0 = self.graph.nodes[edge[0]]['pos']
            # x1, y1 = self.graph.nodes[edge[1]]['pos']
            # self.edge_x.append(x0)
            # self.edge_x.append(x1)
            # self.edge_x.append(None)
            # self.edge_y.append(y0)
            # self.edge_y.append(y1)
            # self.edge_y.append(None)

    def node_trace_t(self):
        """

        :return:
        """
        node_trace_t = go.Scatter(
            # first entry + all T
            x=[self.df.iloc[0:1].Pos[0][0]] + [x for [x, y] in self.df[self.df['Relation Type'] == 'T'].Pos],
            y=[self.df.iloc[0:1].Pos[0][1]] + [y for [x, y] in self.df[self.df['Relation Type'] == 'T'].Pos],
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
        return node_trace_t

    def node_trace_p(self):
        """

        :return:
        """
        node_trace_p = go.Scatter(
            # first entry + all T
            x=[self.df.iloc[0:1].Pos[0][0]] + [x for [x, y] in self.df[self.df['Relation Type'] == 'P'].Pos],
            y=[self.df.iloc[0:1].Pos[0][1]] + [y for [x, y] in self.df[self.df['Relation Type'] == 'P'].Pos],
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
        return node_trace_p

    def node_trace_b(self):
        """

        :return:
        """
        node_trace_b = go.Scatter(
            # first entry + all T
            x=[self.df.iloc[0:1].Pos[0][0]] + [x for [x, y] in self.df[self.df['Relation Type'] == 'B'].Pos],
            y=[self.df.iloc[0:1].Pos[0][1]] + [y for [x, y] in self.df[self.df['Relation Type'] == 'B'].Pos],
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
        return node_trace_b

    def edge_trace(self):
        """

        :return:
        """
        edge_trace = go.Scatter(
            x=self.edge_x,
            y=self.edge_y,
            name="responds to",
            line=dict(width=1, color='#888'),
            hoverinfo='none',
            mode='lines')
        return edge_trace

    def edge_dotted_trace(self):
        """

        :return:
        """
        edge_dotted_trace = go.Scatter(
            x=self.edge_dotted_x,
            y=self.edge_dotted_y,
            name="may respond to",
            line=dict(dash='dot', width=1, color='#888'),
            hoverinfo='none',
            mode='lines')
        return edge_dotted_trace

    def annotations(self):
        annotations = [dict(
            x=self.df.iloc[i].Pos[0],
            y=self.df.iloc[i].Pos[1],
            hovertext=self.df.iloc[i].Speaker,
            xanchor='right',
            yanchor='bottom',
            text=self.df.iloc[i].Text,
            visible=True,
            showarrow=False)
            for i in range(self.df.shape[0])]

        return annotations

    def boxer(self, retrun=None):
        fig = go.Figure(data=[self.node_trace_t(), self.node_trace_p(), self.node_trace_b(),
                              self.edge_trace(), self.edge_dotted_trace()],
                        layout=go.Layout(
                            # title='Visual-DTA: A Demo',
                            titlefont_size=20,
                            showlegend=True,
                            hovermode='closest',
                            width=1000,
                            height=1000,
                            margin=dict(b=20, l=5, r=5, t=40),
                            annotations=self.annotations(),
                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=True),
                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=True))
                        )
        # fig.show()
        return fig
