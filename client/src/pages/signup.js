// Signup.js
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/AuthStyles.css';
import Footer from '../components/Footer';
import { useUser } from '../contexts/UserContext';

const Signup = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [password2, setPassword2] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useUser();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    if (password !== password2) {
      setError("Passwords don't match");
      setLoading(false);
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
          password,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        let errorMessage = 'Registration failed';
        if (errorData.username) {
          errorMessage = errorData.username[0];
        } else if (errorData.password) {
          errorMessage = errorData.password[0];
        }
        throw new Error(errorMessage);
      }

      // Automatically log in after registration
      const result = await login(username, password);
      
      if (result.success) {
        navigate('/app');
      } else {
        throw new Error('Registration successful but automatic login failed. Please log in manually.');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
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
        
        <button type="submit" className="signup-button" disabled={loading}>
          {loading ? 'Creating Account...' : 'Sign Up'}
        </button>
      </form>
      
      <div className="switch-auth">
        Already have an account? <button className="link-button" onClick={() => navigate('/login')}>Log in</button>
      </div>
      
      <Footer />
    </div>
  );
};

export default Signup;