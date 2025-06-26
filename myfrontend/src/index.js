import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter as Router, Routes, Route, Navigate} from 'react-router-dom';
import App from './App';
import NextPage from './NextPage';
import NextNextPage from './NextNextPage';
import Login from './login';
import Signup from './signup';
import ProtectedRoute from './ProtectedRoute';

ReactDOM.render(
  <Router>
    <Routes>
      <Route index element={<Login />} />
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />
      <Route path="/app" element={<ProtectedRoute><App /></ProtectedRoute>} />
      <Route path="/next-page" element={<NextPage />} />
      <Route path="/next-next-page" element={<NextNextPage />} />
    </Routes>
  </Router>,
  document.getElementById('root')
);


