import React, { useState } from 'react';
import { Card, Form, Button, Alert } from 'react-bootstrap';

const Settings = () => {
  const [settings, setSettings] = useState({
    terminalFontSize: 14,
    terminalTheme: 'dark',
    autoReconnect: true,
    showNotifications: true,
    enableAIFeatures: true
  });
  const [saved, setSaved] = useState(false);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setSettings(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // 实际应用中，这里会保存设置到后端
    console.log('Saving settings:', settings);
    setSaved(true);
    setTimeout(() => setSaved(false), 3000); // Hide success message after 3 seconds
  };

  return (
    <Card>
      <Card.Header>
        <h5>Settings</h5>
      </Card.Header>
      <Card.Body>
        {saved && (
          <Alert variant="success">
            Settings saved successfully!
          </Alert>
        )}

        <Form onSubmit={handleSubmit}>
          <Form.Group className="mb-3">
            <Form.Label>Terminal Font Size</Form.Label>
            <Form.Control
              type="number"
              name="terminalFontSize"
              value={settings.terminalFontSize}
              onChange={handleChange}
              min="8"
              max="24"
            />
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Terminal Theme</Form.Label>
            <Form.Select
              name="terminalTheme"
              value={settings.terminalTheme}
              onChange={handleChange}
            >
              <option value="dark">Dark</option>
              <option value="light">Light</option>
              <option value="classic">Classic</option>
            </Form.Select>
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Check
              type="switch"
              name="autoReconnect"
              label="Auto Reconnect on Disconnection"
              checked={settings.autoReconnect}
              onChange={handleChange}
            />
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Check
              type="switch"
              name="showNotifications"
              label="Show Notifications"
              checked={settings.showNotifications}
              onChange={handleChange}
            />
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Check
              type="switch"
              name="enableAIFeatures"
              label="Enable AI Features"
              checked={settings.enableAIFeatures}
              onChange={handleChange}
            />
          </Form.Group>

          <Button variant="primary" type="submit">
            Save Settings
          </Button>
        </Form>
      </Card.Body>
    </Card>
  );
};

export default Settings;