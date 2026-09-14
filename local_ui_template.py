LOCAL_UI_HTML = '''<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Pentactopus PC Agent</title>
  <style>
    :root { --bg: #000; --panel: #09090b; --border: #27272a; --text: #e4e4e7; --accent: #3b82f6; }
    body { font-family: -apple-system, system-ui, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 24px; }
    .header { display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--border); padding-bottom: 16px; margin-bottom: 24px; }
    .status-dot { height: 8px; width: 8px; background: #10b981; border-radius: 50%; display: inline-block; margin-right: 8px; box-shadow: 0 0 8px rgba(16, 185, 129, 0.6); }
    .card { background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 20px; margin-bottom: 16px; }
    .btn { background: var(--accent); color: #fff; border: 1px solid rgba(255,255,255,0.1); padding: 8px 16px; border-radius: 6px; cursor: pointer; font-weight: 500; font-size: 13px; }
    .btn:hover { background: #2563eb; }
    .btn-secondary { background: #18181b; color: #e4e4e7; border: 1px solid var(--border); }
    .btn-secondary:hover { background: #27272a; }
    .terminal { background: #000; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; color: #34d399; padding: 16px; border-radius: 6px; height: 180px; overflow-y: auto; font-size: 12px; line-height: 1.6; border: 1px solid var(--border); }
    input[type="text"] { width: 100%; background: #000; border: 1px solid var(--border); color: #fff; padding: 12px; border-radius: 6px; margin-bottom: 12px; box-sizing: border-box; font-size: 13px; }
    input:focus { outline: none; border-color: var(--accent); }
    h3 { margin-top: 0; font-size: 15px; margin-bottom: 16px; font-weight: 600; color: #fff; }
  </style>
</head>
<body>
  <div class="header">
    <div style="display:flex; align-items:center; gap:12px;">
      <svg width="28" height="28" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="16" cy="16" r="5" fill="#3b82f6" stroke="#60a5fa" stroke-width="1.5"/>
        <path d="M16 11V7.5M20 13.5L23.5 13M18.5 19.5L20.5 23M13.5 19.5L11.5 23M12 13.5L8.5 13" stroke="#475569" stroke-width="1.5" stroke-linecap="round"/>
      </svg>
      <h2 style="margin:0; font-size:20px; font-weight: 700;">Pentactopus PC Agent</h2>
    </div>
    <div style="display:flex; align-items:center;">
      <span class="status-dot"></span><span style="font-size:13px; color:#a1a1aa; font-weight:500;">Daemon Active</span>
    </div>
  </div>

  <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
    <div class="card">
      <h3>Local Autonomous Agent</h3>
      <div style="font-size:12px; color:#a1a1aa; margin-bottom:16px;">Instruct the AI to perform actions directly on this Windows desktop.</div>
      <input type="text" id="ai-prompt" placeholder="e.g. Open Notepad and write a greeting message...">
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <span style="font-size:11px; color:#71717a; background: #000; padding: 4px 8px; border-radius: 4px; border: 1px solid var(--border);">Model: Gemini 2.5 Flash</span>
        <button class="btn" onclick="runAgent()" id="run-btn">Execute Task</button>
      </div>
    </div>

    <div class="card">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
        <h3 style="margin:0;">Android Device Link</h3>
        <button class="btn btn-secondary btn-sm" onclick="scanDevices()" style="padding:4px 8px; font-size:11px;">Refresh</button>
      </div>
      <div style="font-size:12px; color:#a1a1aa; margin-bottom:16px;">Connect your phone via USB or Wi-Fi to mirror it securely to this workstation.</div>
      <div style="display:flex; gap:10px;">
        <button class="btn btn-secondary" onclick="startMirror()" style="flex:1;">Launch Viewport</button>
      </div>
      <div id="device-status" style="margin-top:16px; font-size:12px; color:#71717a; background: #000; padding: 8px; border-radius: 4px; border: 1px solid var(--border);">Checking USB connections...</div>
    </div>
  </div>

  <h3 style="font-size:12px; color:#71717a; text-transform:uppercase; margin-top:24px; margin-bottom:10px; letter-spacing:0.5px;">Daemon Event Log</h3>
  <div class="terminal" id="terminal">
    [SYS] Pentactopus Desktop Agent Initialized.<br>
    [SYS] Awaiting cloud commands or local input...<br>
  </div>

  <script>
    function log(msg) {
      const term = document.getElementById('terminal');
      const time = new Date().toLocaleTimeString('en-US', { hour12: false });
      term.innerHTML += `<div><span style="color:#71717a;">[${time}]</span> ${msg}</div>`;
      term.scrollTop = term.scrollHeight;
    }

    async function runAgent() {
      const prompt = document.getElementById('ai-prompt').value.trim();
      if(!prompt) return;
      
      const btn = document.getElementById('run-btn');
      btn.innerText = 'Running...';
      btn.disabled = true;
      
      log(`<span style="color:#60a5fa;">[AGENT] Dispatched: ${prompt}</span>`);
      
      try {
        const res = await fetch('/api/run-agent', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({goal: prompt})
        });
        const data = await res.json();
        
        if (data.success) {
          log(`<span style="color:#10b981;">[AGENT] Task completed successfully.</span>`);
        } else {
          log(`<span style="color:#ef4444;">[AGENT] Error: ${data.error || 'Task failed'}</span>`);
        }
        
        if (data.output) {
           log(`<span style="color:#a1a1aa;">${data.output}</span>`);
        }
      } catch(err) {
        log(`<span style="color:#ef4444;">[SYS] Network error communicating with local daemon.</span>`);
      } finally {
        btn.innerText = 'Execute Task';
        btn.disabled = false;
        document.getElementById('ai-prompt').value = '';
      }
    }

    async function scanDevices() {
      log('Scanning for connected Android endpoints...');
      try {
        const res = await fetch('/api/status');
        const data = await res.json();
        const active = data.devices.filter(d => d.state === 'device');
        const statusBox = document.getElementById('device-status');
        
        if (active.length > 0) {
          log(`Found ${active.length} active device(s).`);
          statusBox.innerHTML = `<span style="color:#10b981;">● ${active[0].model || active[0].serial} Connected</span>`;
        } else {
          log('No authorized devices detected.');
          statusBox.innerHTML = 'No devices detected.';
        }
      } catch(err) {
        log('<span style="color:#ef4444;">[SYS] Error scanning ADB backend.</span>');
      }
    }

    async function startMirror() {
      log('Requesting high-performance viewport...');
      try {
        const res = await fetch('/api/scrcpy', { method: 'POST' });
        const data = await res.json();
        if (data.success) {
          log('<span style="color:#10b981;">[VIEWPORT] ' + data.message + '</span>');
        } else {
          log('<span style="color:#ef4444;">[VIEWPORT] Error: ' + data.error + '</span>');
        }
      } catch(err) {
        log('<span style="color:#ef4444;">[SYS] Failed to launch viewport process.</span>');
      }
    }

    setTimeout(scanDevices, 1000);
  </script>
</body>
</html>'''
