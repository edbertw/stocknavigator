import React, { useState, useEffect, useRef, useCallback } from 'react';
import '../styles/ChatInterface.css';

const ChatInterface = ({ sessionId, userId, onSessionEnd }) => {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const messagesEndRef = useRef(null);

  // Scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load messages for current session
  const loadSessionMessages = useCallback(async () => {
    if (!sessionId) return;

    setLoading(true);
    setError('');

    try {
      const response = await fetch(`http://127.0.0.1:8000/api/get-chat-session/${sessionId}/`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to load session messages');
      }

      const data = await response.json();
      const formattedMessages = data.messages.map(msg => ({
        id: msg.id,
        text: msg.content,
        sender: msg.message_type === 'user' ? 'user' : 'bot',
        timestamp: msg.timestamp
      }));

      setMessages(formattedMessages);
    } catch (err) {
      setError('Failed to load messages');
      console.error('Error loading session messages:', err);
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  // Load session messages when sessionId changes
  useEffect(() => {
    if (sessionId) {
      loadSessionMessages();
    } else {
      setMessages([]);
    }
  }, [sessionId, loadSessionMessages]);

  // Send message to chatbot
  const sendMessage = async (e) => {
    e.preventDefault();
    
    if (!inputText.trim() || !sessionId || !userId) return;

    const userMessage = {
      id: Date.now(),
      text: inputText,
      sender: 'user',
      timestamp: new Date().toISOString()
    };

    // Add user message immediately
    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setLoading(true);
    setError('');

    try {
      const response = await fetch('http://127.0.0.1:8000/api/ask-chatbot/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: inputText,
          session_id: sessionId,
          user_id: userId
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get bot response');
      }

      const data = await response.json();
      
      const botMessage = {
        id: Date.now() + 1,
        text: data.response,
        sender: 'bot',
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (err) {
      setError('Failed to get response from chatbot');
      console.error('Error sending message:', err);
      
      const errorMessage = {
        id: Date.now() + 1,
        text: 'Sorry, I encountered an error. Please try again.',
        sender: 'assistant',
        timestamp: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  // Format timestamp for display
  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  if (!sessionId) {
    return (
      <div className="chat-interface no-session">
        <div className="no-session-message">
          <h3>Select a Chat Session</h3>
          <p>Choose an existing session or create a new one to start chatting with our bot.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <h3>Chat Assistant</h3>
        <div className="session-info">
          Session: {sessionId.slice(0, 8)}...
        </div>
        {onSessionEnd && (
          <button 
            className="end-session-btn"
            onClick={() => onSessionEnd(sessionId)}
            title="End Session"
          >
            ✗
          </button>
        )}
      </div>

      <div className="chat-messages">
        {loading && messages.length === 0 && (
          <div className="loading-message">Loading conversation...</div>
        )}
        
        {messages.map((message) => (
          <div key={message.id} className={`message ${message.sender}`}>
            <div className="message-content">
              <div className="message-text">{message.text}</div>
              <div className="message-time">{formatTime(message.timestamp)}</div>
            </div>
          </div>
        ))}
        
        {loading && messages.length > 0 && (
          <div className="message bot">
            <div className="message-content">
              <div className="message-text typing">Assistant is typing...</div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {error && <div className="chat-error">{error}</div>}

      <form onSubmit={sendMessage} className="chat-input-form">
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Ask about financial analysis, technical indicators..."
          disabled={loading}
          className="chat-input"
        />
        <button 
          type="submit" 
          disabled={loading || !inputText.trim()}
          className="send-button"
        >
          {loading ? 'Sending...' : 'Send'}
        </button>
      </form>
    </div>
  );
};

export default ChatInterface;
