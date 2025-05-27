import React, { useState, useEffect } from 'react';
import Plot from 'react-plotly.js';
import { useLocation, useNavigate } from 'react-router-dom';

const NextNextPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { stockSymbol, company } = location.state || {};

  const [graphDataPredictions, setGraphDataPredictions] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!stockSymbol) {
      setError('No stock symbol provided.');
      setLoading(false);
      return;
    }

    // Fetch prediction data from Django backend
    fetch('http://localhost:8000/api/predict-stock/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ stock_symbol: stockSymbol }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.graph_json_pred) {
          setGraphDataPredictions(JSON.parse(data.graph_json_pred));
        } else {
          setError(data.error || 'Error fetching predictions.');
        }
        setLoading(false);
      })
      .catch((error) => {
        console.error('Error fetching data:', error);
        setError('Error fetching predictions.');
        setLoading(false);
      });
  }, [stockSymbol]);

  const handleBack = () => {
    navigate(-1);
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p className="loading-text">Loading... Might take a while</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-container">
        <p className="error-text">{error}</p>
      </div>
    );
  }

  return (
    <div className="next-next-page">
      <div className="content-wrapper">
        {company && (
          <div>
            <h1>Stock Price Forecasting for {company.name}</h1>
            <h2>LSTM RNN architecture</h2>
            <p>Stock Symbol: {stockSymbol}</p>
            <p>Company: {company.name}</p>
          </div>
        )}

        <div className="dashboard-grid">
          {graphDataPredictions && (
            <div className="graph-card">
              <h3>30-Day Stock Price Predictions</h3>
              <Plot
                data={graphDataPredictions.data}
                layout={{
                  ...graphDataPredictions.layout,
                  autosize: true,
                  height: 500,
                  width: 800,
                }}
                config={graphDataPredictions.config}
              />
            </div>
          )}
        </div>

        <div className="info-section">
          <h2>Forecasting Insights</h2>
          <p>
            These predictions are generated using Dual Layer LSTM architecture, trained on past 60 days of data
          </p>

          <div className="info-item">
            <h2>Model Insights</h2>
            <p> The model uses a Dual Layer LSTM architecture to predict stock prices based on historical data. It captures temporal dependencies and trends in the stock market, providing insights into future price movements.
            </p>
          </div>

          <h3></h3>
        </div>

        <button onClick={handleBack} className="back-button">BACK</button>
      </div>
    </div>
  );
};

export default NextNextPage;
