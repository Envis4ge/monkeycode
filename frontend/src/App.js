import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Container, Nav, Navbar, Tab, Row, Col } from 'react-bootstrap';
import ConnectionManager from './components/ConnectionManager';
import Terminal from './components/Terminal';
import AiPanel from './components/AiPanel';
import SessionManager from './components/SessionManager';
import Settings from './components/Settings';
import 'bootstrap/dist/css/bootstrap.min.css';

function App() {
  const [activeSession, setActiveSession] = useState(null);
  const [connectionConfigs, setConnectionConfigs] = useState([]);

  // 模拟获取连接配置
  useEffect(() => {
    fetch('http://localhost:8000/api/configs')
      .then(response => response.json())
      .then(data => setConnectionConfigs(data.configs || []))
      .catch(error => console.error('Error fetching configs:', error));
  }, []);

  return (
    <Router>
      <div className="App">
        <Navbar bg="dark" variant="dark" expand="lg">
          <Container>
            <Navbar.Brand href="/">SmartTerm Web UI</Navbar.Brand>
            <Navbar.Toggle aria-controls="basic-navbar-nav" />
            <Navbar.Collapse id="basic-navbar-nav">
              <Nav className="me-auto">
                <Nav.Link href="/">Home</Nav.Link>
                <Nav.Link href="/connections">Connections</Nav.Link>
                <Nav.Link href="/terminal">Terminal</Nav.Link>
                <Nav.Link href="/ai">AI Assistant</Nav.Link>
                <Nav.Link href="/sessions">Sessions</Nav.Link>
                <Nav.Link href="/settings">Settings</Nav.Link>
              </Nav>
            </Navbar.Collapse>
          </Container>
        </Navbar>

        <Container fluid className="mt-3">
          <Tab.Container id="main-tabs" defaultActiveKey="terminal">
            <Row>
              <Col sm={3}>
                <div className="nav flex-column nav-pills">
                  <button className="nav-link" data-bs-toggle="pill" data-bs-target="#terminal-tab">Terminal</button>
                  <button className="nav-link" data-bs-toggle="pill" data-bs-target="#ai-tab">AI Assistant</button>
                  <button className="nav-link" data-bs-toggle="pill" data-bs-target="#connections-tab">Connections</button>
                  <button className="nav-link" data-bs-toggle="pill" data-bs-target="#sessions-tab">Sessions</button>
                  <button className="nav-link" data-bs-toggle="pill" data-bs-target="#settings-tab">Settings</button>
                </div>
              </Col>
              <Col sm={9}>
                <Tab.Content>
                  <Tab.Pane eventKey="terminal">
                    <Terminal activeSession={activeSession} />
                  </Tab.Pane>
                  <Tab.Pane eventKey="ai">
                    <AiPanel activeSession={activeSession} />
                  </Tab.Pane>
                  <Tab.Pane eventKey="connections">
                    <ConnectionManager
                      configs={connectionConfigs}
                      setConfigs={setConnectionConfigs}
                    />
                  </Tab.Pane>
                  <Tab.Pane eventKey="sessions">
                    <SessionManager activeSession={activeSession} />
                  </Tab.Pane>
                  <Tab.Pane eventKey="settings">
                    <Settings />
                  </Tab.Pane>
                </Tab.Content>
              </Col>
            </Row>
          </Tab.Container>
        </Container>
      </div>
    </Router>
  );
}

export default App;