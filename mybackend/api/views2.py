from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
import yfinance as yf
import pandas as pd
import numpy as np
import datetime
from datetime import date, timedelta
from autots import AutoTS
import plotly.express as px 
import plotly.io as pio
import plotly.graph_objects as go
import plotly.figure_factory as ff
@csrf_exempt
@api_view(['POST'])
def predict_stock(request):
    stock_symbol = request.data.get('stock_symbol')
    if stock_symbol:
        current = date.today()
        end = current.strftime("%Y-%m-%d")
        start = (date.today() - timedelta(days = 365)).strftime("%Y-%m-%d")
        try:
            stock = yf.download(stock_symbol, start = start, end = end, progress = False,multi_level_index=False )
            if stock.empty:
                return Response({'error': 'No stock data found'}, status=404)
            stock["Date"] = stock.index
            stock["Date"] = pd.to_datetime(stock["Date"])
            stock = stock.reset_index(drop = True)
            stock = stock[["Date", "Close"]]
            model = AutoTS(forecast_length = 35,
                           model_list = ["Prophet", "ARIMA"],
                           frequency = "infer",
                           ensemble = "simple")
            model = model.fit(stock, date_col = "Date", value_col = "Close", id_col = None)
            predictions = model.predict().forecast
            predictions = pd.DataFrame(predictions)
            predictions = predictions.reset_index()
            predictions = predictions.rename(columns = {"index": "Date"})
            fig = px.line(predictions, x='Date', y='Close', title=f'{stock_symbol} Stock Price Predictions for 35 days')
            
            common_layout = {
            'plot_bgcolor': 'rgba(43, 43, 43, 0.85)', 
            'paper_bgcolor': 'rgba(43, 43, 43, 0.85)',  
            'font': {'color': '#eaeaea'},  
            'xaxis': {'gridcolor': 'rgba(255, 255, 255, 0.2)', 'color': '#eaeaea'},
            'yaxis': {'gridcolor': 'rgba(255, 255, 255, 0.2)', 'color': '#eaeaea'},
            'hovermode': 'x',}
            
            fig.update_layout(**common_layout)
            graph_json_pred = pio.to_json(fig)
            return Response({"graph_json_pred": graph_json_pred})
        except Exception as e:
            return Response({'error': str(e)}, status=500)
    else:
        return Response({'error': 'Company not found'}, status=404)
            
    
    
    
    
