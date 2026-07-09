import React, { useState, useEffect } from 'react';
import { ethers } from 'ethers';

const AEGIS_CONTRACT_ADDRESS = '0x0000000000000000000000000000000000000000';

// ── helpers ───────────────────────────────────────────────────────────────────
const fmt = (n, digits = 2) => (typeof n === 'number' ? n.toFixed(digits) : '—');
const fmtPrice = (p) => {
  if (!p) return '—';
  if (p >= 1) return `$${p.toFixed(2)}`;
  if (p >= 0.01) return `$${p.toFixed(4)}`;
  return `$${p.toExponential(3)}`;
};
const fmtK = (n) => {
  if (!n) return '—';
  if (n >= 1e6) return `$${(n / 1e6).toFixed(2)}M`;
  if (n >= 1e3) return `$${(n / 1e3).toFixed(1)}K`;
  return `$${n.toFixed(0)}`;
};

const phaseColor = (phase = '') => {
  if (phase.includes('ACCUM')) return 'var(--accent)';
  if (phase.includes('DIST')) return '#ff4466';
  return 'var(--text-dim)';
};

const getSAIClass = (sai) => {
  if (sai >= 8) return 'sai-high'; // Example class for high SAI
  if (sai >= 5) return 'sai-medium'; // Example class for medium SAI
  return 'sai-low'; // Example class for low SAI
};

// ── Dashboard ─────────────────────────────────────────────────────────────────
const Dashboard = () => {
  const [tokens, setTokens] = useState([]);
  const [selected, setSelected] = useState(null);
  const [isUnlocked, setIsUnlocked] = useState(false);
  const [status, setStatus] = useState('');
  const [wallet, setWallet] = useState(null);
  const [updatedAt, setUpdatedAt] = useState('');
  const [sosoData, setSosoData] = useState(null);
  const [loadingState, setLoadingState] = useState('loading'); // 'loading' | 'loaded' | 'error'

  // Fetch forensics from Vercel API on mount and every 2 minutes
  useEffect(() => {
    const load = () => {
      setLoadingState('loading');

      // Try loading SoSoValue data from memory.json as supplement
      fetch('/memory.json?t=' + Date.now())
        .then(res => res.json())
        .then(mem => {
          if (mem.sosovalue) setSosoData(mem.sosovalue);
        })
        .catch(() => {});

      fetch('/api/forensics?t=' + Date.now())
        .then(async r => {
          if (!r.ok) {
            const errBody = await r.text();
            console.error(`API Error (${r.status}):`, errBody);
            throw new Error(`API Error ${r.status}`);
          }
          return r.json();
        })
        .then(data => {
          console.log("Aegis API Response:", data);
          const list = Object.values(data.tokens || {});
          setTokens(list);
          if (data.api_source) {
            setStatus(`Connected (${data.api_source})`);
          }
          setUpdatedAt(data.timestamp ? new Date(data.timestamp).toLocaleTimeString() : '');
          if (!selected && list.length) setSelected(list[0]);
          setLoadingState('loaded');
        })
        .catch(() => {
          console.warn('Aegis API not yet online. Fallback to cached state.');
          fetch('/memory.json?t=' + Date.now())
            .then(res => res.json())
            .then(fallbackData => {
              if (fallbackData.tokens) {
                setTokens(fallbackData.tokens);
                setUpdatedAt(fallbackData.updated_at ? new Date(fallbackData.updated_at).toLocaleTimeString() : '');
                if (!selected && fallbackData.tokens.length) setSelected(fallbackData.tokens[0]);
                setLoadingState('loaded');
              } else {
                setLoadingState('error');
              }
              if (fallbackData.sosovalue) {
                setSosoData(fallbackData.sosovalue);
              }
            })
            .catch(() => setLoadingState('error'));
        });
    };
    load();
    const iv = setInterval(load, 120_000);
    return () => clearInterval(iv);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Auto-unlock for SoSoValue Buildathon demo
  useEffect(() => {
    setIsUnlocked(true);
  }, []);

  const [isLoading, setIsLoading] = useState(false);
  const [bailoutStatus, setBailoutStatus] = useState('');

  const executeBailout = async (token) => {
    if (!wallet) return;
    setBailoutStatus('🔍 Fetching Uniswap route via Trading API...');
    try {
      const res = await fetch(`/api/uniswap?token=${token.address}&wallet=${wallet}&amount=1000000000000000000`);
      const data = await res.json();
      if (data.error) throw new Error(data.error);

      // New schema: { swap: { to, data, value, chainId }, estimatedOutput }
      const swapTx = data.swap;
      if (!swapTx?.to || !swapTx?.data) throw new Error('No routing path found — insufficient liquidity?');

      const estimatedUsdc = data.estimatedOutput
        ? `~${(parseInt(data.estimatedOutput) / 1e6).toFixed(4)} USDC`
        : '';

      setBailoutStatus(`✅ Route found ${estimatedUsdc}. Signing in wallet...`);
      const provider = new ethers.providers.Web3Provider(window.ethereum);
      const signer = provider.getSigner();

      const tx = await signer.sendTransaction({
        to: swapTx.to,
        data: swapTx.data,
        value: swapTx.value || '0x00'
      });

      setBailoutStatus(`✓ Emergency Bailout Sent! Tx: ${tx.hash.slice(0, 18)}...`);
    } catch (e) {
      console.error(e);
      setBailoutStatus(`❌ Swap Failed: ${e.message}`);
    }
  };

  const connectWallet = async () => {
    console.log("🛠️ Attempting to connect wallet...");
    if (!window.ethereum) {
      console.error("❌ No window.ethereum found");
      alert('MetaMask or a Web3 wallet was not found. Please install it to continue.');
      return;
    }
    
    setIsLoading(true);
    setStatus('Connecting to wallet...');
    
    try {
      // Direct request to avoid any provider wrapper issues
      const accs = await window.ethereum.request({ method: 'eth_requestAccounts' });
      console.log("✅ Wallet connected:", accs[0]);
      setWallet(accs[0]);
      setStatus('Wallet connected.');
      checkSubscription(accs[0], new ethers.providers.Web3Provider(window.ethereum));
    } catch (e) { 
      console.error('❌ Wallet connect error:', e); 
      if (e.code === -32002) {
        alert('Connection request already pending in MetaMask. Please check your wallet extension.');
      } else {
        setStatus('Connection failed.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Dashboard is always accessible for SoSoValue Buildathon
  const handleUnlock = () => {
    setIsUnlocked(true);
  };

  const t = selected;
  const fhsValue = t?.fhs ?? t?.sai ?? 0;
  const nbpValue = t?.nbp ?? t?.tfa ?? null;
  const icrValue = t?.icr ?? t?.ips_50k ?? t?.ips_10k ?? null;
  const lfiValue = t?.lfi ?? 0;

  return (
    <div className="main-grid">
      {/* ── Top Bar Logic (Connect Wallet Button) ── */}
      <div style={{ position: 'fixed', top: '15px', right: '15px', zIndex: 1000, display: 'flex', gap: '8px' }}>
        <button 
          className="btn-secondary"
          style={{ padding: '8px 12px', fontSize: '11px', borderRadius: '4px', cursor: 'pointer' }}
          title="Force-rebuild backend cache"
          onClick={async () => {
            try {
              setIsLoading(true);
              await fetch('/api/forensics?refresh=true');
              window.location.reload();
            } catch(e) {
              console.error(e);
              setIsLoading(false);
            }
          }}
        >
          REFRESH
        </button>

        <button 
          onClick={connectWallet}
          className="btn-primary" 
          disabled={isLoading}
          style={{ 
            padding: '8px 16px', 
            fontSize: '11px', 
            borderRadius: '4px', 
            background: wallet ? 'rgba(0,229,255,0.1)' : 'var(--accent)', 
            color: wallet ? 'var(--accent)' : '#000',
            opacity: isLoading ? 0.7 : 1,
            cursor: isLoading ? 'not-allowed' : 'pointer'
          }}
        >
          {isLoading ? 'CONNECTING...' : wallet ? `${wallet.slice(0, 6)}...${wallet.slice(-4)}` : 'CONNECT WALLET'}
        </button>
      </div>

      {/* ── Sidebar ── */}
      <aside className="sidebar">
        <div className="sidebar-label">
          <span>Forensic Assets</span>
          <span className="mono" style={{ color: 'var(--accent)' }}>{tokens.length}</span>
        </div>
        {updatedAt && (
          <div style={{ fontSize: '10px', color: 'var(--text-ghost)', padding: '4px 16px', marginBottom: '4px' }}>
            Updated {updatedAt}
          </div>
        )}
        <div className="token-list">
          {tokens.length === 0 && (
            <div style={{ padding: '20px 16px', color: 'var(--text-ghost)', fontSize: '11px', textAlign: 'center' }}>
              AUTONOMOUS SURVEILLANCE ACTIVE<br/>
              Awaiting next forensic cycle...
            </div>
          )}
          {tokens.map(tok => (
            <div
              key={tok.address || tok.symbol}
              className={`token-item ${selected?.symbol === tok.symbol ? 'active' : ''}`}
              onClick={() => setSelected(tok)}
            >
              <div>
                <div className="token-name">{tok.symbol}</div>
                <div className="token-meta" style={{ color: phaseColor(tok.phase), fontSize: '10px' }}>
                  {tok.phase || tok.chain?.toUpperCase() || 'CELO'}
                </div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div className="token-score" style={{ color: (tok.fhs ?? tok.sai ?? 0) >= 8 ? 'var(--accent)' : 'var(--text-main)' }}>
                  {fmt((tok.fhs ?? tok.sai ?? 0), 1)}
                </div>
                <div className="token-rsi">RSI: {fmt(tok.rsi_1h, 0)}</div>
              </div>
            </div>
          ))}
        </div>
      </aside>

      {/* ── Main Content ── */}
      <main className="content-area" style={{ position: 'relative' }}>
        {/* Loading skeleton */}
        {loadingState === 'loading' && (
          <div className="paywall-overlay">
            <div className="paywall-card">
              <div className="pw-chip">Loading forensic data...</div>
              <div className="skel skel-line" style={{ width: '60%', height: '16px', margin: '16px auto' }}></div>
              <div className="skel skel-line" style={{ width: '80%', height: '12px', margin: '8px auto' }}></div>
              <div className="skel skel-line" style={{ width: '40%', height: '12px', margin: '8px auto' }}></div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '8px', marginTop: '20px' }}>
                {[1,2,3].map(i => <div key={i} className="skel skel-card"></div>)}
              </div>
            </div>
          </div>
        )}

        {/* Error state */}
        {loadingState === 'error' && tokens.length === 0 && (
          <div className="paywall-overlay">
            <div className="paywall-card">
              <div className="pw-chip" style={{ color: '#ff4466' }}>Connection Failed</div>
              <div style={{ fontSize: '24px', marginBottom: '12px' }}>⚠️</div>
              <h2>Unable to Load Data</h2>
              <p style={{ color: 'var(--text-dim)', fontSize: '12px', lineHeight: 1.6 }}>
                The forensic engine is not responding. This may be because:
              </p>
              <ul style={{ color: 'var(--text-ghost)', fontSize: '11px', textAlign: 'left', margin: '12px 0', paddingLeft: '20px', lineHeight: 2 }}>
                <li>No API keys are configured in the environment</li>
                <li>The backend pipeline has not completed a cycle yet</li>
                <li>The Vercel deployment is cold-starting</li>
              </ul>
              <button
                className="btn-unlock-pw"
                onClick={() => window.location.reload()}
                style={{ marginTop: '12px' }}
              >
                Retry Connection
              </button>
            </div>
          </div>
        )}

        {t && (
          <div>
            {/* Token Header */}
            <div className="intel-header">
              <div>
                <div className="intel-title">
                  <h1 style={{ fontSize: '48px', fontWeight: 800 }}>{t.symbol}</h1>
                </div>
                <div className="addr-pill" title={t.address}>
                  {t.address ? `${t.address.slice(0, 6)}…${t.address.slice(-4)}` : 'CELO'}
                </div>
                {t.bailout_recommended && (
                  <div style={{ marginTop: '12px' }}>
                    <button 
                      onClick={() => executeBailout(t)} 
                      style={{ background: '#ff4466', color: '#fff', padding: '8px 16px', borderRadius: '4px', fontWeight: 'bold', fontSize: '11px', border: 'none', cursor: 'pointer', letterSpacing: '0.5px' }}
                    >
                      🚨 EXECUTE AUTONOMOUS BAILOUT
                    </button>
                    {bailoutStatus && <div style={{ fontSize: '10px', color: 'var(--text-dim)', marginTop: '8px' }}>{bailoutStatus}</div>}
                  </div>
                )}
              </div>
              <div className="fhs-radar">
                <div style={{ fontSize: '10px', color: 'var(--text-ghost)', marginBottom: '4px' }}>FHS</div>
                <div className="fhs-val">{fmt(fhsValue, 1)}</div>
                <div style={{ fontSize: '10px', color: 'var(--text-ghost)' }}>{t.fhs_label || ''}</div>
              </div>
            </div>

            {/* Price row */}
            <div style={{ display: 'flex', gap: '16px', marginBottom: '24px', flexWrap: 'wrap' }}>
              {[
                ['Price', fmtPrice(t.price_usd)],
                ['24h Δ', t.price_change_24h != null ? `${t.price_change_24h > 0 ? '+' : ''}${fmt(t.price_change_24h)}%` : '—'],
                ['Vol 24h', fmtK(t.volume_24h)],
                ['Liq', fmtK(t.liquidity_usd)],
                ['MCap', fmtK(t.mcap)],
              ].map(([label, val]) => (
                <div key={label} style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: '6px', padding: '10px 14px', minWidth: '90px' }}>
                  <div style={{ fontSize: '10px', color: 'var(--text-ghost)', marginBottom: '4px' }}>{label}</div>
                  <div className="mono" style={{ fontSize: '13px', color: label === '24h Δ' && t.price_change_24h < 0 ? '#ff4466' : 'var(--text-main)' }}>{val}</div>
                </div>
              ))}
            </div>

            {/* Core Metrics */}
            <div className="section-header">// Core Metrics</div>
            <div className="metrics-grid">
              <div className="m-card">
                <div className="m-label">Net Buy Pressure</div>
                <div className="m-val" style={{ color: (nbpValue ?? 0) > 0 ? 'var(--accent)' : '#ff4466' }}>
                  {nbpValue != null ? `${nbpValue > 0 ? '+' : ''}${fmt(nbpValue, 1)}%` : '—'}
                </div>
              </div>
              <div className="m-card">
                <div className="m-label">LFI Fragility</div>
                <div className="m-val" style={{ color: lfiValue > 0.5 ? '#ff4466' : 'var(--accent)' }}>
                  {(lfiValue * 100).toFixed(1)}%
                </div>
              </div>
              <div className="m-card">
                <div className="m-label">Impact Crash Risk</div>
                <div className="m-val" style={{ color: (icrValue ?? 0) > 1.0 ? '#ff4466' : 'var(--accent)' }}>
                  {icrValue != null ? fmt(icrValue) : '—'}
                </div>
              </div>
              <div className="m-card">
                <div className="m-label">Liquidity Cover</div>
                <div className="m-val">{fmt(t.lcr)}%</div>
              </div>
              <div className="m-card">
                <div className="m-label">Whale Concentration</div>
                <div className="m-val" style={{ color: t.wcc > 10 ? '#ffb800' : 'var(--text-main)' }}>
                  {fmt(t.wcc)}%
                </div>
              </div>
              <div className="m-card">
                <div className="m-label">Bull Flag</div>
                <div className="m-val" style={{ color: t.bull_flag ? 'var(--accent)' : 'var(--text-ghost)' }}>
                  {t.bull_flag ? `✓ Class ${t.bf_class}` : 'None'}
                </div>
              </div>
              <div className="m-card">
                <div className="m-label">SAI Index</div>
                <div className={`m-val ${getSAIClass(t.sai)}`}>
                  {t.sai?.toFixed(1) || '0.0'}
                </div>
              </div>
              <div className="m-card">
                <div className="m-label">BPI Score</div>
                <div className="m-val">{fmt(t.bpi)}</div>
              </div>
              <div className="m-card">
                <div className="m-label">Top 5 Holders</div>
                <div className="m-val">{fmt(t.top5_pct)}%</div>
              </div>
              <div className="m-card">
                <div className="m-label">RSI 1H</div>
                <div className="m-val">{fmt(t.rsi_1h, 0)}</div>
              </div>
            </div>

            {/* Alerts */}
            {t.alerts && t.alerts.length > 0 && (
              <>
                <div className="section-header">// Alerts</div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '24px' }}>
                  {t.alerts.map((a, i) => (
                    <div key={i} style={{
                      padding: '10px 14px',
                      borderLeft: `3px solid ${a.severity === 'critical' ? '#ff4466' : '#ffb800'}`,
                      background: a.severity === 'critical' ? 'rgba(255,68,102,0.07)' : 'rgba(255,184,0,0.07)',
                      fontSize: '12px',
                      color: a.severity === 'critical' ? '#ff7799' : '#ffd066',
                      borderRadius: '0 4px 4px 0'
                    }}>
                      {a.message}
                    </div>
                  ))}
                </div>
              </>
            )}

            {/* AI Narrative */}
            <div className="section-header">// Venice AI Assessment</div>
            <div style={{ background: 'var(--surface)', borderLeft: '2px solid var(--accent)', padding: '20px 24px', lineHeight: 1.7, fontSize: '13px', color: 'var(--text-dim)', marginBottom: '24px' }}>
              <div style={{ marginBottom: '8px' }}>{t.narrative_phase || '—'}</div>
              <div style={{ marginBottom: '8px' }}>{t.narrative_insight || '—'}</div>
              <div style={{ color: 'var(--text-ghost)' }}>{t.narrative_structure || '—'}</div>
            </div>

            {/* SoSoValue Intelligence Panel */}
            {sosoData && (
              <>
                <div className="section-header">// SoSoValue Intelligence</div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px', marginBottom: '24px' }}>
                  {/* News Sentiment */}
                  {sosoData.news_sentiment && (
                    <div style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: '6px', padding: '14px' }}>
                      <div style={{ fontSize: '10px', color: 'var(--text-ghost)', textTransform: 'uppercase', marginBottom: '8px' }}>News Sentiment</div>
                      <div style={{ fontSize: '18px', fontWeight: 700, color: sosoData.news_sentiment.label === 'bullish' ? 'var(--accent)' : sosoData.news_sentiment.label === 'bearish' ? '#ff4466' : '#ffb800' }}>
                        {(sosoData.news_sentiment.label || 'neutral').toUpperCase()}
                      </div>
                      <div style={{ fontSize: '11px', color: 'var(--text-dim)', marginTop: '4px' }}>
                        {sosoData.news_sentiment.positive || 0} pos / {sosoData.news_sentiment.negative || 0} neg of {sosoData.news_sentiment.total || 0}
                      </div>
                    </div>
                  )}

                  {/* ETF Flows */}
                  {sosoData.etf_signal && (
                    <div style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: '6px', padding: '14px' }}>
                      <div style={{ fontSize: '10px', color: 'var(--text-ghost)', textTransform: 'uppercase', marginBottom: '8px' }}>ETF Flows</div>
                      <div style={{ fontSize: '18px', fontWeight: 700, color: (sosoData.etf_signal.signal || '').includes('inflow') ? 'var(--accent)' : '#ff4466' }}>
                        {(sosoData.etf_signal.signal || 'neutral').replace(/_/g, ' ').toUpperCase()}
                      </div>
                      <div style={{ fontSize: '11px', color: 'var(--text-dim)', marginTop: '4px' }}>
                        {fmtK(sosoData.etf_signal.total_flow || 0)}
                      </div>
                    </div>
                  )}

                  {/* Macro Risk */}
                  {sosoData.macro_impact && (
                    <div style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: '6px', padding: '14px' }}>
                      <div style={{ fontSize: '10px', color: 'var(--text-ghost)', textTransform: 'uppercase', marginBottom: '8px' }}>Macro Risk</div>
                      <div style={{ fontSize: '18px', fontWeight: 700, color: sosoData.macro_impact.risk_level === 'high' ? '#ff4466' : sosoData.macro_impact.risk_level === 'medium' ? '#ffb800' : 'var(--accent)' }}>
                        {(sosoData.macro_impact.risk_level || 'low').toUpperCase()}
                      </div>
                      <div style={{ fontSize: '11px', color: 'var(--text-dim)', marginTop: '4px' }}>
                        {sosoData.macro_impact.high_impact_count || 0} high-impact events
                      </div>
                    </div>
                  )}

                  {/* BTC Treasuries */}
                  {sosoData.treasury_signal && (
                    <div style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: '6px', padding: '14px' }}>
                      <div style={{ fontSize: '10px', color: 'var(--text-ghost)', textTransform: 'uppercase', marginBottom: '8px' }}>BTC Treasuries</div>
                      <div style={{ fontSize: '18px', fontWeight: 700, color: sosoData.treasury_signal.sentiment === 'bullish' ? 'var(--accent)' : '#ffb800' }}>
                        {(sosoData.treasury_signal.sentiment || 'neutral').toUpperCase()}
                      </div>
                      <div style={{ fontSize: '11px', color: 'var(--text-dim)', marginTop: '4px' }}>
                        {sosoData.treasury_signal.company_count || 0} companies · {sosoData.treasury_signal.recent_buyers || 0} buying
                      </div>
                    </div>
                  )}
                </div>

                {/* SoSoValue Indices */}
                {sosoData.indices && sosoData.indices.length > 0 && (
                  <div style={{ display: 'flex', gap: '12px', marginBottom: '24px', flexWrap: 'wrap' }}>
                    {sosoData.indices.map((idx, i) => (
                      <div key={i} style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: '6px', padding: '10px 14px', minWidth: '120px' }}>
                        <div style={{ fontSize: '10px', color: 'var(--text-ghost)', marginBottom: '4px' }}>{idx.ticker || idx.name || 'INDEX'}</div>
                        <div className="mono" style={{ fontSize: '13px' }}>{fmtPrice(idx.price)}</div>
                        <div className="mono" style={{ fontSize: '11px', color: (idx.change_24h || 0) >= 0 ? 'var(--accent)' : '#ff4466' }}>
                          {idx.change_24h > 0 ? '+' : ''}{fmt(idx.change_24h)}%
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </main>

      {/* ── Telemetry ── */}
      <aside className="telemetry" style={{ borderLeft: '1px solid var(--border)', background: 'rgba(10,10,12,0.5)', padding: '20px' }}>
        <div className="t-section-title" style={{ color: 'var(--amber)', fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', marginBottom: '15px' }}>
          Autonomous Signal Watch
        </div>
        {t?.alerts && t.alerts.length > 0 ? t.alerts.map((a, i) => (
          <div key={i} style={{
            padding: '10px',
            background: a.severity === 'critical' ? 'rgba(255,68,102,0.1)' : 'rgba(255,184,0,0.1)',
            borderLeft: `3px solid ${a.severity === 'critical' ? '#ff4466' : '#ffb800'}`,
            color: a.severity === 'critical' ? '#ff9999' : '#ffdd88',
            fontSize: '11px',
            marginBottom: '8px',
            borderRadius: '0 4px 4px 0'
          }}>
            {a.code}
          </div>
        )) : (
          <div style={{ padding: '10px', background: 'rgba(252,255,82,0.07)', borderLeft: '3px solid var(--accent)', color: 'var(--text-ghost)', fontSize: '11px' }}>
            No active alerts
          </div>
        )}


        {t?.bull_flag && (
          <div style={{ marginTop: '16px' }}>
            <div style={{ fontSize: '10px', color: 'var(--text-ghost)', marginBottom: '8px', textTransform: 'uppercase' }}>Bull Flag</div>
            <div style={{ padding: '10px', background: 'rgba(252,255,82,0.07)', borderLeft: '3px solid var(--accent)', color: 'var(--accent)', fontSize: '11px' }}>
              🚩 Class {t.bf_class} · Retrace {fmt(t.bf_retracement)}%
            </div>
            {t.fib_target > 0 && (
              <div style={{ padding: '8px 10px', background: 'var(--surface)', fontSize: '11px', color: 'var(--text-dim)', marginTop: '4px' }}>
                Target: {fmtPrice(t.fib_target)} (+{fmt(t.fib_upside_pct)}%)
              </div>
            )}
          </div>
        )}

        <div style={{ marginTop: '24px', borderTop: '1px solid var(--border)', paddingTop: '16px' }}>
          <div style={{ fontSize: '10px', color: 'var(--text-ghost)', textTransform: 'uppercase', marginBottom: '8px' }}>Phase</div>
          <div style={{ fontSize: '13px', fontWeight: 700, color: phaseColor(t?.phase) }}>
            {t?.phase || '—'}
          </div>
          <div style={{ fontSize: '11px', color: 'var(--text-ghost)', marginTop: '4px' }}>
            NBP: {nbpValue != null ? `${nbpValue > 0 ? '+' : ''}${fmt(nbpValue, 1)}%` : '—'}
          </div>
        </div>
      </aside>
    </div>
  );
};

export default Dashboard;
