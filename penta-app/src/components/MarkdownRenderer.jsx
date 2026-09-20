import React, { useState } from 'react';

const KEYWORDS = new Set([
  'class', 'def', 'async', 'await', 'return', 'import', 'from', 'if', 'else', 'elif',
  'try', 'except', 'finally', 'with', 'as', 'for', 'in', 'while', 'break', 'continue',
  'pass', 'raise', 'yield', 'lambda', 'assert', 'const', 'let', 'var', 'function',
  'new', 'export', 'default', 'extends', 'super', 'this', 'throw', 'catch', 'typeof',
  'instanceof', 'void', 'delete', 'switch', 'case', 'sudo', 'pip', 'npm', 'uvicorn', 'python'
]);

const TYPES = new Set([
  'BaseModel', 'Prompt', 'FastAPI', 'None', 'True', 'False', 'self', 'str', 'int',
  'float', 'bool', 'dict', 'list', 'set', 'tuple', 'Promise', 'Response', 'Request',
  'true', 'false', 'null', 'undefined', 'object', 'string', 'number', 'boolean'
]);

function highlightCodeLine(line) {
  const parts = [];
  const regex = /(#.*$|\/\/.*$|"[^"]*"|'[^']*'|`[^`]*`|@[a-zA-Z0-9_.]+|\b\d+(?:\.\d+)?\b|\b[a-zA-Z_][a-zA-Z0-9_]*\b|[^"'\`\s\w]+|\s+)/g;
  let match;
  let keyIdx = 0;

  while ((match = regex.exec(line)) !== null) {
    const val = match[0];
    keyIdx++;

    if (val.startsWith('#') || val.startsWith('//')) {
      parts.push(
        <span key={keyIdx} style={{ color: '#71717a', fontStyle: 'italic' }}>
          {val}
        </span>
      );
    } else if (val.startsWith('"') || val.startsWith("'") || val.startsWith('`')) {
      parts.push(
        <span key={keyIdx} style={{ color: '#34d399' }}>
          {val}
        </span>
      );
    } else if (val.startsWith('@')) {
      parts.push(
        <span key={keyIdx} style={{ color: '#38bdf8', fontWeight: '500' }}>
          {val}
        </span>
      );
    } else if (KEYWORDS.has(val)) {
      parts.push(
        <span key={keyIdx} style={{ color: '#c084fc', fontWeight: '600' }}>
          {val}
        </span>
      );
    } else if (TYPES.has(val)) {
      parts.push(
        <span key={keyIdx} style={{ color: '#60a5fa', fontWeight: '500' }}>
          {val}
        </span>
      );
    } else if (/^\d+(?:\.\d+)?$/.test(val)) {
      parts.push(
        <span key={keyIdx} style={{ color: '#fb923c' }}>
          {val}
        </span>
      );
    } else {
      parts.push(
        <span key={keyIdx} style={{ color: '#e2e8f0' }}>
          {val}
        </span>
      );
    }
  }

  return parts.length > 0 ? parts : line;
}

const LANG_ICONS = {
  python: '🐍',
  py: '🐍',
  javascript: '📜',
  js: '📜',
  jsx: '⚛️',
  typescript: '🔷',
  ts: '🔷',
  tsx: '⚛️',
  bash: '⚡',
  sh: '⚡',
  shell: '⚡',
  powershell: '💻',
  json: '📦',
  html: '🌐',
  css: '🎨',
  sql: '🗄️',
  yaml: '⚙️',
  yml: '⚙️'
};

export function CodeBlock({ code, language }) {
  const [copied, setCopied] = useState(false);
  const cleanLang = (language || 'code').toLowerCase().trim();
  const icon = LANG_ICONS[cleanLang] || '📄';
  const lines = code.split('\n');

  const handleCopy = (e) => {
    e.stopPropagation();
    if (navigator?.clipboard?.writeText) {
      navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div style={{ margin: '14px 0', borderRadius: '10px', overflow: 'hidden', border: '1px solid rgba(255, 255, 255, 0.1)', background: '#09090d', boxShadow: '0 8px 24px rgba(0, 0, 0, 0.4)' }}>
      {/* Code Header Bar */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '7px 14px', background: '#121218', borderBottom: '1px solid rgba(255, 255, 255, 0.08)', fontSize: '11px', color: '#94a3b8' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span>{icon}</span>
          <span style={{ fontFamily: 'Consolas, Monaco, monospace', textTransform: 'uppercase', letterSpacing: '0.6px', fontWeight: '600', color: '#cbd5e1' }}>
            {cleanLang}
          </span>
          <span style={{ fontSize: '10px', color: '#52525b' }}>• {lines.length} {lines.length === 1 ? 'line' : 'lines'}</span>
        </div>
        <button
          onClick={handleCopy}
          style={{
            background: copied ? 'rgba(16, 185, 129, 0.15)' : 'rgba(255, 255, 255, 0.06)',
            border: `1px solid ${copied ? 'rgba(16, 185, 129, 0.4)' : 'rgba(255, 255, 255, 0.1)'}`,
            color: copied ? '#34d399' : '#e4e4e7',
            fontSize: '11px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '5px',
            padding: '3px 10px',
            borderRadius: '6px',
            fontWeight: '500',
            transition: 'all 0.15s'
          }}
          onMouseEnter={e => { if (!copied) e.currentTarget.style.background = 'rgba(255, 255, 255, 0.12)'; }}
          onMouseLeave={e => { if (!copied) e.currentTarget.style.background = 'rgba(255, 255, 255, 0.06)'; }}
        >
          <span>{copied ? '✓' : '📋'}</span>
          <span>{copied ? 'Copied!' : 'Copy Code'}</span>
        </button>
      </div>

      {/* Code Body with Optional Line Numbers */}
      <div style={{ display: 'flex', overflowX: 'auto', padding: '12px 0', background: '#09090d', fontSize: '13px', lineHeight: '1.65', fontFamily: 'Consolas, Monaco, "Courier New", monospace' }}>
        {/* Line Numbers */}
        <div style={{ userSelect: 'none', padding: '0 12px 0 14px', textAlign: 'right', color: '#52525b', fontSize: '12px', borderRight: '1px solid rgba(255, 255, 255, 0.06)' }}>
          {lines.map((_, idx) => (
            <div key={idx}>{idx + 1}</div>
          ))}
        </div>

        {/* Code Content */}
        <pre style={{ margin: 0, padding: '0 16px', overflowX: 'auto', flex: 1, color: '#e2e8f0', background: 'transparent' }}>
          <code>
            {lines.map((line, idx) => (
              <div key={idx} style={{ minHeight: '21px' }}>
                {highlightCodeLine(line)}
              </div>
            ))}
          </code>
        </pre>
      </div>
    </div>
  );
}

export default function MarkdownRenderer({ content }) {
  if (!content) return null;

  // Normalize Windows CRLF to standard LF
  const normalized = String(content).replace(/\r\n/g, '\n').replace(/\r/g, '\n');

  // Split content by code fences ```(lang)?\n...```
  const parts = [];
  const regex = /```([a-zA-Z0-9_#-]*)[^\n]*\n([\s\S]*?)```/g;
  let lastIndex = 0;
  let match;

  while ((match = regex.exec(normalized)) !== null) {
    if (match.index > lastIndex) {
      parts.push({ type: 'markdown', text: normalized.substring(lastIndex, match.index) });
    }
    parts.push({ type: 'code', language: match[1] || '', code: match[2].trimEnd() });
    lastIndex = regex.lastIndex;
  }

  if (lastIndex < normalized.length) {
    parts.push({ type: 'markdown', text: normalized.substring(lastIndex) });
  }

  const renderInline = (str) => {
    const tokens = [];
    const inlineRegex = /(`[^`]+`|\*\*[^*]+\*\*|\*[^*]+\*|\[[^\]]+\]\([^)]+\))/g;
    let idx = 0;
    let m;

    while ((m = inlineRegex.exec(str)) !== null) {
      if (m.index > idx) {
        tokens.push(str.substring(idx, m.index));
      }
      const val = m[0];
      if (val.startsWith('`') && val.endsWith('`')) {
        tokens.push(
          <code key={tokens.length} style={{ background: 'rgba(255,255,255,0.08)', color: '#93c5fd', padding: '2px 6px', borderRadius: '4px', fontFamily: 'Consolas, monospace', fontSize: '12.5px' }}>
            {val.slice(1, -1)}
          </code>
        );
      } else if (val.startsWith('**') && val.endsWith('**')) {
        tokens.push(
          <strong key={tokens.length} style={{ color: '#ffffff', fontWeight: '600' }}>
            {val.slice(2, -2)}
          </strong>
        );
      } else if (val.startsWith('*') && val.endsWith('*')) {
        tokens.push(
          <em key={tokens.length} style={{ color: '#cbd5e1' }}>
            {val.slice(1, -1)}
          </em>
        );
      } else if (val.startsWith('[') && val.includes('](')) {
        const titleMatch = val.match(/\[([^\]]+)\]\(([^)]+)\)/);
        if (titleMatch) {
          tokens.push(
            <a key={tokens.length} href={titleMatch[2]} target="_blank" rel="noreferrer" style={{ color: '#60a5fa', textDecoration: 'underline' }}>
              {titleMatch[1]}
            </a>
          );
        } else {
          tokens.push(val);
        }
      }
      idx = inlineRegex.lastIndex;
    }
    if (idx < str.length) {
      tokens.push(str.substring(idx));
    }
    return tokens;
  };

  return (
    <div style={{ fontSize: '14px', lineHeight: '1.7', color: '#f4f4f5' }}>
      {parts.map((part, pIdx) => {
        if (part.type === 'code') {
          return <CodeBlock key={pIdx} code={part.code} language={part.language} />;
        }

        const lines = part.text.split('\n');
        const elements = [];
        let listItems = [];
        let listType = null;

        const flushList = () => {
          if (listItems.length > 0) {
            if (listType === 'ul') {
              elements.push(
                <ul key={`ul-${elements.length}`} style={{ margin: '8px 0', paddingLeft: '22px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  {listItems.map((item, idx) => (
                    <li key={idx} style={{ color: '#e4e4e7', lineHeight: '1.6' }}>
                      {renderInline(item)}
                    </li>
                  ))}
                </ul>
              );
            } else {
              elements.push(
                <ol key={`ol-${elements.length}`} style={{ margin: '8px 0', paddingLeft: '22px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  {listItems.map((item, idx) => (
                    <li key={idx} style={{ color: '#e4e4e7', lineHeight: '1.6' }}>
                      {renderInline(item)}
                    </li>
                  ))}
                </ol>
              );
            }
            listItems = [];
            listType = null;
          }
        };

        lines.forEach((line, lIdx) => {
          const trimmed = line.trim();

          if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
            if (listType !== 'ul') flushList();
            listType = 'ul';
            listItems.push(trimmed.slice(2));
          } else if (/^\d+\.\s/.test(trimmed)) {
            if (listType !== 'ol') flushList();
            listType = 'ol';
            listItems.push(trimmed.replace(/^\d+\.\s/, ''));
          } else {
            flushList();

            if (trimmed.startsWith('### ')) {
              elements.push(
                <h3 key={lIdx} style={{ fontSize: '16px', fontWeight: '600', color: '#ffffff', margin: '14px 0 6px 0' }}>
                  {renderInline(trimmed.slice(4))}
                </h3>
              );
            } else if (trimmed.startsWith('## ')) {
              elements.push(
                <h2 key={lIdx} style={{ fontSize: '18px', fontWeight: '600', color: '#ffffff', margin: '18px 0 8px 0', borderBottom: '1px solid rgba(255,255,255,0.06)', paddingBottom: '4px' }}>
                  {renderInline(trimmed.slice(3))}
                </h2>
              );
            } else if (trimmed.startsWith('# ')) {
              elements.push(
                <h1 key={lIdx} style={{ fontSize: '20px', fontWeight: '700', color: '#ffffff', margin: '20px 0 10px 0' }}>
                  {renderInline(trimmed.slice(2))}
                </h1>
              );
            } else if (trimmed.startsWith('> ')) {
              elements.push(
                <blockquote key={lIdx} style={{ margin: '10px 0', padding: '8px 14px', borderLeft: '3px solid #3b82f6', background: 'rgba(59, 130, 246, 0.05)', borderRadius: '0 6px 6px 0', color: '#cbd5e1' }}>
                  {renderInline(trimmed.slice(2))}
                </blockquote>
              );
            } else if (trimmed === '') {
              // blank line
            } else {
              elements.push(
                <p key={lIdx} style={{ margin: '6px 0' }}>
                  {renderInline(trimmed)}
                </p>
              );
            }
          }
        });

        flushList();
        return <div key={pIdx}>{elements}</div>;
      })}
    </div>
  );
}
