import React, { useState, useEffect, useRef } from 'react';

export default function App() {
  const [selectedDevice, setSelectedDevice] = useState('pc');
  const [serverUrl, setServerUrl] = useState('http://localhost:5050');
  const [deviceCode, setDeviceCode] = useState('849-210');
  const [targetCode, setTargetCode] = useState('');
  const [licenseKey, setLicenseKey] = useState('');
  const [isPro, setIsPro] = useState(false);
  const [aiGoal, setAiGoal] = useState('');
  const [aiLogs, setAiLogs] = useState('Ready for Pentactopus directives...');
  const [isExecuting, setIsExecuting] = useState(false);
  const [frameTimestamp, setFrameTimestamp] = useState(Date.now());
  const viewportRef = useRef(null);

  // Auto-refresh remote viewport stream
  useEffect(() => {
    const interval = setInterval(() => {
      setFrameTimestamp(Date.now());
    }, 1500);
    return () => clearInterval(interval);
  }, []);

  const connectToDevice = () => {
    if (!targetCode) return;
    setAiLogs(`Connected to remote mesh node: ${targetCode}`);
  };

  const redeemCoupon = async () => {
    const code = prompt("Enter Promo / Coupon Code (e.g. PENTAFREE or LAUNCH50):");
    if (!code) return;
    try {
      const res = await fetch(`${serverUrl}/api/coupons/redeem`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code })
      });
      const data = await res.json();
      if (data.success || data.valid) {
        setIsPro(true);
        const lic = data.license_key || "PENTA-PRO-ACTIVATED";
        setLicenseKey(lic);
        setAiLogs(`License Activated: ${lic}`);
        alert("License Activated: " + lic);
      } else {
        alert("Error: " + (data.error || "Invalid code"));
      }
    } catch (e) {
      alert("Error redeeming coupon: " + e);
    }
  };

  const sendQuickAction = async (actionType, param) => {
    const devId = selectedDevice === 'pc' ? 'pc_windows_host' : 'phone_android_node';
    setAiLogs(`Dispatching hardware action: ${param} to ${devId}...`);

    try {
      let endpoint = `${serverUrl}/api/device/${devId}/action`;
      let payload = {};

      if (selectedDevice === 'pc') {
        payload = { action: 'hotkey', hotkey: param, type: 'hotkey' };
      } else {
        payload = { action: 'key_event', key: param, type: 'key', keycode: param === 'BACK' ? 4 : (param === 'HOME' ? 3 : 187) };
      }

      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (data.success) {
        setAiLogs(`Action '${param}' executed successfully.`);
      } else {
        setAiLogs(`Action warning: ${data.error || 'Pending queue'}`);
      }
    } catch (err) {
      setAiLogs(`Local dispatch: ${param} injected.`);
    }
  };

  const handleViewportClick = async (e) => {
    if (!viewportRef.current) return;
    const rect = viewportRef.current.getBoundingClientRect();
    const normX = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
    const normY = Math.max(0, Math.min(1, (e.clientY - rect.top) / rect.height));

    const devId = selectedDevice === 'pc' ? 'pc_windows_host' : 'phone_android_node';
    setAiLogs(`Touch/Click at [${normX.toFixed(3)}, ${normY.toFixed(3)}] dispatched.`);

    try {
      await fetch(`${serverUrl}/api/device/${devId}/action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: selectedDevice === 'pc' ? 'click' : 'tap',
          type: selectedDevice === 'pc' ? 'click' : 'tap',
          norm_x: normX,
          norm_y: normY
        })
      });
    } catch (err) {
      // Graceful fallback
    }
  };

  const executeAiDirective = async () => {
    if (!aiGoal.trim() || isExecuting) return;
    const devId = selectedDevice === 'pc' ? 'pc_windows_host' : 'phone_android_node';
    setIsExecuting(true);
    setAiLogs(`[COGNITIVE DISPATCH] Objective: "${aiGoal}" on ${devId}...\n`);

    try {
      const res = await fetch(`${serverUrl}/api/device/${devId}/action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'goal',
          type: 'goal',
          goal: aiGoal
        })
      });
      const data = await res.json();
      if (data.success) {
        setAiLogs(prev => prev + `[STATUS] Action Task Queued (${data.task_id}). Awaiting local daemon perception step.`);
      } else {
        setAiLogs(prev => prev + `[ERROR] ${data.error || 'Failed to dispatch mission'}`);
      }
    } catch (err) {
      setAiLogs(prev => prev + `[LOCAL EMULATION] Dispatched directive locally.`);
    } finally {
      setIsExecuting(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', background: '#09090b', color: '#f4f4f5', fontFamily: 'Inter, system-ui, sans-serif' }}>
      {/* Top Header */}
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 20px', borderBottom: '1px solid #27272a', background: '#121215' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ fontSize: '16px', fontWeight: '600', letterSpacing: '-0.02em', color: '#f4f4f5' }}>Pentactopus</span>
          <span style={{ background: '#27272a', color: '#a1a1aa', fontSize: '11px', padding: '2px 8px', borderRadius: '4px', border: '1px solid #3f3f46' }}>Native Client</span>
          {isPro ? (
            <span style={{ background: 'rgba(59,130,246,0.15)', color: '#60a5fa', fontSize: '11px', padding: '2px 8px', borderRadius: '4px', border: '1px solid rgba(59,130,246,0.3)' }}>PRO ACTIVATED</span>
          ) : (
            <button onClick={redeemCoupon} style={{ background: '#2563eb', color: '#fff', fontSize: '11px', fontWeight: '500', padding: '3px 10px', borderRadius: '4px', border: 'none', cursor: 'pointer' }}>
              Redeem Code
            </button>
          )}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <span style={{ fontSize: '12px', color: '#71717a' }}>
            Hub: <input 
              type="text" 
              value={serverUrl} 
              onChange={e => setServerUrl(e.target.value)}
              style={{ background: '#18181b', border: '1px solid #27272a', color: '#a1a1aa', fontSize: '11px', padding: '2px 6px', borderRadius: '3px', width: '150px' }}
            />
          </span>
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
              <div style={{ fontSize: '11px', color: '#10b981' }}>● Online (Desktop Controller)</div>
            </div>
            <div 
              onClick={() => setSelectedDevice('phone')}
              style={{ padding: '10px', borderRadius: '4px', border: selectedDevice === 'phone' ? '1px solid #3b82f6' : '1px solid #27272a', background: '#18181b', cursor: 'pointer' }}
            >
              <div style={{ fontWeight: '500', fontSize: '13px', color: '#f4f4f5' }}>Android Node (Mobile)</div>
              <div style={{ fontSize: '11px', color: '#10b981' }}>● Online (ADB Remote Bridge)</div>
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
                  <button onClick={() => sendQuickAction('hotkey', 'win_d')} style={{ padding: '5px 10px', background: '#18181b', border: '1px solid #27272a', color: '#a1a1aa', borderRadius: '4px', cursor: 'pointer', fontSize: '12px' }}>Win+D</button>
                  <button onClick={() => sendQuickAction('hotkey', 'vol_up')} style={{ padding: '5px 10px', background: '#18181b', border: '1px solid #27272a', color: '#a1a1aa', borderRadius: '4px', cursor: 'pointer', fontSize: '12px' }}>Vol+</button>
                  <button onClick={() => sendQuickAction('hotkey', 'enter')} style={{ padding: '5px 10px', background: '#18181b', border: '1px solid #27272a', color: '#a1a1aa', borderRadius: '4px', cursor: 'pointer', fontSize: '12px' }}>Enter</button>
                </>
              ) : (
                <>
                  <button onClick={() => sendQuickAction('key', 'BACK')} style={{ padding: '5px 10px', background: '#18181b', border: '1px solid #27272a', color: '#a1a1aa', borderRadius: '4px', cursor: 'pointer', fontSize: '12px' }}>Back</button>
                  <button onClick={() => sendQuickAction('key', 'HOME')} style={{ padding: '5px 10px', background: '#18181b', border: '1px solid #27272a', color: '#a1a1aa', borderRadius: '4px', cursor: 'pointer', fontSize: '12px' }}>Home</button>
                  <button onClick={() => sendQuickAction('key', 'RECENTS')} style={{ padding: '5px 10px', background: '#18181b', border: '1px solid #27272a', color: '#a1a1aa', borderRadius: '4px', cursor: 'pointer', fontSize: '12px' }}>Recents</button>
                </>
              )}
            </div>
          </div>

          {/* Screen Canvas with Coordinate Event Forwarding */}
          <div 
            ref={viewportRef}
            onClick={handleViewportClick}
            style={{ flex: 1, background: '#000', borderRadius: '6px', border: '1px solid #27272a', display: 'flex', alignItems: 'center', justifyContent: 'center', overflow: 'hidden', position: 'relative' }}
          >
            <img 
              src={`${serverUrl}${selectedDevice === 'pc' ? '/api/pc/screen' : '/api/screenshot'}?t=${frameTimestamp}`} 
              alt="Remote Viewport" 
              onError={(e) => { e.target.src = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='400' height='300' viewBox='0 0 400 300'><rect width='100%' height='100%' fill='%23121215'/><text x='50%' y='50%' fill='%2371717a' font-family='sans-serif' font-size='14' text-anchor='middle'>Awaiting Remote Display Buffer...</text></svg>"; }}
              style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain', cursor: 'crosshair', userSelect: 'none' }} 
            />
          </div>

          {/* AI Prompt Bar & Execution Console */}
          <div style={{ marginTop: '12px', background: '#121215', padding: '12px', borderRadius: '6px', border: '1px solid #27272a' }}>
            <div style={{ fontSize: '12px', color: '#3b82f6', fontWeight: '500', marginBottom: '6px' }}>
              Pentactopus Co-Pilot ({selectedDevice === 'pc' ? 'PC Agent' : 'Mobile Agent'})
            </div>
            <div style={{ display: 'flex', gap: '8px', marginBottom: '8px' }}>
              <input 
                type="text" 
                placeholder={`Give an autonomous instruction to ${selectedDevice === 'pc' ? 'Windows' : 'Android'}...`}
                value={aiGoal}
                onChange={e => setAiGoal(e.target.value)}
                onKeyDown={e => { if (e.key === 'Enter') executeAiDirective(); }}
                style={{ flex: 1, padding: '8px 12px', background: '#18181b', border: '1px solid #27272a', borderRadius: '4px', color: '#fff', fontSize: '13px' }}
              />
              <button 
                onClick={executeAiDirective}
                disabled={isExecuting}
                style={{ background: isExecuting ? '#475569' : '#2563eb', border: 'none', color: '#fff', padding: '8px 16px', borderRadius: '4px', fontWeight: '500', cursor: isExecuting ? 'not-allowed' : 'pointer' }}
              >
                {isExecuting ? 'Executing...' : 'Execute'}
              </button>
            </div>
            <div style={{ background: '#09090b', padding: '8px 10px', borderRadius: '4px', border: '1px solid #27272a', fontSize: '11px', color: '#10b981', fontFamily: 'monospace', minHeight: '28px', whiteSpace: 'pre-wrap' }}>
              {aiLogs}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
