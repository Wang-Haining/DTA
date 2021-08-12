"""
Author: Haining Wang hw56@indiana.edu

This module holds DTA class.
"""


import warnings
import numpy as np
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
warnings.simplefilter("ignore")

# reduced fool-proof
UNKNOWN = ['n/a', 'N/A', 'na', 'NA', '', np.nan, 'unknown', 'UNKNOWN', '?', '??', "???"]
# no-line(0), solid-line (1), and dotted-line (2)
NO_LINE = [0, 'no', 'n', 'No', 'NO', 'N']
SOLID_LINE = [1, 'yes', 'y', 'Yes', 'YES', 'Y']
DOTTED_LINE = [2, 'SOLID', 'solid', 'solid line', 'SOLID LINE', 'SOLID_LINE', 'solid_line']
# YES = [1, 'yes', 'y', 'Yes', 'YES', 'Y']
# NO = [0, 'no', 'n', 'No', 'NO', 'N']

# # # dev use
# df_colbert = pd.read_excel('samples/Clolbert_NewCoding_hw_edits.xlsx')
# df_bilibili = pd.read_excel('samples/BiliBili_danmu.xlsx')
# dta = DTA(df_colbert)
# dta.process_nodes()
# dta.process_edges()
# dta.draw_graph(True)

# def autodta(df=None):
#     dta = DTA(df)
#     dta.process_nodes()
#     dta.process_edges()
#     dta.draw_graph(True).show()
# # #


class DTA(object):
    """
    DTA class is used to do the heavy lifting on https://visual-dta.herokuapp.com/.
    Generates a graph with read-in dataframe.
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
        self.edge_noline_x = []
        self.edge_noline_y = []
        # semantic distance metrics
        self.accumulated_semantic_distance = None
        self.mean_semantic_distance = None
        self.mean_semantic_distance_only_for_P = None

    def process_nodes(self):
        # calculates x, y coordinates from data
        node_x = []
        node_y = []

        for idx, row in self.df.iterrows():
            # root, root should starts from x==0, suggested by SCH
            if idx == 0:
                cur_x = 0.0
                cur_y = float(self.df.Proposition.count())
            # tree
            else:
                # deal with the P, T, B, and X situation
                # cur_x' calculation is subjective to position (whether is the first point) and
                # 'Responds To' value
                # TODO: ROBUST ('Responds To')
#                 if not row['Responds To'] in UNKNOWN:
                try:
                    # in case of string proposition
                    cur_x = self.nodes[int(row['Responds To'])][0] + float(row.Distance)
                except:
                    # for propositions coded with pure number
                    cur_x = self.nodes[row['Responds To']][0] + float(row.Distance)
#                 else:
#                     # deal with the [B]reak situation
#                     # conveniently set the current point four units to the root
# #                     cur_x = self.nodes[0][0] + 4
# #                     cur_x += 4
#                     pass
                cur_y = float(self.df.Proposition.count() - idx)

            node_x.append(cur_x)
            node_y.append(cur_y)
            self.nodes.update({row.Proposition: [cur_x, cur_y]})

        for node in self.df.Proposition:
            self.graph.add_node(node, pos=(self.nodes[node]))

        # for (node, xy) in zip(self.nodes.keys(), list(zip(node_x, node_y))):
        #     graph.add_node(node, pos=(xy[0], xy[1]))

        # use df to trace positions
        self.df['Pos'] = pd.Series(list(self.nodes.values()))
        self.accumulated_semantic_distance = max([x for node, (x, y) in self.nodes.items()])
        self.mean_semantic_distance = round(np.mean([x for node, (x, y) in self.nodes.items()]), 3)
        self.mean_semantic_distance_only_for_P = round(np.mean([[x for node, (x, y) in self.nodes.items()][idx] for idx in list(self.df[self.df['Relation Type'] == 'P'].index)]), 3)

    def process_edges(self):
        """
        Finds no-line(0), dotted-line (1), and solid-line (2) edges
        :return:
        """
        for idx1, row1 in self.df.iterrows():
            for idx2, row2 in self.df.iterrows():
                if row1.Proposition == row2['Responds To'] and row2['Line Type'] in NO_LINE and row2.Distance != 4:
                    # self.edges.append([row1.Proposition, row2.Proposition])
                    self.graph.add_edge(row1.Proposition, row2.Proposition, line_type='no_line')
                #                 edges.append((row1.Proposition, row2.Proposition))
                elif row1.Proposition == row2['Responds To'] and row2['Line Type'] in SOLID_LINE and row2.Distance != 4:
                    # self.edges_dotted.append([row1.Proposition, row2.Proposition])
                    self.graph.add_edge(row1.Proposition, row2.Proposition, line_type='solid_line')
                #                 edges_dotted.append((row1.Proposition, row2.Proposition))
                elif row1.Proposition == row2['Responds To'] and row2['Line Type'] in DOTTED_LINE and row2.Distance != 4:
                    # self.edges_dotted.append([row1.Proposition, row2.Proposition])
                    self.graph.add_edge(row1.Proposition, row2.Proposition, line_type='dotted_line')
                #                 edges_dotted.append((row1.Proposition, row2.Proposition))
                else:
                    # TODO: ROBUST
                    # should raise some error to guide users
                    pass

        for edgeTuple in list(self.graph.edges.data()):
            x0, y0 = self.graph.nodes[edgeTuple[:2][0]]['pos']
            x1, y1 = self.graph.nodes[edgeTuple[:2][1]]['pos']
            if edgeTuple[2]['line_type'] == 'solid_line':
                self.edge_x.append(x0)
                self.edge_x.append(x1)
                self.edge_x.append(None)
                self.edge_y.append(y0)
                self.edge_y.append(y1)
                self.edge_y.append(None)
            elif edgeTuple[2]['line_type'] == 'dotted_line':
                self.edge_dotted_x.append(x0)
                self.edge_dotted_x.append(x1)
                self.edge_dotted_x.append(None)
                self.edge_dotted_y.append(y0)
                self.edge_dotted_y.append(y1)
                self.edge_dotted_y.append(None)
            else:
                self.edge_noline_x.append(x0)
                self.edge_noline_x.append(x1)
                self.edge_noline_x.append(None)
                self.edge_noline_y.append(y0)
                self.edge_noline_y.append(y1)
                self.edge_noline_y.append(None)

    # def node_trace_first_proposition(self):
    #     """
    #
    #     :return:
    #     """
    #     node_trace_first_proposition = go.Scatter(
    #         # first entry
    #         x=[self.df.iloc[0:1].Pos[0][0]],
    #         y=[self.df.iloc[0:1].Pos[0][1]],
    #         name='proposition',
    #         mode='markers',
    #         hoverinfo='text',
    #         marker_symbol='square',
    #         marker=dict(
    #             showscale=False,
    #             color='yellow',
    #             size=8,
    #             line_width=2))
    #     return node_trace_first_proposition

    def node_trace_pr(self):
        """

        :return:
        """
        x = [self.df.iloc[0:1].Pos[0][0]] + [x for [x, y] in self.df[self.df['Relation Type'] == 'PR'].Pos]
        y = [self.df.iloc[0:1].Pos[0][1]] + [y for [x, y] in self.df[self.df['Relation Type'] == 'PR'].Pos]
        node_trace_pr = go.Scatter(
            # first entry
            x=x,
            y=y,
            name='prompt',
            mode='markers',
            hoverinfo='text',
            marker_symbol='square',
            marker=dict(
                showscale=False,
                color='yellow',
                size=8,
                line_width=2))
        return node_trace_pr

    def node_trace_t(self):
        """

        :return:
        """
        x = [self.df.iloc[0:1].Pos[0][0]] + [x for [x, y] in self.df[self.df['Relation Type'] == 'T'].Pos]
        y = [self.df.iloc[0:1].Pos[0][1]] + [y for [x, y] in self.df[self.df['Relation Type'] == 'T'].Pos]
        x = x[1:]
        y = y[1:]
        node_trace_t = go.Scatter(
            # all T
            x=x,
            y=y,
            name='Narrowly on-topic (T)',
            mode='markers',
            hoverinfo='text',
            marker=dict(
                showscale=False,
                color='blue',
                size=8,
                line_width=2))
        return node_trace_t

    def node_trace_p(self):
        """

        :return:
        """
        x = [self.df.iloc[0:1].Pos[0][0]] + [x for [x, y] in self.df[self.df['Relation Type'] == 'P'].Pos]
        y = [self.df.iloc[0:1].Pos[0][1]] + [y for [x, y] in self.df[self.df['Relation Type'] == 'P'].Pos]
        x = x[1:]
        y = y[1:]
        node_trace_p = go.Scatter(
            # all P
            x=x,
            y=y,
            name='Parallel Shift (P)',
            mode='markers',
            hoverinfo='text',
            marker=dict(
                showscale=False,
                color='red',
                size=8,
                line_width=2))
        return node_trace_p

    def node_trace_b(self):
        """

        :return:
        """
        x = [self.df.iloc[0:1].Pos[0][0]] + [x for [x, y] in self.df[self.df['Relation Type'] == 'B'].Pos]
        y = [self.df.iloc[0:1].Pos[0][1]] + [y for [x, y] in self.df[self.df['Relation Type'] == 'B'].Pos]
        x = x[1:]
        y = y[1:]
        node_trace_b = go.Scatter(
            # all B
            x=x,
            y=y,
            name='Break (B)',
            mode='markers',
            hoverinfo='text',
            marker=dict(
                showscale=False,
                color='green',
                size=8,
                line_width=2))
        return node_trace_b

    def node_trace_x(self):
        """

        :return:
        """
        x = [self.df.iloc[0:1].Pos[0][0]] + [x for [x, y] in self.df[self.df['Relation Type'] == 'X'].Pos]
        y = [self.df.iloc[0:1].Pos[0][1]] + [y for [x, y] in self.df[self.df['Relation Type'] == 'X'].Pos]
        x = x[1:]
        y = y[1:]
        node_trace_x = go.Scatter(
            # all X
            x=x,
            y=y,
            name='Flexible (X)',
            mode='markers',
            hoverinfo='text',
            marker=dict(
                showscale=False,
                color='purple',
                size=8,
                line_width=2))
        return node_trace_x

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

    def edge_noline_trace(self):
        """

        :return:
        """
        edge_noline_trace = go.Scatter(
            x=self.edge_noline_x,
            y=self.edge_noline_y,
            name="no line",
            visible=True,
            line=dict(width=0.01, color='#888'),
            hoverinfo='none',
            mode='lines')
        return edge_noline_trace

    def annotations(self):
        annotations = [dict(
            x=self.df.iloc[i].Pos[0],
            y=self.df.iloc[i].Pos[1],
            hovertext=self.df.iloc[i].Speaker,
            xanchor='left',
            yanchor='bottom',
            text=self.df.iloc[i].Text,
            visible=True,
            showarrow=False)
            for i in range(self.df.shape[0])]

        return annotations
    #
    # def no_annotations(self):
    #     annotations = [dict(
    #         x=self.df.iloc[i].Pos[0],
    #         y=self.df.iloc[i].Pos[1],
    #         hovertext=self.df.iloc[i].Speaker,
    #         xanchor='left',
    #         yanchor='bottom',
    #         text=[],
    #         visible=True,
    #         showarrow=False)
    #         for i in range(self.df.shape[0])]
    #
    #     return annotations

    def draw_graph(self, annotations_switch):
        """
        param:
            annotations_switch: a boolean, a plotly dash radio-item value, control if the text is annotated on the graph
        """
        if annotations_switch:
            fig = go.Figure()
            fig.add_trace(self.node_trace_t())
            fig.add_trace(self.node_trace_p())
            fig.add_trace(self.node_trace_b())
            fig.add_trace(self.node_trace_x())
            fig.add_trace(self.node_trace_pr())
            fig.add_trace(self.edge_trace())
            fig.add_trace(self.edge_dotted_trace())
            fig.add_trace(self.edge_noline_trace())

            fig.update_layout(go.Layout(
                titlefont_size=20,
                showlegend=True,
                hovermode='closest',
                # hoverlabel={'Proposition': [p for p in self.df.Proposition],
                #             'Speaker': [s for s in self.df.Speaker],
                #             'Text': [t for t in self.df.Text]},
                width=1000,
                height=1000,
                margin=dict(b=20, l=5, r=5, t=40),
                annotations=self.annotations(),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=True),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=True)))

            fig.update_yaxes(type='linear',
                             # tickmode='auto',
                             # title={'text': [str(p) for p in self.df.Proposition]},
                             # ticktext=[y for y in self.edge_y].reverse(),
                             # autorange="reversed",
                             constrain='range',
                             ticks='outside')
            fig.update_xaxes(tickformat=',d',
                             scaleanchor="y",
                             scaleratio=8
                             )

        else:
            fig = go.Figure(data=[self.node_trace_pr(), self.node_trace_t(), self.node_trace_p(), self.node_trace_b(), self.node_trace_x(),
                                  self.edge_trace(), self.edge_dotted_trace(), self.edge_noline_trace()],
                            layout=go.Layout(
                                titlefont_size=20,
                                showlegend=True,
                                hovermode='closest',
                                width=1000,
                                height=1000,
                                margin=dict(b=20, l=5, r=5, t=40),
                                # annotations=self.annotations(),
                                xaxis=dict(showgrid=False, zeroline=False, showticklabels=True),
                                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                            )
            fig.update_yaxes(type='linear',
                             # tickmode='auto',
                             # title={'text': [str(p) for p in self.df.Proposition]},
                             ticktext=[y for y in self.edge_y].reverse(),
                             # autorange="reversed",
                             constrain='range',
                             ticks='outside')
            fig.update_xaxes(tickformat=',d',
                             scaleanchor="y",
                             scaleratio=8
                             )
        return fig
