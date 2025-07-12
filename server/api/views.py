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
        'description': 'NVIDIA is a leading manufacturer of GPUs for gaming, AI, and data center computing.'
    },
    'NDAQ': {
        'name': 'NASDAQ',
        'description': 'NASDAQ is the second-largest stock exchange in the world, known for its tech-heavy listings.'
    },
    'TSLA': {
        'name': 'Tesla',
        'description': 'Tesla is an electric vehicle and clean energy company led by Elon Musk.'
    },
    'HSBC': {
        'name': 'HSBC',
        'description': 'HSBC is a British multinational banking and financial services company with a strong presence in Asia.'
    },
    'JPM': {
        'name': 'JPMorgan Chase',
        'description': 'JPMorgan Chase is a global financial services firm and the largest bank in the U.S. by assets.'
    },
    'MS': {
        'name': 'Morgan Stanley',
        'description': 'Morgan Stanley is a leading investment bank specializing in wealth management and institutional securities.'
    },
    'GS': {
        'name': 'Goldman Sachs',
        'description': 'Goldman Sachs is a top-tier investment bank serving corporations and high-net-worth clients.'
    },
    'JEF': {
        'name': 'Jefferies',
        'description': 'Jefferies is a global investment banking firm focused on equities, fixed income, and advisory services.'
    },
    'AAPL': {
        'name': 'Apple',
        'description': 'Apple is a tech giant known for iPhones, Macs, and services like Apple Music and iCloud.'
    },
    'GOOGL': {
        'name': 'Google (Alphabet)',
        'description': 'Google dominates online search, advertising, cloud computing, and AI through products like YouTube and Android.'
    },
    'AMZN': {
        'name': 'Amazon',
        'description': 'Amazon is the world’s largest e-commerce company and a leader in cloud computing (AWS).'
    },
    'META': {
        'name': 'Meta',
        'description': 'Meta owns Facebook, Instagram, and WhatsApp, and invests heavily in VR/AR technologies.'
    },
    'MSFT': {
        'name': 'Microsoft',
        'description': 'Microsoft is a software leader (Windows, Office, Azure) and a major player in cloud computing and AI.'
    },
    'NFLX': {
        'name': 'Netflix',
        'description': 'Netflix is the leading global streaming service, producing original films and TV shows.'
    },
    'DIS': {
        'name': 'Disney',
        'description': 'Disney is a media powerhouse, owning Marvel, Star Wars, ESPN, and theme parks.'
    },
    'C': {
        'name': 'Citigroup',
        'description': 'Citigroup is a global bank offering consumer banking, investment services, and corporate finance.'
    },
    'V': {
        'name': 'Visa',
        'description': 'Visa is the world’s largest payment processor, enabling digital transactions worldwide.'
    },
    'BLK': {
        'name': 'BlackRock',
        'description': 'BlackRock is the world’s largest asset manager, known for its iShares ETFs.'
    },
    'IBM': {
        'name': 'IBM',
        'description': 'IBM focuses on hybrid cloud, AI (Watson), and enterprise solutions.'
    },
    'UBER': {
        'name': 'Uber',
        'description': 'Uber is a ride-hailing and food delivery (Uber Eats) platform operating globally.'
    },
    'ORCL': {
        'name': 'Oracle',
        'description': 'Oracle provides enterprise software, cloud solutions, and database management systems.'
    },
    'WMT': {
        'name': 'Walmart',
        'description': 'Walmart is the world’s largest retailer, operating hypermarkets and e-commerce platforms.'
    },
    'MA': {
        'name': 'Mastercard',
        'description': 'Mastercard is a global payments technology company, second only to Visa in transaction volume.'
    },
    'XOM': {
        'name': 'ExxonMobil',
        'description': 'ExxonMobil is one of the largest publicly traded oil and gas companies.'
    },
    'COST': {
        'name': 'Costco',
        'description': 'Costco operates membership-based warehouse clubs offering bulk retail goods.'
    },
    'BAC': {
        'name': 'Bank of America',
        'description': 'Bank of America is a major U.S. bank providing consumer banking, investing, and corporate services.'
    },
    'PLTR': {
        'name': 'Palantir',
        'description': 'Palantir provides big data analytics and AI software for governments and enterprises.'
    },
    'KO': {
        'name': 'Coca-Cola',
        'description': 'Coca-Cola is the world’s largest beverage company, famous for its soft drinks.'
    },
    'PEP': {
        'name': 'PepsiCo',
        'description': 'PepsiCo is a global food and beverage leader (Pepsi, Lay’s, Gatorade).'
    },
    'UNH': {
        'name': 'UnitedHealth Group',
        'description': 'UnitedHealth Group is the largest U.S. health insurer and a provider of healthcare services.'
    },
    'CRM': {
        'name': 'Salesforce',
        'description': 'Salesforce is the leading CRM (customer relationship management) software provider.'
    },
    'MCD': {
        'name': 'McDonald’s',
        'description': 'McDonald’s is the world’s largest fast-food chain, known for its burgers and fries.'
    },
    'ACN': {
        'name': 'Accenture',
        'description': 'Accenture is a global IT services and consulting firm specializing in digital transformation.'
    },
    'BA': {
        'name': 'Boeing',
        'description': 'Boeing is a major aerospace company manufacturing commercial jets and defense systems.'
    },
    'ABNB': {
        'name': 'Airbnb',
        'description': 'Airbnb operates an online marketplace for short-term lodging and travel experiences.'
    },
    'AON': {
        'name': 'Aon',
        'description': 'Aon is a professional services firm offering risk management and insurance solutions.'
    },
    'DASH': {
        'name': 'DoorDash',
        'description': 'DoorDash is a leading food delivery platform in the U.S. and other markets.'
    },
    'INTC': {
        'name': 'Intel',
        'description': 'Intel is a semiconductor leader, producing CPUs for PCs, servers, and data centers.'
    },
    'ZM': {
        'name': 'Zoom',
        'description': 'Zoom provides video conferencing software widely used for remote work and education.'
    },
    'SBUX': {
        'name': 'Starbucks',
        'description': 'Starbucks is the world’s largest coffeehouse chain, offering beverages and food.'
    },
    'NKE': {
        'name': 'Nike',
        'description': 'Nike is a global leader in athletic footwear, apparel, and sports equipment.'
    },
    'CB': {
        'name': 'Chubb',
        'description': 'Chubb is a multinational insurer specializing in property, casualty, and reinsurance.'
    },
    'CRWD': {
        'name': 'CrowdStrike',
        'description': 'CrowdStrike is a cybersecurity firm offering cloud-based endpoint protection.'
    },
    'BX': {
        'name': 'Blackstone',
        'description': 'Blackstone is a leading private equity and alternative investment firm.'
    },
    'MFC': {
        'name': 'Manulife',
        'description': 'Manulife is a Canadian insurance and financial services company with global operations.'
    },
    '1299.HK': {
        'name': 'AIA Group',
        'description': 'AIA Group is a pan-Asian life insurance giant headquartered in Hong Kong.'
    },
    '0388.HK': {
        'name': 'HKEX',
        'description': 'Hong Kong Exchanges & Clearing operates the Hong Kong Stock Exchange.'
    },
    '0700.HK': {
        'name': 'Tencent',
        'description': 'Tencent is a Chinese tech conglomerate known for WeChat, gaming, and fintech.'
    },
    '2318.HK': {
        'name': 'Ping An Insurance',
        'description': 'Ping An Insurance is a Chinese financial services group focusing on insurance and banking.'
    },
    '0939.HK': {
        'name': 'China Construction Bank',
        'description': 'China Construction Bank is one of China’s "Big Four" state-owned banks.'
    },
    '0005.HK': {
        'name': 'HSBC Holdings',
        'description': 'HSBC Holdings is the Hong Kong-listed entity of the global HSBC banking group.'
    },
    '0001.HK': {
        'name': 'CK Hutchison Holdings',
        'description': 'CK Hutchison is a Hong Kong conglomerate with global ports, retail, and telecom interests.'
    },
    '0002.HK': {
        'name': 'CLP Holdings',
        'description': 'CLP Holdings is a Hong Kong-based electric utility company operating in Asia.'
    },
    '0011.HK': {
        'name': 'MTR Corporation',
        'description': 'MTR Corporation operates Hong Kong’s metro system and has international rail investments.'
    },
        '3988.HK': {
        'name': 'Bank of China (HK)',
        'description': 'Bank of China (Hong Kong) is a leading commercial bank in Hong Kong and a subsidiary of China\'s state-owned Bank of China.'
    },
    '0003.HK': {
        'name': 'Hang Seng Bank',
        'description': 'Hang Seng Bank is a major Hong Kong-based commercial bank and a subsidiary of HSBC, specializing in retail and corporate banking.'
    },
    '9888.HK': {
        'name': 'Baidu',
        'description': 'Baidu is China\'s leading search engine and AI company, often called "China\'s Google".'
    },
    '9988.HK': {
        'name': 'Alibaba Group',
        'description': 'Alibaba Group is China\'s largest e-commerce company, operating platforms like Taobao and AliExpress, with major cloud computing operations.'
    },
    '9618.HK': {
        'name': 'Meituan',
        'description': 'Meituan is a Chinese tech giant dominating food delivery, hotel bookings, and local services.'
    },
    '8147.HK': {
        'name': 'Millennium Pacific Group Holdings Ltd.',
        'description': 'Millennium HK is a financial services firm providing investment and wealth management solutions.'
    },
    '1828.HK': {
        'name': 'FWD Group',
        'description': 'FWD Group is a pan-Asian life insurer headquartered in Hong Kong, serving over 10 million customers across Asia.'
    },
    '2628.HK': {
        'name': 'China Life Insurance',
        'description': 'China Life Insurance is China\'s largest state-owned life insurer with dominant domestic market share and growing international presence.'
    },
    '0966.HK': {
        'name': 'China Taiping Insurance',
        'description': 'China Taiping Insurance is a Chinese state-owned insurer with operations in life/property insurance and asset management.'
    },
    '1508.HK': {
        'name': 'China Reinsurance Group',
        'description': 'China Reinsurance Group is China\'s only national reinsurer, providing risk coverage for insurance companies across Asia.'
    },
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


