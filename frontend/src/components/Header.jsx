import React from 'react';
import { Link } from 'react-router-dom';

const Header = () => {
  const [wallet, setWallet] = React.useState(null);

  const connectWallet = async () => {
    if (!window.ethereum) {
      alert("No wallet — install MetaMask");
      return;
    }
    try {
      const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
      setWallet(accounts[0]);
    } catch (e) {
      console.error(e);
    }
  };

  const handleRefresh = async () => {
    try {
      await fetch('/api/forensics?refresh=true');
      window.location.reload();
    } catch (e) {
      console.error("Refresh failed", e);
    }
  };

  return (
    <header>
      <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
        <Link to="/" style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '15px' }}>
          <div className="logo-box">Δ</div>
          <div>
            <div style={{ fontWeight: 800, fontSize: '18px', letterSpacing: '-0.02em', color: 'var(--text-main)' }}>AegisAgent</div>
          <div className="mono" style={{ fontSize: '9px', color: 'var(--text-dim)', letterSpacing: '0.05em' }}>TACTICAL FORENSIC INTELLIGENCE</div>
          </div>
        </Link>
      </div>
      
      <div className="status-ticker mono">
        <div className="status-item"><span>●</span> SYSTEM: ONLINE</div>
        <div className="status-item"><span>●</span> STREAM: ACTIVE</div>
        <div className="status-item">LAST SCAN: LIVE</div>
      </div>
      
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <button 
          id="wallet-btn" 
          onClick={connectWallet}
          className={wallet ? 'connected' : ''}
        >
          <span className="w-dot"></span>
          <span>{wallet ? `${wallet.slice(0,6)}...${wallet.slice(-4)}` : 'Connect Wallet'}</span>
        </button>
      </div>
    </header>
  );
};


export default Header;
