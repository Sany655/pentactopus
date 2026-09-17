import React, { useState, useEffect, useRef } from 'react';

export default function App() {
  const [currentView, setCurrentView] = useState('login');
  const [serverUrl, setServerUrl] = useState('http://localhost:5050');
  
  // Auth state
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [authToken, setAuthToken] = useState(localStorage.getItem('penta_auth_token') || '');
  const [loginError, setLoginError] = useState('');
  
  // General State
  const [deviceCode, setDeviceCode] = useState('849-210');
  const [targetCode, setTargetCode] = useState('');
  const [userPlan, setUserPlan] = useState(localStorage.getItem('penta_plan') || 'free');
  const [menuOpen, setMenuOpen] = useState(false);
  
  // Chat Agent State
  const [aiGoal, setAiGoal] = useState('');
  const [chatHistory, setChatHistory] = useState([
    { sender: 'agent', text: 'Hello! I am your Pentactopus local AI agent. How can I assist you today?' }
  ]);
  const [isExecuting, setIsExecuting] = useState(false);
  const [agentAccessLevel, setAgentAccessLevel] = useState('full'); // 'read_only' or 'full'
  const [showVisionPreview, setShowVisionPreview] = useState(false);
  
  // New States
  const [llmProvider, setLlmProvider] = useState(localStorage.getItem('penta_llm_provider') || 'openai');
  const [apiKey, setApiKey] = useState(localStorage.getItem('penta_api_key') || '');
  const [visionQuality, setVisionQuality] = useState('high');
  
  // Viewport State
  const [selectedDevice, setSelectedDevice] = useState('pc');
  const [frameTimestamp, setFrameTimestamp] = useState(Date.now());
  const viewportRef = useRef(null);
  const videoRef = useRef(null);
  const chatEndRef = useRef(null);
  
  // Mobile / Touch State
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);
  const [touchStartPos, setTouchStartPos] = useState(null);
  
  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth < 768);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);
  
  // WebRTC State
  const [rtcConnectionState, setRtcConnectionState] = useState('disconnected');
  const peerConnection = useRef(null);
  const dataChannel = useRef(null);
  const webrtcPollInterval = useRef(null);

  useEffect(() => {
    if (authToken && currentView === 'login') {
      setCurrentView('chat');
    }
  }, [authToken, currentView]);

  useEffect(() => {
    if (currentView === 'anydesk') {
      startWebRTCSession();
      const interval = setInterval(() => {
        setFrameTimestamp(Date.now());
      }, 1500);
      return () => {
        clearInterval(interval);
        stopWebRTCSession();
      };
    }
  }, [currentView]);

  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [chatHistory]);

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`${serverUrl}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      const data = await res.json();
      if (data.success) {
        localStorage.setItem('penta_auth_token', data.token);
        const plan = data.user ? data.user.plan : 'free';
        localStorage.setItem('penta_plan', plan);
        setUserPlan(plan);
        setAuthToken(data.token);
        setCurrentView('chat');
      } else {
        setLoginError(data.error || 'Login failed');
      }
    } catch (err) {
      // Graceful fallback for local development without actual user store
      console.warn("Login endpoint failed, using mock auth");
      localStorage.setItem('penta_auth_token', 'mock_token');
      setAuthToken('mock_token');
      setCurrentView('chat');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('penta_auth_token');
    localStorage.removeItem('penta_plan');
    setUserPlan('free');
    setAuthToken('');
    setCurrentView('login');
    setMenuOpen(false);
  };

  const isLocalServer = () => serverUrl.includes('localhost') || serverUrl.includes('127.0.0.1');

  const handleNewChat = () => {
    setChatHistory([{ sender: 'agent', text: 'Hello! I am your Pentactopus local AI agent. How can I assist you today?' }]);
    setAiGoal('');
  };

  const executeAiDirective = async () => {
    if (!aiGoal.trim() || isExecuting) return;
    const goalText = aiGoal;
    setAiGoal('');
    setChatHistory(prev => [...prev, { sender: 'user', text: goalText }]);
    setIsExecuting(true);
    
    const devId = selectedDevice === 'pc' ? 'pc_windows_host' : 'phone_android_node';

    try {
      const isLocal = isLocalServer();
      const endpoint = isLocal
        ? `${serverUrl}/api/${selectedDevice === 'pc' ? 'pc' : 'mobile'}/agent`
        : `${serverUrl}/api/device/${devId}/action`;

      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'goal', type: 'goal', goal: goalText })
      });
      const data = await res.json();
      
      if (data.success) {
        if (isLocal) {
          let aiText = data.output;
          try {
            const jsonStart = aiText.indexOf('{');
            const jsonEnd = aiText.lastIndexOf('}');
            if (jsonStart !== -1 && jsonEnd !== -1) {
              const parsed = JSON.parse(aiText.substring(jsonStart, jsonEnd + 1));
              if (parsed.message) aiText = parsed.message;
            }
          } catch (e) {}
          setChatHistory(prev => [...prev, { sender: 'agent', text: aiText }]);
        } else {
          setChatHistory(prev => [...prev, { sender: 'agent', text: `Action Task Queued (${data.task_id}). Awaiting local daemon perception step.` }]);
        }
      } else {
        setChatHistory(prev => [...prev, { sender: 'agent', text: `Error: ${data.error || 'Failed to dispatch mission'}` }]);
      }
    } catch (err) {
      setChatHistory(prev => [...prev, { sender: 'agent', text: `[LOCAL EMULATION] Dispatched directive locally.` }]);
    } finally {
      setIsExecuting(false);
    }
  };

  const connectToDevice = () => {
    if (!targetCode) return;
    setCurrentView('anydesk');
  };

  const startWebRTCSession = async () => {
    setRtcConnectionState('connecting');
    const configuration = { iceServers: [{ urls: 'stun:stun.l.google.com:19302' }] };
    const pc = new RTCPeerConnection(configuration);
    peerConnection.current = pc;
    
    dataChannel.current = pc.createDataChannel('control');
    dataChannel.current.onopen = () => setRtcConnectionState('connected');
    dataChannel.current.onclose = () => setRtcConnectionState('disconnected');

    pc.ontrack = (event) => {
      if (videoRef.current) {
        videoRef.current.srcObject = event.streams[0];
      }
    };

    pc.onicecandidate = async (event) => {
      if (event.candidate) {
        await sendWebRTCSignal('ice', event.candidate);
      }
    };

    try {
      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);
      await sendWebRTCSignal('offer', offer);
      
      // Start polling for answers/ice from remote
      webrtcPollInterval.current = setInterval(pollWebRTCSignals, 2000);
    } catch (err) {
      console.warn("Failed to create WebRTC offer", err);
      setRtcConnectionState('error');
    }
  };

  const stopWebRTCSession = () => {
    if (webrtcPollInterval.current) clearInterval(webrtcPollInterval.current);
    if (peerConnection.current) peerConnection.current.close();
    setRtcConnectionState('disconnected');
  };

  const sendWebRTCSignal = async (type, payload) => {
    try {
      await fetch(`${serverUrl}/api/webrtc/signal`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${authToken}` },
        body: JSON.stringify({ target_id: targetCode, sender_id: deviceCode, type, payload })
      });
    } catch (e) {
      console.warn("Signaling failed:", e);
    }
  };

  const pollWebRTCSignals = async () => {
    try {
      const res = await fetch(`${serverUrl}/api/webrtc/poll?target_id=${deviceCode}`, {
        headers: { 'Authorization': `Bearer ${authToken}` }
      });
      const data = await res.json();
      if (data.signals) {
        for (const sig of data.signals) {
          if (sig.sender !== targetCode) continue;
          const pc = peerConnection.current;
          if (!pc) return;
          if (sig.type === 'answer') {
            await pc.setRemoteDescription(new RTCSessionDescription(sig.payload));
          } else if (sig.type === 'ice') {
            await pc.addIceCandidate(new RTCIceCandidate(sig.payload));
          }
        }
      }
    } catch (e) {}
  };

  const handleViewportTouchStart = (e) => {
    if (e.touches.length > 0) {
      setTouchStartPos({ x: e.touches[0].clientX, y: e.touches[0].clientY });
    }
  };

  const handleViewportTouchEnd = async (e) => {
    if (!viewportRef.current || e.changedTouches.length === 0) return;
    const touch = e.changedTouches[0];
    const rect = viewportRef.current.getBoundingClientRect();
    const normX = Math.max(0, Math.min(1, (touch.clientX - rect.left) / rect.width));
    const normY = Math.max(0, Math.min(1, (touch.clientY - rect.top) / rect.height));

    const devId = selectedDevice === 'pc' ? 'pc_windows_host' : 'phone_android_node';

    if (touchStartPos) {
      const dx = touch.clientX - touchStartPos.x;
      const dy = touch.clientY - touchStartPos.y;
      if (Math.abs(dx) > 30 || Math.abs(dy) > 30) {
        // Swipe gesture detected
        try {
          await fetch(`${serverUrl}/api/device/${devId}/action`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${authToken}` },
            body: JSON.stringify({ type: 'swipe', dx, dy })
          });
        } catch (err) {}
        setTouchStartPos(null);
        return;
      }
    }
    setTouchStartPos(null);

    try {
      const isLocal = isLocalServer();
      const endpoint = isLocal
        ? `${serverUrl}/api/${selectedDevice === 'pc' ? 'pc' : 'mobile'}/click`
        : `${serverUrl}/api/device/${devId}/action`;

      await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${authToken}` },
        body: JSON.stringify({
          action: selectedDevice === 'pc' ? 'click' : 'tap',
          type: selectedDevice === 'pc' ? 'click' : 'tap',
          norm_x: normX,
          norm_y: normY
        })
      });
    } catch (err) {
      console.warn("Touch failed", err);
    }
  };

  // -----------------------------------------------------
  // STYLES
  // -----------------------------------------------------
  const styles = {
    app: { display: 'flex', flexDirection: 'column', height: '100vh', background: '#0a0a0f', color: '#f4f4f5', fontFamily: 'Inter, system-ui, sans-serif' },
    header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '16px 24px', background: 'rgba(15, 15, 20, 0.8)', backdropFilter: 'blur(12px)', borderBottom: '1px solid rgba(255,255,255,0.05)', position: 'relative', zIndex: 10 },
    logo: { fontSize: '18px', fontWeight: '700', background: 'linear-gradient(90deg, #60a5fa, #a78bfa)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' },
    menuBtn: { background: 'transparent', border: 'none', color: '#a1a1aa', fontSize: '24px', cursor: 'pointer', padding: '4px' },
    dropdown: { position: 'absolute', top: '60px', right: '24px', background: '#18181b', border: '1px solid #27272a', borderRadius: '8px', boxShadow: '0 10px 25px rgba(0,0,0,0.5)', overflow: 'hidden', minWidth: '200px' },
    dropdownItem: { padding: '12px 16px', cursor: 'pointer', fontSize: '14px', borderBottom: '1px solid #27272a', transition: 'background 0.2s' },
    loginContainer: { flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' },
    loginCard: { background: '#121215', padding: '40px', borderRadius: '16px', border: '1px solid rgba(255,255,255,0.05)', width: '360px', boxShadow: '0 20px 40px rgba(0,0,0,0.4)' },
    input: { width: '100%', padding: '12px', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', color: '#fff', fontSize: '14px', marginBottom: '16px', boxSizing: 'border-box' },
    button: { width: '100%', padding: '12px', background: '#3b82f6', color: '#fff', border: 'none', borderRadius: '8px', fontSize: '14px', fontWeight: '600', cursor: 'pointer', transition: 'background 0.2s' },
    chatContainer: { flex: 1, display: 'flex', flexDirection: 'column', maxWidth: '800px', margin: '0 auto', width: '100%', padding: '24px', boxSizing: 'border-box' },
    messageList: { flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '20px', paddingBottom: '20px' },
    bubbleUser: { alignSelf: 'flex-end', background: '#3b82f6', color: '#fff', padding: '12px 16px', borderRadius: '16px 16px 4px 16px', maxWidth: '80%' },
    bubbleAgent: { alignSelf: 'flex-start', background: '#1e1e24', border: '1px solid #27272a', color: '#e4e4e7', padding: '12px 16px', borderRadius: '16px 16px 16px 4px', maxWidth: '85%', whiteSpace: 'pre-wrap', fontFamily: 'monospace', fontSize: '13px' },
    inputBar: { display: 'flex', gap: '12px', background: '#121215', padding: '12px', borderRadius: '12px', border: '1px solid #27272a' },
    viewportContainer: { flex: 1, display: 'flex', flexDirection: 'column', padding: '24px', background: '#09090b' },
    canvasWrapper: { flex: 1, background: '#000', borderRadius: '12px', border: '1px solid #27272a', overflow: 'hidden', display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'relative' },
  };

  // -----------------------------------------------------
  // RENDERERS
  // -----------------------------------------------------
  const renderHeader = () => (
    <header style={styles.header}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={styles.logo}>Pentactopus</div>
        {currentView !== 'login' && (
          <>
            <span style={{ background: 'rgba(255,255,255,0.05)', color: '#a1a1aa', fontSize: '11px', padding: '4px 8px', borderRadius: '6px' }}>Local Agent Mode</span>
            {userPlan === 'free' ? (
              <span style={{ background: 'rgba(245, 158, 11, 0.1)', color: '#f59e0b', fontSize: '11px', padding: '4px 8px', borderRadius: '6px', border: '1px solid rgba(245, 158, 11, 0.3)' }}>Free Starter</span>
            ) : (
              <span style={{ background: 'rgba(59, 130, 246, 0.15)', color: '#60a5fa', fontSize: '11px', padding: '4px 8px', borderRadius: '6px', border: '1px solid rgba(59, 130, 246, 0.3)' }}>{userPlan.toUpperCase()} PLAN</span>
            )}
          </>
        )}
      </div>
      
      {currentView !== 'login' && (
        <div style={{ position: 'relative' }}>
          <button style={styles.menuBtn} onClick={() => setMenuOpen(!menuOpen)}>☰</button>
          
          {menuOpen && (
            <div style={styles.dropdown}>
              <div 
                style={styles.dropdownItem} 
                onMouseEnter={e => e.target.style.background = '#27272a'} 
                onMouseLeave={e => e.target.style.background = 'transparent'}
                onClick={() => { setCurrentView('chat'); setMenuOpen(false); }}
              >
                💬 AI Chat Agent
              </div>
              <div 
                style={styles.dropdownItem} 
                onMouseEnter={e => e.target.style.background = '#27272a'} 
                onMouseLeave={e => e.target.style.background = 'transparent'}
                onClick={() => { setCurrentView('connect'); setMenuOpen(false); }}
              >
                🔗 Connect to other host
              </div>
              <div 
                style={styles.dropdownItem} 
                onMouseEnter={e => e.target.style.background = '#27272a'} 
                onMouseLeave={e => e.target.style.background = 'transparent'}
                onClick={() => { setCurrentView('host_setup'); setMenuOpen(false); }}
              >
                🖥️ Host this device
              </div>
              <div 
                style={styles.dropdownItem} 
                onMouseEnter={e => e.target.style.background = '#27272a'} 
                onMouseLeave={e => e.target.style.background = 'transparent'}
                onClick={() => { setCurrentView('model_config'); setMenuOpen(false); }}
              >
                🧠 Model Configuration
              </div>
              <div 
                style={styles.dropdownItem} 
                onMouseEnter={e => e.target.style.background = '#27272a'} 
                onMouseLeave={e => e.target.style.background = 'transparent'}
                onClick={() => { setCurrentView('subscription'); setMenuOpen(false); }}
              >
                💳 Subscription Plan
              </div>
              <div 
                style={styles.dropdownItem} 
                onMouseEnter={e => e.target.style.background = '#27272a'} 
                onMouseLeave={e => e.target.style.background = 'transparent'}
                onClick={() => { setCurrentView('usage'); setMenuOpen(false); }}
              >
                📊 Usage & History
              </div>
              <div 
                style={styles.dropdownItem} 
                onMouseEnter={e => e.target.style.background = '#27272a'} 
                onMouseLeave={e => e.target.style.background = 'transparent'}
                onClick={() => { setCurrentView('settings'); setMenuOpen(false); }}
              >
                ⚙️ Settings
              </div>
              <div 
                style={{ ...styles.dropdownItem, color: '#ef4444', borderBottom: 'none' }} 
                onMouseEnter={e => e.target.style.background = 'rgba(239, 68, 68, 0.1)'} 
                onMouseLeave={e => e.target.style.background = 'transparent'}
                onClick={handleLogout}
              >
                🚪 Logout
              </div>
            </div>
          )}
        </div>
      )}
    </header>
  );

  const renderLogin = () => (
    <div style={styles.loginContainer}>
      <form onSubmit={handleLogin} style={styles.loginCard}>
        <h2 style={{ margin: '0 0 8px 0', fontSize: '24px', fontWeight: '600' }}>Welcome Back</h2>
        <p style={{ color: '#a1a1aa', fontSize: '14px', marginBottom: '24px' }}>Sign in to access your autonomous AI agents.</p>
        
        {loginError && <div style={{ background: 'rgba(239,68,68,0.1)', color: '#ef4444', padding: '10px', borderRadius: '6px', fontSize: '13px', marginBottom: '16px' }}>{loginError}</div>}
        
        <input style={styles.input} type="email" placeholder="Email Address" value={email} onChange={e => setEmail(e.target.value)} required />
        <input style={styles.input} type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} required />
        
        <button style={styles.button} type="submit">Sign In</button>
        
        <div style={{ textAlign: 'center', marginTop: '16px' }}>
          <a href="https://pentactopus.vercel.app/" target="_blank" rel="noreferrer" style={{ color: '#60a5fa', textDecoration: 'none', fontSize: '13px' }}>
            Don't have an account? Register on the Web Portal
          </a>
        </div>
      </form>
    </div>
  );

  const renderChat = () => (
    <div style={{ flex: 1, display: 'flex', overflow: 'hidden', flexDirection: isMobile ? 'column' : 'row' }}>
      <div style={{ width: isMobile ? '100%' : '260px', height: isMobile ? '140px' : 'auto', background: '#0e0e11', borderRight: isMobile ? 'none' : '1px solid #27272a', borderBottom: isMobile ? '1px solid #27272a' : 'none', display: 'flex', flexDirection: 'column', padding: '16px', boxSizing: 'border-box', flexShrink: 0 }}>
        <button 
          style={{ ...styles.button, background: 'transparent', border: '1px solid #3f3f46', marginBottom: '16px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', color: '#e4e4e7' }}
          onClick={handleNewChat}
        >
          <span style={{ fontSize: '16px', fontWeight: 'bold' }}>+</span> New Chat
        </button>
        
        <div style={{ marginBottom: '16px' }}>
          <label style={{ fontSize: '11px', fontWeight: '600', color: '#71717a', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Agent Access</label>
          <select 
            style={{ ...styles.input, marginTop: '8px', fontSize: '12px', padding: '8px', background: '#18181b' }}
            value={agentAccessLevel}
            onChange={e => setAgentAccessLevel(e.target.value)}
          >
            <option value="full">Full Control (Click/Type)</option>
            <option value="read_only">Read-Only (Analysis)</option>
          </select>
        </div>
        
        <div style={{ marginBottom: '16px' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', color: '#a1a1aa', cursor: 'pointer' }}>
            <input type="checkbox" checked={showVisionPreview} onChange={e => setShowVisionPreview(e.target.checked)} />
            Show Vision Preview
          </label>
        </div>

        <div style={{ fontSize: '11px', fontWeight: '600', color: '#71717a', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '12px' }}>Recent Sessions</div>
        <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '4px' }}>
          <div style={{ padding: '10px 12px', background: '#18181b', borderRadius: '6px', fontSize: '13px', color: '#e4e4e7', cursor: 'pointer', border: '1px solid #3b82f6' }}>
            Current Session
          </div>
          <div style={{ padding: '10px 12px', borderRadius: '6px', fontSize: '13px', color: '#a1a1aa', cursor: 'pointer' }} onMouseEnter={e => e.target.style.background = '#18181b'} onMouseLeave={e => e.target.style.background = 'transparent'}>
            System Diagnostics
          </div>
          <div style={{ padding: '10px 12px', borderRadius: '6px', fontSize: '13px', color: '#a1a1aa', cursor: 'pointer' }} onMouseEnter={e => e.target.style.background = '#18181b'} onMouseLeave={e => e.target.style.background = 'transparent'}>
            File cleanup
          </div>
        </div>
      </div>
      <div style={styles.chatContainer}>
        <div style={styles.messageList}>
          {chatHistory.map((msg, i) => (
            <div key={i} style={msg.sender === 'user' ? styles.bubbleUser : styles.bubbleAgent}>
              {msg.text}
            </div>
          ))}
          {isExecuting && (
            <div style={{ ...styles.bubbleAgent, opacity: 0.7 }}>
              <span style={{ display: 'inline-block', animation: 'pulse 1.5s infinite' }}>●</span>
              <span style={{ display: 'inline-block', animation: 'pulse 1.5s infinite', animationDelay: '0.2s', margin: '0 4px' }}>●</span>
              <span style={{ display: 'inline-block', animation: 'pulse 1.5s infinite', animationDelay: '0.4s' }}>●</span>
            </div>
          )}
          {showVisionPreview && (
            <div style={{ alignSelf: 'center', background: '#18181b', padding: '8px', borderRadius: '8px', border: '1px solid #27272a', margin: '8px 0', textAlign: 'center' }}>
              <div style={{ fontSize: '11px', color: '#a1a1aa', marginBottom: '4px' }}>Agent Vision (Live View)</div>
              <img 
                src={`${serverUrl}/api/pc/screen?t=${Date.now()}`} 
                alt="Agent Vision" 
                style={{ width: '200px', borderRadius: '4px', border: '1px solid #3f3f46' }}
                onError={(e) => { e.target.style.display = 'none'; }}
              />
            </div>
          )}
          <div ref={chatEndRef} />
        </div>
        
        <div style={styles.inputBar}>
          <input 
            style={{ ...styles.input, marginBottom: 0, border: 'none', background: 'transparent' }}
            type="text" 
            placeholder="Ask the AI agent to perform a task on your device..." 
            value={aiGoal}
            onChange={e => setAiGoal(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter') executeAiDirective(); }}
          />
          <button 
            style={{ ...styles.button, width: 'auto', padding: '0 24px' }}
            onClick={executeAiDirective}
            disabled={isExecuting}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );

  const renderConnect = () => (
    <div style={styles.loginContainer}>
      <div style={styles.loginCard}>
        <h2 style={{ margin: '0 0 8px 0', fontSize: '20px' }}>Connect to Remote Host</h2>
        <p style={{ color: '#a1a1aa', fontSize: '14px', marginBottom: '16px' }}>Enter the unique identifier of the device you want to control.</p>
        
        {userPlan === 'free' && (
          <div style={{ background: 'rgba(245,158,11,0.1)', padding: '12px', borderRadius: '8px', border: '1px solid rgba(245,158,11,0.2)', marginBottom: '20px', fontSize: '12px', color: '#fcd34d' }}>
            <strong>Note:</strong> Cloud Remote Access is limited to 30 mins/day on the Free plan. 
          </div>
        )}

        <input 
          style={{ ...styles.input, fontSize: '18px', letterSpacing: '2px', textAlign: 'center' }} 
          type="text" 
          placeholder="e.g. 123-456" 
          value={targetCode} 
          onChange={e => setTargetCode(e.target.value)} 
        />
        <button style={styles.button} onClick={connectToDevice}>Connect Session</button>
      </div>
    </div>
  );

  const renderHostSetup = () => (
    <div style={styles.loginContainer}>
      <div style={{ ...styles.loginCard, textAlign: 'center' }}>
        <h2 style={{ margin: '0 0 8px 0', fontSize: '20px' }}>Host This Device</h2>
        <p style={{ color: '#a1a1aa', fontSize: '14px', marginBottom: '24px' }}>Share this identifier with another user to allow them to connect and control this device remotely.</p>
        
        <div style={{ background: '#18181b', border: '1px dashed #3f3f46', padding: '24px', borderRadius: '12px', marginBottom: '24px' }}>
          <div style={{ fontSize: '12px', color: '#71717a', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '1px' }}>Your Device ID</div>
          <div style={{ fontSize: '36px', fontWeight: 'bold', color: '#60a5fa', letterSpacing: '4px' }}>{deviceCode}</div>
        </div>
        
        <button style={{ ...styles.button, background: '#27272a', color: '#fff' }} onClick={() => setCurrentView('chat')}>Back to Chat</button>
      </div>
    </div>
  );

  const renderAnydesk = () => (
    <div style={styles.viewportContainer}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <button style={{ background: '#27272a', color: '#fff', border: 'none', padding: '6px 12px', borderRadius: '6px', cursor: 'pointer' }} onClick={() => setCurrentView('connect')}>← Leave Session</button>
          <h2 style={{ fontSize: '16px', fontWeight: '500', margin: 0 }}>Controlling Remote Session: <span style={{ color: '#60a5fa' }}>{targetCode}</span></h2>
          <span style={{ fontSize: '12px', color: rtcConnectionState === 'connected' ? '#10b981' : '#f59e0b', padding: '2px 8px', background: 'rgba(255,255,255,0.05)', borderRadius: '12px' }}>
            {rtcConnectionState === 'connected' ? '● WebRTC Active' : '● Polling Fallback'}
          </span>
        </div>
        
        <div style={{ display: 'flex', gap: '8px' }}>
          <button style={{ padding: '6px 12px', background: '#18181b', border: '1px solid #27272a', color: '#a1a1aa', borderRadius: '6px', cursor: 'pointer', fontSize: '12px' }}>Win+D</button>
          <button style={{ padding: '6px 12px', background: '#18181b', border: '1px solid #27272a', color: '#a1a1aa', borderRadius: '6px', cursor: 'pointer', fontSize: '12px' }}>Vol+</button>
        </div>
      </div>
      
      <div 
        ref={viewportRef} 
        onClick={handleViewportTouchEnd} // Unified click/touch logic
        onTouchStart={handleViewportTouchStart}
        onTouchEnd={handleViewportTouchEnd}
        style={{...styles.canvasWrapper, touchAction: 'none'}}
      >
        <video 
          ref={videoRef}
          autoPlay 
          playsInline 
          style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', objectFit: 'contain', zIndex: rtcConnectionState === 'connected' ? 2 : 0 }} 
        />
        <img 
          src={`${serverUrl}${selectedDevice === 'pc' ? '/api/pc/screen' : '/api/screenshot'}?t=${frameTimestamp}`} 
          alt="Remote Viewport Fallback" 
          onError={(e) => { e.target.src = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='400' height='300' viewBox='0 0 400 300'><rect width='100%' height='100%' fill='%23121215'/><text x='50%' y='50%' fill='%2371717a' font-family='sans-serif' font-size='14' text-anchor='middle'>Awaiting Remote Display Buffer...</text></svg>"; }}
          style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain', cursor: 'crosshair', userSelect: 'none', position: 'relative', zIndex: 1 }} 
        />
      </div>
    </div>
  );

  const renderModelConfig = () => (
    <div style={styles.loginContainer}>
      <div style={{...styles.loginCard, width: '420px'}}>
        <h2 style={{ margin: '0 0 8px 0', fontSize: '20px' }}>Model Configuration</h2>
        <p style={{ color: '#a1a1aa', fontSize: '14px', marginBottom: '24px' }}>Configure your local or cloud LLM provider for autonomous AI capabilities.</p>
        
        <label style={{display: 'block', marginBottom: '8px', fontSize: '13px', color: '#e4e4e7'}}>AI Provider</label>
        <select 
          style={{...styles.input, WebkitAppearance: 'none', background: '#18181b', color: '#fff'}} 
          value={llmProvider} 
          onChange={e => setLlmProvider(e.target.value)}
        >
          <option style={{ background: '#18181b', color: '#fff' }} value="openai">OpenAI (GPT-4o)</option>
          <option style={{ background: '#18181b', color: '#fff' }} value="gemini">Google (Gemini 2.5 Pro)</option>
          <option style={{ background: '#18181b', color: '#fff' }} value="anthropic">Anthropic (Claude 3.5 Sonnet)</option>
          <option style={{ background: '#18181b', color: '#fff' }} value="groq">Groq (Llama 3)</option>
          <option style={{ background: '#18181b', color: '#fff' }} value="ollama">Ollama (Local Inference)</option>
        </select>
        
        <label style={{display: 'block', marginBottom: '8px', fontSize: '13px', color: '#e4e4e7'}}>API Key</label>
        <input 
          style={styles.input} 
          type="password" 
          placeholder={`Enter your ${llmProvider} API key...`} 
          value={apiKey} 
          onChange={e => setApiKey(e.target.value)} 
        />
        
        <button style={styles.button} onClick={() => {
          localStorage.setItem('penta_llm_provider', llmProvider);
          localStorage.setItem('penta_api_key', apiKey);
          setCurrentView('chat');
        }}>Save Configuration</button>
      </div>
    </div>
  );

  const renderSubscription = () => (
    <div style={styles.loginContainer}>
      <div style={{...styles.loginCard, width: '420px'}}>
        <h2 style={{ margin: '0 0 8px 0', fontSize: '20px' }}>Subscription Plan</h2>
        <p style={{ color: '#a1a1aa', fontSize: '14px', marginBottom: '24px' }}>Manage your Pentactopus tier and usage.</p>
        
        <div style={{ background: '#18181b', border: '1px solid #3b82f6', padding: '24px', borderRadius: '12px', marginBottom: '24px' }}>
          <div style={{ fontSize: '12px', color: '#60a5fa', marginBottom: '4px', textTransform: 'uppercase', letterSpacing: '1px', fontWeight: 'bold' }}>Current Plan</div>
          <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#fff' }}>{userPlan === 'free' ? 'Free Starter' : 'PRO Tier'}</div>
          <p style={{color: '#a1a1aa', fontSize: '13px', margin: '8px 0 0 0'}}>
            {userPlan === 'free' ? 'Limited to 1 device and local network mesh.' : 'Unlimited P2P WebRTC mesh with 5 devices.'}
          </p>
        </div>
        
        {userPlan === 'free' && (
          <button style={{...styles.button, background: '#10b981', marginBottom: '12px'}}>Upgrade to PRO ($12/mo)</button>
        )}
        <button style={{...styles.button, background: '#27272a', color: '#fff'}} onClick={() => setCurrentView('chat')}>Back to Dashboard</button>
      </div>
    </div>
  );

  const renderUsageHistory = () => (
    <div style={styles.loginContainer}>
      <div style={{...styles.loginCard, width: '480px'}}>
        <h2 style={{ margin: '0 0 8px 0', fontSize: '20px' }}>Usage & Action History</h2>
        <p style={{ color: '#a1a1aa', fontSize: '14px', marginBottom: '24px' }}>Log of autonomous AI actions executed on your devices.</p>
        
        <div style={{ background: '#18181b', border: '1px solid #27272a', borderRadius: '12px', padding: '16px', marginBottom: '24px', maxHeight: '300px', overflowY: 'auto' }}>
          {[
            { id: 1, time: '2 mins ago', device: 'pc_windows_host', action: 'Opened Chrome' },
            { id: 2, time: '15 mins ago', device: 'phone_android_node', action: 'Tapped Settings' },
            { id: 3, time: '1 hour ago', device: 'pc_windows_host', action: 'Typed document' },
          ].map((item) => (
            <div key={item.id} style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 0', borderBottom: '1px solid #27272a' }}>
              <div>
                <div style={{ fontSize: '14px', color: '#e4e4e7' }}>{item.action}</div>
                <div style={{ fontSize: '11px', color: '#60a5fa' }}>{item.device}</div>
              </div>
              <div style={{ fontSize: '12px', color: '#71717a' }}>{item.time}</div>
            </div>
          ))}
        </div>
        
        <button style={{...styles.button, background: '#27272a', color: '#fff'}} onClick={() => setCurrentView('chat')}>Back to Dashboard</button>
      </div>
    </div>
  );

  const renderSettings = () => (
    <div style={styles.loginContainer}>
      <div style={{...styles.loginCard, width: '420px'}}>
        <h2 style={{ margin: '0 0 8px 0', fontSize: '20px' }}>App Settings</h2>
        <p style={{ color: '#a1a1aa', fontSize: '14px', marginBottom: '24px' }}>General application preferences.</p>
        
        <label style={{display: 'block', marginBottom: '8px', fontSize: '13px', color: '#e4e4e7'}}>Remote Viewport Quality</label>
        <select 
          style={{...styles.input, WebkitAppearance: 'none', marginBottom: '24px', background: '#18181b', color: '#fff'}} 
          value={visionQuality} 
          onChange={e => setVisionQuality(e.target.value)}
        >
          <option style={{ background: '#18181b', color: '#fff' }} value="high">High (1080p, 60fps)</option>
          <option style={{ background: '#18181b', color: '#fff' }} value="medium">Medium (720p, 30fps)</option>
          <option style={{ background: '#18181b', color: '#fff' }} value="low">Low (480p, Low Latency)</option>
        </select>
        
        <button style={styles.button} onClick={() => setCurrentView('chat')}>Save Settings</button>
      </div>
    </div>
  );

  return (
    <div style={styles.app}>
      <style>
        {`
          @keyframes pulse {
            0% { opacity: 0.3; }
            50% { opacity: 1; }
            100% { opacity: 0.3; }
          }
          ::-webkit-scrollbar { width: 8px; }
          ::-webkit-scrollbar-track { background: transparent; }
          ::-webkit-scrollbar-thumb { background: #27272a; border-radius: 4px; }
          ::-webkit-scrollbar-thumb:hover { background: #3f3f46; }
        `}
      </style>
      
      {renderHeader()}
      
      {currentView === 'login' && renderLogin()}
      {currentView === 'chat' && renderChat()}
      {currentView === 'connect' && renderConnect()}
      {currentView === 'host_setup' && renderHostSetup()}
      {currentView === 'anydesk' && renderAnydesk()}
      {currentView === 'model_config' && renderModelConfig()}
      {currentView === 'subscription' && renderSubscription()}
      {currentView === 'usage' && renderUsageHistory()}
      {currentView === 'settings' && renderSettings()}
    </div>
  );
}
