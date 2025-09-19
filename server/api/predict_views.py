from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
import yfinance as yf
import pandas as pd
import numpy as np
import datetime
from datetime import date, timedelta
import plotly.express as px 
import plotly.io as pio
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import os
import json
import redis

class StockPredictor:
    def __init__(self):
        self.common_layout = {
            'plot_bgcolor': 'white',
            'paper_bgcolor': 'white',
            'font': {'color': 'darkgreen'},
            'xaxis': {'gridcolor': 'rgba(0,0,0,0.1)', 'color': 'darkgreen'},
            'yaxis': {'gridcolor': 'rgba(0,0,0,0.1)', 'color': 'darkgreen'},
            'hovermode': 'x'
        }
    
    def get_stock_data(self, stock_symbol, days_back=1983):
        """Download historical stock data"""
        current = date.today()
        end = current.strftime("%Y-%m-%d")
        start = (current - timedelta(days=days_back)).strftime("%Y-%m-%d")
        
        stock = yf.download(
            stock_symbol, 
            start=start, 
            end=end, 
            progress=False,
            multi_level_index=False
        )
        
        if stock.empty:
            raise ValueError("No stock data found")
            
        return stock[["Close"]]
    
    def prepare_data(self, data, train_ratio=0.8, lookback=60):
        """Prepare data for LSTM model"""
        # Scale data
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(data)
        
        # Split into training and test sets
        training_data_len = int(np.ceil(len(scaled_data) * train_ratio))
        train_data = scaled_data[0:training_data_len, :]
        
        # Create training sequences
        x_train, y_train = [], []
        for i in range(lookback, len(train_data)):
            x_train.append(train_data[i-lookback:i, 0])
            y_train.append(train_data[i, 0])
            
        # Convert to numpy arrays and reshape
        x_train = np.array(x_train)
        y_train = np.array(y_train)
        x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))
        
        return scaler, x_train, y_train, scaled_data
    
    def build_model(self, input_shape):
        """Build LSTM model"""
        model = Sequential([
            LSTM(units=50, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            LSTM(units=50, return_sequences=False),
            Dropout(0.2),
            Dense(units=25),
            Dense(units=1)
        ])
        
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model
    
    def make_predictions(self, model, scaler, last_data, days_to_predict=30):
        """Make future predictions"""
        future_predictions = []
        x_future = last_data.reshape((1, last_data.shape[0], 1))
        
        for _ in range(days_to_predict):
            pred = model.predict(x_future)
            future_predictions.append(pred[0, 0])
            x_future = np.append(x_future[:, 1:, :], [[pred[0]]], axis=1)
        
        # Inverse transform predictions
        future_predictions = scaler.inverse_transform(
            np.array(future_predictions).reshape(-1, 1)
        )
        
        return future_predictions
    
    def create_forecast_df(self, predictions, last_date):
        """Create DataFrame with forecast dates"""
        forecast_dates = pd.date_range(
            start=last_date + pd.Timedelta(days=1),
            periods=len(predictions),
            freq='B'
        )
        return pd.DataFrame(predictions, index=forecast_dates, columns=['Prediction'])
    
    def generate_plot(self, forecast_df, stock_symbol):
        """Generate Plotly figure"""
        fig = px.line(
            forecast_df, 
            x=forecast_df.index, 
            y='Prediction', 
            title=f'{stock_symbol} Stock Price Predictions for Next 30 Days'
        )
        fig.update_layout(**self.common_layout)
        return pio.to_json(fig)
    
    def predict(self, stock_symbol):
        """Main prediction pipeline"""
        # Get data
        closing_prices = self.get_stock_data(stock_symbol)
        
        # Prepare data
        scaler, x_train, y_train, scaled_data = self.prepare_data(closing_prices)

        # Build and train model
        model = self.build_model((x_train.shape[1], 1))
        model.fit(x_train, y_train, batch_size=2, epochs=20)
        
        # Make predictions
        last_60_days = scaled_data[-60:]
        predictions = self.make_predictions(model, scaler, last_60_days)
        
        # Create forecast DataFrame
        forecast_df = self.create_forecast_df(predictions, closing_prices.index[-1])
        
        # Generate plot
        return self.generate_plot(forecast_df, stock_symbol)

# Initialize the stock predictor
stock_predictor = StockPredictor()

# Initialize Redis client (lazy; created on module import)
_redis_client = None

def get_redis_client():
    global _redis_client
    # Redis client will store key-vale pairs of stock_symbol -> graph_json_pred
    if _redis_client is None:
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = int(os.getenv('REDIS_PORT', '6379'))
        redis_db = int(os.getenv('REDIS_DB', '0'))
        _redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db, socket_timeout=2)
    return _redis_client

@csrf_exempt
@api_view(['POST'])
def predict_stock(request):
    try:
        stock_symbol = request.data.get('stock_symbol')
        if not stock_symbol:
            return Response({'error': 'Stock symbol not provided'}, status=400)
        
        symbol_key = f"prediction:{stock_symbol.upper()}"
        redis_ttl_seconds = int(os.getenv('REDIS_TTL_SECONDS', '86400'))

        # Try cache first
        try:
            client = get_redis_client()
            cached = client.get(symbol_key)
            if cached is not None:
                # Value stored is raw JSON string of plotly fig
                graph_json_pred = cached.decode('utf-8')
                return Response({"graph_json_pred": graph_json_pred})
        except Exception:
            # Cache is best-effort; continue on failure
            pass

        # Compute fresh
        graph_json_pred = stock_predictor.predict(stock_symbol)

        # Store in cache
        try:
            client = get_redis_client()
            client.setex(symbol_key, redis_ttl_seconds, graph_json_pred)
        except Exception:
            pass

        return Response({"graph_json_pred": graph_json_pred})
    
    except ValueError as e:
        return Response({'error': str(e)}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)
            
    
    
    
    
