import { useState } from 'react'
import './TheoryPanel.css'

const THEORY = [
  {
    param: 'Reasoning Mode',
    range: 'Direct | CoT | AoT',
    desc: 'How the model structures its reasoning. Direct = straight answer. Chain-of-Thought = step-by-step. Atom of Thought = finer reasoning steps.',
    examples: [
      { val: 'Direct', label: 'Concise answers' },
      { val: 'CoT', label: 'Step-by-step reasoning' },
      { val: 'AoT', label: 'Detailed reasoning' },
    ],
  },
  {
    param: 'Temperature',
    range: '0 – 2',
    desc: 'Controls randomness. Low = focused, deterministic. High = diverse, creative.',
    examples: [
      { val: 0, label: 'Precise (factual Q&A)' },
      { val: 0.7, label: 'Balanced (default)' },
      { val: 1.5, label: 'Creative (brainstorming)' },
    ],
  },
  {
    param: 'Top-p (nucleus)',
    range: '0 – 1',
    desc: 'Cumulative probability cutoff. Lower = more focused. 1 = no filtering.',
    examples: [
      { val: 0.5, label: 'Conservative' },
      { val: 1.0, label: 'No filtering (default)' },
    ],
  },
  {
    param: 'Max tokens',
    range: '64 – 4096',
    desc: 'Maximum length of the model response.',
    examples: [
      { val: 256, label: 'Short answers' },
      { val: 1024, label: 'Standard' },
      { val: 2048, label: 'Long explanations' },
    ],
  },
  {
    param: 'Chunk size',
    range: '128 – 1024',
    desc: 'Size of text chunks for embedding. Smaller = more precise retrieval, larger = more context per chunk.',
    examples: [
      { val: 256, label: 'Fine-grained' },
      { val: 512, label: 'Balanced (default)' },
      { val: 1024, label: 'More context per chunk' },
    ],
  },
  {
    param: 'Top-K retrieval',
    range: '1 – 20',
    desc: 'Number of chunks to retrieve for context. Higher = more context, but may add noise.',
    examples: [
      { val: 2, label: 'Minimal context' },
      { val: 4, label: 'Standard (default)' },
      { val: 10, label: 'More context' },
    ],
  },
]

export default function TheoryPanel() {
  const [panelOpen, setPanelOpen] = useState(false)
  const [expandedItem, setExpandedItem] = useState(null)

  return (
    <aside className={`theory-panel ${panelOpen ? 'open' : ''}`}>
      <button
        type="button"
        className="theory-toggle"
        onClick={() => setPanelOpen(!panelOpen)}
        aria-label={panelOpen ? 'Collapse theory' : 'Expand theory'}
      >
        <span className="theory-toggle-icon">{panelOpen ? '◀' : '▶'}</span>
        <span className="theory-toggle-label">Theory</span>
      </button>
      <div className="theory-content">
        <h3>Theory & Examples</h3>
        <p className="theory-intro">
          Click a parameter to see description and examples.
        </p>
        {THEORY.map((item, i) => (
          <div key={i} className="theory-item">
            <button
              type="button"
              className={`theory-header-btn ${expandedItem === i ? 'expanded' : ''}`}
              onClick={() => setExpandedItem(expandedItem === i ? null : i)}
            >
              <strong>{item.param}</strong>
              <span className="theory-range">[{item.range}]</span>
              <span className="theory-chevron">{expandedItem === i ? '▼' : '▶'}</span>
            </button>
            {expandedItem === i && (
              <div className="theory-body">
                <p className="theory-desc">{item.desc}</p>
                <div className="theory-examples">
                  {item.examples.map((ex, j) => (
                    <span key={j} className="theory-example">
                      <code>{ex.val}</code> → {ex.label}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </aside>
  )
}
