// components/TransparentHeader.js
import React from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/Header.css';

const Header = ({ 
  showPredict = false, 
  showHome = true, 
  showSignOut = true,
  predictText = "PREDICT",
  homeText = "HOME",
  signOutText = "SIGNOUT",
  onPredict,
  customButtons = []
}) => {
  const navigate = useNavigate();

  const handleSignOut = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    navigate('/login');
  };

  const handleHome = () => {
    navigate('/app');
  };

  return (
    <header className="transparent-header">
      <div className="header-buttons">
        {/* Predict Button (conditionally shown) */}
        {showPredict && (
          <button 
            className="header-button predict-button" 
            onClick={onPredict}
          >
            {predictText}
          </button>
        )}

        {/* Home Button (conditionally shown) */}
        {showHome && (
          <button 
            className="header-button home-button" 
            onClick={handleHome}
          >
            {homeText}
          </button>
        )}

        {/* Custom Buttons */}
        {customButtons.map((button, index) => (
          <button
            key={index}
            className={`header-button ${button.className || ''}`}
            onClick={button.onClick}
          >
            {button.text}
          </button>
        ))}

        {/* Sign Out Button (conditionally shown) */}
        {showSignOut && (
          <button 
            className="header-button signout-button" 
            onClick={handleSignOut}
          >
            {signOutText}
          </button>
        )}
      </div>
    </header>
  );
};

export default Header;