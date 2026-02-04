import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Alert } from 'react-bootstrap';

const SessionManager = ({ activeSession }) => {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchSessions = async () => {
    setLoading(true);
    setError('');

    try {
      // 这里我们会调用API获取会话信息
      // 模拟数据
      const mockSessions = activeSession ? [{
        id: activeSession.id,
        host: activeSession.host,
        port: activeSession.port,
        protocol: activeSession.protocol,
        username: activeSession.username,
        status: activeSession.status,
        commandsCount: activeSession.commands_count || 0,
        startedAt: activeSession.started_at || new Date().toISOString()
      }] : [];

      setSessions(mockSessions);
    } catch (err) {
      setError('Failed to load sessions');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSessions();
  }, [activeSession]);

  const handleDisconnect = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/disconnect', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({})
      });

      if (response.ok) {
        alert('Disconnected successfully');
        fetchSessions(); // Refresh sessions list
      } else {
        const errorData = await response.json();
        alert(`Disconnection failed: ${errorData.detail || 'Unknown error'}`);
      }
    } catch (err) {
      alert(`Disconnection failed: ${err.message}`);
    }
  };

  const handleSessionDetail = (sessionId) => {
    alert(`Session detail for ${sessionId}`);
  };

  return (
    <Card>
      <Card.Header className="d-flex justify-content-between align-items-center">
        <h5>Session Manager</h5>
      </Card.Header>
      <Card.Body>
        {error && <Alert variant="danger">{error}</Alert>}

        {loading ? (
          <p>Loading sessions...</p>
        ) : (
          <>
            <div className="mb-3">
              <h6>Current Session</h6>
              {activeSession ? (
                <div className="border p-3 rounded bg-light">
                  <p><strong>ID:</strong> {activeSession.id}</p>
                  <p><strong>Host:</strong> {activeSession.host}:{activeSession.port}</p>
                  <p><strong>Protocol:</strong> {activeSession.protocol}</p>
                  <p><strong>Username:</strong> {activeSession.username}</p>
                  <p><strong>Status:</strong> {activeSession.status}</p>
                  <p><strong>Commands Executed:</strong> {activeSession.commands_count || 0}</p>
                  <Button variant="danger" onClick={handleDisconnect}>
                    Disconnect
                  </Button>
                </div>
              ) : (
                <div className="border p-3 rounded bg-light">
                  <p>No active session</p>
                  <p>Connect to a remote host to start a session.</p>
                </div>
              )}
            </div>

            <div className="mt-4">
              <h6>All Sessions</h6>
              {sessions.length > 0 ? (
                <Table striped bordered hover>
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Host</th>
                      <th>Protocol</th>
                      <th>Username</th>
                      <th>Status</th>
                      <th>Commands</th>
                      <th>Started At</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {sessions.map((session) => (
                      <tr key={session.id}>
                        <td>{session.id.substring(0, 12)}...</td>
                        <td>{session.host}:{session.port}</td>
                        <td>{session.protocol}</td>
                        <td>{session.username}</td>
                        <td>
                          <span className={`badge ${
                            session.status === 'connected' ? 'bg-success' :
                            session.status === 'connecting' ? 'bg-warning' : 'bg-secondary'
                          }`}>
                            {session.status}
                          </span>
                        </td>
                        <td>{session.commandsCount}</td>
                        <td>{new Date(session.startedAt).toLocaleString()}</td>
                        <td>
                          <Button
                            variant="info"
                            size="sm"
                            className="me-2"
                            onClick={() => handleSessionDetail(session.id)}
                          >
                            Detail
                          </Button>
                          <Button
                            variant="danger"
                            size="sm"
                            onClick={handleDisconnect}
                            disabled={!activeSession}
                          >
                            Disconnect
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              ) : (
                <p>No sessions found.</p>
              )}
            </div>
          </>
        )}
      </Card.Body>
    </Card>
  );
};

export default SessionManager;