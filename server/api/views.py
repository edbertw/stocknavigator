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
from django.contrib.auth.models import User
from rest_framework import generics
from .serializers import UserSerializer, NoteSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Note
from rest_framework.views import APIView


class NoteListCreate(generics.ListCreateAPIView):
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Note.objects.filter(author=user)
    
    def perform_create(self, serializer):
        if serializer.is_valid():
            serializer.save(author=self.request.user)
        else:
            print(serializer.errors)
            
class UserInfoView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        return Response({
            'username': user.username
        })
    
          
class NoteDelete(generics.DestroyAPIView):
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Note.objects.filter(author=user)
    
class createUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    


def index(request):
    return render(request, "index.html")



company_data = {
    'NVDA': {
        'name': 'NVIDIA',
        'description': 'NVIDIA is a leading manufacturer of GPUs for gaming and AI computing.'
    },
    'NDAQ': {
        'name': 'NASDAQ',
        'description': 'NASDAQ is an American stock exchange, the second-largest in the world by market cap.',
    },
    'TSLA': {
        'name': 'Tesla',
        'description': 'Tesla is a clean energy and electric vehicle company.',
    },
    'HSBC': {
        'name': 'HSBC',
        'description': 'HSBC is one of the world\'s largest banking and financial services organizations.',
    },
    'JPM': {
        'name': 'JP Morgan',
        'description': 'JP Morgan is a global leader in financial services offering solutions to corporations, institutions, and governments.',
    },
    'MS': {
        'name': 'Morgan Stanley',
        'description': 'Morgan Stanley is a global financial services firm providing investment banking, securities, wealth management, and investment management services.',
    },
    'GS': {
        'name': 'Goldman Sachs',
        'description': 'Goldman Sachs is a leading global investment banking, securities, and investment management firm.',
    },
    'JEF': {
        'name': 'Jefferies',
        'description': 'Jefferies is a global investment banking firm that provides financial services to institutional clients.',
    },
    'AAPL': {
        'name': 'Apple',
        'description': 'Apple is a multinational technology company that designs, manufactures, and markets consumer electronics, software, and services.',
    },
    'AMZN': {
        'name': 'Amazon',
        'description': 'Amazon is a multinational technology company focusing on e-commerce, cloud computing, and artificial intelligence.',
    },
    'GOOGL': {
        'name': 'Google',
        'description': 'Google is a multinational technology company specializing in Internet-related services and products, including search engines, online advertising, and cloud computing.',
    },
    'META': {
        'name': 'Meta (Formerly Facebook)',
        'description': 'Meta Platforms is a technology company that focuses on social media and virtual reality.',
    },
    'MSFT': {
        'name': 'Microsoft',
        'description': 'Microsoft is a multinational technology company that develops, licenses, and supports a wide range of software products and services.',
    },
    'NFLX': {
        'name': 'Netflix',
        'description': 'Netflix is a media-services provider and production company known for its streaming service.',
    },
    'DIS': {
        'name': 'Disney',
        'description': 'The Walt Disney Company is a diversified international family entertainment and media enterprise.',
    },
    'V': {
        'name': 'Visa',
        'description': 'Visa is a global payments technology company that connects consumers, businesses, banks, and governments.',
    },
    'C': {
        'name': 'Citigroup',
        'description': 'Citigroup is a multinational investment bank and financial services corporation.',
    },
    'BLK':{
        'name': 'BlackRock',
        'description': 'BlackRock is an American global investment management corporation.',
    },
    'IBM':{
        'name': 'IBM',
        'description': 'International Business Machines Corporation is an American multinational technology company.',
    },
    'UBER':{
        'name': 'Uber',
        'description': 'Uber Technologies, Inc. is an American technology company that offers ride-hailing, food delivery, and freight transportation services.',
    },
    'ORCL':{
        'name': 'Oracle',
        'description': 'Oracle Corporation is an American multinational computer technology corporation that offers software, cloud solutions, and hardware products.',
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
            xaxis_title='Date',  # Label for x-axis
            yaxis_title='Price',  # Label for y-axis
            plot_bgcolor='white',  # Dark background for plot
            paper_bgcolor='white',  # Dark background for outer paper
            font=dict(color='black'),  # Font color (for dark theme)
            xaxis=dict(gridcolor='rgba(0,0,0,0.1)', color='darkgreen', title_font=dict(color='darkgreen')),  # X-axis settings
            yaxis=dict(gridcolor='rgba(0,0,0,0.1)', color='darkgreen', title_font=dict(color='darkgreen')),  # Y-axis settings
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
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color='darkgreen'),
            )
            print(stock)
            # Get the Date and Close columns
            dates = stock.index
            print(dates)
            close_prices = stock['Close']

            #  Calculate the 20-day moving average
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
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color='darkgreen'),
            xaxis=dict(gridcolor='rgba(0,0,0,0.1)', color='darkgreen', title_font=dict(color='darkgreen')),
            yaxis=dict(gridcolor='rgba(0,0,0,0.1)', color='darkgreen', title_font=dict(color='darkgreen')),
            )
            
            fig_rsi = px.line(stock, x='Date', y='RSI')
            fig_rsi.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color='darkgreen'),
            xaxis=dict(gridcolor='rgba(0,0,0,0.1)', color='darkgreen', title_font=dict(color='darkgreen')),
            yaxis=dict(gridcolor='rgba(0,0,0,0.1)', color='darkgreen', title_font=dict(color='darkgreen')),)
            
            stock_data['12-Day EMA'] = stock_data['Close'].ewm(span=12, adjust=False).mean()
            stock_data['26-Day EMA'] = stock_data['Close'].ewm(span=26, adjust=False).mean()
            stock_data['MACD'] = stock_data['12-Day EMA'] - stock_data['26-Day EMA']
            stock_data['Signal Line'] = stock_data['MACD'].ewm(span=9, adjust=False).mean()
            fig_macd = go.Figure()
            fig_macd.add_trace(go.Scatter(x=stock_data['Date'], y=stock_data['MACD'], name='MACD'))
            fig_macd.add_trace(go.Scatter(x=stock_data['Date'], y=stock_data['Signal Line'], name='Signal Line'))
            
            fig_macd.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color='darkgreen'),
            xaxis=dict(gridcolor='rgba(0,0,0,0.1)', color='darkgreen', title_font=dict(color='darkgreen')),
            yaxis=dict(gridcolor='rgba(0,0,0,0.1)', color='darkgreen', title_font=dict(color='darkgreen')),
            )
        
            fig_ma10 = px.line(stock_data_2, x='Date', y="MA10")
            fig_ma20 = px.line(stock_data_3, x='Date', y="MA20")
            fig_momentum = px.line(stock_data_1, x='Date', y='Momentum')
            fig = px.line(stock_data, x='Date', y='Close')
           
            stock_data['Daily Return'] = stock_data['Close'].pct_change()
            stock_data['Cumulative Return'] = (1 + stock_data['Daily Return']).cumprod()
            fig_cumulative_return = go.Figure(data=[
            go.Scatter(x=stock_data['Date'], y=stock_data['Cumulative Return'], mode='lines', name='Cumulative Return')
            ])
            fig_cumulative_return.update_layout(
            xaxis_title='Date',
            yaxis_title='Cumulative Return',
            plot_bgcolor='white',  
            paper_bgcolor='white',
            font=dict(color='darkgreen'))
            
            common_layout = {
            'plot_bgcolor': 'white',  # Graph background
            'paper_bgcolor': 'white',  # Outer paper background
            'font': {'color': 'darkgreen'},  # Font color for labels and titles
            'xaxis': {'gridcolor': 'rgba(0,0,0,0.1)', 'color': 'darkgreen'},
            'yaxis': {'gridcolor': 'rgba(0,0,0,0.1)', 'color': 'darkgreen'},
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


