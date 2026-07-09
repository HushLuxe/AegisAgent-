import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

const Landing = () => {
  const [liveStats, setLiveStats] = useState({ tokens: '16', avgSai: '—', status: 'ONLINE' });

  useEffect(() => {
    fetch('/api/status?t=' + Date.now())
      .then(r => r.json())
      .then(data => {
        setLiveStats({
          tokens: String(data.tokens_monitored || 16),
          avgSai: data.avg_sai ? data.avg_sai.toFixed(1) : '—',
          status: data.status === 'operational' ? 'ONLINE' : 'DEGRADED',
        });
      })
      .catch(() => {});
  }, []);

  return (
    <>
      <header>
        <div className="logo-area">
          <div className="logo-box">Δ</div>
          <div>
            <div style={{ fontWeight: 800, fontSize: '16px', letterSpacing: '-0.02em', color: 'var(--text-main)' }}>AegisAgent</div>
            <div className="mono" style={{ fontSize: '9px', color: 'var(--text-dim)' }}>TACTICAL FORENSIC INTELLIGENCE</div>
          </div>
        </div>
        <div className="status-ticker mono">
          <div className="status-item"><span>●</span> SYSTEM: {liveStats.status}</div>
          <div className="status-item"><span>●</span> ANALYSIS: REAL-TIME</div>
          <div className="status-item"><span>●</span> SOSOVALUE: {liveStats.tokens} ASSETS</div>
        </div>
      </header>

      <div className="hero">
        <div className="hero-left">
          <div className="eyebrow">Autonomous Forensic Intelligence · Powered by SoSoValue API</div>
          <h1 className="hero-title">
            <span className="accent">AEGIS</span><br />
            <span className="dim">FORENSIC</span><br />
            AGENT
          </h1>
          <p className="hero-desc">
            AegisAgent is an autonomous AI agent conducting continuous forensic surveillance powered by SoSoValue data infrastructure.
            Every 60 minutes, the engine ingests market data, news sentiment, ETF flows, macro events, and BTC treasuries — computes <strong>100+ proprietary metrics</strong> —
            liquidity depth, flow quality, holder concentration, and structural momentum — condensed into a single
            <strong> Sovereign Anomaly Index (SAI)</strong> per token.
          </p>
          <div className="cta-group">
            <Link to="/dashboard" className="btn-primary">Access Intelligence Feed →</Link>
          </div>
        </div>

        <div className="hero-right">
          <div className="terminal">
            <div className="terminal-bar">
              <div className="t-dot" style={{ background: '#ff3e3e' }}></div>
              <div className="t-dot" style={{ background: '#ffb800' }}></div>
              <div className="t-dot" style={{ background: '#00E5FF' }}></div>
              <span className="t-label">aegis-agent · forensic_engine_v5.1</span>
            </div>
            <div className="t-line"><span className="cmd">$</span> <span className="out">aegis run</span> <span className="val">forensic_engine_v5.1</span></div>
                <div className="t-line"><span className="out">→ Loading watchlist... {liveStats.tokens} assets · SoSoValue API</span></div>
                <div className="t-line"><span className="out">→ Fetching market data [SoSoValue / DexScreener]</span></div>
                <div className="t-line"><span className="out">→ Computing metrics: SAI / TFA / LFI / LCR / BPI</span></div>
                <div className="t-line"><span className="out">→ Forensic LLM synthesis... report generated</span></div>
                <div className="t-line"><span className="out">→ Pushing memory.json to Sovereign KV</span></div>
            <div className="t-line"><span className="out">→ Status:</span> <span className="val">{liveStats.status} ✓</span></div>
            <div className="t-line"><span className="cmd">$</span> <span className="cursor"></span></div>
          </div>
          <div className="stats-strip">
            <div className="stat-cell"><div className="stat-val">{liveStats.tokens}</div><div className="stat-key">Assets</div></div>
              <div className="stat-cell">
                <div className="stat-val">100+</div>
                <div className="stat-key">Metrics</div>
              </div>
            <div className="stat-cell"><div className="stat-val">1H</div><div className="stat-key">Cycle</div></div>
            <div className="stat-cell"><div className="stat-val">7</div><div className="stat-key">SoSoValue Modules</div></div>
          </div>
        </div>
      </div>

      <section id="metrics" style={{ padding: '80px 64px', borderTop: '1px solid var(--border)' }}>
        <div className="section-label" style={{ fontSize: '10px', fontWeight: 700, letterSpacing: '0.15em', textTransform: 'uppercase', color: 'var(--accent)', marginBottom: '48px', display: 'flex', alignItems: 'center', gap: '12px' }}>
          // Core Forensic Metrics
          <span style={{ flex: 1, height: '1px', background: 'var(--border)' }}></span>
        </div>
        <div className="metrics-grid">
          <div className="m-card">
            <div className="metric-name" style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '20px', fontWeight: 700, color: 'var(--accent)' }}>SAI</div>
            <div className="metric-full" style={{ fontWeight: 700, fontSize: '13px', marginBottom: '8px' }}>Sovereign Anomaly Index</div>
             <div className="metric-desc" style={{ fontSize: '11px', color: 'var(--text-dim)', lineHeight: 1.6 }}>Weighted composite score (0–10) integrating liquidity depth, directional flow, holder concentration, and structural momentum. The primary risk-adjusted output of each forensic cycle.</div>
          </div>
          <div className="m-card">
            <div className="metric-name" style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '20px', fontWeight: 700, color: 'var(--accent)' }}>TFA</div>
            <div className="metric-full" style={{ fontWeight: 700, fontSize: '13px', marginBottom: '8px' }}>Tactical Flow Analysis</div>
            <div className="metric-desc" style={{ fontSize: '11px', color: 'var(--text-dim)', lineHeight: 1.6 }}>Net buy/sell pressure over a 24h rolling window, normalised against on-chain volume. Distinguishes programmatic accumulation from retail-driven distribution at the transaction level.</div>
          </div>
          <div className="m-card">
            <div className="metric-name" style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '20px', fontWeight: 700, color: 'var(--accent)' }}>LFI</div>
            <div className="metric-full" style={{ fontWeight: 700, fontSize: '13px', marginBottom: '8px' }}>Liquidity Fragility Index</div>
            <div className="metric-desc" style={{ fontSize: '11px', color: 'var(--text-dim)', lineHeight: 1.6 }}>Simulated price impact of a top-wallet exit event, derived from live liquidity pool depth. Quantifies systemic fragility with a threshold-based alert at LFI &gt; 0.6.</div>
          </div>
          <div className="m-card">
            <div className="metric-name" style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '20px', fontWeight: 700, color: 'var(--accent)' }}>WCC</div>
            <div className="metric-full" style={{ fontWeight: 700, fontSize: '13px', marginBottom: '8px' }}>Whale Concentration Coefficient</div>
            <div className="metric-desc" style={{ fontSize: '11px', color: 'var(--text-dim)', lineHeight: 1.6 }}>Gini-derived supply concentration ratio across the top 20 on-chain wallets. Elevated WCC (&gt;15%) correlates strongly with coordination risk and asymmetric sell pressure.</div>
          </div>
        </div>
      </section>

      <div style={{ padding: '80px 64px', borderTop: '1px solid var(--border)', background: 'var(--surface)' }}>
        <div style={{ fontSize: '10px', fontWeight: 700, letterSpacing: '0.15em', textTransform: 'uppercase', color: 'var(--accent)', marginBottom: '48px', display: 'flex', alignItems: 'center', gap: '12px' }}>
          // Autonomous Intelligence Pipeline
          <span style={{ flex: 1, height: '1px', background: 'var(--border)' }}></span>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1px', background: 'var(--border)', border: '1px solid var(--border)' }}>
          <div style={{ background: 'var(--bg)', padding: '40px' }}>
            <div className="pw-chip">Per-Token Forensic Intelligence</div>
            <h2 style={{ fontSize: 'clamp(28px, 3.5vw, 48px)', fontWeight: 800, lineHeight: 0.9, letterSpacing: '-0.04em', textTransform: 'uppercase', marginBottom: '20px' }}>
              TOKEN<br/>DASHBOARD
            </h2>
            <p style={{ fontSize: '14px', color: 'var(--text-dim)', lineHeight: 1.7, marginBottom: '28px' }}>
              Full forensic depth — 100+ computed metrics, LFI simulation, whale mapping, bull flag detection, and an AI-powered risk narrative. All data sourced from SoSoValue API and on-chain feeds.
            </p>
            <Link to="/dashboard" className="btn-primary" style={{ padding: '14px 32px' }}>Open Intelligence Feed →</Link>
          </div>
          <div style={{ background: 'var(--bg)', padding: '40px', borderLeft: '1px solid var(--border)' }}>
            <div className="pw-chip" style={{ borderColor: 'rgba(255,140,0,0.3)', background: 'rgba(255,140,0,0.06)', color: 'var(--amber)' }}>AI-Powered Intelligence</div>
            <h2 style={{ fontSize: 'clamp(28px, 3.5vw, 48px)', fontWeight: 800, lineHeight: 0.9, letterSpacing: '-0.04em', textTransform: 'uppercase', marginBottom: '20px' }}>
              GLOBAL<br/>SYNTHESIS
            </h2>
            <p style={{ fontSize: '14px', color: 'var(--text-dim)', lineHeight: 1.7, marginBottom: '28px' }}>
              Every 60 minutes, AegisAgent autonomously ingests live data from SoSoValue API — market snapshots, news, ETF flows, macro events, BTC treasuries — and invokes Venice AI to generate a structured forensic narrative with no human input.
            </p>
          </div>
        </div>
      </div>

      <footer style={{ padding: '24px 64px', borderTop: '1px solid var(--border)', background: 'var(--surface)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '10px', color: 'var(--text-ghost)', fontFamily: "'JetBrains Mono', monospace" }}>
        <div>AegisAgent · <span style={{ color: 'var(--accent)' }}>SOVEREIGN FORENSIC INTELLIGENCE</span> · Powered by SoSoValue</div>
        <div>ForensicEngineV5 · Venice AI</div>
        <div>© 2026 · <span style={{ color: 'var(--accent)' }}>AUTONOMOUS</span></div>
      </footer>
    </>
  );
};

export default Landing;
