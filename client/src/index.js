import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter as Router, Routes, Route, Navigate} from 'react-router-dom';
import App from './pages/App';
import { jwtDecode } from 'jwt-decode';
import NextPage from './pages/NextPage';
import NextNextPage from './pages/NextNextPage';
import Login from './pages/login';
import Signup from './pages/signup';
import ProtectedRoute from './private/ProtectedRoute';

const token = localStorage.getItem('access_token');
if (token) {
  try {
    const { decoded } = jwtDecode(token);
    const tokenExpiration = decoded.exp;
    const now = Date.now() / 1000;
    if (tokenExpiration < now) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  } catch {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }
}


ReactDOM.render(
  <Router>
    <Routes>
      <Route index element={<Login />} />
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />
      <Route path="/app" element={<ProtectedRoute><App /></ProtectedRoute>} />
      <Route path="/next-page" element={<ProtectedRoute><NextPage /></ProtectedRoute>} />
      <Route path="/next-next-page" element={<ProtectedRoute><NextNextPage /></ProtectedRoute>} />
    </Routes>
  </Router>,
  document.getElementById('root')
);


