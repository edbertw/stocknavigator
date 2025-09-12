import React, { useState, useEffect } from 'react';
import Plot from 'react-plotly.js';
import { useLocation, useNavigate } from 'react-router-dom';
import '../styles/NextNextPage.css';

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

  const handleHome = () => {
    navigate(-1);
    navigate(-1);
  };


  if (loading) {
    return (
      <div className="prediction-page-loading">
        <div className="prediction-page-spinner"></div>
        <p className="prediction-page-loading-text">Loading... Might take a while</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="prediction-page-error">
        <p className="prediction-page-error-text">{error}</p>
      </div>
    );
  }

  return (
    <div className="trading-platform">
      {/* Sidebar Navigation */}
      <nav className="trading-sidebar">
        <div className="sidebar-header">
          <a href="/" className="sidebar-logo">
            <div className="sidebar-logo-icon">📈</div>
            <span>StockNavigator</span>
          </a>
        </div>
        <div className="sidebar-nav">
          <a className="nav-item" onClick={handleHome}>
            <span className="nav-icon">🏠</span>
            <span>Dashboard</span>
          </a>
          <a className="nav-item" onClick={handleBack}>
            <span className="nav-icon">📊</span>
            <span>Analytics</span>
          </a>
          <a className="nav-item active">
            <span className="nav-icon">🔮</span>
            <span>Predictions</span>
          </a>
          <a href="/login" className="nav-item" onClick={() => {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
          }}>
            <span className="nav-icon">🚪</span>
            <span>Sign Out</span>
          </a>
        </div>
      </nav>

      {/* Main Content Area */}
      <main className="trading-main">
        {/* Header */}
        <header className="trading-header">
          <div className="header-left">
            <h1 className="header-title">AI Predictions</h1>
            <p className="header-subtitle">{company?.name || 'Stock Forecasting'}</p>
          </div>
          <div className="header-right">
            <button onClick={handleBack} className="trading-btn secondary">
              ← Back to Analysis
            </button>
          </div>
        </header>

        {/* Main Content */}
        <div className="trading-content">
          {/* Prediction Header */}
          {company && (
            <section className="prediction-header-section">
              <div className="prediction-header">
                <h2 className="prediction-title">Stock Price Forecasting</h2>
                <div className="prediction-subtitle">LSTM RNN Architecture</div>
                <div className="prediction-meta">
                  <span className="meta-item">
                    <strong>Symbol:</strong> {stockSymbol}
                  </span>
                  <span className="meta-item">
                    <strong>Company:</strong> {company.name}
                  </span>
                </div>
              </div>
            </section>
          )}

          {/* Prediction Chart */}
          <section className="prediction-chart-section">
            <div className="prediction-chart-card">
              <div className="chart-header">
                <h3>30-Day Price Predictions</h3>
                <div className="prediction-badge">
                  <span className="badge-icon">🔮</span>
                  <span>AI Generated</span>
                </div>
              </div>
              <div className="prediction-chart-container">
                {graphDataPredictions && (
                  <Plot
                    data={graphDataPredictions.data}
                    layout={{
                      ...graphDataPredictions.layout,
                      autosize: true,
                      height: 500,
                      paper_bgcolor: 'rgba(0,0,0,0)',
                      plot_bgcolor: 'rgba(0,0,0,0)',
                      font: { color: '#ffffff' },
                      xaxis: { color: '#ffffff' },
                      yaxis: { color: '#ffffff' }
                    }}
                  />
                )}
              </div>
            </div>
          </section>

          {/* Model Information */}
          <section className="model-info-section">
            <h2 className="section-title">Model Information</h2>
            <div className="model-info-grid">
              <div className="model-card">
                <div className="model-icon">🧠</div>
                <h3>LSTM Architecture</h3>
                <p>Dual Layer LSTM neural network trained on historical price data to capture temporal dependencies and market patterns.</p>
              </div>
              <div className="model-card">
                <div className="model-icon">📊</div>
                <h3>Training Data</h3>
                <p>Model trained on past 60 days of historical data, including price movements, volume, and technical indicators.</p>
              </div>
              <div className="model-card">
                <div className="model-icon">⚡</div>
                <h3>Real-time Updates</h3>
                <p>Predictions are generated in real-time based on the latest market data and technical analysis patterns.</p>
              </div>
            </div>
          </section>

          {/* Disclaimer */}
          <section className="disclaimer-section">
            <div className="disclaimer-card">
              <div className="disclaimer-header">
                <span className="disclaimer-icon">⚠️</span>
                <h3>Important Disclaimer</h3>
              </div>
              <p>
                These predictions are generated by AI models and should not be considered as financial advice. 
                Stock market predictions are inherently uncertain and past performance does not guarantee future results. 
                Always conduct your own research and consult with financial advisors before making investment decisions.
              </p>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
};

export default NextNextPage;
