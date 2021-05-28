"""
Author: Haining Wang hw56@indiana.edu
"""
import dash
import json
import numpy as np
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
from dash_extensions import Download
from dash.dependencies import Input, Output
from dash_extensions.snippets import send_file

from src import static
from src.algorithm import DTA

import warnings
# warnings.simplefilter("ignore")

UNKNOWN = ['n/a', 'N/A', 'na', 'NA', '', np.nan, 'unknown', 'UNKNOWN', '?', '??', "???"]
YES = [1, 'yes', 'y', 'Yes', 'YES', 'Y']
NO = [0, 'no', 'n', 'No', 'NO', 'N']
TYPES = ['B', 'P', 'T']
HEADINGS = ['Proposition', 'Speaker', 'Responds To', 'Relation Type', 'Distance', 'Dotted Line', 'Text']

# for page foot
MARKDOWN_STYLE_SMALL = {'fontFamily': 'Times', 'fontSize': 15}
# for normal display
MARKDOWN_STYLE_NORMAL = {'fontFamily': 'Times', 'fontSize': 20}
# for error feedback
MARKDOWN_STYLE_LARGE = {'fontFamily': 'Times', 'fontSize': 30, 'bold': True}

##################

app = dash.Dash(__name__,
                # external_stylesheets=external_stylesheets,
                prevent_initial_callbacks=True,
                suppress_callback_exceptions=True
                )

# server = app.server

md_intro = '''
Visual DTA visualizes the structure of the topic flow within a conversation.
The philosophy behind it follows
[*Dynamic Topic Analysis of Synchronous Chat*](https://ella.sice.indiana.edu/~herring/dta.html),
proposed by [Dr. Susan Herring](https://info.sice.indiana.edu/~herring/) at Indiana University Bloomington.

We encourage you to take a look at the [user manual](https://info.sice.indiana.edu/~herring/VisualDTA/) before starting.
If you know Visual DTA jargon like *proposition* and *semantic distance* you are ready to go✅

Upload your data, and we will do a superficial validity check before visualizing.
You can also try some [existing examples](./demo) or [download the template](./template).
'''

md_specify_data = '''
Upload your data in comma/tab-separated values (`.csv`/`.tsv`/`.txt`) or Excel (`.xlsx`/`.xls`) format. 
Or, choose an example and see how Visual DTA performs.
You can also down a void template for your own data. 
'''

md_check = """
A superficial check will be performed on the data.
"""

md_generate = """
Click to visualize the topic flow.
"""

md_foot = """
**Licence**: Visual DTA is under the MIT licence.

**Feedback**: For any questions, please drop us a line on [GitHub](https://github.com/Wang-Haining/VisualDTA/issues).

**Contact**:

Susan Herring <herring@indiana.edu> for general questions.

Haining Wang <hw56@indiana.edu> for bugs. 
"""

"""
LAYOUT BEGINS
"""

app.layout = html.Div([
    # This "header" will persist across pages
    # header section
    html.H1(children='Visual DTA',
            style={
                'textAlign': 'center',
                'fontFamily': 'Times',
                'fontSize': 80}
            # 'color': colors['text']
            ),
    # intro section
    html.Div(dcc.Markdown(children=[md_intro], style=MARKDOWN_STYLE_NORMAL)),
    # dcc.Link(dcc.Markdown('You can also try some existing data.'), href="/demo", style={'fontFamily': 'Times', 'fontSize': 20}),
    # Each "page" will modify this element
    html.Div(id='content-container'),
    # html.Hr(),
    # This Location component represents the URL bar
    dcc.Location(id='url', refresh=False),

    html.Hr(),
    # # reset graph
    # html.Button(id='submit-button-state', n_clicks=0, children='Reset')

    # foot
    dcc.Markdown(md_foot, style=MARKDOWN_STYLE_SMALL),
    html.Hr(),
    # visualize button's trigger div
    # html.Div(id='trigger', children=0, style=dict(display='none'))

], className="container")

"""
STATIC FUNCTIONS Begins
"""


@app.callback(
    Output('content-container', 'children'),
    [Input('url', 'pathname')])
def display_page(pathname):
    # print(pathname)
    if pathname == '/':
        return html.Div([
            # html.Div('You are on the index page.'),

            # the dcc.Link component updates the `Location` pathname
            # without refreshing the page
            # dcc.Link(dcc.Markdown('You can also try some existing data.'), href="/demo", style=MARKDOWN_STYLE_NORMAL),
            # html.Hr(),
            # html.A('Go to page 2 but refresh the page', href="/demo")

            # to show starts
            html.Hr(),
            # Step 1
            html.Div(
                [
                    dcc.Markdown(children="Step 1", style=MARKDOWN_STYLE_LARGE),
                    dcc.Markdown(children=md_specify_data, style=MARKDOWN_STYLE_NORMAL),
                ]
            ),
            html.Div(
                [
                    html.Tr(
                        [
                            # upload
                            html.Th([
                                dcc.Upload(
                                    id='upload',
                                    children=html.Div([
                                        'Drag and Drop or ',
                                        html.A('Select Files'),
                                        ' in .xlsx, .csv, or .txt.',
                                    ]),
                                    style={
                                        'lineHeight': '60px',
                                        'borderWidth': '1px',
                                        'borderStyle': 'dashed',
                                        'borderRadius': '5px',
                                        'textAlign': 'center',
                                        'margin': '10px'
                                    },
                                ),
                            ], style={'height': '40px', 'width': '500px', "borderBottom": 'none'}),
                        ],
                    )
                ]
            ),

            html.Hr(),
            # Step 2
            html.Div(
                [
                    dcc.Markdown(children='Step 2', style=MARKDOWN_STYLE_LARGE),
                    dcc.Markdown(children=md_check, style=MARKDOWN_STYLE_NORMAL),
                    dcc.Markdown(id='feedback'),
                    # html.Div(id='cache')
                ]
            ),

            html.Hr(),
            # Step 3
            # generate graph
            html.Div(
                [
                    dcc.Markdown(children='Step 3', style=MARKDOWN_STYLE_LARGE),
                    dcc.Markdown(children=md_generate, style=MARKDOWN_STYLE_NORMAL),
                    html.Button(id='visualize', children='Visualize topic flow', disabled=False,
                                style={'height': "60px", 'width': "450px", 'margin': '10px'}),
                    html.Div(id='dta_graph'),
                    html.Div([dcc.RadioItems(
                                id='hide_show_button',
                                options=[{'label': x, 'value': x}
                                         for x in ['Show Text', 'Hide Text']],
                                value='Show Text',
                                labelStyle={'display': 'inline-block'})]),
                    # show accumulated/mean semantic distance
                    html.Div(id='mean_semantic_distance'),
                    html.Div(id='accumulated_semantic_distance'),
                    # dcc.Store stores the uploaded file
                    dcc.Store(id='shared_file')
                ]

            ),
            # to show ends
        ])
    elif pathname == '/demo':
        return html.Div([
            # demo opening
            dcc.Markdown('Choose an example.', style=MARKDOWN_STYLE_NORMAL),
            # dropdown
            html.Th([
                dcc.Dropdown(
                    id='dropdown',
                    options=[
                        {'label': 'en_whole.txt', 'value': 'example_whole'},
                        {'label': 'en_citizen3_1.txt', 'value': 'example_citizen'},
                        {'label': 'zh_danmu.xlsx', 'value': 'example_danmu'}
                    ],
                    # value='example_whole'
                ),
            ], style={'height': '30px', 'width': '450px', "borderBottom": 'none'}),
            # graph to show [TODO]
            html.Div(id='drop_down_show_graph'),
            html.Div([dcc.RadioItems(
                id='hide_show_button_demo',
                options=[{'label': x, 'value': x}
                         for x in ['Show Text', 'Hide Text']],
                value='Show Text',
                labelStyle={'display': 'inline-block'})]),
            # show accumulated/mean semantic distance
            html.Div(id='mean_semantic_distance_demo'),
            html.Div(id='accumulated_semantic_distance_demo'),
            # go back home
            dcc.Link(dcc.Markdown('Go back home'), href="/", style=MARKDOWN_STYLE_NORMAL),
        ])
    elif pathname == '/template':
        return html.Div([
            # template opening
            dcc.Markdown('Download the template or an existing example.', style=MARKDOWN_STYLE_NORMAL),
            # download
            html.Div([html.Button("Download the template", id="btn_download_template"), Download(id="download_template")
                      ]),
            # go back home
            dcc.Link(dcc.Markdown('Go back home'), href="/", style=MARKDOWN_STYLE_NORMAL),
        ])
    else:
        # feedback error 404
        return dcc.Markdown('Error: no content available', style=MARKDOWN_STYLE_LARGE)


@app.callback(Output("download_template", "data"), Input("btn_download_template", "n_clicks"))
def return_pdf(n_clicks):
    return send_file("./samples/template.xlsx")


@app.callback(Output('feedback', 'children'),
              Output('shared_file', 'data'),
              Input('upload', 'contents'),
              Input('upload', 'filename'))
def check_upload(contents, filename):

    df = static.read_in_uploaded(contents, filename)
    shared_file = None
    # 1. check if we successfully read in a dataframe
    if isinstance(df, pd.DataFrame):
        feedback = """🎉🎉🎉 **Successfully uploaded!**
        
        """
        # check headings
        feedback += static.check_heading(df)
        feedback += static.check_minimal_length(df)
        feedback += static.check_equal_length(df)
        feedback += static.check_first_row(df)
        feedback += static.check_blank_value(df)
        feedback += static.check_value_type(df)
        feedback += static.check_order(df)
        # store the uploaded file
        shared_file = df.to_json(date_format='iso', orient='split')
    # if we did not read in a dataframe
    else:
        feedback = df
    return feedback, shared_file


@app.callback([Output("dta_graph", 'children'),
              Output("mean_semantic_distance", 'children'),
              Output("accumulated_semantic_distance", 'children')],
              [Input('visualize', 'n_clicks'),
              Input('shared_file', 'data'),
              Input('hide_show_button', 'value')])
def visualize(n_clicks, data, hide_show):

    df = pd.read_json(data, orient='split')

    dta = DTA(df)
    dta.process_nodes()
    dta.process_edges()
    if hide_show == 'Show Text':
        fig = dta.draw_graph(annotations_switch=True)
    else:
        fig = dta.draw_graph(annotations_switch=False)
    # get background color as white
    fig.layout.plot_bgcolor = '#fff'
    fig.layout.paper_bgcolor = '#fff'

    if n_clicks:
        return (dcc.Graph(figure=fig),
                f'Mean Semantic Distance: {dta.mean_semantic_distance}',
                f'Accumulated Semantic Distance: {dta.accumulated_semantic_distance}')


@app.callback([Output('drop_down_show_graph', 'children'),
              Output("mean_semantic_distance_demo", 'children'),
              Output("accumulated_semantic_distance_demo", 'children')],
              [Input('dropdown', 'value'),
               Input('hide_show_button_demo', 'value')])
def show_dropdown(dropdown, hide_show):
    if dropdown == 'example_whole':
        df = pd.read_excel('./samples/whole.xlsx')
    elif dropdown == 'example_citizen':
        df = pd.read_csv('./samples/citizen3-1.txt', delimiter='\t')
    elif dropdown == 'example_danmu':
        df = pd.read_excel('./samples/BiliBili_comments.xlsx')
    else:
        pass
    dta = DTA(df)
    dta.process_nodes()
    dta.process_edges()
    if hide_show == 'Show Text':
        fig = dta.draw_graph(annotations_switch=True)
    else:
        fig = dta.draw_graph(annotations_switch=False)
    # get background color as white
    fig.layout.plot_bgcolor = '#fff'
    fig.layout.paper_bgcolor = '#fff'

    return (dcc.Graph(figure=fig),
            f'Mean Semantic Distance: {dta.mean_semantic_distance}',
            f'Accumulated Semantic Distance: {dta.accumulated_semantic_distance}'
            )


if __name__ == '__main__':
    app.run_server(debug=True,
                   use_reloader=False,
                   dev_tools_ui=True,
                   dev_tools_props_check=False,
                   port=8080)
