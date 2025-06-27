// ProtectedRoute.js
import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';

const ProtectedRoute = ({ children }) => {
  const location = useLocation();
  const token = localStorage.getItem('access_token');
  
  if (!token) {
    return <Navigate to="/signup" replace state={{ from: location }} />;
  }
  
  return children;
};

export default ProtectedRoute;