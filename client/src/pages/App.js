import React, { useState, useEffect } from 'react';
import './App.css';
import { useNavigate, Routes, Route } from 'react-router-dom';
import NextPage from './NextPage'; // Import NextPage
import NextNextPage from './NextNextPage'; // Import NextNextPage
import { FaLinkedin, FaInstagram, FaGithub } from 'react-icons/fa'; // Import LinkedIn and Instagram icons

const App = () => {
  const [selectedValue, setSelectedValue] = useState(''); // Selected stock
  const [loading, setLoading] = useState(false); // Loading state
  const [error, setError] = useState(''); // Error state
  const [description, setDescription] = useState(''); // Description state
  const [username, setUsername] = useState(null); // Username state
  const navigate = useNavigate(); // Navigation
  

  useEffect(() => {
    const fetchUserInfo = async () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          const response = await fetch('http://127.0.0.1:8000/api/user/info/', {
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          });
          
          if (response.ok) {
            const userData = await response.json();
            setUsername(userData.username);
          }
        } catch (err) {
          console.error('Error fetching user info:', err);
        }
      }
    };

    fetchUserInfo();
  }, []);


  const handleSelectChange = (e) => {
    const value = e.target.value;
    setSelectedValue(value); // Update selected stock

    // Update description based on selected stock
    const descriptions = {
      NVDA: 'NVIDIA is a leading manufacturer of GPUs for gaming and AI computing.',
      NDAQ: 'NASDAQ is an American stock exchange, the second-largest in the world by market cap.',
      TSLA: 'Tesla is a clean energy and electric vehicle company.',
      HSBC: 'HSBC is one of the world\'s largest banking and financial services organizations.',
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
      .catch((err) => {
        setError('An error occurred while submitting the stock.');
        setLoading(false); // Hide loading
      });
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>📈 Stock Navigator</h1>
        {username && (
          <div className="welcome-message">
            Welcome, <span className="username">{username}</span>!
          </div>
        )}
        <p>Explore insights and predictions for your favorite stocks.</p>
      </header>

      <main className="app-main">
        <div className="stock-selector">
          <label htmlFor="stock-select">Select a Stock:</label>
          <select
            id="stock-select"
            value={selectedValue}
            onChange={handleSelectChange}
            className="stock-dropdown"
          >
            <option value="">-- Choose a Stock --</option>
            <option value="NVDA">NVIDIA</option>
            <option value="NDAQ">NASDAQ</option>
            <option value="TSLA">Tesla</option>
            <option value="HSBC">HSBC</option>
          </select>
        </div>

        {description && (
          <div className="stock-description">
            <h3>About the Stock:</h3>
            <p>{description}</p>
          </div>
        )}

        {error && <p className="error-message">{error}</p>}

        <button
          onClick={handleSubmit}
          className="submit-button"
          disabled={loading || !selectedValue}
        >
          {loading ? 'Submitting...' : 'Submit'}
        </button>
      </main>

      <footer className="app-footer">
        <p>© 2025 Stock Navigator. All rights reserved.</p>
        <div className="social-icons">
          <a href="https://www.linkedin.com/in/edbertwidjaja/" target="_blank" rel="noopener noreferrer">
            <FaLinkedin size={24} style={{ marginRight: '10px', color: '#0077b5' }} />
          </a>
          <a href="https://www.instagram.com/edbert__wid/" target="_blank" rel="noopener noreferrer">
            <FaInstagram size={24} style={{ marginRight: '10px', color: '#e4405f' }} />
          </a>
          <a href="https://github.com/edbertw" target="_blank" rel="noopener noreferrer">
            <FaGithub size={24} style={{ color: '#333' }} />
          </a>  
        </div>
      </footer>

      <Routes>
        <Route path="/next-page" element={<NextPage />} />
        <Route path="/next-next-page" element={<NextNextPage />} />
      </Routes>
    </div>
  );
};

export default App;