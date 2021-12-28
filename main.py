import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import talib

app = dash.Dash(external_stylesheets=[dbc.themes.CERULEAN], title='Stock Market View', update_title='Loading...')

server = app.server


def load_ticks():
    options = []
    optdf = pd.read_csv('ticksymbols.csv', encoding='latin-1')
    optdf.set_index('Ticker', inplace=True)

    for index, row in optdf.iterrows():
        optdict = {'label': str(row['Name']) + '-\t' + str(index), 'value': index}
        options.append(optdict)
    return options


def load_data(period, interval, tick, compare=None):
    ticker = yf.Ticker(tick)
    df = ticker.history(period=period, interval=interval)
    df = df.dropna()
    if compare is not None and compare != []:
        return df - df['Close'].iloc[0]
    else:
        return df


def period_int(p):
    if p == '15m' or p == '1d':
        return '1m'
    elif p == '5d':
        return '5m'
    elif p == '1mo':
        return '30m'
    elif p == '3mo':
        return '60m'
    elif p == '6mo' or p == 'ytd' or p == '1y':
        return '1d'
    elif p == '5y' or p == '10y':
        return '1wk'
    elif p == 'max':
        return '1mo'


def rangebreak(fig, period, interval):
    if period != '1d':
        if interval == '1d':
            fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"])])
        elif interval == '60m' or interval == '30m' or interval == '15m' or interval == '5m' or interval == '2m' or interval == '1m':
            fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"]), dict(bounds=[15.5, 9], pattern='hour')])
    return fig


app.layout = html.Div([dcc.Tabs([
    dcc.Tab(label='Single Time Frame', children=[dbc.Row([dbc.Col(dcc.Dropdown(id='tickinput',
                                                                               options=load_ticks(),
                                                                               placeholder='Stock',
                                                                               value='^NSEI',
                                                                               multi=False,
                                                                               searchable=True,
                                                                               clearable=False,
                                                                               optionHeight=45,
                                                                               persistence=True,
                                                                               persistence_type='session',
                                                                               style={'background-color': '#F0F8FF'}
                                                                               ),
                                                                  width={'size': 3, 'offset': 0}
                                                                  ),
                                                          dbc.Col(dcc.Dropdown(id='periodinput',
                                                                               options=[
                                                                                   {'label': 'Period', 'value': 'p',
                                                                                    'disabled': True},
                                                                                   {'label': '15min', 'value': '15m'},
                                                                                   {'label': '1day', 'value': '1d'},
                                                                                   {'label': '5day', 'value': '5d'},
                                                                                   {'label': '1mon', 'value': '1mo'},
                                                                                   {'label': '3mon', 'value': '3mo'},
                                                                                   {'label': '6mon', 'value': '6mo'},
                                                                                   {'label': 'YTD', 'value': 'ytd'},
                                                                                   {'label': '1Y', 'value': '1y'},
                                                                                   {'label': '5Y', 'value': '5y'},
                                                                                   {'label': '10Y', 'value': '10y'},
                                                                                   {'label': 'All', 'value': 'max'}
                                                                               ],
                                                                               placeholder='Period',
                                                                               value='1y',
                                                                               optionHeight=30,
                                                                               searchable=True,
                                                                               clearable=False,
                                                                               persistence=True,
                                                                               persistence_type='session',
                                                                               style={'background-color': '#F0F8FF'}
                                                                               ),
                                                                  width={'size': 1, 'offset': 0}
                                                                  ),
                                                          dbc.Col(dcc.Dropdown(id='intervalinput',
                                                                               options=[
                                                                                   {'label': 'Interval', 'value': 'i',
                                                                                    'disabled': True},
                                                                                   {'label': '1min', 'value': '1m'},
                                                                                   {'label': '2min', 'value': '2m'},
                                                                                   {'label': '5min', 'value': '5m'},
                                                                                   {'label': '15min', 'value': '15m'},
                                                                                   {'label': '30min', 'value': '30m'},
                                                                                   {'label': '1h', 'value': '60m'},
                                                                                   # {'label': '90min', 'value': '90m'},
                                                                                   {'label': 'D', 'value': '1d'},
                                                                                   # {'label': '5D', 'value': '5d'},
                                                                                   {'label': 'W', 'value': '1wk'},
                                                                                   {'label': 'M', 'value': '1mo'},
                                                                                   {'label': '3M', 'value': '3mo'}
                                                                               ],
                                                                               placeholder='Interval',
                                                                               value='1d',
                                                                               optionHeight=30,
                                                                               searchable=True,
                                                                               clearable=False,
                                                                               persistence=True,
                                                                               persistence_type='session',
                                                                               style={'background-color': '#F0F8FF'}
                                                                               ),
                                                                  width={'size': 1, 'offset': 0},
                                                                  ),
                                                          dbc.Col(dcc.Dropdown(id='compare',
                                                                               options=load_ticks(),
                                                                               placeholder='Compare',
                                                                               multi=True,
                                                                               searchable=True,
                                                                               clearable=True,
                                                                               optionHeight=45,
                                                                               persistence=True,
                                                                               persistence_type='session',
                                                                               style={'background-color': '#F0F8FF'}
                                                                               ),
                                                                  width={'size': 3, 'offset': 0},
                                                                  style={'display': 'inline-block'},
                                                                  ),
                                                          dbc.Col(dcc.Dropdown(id='indicator_sel',
                                                                               options=[
                                                                                   {'label': 'Bollinger Bands',
                                                                                    'value': 'bbands'},
                                                                                   {'label': 'Exp MovAvg',
                                                                                    'value': 'ema'},
                                                                                   {'label': 'Ichimoku Cloud',
                                                                                    'value': 'ichi'},
                                                                                   {'label': 'MovAvg20',
                                                                                    'value': 'mov20'},
                                                                                   {'label': 'MovAvg50',
                                                                                    'value': 'mov50'},
                                                                                   {'label': 'MovAvg100',
                                                                                    'value': 'mov100'},
                                                                                   {'label': 'MovAvg200',
                                                                                    'value': 'mov200'},
                                                                                   {'label': 'Parabolic SAR',
                                                                                    'value': 'sar'},
                                                                                   {'label': 'Bullish Engulfing',
                                                                                    'value': 'bulleng'},
                                                                                   {'label': 'Bearish Engulfing',
                                                                                    'value': 'beareng'}
                                                                               ],
                                                                               placeholder='Indicators',
                                                                               optionHeight=35,
                                                                               multi=True,
                                                                               searchable=True,
                                                                               clearable=True,
                                                                               persistence=True,
                                                                               persistence_type='session',
                                                                               style={'background-color': '#F0F8FF'}
                                                                               ),
                                                                  width={'size': 3, 'offset': 0}
                                                                  )
                                                          ],
                                                         style={'marginBottom': 0, 'marginTop': 10}
                                                         ),
                                                 dbc.Row(dbc.Col(html.Div(id='displayhover', children='O-\tH-\tL-\tC-'),
                                                                 style={'marginBottom': 0, 'marginTop': 5,
                                                                        'fontSize': 20},
                                                                 )),
                                                 dbc.Row(dbc.Col(dcc.Graph(id='graph',
                                                                           config={'modeBarButtonsToAdd': ['drawline',
                                                                                                           'drawopenpath',
                                                                                                           'drawclosedpath',
                                                                                                           'drawcircle',
                                                                                                           'drawrect',
                                                                                                           'eraseshape'
                                                                                                           ],
                                                                                   'modeBarButtonsToRemove': ['lasso2d',
                                                                                                              'select2d',
                                                                                                              'hoverClosestCartesian',
                                                                                                              'hoverCompareCartesian'],
                                                                                   'scrollZoom': True,
                                                                                   'displayModeBar': True,
                                                                                   'editable': False,
                                                                                   'displaylogo': False
                                                                                   }
                                                                           ),
                                                                 width={'size': 12, 'offset': 0}
                                                                 )
                                                         ),
                                                 dcc.Interval(
                                                     id='interval-component',
                                                     interval=30 * 1000,
                                                     n_intervals=0
                                                 ),
                                                 dbc.Modal([
                                                     dbc.ModalHeader(html.H3("Welcome to Stock Market View!!")),
                                                     dbc.ModalBody(
                                                         "This application can be used to visualize NSE and BSE stocks with indicators and "
                                                         "to compare different stocks.")
                                                 ],
                                                     is_open=True)
                                                 ],
            style={'height': '35px',
                   'padding': '6px'},
            selected_style={'height': '35px',
                            'padding': '6px'}
            ),
    dcc.Tab(label='Multiple Time Frames', children=[dbc.Row(dbc.Col(dcc.Dropdown(id='tab2_tickinput',
                                                                                 options=load_ticks(),
                                                                                 placeholder='Stock',
                                                                                 value='^NSEI',
                                                                                 multi=False,
                                                                                 searchable=True,
                                                                                 clearable=False,
                                                                                 optionHeight=45,
                                                                                 persistence=True,
                                                                                 persistence_type='session',
                                                                                 style={'background-color': '#F0F8FF'}
                                                                                 ),
                                                                    width={'size': 4, 'offset': 4}
                                                                    ),
                                                            style={'marginBottom': 0, 'marginTop': 5}
                                                            ),
                                                    dbc.Row([dbc.Col(dcc.Dropdown(id='tab2-periodinput-A',
                                                                                  options=[
                                                                                      {'label': 'Period', 'value': 'p',
                                                                                       'disabled': True},
                                                                                      {'label': '15min',
                                                                                       'value': '15m'},
                                                                                      {'label': '1day', 'value': '1d'},
                                                                                      {'label': '5day', 'value': '5d'},
                                                                                      {'label': '1mon', 'value': '1mo'},
                                                                                      {'label': '3mon', 'value': '3mo'},
                                                                                      {'label': '6mon', 'value': '6mo'},
                                                                                      {'label': 'YTD', 'value': 'ytd'},
                                                                                      {'label': '1Y', 'value': '1y'},
                                                                                      {'label': '5Y', 'value': '5y'},
                                                                                      {'label': '10Y', 'value': '10y'},
                                                                                      {'label': 'All', 'value': 'max'}
                                                                                  ],
                                                                                  placeholder='Period',
                                                                                  value='1d',
                                                                                  optionHeight=30,
                                                                                  searchable=True,
                                                                                  clearable=False,
                                                                                  persistence=True,
                                                                                  persistence_type='session',
                                                                                  style={'background-color': '#F0F8FF'}
                                                                                  ),
                                                                     width={'size': 1, 'offset': 2}
                                                                     ),
                                                             dbc.Col(dcc.Dropdown(id='tab2-intervalinput-A',
                                                                                  options=[
                                                                                      {'label': 'Interval',
                                                                                       'value': 'i',
                                                                                       'disabled': True},
                                                                                      {'label': '1min', 'value': '1m'},
                                                                                      {'label': '2min', 'value': '2m'},
                                                                                      {'label': '5min', 'value': '5m'},
                                                                                      {'label': '15min',
                                                                                       'value': '15m'},
                                                                                      {'label': '30min',
                                                                                       'value': '30m'},
                                                                                      {'label': '1h', 'value': '60m'},
                                                                                      # {'label': '90min', 'value': '90m'},
                                                                                      {'label': 'D', 'value': '1d'},
                                                                                      # {'label': '5D', 'value': '5d'},
                                                                                      {'label': 'W', 'value': '1wk'},
                                                                                      {'label': 'M', 'value': '1mo'},
                                                                                      {'label': '3M', 'value': '3mo'}
                                                                                  ],
                                                                                  placeholder='Interval',
                                                                                  value='1m',
                                                                                  optionHeight=30,
                                                                                  searchable=True,
                                                                                  clearable=False,
                                                                                  persistence=True,
                                                                                  persistence_type='session',
                                                                                  style={'background-color': '#F0F8FF'}
                                                                                  ),
                                                                     width={'size': 1, 'offset': 0},
                                                                     ),
                                                             dbc.Col(dcc.Dropdown(id='tab2-periodinput-B',
                                                                                  options=[
                                                                                      {'label': 'Period', 'value': 'p',
                                                                                       'disabled': True},
                                                                                      {'label': '15min',
                                                                                       'value': '15m'},
                                                                                      {'label': '1day', 'value': '1d'},
                                                                                      {'label': '5day', 'value': '5d'},
                                                                                      {'label': '1mon', 'value': '1mo'},
                                                                                      {'label': '3mon', 'value': '3mo'},
                                                                                      {'label': '6mon', 'value': '6mo'},
                                                                                      {'label': 'YTD', 'value': 'ytd'},
                                                                                      {'label': '1Y', 'value': '1y'},
                                                                                      {'label': '5Y', 'value': '5y'},
                                                                                      {'label': '10Y', 'value': '10y'},
                                                                                      {'label': 'All', 'value': 'max'}
                                                                                  ],
                                                                                  placeholder='Period',
                                                                                  value='1y',
                                                                                  optionHeight=30,
                                                                                  searchable=True,
                                                                                  clearable=False,
                                                                                  persistence=True,
                                                                                  persistence_type='session',
                                                                                  style={'background-color': '#F0F8FF'}
                                                                                  ),
                                                                     width={'size': 1, 'offset': 4}
                                                                     ),
                                                             dbc.Col(dcc.Dropdown(id='tab2-intervalinput-B',
                                                                                  options=[
                                                                                      {'label': 'Interval',
                                                                                       'value': 'i',
                                                                                       'disabled': True},
                                                                                      {'label': '1min', 'value': '1m'},
                                                                                      {'label': '2min', 'value': '2m'},
                                                                                      {'label': '5min', 'value': '5m'},
                                                                                      {'label': '15min',
                                                                                       'value': '15m'},
                                                                                      {'label': '30min',
                                                                                       'value': '30m'},
                                                                                      {'label': '1h', 'value': '60m'},
                                                                                      # {'label': '90min', 'value': '90m'},
                                                                                      {'label': 'D', 'value': '1d'},
                                                                                      # {'label': '5D', 'value': '5d'},
                                                                                      {'label': 'W', 'value': '1wk'},
                                                                                      {'label': 'M', 'value': '1mo'},
                                                                                      {'label': '3M', 'value': '3mo'}
                                                                                  ],
                                                                                  placeholder='Interval',
                                                                                  value='1d',
                                                                                  optionHeight=30,
                                                                                  searchable=True,
                                                                                  clearable=False,
                                                                                  persistence=True,
                                                                                  persistence_type='session',
                                                                                  style={'background-color': '#F0F8FF'}
                                                                                  ),
                                                                     width={'size': 1, 'offset': 0},
                                                                     )
                                                             ],
                                                            style={'marginBottom': 0, 'marginTop': 10}
                                                            ),
                                                    dbc.Row([dbc.Col(dcc.Graph(id='tab2-graph-A',
                                                                               config={
                                                                                   'modeBarButtonsToAdd': ['drawline',
                                                                                                           'drawopenpath',
                                                                                                           'drawclosedpath',
                                                                                                           'drawcircle',
                                                                                                           'drawrect',
                                                                                                           'eraseshape'
                                                                                                           ],
                                                                                   'modeBarButtonsToRemove': ['lasso2d',
                                                                                                              'autoScale2d',
                                                                                                              'select2d',
                                                                                                              'hoverClosestCartesian',
                                                                                                              'hoverCompareCartesian',
                                                                                                              'toggleSpikelines'],
                                                                                   'scrollZoom': True,
                                                                                   # 'displayModeBar': True,
                                                                                   'editable': False,
                                                                                   'displaylogo': False
                                                                                   }
                                                                               ),
                                                                     width={'size': 6, 'offset': 0}
                                                                     ),
                                                             # dbc.Col(html.Hr(style={'width': '100px', 'height': '2px', 'display': 'inline-block'}),
                                                             #         width={'size': 1, 'offset': 0}
                                                             #         ),
                                                             dbc.Col(dcc.Graph(id='tab2-graph-B',
                                                                               config={
                                                                                   'modeBarButtonsToAdd': ['drawline',
                                                                                                           'drawopenpath',
                                                                                                           'drawclosedpath',
                                                                                                           'drawcircle',
                                                                                                           'drawrect',
                                                                                                           'eraseshape'
                                                                                                           ],
                                                                                   'modeBarButtonsToRemove': ['lasso2d',
                                                                                                              'autoScale2d',
                                                                                                              'select2d',
                                                                                                              'hoverClosestCartesian',
                                                                                                              'hoverCompareCartesian',
                                                                                                              'toggleSpikelines'],
                                                                                   'scrollZoom': True,
                                                                                   # 'displayModeBar': True,
                                                                                   'editable': False,
                                                                                   'displaylogo': False
                                                                                   }
                                                                               ),
                                                                     width={'size': 6, 'offset': 0}
                                                                     )
                                                             ]),
                                                    # html.Hr(),
                                                    dbc.Row([dbc.Col(dcc.Dropdown(id='tab2-periodinput-C',
                                                                                  options=[
                                                                                      {'label': 'Period', 'value': 'p',
                                                                                       'disabled': True},
                                                                                      {'label': '15min',
                                                                                       'value': '15m'},
                                                                                      {'label': '1day', 'value': '1d'},
                                                                                      {'label': '5day', 'value': '5d'},
                                                                                      {'label': '1mon', 'value': '1mo'},
                                                                                      {'label': '3mon', 'value': '3mo'},
                                                                                      {'label': '6mon', 'value': '6mo'},
                                                                                      {'label': 'YTD', 'value': 'ytd'},
                                                                                      {'label': '1Y', 'value': '1y'},
                                                                                      {'label': '5Y', 'value': '5y'},
                                                                                      {'label': '10Y', 'value': '10y'},
                                                                                      {'label': 'All', 'value': 'max'}
                                                                                  ],
                                                                                  placeholder='Period',
                                                                                  value='10y',
                                                                                  optionHeight=30,
                                                                                  searchable=True,
                                                                                  clearable=False,
                                                                                  persistence=True,
                                                                                  persistence_type='session',
                                                                                  style={'background-color': '#F0F8FF'}
                                                                                  ),
                                                                     width={'size': 1, 'offset': 5}
                                                                     ),
                                                             dbc.Col(dcc.Dropdown(id='tab2-intervalinput-C',
                                                                                  options=[
                                                                                      {'label': 'Interval',
                                                                                       'value': 'i',
                                                                                       'disabled': True},
                                                                                      {'label': '1min', 'value': '1m'},
                                                                                      {'label': '2min', 'value': '2m'},
                                                                                      {'label': '5min', 'value': '5m'},
                                                                                      {'label': '15min',
                                                                                       'value': '15m'},
                                                                                      {'label': '30min',
                                                                                       'value': '30m'},
                                                                                      {'label': '1h', 'value': '60m'},
                                                                                      # {'label': '90min', 'value': '90m'},
                                                                                      {'label': 'D', 'value': '1d'},
                                                                                      # {'label': '5D', 'value': '5d'},
                                                                                      {'label': 'W', 'value': '1wk'},
                                                                                      {'label': 'M', 'value': '1mo'},
                                                                                      {'label': '3M', 'value': '3mo'}
                                                                                  ],
                                                                                  placeholder='Interval',
                                                                                  value='1wk',
                                                                                  optionHeight=30,
                                                                                  searchable=True,
                                                                                  clearable=False,
                                                                                  persistence=True,
                                                                                  persistence_type='session',
                                                                                  style={'background-color': '#F0F8FF'}
                                                                                  ),
                                                                     width={'size': 1, 'offset': 0},
                                                                     )
                                                             ]),
                                                    dbc.Row(dbc.Col(dcc.Graph(id='tab2-graph-C',
                                                                              config={
                                                                                  'modeBarButtonsToAdd': ['drawline',
                                                                                                          'drawopenpath',
                                                                                                          'drawclosedpath',
                                                                                                          'drawcircle',
                                                                                                          'drawrect',
                                                                                                          'eraseshape'
                                                                                                          ],
                                                                                  'modeBarButtonsToRemove': ['lasso2d',
                                                                                                             'autoScale2d',
                                                                                                             'select2d',
                                                                                                             'hoverClosestCartesian',
                                                                                                             'hoverCompareCartesian',
                                                                                                             'toggleSpikelines'],
                                                                                  'scrollZoom': True,
                                                                                  # 'displayModeBar': True,
                                                                                  'editable': False,
                                                                                  'displaylogo': False
                                                                                  }
                                                                              ),
                                                                    width={'size': 12, 'offset': 0}
                                                                    ),
                                                            ),
                                                    dcc.Interval(id='tab2-interval-component',
                                                                 interval=30 * 1000,
                                                                 n_intervals=0
                                                                 ),
                                                    ],
            style={'height': '35px',
                   'padding': '6px'},
            selected_style={'height': '35px',
                            'padding': '6px'})],
    style={'height': '35px'},
    colors={
        "border": "white",
        "primary": "#1da1f2",
        "background": "#F0F8FF"
    }
)])


@app.callback(
    Output(component_id='graph', component_property='figure'),
    [Input(component_id='tickinput', component_property='value'),
     Input(component_id='periodinput', component_property='value'),
     Input(component_id='intervalinput', component_property='value'),
     Input(component_id='interval-component', component_property='n_intervals'),
     Input(component_id='indicator_sel', component_property='value'),
     Input(component_id='compare', component_property='value')],
    # prevent_initial_call=True
)
def callback1(tick, period, interval, n, indicator_sel, compare):
    global df
    df = load_data(period, interval, tick, compare)

    trace = {
        'type': 'candlestick',
        'open': df.Open,
        'high': df.High,
        'low': df.Low,
        'close': df.Close,
        'x': df.index,
        'name': tick.upper(),
        'hoverinfo': 'x'
    }

    layout = go.Layout({
        'xaxis_title': 'Time',
        # 'yaxis_title': 'Price',
        'xaxis': {
            # 'type': 'category',
            'showspikes': True,
            'spikemode': 'across',
            'spikesnap': 'cursor',
            'spikecolor': 'black',
            'spikethickness': 1
        },
        'yaxis': {
            'showspikes': True,
            'spikemode': 'across',
            'spikesnap': 'cursor',
            'spikecolor': 'black',
            'spikethickness': 1,
            'side': 'right'
        },
        'width': 1500,
        'height': 700,
        'dragmode': 'pan',
        'hovermode': 'x',
        'xaxis_rangeslider_visible': False,
        'modebar': {
            'orientation': 'v'},
        'uirevision': (period + interval + tick + str(compare)),
        'spikedistance': -1, 'hoverdistance': 100,
        'template': 'plotly_white',
        'legend': {
            'orientation': 'h'
        },
        'margin': {
            'l': 80, 'r': 80, 't': 20, 'b': 80
        },
        # 'paper_bgcolor': "#19334d",
        # 'plot_bgcolor': "#d8e6f3"
    })

    fig = go.Figure(data=trace, layout=layout)

    if compare is not None and compare != []:
        for c in compare:
            dfc = load_data(period, interval, c)
            dfc = dfc - dfc['Close'].iloc[0]
            comptrace = {
                'x': dfc.index,
                'y': dfc.Close,
                'type': 'scatter',
                'mode': 'lines',
                'line': {
                    'width': 1,
                    'color': 'green'
                },
                'hoverinfo': 'skip',
                'name': c.upper()

            }
            fig.add_trace(comptrace)

    if indicator_sel is not None:
        df['Engulfing'] = talib.CDLENGULFING(df['Open'], df['High'], df['Low'], df['Close'])
        for ind in indicator_sel:
            if ind == 'mov20':
                trace_mov20 = {
                    'x': df.index,
                    'y': talib.MA(df['Close'], timeperiod=20, matype=0),
                    'type': 'scatter',
                    'mode': 'lines',
                    'line': {
                        'width': 1,
                        'color': 'fuchsia'
                    },
                    'name': 'MovAvg20',
                    'hoverinfo': 'skip'
                }
                fig.add_trace(trace_mov20)
            elif ind == 'mov50':
                trace_mov50 = {
                    'x': df.index,
                    'y': talib.MA(df['Close'], timeperiod=50, matype=0),
                    'type': 'scatter',
                    'mode': 'lines',
                    'line': {
                        'width': 1,
                        'color': 'red'
                    },
                    'name': 'MovAvg50',
                    'hoverinfo': 'skip'
                }
                fig.add_trace(trace_mov50)
            elif ind == 'mov100':
                trace_mov100 = {
                    'x': df.index,
                    'y': talib.MA(df['Close'], timeperiod=100, matype=0),
                    'type': 'scatter',
                    'mode': 'lines',
                    'line': {
                        'width': 1,
                        'color': 'green'
                    },
                    'name': 'MovAvg100',
                    'hoverinfo': 'skip'
                }
                fig.add_trace(trace_mov100)
            elif ind == 'mov200':
                trace_mov200 = {
                    'x': df.index,
                    'y': talib.MA(df['Close'], timeperiod=200, matype=0),
                    'type': 'scatter',
                    'mode': 'lines',
                    'line': {
                        'width': 1,
                        'color': 'yellow'
                    },
                    'name': 'MovAvg200',
                    'hoverinfo': 'skip'
                }
                fig.add_trace(trace_mov200)
            elif ind == 'bbands':
                upperband, middleband, lowerband = talib.BBANDS(df['Close'], timeperiod=20, nbdevup=2, nbdevdn=2,
                                                                matype=0)
                trace_bbandlow = {
                    'x': df.index,
                    'y': lowerband,
                    'type': 'scatter',
                    'mode': 'lines',
                    'line': {
                        'width': 1,
                        'color': 'green'
                    },
                    'name': 'BBlow',
                    'hoverinfo': 'skip'
                }
                fig.add_trace(trace_bbandlow)
                trace_bbandup = {
                    'x': df.index,
                    'y': upperband,
                    'type': 'scatter',
                    'mode': 'lines',
                    'line': {
                        'width': 1,
                        'color': 'green'
                    },
                    'fill': 'tonexty',
                    'fillcolor': 'rgba(173,204,255,0.2)',
                    'name': 'BBup',
                    'hoverinfo': 'skip'
                }
                fig.add_trace(trace_bbandup)
                trace_bbandmid = {
                    'x': df.index,
                    'y': middleband,
                    'type': 'scatter',
                    'mode': 'lines',
                    'line': {
                        'width': 1,
                        'color': 'brown'
                    },
                    'name': 'BBmid',
                    'hoverinfo': 'skip'
                }
                fig.add_trace(trace_bbandmid)
            elif ind == 'ema':
                trace_ema = {
                    'x': df.index,
                    'y': talib.EMA(df['Close'], timeperiod=9),
                    'type': 'scatter',
                    'mode': 'lines',
                    'line': {
                        'width': 1,
                        'color': 'purple'
                    },
                    'name': 'EMA',
                    'hoverinfo': 'skip'
                }
                fig.add_trace(trace_ema)
            elif ind == 'sar':
                trace_sar = {
                    'x': df.index,
                    'y': talib.SAR(df['High'], df['Close'], acceleration=0.02, maximum=0.2),
                    'type': 'scatter',
                    'mode': 'markers',
                    'marker': {
                        'size': 3,
                        'color': 'orange'
                    },
                    'name': 'SAR',
                    'hoverinfo': 'skip'

                }
                fig.add_trace(trace_sar)
            elif ind == 'ichi':
                tenkan_sen = (df['High'].rolling(window=9).max() + df['Low'].rolling(window=9).min()) / 2
                kijun_sen = (df['High'].rolling(window=26).max() + df['Low'].rolling(window=26).min()) / 2
                senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(26)
                senkou_span_b = ((df['High'].rolling(window=52).max() + df['Low'].rolling(window=52).min()) / 2).shift(
                    26)
                chikou_span = df['Close'].shift(-26)
                trace_tenkan = {
                    'x': df.index,
                    'y': tenkan_sen,
                    'type': 'scatter',
                    'mode': 'lines',
                    'line': {
                        'width': 1,
                        'color': 'cyan'
                    },
                    'name': 'tenkan_sen',
                    'hoverinfo': 'skip'
                }
                fig.add_trace(trace_tenkan)
                trace_kijun = {
                    'x': df.index,
                    'y': kijun_sen,
                    'type': 'scatter',
                    'mode': 'lines',
                    'line': {
                        'width': 1,
                        'color': 'maroon'
                    },
                    'name': 'kijun_sen',
                    'hoverinfo': 'skip'
                }
                fig.add_trace(trace_kijun)
                trace_senkou_span_a = {
                    'x': df.index,
                    'y': senkou_span_a,
                    'type': 'scatter',
                    'mode': 'lines',
                    'line': {
                        'width': 1,
                        'color': 'green'
                    },
                    'name': 'senkou_span_a',
                    'hoverinfo': 'skip'
                }
                fig.add_trace(trace_senkou_span_a)
                trace_senkou_span_b = {
                    'x': df.index,
                    'y': senkou_span_b,
                    'type': 'scatter',
                    'mode': 'lines',
                    'line': {
                        'width': 1,
                        'color': 'red'
                    },
                    'fill': 'tonexty',
                    'fillcolor': 'rgba(173,204,255,0.2)',
                    'name': 'senkou_span_b',
                    'hoverinfo': 'skip'
                }
                fig.add_trace(trace_senkou_span_b)
                trace_chikou_span = {
                    'x': df.index,
                    'y': chikou_span,
                    'type': 'scatter',
                    'mode': 'lines',
                    'line': {
                        'width': 1,
                        'color': 'green'
                    },
                    'name': 'chikou_span',
                    'hoverinfo': 'skip'
                }
                fig.add_trace(trace_chikou_span)
            elif ind == 'bulleng':
                for i, j in df.iterrows():
                    if j['Engulfing'] != 100:
                        k = i
                        continue
                    else:
                        fig.add_vrect(
                            x0=k, x1=i,
                            annotation_text="BE", annotation_position="top left",
                            fillcolor="green", opacity=0.25,
                            line_width=0, line_color='green')
            elif ind == 'beareng':
                for i, j in df.iterrows():
                    if j['Engulfing'] != -100:
                        k = i
                        continue
                    else:
                        fig.add_vrect(
                            x0=k, x1=i,
                            # x0=k-datetime.timedelta(hours=6), x1=i+datetime.timedelta(hours=6),
                            annotation_text="BE", annotation_position="top left",
                            fillcolor="red", opacity=0.25,
                            line_width=0, line_color='red'
                        )
    fig = rangebreak(fig, period, interval)
    return fig


@app.callback(Output(component_id='intervalinput', component_property='value'),
              Input(component_id='periodinput', component_property='value'),
              # prevent_initial_call=True
              )
def update_interval(p):
    return period_int(p)


@app.callback([Output('displayhover', 'children'),
               Output('displayhover', 'style')],
              Input('graph', 'hoverData'),
              prevent_initial_call=True
              )
def display_hover_data(hoverData):
    open = round(df.Open[df.index == hoverData["points"][0]['x']].sum(), 2)
    high = round(df.High[df.index == hoverData["points"][0]['x']].sum(), 2)
    low = round(df.Low[df.index == hoverData["points"][0]['x']].sum(), 2)
    close = round(df.Close[df.index == hoverData["points"][0]['x']].sum(), 2)
    ohlc = 'O-' + str(open) + '\t' + 'H-' + str(high) + '\t' + 'L-' + str(low) + '\t' + 'C-' + str(close)
    if close > open:
        color = 'forestgreen'
    else:
        color = 'red'
    style = {'color': color}
    return ohlc, style


@app.callback([Output('tab2-graph-A', 'figure'),
               Output('tab2-graph-B', 'figure'),
               Output('tab2-graph-C', 'figure')],
              [Input('tab2_tickinput', 'value'),
               Input('tab2-periodinput-A', 'value'),
               Input('tab2-intervalinput-A', 'value'),
               Input('tab2-periodinput-B', 'value'),
               Input('tab2-intervalinput-B', 'value'),
               Input('tab2-periodinput-C', 'value'),
               Input('tab2-intervalinput-C', 'value'),
               Input('tab2-interval-component', 'n_intervals')],
              # prevent_initial_call=True
              )
def tab2_callback(tick2, periodA, intervalA, periodB, intervalB, periodC, intervalC, n):
    dfA = load_data(periodA, intervalA, tick2)
    dfB = load_data(periodB, intervalB, tick2)
    dfC = load_data(periodC, intervalC, tick2)
    layoutA = go.Layout({
        'xaxis_title': 'Time',
        # 'yaxis_title': 'Price',
        'xaxis': {
            'showspikes': True,
            'spikemode': 'across',
            'spikesnap': 'cursor',
            'spikecolor': 'black',
            'spikethickness': 1
        },
        'yaxis': {
            'showspikes': True,
            'spikemode': 'across',
            'spikesnap': 'cursor',
            'spikecolor': 'black',
            'spikethickness': 1,
            'side': 'right'
        },
        'width': 750,
        'height': 300,
        'dragmode': 'pan',
        'hovermode': 'x',
        'xaxis_rangeslider_visible': False,
        'modebar': {
            'orientation': 'v'},
        'uirevision': (periodA + intervalA + tick2),
        'spikedistance': -1, 'hoverdistance': 100,
        'template': 'plotly_white',
        'legend': {
            'orientation': 'h'
        },
        'margin': {
            'l': 80, 'r': 80, 't': 20, 'b': 80
        },
    })

    dataA = {
        'type': 'candlestick',
        'open': dfA.Open,
        'high': dfA.High,
        'low': dfA.Low,
        'close': dfA.Close,
        'x': dfA.index,
        'name': tick2.upper(),
        'hoverinfo': 'x'
    }
    figA = go.Figure(data=dataA, layout=layoutA)

    layoutB = go.Layout({
        'xaxis_title': 'Time',
        # 'yaxis_title': 'Price',
        'xaxis': {
            'showspikes': True,
            'spikemode': 'across',
            'spikesnap': 'cursor',
            'spikecolor': 'black',
            'spikethickness': 1
        },
        'yaxis': {
            'showspikes': True,
            'spikemode': 'across',
            'spikesnap': 'cursor',
            'spikecolor': 'black',
            'spikethickness': 1,
            'side': 'right'
        },
        'width': 750,
        'height': 300,
        'dragmode': 'pan',
        'hovermode': 'x',
        'xaxis_rangeslider_visible': False,
        'modebar': {
            'orientation': 'v'},
        'uirevision': (periodB + intervalB + tick2),
        'spikedistance': -1, 'hoverdistance': 100,
        'template': 'plotly_white',
        'legend': {
            'orientation': 'h'
        },
        'margin': {
            'l': 80, 'r': 80, 't': 20, 'b': 80
        },
    })

    dataB = {
        'type': 'candlestick',
        'open': dfB.Open,
        'high': dfB.High,
        'low': dfB.Low,
        'close': dfB.Close,
        'x': dfB.index,
        'name': tick2.upper(),
        'hoverinfo': 'x'
    }
    figB = go.Figure(data=dataB, layout=layoutB)

    layoutC = go.Layout({
        'xaxis_title': 'Time',
        # 'yaxis_title': 'Price',
        'xaxis': {
            'showspikes': True,
            'spikemode': 'across',
            'spikesnap': 'cursor',
            'spikecolor': 'black',
            'spikethickness': 1
        },
        'yaxis': {
            'showspikes': True,
            'spikemode': 'across',
            'spikesnap': 'cursor',
            'spikecolor': 'black',
            'spikethickness': 1,
            'side': 'right'
        },
        'width': 1500,
        'height': 350,
        'dragmode': 'pan',
        'hovermode': 'x',
        'xaxis_rangeslider_visible': False,
        'modebar': {
            'orientation': 'v'},
        'uirevision': (periodB + intervalB + tick2),
        'spikedistance': -1, 'hoverdistance': 100,
        'template': 'plotly_white',
        'legend': {
            'orientation': 'h'
        },
        'margin': {
            'l': 80, 'r': 80, 't': 20, 'b': 80
        },
    })

    dataC = {
        'type': 'candlestick',
        'open': dfC.Open,
        'high': dfC.High,
        'low': dfC.Low,
        'close': dfC.Close,
        'x': dfC.index,
        'name': tick2.upper(),
        'hoverinfo': 'x'
    }
    figC = go.Figure(data=dataC, layout=layoutC)

    figA = rangebreak(figA, periodA, intervalA)
    figB = rangebreak(figB, periodB, intervalB)
    figC = rangebreak(figC, periodC, intervalC)

    return figA, figB, figC


@app.callback([Output('tab2-intervalinput-A', 'value'),
               Output('tab2-intervalinput-B', 'value'),
               Output('tab2-intervalinput-C', 'value')],
              [Input('tab2-periodinput-A', 'value'),
               Input('tab2-periodinput-B', 'value'),
               Input('tab2-periodinput-C', 'value')],
              # prevent_initial_call=True
              )
def tab2_update_interval(pA, pB, pC):
    return period_int(pA), period_int(pB), period_int(pC)


if __name__ == '__main__':
    app.run_server(debug=True)
