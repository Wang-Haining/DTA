"""
Author: Haining Wang hw56@indiana.edu

This module holds app setup, layout, and callbacks for VisualDTA Online.
"""

import dash
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
from dash_extensions import Download
from dash.dependencies import Input, Output
from dash_extensions.snippets import send_file

from src import static
from src.dta import DTA

# for page foot
MARKDOWN_STYLE_SMALL = {'fontFamily': 'Times', 'fontSize': 15}
# for normal display
MARKDOWN_STYLE_NORMAL = {'fontFamily': 'Times', 'fontSize': 20}
# for error feedback
MARKDOWN_STYLE_LARGE = {'fontFamily': 'Times', 'fontSize': 30, 'bold': True}

##################

INTRODUCTION = '''
Visual DTA visualizes the structure of the topic flow within a conversation.
The philosophy behind it follows
[*Dynamic Topic Analysis of Synchronous Chat*](https://ella.sice.indiana.edu/~herring/dta.html),
designed by [Dr. Susan Herring](https://info.sice.indiana.edu/~herring/) at Indiana University Bloomington.

We encourage you to take a look at the [user manual](https://info.sice.indiana.edu/~herring/VisualDTA/) or [tutorial](/) before starting.
If you know Visual DTA jargon like *proposition* and *semantic distance* you are ready to go.

Upload your data, and we will do a superficial validity check before visualizing.
You can also try some [existing examples](./demo) or [download the template](./template).
'''

SPECIFY_DATA = '''Upload your data in comma/tab-separated values (csv/tsv/txt) or Excel (xlsx/xls) format.'''

FILE_CHECK = """A superficial check will be performed on the uploaded file."""

GENERATE_DTA = """
Click to visualize the topic flow.
"""

FOOT = """
**Licence**: This work is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.

**Feedback**: For any questions, please drop us a line on [GitHub](https://github.com/Wang-Haining/VisualDTA/issues).

**Contact**:

Susan Herring <herring@indiana.edu> for general.

Haining Wang <hw56@indiana.edu> for technical. 
"""
# --------------------------------------------------APP SETUP BEGINS--------------------------------------------------
app = dash.Dash(__name__,
                prevent_initial_callbacks=True,
                suppress_callback_exceptions=True
                )
# html tag name
app.title = 'VisualDTA Online'

server = app.server

# --------------------------------------------------APP SETUP ENDS--------------------------------------------------

# --------------------------------------------------LAYOUT BEGINS--------------------------------------------------

app.layout = html.Div([
    # This "header" persists across pages
    # banner section
    html.Div(html.H1([html.A([html.Img(src='/assets/dta_logo.png',
                                       style={'height': '12%',
                                              'width': '12%',
                                              'verticalAlign': 'baseline',
                                              'marginBottom': -20,
                                              'display': 'inlineBlock'})],
                             href='/'),
                      html.Span(children='Visual DTA',
                                style={
                                    'textAlign': 'left',
                                    'fontFamily': 'Times',
                                    'fontSize': 80,
                                    'color': "#3D4E76"}),
                      html.Span(children='  Online',
                                style={
                                    'textAlign': 'left',
                                    'fontFamily': 'Times',
                                    'fontSize': 40,
                                    'color': "#3D4E76"}),
                      html.Span(children=' Dev. 0.0.3',
                                style={
                                    'textAlign': 'left',
                                    'fontFamily': 'monospace',
                                    'font-style': 'italic',
                                    'fontSize': 20,
                                    'color': "#69BFB0"}),
                      ], style={'verticalAlign': 'baseline'}),
             # className="wrapper_header"
             ),
    html.Hr(),
    # intro section
    html.Div(dcc.Markdown(children=[INTRODUCTION], style=MARKDOWN_STYLE_NORMAL, dedent=False)),
    # Each "page" will modify this element
    html.Div(id='content-container'),
    # html.Hr(),
    # This Location component represents the URL bar
    dcc.Location(id='url', refresh=False),

    html.Hr(),
    # # reset graph
    # html.Button(id='submit-button-state', n_clicks=0, children='Reset')

    # foot
    dcc.Markdown(FOOT, style=MARKDOWN_STYLE_SMALL),
    html.Hr(),

], className="container")


# --------------------------------------------------LAYOUT ENDS--------------------------------------------------

# --------------------------------------------------CALLBACKS BEGIN--------------------------------------------------


@app.callback(
    Output('content-container', 'children'),
    [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return html.Div([
            html.Hr(),
            # Step 1
            html.Div(
                [
                    html.H3(children="Step 1", style=MARKDOWN_STYLE_LARGE, className="wrapper_subheader"),
                    html.Span(children=SPECIFY_DATA, style=MARKDOWN_STYLE_NORMAL)
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
                                        'DRAG and DROP or ',
                                        html.A('SELECT A FILE')]),
                                    style={
                                        'lineHeight': '60px',
                                        'borderWidth': '1px',
                                        'borderStyle': 'dashed',
                                        'borderRadius': '5px',
                                        'textAlign': 'center',
                                        'margin': '10px',
                                        'fontFamily': 'monospace',
                                        'fontSize': 16,
                                        'color': '#2D2D2D'},
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
                    dcc.Markdown(children='Step 2', style=MARKDOWN_STYLE_LARGE, className="wrapper_subheader"),
                    dcc.Markdown(children=FILE_CHECK, style=MARKDOWN_STYLE_NORMAL),
                    dcc.Markdown(id='feedback', dedent=True,
                                 style={'fontFamily': 'monospace',
                                        'fontSize': 16}),
                ]
            ),

            html.Hr(),
            # Step 3
            # generate graph
            html.Div(
                [
                    dcc.Markdown(children='Step 3', style=MARKDOWN_STYLE_LARGE, className="wrapper_subheader"),
                    dcc.Markdown(children=GENERATE_DTA, style=MARKDOWN_STYLE_NORMAL),
                    html.Button(id='visualize', children='Visualize Topic Flow', disabled=False,
                                style={'height': "60px",
                                       'width': "480px",
                                       'margin': '10px',
                                       'fontFamily': 'monospace',
                                       'fontSize': 16,
                                       'color': '#2D2D2D'}),
                    html.Div(id='dta_graph'),
                    html.Br(),
                    html.Div([dcc.RadioItems(
                        id='hide_show_button',
                        options=[{'label': x, 'value': x}
                                 for x in ['Show Text', 'Hide Text']],
                        value='Show Text',
                        labelStyle={'display': 'inline-block'},
                        style=MARKDOWN_STYLE_SMALL)]),
                    # show accumulated/mean semantic distance/mean semantic distance only counting Ps
                    html.Div(id='mean_semantic_distance', style=MARKDOWN_STYLE_SMALL),
                    html.Div(id='accumulated_semantic_distance', style=MARKDOWN_STYLE_SMALL),
                    html.Div(id='mean_semantic_distance_only_for_P', style=MARKDOWN_STYLE_SMALL),
                    # dcc.Store stores the uploaded file
                    dcc.Store(id='shared_file')
                ]

            ),
            # to show ends
        ])
    elif pathname == '/demo':
        return html.Div([
            html.Hr(),
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
                ),
            ], style={'height': '30px', 'width': '450px', "borderBottom": 'none'}),
            # graph to show [TODO]
            html.Div(id='drop_down_show_graph'),
            html.Br(),
            html.Div([dcc.RadioItems(
                id='hide_show_button_demo',
                options=[{'label': x, 'value': x}
                         for x in ['Show Text', 'Hide Text']],
                value='Show Text',
                labelStyle={'display': 'inline-block'},
                style=MARKDOWN_STYLE_SMALL
            )]),
            # show accumulated/mean semantic distance
            html.Div(id='mean_semantic_distance_demo', style=MARKDOWN_STYLE_SMALL),
            html.Div(id='accumulated_semantic_distance_demo', style=MARKDOWN_STYLE_SMALL),
            html.Div(id='mean_semantic_distance_only_for_P_demo', style=MARKDOWN_STYLE_SMALL),
            html.Br(),
            # go back home
            dcc.Link(dcc.Markdown('Go Back Home'), href="/", style=MARKDOWN_STYLE_NORMAL),
        ])
    elif pathname == '/template':
        return html.Div([
            html.Hr(),
            # template opening
            dcc.Markdown('Download the template.', style=MARKDOWN_STYLE_NORMAL),
            html.Br(),
            # download
            html.Div([html.Button("Download the template", id="btn_download_template",
                                  style={'height': "60px",
                                         'width': "480px",
                                         'margin': '10px',
                                         'fontFamily': 'monospace',
                                         'fontSize': 16,
                                         'color': '#2D2D2D'}),
                      Download(id="download_template")
                      ]),
            html.Br(),
            # go back home
            dcc.Link(dcc.Markdown('Go Back Home'), href="/", style=MARKDOWN_STYLE_NORMAL),
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
        feedback = """🎉🎉🎉 **Successfully uploaded!** 🎉🎉🎉"""
        # check headings
        feedback += static.check_heading(df)
        feedback += static.check_minimal_length(df)
        feedback += static.check_equal_length(df)
        feedback += static.check_first_row(df)
        feedback += static.check_blank_value(df)
        feedback += static.check_value_type(df)
        feedback += static.check_order(df)
        feedback += """
        
Please check the file regarding the above messages. Or you can process to visualize, but it may not work as expected, if at all."""
        # for testing purpose
        # print(feedback)
        # store the uploaded file
        shared_file = df.to_json(date_format='iso', orient='split')
    # if we did not read in a dataframe
    else:
        feedback = df
    return feedback, shared_file


@app.callback([Output("dta_graph", 'children'),
               Output("mean_semantic_distance", 'children'),
               Output("accumulated_semantic_distance", 'children'),
               Output("mean_semantic_distance_only_for_P", 'children')],
              [Input('visualize', 'n_clicks'),
               Input('shared_file', 'data'),
               Input('hide_show_button', 'value')])
def visualize_uploaded(n_clicks, data, hide_show):
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
                f'Mean Semantic Distance (all): {dta.mean_semantic_distance}',
                f'Accumulated Semantic Distance: {dta.accumulated_semantic_distance}',
                f'Mean Semantic Distance (P): {dta.mean_semantic_distance_only_for_P}')


@app.callback([Output('drop_down_show_graph', 'children'),
               Output("mean_semantic_distance_demo", 'children'),
               Output("accumulated_semantic_distance_demo", 'children'),
               Output("mean_semantic_distance_only_for_P_demo", 'children')],
              [Input('dropdown', 'value'),
               Input('hide_show_button_demo', 'value')])
def visualize_demo(dropdown, hide_show):
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
            f'Mean Semantic Distance (all): {dta.mean_semantic_distance}',
            f'Accumulated Semantic Distance: {dta.accumulated_semantic_distance}',
            f'Mean Semantic Distance (P): {dta.mean_semantic_distance_only_for_P}'
            )


# --------------------------------------------------CALLBACKS END--------------------------------------------------

if __name__ == '__main__':
    app.run_server(debug=False,
                   use_reloader=False,
                   dev_tools_ui=True,
                   dev_tools_props_check=True,
                   port=8080)
