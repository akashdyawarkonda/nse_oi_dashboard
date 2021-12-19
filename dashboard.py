from nsepython import *
import numpy as np 
import dash
import dash_auth
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import dash_table
import dash_bootstrap_components as dbc
import pandas as pd

graph_data=[]

def get_expiryData(exp_date = None, symbol = 'NIFTY', get_expiryDate = False):

	strikePrice=[]
	expiryData =[]
	x_dates =[]
	result = nse_optionchain_scrapper(symbol)
	data = (result['records']['data'])
	for x in data:
		if x['expiryDate'] == exp_date:
			strikePrice.append(x['strikePrice'])
			expiryData.append(x)
			
	if get_expiryDate:
		expiryDate = result['records']['expiryDates']
		for date in expiryDate:
			x_dates.append(date)
		return x_dates
	else:
		return strikePrice, expiryData
			# print(strikePrice, PCR)


def calculations(exp_date, symbol):
	data =[]
	current_price = round(nse_quote_ltp(symbol),2)
	strikePrice, expiryData = get_expiryData(exp_date, symbol)

	stp_arr = np.array(strikePrice)

	diff_arr = np.absolute(stp_arr - int(current_price))
	index = diff_arr.argmin()

	nearest_stp = stp_arr[index]

		# 
	stp_window_size = 10
	stp_window = []
	# print(expiryData)

	for i,x in enumerate(strikePrice):
		if x == nearest_stp:
			for y in range(0, stp_window_size):
				stp_window.append(strikePrice[i-y])
				stp_window.append(strikePrice[i+y])

				# print(i)
				# print(strikePrice[i-10])
				# print(strikePrice[i+10])
		
	stp_window = list(set(stp_window))
	# print(stp_window)
	# print(type(expiryData))
	# print(expiryData)

		
	for x in expiryData:
		if x['strikePrice'] in stp_window:
			# print(x['strikePrice'], x['PE']['openInterest'])
			STR_PRC = x['strikePrice']
			PE_OI = x['PE']['openInterest']
			PE_OI_Ch = x['PE']['changeinOpenInterest']
			PE_volume = x['PE']['totalTradedVolume']
			PE_LTP = x['PE']['lastPrice']

			graph_data.append([STR_PRC, 'PUTS OI', PE_OI])



			CE_OI = x['CE']['openInterest']
			CE_OI_Ch = x['CE']['changeinOpenInterest']
			CE_volume = x['CE']['totalTradedVolume']
			CE_LTP = x['CE']['lastPrice']
			graph_data.append([STR_PRC,'CALLS OI', CE_OI])

			if PE_OI > 0 and CE_OI > 0:
				PCR = PE_OI/CE_OI
			else:
				PCR = 0

			STR_PCR = str(STR_PRC) + ' - ('+ str(round(PCR,2)) + ')'

			# data.append([STR_PRC, CE_OI, PE_OI, round(PCR, 2), CE_OI_Ch, PE_OI_Ch, CE_volume,  PE_volume])
			data.append([STR_PRC, round(PCR, 2), CE_volume, CE_OI_Ch, CE_OI, STR_PCR, PE_OI, PE_OI_Ch, PE_volume])



	# ng = pd.DataFrame(data, columns=['Strike Price', 'CE OI', 'PE OI', 'PCR', 'CE OI CHNG', 'PE OI CHNG', 'CALLS VOL', 'PUTS VOL'])
	ng = pd.DataFrame(data, columns=['Strike Price', 'PCR', 'CALLS VOL','CE OI CHNG', 'CE OI', 'Strike Price - (PCR)', 'PE OI', 'PE OI CHNG','PUTS VOL'])
	# print(ng)

	# gf = pd.DataFrame(graph_data, columns=['Strike Price', 'Side', 'OI'])
	# print(gf)

	return ng

exp_dates = get_expiryData(get_expiryDate = True)
app = dash.Dash(__name__)
suppress_callback_exceptions=True

colors = {
    'background': '#111222',
    'text': 'white'
}
app.layout=html.Div(
    [
    	dcc.Interval(
                    id='intervalNG',
                    interval = 1*10000,
                    n_intervals=0
                                      
                ),
    	html.Div(
            children='NSE Dashboard',
            style={
                        'textAlign': 'center',
                        'color': colors['text'],
                        'fontSize':45,
                        'background': '#111222'
                        }
            
            ),
          html.Div([
        	html.Div([

        		html.Div(
		            [
		            html.Div(
		            	children='NIFTY',
		            style={
		                        'textAlign': 'center',
		                        'color': colors['text'],
		                        'fontSize':30,
		                        'background': '#111222',
		                        'display': 'inline-block',
		                        'width':'50%',
		                        }),

		            html.Div([
		            	dcc.Dropdown(id="nifty-dynamic-dropdown",

		            		options=[
		                        {"label": i, "value": i} for i in exp_dates
		                    ],
		                    value = exp_dates[0]
		            		),

		            	],
		            	style={'display':'inline-block',
		            			 'width':'50%',
		            			  'marginBottom':'-8px',
		            			  
		            			   }
		            	)
		            ]
		            
		            ),

        		html.Div([
        			dash_table.DataTable(
                            id='nse_oi',
                            style_header={'backgroundColor': 'rgb(30, 30, 30)',
                                          'fontWeight':'bold',
                                          'color': colors['text'],
                                          'textAlign':'center'
                                          },
                            fixed_rows={'headers': True},
				            style_cell={'backgroundColor': 'rgb(50, 50, 50)',
				                                'color': colors['text'],
				                                'textAlign':'center'
				                                },

				            style_data_conditional=[
						        {
						            'if': {
						            	'row_index':10,
						                
						            },
						            'backgroundColor': 'orange',
						            'color': 'white'
						        },

						        {
					            'if': {
					                'filter_query': '{CE OI} > {PE OI}', # comparing columns to each other
					                'column_id': 'Strike Price - (PCR)'
					            },
					            'backgroundColor': 'red',
					            'color': 'white'
					        },
					        {
					            'if': {
					                'filter_query': '{CE OI} < {PE OI}', # comparing columns to each other
					                'column_id': 'Strike Price - (PCR)'
					            },
					            'backgroundColor': 'green',
					            'color': 'white'
					        },]

                            
                            )])
                          
                          ],

                          style={'width': '49%', 'display': 'inline-block','marginTop':'0.5%','marginLeft':'0.5%'},
                        ),
        	html.Div([

        		html.Div(
		            [
		            html.Div(
		            	children='BANKNIFTY',
		            style={
		                        'textAlign': 'center',
		                        'color': colors['text'],
		                        'fontSize':30,
		                        'background': '#111222',
		                        'display': 'inline-block',
		                        'width':'50%',
		                        }),

		            html.Div([
		            	dcc.Dropdown(id="banknifty-dynamic-dropdown",

		            		options=[
		                        {"label": i, "value": i} for i in exp_dates
		                    ],
		                    value = exp_dates[0]
		            		),

		            	],
		            	style={'display':'inline-block',
		            			 'width':'50%',
		            			  'marginBottom':'-8px',
		            			  
		            			   }
		            	)
		            ]
		            
		            ),

        		html.Div([
        			dash_table.DataTable(
                            id='nse_oi1',
                            style_header={'backgroundColor': 'rgb(30, 30, 30)',
                                          'fontWeight':'bold',
                                          'color': colors['text'],
                                          'textAlign':'center'
                                          },
                            fixed_rows={'headers': True},
				            style_cell={'backgroundColor': 'rgb(50, 50, 50)',
				                                'color': colors['text'],
				                                'textAlign':'center'
				                                },

				            style_data_conditional=[
						        {
						            'if': {
						            	'row_index':10,
						                
						            },
						            'backgroundColor': 'orange',
						            'color': 'white'
						        },

						        {
					            'if': {
					                'filter_query': '{CE OI} > {PE OI}', # comparing columns to each other
					                'column_id': 'Strike Price - (PCR)'
					            },
					            'backgroundColor': 'red',
					            'color': 'white'
					        },
					        {
					            'if': {
					                'filter_query': '{CE OI} < {PE OI}', # comparing columns to each other
					                'column_id': 'Strike Price - (PCR)'
					            },
					            'backgroundColor': 'green',
					            'color': 'white'
					        },]

                            
                            )])
                          
                          ],

                          style={'width': '49%', 'display': 'inline-block','marginTop':'0.5%','marginLeft':'0.5%'},
                        ),

        	]),

       html.Div([

       	html.Div([
       		dcc.Graph(id = 'oi_chart')

       		],
       		style={'width': '49%', 'display': 'inline-block','marginTop':'0.5%','marginLeft':'0.5%'},
       		),

       	html.Div([
       		dcc.Graph(id = 'oi_chart1')

       		],
       		style={'width': '49%', 'display': 'inline-block','marginTop':'0.5%','marginLeft':'0.5%'},
       		)

       	])    




        ])

#nifty dropdown call back
# @app.callback(
#     Output("nifty-dynamic-dropdown", "options"),
#     Input("nifty-dynamic-dropdown", "search_value")
# )
# def update_options(search_value):
# 	dates = get_expiryData(get_expiryDate = True)
# 	# print(dates)
# 	if not search_value:
# 		raise PreventUpdate
# 	return [o for o in dates if search_value in o["label"]]


@app.callback(
    [Output('nse_oi', 'data'),
    Output('nse_oi', 'columns')],
    [Input('intervalNG','n_intervals'),
    Input('nifty-dynamic-dropdown','value')]
)
def update_output(n, value):

	ng = calculations(value, 'NIFTY')
	ng = ng.drop(['Strike Price', 'PCR'], axis = 1)
	data=ng.to_dict("rows")
	columns=[{"id": x, "name": x} for x in ng.columns]
		
	return  data, columns


@app.callback(
    [Output('nse_oi1', 'data'),
    Output('nse_oi1', 'columns')],
    [Input('intervalNG','n_intervals'),
    Input('banknifty-dynamic-dropdown','value')]
)
def update_output(n,value):

	ng = calculations(exp_date = value, symbol = 'BANKNIFTY')
	ng = ng.drop(['Strike Price', 'PCR'], axis = 1)

	data=ng.to_dict("rows")
	columns=[{"id": x, "name": x} for x in ng.columns]
		
	return  data, columns
     

@app.callback(Output('oi_chart1','figure'),
              [Input('intervalNG','n_intervals'),
              Input('banknifty-dynamic-dropdown','value')])



def update_graph(n, value):
	ng = calculations(exp_date = value, symbol='BANKNIFTY')
	fig={'data':
                              [
                                {'x':ng['Strike Price'],'y':ng['CE OI'], 'type':'bar', 'name':'Calls OI', 'base':0,'marker' : { "color" : "green"}},
                                {'x':ng['Strike Price'],'y':ng['PE OI'], 'type':'bar', 'name':'Puts OI', 'base':0, 'width':40, 'marker' : { "color" : 'red'}},
                                {'x':ng['Strike Price'],'y':ng['PCR'], 'type':'markers+lines', 'name':'PCR', 'base':0, 'marker' : { "color" : colors['text'], 'yaxis':{'autorange':True}}, 'showscale':False},

                                
                              ],
                              'layout':{
                                  'title':'BANKNIFTY OI Data',
                             		'barmode':'stack',
                             		'hovermode': 'x',
                                  'plot_bgcolor':colors['background'],
                                  'paper_bgcolor':colors['background'],
                                  'font':{
                                      'color':colors['text']
                                  },
                                  
                                  'xaxis':{
                                      'title':'Strike Price'

                                  },
                                  
                              }
                              }
	return fig

@app.callback(Output('oi_chart','figure'),
              [Input('intervalNG','n_intervals'),
              Input('nifty-dynamic-dropdown','value')])



def update_graph(n, value):
	
	ng = calculations(exp_date = value, symbol='NIFTY')
	fig={'data':
                              [
                                {'x':ng['Strike Price'],'y':ng['CE OI'], 'type':'bar', 'name':'Calls OI', 'base':0,'marker' : { "color" : "green"}},
                                {'x':ng['Strike Price'],'y':ng['PE OI'], 'type':'bar', 'name':'Puts OI', 'base':0, 'width':20, 'marker' : { "color" : 'red'}},
                                {'x':ng['Strike Price'],'y':ng['PCR'], 'type':'markers+lines', 'name':'PCR', 'base':0, 'marker' : { "color" : colors['text'], 'yaxis':{'autorange':True}}, 'showscale':False},

                                
                              ],
                              'layout':{
                                  'title':'NIFTY OI Data',
                             		'barmode':'stack',
                             		'hovermode': 'x',
                                  'plot_bgcolor':colors['background'],
                                  'paper_bgcolor':colors['background'],
                                  'font':{
                                      'color':colors['text']
                                  },
                                  
                                  'xaxis':{
                                      'title':'Strike Price'

                                  },
                                  
                              }
                              }
	return fig

if __name__ == '__main__':

    app.run_server(debug=True, use_reloader=True)
