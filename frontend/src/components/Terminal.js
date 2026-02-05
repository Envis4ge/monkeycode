import React, { useEffect, useRef } from 'react';
import { Terminal as XTerm } from 'xterm';
import { FitAddon } from 'xterm-addon-fit';
import { WebLinksAddon } from 'xterm-addon-web-links';
import 'xterm/css/xterm.css';

const Terminal = ({ activeSession }) => {
  const terminalRef = useRef(null);
  const termRef = useRef(null);
  const wsRef = useRef(null);

  useEffect(() => {
    // 初始化xterm.js
    if (!termRef.current) {
      const term = new XTerm({
        cursorBlink: true,
        theme: {
          background: '#000',
          foreground: '#fff',
          selection: '#aaa'
        }
      });

      const fitAddon = new FitAddon();
      term.loadAddon(fitAddon);
      term.loadAddon(new WebLinksAddon());

      term.open(terminalRef.current);
      termRef.current = term;

      // 调整大小
      fitAddon.fit();

      window.addEventListener('resize', () => {
        setTimeout(() => fitAddon.fit());
      });
    }

    // 连接到WebSocket终端服务
    if (activeSession && !wsRef.current) {
      const ws = new WebSocket('ws://localhost:3000/ws/terminal');

      ws.onopen = () => {
        termRef.current.writeln('Connected to terminal...');
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);

        switch (data.type) {
          case 'output':
            termRef.current.writeln(data.output || '');
            break;
          case 'ai_result':
            termRef.current.writeln(`AI converted: ${data.converted_command}`);
            termRef.current.writeln(`Confidence: ${data.confidence}`);
            termRef.current.writeln(data.output || '');
            break;
          case 'error':
            termRef.current.writeln(`Error: ${data.message}`);
            break;
          default:
            termRef.current.writeln(data.data || '');
        }
      };

      ws.onclose = () => {
        termRef.current.writeln('Disconnected from terminal...');
      };

      ws.onerror = (error) => {
        termRef.current.writeln(`WebSocket error: ${error}`);
      };

      wsRef.current = ws;

      // 监听键盘输入
      termRef.current.onData(data => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
          const commandData = {
            command: data,
            mode: "interactive"
          };
          wsRef.current.send(JSON.stringify(commandData));
        }
      });
    }

    // 清理函数
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [activeSession]);

  return (
    <div className="card">
      <div className="card-header">
        <h5>Terminal</h5>
        <p>Status: {activeSession ? `Connected to ${activeSession.host}:${activeSession.port}` : 'No active session'}</p>
      </div>
      <div className="card-body p-0">
        <div ref={terminalRef} className="terminal-container" />
      </div>
    </div>
  );
};

export default Terminal;