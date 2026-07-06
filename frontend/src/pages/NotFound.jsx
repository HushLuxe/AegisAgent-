import React from 'react';
import { Link } from 'react-router-dom';

const NotFound = () => {
  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'var(--bg)',
      color: 'var(--text-main)',
      fontFamily: "'Bricolage Grotesque', sans-serif",
      textAlign: 'center',
      padding: '24px',
    }}>
      <div style={{
        fontSize: '72px',
        fontWeight: 800,
        color: 'var(--accent)',
        fontFamily: "'JetBrains Mono', monospace",
        lineHeight: 1,
        marginBottom: '8px',
      }}>
        404
      </div>
      <div style={{
        fontSize: '11px',
        color: 'var(--text-ghost)',
        textTransform: 'uppercase',
        letterSpacing: '0.1em',
        marginBottom: '24px',
      }}>
        Signal Not Found
      </div>
      <p style={{
        fontSize: '13px',
        color: 'var(--text-dim)',
        maxWidth: '400px',
        lineHeight: 1.6,
        marginBottom: '32px',
      }}>
        The forensic node you are looking for does not exist or has been rotated.
        Return to the intelligence dashboard.
      </p>
      <Link
        to="/"
        style={{
          background: 'var(--accent)',
          color: '#000',
          padding: '10px 24px',
          borderRadius: '4px',
          fontSize: '12px',
          fontWeight: 700,
          textDecoration: 'none',
          letterSpacing: '0.5px',
        }}
      >
        Return to Base
      </Link>
    </div>
  );
};

export default NotFound;
