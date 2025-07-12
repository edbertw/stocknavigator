import React from 'react';
import { FaLinkedin, FaInstagram, FaGithub } from 'react-icons/fa';
import '../styles/Footer.css';

const Footer = ({ year = 2025, appName = "Stock Navigator" }) => {
  return (
    <footer className="app-footer">
      <p>© {year} {appName}. All rights reserved.</p>
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
  );
};

export default Footer;