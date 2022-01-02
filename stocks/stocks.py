
from datetime import datetime
import holoviews as hv
from holoviews import dim
import nasdaqdatalink
import numpy as np
import os
import pandas as pd
import pickle
import quandl


class Stocks():
    
    # popular exchanges
    EXCHANGES = ["BITFINEX", "BITSTAMP", "COINBASE", "ITBIT", "KRAKEN", "OKCOIN"]

    CURRENCIES = {
        'BCHARTS/BITFINEXUSD':  'BCHARTS-BITFINEXUSD.pkl',
        'BCHARTS/BITSTAMPUSD':  'BCHARTS-BITSTAMPUSD.pkl',
        'BCHARTS/COINBASEUSD':  'BCHARTS-COINBASEUSD.pkl',
        'BCHARTS/ITBITUSD':  'BCHARTS-ITBITUSD.pkl',
        'BCHARTS/KRAKENUSD':  'KRAKENUSD.pkl',
        'BCHARTS/OKCOINUSD':  'BCHARTS-OKCOINUSD.pkl',        
    }
    
    COINS = ['ETH','LTC','XRP','ETC','STR','DASH','SC','XMR','XEM']
    
    POLONIEX_URL = 'https://poloniex.com/public?command=returnChartData&currencyPair={}&start={}&end={}&period={}'
    
    def __init__(self, name=None):
        hv.extension('bokeh')

        quandl.ApiConfig.api_key = os.environ['QUANDL_API_KEY']
        self.price = {}
        # collate exchange data
        self.exchange_data = {}
        self.altcoin_data = {}


    def get_quandl_data(self, quandl_code:str, data_dir:str=None):
        """
        Provide price data for given quandl_code via caching mechanism 
        """
        if data_dir:
            cache_path = '{}/{}.pkl'.format(data_dir, quandl_code.replace('/','-'))
        else:
            cache_path = "{}.pkl".format(quandl_code).replace("/", "-")
        
        # load price data if it exists
        if os.path.exists(cache_path):
            with open(cache_path, "rb") as f:
                df = pd.DataFrame(pickle.load(f))
                df = df.replace(0, np.nan)
                print(f"Loaded {quandl_code} data from cache")
        # othewise cache the data
        else:
            print('Downloading {} from Quandl'.format(quandl_code))
            df = quandl.get(quandl_code, returns="pandas")
            # Remove "0" values
            df = df.replace(0, np.nan)
            df.to_pickle(cache_path)
            print(f"Cached {quandl_code} data to {cache_path}")
        return df
        
    def get_quandl_trace(self, quandl_code:str=None):
        if quandl_code:
            #trace = hv.Scatter(self.price[quandl_code], kdims=['Date'], vdims=['Weighted Price'])
            trace = hv.Curve((self.price[quandl_code].index, self.price[quandl_code]['Weighted Price']))
        else:
            #trace = hv.Scatter(self.price, kdims=['Date'], vdims=['Weighted Price'])
            trace = hv.Curve((self.price.index, self.price['Weighted Price']))
        overlay = (trace)
        overlay.opts(width=900, height=400, xrotation=45, title=' Price')#, legend_position='bottom_right')
        return overlay
    
    def merge(self, dataframes, col):
        '''
        Merge a single column of each dataframe into a new combined dataframe
        '''
        d = {}        
        # extract given col from each exchange dataframe
        for key in dataframes.keys():
            d[key] = dataframes[key][col]
            
        return pd.DataFrame(d)

    def get_quandl_traces(self):
        # setting up traces for plotting
        traces = []
        for cid in self.average_price.columns:
            #trace = hv.Scatter(self.average_price[cid], kdims=['Date'], vdims=[cid])
            trace = hv.Curve((self.average_price.index, self.average_price[cid]))
            traces.append(trace)

        print(len(traces))
        overlay = (traces[0] * traces[1] * traces[2] * traces[3] * traces[4] * traces[5])
        overlay.opts(width=900, height=400, logy=True, xrotation=45, title="Price by Exchange", legend_position='bottom_right')
        
        return overlay
    
    def save_trace(self, filename:str):
        #hv.save(overlay, filename, fmt='png')
        hv.output(self.overlay, backend='matplotlib', fig='svg')

    """def df_scatter(self, df, title, seperate_y_axis=False, y_axis_label='', scale='linear', initial_hide=False):
        '''Generate a scatter plot of the entire dataframe'''
        label_arr = list(df)
        series_arr = list(map(lambda col: df[col], label_arr))
        
        #layout = go.Layout(
        #    title=title,
        #    legend=dict(orientation="h"),
        #    xaxis=dict(type='date'),
        #    yaxis=dict(
        #        title=y_axis_label,
        #        showticklabels= not seperate_y_axis,
        #        type=scale
        #    )
        #)
        
        y_axis_config = dict(
            overlaying='y',
            showticklabels=False,
            type=scale )
        
        visibility = True #'visible'
        if initial_hide:
            visibility = 'legendonly'
            
        # Form Trace For Each Series
        trace_arr = []
        for index, series in enumerate(series_arr):
            trace = hv.scatter(
                x=series.index, 
                y=series, 
                name=label_arr[index],
                visible=visibility
            )
            
            # Add seperate axis for the series
            if seperate_y_axis:
                trace['yaxis'] = 'y{}'.format(index + 1)
                layout['yaxis{}'.format(index + 1)] = y_axis_config    
            trace_arr.append(trace)

        #fig = go.Figure(data=trace_arr, layout=layout)
        #py.iplot(fig)
        print(len(trace_arr))
        overlay = (trace_arr[0] * trace_arr[1] * trace_arr[2] * trace_arr[3] * trace_arr[4] * trace_arr[5])
        overlay.opts(width=900, height=400, legend_position='bottom_right')
        
        return overlay
    """
    
    def read_json(self, url, filename:None):
        '''Download and cache JSON data, return as a dataframe.'''
        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                df = pd.DataFrame(pickle.load(f))
                print('Loaded {} from cache'.format(filename))
        else:
            print('Downloading {}'.format(url))
            df = pd.read_json(url)
            if filename:
                df.to_pickle(filename)
                print('Cached response at {}'.format(filename))
        return df
        
    def get_crypto_data(self, poloniex_pair, start_date, end_date, period):
        '''Retrieve cryptocurrency data from poloniex'''
        url = self.POLONIEX_URL.format(poloniex_pair, start_date.timestamp(), end_date.timestamp(), period)
        df = self.read_json(url, poloniex_pair)
        df = df.set_index('date')
        return df
        
    def correlation_heatmap(self, df, title, absolute_bounds=True):
        '''Plot a correlation heatmap for the entire dataframe'''
        heatmap = hv.HeatMap(df.corr(method='pearson')).sort()
        #    z = df.corr(method='pearson'), #.as_matrix(),
        #    x = df.columns,
        #    y = df.columns,
        #    colorbar=dict(title='Pearson Coefficient'),
        #)
        
        #layout = go.Layout(title=title)
        
        #if absolute_bounds:
        #    heatmap['zmax'] = 1.0
        #    heatmap['zmin'] = -1.0
            
        #fig = go.Figure(data=[heatmap], layout=layout)
        #py.iplot(fig)
        #print(len(trace_arr))
        overlay = (heatmap)
        overlay.opts(width=900, height=400)#, legend_position='bottom_right')
        
        return overlay
