import React, { useState, useEffect, useCallback } from 'react';
import '../styles/ChatSessionManager.css';

const ChatSessionManager = ({ userId, onSessionSelect, currentSessionId, onSessionEnd }) => {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showNewSessionForm, setShowNewSessionForm] = useState(false);

  // Fetch user sessions
  const fetchSessions = useCallback(async () => {
    if (!userId) return;
    
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch(`http://127.0.0.1:8000/api/get-user-sessions/${userId}/`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch sessions');
      }

      const data = await response.json();
      setSessions(data.sessions || []);
    } catch (err) {
      setError('Failed to load sessions');
      console.error('Error fetching sessions:', err);
    } finally {
      setLoading(false);
    }
  }, [userId]);

  // Create new session
  const createNewSession = async () => {
    if (!userId) return;

    setLoading(true);
    setError('');

    try {
      const response = await fetch('http://127.0.0.1:8000/api/create-chat-session/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_id: userId }),
      });

      if (!response.ok) {
        throw new Error('Failed to create session');
      }

      const data = await response.json();
      const newSession = {
        session_id: data.session_id,
        created_at: data.created_at,
        updated_at: data.created_at,
        message_count: 0
      };

      setSessions(prev => [newSession, ...prev]);
      onSessionSelect(data.session_id);
      setShowNewSessionForm(false);
    } catch (err) {
      setError('Failed to create session');
      console.error('Error creating session:', err);
    } finally {
      setLoading(false);
    }
  };

  // End session
  const endSession = async (sessionId) => {
    if (!sessionId) return;

    setLoading(true);
    setError('');

    try {
      const response = await fetch(`http://127.0.0.1:8000/api/end-chat-session/${sessionId}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to end session');
      }

      setSessions(prev => prev.filter(session => session.session_id !== sessionId));
      
      if (currentSessionId === sessionId) {
        onSessionSelect(null);
      }
      
      if (onSessionEnd) {
        onSessionEnd(sessionId);
      }
    } catch (err) {
      setError('Failed to end session');
      console.error('Error ending session:', err);
    } finally {
      setLoading(false);
    }
  };

  // Format date for display
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);

  return (
    <div className="chat-session-manager">
      <div className="session-manager-header">
        <h3>Chat Sessions</h3>
        <button 
          className="new-session-btn"
          onClick={() => setShowNewSessionForm(true)}
          disabled={loading}
        >
          + New Session
        </button>
      </div>

      {error && <div className="session-error">{error}</div>}

      {showNewSessionForm && (
        <div className="new-session-form">
          <p>Create a new chat session?</p>
          <div className="form-buttons">
            <button onClick={createNewSession} disabled={loading}>
              {loading ? 'Creating...' : 'Yes, Create'}
            </button>
            <button onClick={() => setShowNewSessionForm(false)}>
              Cancel
            </button>
          </div>
        </div>
      )}

      <div className="sessions-list">
        {loading && sessions.length === 0 ? (
          <div className="loading">Loading sessions...</div>
        ) : sessions.length === 0 ? (
          <div className="no-sessions">No active sessions</div>
        ) : (
          sessions.map((session) => (
            <div 
              key={session.session_id} 
              className={`session-item ${currentSessionId === session.session_id ? 'active' : ''}`}
            >
              <div 
                className="session-info"
                onClick={() => onSessionSelect(session.session_id)}
              >
                <div className="session-id">
                  Session {session.session_id.slice(0, 8)}...
                </div>
                <div className="session-details">
                  <div className="session-time">
                    {formatDate(session.updated_at)}
                  </div>
                  <div className="session-messages">
                    {session.message_count} messages
                  </div>
                </div>
              </div>
              <button 
                className="end-session-btn"
                onClick={() => endSession(session.session_id)}
                disabled={loading}
                title="End Session"
              >
                ×
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default ChatSessionManager;
