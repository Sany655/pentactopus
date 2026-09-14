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
  const [aiLogs, setAiLogs] = useState('Ready for Pentatopus directives...');

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
        alert("License Activated: " + data.license_key);
      } else {
        alert("Error: " + data.error);
      }
    } catch (e) {
      alert("Error redeeming coupon: " + e);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', background: '#09090b', color: '#f4f4f5', fontFamily: 'Inter, system-ui, sans-serif' }}>
      {/* Top Header */}
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 20px', borderBottom: '1px solid #27272a', background: '#121215' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ fontSize: '16px', fontWeight: '600', letterSpacing: '-0.02em', color: '#f4f4f5' }}>Pentatopus</span>
          <span style={{ background: '#27272a', color: '#a1a1aa', fontSize: '11px', padding: '2px 8px', borderRadius: '4px', border: '1px solid #3f3f46' }}>Native Client</span>
          {isPro ? (
            <span style={{ background: 'rgba(59,130,246,0.15)', color: '#60a5fa', fontSize: '11px', padding: '2px 8px', borderRadius: '4px', border: '1px solid rgba(59,130,246,0.3)' }}>PRO ACTIVATED</span>
          ) : (
            <button onClick={redeemCoupon} style={{ background: '#2563eb', color: '#fff', fontSize: '11px', fontWeight: '500', padding: '3px 10px', borderRadius: '4px', border: 'none', cursor: 'pointer' }}>
              Redeem Code
            </button>
          )}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span style={{ fontSize: '13px', color: '#71717a' }}>Device Identifier: <strong style={{ color: '#e4e4e7', fontFamily: 'monospace' }}>{deviceCode}</strong></span>
        </div>
      </header>

      {/* Main Container */}
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        {/* Left Sidebar: Device Mesh & Connection */}
        <div style={{ width: '280px', borderRight: '1px solid #27272a', padding: '16px', background: '#0e0e11' }}>
          <h3 style={{ fontSize: '11px', fontWeight: '600', color: '#71717a', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '12px' }}>Connect Remote Device</h3>
          <div style={{ display: 'flex', gap: '6px', marginBottom: '16px' }}>
            <input 
              type="text" 
              placeholder="e.g. 912-440" 
              value={targetCode} 
              onChange={e => setTargetCode(e.target.value)}
              style={{ flex: 1, padding: '8px', background: '#18181b', border: '1px solid #27272a', borderRadius: '4px', color: '#fff', fontSize: '13px' }}
            />
            <button onClick={connectToDevice} style={{ background: '#2563eb', border: 'none', color: '#fff', padding: '8px 12px', borderRadius: '4px', cursor: 'pointer', fontWeight: '500' }}>
              Connect
            </button>
          </div>

          <h3 style={{ fontSize: '11px', fontWeight: '600', color: '#71717a', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '12px' }}>Connected Devices</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <div 
              onClick={() => setSelectedDevice('pc')}
              style={{ padding: '10px', borderRadius: '4px', border: selectedDevice === 'pc' ? '1px solid #3b82f6' : '1px solid #27272a', background: '#18181b', cursor: 'pointer' }}
            >
              <div style={{ fontWeight: '500', fontSize: '13px', color: '#f4f4f5' }}>Windows Host (PC)</div>
              <div style={{ fontSize: '11px', color: '#10b981' }}>● Online (1366x768)</div>
            </div>
            <div 
              onClick={() => setSelectedDevice('phone')}
              style={{ padding: '10px', borderRadius: '4px', border: selectedDevice === 'phone' ? '1px solid #3b82f6' : '1px solid #27272a', background: '#18181b', cursor: 'pointer' }}
            >
              <div style={{ fontWeight: '500', fontSize: '13px', color: '#f4f4f5' }}>Android Node (Mobile)</div>
              <div style={{ fontSize: '11px', color: '#10b981' }}>● Online (1080x2160)</div>
            </div>
          </div>
        </div>

        {/* Center: Remote Viewport & Control */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', padding: '16px', background: '#09090b' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
            <h2 style={{ fontSize: '14px', fontWeight: '500', color: '#f4f4f5', margin: 0 }}>
              Viewport — {selectedDevice === 'pc' ? 'Windows Host' : 'Android Mobile Node'}
            </h2>
            <div style={{ display: 'flex', gap: '6px' }}>
              {selectedDevice === 'pc' ? (
                <>
                  <button style={{ padding: '5px 10px', background: '#18181b', border: '1px solid #27272a', color: '#a1a1aa', borderRadius: '4px', cursor: 'pointer', fontSize: '12px' }}>Win+D</button>
                  <button style={{ padding: '5px 10px', background: '#18181b', border: '1px solid #27272a', color: '#a1a1aa', borderRadius: '4px', cursor: 'pointer', fontSize: '12px' }}>Vol+</button>
                  <button style={{ padding: '5px 10px', background: '#18181b', border: '1px solid #27272a', color: '#a1a1aa', borderRadius: '4px', cursor: 'pointer', fontSize: '12px' }}>Lock</button>
                </>
              ) : (
                <>
                  <button style={{ padding: '5px 10px', background: '#18181b', border: '1px solid #27272a', color: '#a1a1aa', borderRadius: '4px', cursor: 'pointer', fontSize: '12px' }}>Back</button>
                  <button style={{ padding: '5px 10px', background: '#18181b', border: '1px solid #27272a', color: '#a1a1aa', borderRadius: '4px', cursor: 'pointer', fontSize: '12px' }}>Home</button>
                  <button style={{ padding: '5px 10px', background: '#18181b', border: '1px solid #27272a', color: '#a1a1aa', borderRadius: '4px', cursor: 'pointer', fontSize: '12px' }}>Recents</button>
                </>
              )}
            </div>
          </div>

          {/* Screen Canvas */}
          <div style={{ flex: 1, background: '#000', borderRadius: '6px', border: '1px solid #27272a', display: 'flex', alignItems: 'center', justifyContent: 'center', overflow: 'hidden' }}>
            <img 
              src={selectedDevice === 'pc' ? 'http://localhost:5050/api/pc/screen' : 'http://localhost:5050/api/screenshot'} 
              alt="Remote Viewport" 
              style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain', cursor: 'crosshair' }} 
            />
          </div>

          {/* AI Prompt Bar */}
          <div style={{ marginTop: '12px', background: '#121215', padding: '12px', borderRadius: '6px', border: '1px solid #27272a' }}>
            <div style={{ fontSize: '12px', color: '#3b82f6', fontWeight: '500', marginBottom: '6px' }}>
              Pentatopus Co-Pilot ({selectedDevice === 'pc' ? 'PC Agent' : 'Mobile Agent'})
            </div>
            <div style={{ display: 'flex', gap: '8px' }}>
              <input 
                type="text" 
                placeholder={`Give an autonomous instruction to ${selectedDevice === 'pc' ? 'Windows' : 'Android'}...`}
                value={aiGoal}
                onChange={e => setAiGoal(e.target.value)}
                style={{ flex: 1, padding: '8px 12px', background: '#18181b', border: '1px solid #27272a', borderRadius: '4px', color: '#fff', fontSize: '13px' }}
              />
              <button style={{ background: '#2563eb', border: 'none', color: '#fff', padding: '8px 16px', borderRadius: '4px', fontWeight: '500', cursor: 'pointer' }}>
                Execute
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
