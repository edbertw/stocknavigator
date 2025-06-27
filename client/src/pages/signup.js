// Signup.js
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './AuthStyles.css';

const Signup = () => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [password2, setPassword2] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (password !== password2) {
      setError("Passwords don't match");
      return;
    }

    try {
      // Register the user
      const response = await fetch('http://127.0.0.1:8000/api/user/register/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username,
          email,
          password,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        let errorMessage = 'Registration failed';
        if (errorData.username) {
          errorMessage = errorData.username[0];
        } else if (errorData.email) {
          errorMessage = errorData.email[0];
        } else if (errorData.password) {
          errorMessage = errorData.password[0];
        }
        throw new Error(errorMessage);
      }

      // Automatically log in after registration
      const loginResponse = await fetch('http://127.0.0.1:8000/api/token/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username,
          password,
        }),
      });

      if (!loginResponse.ok) {
        throw new Error('Registration successful but automatic login failed. Please log in manually.');
      }

      const data = await loginResponse.json();
      
      // Store tokens
      localStorage.setItem('access_token', data.access);
      localStorage.setItem('refresh_token', data.refresh);
      
      // Redirect to stock navigator
      navigate('/app');
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="auth-container">
      <h1>Stock Navigator</h1>
      <p>Create an account to access stock insights and predictions</p>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="username">Username</label>
          <input
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>
        
        
        <div className="form-group">
          <label htmlFor="password">Password</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="password2">Confirm Password</label>
          <input
            type="password"
            id="password2"
            value={password2}
            onChange={(e) => setPassword2(e.target.value)}
            required
          />
        </div>
        
        {error && <div className="error">{error}</div>}
        
        <button type="submit" className="signup-button">Sign Up</button>
      </form>
      
      <div className="switch-auth">
        Already have an account? <button className="link-button" onClick={() => navigate('/login')}>Log in</button>
      </div>
      
      <div className="footer">
        © 2025 Stock Navigator. All rights reserved.
      </div>
    </div>
  );
};

export default Signup;