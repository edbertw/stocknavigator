import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import App from './App';
import NextPage from './NextPage';
import NextNextPage from './NextNextPage'

ReactDOM.render(
  <Router>
    <Routes>
      <Route path="/" element={<App />} />
      <Route path="/next-page" element={<NextPage />} />
      <Route path="/next-next-page" element={<NextNextPage />} />
    </Routes>
  </Router>,
  document.getElementById('root')
);


