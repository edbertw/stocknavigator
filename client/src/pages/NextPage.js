import React, { useEffect, useState } from 'react';
import Plot from 'react-plotly.js';
import { useLocation, useNavigate } from 'react-router-dom';
import '../styles/NextPage.css';
import ChatSessionManager from '../components/ChatSessionManager';
import ChatInterface from '../components/ChatInterface';
import { useUser } from '../contexts/UserContext';
import Footer from '../components/Footer';

const NextPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { stockSymbol, company } = location.state || {};
  const { user, currentSessionId, selectSession, endCurrentSession } = useUser();

  const [graphDataStock, setGraphDataStock] = useState(null);
  const [graphDataMomentum, setGraphDataMomentum] = useState(null);
  const [graphDataMA10, setGraphDataMA10] = useState(null);
  const [graphDataMA20, setGraphDataMA20] = useState(null);
  const [graphDataCandlestick, setGraphDataCandlestick] = useState(null);
  const [graphDataRSI, setGraphDataRSI] = useState(null);
  const [graphDataCorr, setGraphDataCorr] = useState(null);
  const [graphDataBollinger, setGraphDataBollinger] = useState(null);
  const [graphDataMACD, setGraphDataMACD] = useState(null);
  const [graphDataCum, setGraphDataCum] = useState(null);
  const [sentimentAnalysis, setSentimentAnalysis] = useState(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showChatPanel, setShowChatPanel] = useState(false);

  useEffect(() => {
    if (!stockSymbol) {
      setError('No stock symbol provided.');
      setLoading(false);
      return;
    }

    fetch('http://localhost:8000/api/submit-stock/', {
      method: 'POST',
      headers: {
        "Authorization": `Bearer ${localStorage.getItem("access_token")}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ stock_symbol: stockSymbol }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.company) {
          setGraphDataStock(JSON.parse(data.graph_json_stock));
          setGraphDataMomentum(JSON.parse(data.graph_json_momentum));
          setGraphDataMA10(JSON.parse(data.graph_json_MA10));
          setGraphDataMA20(JSON.parse(data.graph_json_MA20));
          setGraphDataCandlestick(JSON.parse(data.graph_json_candlestick));
          setGraphDataRSI(JSON.parse(data.graph_json_rsi));
          setGraphDataCorr(JSON.parse(data.graph_json_corr));
          setGraphDataBollinger(JSON.parse(data.graph_json_bollinger));
          setGraphDataMACD(JSON.parse(data.graph_json_macd));
          setGraphDataCum(JSON.parse(data.graph_json_cumulative));
        } else {
          setError(data.error || 'Error fetching data');
        }
        setLoading(false);
      })
      .catch((error) => {
        console.error('Error fetching data:', error);
        setError('Error fetching data');
        setLoading(false);
      });

    fetch('http://localhost:8000/api/sen-display/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ stock_symbol: stockSymbol }),
    })
      .then((response) => response.json())
      .then((data) => {
        setSentimentAnalysis(data.response);
      })
      .catch((error) => {
        console.error('Error fetching sentiment analysis:', error);
        setSentimentAnalysis('Unable to fetch sentiment analysis');
      });
  }, [stockSymbol]);
  
  const handleBack = () => {
    navigate(-1);
  };


  const handleNext = () => {
    navigate('/next-next-page', { state: { stockSymbol, company } });
  };

  const handleSessionSelect = (sessionId) => {
    selectSession(sessionId);
    setShowChatPanel(true);
  };

  const handleSessionEnd = (sessionId) => {
    endCurrentSession();
    setShowChatPanel(false);
  };

  const toggleChatPanel = () => {
    setShowChatPanel(!showChatPanel);
  };

  if (loading) return <div className="next-page-loading">Loading...</div>;
  if (error) return <div className="next-page-error">{error}</div>;

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
          <a className="nav-item" onClick={handleBack}>
            <span className="nav-icon">🏠</span>
            <span>Dashboard</span>
          </a>
          <a className="nav-item active">
            <span className="nav-icon">📊</span>
            <span>Analytics</span>
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
            <h1 className="header-title">Technical Analysis</h1>
            <p className="header-subtitle">{company?.name || 'Stock Analysis'}</p>
          </div>
          <div className="header-right">
            <button onClick={handleBack} className="trading-btn secondary">
              ← Back
            </button>
            <button onClick={handleNext} className="trading-btn primary">
              Predict →
            </button>
          </div>
        </header>

        {/* Main Content */}
        <div className="trading-content">
          {/* Company Info */}
          {company && (
            <section className="company-info-section">
              <div className="company-header">
                <h2 className="company-name">{company.name}</h2>
                <div className="company-symbol">{stockSymbol}</div>
              </div>
              <p className="company-description">{company.description}</p>
            </section>
          )}

          {/* Charts Grid */}
          <section className="charts-section">
            <h2 className="section-title">Technical Indicators</h2>
            <div className="charts-grid">
              {graphDataStock && (
                <div className="chart-card">
                  <div className="chart-header">
                    <h3>Stock Prices</h3>
                    <span className="chart-type">Price Chart</span>
                  </div>
                  <div className="chart-container">
                    <Plot 
                      data={graphDataStock.data} 
                      layout={{ 
                        ...graphDataStock.layout, 
                        autosize: true, 
                        height: 300,
                        paper_bgcolor: 'rgba(0,0,0,0)',
                        plot_bgcolor: 'rgba(0,0,0,0)',
                        font: { color: '#ffffff' },
                        xaxis: { color: '#ffffff' },
                        yaxis: { color: '#ffffff' },
                        margin: { l: 40, r: 40, t: 40, b: 40 }
                      }}
                      config={{ responsive: true, displayModeBar: false }}
                      style={{ width: '100%', height: '100%' }}
                    />
                  </div>
                </div>
              )}
              
              {graphDataCandlestick && (
                <div className="chart-card">
                  <div className="chart-header">
                    <h3>Candlestick Chart</h3>
                    <span className="chart-type">OHLC</span>
                  </div>
                  <div className="chart-container">
                    <Plot 
                      data={graphDataCandlestick.data} 
                      layout={{ 
                        ...graphDataCandlestick.layout, 
                        autosize: true, 
                        height: 300,
                        paper_bgcolor: 'rgba(0,0,0,0)',
                        plot_bgcolor: 'rgba(0,0,0,0)',
                        font: { color: '#ffffff' },
                        xaxis: { color: '#ffffff' },
                        yaxis: { color: '#ffffff' },
                        margin: { l: 40, r: 40, t: 40, b: 40 }
                      }}
                      config={{ responsive: true, displayModeBar: false }}
                      style={{ width: '100%', height: '100%' }}
                    />
                  </div>
                </div>
              )}

              {graphDataRSI && (
                <div className="chart-card">
                  <div className="chart-header">
                    <h3>RSI Indicator</h3>
                    <span className="chart-type">Momentum</span>
                  </div>
                  <div className="chart-container">
                    <Plot 
                      data={graphDataRSI.data} 
                      layout={{ 
                        ...graphDataRSI.layout, 
                        autosize: true, 
                        height: 300,
                        paper_bgcolor: 'rgba(0,0,0,0)',
                        plot_bgcolor: 'rgba(0,0,0,0)',
                        font: { color: '#ffffff' },
                        xaxis: { color: '#ffffff' },
                        yaxis: { color: '#ffffff' },
                        margin: { l: 40, r: 40, t: 40, b: 40 }
                      }}
                      config={{ responsive: true, displayModeBar: false }}
                      style={{ width: '100%', height: '100%' }}
                    />
                  </div>
                </div>
              )}

              {graphDataMACD && (
                <div className="chart-card">
                  <div className="chart-header">
                    <h3>MACD</h3>
                    <span className="chart-type">Trend</span>
                  </div>
                  <div className="chart-container">
                    <Plot 
                      data={graphDataMACD.data} 
                      layout={{ 
                        ...graphDataMACD.layout, 
                        autosize: true, 
                        height: 300,
                        paper_bgcolor: 'rgba(0,0,0,0)',
                        plot_bgcolor: 'rgba(0,0,0,0)',
                        font: { color: '#ffffff' },
                        xaxis: { color: '#ffffff' },
                        yaxis: { color: '#ffffff' },
                        margin: { l: 40, r: 40, t: 40, b: 40 }
                      }}
                      config={{ responsive: true, displayModeBar: false }}
                      style={{ width: '100%', height: '100%' }}
                    />
                  </div>
                </div>
              )}

              {graphDataBollinger && (
                <div className="chart-card">
                  <div className="chart-header">
                    <h3>Bollinger Bands</h3>
                    <span className="chart-type">Volatility</span>
                  </div>
                  <div className="chart-container">
                    <Plot 
                      data={graphDataBollinger.data} 
                      layout={{ 
                        ...graphDataBollinger.layout, 
                        autosize: true, 
                        height: 300,
                        paper_bgcolor: 'rgba(0,0,0,0)',
                        plot_bgcolor: 'rgba(0,0,0,0)',
                        font: { color: '#ffffff' },
                        xaxis: { color: '#ffffff' },
                        yaxis: { color: '#ffffff' },
                        margin: { l: 40, r: 40, t: 40, b: 40 }
                      }}
                      config={{ responsive: true, displayModeBar: false }}
                      style={{ width: '100%', height: '100%' }}
                    />
                  </div>
                </div>
              )}

              {graphDataMomentum && (
                <div className="chart-card">
                  <div className="chart-header">
                    <h3>Momentum</h3>
                    <span className="chart-type">Momentum</span>
                  </div>
                  <div className="chart-container">
                    <Plot 
                      data={graphDataMomentum.data} 
                      layout={{ 
                        ...graphDataMomentum.layout, 
                        autosize: true, 
                        height: 300,
                        paper_bgcolor: 'rgba(0,0,0,0)',
                        plot_bgcolor: 'rgba(0,0,0,0)',
                        font: { color: '#ffffff' },
                        xaxis: { color: '#ffffff' },
                        yaxis: { color: '#ffffff' },
                        margin: { l: 40, r: 40, t: 40, b: 40 }
                      }}
                      config={{ responsive: true, displayModeBar: false }}
                      style={{ width: '100%', height: '100%' }}
                    />
                  </div>
                </div>
              )}

              {graphDataMA10 && (
                <div className="chart-card">
                  <div className="chart-header">
                    <h3>Moving Average (10-day)</h3>
                    <span className="chart-type">Trend</span>
                  </div>
                  <div className="chart-container">
                    <Plot 
                      data={graphDataMA10.data} 
                      layout={{ 
                        ...graphDataMA10.layout, 
                        autosize: true, 
                        height: 300,
                        paper_bgcolor: 'rgba(0,0,0,0)',
                        plot_bgcolor: 'rgba(0,0,0,0)',
                        font: { color: '#ffffff' },
                        xaxis: { color: '#ffffff' },
                        yaxis: { color: '#ffffff' },
                        margin: { l: 40, r: 40, t: 40, b: 40 }
                      }}
                      config={{ responsive: true, displayModeBar: false }}
                      style={{ width: '100%', height: '100%' }}
                    />
                  </div>
                </div>
              )}

              {graphDataMA20 && (
                <div className="chart-card">
                  <div className="chart-header">
                    <h3>Moving Average (20-day)</h3>
                    <span className="chart-type">Trend</span>
                  </div>
                  <div className="chart-container">
                    <Plot 
                      data={graphDataMA20.data} 
                      layout={{ 
                        ...graphDataMA20.layout, 
                        autosize: true, 
                        height: 300,
                        paper_bgcolor: 'rgba(0,0,0,0)',
                        plot_bgcolor: 'rgba(0,0,0,0)',
                        font: { color: '#ffffff' },
                        xaxis: { color: '#ffffff' },
                        yaxis: { color: '#ffffff' },
                        margin: { l: 40, r: 40, t: 40, b: 40 }
                      }}
                      config={{ responsive: true, displayModeBar: false }}
                      style={{ width: '100%', height: '100%' }}
                    />
                  </div>
                </div>
              )}

              {graphDataCorr && (
                <div className="chart-card">
                  <div className="chart-header">
                    <h3>Feature Correlations</h3>
                    <span className="chart-type">Correlation</span>
                  </div>
                  <div className="chart-container">
                    <Plot 
                      data={graphDataCorr.data} 
                      layout={{ 
                        ...graphDataCorr.layout, 
                        autosize: true, 
                        height: 300,
                        paper_bgcolor: 'rgba(0,0,0,0)',
                        plot_bgcolor: 'rgba(0,0,0,0)',
                        font: { color: '#ffffff' },
                        xaxis: { color: '#ffffff' },
                        yaxis: { color: '#ffffff' },
                        margin: { l: 40, r: 40, t: 40, b: 40 }
                      }}
                      config={{ responsive: true, displayModeBar: false }}
                      style={{ width: '100%', height: '100%' }}
                    />
                  </div>
                </div>
              )}

              {graphDataCum && (
                <div className="chart-card">
                  <div className="chart-header">
                    <h3>Cumulative Returns</h3>
                    <span className="chart-type">Performance</span>
                  </div>
                  <div className="chart-container">
                    <Plot 
                      data={graphDataCum.data} 
                      layout={{ 
                        ...graphDataCum.layout, 
                        autosize: true, 
                        height: 300,
                        paper_bgcolor: 'rgba(0,0,0,0)',
                        plot_bgcolor: 'rgba(0,0,0,0)',
                        font: { color: '#ffffff' },
                        xaxis: { color: '#ffffff' },
                        yaxis: { color: '#ffffff' },
                        margin: { l: 40, r: 40, t: 40, b: 40 }
                      }}
                      config={{ responsive: true, displayModeBar: false }}
                      style={{ width: '100%', height: '100%' }}
                    />
                  </div>
                </div>
              )}
            </div>
          </section>

          {/* Sentiment Analysis */}
          <section className="sentiment-section">
            <h2 className="section-title">Market Sentiment</h2>
            <div className="sentiment-card">
              <div className="sentiment-header">
                <h3>AI Sentiment Analysis</h3>
                <div className="sentiment-indicator">
                  <span className="indicator-dot"></span>
                  <span>Live Analysis</span>
                </div>
              </div>
              <div className="sentiment-content">
                {sentimentAnalysis || "Loading sentiment analysis..."}
              </div>
            </div>
          </section>

          {/* AI Chat Section */}
          <section className="chat-section">
            <div className="chat-toggle-container">
              <button 
                className="chat-toggle-btn"
                onClick={toggleChatPanel}
              >
                {showChatPanel ? 'Hide' : 'Show'} AI Financial Advisor
              </button>
            </div>
            
            {showChatPanel && (
              <div className="chat-panel">
                <div className="chat-session-sidebar">
                  <ChatSessionManager
                    userId={user?.id}
                    onSessionSelect={handleSessionSelect}
                    currentSessionId={currentSessionId}
                    onSessionEnd={handleSessionEnd}
                  />
                </div>
                <div className="chat-interface-main">
                  <ChatInterface
                    sessionId={currentSessionId}
                    userId={user?.id}
                    onSessionEnd={handleSessionEnd}
                  />
                </div>
              </div>
            )}
          </section>
          <Footer />
        </div>
      </main>
    </div>
  );
};

export default NextPage;