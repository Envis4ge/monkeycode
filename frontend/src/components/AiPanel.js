import React, { useState } from 'react';
import { Card, Form, Button, ListGroup } from 'react-bootstrap';

const AiPanel = ({ activeSession }) => {
  const [inputValue, setInputValue] = useState('');
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!inputValue.trim()) return;

    const userMessage = { type: 'user', content: inputValue, timestamp: new Date() };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // 发送自然语言命令到后端AI接口
      const response = await fetch('http://localhost:8000/api/command', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          command: inputValue,
          mode: 'ai'
        })
      });

      const data = await response.json();

      if (response.ok) {
        const aiMessage = {
          type: 'ai',
          originalRequest: data.original_request,
          convertedCommand: data.converted_command,
          explanation: data.explanation,
          confidence: data.confidence,
          output: data.output,
          exitCode: data.exit_code,
          timestamp: new Date()
        };

        setMessages(prev => [...prev, aiMessage]);
      } else {
        const errorMessage = {
          type: 'error',
          content: data.detail || 'Error processing command',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      const errorMessage = {
        type: 'error',
        content: `Network error: ${error.message}`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      setInputValue('');
    }
  };

  return (
    <Card>
      <Card.Header>
        <h5>AI Assistant</h5>
        <p>Status: {activeSession ? `Connected to ${activeSession.host}:${activeSession.port}` : 'No active session'}</p>
      </Card.Header>
      <Card.Body>
        <div className="ai-messages mb-3">
          <ListGroup>
            {messages.map((msg, index) => (
              <ListGroup.Item key={index} className={msg.type === 'user' ? 'bg-light' : ''}>
                {msg.type === 'user' ? (
                  <div>
                    <strong>You:</strong> {msg.content}
                  </div>
                ) : msg.type === 'ai' ? (
                  <div>
                    <strong>AI:</strong> {msg.originalRequest}<br/>
                    <small className="text-muted">
                      Converted to: <code>{msg.convertedCommand}</code> (Confidence: {(msg.confidence * 100).toFixed(0)}%)<br/>
                      Explanation: {msg.explanation}
                    </small><br/>
                    <pre className="mt-2 p-2 bg-secondary text-white">{msg.output}</pre>
                  </div>
                ) : (
                  <div className="text-danger">
                    <strong>Error:</strong> {msg.content}
                  </div>
                )}
              </ListGroup.Item>
            ))}
            {isLoading && (
              <ListGroup.Item>
                <div className="text-info">
                  <strong>AI:</strong> Processing your request...
                </div>
              </ListGroup.Item>
            )}
          </ListGroup>
        </div>

        <Form onSubmit={handleSubmit}>
          <Form.Group className="mb-3">
            <Form.Label>Describe what you want to do:</Form.Label>
            <Form.Control
              type="text"
              placeholder="e.g., 'Show me the current directory contents'"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              disabled={!activeSession}
            />
          </Form.Group>
          <Button type="submit" disabled={!activeSession || isLoading || !inputValue.trim()}>
            {isLoading ? 'Processing...' : 'Send to AI'}
          </Button>
          {!activeSession && (
            <div className="text-warning mt-2">
              Please establish a connection first to use the AI assistant.
            </div>
          )}
        </Form>
      </Card.Body>
    </Card>
  );
};

export default AiPanel;