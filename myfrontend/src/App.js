import React, { useState } from 'react';
import './App.css';
import { useNavigate, Routes, Route } from 'react-router-dom';
import NextPage from './NextPage'; // Import NextPage
import NextNextPage from './NextNextPage'; // Import NextNextPage

const logoImage = 'file.png'; 

const App = () => {
  const [selectedValue, setSelectedValue] = useState(''); // Selected stock
  const [loading, setLoading] = useState(false); // Loading state
  const [error, setError] = useState(''); // Error state
  const [description, setDescription] = useState(''); // Description state
  const navigate = useNavigate(); // Navigation

  const handleSelectChange = (e) => {
    const value = e.target.value;
    setSelectedValue(value); // Update selected stock

    // Update description based on selected stock
    const descriptions = {
      NVDA: 'NVIDIA is a leading manufacturer of GPUs for gaming and AI computing.',
      NDAQ: 'NASDAQ is an American stock exchange, the second-largest in the world by market cap.',
      TSLA: 'Tesla is a clean energy and electric vehicle company.',
      HSBC: 'HSBC is one of the world\'s largest banking and financial services organizations.',
      JPM: 'JP Morgan is a global leader in financial services offering solutions to corporations, institutions, and governments.',
    };
    setDescription(descriptions[value] || '');
  };

  const handleSubmit = () => {
    setLoading(true); // Show loading
    setError(''); // Clear errors

    // API call to submit stock
    fetch('http://127.0.0.1:8000/api/submit-stock/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        stock_symbol: selectedValue, // Send selected stock
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.company) {
          // Navigate to NextPage with state
          navigate('/next-page', { state: { stockSymbol: selectedValue, company: data.company } });
        } else {
          setError(data.error || 'Company not found'); // Handle error
        }
        setLoading(false); // Hide loading
      })
      .catch(() => {
        setError('Error fetching company details'); // API call failed
        setLoading(false); // Hide loading
      });
  };

  return (
    <div className="app-container"> 
      <Routes>
        <Route path="/" element={
          <div className="content">
            <img src={logoImage} alt="Logo" className="app-logo" />
            <h1>Stock Navigator</h1>

            {/* Application description */}
            <div className="app-description">
              <p>
                Stock Navigator is a powerful tool to analyze and visualize stock data in real-time. 
              </p>
              <p>
                Select a stock from the dropdown menu to view detailed analytics, including price trends, 
                moving averages, predictions, and so much more.
              </p>
              <p>
                We have additional features incoming, including a chatbot to handle personalized queries
              </p>
            </div>

            {/* Dropdown container */}
            <div className="dropdown-container">
              <label htmlFor="dropdown">Choose a stock: </label>
              <select id="dropdown" value={selectedValue} onChange={handleSelectChange}>
                <option value="" disabled>Select a stock</option>
                <option value="NVDA">NVIDIA</option>
                <option value="NDAQ">NASDAQ</option>
                <option value="TSLA">TESLA</option>
                <option value="HSBC">HSBC</option>
                <option value="JPM">JP Morgan</option>
              </select>
            </div>

            {/* Description box */}
            {description && (
              <div className="description-box">
                <p>{description}</p>
              </div>
            )}

            {/* Submit button */}
            <button onClick={handleSubmit} disabled={!selectedValue || loading}>
              {loading ? 'Submitting...' : 'Submit'}
            </button>

            {/* Error message */}
            {error && <p className="error">{error}</p>}
          </div>
        } />
        
        {/* Next pages */}
        <Route path="/next-page" element={<NextPage />} />
        <Route path="/next-next-page" element={<NextNextPage />} />
      </Routes>
    </div>
  );
};

export default App;