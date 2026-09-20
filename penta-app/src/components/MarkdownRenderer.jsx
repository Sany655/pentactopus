import React, { useState } from 'react';

export function CodeBlock({ code, language }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = (e) => {
    e.stopPropagation();
    if (navigator?.clipboard?.writeText) {
      navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div style={{ margin: '14px 0', borderRadius: '8px', overflow: 'hidden', border: '1px solid #27272a', background: '#0a0a0f' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '6px 12px', background: '#121217', borderBottom: '1px solid #27272a', fontSize: '11px', color: '#94a3b8' }}>
        <span style={{ fontFamily: 'Consolas, monospace', textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: '600' }}>
          {language || 'code'}
        </span>
        <button
          onClick={handleCopy}
          style={{
            background: 'transparent',
            border: 'none',
            color: copied ? '#10b981' : '#a1a1aa',
            fontSize: '11px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            padding: '2px 6px',
            borderRadius: '4px',
            transition: 'color 0.15s'
          }}
          onMouseEnter={e => { if (!copied) e.currentTarget.style.color = '#fff'; }}
          onMouseLeave={e => { if (!copied) e.currentTarget.style.color = '#a1a1aa'; }}
        >
          <span>{copied ? '✓' : '📋'}</span>
          <span>{copied ? 'Copied to clipboard' : 'Copy code'}</span>
        </button>
      </div>
      <pre style={{ margin: 0, padding: '14px 16px', overflowX: 'auto', fontFamily: 'Consolas, Monaco, "Courier New", monospace', fontSize: '13px', lineHeight: '1.6', color: '#e2e8f0', background: '#09090d' }}>
        <code>{code}</code>
      </pre>
    </div>
  );
}

export default function MarkdownRenderer({ content }) {
  if (!content) return null;

  // Split content by code fences ```(lang)?\n...```
  const parts = [];
  const regex = /```([a-zA-Z0-9_-]*)\n([\s\S]*?)```/g;
  let lastIndex = 0;
  let match;

  while ((match = regex.exec(content)) !== null) {
    if (match.index > lastIndex) {
      parts.push({ type: 'markdown', text: content.substring(lastIndex, match.index) });
    }
    parts.push({ type: 'code', language: match[1] || '', code: match[2].trimEnd() });
    lastIndex = regex.lastIndex;
  }

  if (lastIndex < content.length) {
    parts.push({ type: 'markdown', text: content.substring(lastIndex) });
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
              // paragraph break
            } else {
              elements.push(
                <p key={lIdx} style={{ margin: '8px 0' }}>
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
