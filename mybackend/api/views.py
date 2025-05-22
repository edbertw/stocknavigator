from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
import numpy as np
import yfinance as yf
import datetime
from datetime import date, timedelta
import plotly.express as px 
import plotly.io as pio
import plotly.graph_objects as go
import plotly.figure_factory as ff
from django.shortcuts import render

def index(request):
    return render(request, "index.html")


company_data = {
    'NVDA': {
        'name': 'NVIDIA',
        'description': 'NVIDIA is a leading manufacturer of GPUs for gaming and AI computing.',
        'logo': 'nvidia.png'
    },
    'NDAQ': {
        'name': 'NASDAQ',
        'description': 'NASDAQ is an American stock exchange, the second-largest in the world by market cap.',
        'logo': 'nasdaq.jpeg'
    },
    'TSLA': {
        'name': 'Tesla',
        'description': 'Tesla is a clean energy and electric vehicle company.',
        'logo': 'tesla.jpeg'
    },
    'HSBC': {
        'name': 'HSBC',
        'description': 'HSBC is one of the world\'s largest banking and financial services organizations.',
        'logo': 'hsbc.jpg'
    },
    'JPM': {
        'name': 'JP Morgan',
        'description': 'JP Morgan is a global leader in financial services offering solutions to corporations, institutions, and governments.',
        'logo': 'jpmorgan.png'
    }
}
@csrf_exempt
@api_view(['POST'])
def submit_stock(request):
    stock_symbol = request.data.get('stock_symbol')  # Get stock symbol from request
    company = company_data.get(stock_symbol)
    if company:
        current = date.today()
        end = current.strftime("%Y-%m-%d")
        start = (date.today() - timedelta(days = 365)).strftime("%Y-%m-%d")
        try:
            stock = yf.download(stock_symbol, start = start, end = end, progress = False,multi_level_index=False)
            #stock = stock.stack().reset_index().rename(index=str, columns={"level_1": "Symbol"}).sort_values(['Symbol','Date'])
            #stock = stock.reset_index()
            #print(stock)
            if stock.empty:
                return Response({'error': 'No stock data found'}, status=404)
            
            stock_data = stock[['Close']].reset_index()
            print(stock_data)
            stock['Momentum'] = stock['Close'].pct_change()
            stock['MA10'] = stock['Close'].rolling(window = 10).mean()
            stock['MA20'] = stock['Close'].rolling(window = 20).mean()
            stock['Date'] = stock.index
            stock_data_1 = stock[['Momentum']].reset_index()
            stock_data_2 = stock[['MA10']].reset_index()
            stock_data_3 = stock[['MA20']].reset_index()
            
            fig_candlestick = go.Figure(data=[go.Candlestick(
            x=stock['Date'],
            open=stock['Open'],
            high=stock['High'],
            low=stock['Low'],
            close=stock['Close'],
            name=f'{stock_symbol} Candlestick'
            )])
            fig_candlestick.update_layout(
            title=f'{stock_symbol} Candlestick Chart',  # Set the chart title
            xaxis_title='Date',  # Label for x-axis
            yaxis_title='Price',  # Label for y-axis
            plot_bgcolor='rgba(43, 43, 43, 0.85)',  # Dark background for plot
            paper_bgcolor='rgba(43, 43, 43, 0.85)',  # Dark background for outer paper
            font=dict(color='#eaeaea'),  # Font color (for dark theme)
            xaxis=dict(gridcolor='rgba(255, 255, 255, 0.2)', color='#eaeaea'),  # X-axis settings
            yaxis=dict(gridcolor='rgba(255, 255, 255, 0.2)', color='#eaeaea'),  # Y-axis settings
            )
            
            delta = stock['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods = 1).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods = 1).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            stock['RSI'] = rsi
            
            corr_matrix = stock[['Open', 'High', 'Low', 'Close', 'Volume']].corr()
            fig_corr = ff.create_annotated_heatmap(z=np.around(corr_matrix.values, decimals = 4), x=list(corr_matrix.columns), y=list(corr_matrix.index), colorscale='Viridis')
            fig_corr.update_layout(
            title=f'{stock_symbol} Feature Correlation',
            plot_bgcolor='rgba(43, 43, 43, 0.85)',
            paper_bgcolor='rgba(43, 43, 43, 0.85)',
            font=dict(color='#eaeaea'),
            )
            print(stock)
            # Get the Date and Close columns
            dates = stock.index
            print(dates)
            close_prices = stock['Close']

#   Calculate the 20-day moving average
            ma_20 = close_prices.rolling(window=20).mean()

            # Calculate the standard deviation
            std_dev_20 = close_prices.rolling(window=20).std()

            # Calculate the upper and lower bands
            upper_band = ma_20 + (std_dev_20 * 2)
            lower_band = ma_20 - (std_dev_20 * 2)

# Create Bollinger Bands chart
            fig_bollinger = go.Figure()
            fig_bollinger.add_trace(go.Scatter(x=stock_data["Date"], y=close_prices, name='Stock Price'))
            fig_bollinger.add_trace(go.Scatter(x=stock_data["Date"], y=upper_band, name='Upper Band', fill=None, mode='lines'))
            fig_bollinger.add_trace(go.Scatter(x=stock_data["Date"], y=lower_band, name='Lower Band', fill='tonexty', mode='lines'))

            # Customize layout
            fig_bollinger.update_layout(
            title=f'{stock_symbol} Bollinger Bands',
            plot_bgcolor='rgba(43, 43, 43, 0.85)',
            paper_bgcolor='rgba(43, 43, 43, 0.85)',
            font=dict(color='#eaeaea'),
            xaxis=dict(gridcolor='rgba(255, 255, 255, 0.2)', color='#eaeaea'),
            yaxis=dict(gridcolor='rgba(255, 255, 255, 0.2)', color='#eaeaea'),
            )
            
            fig_rsi = px.line(stock, x='Date', y='RSI', title=f'{stock_symbol} Relative Strength Index (14-day)')
            fig_rsi.update_layout(
            plot_bgcolor='rgba(43, 43, 43, 0.85)',
            paper_bgcolor='rgba(43, 43, 43, 0.85)',
            font=dict(color='#eaeaea'),
            xaxis=dict(gridcolor='rgba(255, 255, 255, 0.2)', color='#eaeaea'),
            yaxis=dict(gridcolor='rgba(255, 255, 255, 0.2)', color='#eaeaea'),)
            
            stock_data['12-Day EMA'] = stock_data['Close'].ewm(span=12, adjust=False).mean()
            stock_data['26-Day EMA'] = stock_data['Close'].ewm(span=26, adjust=False).mean()
            stock_data['MACD'] = stock_data['12-Day EMA'] - stock_data['26-Day EMA']
            stock_data['Signal Line'] = stock_data['MACD'].ewm(span=9, adjust=False).mean()
            fig_macd = go.Figure()
            fig_macd.add_trace(go.Scatter(x=stock_data['Date'], y=stock_data['MACD'], name='MACD'))
            fig_macd.add_trace(go.Scatter(x=stock_data['Date'], y=stock_data['Signal Line'], name='Signal Line'))
            
            fig_macd.update_layout(
            title=f'{stock_symbol} Moving Average Convergence Divergence (MACD)',
            plot_bgcolor='rgba(43, 43, 43, 0.85)',
            paper_bgcolor='rgba(43, 43, 43, 0.85)',
            font=dict(color='#eaeaea'),
            xaxis=dict(gridcolor='rgba(255, 255, 255, 0.2)', color='#eaeaea'),
            yaxis=dict(gridcolor='rgba(255, 255, 255, 0.2)', color='#eaeaea'),
            )
        
            fig_ma10 = px.line(stock_data_2, x='Date', y="MA10", title = f'{stock_symbol} Moving Average of 10 days Over Time')
            fig_ma20 = px.line(stock_data_3, x='Date', y="MA20", title = f'{stock_symbol} Moving Average of 20 days Over Time')
            fig_momentum = px.line(stock_data_1, x='Date', y='Momentum', title=f'{stock_symbol} Momentum Over Time')
            fig = px.line(stock_data, x='Date', y='Close', title=f'{stock_symbol} Stock Price Over Time')
            
            stock_data['Daily Return'] = stock_data['Close'].pct_change()
            stock_data['Cumulative Return'] = (1 + stock_data['Daily Return']).cumprod()
            fig_cumulative_return = go.Figure(data=[
            go.Scatter(x=stock_data['Date'], y=stock_data['Cumulative Return'], mode='lines', name='Cumulative Return')
            ])
            fig_cumulative_return.update_layout(
            title=f'Cumulative Returns of {stock_symbol}',
            xaxis_title='Date',
            yaxis_title='Cumulative Return',
            plot_bgcolor='rgba(43, 43, 43, 0.85)',  # Dark background
            paper_bgcolor='rgba(43, 43, 43, 0.85)',
            font=dict(color='#eaeaea'))
            
            common_layout = {
            'plot_bgcolor': 'rgba(43, 43, 43, 0.85)',  # Graph background
            'paper_bgcolor': 'rgba(43, 43, 43, 0.85)',  # Outer paper background
            'font': {'color': '#eaeaea'},  # Font color for labels and titles
            'xaxis': {'gridcolor': 'rgba(255, 255, 255, 0.2)', 'color': '#eaeaea'},
            'yaxis': {'gridcolor': 'rgba(255, 255, 255, 0.2)', 'color': '#eaeaea'},
            'hovermode': 'x',}
            
            fig.update_layout(**common_layout)
            fig_momentum.update_layout(**common_layout)
            fig_ma10.update_layout(**common_layout)
            fig_ma20.update_layout(**common_layout)
            
            graph_json_stock = pio.to_json(fig)
            graph_json_momentum = pio.to_json(fig_momentum)
            graph_json_MA10 = pio.to_json(fig_ma10)
            graph_json_MA20 = pio.to_json(fig_ma20)
            graph_json_candlestick = pio.to_json(fig_candlestick)
            graph_json_rsi = pio.to_json(fig_rsi)
            graph_json_corr = pio.to_json(fig_corr)
            graph_json_bollinger = pio.to_json(fig_bollinger)
            graph_json_macd = pio.to_json(fig_macd)
            graph_json_cumulative = pio.to_json(fig_cumulative_return)
            return Response({'company': company, 'graph_json_stock': graph_json_stock, 
                             'graph_json_momentum': graph_json_momentum,
                             'graph_json_MA10': graph_json_MA10,
                             'graph_json_MA20': graph_json_MA20,
                             'graph_json_candlestick': graph_json_candlestick,
                             'graph_json_rsi': graph_json_rsi,
                             'graph_json_corr': graph_json_corr,
                             'graph_json_bollinger': graph_json_bollinger,
                             'graph_json_macd': graph_json_macd,
                             'graph_json_cumulative': graph_json_cumulative})
        except Exception as e:
            return Response({'error': str(e)}, status=500)
            
    else:
        return Response({'error': 'Company not found'}, status=404)


