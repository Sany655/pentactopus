import React, { useState, useEffect, useRef } from 'react';

const PROVIDER_INFO = {
  groq: {
    name: 'Groq (Llama 3.3)',
    model: 'llama-3.3-70b-versatile',
    keyUrl: 'https://console.groq.com/keys',
    label: 'console.groq.com/keys',
    buttonText: 'Get Free Groq Key',
    description: 'Ultra-fast Llama 3.3 70B inference with high free-tier rate limits.'
  },
  gemini: {
    name: 'Google Gemini',
    model: 'gemini-2.5-flash',
    keyUrl: 'https://aistudio.google.com/app/apikey',
    label: 'aistudio.google.com/app/apikey',
    buttonText: 'Get Free Gemini Key',
    description: 'Multimodal vision intelligence via Google AI Studio.'
  },
  openai: {
    name: 'OpenAI (GPT-4o)',
    model: 'gpt-4o-mini',
    keyUrl: 'https://platform.openai.com/api-keys',
    label: 'platform.openai.com/api-keys',
    buttonText: 'Get OpenAI Key',
    description: 'Official GPT-4o / GPT-4o-mini autonomous computer-use.'
  },
  anthropic: {
    name: 'Anthropic Claude',
    model: 'claude-3-5-sonnet-20241022',
    keyUrl: 'https://console.anthropic.com/settings/keys',
    label: 'console.anthropic.com/settings/keys',
    buttonText: 'Get Claude Key',
    description: 'Claude 3.5 Sonnet advanced reasoning and precision action execution.'
  },
  deepseek: {
    name: 'DeepSeek',
    model: 'deepseek-chat',
    keyUrl: 'https://platform.deepseek.com/api_keys',
    label: 'platform.deepseek.com/api_keys',
    buttonText: 'Get DeepSeek Key',
    description: 'DeepSeek V3 cost-efficient high intelligence model.'
  },
  openrouter: {
    name: 'OpenRouter',
    model: 'google/gemini-2.5-flash',
    keyUrl: 'https://openrouter.ai/keys',
    label: 'openrouter.ai/keys',
    buttonText: 'Get OpenRouter Key',
    description: 'Unified router supporting hundreds of models with a single API key.'
  },
  ollama: {
    name: 'Ollama (Local)',
    model: 'llama3.2',
    keyUrl: 'https://ollama.com/download',
    label: 'ollama.com/download',
    buttonText: 'Download Ollama Engine',
    description: '100% offline local inference on your GPU/CPU without needing an API key.'
  }
};

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
  const [llmProvider, setLlmProvider] = useState(localStorage.getItem('penta_llm_provider') || 'groq');
  const [apiKey, setApiKey] = useState(localStorage.getItem('penta_api_key') || '');
  const [visionQuality, setVisionQuality] = useState('high');
  const [isSavingConfig, setIsSavingConfig] = useState(false);
  const [configSaveStatus, setConfigSaveStatus] = useState('');
  
  // Support & FAQ State
  const [supportName, setSupportName] = useState('');
  const [supportEmail, setSupportEmail] = useState('');
  const [supportMessage, setSupportMessage] = useState('');
  const [supportImages, setSupportImages] = useState([]);
  const [supportStatus, setSupportStatus] = useState('');
  const [expandedFaq, setExpandedFaq] = useState(null);
  
  // Billing & Usage State
  const [usageHistory, setUsageHistory] = useState([]);
  const [billingMath, setBillingMath] = useState(null);
  const [isUpgrading, setIsUpgrading] = useState(false);
  
  // Viewport State
  const [selectedDevice, setSelectedDevice] = useState('pc');
  const [frameTimestamp, setFrameTimestamp] = useState(Date.now());
  const viewportRef = useRef(null);
  const videoRef = useRef(null);
  const chatEndRef = useRef(null);
  
  // Mobile / Touch State
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);
  const [touchStartPos, setTouchStartPos] = useState(null);

  // Multi-Device Communication & Control (F3)
  const [controlPermission, setControlPermission] = useState('interactive'); // 'view_only' | 'interactive' | 'admin'
  const [audioStreamActive, setAudioStreamActive] = useState(false);
  const [sessionChatOpen, setSessionChatOpen] = useState(false);
  const [sessionChatHistory, setSessionChatHistory] = useState([
    { sender: 'system', text: 'P2P Session initialized. Multi-device channel ready.', time: 'Now' }
  ]);
  const [sessionChatMessage, setSessionChatMessage] = useState('');
  const [sessionLatency, setSessionLatency] = useState(24);
  const [viewportZoom, setViewportZoom] = useState(1.0);
  const localAudioStream = useRef(null);
  const pinchStartDist = useRef(null);
  
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
    if (currentView === 'usage') {
      fetch(`${serverUrl}/api/usage/history`, {
        headers: { 'Authorization': `Bearer ${authToken}` }
      })
      .then(r => r.json())
      .then(d => { if (d.success) setUsageHistory(d.history); })
      .catch(e => console.error(e));
    } else if (currentView === 'subscription') {
      fetch(`${serverUrl}/api/billing/calculate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ devices: 2, ai_tasks: 15, stream_hours: 10 })
      })
      .then(r => r.json())
      .then(d => setBillingMath(d))
      .catch(e => console.error(e));
    }
  }, [currentView, authToken, serverUrl]);

  useEffect(() => {
    if (currentView === 'anydesk') {
      startWebRTCSession();
      const interval = setInterval(() => {
        setFrameTimestamp(Date.now());
      }, 500);
      return () => {
        clearInterval(interval);
        stopWebRTCSession();
      };
    } else if (currentView === 'host_setup') {
      startHostWebRTCSession();
      return () => {
        stopWebRTCSession();
      };
    }
  }, [currentView, targetCode]);

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

  const handleSaveModelConfig = async () => {
    setIsSavingConfig(true);
    setConfigSaveStatus('');
    try {
      localStorage.setItem('penta_llm_provider', llmProvider);
      localStorage.setItem('penta_api_key', apiKey);
      
      const defaultModel = PROVIDER_INFO[llmProvider]?.model || 'gemini-2.5-flash';
      await fetch(`${serverUrl}/api/config`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          provider: llmProvider,
          model: defaultModel,
          model_name: defaultModel,
          api_key: apiKey
        })
      });
      setConfigSaveStatus('Configuration saved and synchronized to system!');
      setTimeout(() => {
        setCurrentView('chat');
      }, 700);
    } catch (err) {
      console.warn('Could not sync config to server, saved locally:', err);
      setConfigSaveStatus('Saved locally to browser storage.');
      setTimeout(() => {
        setCurrentView('chat');
      }, 700);
    } finally {
      setIsSavingConfig(false);
    }
  };

  const executeAiDirective = async () => {
    if (!aiGoal.trim() || isExecuting) return;
    const goalText = aiGoal;
    setAiGoal('');
    setChatHistory(prev => [...prev, { sender: 'user', text: goalText }]);
    setIsExecuting(true);
    
    const devId = selectedDevice === 'pc' ? 'pc_windows_host' : 'phone_android_node';
    const targetModel = PROVIDER_INFO[llmProvider]?.model;

    try {
      const isLocal = isLocalServer();
      const endpoint = isLocal
        ? `${serverUrl}/api/${selectedDevice === 'pc' ? 'pc' : 'mobile'}/agent`
        : `${serverUrl}/api/device/${devId}/action`;

      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          action: 'goal', 
          type: 'goal', 
          goal: goalText, 
          provider: llmProvider, 
          model: targetModel,
          model_name: targetModel,
          api_key: apiKey 
        })
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
          setChatHistory(prev => [...prev, { sender: 'agent', text: data.message || `Mission dispatched. Task ID: ${data.task_id}` }]);
        }
      } else {
        const errMsg = data.error || data.message || data.output || 'Failed to dispatch mission';
        setChatHistory(prev => [...prev, { sender: 'agent', text: `Error: ${errMsg}` }]);
      }
    } catch (err) {
      setChatHistory(prev => [...prev, { sender: 'agent', text: `Error: Failed to reach agent service (${err.message || 'Connection error'})` }]);
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
    dataChannel.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'chat') {
          setSessionChatHistory(prev => [...prev, data]);
        }
      } catch (err) {}
    };

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
    if (localAudioStream.current) {
      localAudioStream.current.getTracks().forEach(t => t.stop());
      localAudioStream.current = null;
    }
    setAudioStreamActive(false);
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

  const sendHostWebRTCSignal = async (client_id, type, payload) => {
    try {
      await fetch(`${serverUrl}/api/webrtc/signal`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${authToken}` },
        body: JSON.stringify({ target_id: client_id, sender_id: deviceCode, type, payload })
      });
    } catch (e) {}
  };

  const startHostWebRTCSession = async () => {
    webrtcPollInterval.current = setInterval(async () => {
      try {
        const res = await fetch(`${serverUrl}/api/webrtc/poll?target_id=${deviceCode}`, {
          headers: { 'Authorization': `Bearer ${authToken}` }
        });
        const data = await res.json();
        if (data.signals && data.signals.length > 0) {
          for (const sig of data.signals) {
            if (sig.type === 'offer' && !peerConnection.current) {
              clearInterval(webrtcPollInterval.current);
              acceptOffer(sig.sender, sig.payload);
              break;
            } else if (sig.type === 'ice' && peerConnection.current) {
              await peerConnection.current.addIceCandidate(new RTCIceCandidate(sig.payload));
            }
          }
        }
      } catch (e) {}
    }, 2000);
  };

  const acceptOffer = async (client_id, offerPayload) => {
    try {
      const configuration = { iceServers: [{ urls: 'stun:stun.l.google.com:19302' }] };
      const pc = new RTCPeerConnection(configuration);
      peerConnection.current = pc;
      
      pc.ondatachannel = (event) => {
        dataChannel.current = event.channel;
        dataChannel.current.onmessage = (e) => {
          try {
            const data = JSON.parse(e.data);
            if (data.type === 'chat') {
              setSessionChatHistory(prev => [...prev, data]);
            }
          } catch (err) {}
        };
      };

      pc.onicecandidate = async (event) => {
        if (event.candidate) {
          await sendHostWebRTCSignal(client_id, 'ice', event.candidate);
        }
      };

      const stream = await navigator.mediaDevices.getDisplayMedia({ video: true, audio: false });
      stream.getTracks().forEach(track => pc.addTrack(track, stream));

      await pc.setRemoteDescription(new RTCSessionDescription(offerPayload));
      const answer = await pc.createAnswer();
      await pc.setLocalDescription(answer);
      
      await sendHostWebRTCSignal(client_id, 'answer', answer);
      
      webrtcPollInterval.current = setInterval(async () => {
        try {
          const res = await fetch(`${serverUrl}/api/webrtc/poll?target_id=${deviceCode}`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
          });
          const data = await res.json();
          if (data.signals) {
            for (const sig of data.signals) {
              if (sig.sender === client_id && sig.type === 'ice') {
                await pc.addIceCandidate(new RTCIceCandidate(sig.payload));
              }
            }
          }
        } catch (e) {}
      }, 2000);
    } catch (e) {
      console.warn("Failed to accept offer", e);
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
          } else if (sig.type === 'chat') {
            setSessionChatHistory(prev => [...prev, sig.payload]);
          }
        }
      }
    } catch (e) {}
  };

  const toggleAudioChannel = async () => {
    try {
      if (audioStreamActive) {
        if (localAudioStream.current) {
          localAudioStream.current.getTracks().forEach(t => t.stop());
          localAudioStream.current = null;
        }
        setAudioStreamActive(false);
      } else {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        localAudioStream.current = stream;
        if (peerConnection.current) {
          stream.getAudioTracks().forEach(track => {
            peerConnection.current.addTrack(track, stream);
          });
        }
        setAudioStreamActive(true);
      }
    } catch (err) {
      console.warn("Audio toggle failed:", err);
    }
  };

  const sendSessionChatMessage = async () => {
    if (!sessionChatMessage.trim()) return;
    const msg = {
      type: 'chat',
      sender: deviceCode,
      text: sessionChatMessage.trim(),
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    setSessionChatHistory(prev => [...prev, msg]);
    setSessionChatMessage('');

    if (dataChannel.current && dataChannel.current.readyState === 'open') {
      try {
        dataChannel.current.send(JSON.stringify(msg));
      } catch (e) {}
    } else {
      await sendWebRTCSignal('chat', msg);
    }
  };

  const handleViewportTouchStart = (e) => {
    if (e.touches.length === 2) {
      const dx = e.touches[0].clientX - e.touches[1].clientX;
      const dy = e.touches[0].clientY - e.touches[1].clientY;
      pinchStartDist.current = Math.hypot(dx, dy);
    } else if (e.touches.length === 1) {
      setTouchStartPos({ x: e.touches[0].clientX, y: e.touches[0].clientY });
    }
  };

  const handleViewportTouchMove = (e) => {
    if (e.touches.length === 2 && pinchStartDist.current) {
      const dx = e.touches[0].clientX - e.touches[1].clientX;
      const dy = e.touches[0].clientY - e.touches[1].clientY;
      const currentDist = Math.hypot(dx, dy);
      const ratio = currentDist / pinchStartDist.current;
      setViewportZoom(prev => Math.min(3.0, Math.max(0.6, prev * (ratio > 1 ? 1.03 : 0.97))));
      pinchStartDist.current = currentDist;
    }
  };

  const handleViewportTouchEnd = async (e) => {
    if (controlPermission === 'view_only') {
      setTouchStartPos(null);
      pinchStartDist.current = null;
      return;
    }

    if (!viewportRef.current || e.changedTouches.length === 0) {
      pinchStartDist.current = null;
      return;
    }
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
        pinchStartDist.current = null;
        return;
      }
    }
    setTouchStartPos(null);
    pinchStartDist.current = null;

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
                style={styles.dropdownItem} 
                onMouseEnter={e => e.target.style.background = '#27272a'} 
                onMouseLeave={e => e.target.style.background = 'transparent'}
                onClick={() => { setCurrentView('support'); setMenuOpen(false); }}
              >
                ❓ Support & FAQ
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
      {/* Top Session Control Bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px', flexWrap: 'wrap', gap: '10px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
          <button style={{ background: '#27272a', color: '#fff', border: 'none', padding: '6px 12px', borderRadius: '6px', cursor: 'pointer', fontSize: '13px' }} onClick={() => setCurrentView('connect')}>← Leave</button>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '14px', fontWeight: '600' }}>Host: <span style={{ color: '#60a5fa' }}>{targetCode}</span></span>
            <span style={{ fontSize: '11px', color: rtcConnectionState === 'connected' ? '#10b981' : '#f59e0b', padding: '2px 8px', background: 'rgba(255,255,255,0.05)', borderRadius: '12px', border: `1px solid ${rtcConnectionState === 'connected' ? 'rgba(16,185,129,0.3)' : 'rgba(245,158,11,0.3)'}` }}>
              {rtcConnectionState === 'connected' ? `● WebRTC (${sessionLatency}ms)` : '● Fallback Relay'}
            </span>
          </div>
        </div>

        {/* Multi-Device F3 Toolbar */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
          {/* Permission Mode Selector */}
          <div style={{ display: 'flex', background: '#18181b', borderRadius: '8px', padding: '2px', border: '1px solid #27272a' }}>
            <button 
              style={{ padding: '4px 8px', fontSize: '11px', border: 'none', borderRadius: '6px', cursor: 'pointer', background: controlPermission === 'view_only' ? '#3b82f6' : 'transparent', color: controlPermission === 'view_only' ? '#fff' : '#a1a1aa' }}
              onClick={() => setControlPermission('view_only')}
            >
              👁️ View
            </button>
            <button 
              style={{ padding: '4px 8px', fontSize: '11px', border: 'none', borderRadius: '6px', cursor: 'pointer', background: controlPermission === 'interactive' ? '#3b82f6' : 'transparent', color: controlPermission === 'interactive' ? '#fff' : '#a1a1aa' }}
              onClick={() => setControlPermission('interactive')}
            >
              🖱️ Control
            </button>
            <button 
              style={{ padding: '4px 8px', fontSize: '11px', border: 'none', borderRadius: '6px', cursor: 'pointer', background: controlPermission === 'admin' ? '#ef4444' : 'transparent', color: controlPermission === 'admin' ? '#fff' : '#a1a1aa' }}
              onClick={() => setControlPermission('admin')}
            >
              🛡️ Admin
            </button>
          </div>

          {/* Audio/Voice Stream Toggle */}
          <button 
            style={{ padding: '6px 10px', fontSize: '12px', borderRadius: '6px', cursor: 'pointer', border: '1px solid #27272a', background: audioStreamActive ? 'rgba(16,185,129,0.2)' : '#18181b', color: audioStreamActive ? '#10b981' : '#a1a1aa' }}
            onClick={toggleAudioChannel}
            title="Two-way audio/voice stream"
          >
            {audioStreamActive ? '🎙️ Mic Active' : '🎙️ Mic Off'}
          </button>

          {/* Zoom Controls */}
          <div style={{ display: 'flex', alignItems: 'center', background: '#18181b', borderRadius: '6px', border: '1px solid #27272a', padding: '2px 6px' }}>
            <button style={{ background: 'none', border: 'none', color: '#a1a1aa', cursor: 'pointer', padding: '2px 6px', fontSize: '13px' }} onClick={() => setViewportZoom(z => Math.max(0.6, z - 0.15))}>-</button>
            <span style={{ fontSize: '11px', color: '#e4e4e7', minWidth: '36px', textAlign: 'center' }}>{Math.round(viewportZoom * 100)}%</span>
            <button style={{ background: 'none', border: 'none', color: '#a1a1aa', cursor: 'pointer', padding: '2px 6px', fontSize: '13px' }} onClick={() => setViewportZoom(z => Math.min(3.0, z + 0.15))}>+</button>
          </div>

          {/* In-Session Chat Drawer Toggle */}
          <button 
            style={{ padding: '6px 10px', fontSize: '12px', borderRadius: '6px', cursor: 'pointer', border: '1px solid #27272a', background: sessionChatOpen ? 'rgba(59,130,246,0.2)' : '#18181b', color: sessionChatOpen ? '#60a5fa' : '#a1a1aa' }}
            onClick={() => setSessionChatOpen(!sessionChatOpen)}
          >
            💬 Chat {sessionChatHistory.length > 1 && `(${sessionChatHistory.length})`}
          </button>

          {/* Hotkey Shortcuts */}
          {controlPermission !== 'view_only' && (
            <div style={{ display: 'flex', gap: '4px' }}>
              <button style={{ padding: '6px 8px', background: '#18181b', border: '1px solid #27272a', color: '#a1a1aa', borderRadius: '6px', cursor: 'pointer', fontSize: '11px' }}>Win+D</button>
              <button style={{ padding: '6px 8px', background: '#18181b', border: '1px solid #27272a', color: '#a1a1aa', borderRadius: '6px', cursor: 'pointer', fontSize: '11px' }}>Esc</button>
            </div>
          )}
        </div>
      </div>
      
      {/* Main Viewport + Chat Drawer Layout */}
      <div style={{ flex: 1, display: 'flex', gap: '12px', overflow: 'hidden', minHeight: 0 }}>
        <div 
          ref={viewportRef} 
          onClick={handleViewportTouchEnd}
          onTouchStart={handleViewportTouchStart}
          onTouchMove={handleViewportTouchMove}
          onTouchEnd={handleViewportTouchEnd}
          style={{
            ...styles.canvasWrapper,
            touchAction: 'none',
            flex: 1,
            position: 'relative'
          }}
        >
          <div style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', transform: `scale(${viewportZoom})`, transformOrigin: 'center center', transition: 'transform 0.1s ease-out' }}>
            <video 
              ref={videoRef}
              autoPlay 
              playsInline 
              style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', objectFit: 'contain', zIndex: rtcConnectionState === 'connected' ? 2 : 0 }} 
            />
            <img 
              src={isLocalServer() ? `${serverUrl}${selectedDevice === 'pc' ? '/api/pc/screen' : '/api/screenshot'}?t=${frameTimestamp}` : `${serverUrl}/api/device/${targetCode || (selectedDevice === 'pc' ? 'pc_windows_host' : 'phone_android_node')}/frame?t=${frameTimestamp}`}
              alt="Remote Viewport Fallback" 
              onError={(e) => { e.target.src = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='400' height='300' viewBox='0 0 400 300'><rect width='100%' height='100%' fill='%23121215'/><text x='50%' y='50%' fill='%2371717a' font-family='sans-serif' font-size='14' text-anchor='middle'>Awaiting Remote Display Buffer...</text></svg>"; }}
              style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain', cursor: controlPermission === 'view_only' ? 'default' : 'crosshair', userSelect: 'none', position: 'relative', zIndex: 1 }} 
            />
          </div>
          {controlPermission === 'view_only' && (
            <div style={{ position: 'absolute', top: 12, left: 12, background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(4px)', padding: '4px 10px', borderRadius: '6px', fontSize: '11px', color: '#fbbf24', zIndex: 10 }}>
              👁️ View-Only Mode Active (Inputs Disabled)
            </div>
          )}
        </div>

        {/* P2P In-Session Text Chat (F3) */}
        {sessionChatOpen && (
          <div style={{ width: isMobile ? '100%' : '300px', background: '#121215', border: '1px solid #27272a', borderRadius: '12px', display: 'flex', flexDirection: 'column', overflow: 'hidden', flexShrink: 0 }}>
            <div style={{ padding: '12px 16px', borderBottom: '1px solid #27272a', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ fontSize: '13px', fontWeight: '600', color: '#e4e4e7' }}>In-Session Comms</div>
              <button style={{ background: 'none', border: 'none', color: '#71717a', cursor: 'pointer', fontSize: '14px' }} onClick={() => setSessionChatOpen(false)}>✕</button>
            </div>
            <div style={{ flex: 1, padding: '12px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {sessionChatHistory.map((m, idx) => (
                <div key={idx} style={{ background: m.sender === deviceCode ? 'rgba(59,130,246,0.15)' : '#18181b', border: '1px solid rgba(255,255,255,0.05)', borderRadius: '8px', padding: '8px 10px', fontSize: '12px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '3px' }}>
                    <span style={{ fontWeight: '600', color: m.sender === deviceCode ? '#60a5fa' : '#a1a1aa', fontSize: '11px' }}>{m.sender === deviceCode ? 'You' : m.sender}</span>
                    <span style={{ color: '#71717a', fontSize: '10px' }}>{m.time}</span>
                  </div>
                  <div style={{ color: '#f4f4f5', wordBreak: 'break-word' }}>{m.text}</div>
                </div>
              ))}
            </div>
            <div style={{ padding: '10px', borderTop: '1px solid #27272a', display: 'flex', gap: '6px' }}>
              <input 
                type="text" 
                placeholder="Message remote host..." 
                value={sessionChatMessage} 
                onChange={e => setSessionChatMessage(e.target.value)}
                onKeyDown={e => { if (e.key === 'Enter') sendSessionChatMessage(); }}
                style={{ ...styles.input, marginBottom: 0, padding: '8px 10px', fontSize: '12px', flex: 1 }} 
              />
              <button 
                onClick={sendSessionChatMessage}
                style={{ ...styles.button, width: 'auto', padding: '0 14px', fontSize: '12px' }}
              >
                Send
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );

  const renderModelConfig = () => {
    const currentMeta = PROVIDER_INFO[llmProvider] || PROVIDER_INFO.gemini;

    return (
      <div style={styles.loginContainer}>
        <div style={{ ...styles.loginCard, width: '460px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
            <h2 style={{ margin: 0, fontSize: '20px' }}>Model Configuration</h2>
            <button 
              onClick={() => setCurrentView('chat')}
              style={{ background: 'transparent', border: 'none', color: '#a1a1aa', cursor: 'pointer', fontSize: '18px', padding: '4px' }}
              title="Close"
            >
              ✕
            </button>
          </div>
          <p style={{ color: '#a1a1aa', fontSize: '13px', marginBottom: '20px' }}>
            Configure your local or cloud LLM provider for autonomous AI capabilities.
          </p>
          
          <label style={{ display: 'block', marginBottom: '6px', fontSize: '13px', color: '#e4e4e7', fontWeight: '500' }}>
            AI Provider
          </label>
          <select 
            style={{ ...styles.input, WebkitAppearance: 'none', background: '#18181b', color: '#fff', cursor: 'pointer' }} 
            value={llmProvider} 
            onChange={e => {
              setLlmProvider(e.target.value);
              setConfigSaveStatus('');
            }}
          >
            <option style={{ background: '#18181b', color: '#fff' }} value="groq">Groq (Llama 3.3 - Fast & Free)</option>
            <option style={{ background: '#18181b', color: '#fff' }} value="gemini">Google (Gemini 2.5 Flash / Pro)</option>
            <option style={{ background: '#18181b', color: '#fff' }} value="openai">OpenAI (GPT-4o / GPT-4o-mini)</option>
            <option style={{ background: '#18181b', color: '#fff' }} value="anthropic">Anthropic (Claude 3.5 Sonnet)</option>
            <option style={{ background: '#18181b', color: '#fff' }} value="deepseek">DeepSeek (V3 / R1)</option>
            <option style={{ background: '#18181b', color: '#fff' }} value="openrouter">OpenRouter (Unified Gateway)</option>
            <option style={{ background: '#18181b', color: '#fff' }} value="ollama">Ollama (Local Offline Inference)</option>
          </select>
          
          <label style={{ display: 'block', marginBottom: '6px', fontSize: '13px', color: '#e4e4e7', fontWeight: '500' }}>
            {llmProvider === 'ollama' ? 'Local Model Name' : 'API Key'}
          </label>
          {llmProvider === 'ollama' ? (
            <input 
              style={styles.input} 
              type="text" 
              placeholder="e.g. llama3.2, mistral, qwen2.5" 
              value={apiKey} 
              onChange={e => setApiKey(e.target.value)} 
            />
          ) : (
            <input 
              style={styles.input} 
              type="password" 
              placeholder={`Paste your ${currentMeta.name} API key...`} 
              value={apiKey} 
              onChange={e => setApiKey(e.target.value)} 
            />
          )}
          
          {/* Direct API Key Retrieval Link Box */}
          <div style={{
            marginTop: '-4px',
            marginBottom: '18px',
            padding: '12px 14px',
            background: 'rgba(59, 130, 246, 0.08)',
            border: '1px solid rgba(59, 130, 246, 0.25)',
            borderRadius: '8px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '8px' }}>
              <span style={{ color: '#a1a1aa', fontSize: '12px', fontWeight: '500' }}>
                {llmProvider === 'ollama' ? 'Get local engine:' : `Need a ${currentMeta.name} key?`}
              </span>
              <a 
                href={currentMeta.keyUrl} 
                target="_blank" 
                rel="noopener noreferrer"
                style={{
                  color: '#60a5fa',
                  textDecoration: 'none',
                  fontWeight: '600',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '4px',
                  fontSize: '12px'
                }}
                onMouseEnter={e => e.currentTarget.style.textDecoration = 'underline'}
                onMouseLeave={e => e.currentTarget.style.textDecoration = 'none'}
              >
                🔑 {currentMeta.buttonText} ↗
              </a>
            </div>
            <div style={{ marginTop: '6px', fontSize: '11px', color: '#71717a', lineHeight: '1.4' }}>
              {currentMeta.description}
            </div>
            <div style={{ marginTop: '6px', fontSize: '11px', color: '#94a3b8' }}>
              Direct Link:{' '}
              <a 
                href={currentMeta.keyUrl} 
                target="_blank" 
                rel="noopener noreferrer"
                style={{ color: '#38bdf8', wordBreak: 'break-all' }}
              >
                {currentMeta.keyUrl}
              </a>
            </div>
          </div>

          {configSaveStatus && (
            <div style={{
              background: 'rgba(16, 185, 129, 0.12)',
              border: '1px solid rgba(16, 185, 129, 0.3)',
              color: '#34d399',
              padding: '10px 12px',
              borderRadius: '8px',
              fontSize: '12px',
              marginBottom: '16px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}>
              ✓ {configSaveStatus}
            </div>
          )}
          
          <button 
            style={{ ...styles.button, opacity: isSavingConfig ? 0.7 : 1 }} 
            disabled={isSavingConfig}
            onClick={handleSaveModelConfig}
          >
            {isSavingConfig ? 'Saving & Syncing...' : 'Save Configuration'}
          </button>

          {/* Direct link below form */}
          <div style={{ marginTop: '14px', textAlign: 'center' }}>
            <a 
              href={currentMeta.keyUrl} 
              target="_blank" 
              rel="noopener noreferrer"
              style={{ color: '#71717a', fontSize: '11px', textDecoration: 'none' }}
              onMouseEnter={e => e.currentTarget.style.color = '#a1a1aa'}
              onMouseLeave={e => e.currentTarget.style.color = '#71717a'}
            >
              Get {currentMeta.name} API Key directly at {currentMeta.label}
            </a>
          </div>
        </div>
      </div>
    );
  };

  const handleUpgrade = async () => {
    setIsUpgrading(true);
    try {
      const res = await fetch(`${serverUrl}/api/stripe/create-checkout`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ plan_id: 'pro', email: 'customer@example.com' })
      });
      const data = await res.json();
      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      }
    } catch (err) {
      console.error(err);
    }
    setIsUpgrading(false);
  };

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
        
        {billingMath && (
          <div style={{ background: '#27272a', padding: '16px', borderRadius: '8px', marginBottom: '24px', fontSize: '13px', color: '#a1a1aa' }}>
            <div style={{ color: '#fff', marginBottom: '8px', fontWeight: 'bold' }}>Live Resource Calculation</div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
              <span>AI Token Cost:</span>
              <span>${billingMath.ai_operating_cost.toFixed(2)}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
              <span>Bandwidth/TURN:</span>
              <span>${billingMath.turn_operating_cost.toFixed(2)}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderTop: '1px solid #3f3f46', paddingTop: '4px', marginTop: '4px', color: '#fff', fontWeight: 'bold' }}>
              <span>Total Cost:</span>
              <span>${billingMath.total_operating_cost.toFixed(2)}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '8px', color: '#10b981' }}>
              <span>PRO Savings:</span>
              <span>${billingMath.monthly_savings.toFixed(2)}/mo vs competitors</span>
            </div>
          </div>
        )}

        {userPlan === 'free' && (
          <button onClick={handleUpgrade} disabled={isUpgrading} style={{...styles.button, background: '#10b981', marginBottom: '12px'}}>
            {isUpgrading ? 'Redirecting...' : 'Upgrade to PRO ($12/mo)'}
          </button>
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
          {usageHistory.length === 0 ? (
            <div style={{ color: '#71717a', fontSize: '14px', textAlign: 'center', padding: '20px 0' }}>No history found.</div>
          ) : (
            usageHistory.map((item) => (
              <div key={item.id} style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 0', borderBottom: '1px solid #27272a' }}>
                <div>
                  <div style={{ fontSize: '14px', color: '#e4e4e7' }}>{item.action}</div>
                  <div style={{ fontSize: '11px', color: '#60a5fa' }}>{item.device}</div>
                </div>
                <div style={{ fontSize: '12px', color: '#71717a' }}>{item.time}</div>
              </div>
            ))
          )}
        </div>
        
        <button style={{...styles.button, background: '#27272a', color: '#fff'}} onClick={() => setCurrentView('chat')}>Back to Dashboard</button>
      </div>
    </div>
  );

  const optimizeImage = (file) => {
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const img = new Image();
        img.onload = () => {
          const canvas = document.createElement('canvas');
          let width = img.width;
          let height = img.height;
          const maxDim = 800;
          if (width > height && width > maxDim) {
            height *= maxDim / width;
            width = maxDim;
          } else if (height > maxDim) {
            width *= maxDim / height;
            height = maxDim;
          }
          canvas.width = width;
          canvas.height = height;
          const ctx = canvas.getContext('2d');
          ctx.drawImage(img, 0, 0, width, height);
          resolve(canvas.toDataURL('image/jpeg', 0.6));
        };
        img.src = e.target.result;
      };
      reader.readAsDataURL(file);
    });
  };

  const handleSupportSubmit = async (e) => {
    e.preventDefault();
    if (!supportName || !supportEmail || !supportMessage) {
      setSupportStatus('Please fill all fields.');
      return;
    }
    if (supportImages.length > 5) {
      setSupportStatus('Maximum 5 images allowed.');
      return;
    }
    
    setSupportStatus('Optimizing images and sending...');
    
    try {
      const optimizedImages = await Promise.all(
        Array.from(supportImages).map(file => optimizeImage(file))
      );

      const res = await fetch(`${serverUrl}/api/support/submit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          name: supportName, 
          email: supportEmail, 
          message: supportMessage,
          images: optimizedImages
        })
      });
      const data = await res.json();
      if (data.success) {
        setSupportStatus('Message sent successfully! We will get back to you soon.');
        setSupportName('');
        setSupportEmail('');
        setSupportMessage('');
        setSupportImages([]);
      } else {
        setSupportStatus(`Error: ${data.error || 'Failed to send message.'}`);
      }
    } catch (err) {
      setSupportStatus('Error connecting to server.');
    }
    setTimeout(() => setSupportStatus(''), 5000);
  };

  const faqs = [
    { q: 'How does the AI agent connect to my device?', a: 'It uses WebRTC to establish a secure peer-to-peer connection for streaming screen data and input actions.' },
    { q: 'Is my data secure?', a: 'Yes, all actions and screen streams are transmitted securely over WebRTC with encryption.' },
    { q: 'Can I use this on mobile?', a: 'Yes, Pentactopus supports both PC (Windows) and Android mobile nodes.' },
    { q: 'What is the limit on the Free plan?', a: 'The free plan allows connection to 1 device on a local network mesh.' }
  ];

  const renderSupport = () => (
    <div style={{...styles.loginContainer, alignItems: 'flex-start', paddingTop: '40px', overflowY: 'auto'}}>
      <div style={{...styles.loginCard, width: '600px', maxWidth: '90%'}}>
        <h2 style={{ margin: '0 0 8px 0', fontSize: '24px', fontWeight: '600' }}>Support & FAQ</h2>
        <p style={{ color: '#a1a1aa', fontSize: '14px', marginBottom: '32px' }}>Find answers to common questions or contact our support team.</p>
        
        <div style={{ marginBottom: '32px' }}>
          <h3 style={{ fontSize: '18px', marginBottom: '16px', color: '#fff' }}>Frequently Asked Questions</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {faqs.map((faq, idx) => (
              <div key={idx} style={{ background: '#18181b', borderRadius: '8px', border: '1px solid #27272a', overflow: 'hidden' }}>
                <button 
                  style={{ width: '100%', padding: '16px', background: 'transparent', border: 'none', color: '#e4e4e7', fontSize: '15px', fontWeight: '500', textAlign: 'left', cursor: 'pointer', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
                  onClick={() => setExpandedFaq(expandedFaq === idx ? null : idx)}
                >
                  {faq.q}
                  <span style={{ color: '#a1a1aa' }}>{expandedFaq === idx ? '−' : '+'}</span>
                </button>
                {expandedFaq === idx && (
                  <div style={{ padding: '0 16px 16px 16px', color: '#a1a1aa', fontSize: '14px', lineHeight: '1.5' }}>
                    {faq.a}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        <div>
          <h3 style={{ fontSize: '18px', marginBottom: '16px', color: '#fff' }}>Contact Us / Report an Issue</h3>
          {supportStatus && (
            <div style={{ background: supportStatus.includes('success') ? 'rgba(16, 185, 129, 0.1)' : supportStatus.includes('Sending') ? 'rgba(59, 130, 246, 0.1)' : 'rgba(239, 68, 68, 0.1)', color: supportStatus.includes('success') ? '#10b981' : supportStatus.includes('Sending') ? '#60a5fa' : '#ef4444', padding: '12px', borderRadius: '8px', fontSize: '14px', marginBottom: '16px', border: `1px solid ${supportStatus.includes('success') ? 'rgba(16, 185, 129, 0.2)' : supportStatus.includes('Sending') ? 'rgba(59, 130, 246, 0.2)' : 'rgba(239, 68, 68, 0.2)'}` }}>
              {supportStatus}
            </div>
          )}
          <form onSubmit={handleSupportSubmit}>
            <input style={styles.input} type="text" placeholder="Your Name" value={supportName} onChange={e => setSupportName(e.target.value)} />
            <input style={styles.input} type="email" placeholder="Your Email" value={supportEmail} onChange={e => setSupportEmail(e.target.value)} />
            <textarea 
              style={{...styles.input, height: '120px', resize: 'vertical', fontFamily: 'inherit'}} 
              placeholder="How can we help you? Describe your issue, suggestion or question..." 
              value={supportMessage} 
              onChange={e => setSupportMessage(e.target.value)} 
            />
            <div style={{ marginBottom: '16px' }}>
              <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', color: '#a1a1aa' }}>
                Attach Images (Optional, max 5)
              </label>
              <input 
                type="file" 
                multiple 
                accept="image/*"
                onChange={e => {
                  const files = Array.from(e.target.files);
                  if (files.length > 5) {
                    setSupportStatus('Maximum 5 images allowed.');
                  } else {
                    setSupportStatus('');
                    setSupportImages(files);
                  }
                }}
                style={{
                  width: '100%',
                  padding: '10px',
                  background: '#18181b',
                  border: '1px solid #27272a',
                  borderRadius: '6px',
                  color: '#e4e4e7',
                  fontSize: '14px'
                }} 
              />
              {supportImages.length > 0 && (
                <div style={{ marginTop: '8px', fontSize: '13px', color: '#10b981' }}>
                  {supportImages.length} image(s) selected
                </div>
              )}
            </div>
            <button style={{...styles.button, padding: '14px', fontSize: '15px'}} type="submit">Submit Request</button>
          </form>
        </div>
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
      {currentView === 'support' && renderSupport()}
    </div>
  );
}
