# Pentactopus UX System

## 1. Design Tokens
The overarching visual theme is Matte Carbon. It is designed to feel like high-performance developer tooling rather than a generic consumer app.

**Colors**
- Global Background: `#000000`
- Panel/Card Background: `#09090b`
- Card Hover: `#121215`
- Borders: `#27272a`
- Primary Text: `#e4e4e7`
- Secondary Text: `#a1a1aa` or `#71717a`
- Accent (Brand): `#3b82f6`
- Accent (Action): `#2563eb`
- Success: `#10b981`
- Warning: `#eab308`
- Error: `#ef4444`

**Typography**
- Font Family: `Inter`, `-apple-system`, `system-ui`, `sans-serif`
- Code/Terminal: `ui-monospace`, `SFMono-Regular`, `Consolas`

## 2. Shared Components
- **Primary Button**: Background `#2563eb`, border none, text `#fff`, hover `#1d4ed8`, border-radius `6px`.
- **Secondary Button**: Background `#18181b`, border `1px solid #27272a`, text `#e4e4e7`, hover `#27272a`.
- **Cards**: Background `#09090b`, border `1px solid #27272a`, border-radius `8px`, padding `16px/20px`.
- **Inputs**: Background `#000` or `#18181b`, border `1px solid #27272a`, text `#fff`, focus border `#3b82f6`.
- **Terminal Log**: Background `#000`, text `#34d399` (success/sys) or `#60a5fa` (info), padding `16px`.

## 3. Empty & Error States
- **Empty Devices**: Show subtle `#71717a` text inside a panel: `No devices detected.`
- **Action Disabled**: Button opacity `0.5`, cursor `not-allowed`.
- **Error Banner**: Inline alert boxes (no browser alerts). Background `#ef4444` at 15% opacity, text `#ef4444`, border `1px solid rgba(239, 68, 68, 0.3)`.

## 4. Accessibility
- All text meets WCAG 2.1 AA contrast ratio (4.5:1 against dark backgrounds).
- Focus states explicitly defined (Blue `#3b82f6` border on inputs).
