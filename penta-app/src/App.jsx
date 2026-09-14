import React, { useState, useEffect } from 'react';

export default function App() {
  const [activeTab, setActiveTab] = useState('viewport');
  const [selectedDevice, setSelectedDevice] = useState('pc');
  const [deviceCode, setDeviceCode] = useState('849-210');
  const [targetCode, setTargetCode] = useState('');
  const [connected, setConnected] = useState(false);
  const [licenseKey, setLicenseKey] = useState('');
  const [isPro, setIsPro] = useState(false);
  const [aiGoal, setAiGoal] = useState('');
  const [aiLogs, setAiLogs] = useState('Ready for Google Antigravity directives...');

  const connectToDevice = () => {
    if (!targetCode) return;
    setConnected(true);
  };

  const redeemCoupon = async () => {
    const code = prompt("Enter Promo / Coupon Code (e.g. PENTAFREE or LAUNCH50):");
    if (!code) return;
    try {
      const res = await fetch('http://localhost:5050/api/coupons/redeem', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code })
      });
      const data = await res.json();
      if (data.success) {
        setIsPro(true);
        setLicenseKey(data.license_key);
        alert("🎉 " + data.message + " License: " + data.license_key);
      } else {
        alert("❌ " + data.error);
      }
    } catch (e) {
      alert("Error redeeming coupon: " + e);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', background: '#0d1117' }}>
      {/* Top Header */}
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 20px', borderBottom: '1px solid #30363d', background: '#161b22' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ fontSize: '18px', fontWeight: 'bold', color: '#f0f6fc' }}>⚡ Penta-Assistant</span>
          <span style={{ background: '#238636', color: '#fff', fontSize: '11px', padding: '2px 8px', borderRadius: '12px' }}>Native Client</span>
          {isPro ? (
            <span style={{ background: '#8957e5', color: '#fff', fontSize: '11px', padding: '2px 8px', borderRadius: '12px' }}>PRO ACTIVATED</span>
          ) : (
            <button onClick={redeemCoupon} style={{ background: '#d29922', color: '#0d1117', fontSize: '11px', fontWeight: 'bold', padding: '2px 8px', borderRadius: '12px', border: 'none', cursor: 'pointer' }}>
              🎁 Redeem Promo
            </button>
          )}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span style={{ fontSize: '13px', color: '#8b949e' }}>Your Device Code: <strong style={{ color: '#58a6ff' }}>{deviceCode}</strong></span>
        </div>
      </header>

      {/* Main Container */}
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        {/* Left Sidebar: Device Mesh & Connection */}
        <div style={{ width: '280px', borderRight: '1px solid #30363d', padding: '16px', background: '#0d1117' }}>
          <h3 style={{ fontSize: '13px', color: '#8b949e', textTransform: 'uppercase', marginBottom: '12px' }}>Connect Remote Device</h3>
          <div style={{ display: 'flex', gap: '6px', marginBottom: '16px' }}>
            <input 
              type="text" 
              placeholder="e.g. 912-440" 
              value={targetCode} 
              onChange={e => setTargetCode(e.target.value)}
              style={{ flex: 1, padding: '8px', background: '#161b22', border: '1px solid #30363d', borderRadius: '6px', color: '#fff', fontSize: '13px' }}
            />
            <button onClick={connectToDevice} style={{ background: '#238636', border: 'none', color: '#fff', padding: '8px 12px', borderRadius: '6px', cursor: 'pointer' }}>
              Connect
            </button>
          </div>

          <h3 style={{ fontSize: '13px', color: '#8b949e', textTransform: 'uppercase', marginBottom: '12px' }}>Connected Devices</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <div 
              onClick={() => setSelectedDevice('pc')}
              style={{ padding: '10px', borderRadius: '6px', border: selectedDevice === 'pc' ? '1px solid #58a6ff' : '1px solid #30363d', background: '#161b22', cursor: 'pointer' }}
            >
              <div style={{ fontWeight: 'bold', fontSize: '13px', color: '#f0f6fc' }}>🖥️ Windows PC (Host)</div>
              <div style={{ fontSize: '11px', color: '#7ee787' }}>● Online (1366x768)</div>
            </div>
            <div 
              onClick={() => setSelectedDevice('phone')}
              style={{ padding: '10px', borderRadius: '6px', border: selectedDevice === 'phone' ? '1px solid #58a6ff' : '1px solid #30363d', background: '#161b22', cursor: 'pointer' }}
            >
              <div style={{ fontWeight: 'bold', fontSize: '13px', color: '#f0f6fc' }}>📱 Android Phone (Node)</div>
              <div style={{ fontSize: '11px', color: '#7ee787' }}>● Online (1080x2160)</div>
            </div>
          </div>
        </div>

        {/* Center: Remote Viewport & Control */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', padding: '16px', background: '#090d13' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
            <h2 style={{ fontSize: '15px', color: '#f0f6fc', margin: 0 }}>
              📡 AnyDesk Viewport — {selectedDevice === 'pc' ? 'Windows Desktop' : 'Android Screen'}
            </h2>
            <div style={{ display: 'flex', gap: '6px' }}>
              {selectedDevice === 'pc' ? (
                <>
                  <button style={{ padding: '5px 10px', background: '#21262d', border: '1px solid #30363d', color: '#fff', borderRadius: '4px', cursor: 'pointer', fontSize: '12px' }}>🪟 Win+D</button>
                  <button style={{ padding: '5px 10px', background: '#21262d', border: '1px solid #30363d', color: '#fff', borderRadius: '4px', cursor: 'pointer', fontSize: '12px' }}>🔊 Vol+</button>
                  <button style={{ padding: '5px 10px', background: '#21262d', border: '1px solid #30363d', color: '#fff', borderRadius: '4px', cursor: 'pointer', fontSize: '12px' }}>🔒 Lock</button>
                </>
              ) : (
                <>
                  <button style={{ padding: '5px 10px', background: '#21262d', border: '1px solid #30363d', color: '#fff', borderRadius: '4px', cursor: 'pointer', fontSize: '12px' }}>◀️ Back</button>
                  <button style={{ padding: '5px 10px', background: '#21262d', border: '1px solid #30363d', color: '#fff', borderRadius: '4px', cursor: 'pointer', fontSize: '12px' }}>⏺️ Home</button>
                  <button style={{ padding: '5px 10px', background: '#21262d', border: '1px solid #30363d', color: '#fff', borderRadius: '4px', cursor: 'pointer', fontSize: '12px' }}>🔲 Recents</button>
                </>
              )}
            </div>
          </div>

          {/* Screen Canvas */}
          <div style={{ flex: 1, background: '#000', borderRadius: '8px', border: '1px solid #30363d', display: 'flex', alignItems: 'center', justifyContent: 'center', overflow: 'hidden' }}>
            <img 
              src={selectedDevice === 'pc' ? 'http://localhost:5050/api/pc/screen' : 'http://localhost:5050/api/screenshot'} 
              alt="Remote Viewport" 
              style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain', cursor: 'crosshair' }} 
            />
          </div>

          {/* Antigravity AI Prompt Bar */}
          <div style={{ marginTop: '12px', background: '#161b22', padding: '12px', borderRadius: '8px', border: '1px solid #30363d' }}>
            <div style={{ fontSize: '12px', color: '#58a6ff', fontWeight: 'bold', marginBottom: '6px' }}>
              🤖 Google Antigravity Co-Pilot ({selectedDevice === 'pc' ? 'PC Agent' : 'Mobile Agent'})
            </div>
            <div style={{ display: 'flex', gap: '8px' }}>
              <input 
                type="text" 
                placeholder={`Give an autonomous instruction to ${selectedDevice === 'pc' ? 'Windows' : 'Android'}...`}
                value={aiGoal}
                onChange={e => setAiGoal(e.target.value)}
                style={{ flex: 1, padding: '8px 12px', background: '#0d1117', border: '1px solid #30363d', borderRadius: '6px', color: '#fff', fontSize: '13px' }}
              />
              <button style={{ background: '#238636', border: 'none', color: '#fff', padding: '8px 16px', borderRadius: '6px', fontWeight: 'bold', cursor: 'pointer' }}>
                🚀 Run AI
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
