# System Architecture: AI-Android-Agent

## 1. Overview
The **AI-Android-Agent** enables multimodal AI models to perceive, reason about, and interact with Android operating systems over ADB and scrcpy with zero cloud emulator overhead.

## 2. Component Pipeline

```
  [Physical Android Phone]
       │
       ├─► (1) Screen Capture (screencap -p) ────────┐
       ├─► (2) UI Hierarchy Dump (uiautomator dump) ─┼─► [State Parser]
       │                                             │         │
       │                                             │         ▼
       │                                             │   [Prompt / Vision Input]
       │                                             │         │
       │                                             │         ▼
       │                                             │   [Model Provider]
       │                                             │   (Gemini / Ollama / Mock)
       │                                             │         │
       │                                             │         ▼
       │                                             │   [Structured Action JSON]
       │                                             │         │
       │                                             │         ▼
       │                                             │   [Security Allowlist & Schema Validator]
       │                                             │         │
       └─◄ (3) Safe ADB Input Dispatch ◄─────────────┘         ▼
          (input tap / swipe / text / monkey)             [Action Execution]
```

## 3. Key Design Choices
1. **Hybrid Perception (Vision + UI Tree)**:
   - Instead of pure coordinate guessing, the agent extracts exact element text, bounding boxes, and accessibility tags.
   - Saves tokens, prevents coordinate drift, and runs efficiently even on slow internet connections.
2. **Strict Security Allowlist**:
   - AI models cannot execute arbitrary shell commands.
   - Text is sanitized to avoid command injection.
   - Package launches use explicit launcher intents (`monkey -p <pkg> -c ... 1`).
3. **Low-Spec Optimization**:
   - Hardware: Optimized for low-power CPUs (e.g. Intel Pentium Silver N5000) and low RAM.
   - Video: scrcpy flags restricted to 30 FPS, 1024px maximum dimension, 2 Mbps bitrate, and no audio stream.
