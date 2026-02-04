import React, { useState } from 'react';
import { Card, Form, Button, Table, Modal, Alert } from 'react-bootstrap';

const ConnectionManager = ({ configs, setConfigs }) => {
  const [showModal, setShowModal] = useState(false);
  const [editingConfig, setEditingConfig] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    host: '',
    port: 22,
    username: '',
    password: '',
    auth_type: 'password',
    protocol: 'ssh'
  });
  const [error, setError] = useState('');

  const handleOpenModal = (config = null) => {
    if (config) {
      setEditingConfig(config);
      setFormData({
        name: config.name,
        host: config.host,
        port: config.port,
        username: config.username,
        password: config.password || '',
        auth_type: config.auth_type || 'password',
        protocol: config.protocol || 'ssh'
      });
    } else {
      setEditingConfig(null);
      setFormData({
        name: '',
        host: '',
        port: 22,
        username: '',
        password: '',
        auth_type: 'password',
        protocol: 'ssh'
      });
    }
    setError('');
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setError('');
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const configData = { ...formData, port: parseInt(formData.port) };

      if (editingConfig) {
        // 更新现有配置（在实际实现中）
        alert(`Would update config ${editingConfig.name} with the provided details`);
      } else {
        // 创建新配置
        const response = await fetch('http://localhost:8000/api/configs', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(configData)
        });

        if (response.ok) {
          const result = await response.json();
          // 在实际应用中，我们会更新configs状态
          alert('Configuration saved successfully!');
          setShowModal(false);
          // 重新加载配置列表
          fetchConfigs();
        } else {
          const errorData = await response.json();
          setError(errorData.detail || 'Failed to save configuration');
        }
      }
    } catch (err) {
      setError('Network error occurred');
    }
  };

  const fetchConfigs = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/configs');
      const data = await response.json();
      setConfigs(data.configs || []);
    } catch (err) {
      console.error('Error fetching configs:', err);
    }
  };

  const handleConnect = async (config) => {
    try {
      const response = await fetch('http://localhost:8000/api/connect', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          id: config.id,
          name: config.name,
          host: config.host,
          port: config.port,
          username: config.username,
          password: config.password,
          auth_type: config.auth_type,
          protocol: config.protocol
        })
      });

      if (response.ok) {
        const result = await response.json();
        alert(`Connected successfully! Session ID: ${result.session_id}`);
      } else {
        const errorData = await response.json();
        alert(`Connection failed: ${errorData.detail || 'Unknown error'}`);
      }
    } catch (err) {
      alert(`Connection failed: ${err.message}`);
    }
  };

  const handleDelete = async (configId) => {
    if (window.confirm('Are you sure you want to delete this configuration?')) {
      try {
        const response = await fetch(`http://localhost:8000/api/configs/${configId}`, {
          method: 'DELETE'
        });

        if (response.ok) {
          alert('Configuration deleted successfully!');
          fetchConfigs(); // Refresh the list
        } else {
          const errorData = await response.json();
          alert(`Deletion failed: ${errorData.detail || 'Unknown error'}`);
        }
      } catch (err) {
        alert(`Deletion failed: ${err.message}`);
      }
    }
  };

  return (
    <Card>
      <Card.Header className="d-flex justify-content-between align-items-center">
        <h5>Connection Manager</h5>
        <Button onClick={() => handleOpenModal()}>Add New Connection</Button>
      </Card.Header>
      <Card.Body>
        {configs.length === 0 ? (
          <p>No saved connections. Add a new connection to get started.</p>
        ) : (
          <Table striped bordered hover>
            <thead>
              <tr>
                <th>Name</th>
                <th>Host</th>
                <th>Port</th>
                <th>Username</th>
                <th>Protocol</th>
                <th>Auth Type</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {configs.map((config) => (
                <tr key={config.id}>
                  <td>{config.name}</td>
                  <td>{config.host}</td>
                  <td>{config.port}</td>
                  <td>{config.username}</td>
                  <td>{config.protocol || 'ssh'}</td>
                  <td>{config.auth_type || 'password'}</td>
                  <td>
                    <Button
                      variant="primary"
                      size="sm"
                      className="me-2"
                      onClick={() => handleConnect(config)}
                    >
                      Connect
                    </Button>
                    <Button
                      variant="secondary"
                      size="sm"
                      className="me-2"
                      onClick={() => handleOpenModal(config)}
                    >
                      Edit
                    </Button>
                    <Button
                      variant="danger"
                      size="sm"
                      onClick={() => handleDelete(config.id)}
                    >
                      Delete
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>
        )}

        <Modal show={showModal} onHide={handleCloseModal}>
          <Form onSubmit={handleSubmit}>
            <Modal.Header closeButton>
              <Modal.Title>{editingConfig ? 'Edit Connection' : 'Add New Connection'}</Modal.Title>
            </Modal.Header>
            <Modal.Body>
              {error && <Alert variant="danger">{error}</Alert>}

              <Form.Group className="mb-3">
                <Form.Label>Name *</Form.Label>
                <Form.Control
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  required
                />
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Label>Host *</Form.Label>
                <Form.Control
                  type="text"
                  name="host"
                  value={formData.host}
                  onChange={handleChange}
                  required
                />
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Label>Port *</Form.Label>
                <Form.Control
                  type="number"
                  name="port"
                  value={formData.port}
                  onChange={handleChange}
                  required
                />
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Label>Username *</Form.Label>
                <Form.Control
                  type="text"
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  required
                />
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Label>Password</Form.Label>
                <Form.Control
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                />
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Label>Authentication Type</Form.Label>
                <Form.Select
                  name="auth_type"
                  value={formData.auth_type}
                  onChange={handleChange}
                >
                  <option value="password">Password</option>
                  <option value="key">SSH Key</option>
                </Form.Select>
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Label>Protocol</Form.Label>
                <Form.Select
                  name="protocol"
                  value={formData.protocol}
                  onChange={handleChange}
                >
                  <option value="ssh">SSH</option>
                  <option value="telnet">Telnet</option>
                </Form.Select>
              </Form.Group>
            </Modal.Body>
            <Modal.Footer>
              <Button variant="secondary" onClick={handleCloseModal}>
                Cancel
              </Button>
              <Button variant="primary" type="submit">
                {editingConfig ? 'Update' : 'Save'} Connection
              </Button>
            </Modal.Footer>
          </Form>
        </Modal>
      </Card.Body>
    </Card>
  );
};

export default ConnectionManager;