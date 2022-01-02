
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
    
    def __init__(self, name=None):
        hv.extension('bokeh')

        quandl.ApiConfig.api_key = os.environ['QUANDL_API_KEY']
        data_dir = 'data/'

    def get_quandl_data(self, quandl_code):
        """
        Provide price data for given quandl_code via caching mechanism 
        """
        cache_path = "{}.pkl".format(quandl_code).replace("/", "-")
        
        # load price data if it exists
        try:
            file = open(cache_path, "rb")
            df = pickle.load(file)
            print(f"Loaded {quandl_code} data from cache")
        # othewise cache the data
        except (OSError, IOError):
            df = quandl.get(quandl_code, returns="pandas")
            df.to_pickle(cache_path)
            print(f"Cached {quandl_code} data to {cache_path}")
        return df
        
    def get_quandl_data2(self, quandl_id):
        '''Download and cache Quandl dataseries'''
        cache_path = '{}{}.pkl'.format(data_dir, quandl_id.replace('/','-'))
        try:
            f = open(cache_path, 'rb')
            df = pickle.load(f)   
            print('Loaded {} from cache'.format(quandl_id))
        except (OSError, IOError) as e:
            print('Downloading {} from Quandl'.format(quandl_id))
            df = quandl.get(quandl_id, returns="pandas")
            df.to_pickle(cache_path)
            print('Cached {} at {}'.format(quandl_id, cache_path))
        return df
    
    def get_quandl_trace(self):
        btc_usd_price_kraken_trace = hv.Scatter(self.btc_usd_price_kraken, kdims=['Date'], vdims=['Weighted Price'])
        overlay = (btc_usd_price_kraken_trace)
        overlay.opts(width=900, height=400, legend_position='bottom_right')
        return overlay
    
    def merge_datafs(dataframes, labels, col):
        """
        Make dataframe which includes specified data from each exchanges dataframe
        """
        series_dict = {}
        
        # extract given col from each exchange dataframe
        for index in range(len(labels)):
            series_dict[labels[index]] = dataframes[index][col]
        return pd.DataFrame(series_dict)
        
    def merge_dfs_on_column(dataframes, labels, col):
        '''Merge a single column of each dataframe into a new combined dataframe'''
        series_dict = {}
        for index in range(len(dataframes)):
            series_dict[labels[index]] = dataframes[index][col]
            
        return pd.DataFrame(series_dict)

        
    def df_scatter(df, title, seperate_y_axis=False, y_axis_label='', scale='linear', initial_hide=False):
        '''Generate a scatter plot of the entire dataframe'''
        label_arr = list(df)
        series_arr = list(map(lambda col: df[col], label_arr))
        
        layout = go.Layout(
            title=title,
            legend=dict(orientation="h"),
            xaxis=dict(type='date'),
            yaxis=dict(
                title=y_axis_label,
                showticklabels= not seperate_y_axis,
                type=scale
            )
        )
        
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
            trace = go.Scatter(
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

        fig = go.Figure(data=trace_arr, layout=layout)
        py.iplot(fig)
        
    def get_json_data(json_url, file_name):
        '''Download and cache JSON data, return as a dataframe.'''
        cache_path = '{}{}.pkl'.format(data_dir, file_name)
        try:        
            f = open(cache_path, 'rb')
            df = pickle.load(f)   
            print('Loaded {} from cache'.format(file_name))
        except (OSError, IOError) as e:
            print('Downloading {}'.format(json_url))
            df = pd.read_json(json_url)
            df.to_pickle(cache_path)
            print('Cached response at {}'.format(cache_path))
        return df
        
    def get_crypto_data(poloniex_pair):
        '''Retrieve cryptocurrency data from poloniex'''
        json_url = base_polo_url.format(poloniex_pair, start_date.timestamp(), end_date.timestamp(), pediod)
        data_df = get_json_data(json_url, poloniex_pair)
        data_df = data_df.set_index('date')
        return data_df
        
    def correlation_heatmap(df, title, absolute_bounds=True):
        '''Plot a correlation heatmap for the entire dataframe'''
        heatmap = go.Heatmap(
            z = df.corr(method='pearson'), #.as_matrix(),
            x = df.columns,
            y = df.columns,
            colorbar=dict(title='Pearson Coefficient'),
        )
        
        layout = go.Layout(title=title)
        
        if absolute_bounds:
            heatmap['zmax'] = 1.0
            heatmap['zmin'] = -1.0
            
        fig = go.Figure(data=[heatmap], layout=layout)
        py.iplot(fig)
