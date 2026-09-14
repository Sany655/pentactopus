# Cross-Platform UX System

## 1. Platform Hierarchy & Constraints
To accelerate time-to-market while setting clear user expectations, the platform features are tiered:

- **Web (Cloud) + Windows PC Agent = Polished MVP**. These serve as the core anchors. They share exact terminology, design tokens, and functional maturity.
- **Android Client = Functional Beta**. Used primarily for remote controlling the Windows host. Streaming is polling-based (MJPEG) due to WebRTC constraints on Vercel.
- **Cloud WebRTC = Roadmap**. Real-time streaming from the cloud dashboard is visibly marked as unavailable/roadmap to prevent user frustration.
- **iOS = Roadmap**. Not part of the immediate beta launch.

## 2. Navigation Consistency
- **Terminology**: 
  - *Viewport* (Screen viewer)
  - *Daemon* (Background service)
  - *Mesh* (Connected devices network)
  - *Agent* (AI task executor)
- **Task Lifecycle**: Every AI execution across all platforms strictly follows: `Idle -> Running (disabled) -> Log Output -> Idle`.

## 3. Permissions & Security
- Admin routes are gated.
- Android warns before capturing screen (OS-level permission).
- Windows explicitly shows terminal output so users know exactly what the AI is controlling locally.
