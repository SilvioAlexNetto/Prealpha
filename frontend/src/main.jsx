import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { Capacitor } from '@capacitor/core';

import './index.css';
import './styles/global.css';

import App from './App.jsx';
import React from 'react';

// =======================
// ERROR BOUNDARY PARA ERROS DE REACT
// =======================
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, info: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    console.error("Erro capturado pelo ErrorBoundary:", error, info);
    this.setState({ error, info });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div
          style={{
            padding: 20,
            color: '#fff',
            backgroundColor: 'red',
            fontFamily: 'monospace',
            whiteSpace: 'pre-wrap',
          }}
        >
          <h2>Ocorreu um erro no app!</h2>
          <strong>{this.state.error?.toString()}</strong>
          <pre>{this.state.info?.componentStack}</pre>
        </div>
      );
    }
    return this.props.children;
  }
}

// =======================
// DEBUG GLOBAL DE ERROS
// =======================

// Captura erros não tratados de JS
window.onerror = function (message, source, lineno, colno, error) {
  console.error("Erro global capturado:", { message, source, lineno, colno, error });
  alert(`Erro global: ${message}\nLinha: ${lineno}, Coluna: ${colno}`);
};

// Captura Promises rejeitadas não tratadas
window.onunhandledrejection = function (event) {
  console.error("Promise rejeitada não tratada:", event.reason);
  alert(`Promise rejeitada: ${event.reason}`);
};

// =======================
// RENDERIZAÇÃO DO APP
// =======================
createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </StrictMode>,
);

// =======================
// SERVICE WORKER (SOMENTE NAVEGADOR)
// =======================
if ("serviceWorker" in navigator && !Capacitor.isNativePlatform()) {
  window.addEventListener("load", () => {
    navigator.serviceWorker
      .register("/service-worker.js")
      .then(() => console.log("Service Worker registrado"))
      .catch(err => console.error("Erro no SW:", err));
  });
}