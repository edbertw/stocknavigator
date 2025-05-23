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
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

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
            '''
            stock["Date"] = stock.index
            stock["Date"] = pd.to_datetime(stock["Date"])
            stock = stock.reset_index(drop = True)
            stock = stock[["Date", "Close"]]
            closing_prices = stock['Close'].values.reshape(-1
            '''
            closing_prices = stock[["Close"]]
            scaler = MinMaxScaler(feature_range=(0, 1))
            scaled_data = scaler.fit_transform(closing_prices)
            training_data_len = int(np.ceil(len(scaled_data) * 0.8))
            train_data = scaled_data[0:int(training_data_len), :]


            # Create empty lists for features (x_train) and target (y_train)

            x_train = []

            y_train = []

            # Populate x_train with 60 days of data and y_train with the following day’s closing price

            for i in range(60, len(train_data)):
                x_train.append(train_data[i-60:i, 0])  # Past 60 days
                y_train.append(train_data[i, 0])       # Target: the next day’s close price


            # Convert lists to numpy arrays for model training

            x_train, y_train = np.array(x_train), np.array(y_train)
            # Reshape x_train to the format [samples, time steps, features] required for LSTM
            x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))
            
            model = Sequential()
            # First LSTM layer with 50 units and return sequences
            model.add(LSTM(units=50, return_sequences=True, input_shape=(x_train.shape[1], 1)))
            model.add(Dropout(0.2))  # Dropout layer to prevent overfitting
            # Second LSTM layer
            model.add(LSTM(units=50, return_sequences=False))
            model.add(Dropout(0.2))  # Dropout layer to prevent overfitting
            # Dense layer with 25 units
            model.add(Dense(units=25))
            # Output layer with 1 unit (the predicted price)
            model.add(Dense(units=1))
            # Compile the model using Adam optimizer and mean squared error as the loss function

            model.compile(optimizer='adam', loss='mean_squared_error')
            model.fit(x_train, y_train, batch_size=2, epochs=50)
            last_60_days = scaled_data[-60:]
            # Reshape last_60_days to fit the model input shape (1 sample, 60 timesteps, 1 feature)
            x_future = last_60_days.reshape((1, last_60_days.shape[0], 1))
            # Create an empty list to store predictions for the next 30 days

            future_predictions = []

            for _ in range(30):  # Change 30 to predict for 60 days

            # Predict the next day’s closing price based on the last 60 days
                pred = model.predict(x_future)
                future_predictions.append(pred[0, 0])  # Add prediction to the list
            # Update x_future with the new prediction by removing the first value and adding the new prediction
                x_future = np.append(x_future[:, 1:, :], [[pred[0]]], axis=1)

            # Convert the scaled predictions back to the original scale using inverse_transform
            future_predictions = scaler.inverse_transform(np.array(future_predictions).reshape(-1, 1))
            forecast_dates = pd.date_range(start=closing_prices.index[-1] + pd.Timedelta(days=1), periods=30, freq='B')
            forecast = pd.DataFrame(future_predictions, index=forecast_dates, columns=['Prediction'])
            fig = px.line(
                forecast, 
                x=forecast.index, 
                y='Prediction', 
                    title=f'{stock_symbol} Stock Price Predictions for 30 days'
            )
            
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
            
    
    
    
    
