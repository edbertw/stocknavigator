import React, { useEffect, useState } from 'react';
import Plot from 'react-plotly.js';
import { useLocation, useNavigate } from 'react-router-dom';
import '../styles/NextPage.css';

const NextPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { stockSymbol, company } = location.state || {};

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

  // Chatbox state
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');

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

  const handleChatSubmit = async (e) => {
    e.preventDefault();
    if (inputText.trim()) {
      setMessages((prevMessages) => [
        ...prevMessages,
        { text: inputText, sender: 'user' },
      ]);
  
      try {
        const response = await fetch('http://localhost:8000/api/ask-chatbot/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ question: inputText }),
        });
        
        if (!response.ok) throw new Error('Failed to fetch bot response');

        const data = await response.json();
        setMessages((prevMessages) => [
          ...prevMessages,
          { text: data.response, sender: 'bot' },
        ]);
      } catch (error) {
        console.error('Error fetching bot response:', error);
        setMessages((prevMessages) => [
          ...prevMessages,
          { text: 'Error: Could not fetch bot response.', sender: 'bot' },
        ]);
      }
      setInputText('');
    }
  };

  if (loading) return <div className="next-page-loading">Loading...</div>;
  if (error) return <div className="next-page-error">{error}</div>;

  return (
    <div className="next-page-container">
      <div className="next-page-content">
        {company && (
          <div className="next-page-company-info">
            <h1>{company.name}</h1>
            <p>{company.description}</p>
          </div>
        )}

        <div className="next-page-grid">
          {graphDataStock && (
            <div className="next-page-graph-card">
              <h3>Stock Prices</h3>
              <Plot data={graphDataStock.data} layout={{ ...graphDataStock.layout, autosize: true, height: 300, width: 400 }} />
            </div>
          )}
          {graphDataMomentum && (
            <div className="next-page-graph-card">
              <h3>Momentum</h3>
              <Plot data={graphDataMomentum.data} layout={{ ...graphDataMomentum.layout, autosize: true, height: 300, width: 400 }} />
            </div>
          )}
          {graphDataMA10 && (
            <div className="next-page-graph-card">
              <h3>Moving Average (10-day)</h3>
              <Plot data={graphDataMA10.data} layout={{ ...graphDataMA10.layout, autosize: true, height: 300, width: 400 }} />
            </div>
          )}
          {graphDataMA20 && (
            <div className="next-page-graph-card">
              <h3>Moving Average (20-day)</h3>
              <Plot data={graphDataMA20.data} layout={{ ...graphDataMA20.layout, autosize: true, height: 300, width: 400 }} />
            </div>
          )}
          {graphDataCandlestick && (
            <div className="next-page-graph-card">
              <h3>Candlestick</h3>
              <Plot data={graphDataCandlestick.data} layout={{ ...graphDataCandlestick.layout, autosize: true, height: 300, width: 400 }} />
            </div>
          )}
          {graphDataRSI && (
            <div className="next-page-graph-card">
              <h3>Relative Strength Index (RSI)</h3>
              <Plot data={graphDataRSI.data} layout={{ ...graphDataRSI.layout, autosize: true, height: 300, width: 400 }} />
            </div>
          )}
          {graphDataCorr && (
            <div className="next-page-graph-card">
              <h3>Feature Correlations</h3>
              <Plot data={graphDataCorr.data} layout={{ ...graphDataCorr.layout, autosize: true, height: 300, width: 400 }} />
            </div>
          )}
          {graphDataBollinger && (
            <div className="next-page-graph-card">
              <h3>Bollinger Bands</h3>
              <Plot data={graphDataBollinger.data} layout={{ ...graphDataBollinger.layout, autosize: true, height: 300, width: 400 }} />
            </div>
          )}
          {graphDataMACD && (
            <div className="next-page-graph-card">
              <h3>MACD</h3>
              <Plot data={graphDataMACD.data} layout={{ ...graphDataMACD.layout, autosize: true, height: 300, width: 400 }} />
            </div>
          )}
          {graphDataCum && (
            <div className="next-page-graph-card">
              <h3>Cumulative Returns</h3>
              <Plot data={graphDataCum.data} layout={{ ...graphDataCum.layout, autosize: true, height: 300, width: 400 }} />
            </div>
          )}
        </div>

        <div className="next-page-sentiment">
          <h2>Market Sentiment Analysis for {company.name}</h2>
          <div className="next-page-sentiment-box">
            {sentimentAnalysis || "Loading sentiment analysis..."}
          </div>
        </div>

        <div className="next-page-info-section">
          <h2>Additional Information</h2>
          <p>
          These charts give a comprehensive view of {company.name}'s stock performance, showing trends over time,
          price volatility, momentum, and potential price patterns. This data can help inform your investment decisions.
          </p>

          <div className="next-page-info-grid">
            <div className="next-page-info-item">
              <h2>Momentum</h2>
              <p>Rate of acceleration of {company.name}'s stock prices. A strong momentum suggests that a price trend is likely to continue and vice versa. A positive momentum often reflects bullish sentiment among investors; otherwise bearish sentiment.</p>
            </div>
            <div className="next-page-info-item">
              <h2>Moving Average</h2>
              <p>Smooths out {company.name}'s stock price data to identify trends over a specific period. An upward trend sloping moving average indicates a bullish trend and vice versa. It also acts as dynamic support and resistance levels. Prices may bounce off the moving average, indicating potential reversal points.</p>
            </div>
            <div className="next-page-info-item">
              <h2>Relative Strength Index</h2>
              <p>A momentum oscillator that measures speed and change of {company.name}'s stock price movements. An RSI of above 70 indicates a stock may be overbought, indicating a potential price correction and vice versa. An RSI of above 50 typically indicates a strong upward trend and vice versa.</p>
            </div>
            <div className="next-page-info-item">
              <h2>Feature Correlations</h2>
              <p>Correlations identify relationships between different features of {company.name}'s stocks, such as Closing Price and Volume. Understanding these relationships can inform trading strategies. Strong correlations between features can serve as potential predictors for stock price movements.</p>
            </div>
            <div className="next-page-info-item">
              <h2>Bollinger Bands</h2>
              <p>A technical analysis tool that consists of a middle band and two outer bands. Wider bands indicate increased volatility and potential price swings and vice versa. When {company.name}'s stock closing price touches or exceeds the upper band, it may indicate that the stock is overbought and vice versa.</p>
            </div>
            <div className="next-page-info-item">
              <h2>MACD</h2>
              <p>A popular momentum indicator used for technical {company.name}'s stock analysis. If this line is above zero, it indicates a bullish trend; otherwise, a bearish trend. When the MACD line crosses above the signal line, a bullish signal will be generated.</p>
            </div>
          </div>
        </div>

        <div className="next-page-chatbox">
          <div className="next-page-chat-messages">
            {messages.map((message, index) => (
              <div key={index} className={`next-page-message next-page-${message.sender}`}>
                {message.text}
              </div>
            ))}
          </div>
          <form onSubmit={handleChatSubmit} className="next-page-chat-input">
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Type a message..."
            />
            <button type="submit">Send</button>
          </form>
        </div>

        <div className="next-page-button-container">
          <button onClick={handleBack} className="next-page-back-button">BACK</button>
          <button onClick={handleNext} className="next-page-next-button">PREDICT</button>
        </div>
      </div>
    </div>
  );
};

export default NextPage;