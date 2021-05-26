"""
Author: Haining Wang hw56@indiana.edu
"""
import dash
import base64
import io
import static
import pandas as pd
# from flask import send_file
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from encodings.aliases import aliases
import chardet

import numpy as np
# from src.guide import GUIDE
from src.main import DTA

import warnings

# warnings.simplefilter("ignore")

UNKNOWN = ['n/a', 'N/A', 'na', 'NA', '', np.nan, 'unknown', 'UNKNOWN', '?', '??', "???"]
YES = [1, 'yes', 'y', 'Yes', 'YES', 'Y']
NO = [0, 'no', 'n', 'No', 'NO', 'N']
TYPES = ['B', 'P', 'T']
HEADINGS = ['Proposition', 'Speaker', 'Responds To', 'Relation Type', 'Distance', 'Dotted Line', 'Text']

##################

# dta = DTA()
# dta.read_in('./samples/BiliBili_comments.xlsx')
# dta.process_nodes()
# dta.process_edges()
# fig = dta.boxer()

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__,
                # external_stylesheets=external_stylesheets
                )

server = app.server

md_intro = '''
Visual DTA visualizes the structure of the topic flow within a conversation.
The philosophy behind it follows
[*Dynamic Topic Analysis of Synchronous Chat*](https://ella.sice.indiana.edu/~herring/dta.html),
from Dr. Susan Herring at Indiana University.

We encourage you to take a look at the [user manual](https://info.sice.indiana.edu/~herring/VisualDTA/) before starting.
If you know Visual DTA jargon like *proposition* and *semantic distance* ✅ you are ready to go!

Upload your data, and we will do a superficial validity check before visualizing;
Or you can try some existing data.

Please follow the below steps.
'''

md_demo = '''
TL; DR the user manual ? Sure, 
'''

md_step1 = '''
Step 1 
'''

md_specify_data = '''
Upload your data in comma/tab-separated values (`.csv`/`.tsv`/`.txt`) or Excel (`.xlsx`/`.xls`) format. 
Or, choose an example and see how Visual DTA performs.
You can also down a void template for your own data. 
'''

md_step2 = """
Step 2
"""

md_check = """
A superficial check will be performed on the data.
"""

md_step3 = """
Step 3
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
app.layout = html.Div(children=[
    # head section
    html.H1(children='Visual DTA',
            style={
                'textAlign': 'center',
                'fontFamily': 'Times',
                'fontSize': 80}
            # 'color': colors['text']
            ),
    # intro section
    html.Div(dcc.Markdown(children=md_intro, style={'fontFamily': 'Times',
                                                    'fontSize': 20})),
    html.Hr(),
    # Step 1
    html.Div(
        [
            dcc.Markdown(children=md_step1, style={'fontFamily': 'Times',
                                                   'fontSize': 30,
                                                   'bold': True}),
            dcc.Markdown(children=md_specify_data, style={'fontFamily': 'Times',
                                                          'fontSize': 20}),
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
                                ' in .xlsx, .csv or .txt.',
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
                    # or
                    html.Th('Or', style={'borderBottom': 'none'}),
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
                    # dowload
                    # html.Th([
                    #     html.Button("Download Template", id="download"),
                    # ], style={'height': '50px', 'width': '450px'}),
                ],
                # style={
                #     'height': '300px'
                # }
            )
        ]
    ),

    html.Hr(),
    # Step 2
    html.Div(
        [
            dcc.Markdown(children=md_step2, style={'fontFamily': 'Times',
                                                   'fontSize': 30,
                                                   'bold': True}),
            dcc.Markdown(children=md_check, style={'fontFamily': 'Times',
                                                   'fontSize': 20}),
            dcc.Markdown(id='feedback'),
            # html.Div(id='cache')
        ]
    ),

    html.Hr(),
    # Step 3
    # generate graph
    html.Div(
        [
            dcc.Markdown(children=md_step3, style={'fontFamily': 'Times',
                                                   'fontSize': 30,
                                                   'bold': True}),
            dcc.Markdown(children=md_generate, style={'fontFamily': 'Times',
                                                      'fontSize': 20}),
            html.Button(id='visualize', children='Visualize topic flow',
                        style={'height': "60px", 'width': "450px", 'margin': '10px'}),
            html.Div(id='output',
                     style={'textAlign': 'center'}
                     ),
        ]
    ),
    html.Hr(),
    # # reset graph
    # html.Button(id='submit-button-state', n_clicks=0, children='Reset')

    # foot
    dcc.Markdown(md_foot, style={'fontFamily': 'Times', 'fontSize': 15}),
    html.Hr(),
])

"""
STATIC FUNCTIONS Begins
"""

@app.callback(Output('feedback', 'children'),
              Output('dropdown', 'value'),
              Input('upload', 'contents'),
              Input('upload', 'filename'),
              Input('dropdown', 'value'))
def check(contents, filename, dropdown):
    df = ''
    # upload
    if contents is not None:
        # clear dropdown value
        dropdown = ""
        df = static.read_in_uploaded(contents, filename)
    else:
        # print('Initiate successfully!')
        pass
    # dropdown
    if dropdown is not None:
        # clear upload value
        contents = ""
        filename = ""
        if dropdown == 'example_whole':
            df = static.read_in_demo('./samples/whole.txt', 'whole.txt')
        elif dropdown == 'example_citizen':
            df = static.read_in_demo('./samples/citizen3-1.txt', 'citizen3-1.txt')
        elif dropdown == 'example_danmu':
            df = static.read_in_demo('./samples/BiliBili_comments.xlsx', 'BiliBili_comments.xlsx')
        else:
            # print('Initiate successfully!')
            pass
    # 1. check if we successfully read in a dataframe
    if isinstance(df, pd.DataFrame):
        feedback = """😁 **Successfully uploaded!**\n"""
        # check headings
        feedback += static.check_heading(df)

    # if we did not read in a dataframe
    else:
        feedback = df
    # print(df)

    return feedback, dropdown


# demo reset [TODO]
# @app.callback(Output('graph&reset', 'children'),
#               Input('reset', 'n_clicks'))
# def demo_reset(n_clicks):
#     if n_clicks > 0:
#         return html.Div(id='void')


if __name__ == '__main__':
    app.run_server(debug=True,
                   use_reloader=False,
                   dev_tools_ui=True,
                   dev_tools_props_check=False
                   )
