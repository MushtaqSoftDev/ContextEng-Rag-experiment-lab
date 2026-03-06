import './ParameterControls.css'

const PROVIDERS = [
  { id: 'openai', label: 'OpenAI' },
  { id: 'groq', label: 'Groq' },
  { id: 'deepseek', label: 'DeepSeek' },
  { id: 'huggingface', label: 'HuggingFace flan-t5-large (CPU)' },
]

const REASONING_MODES = [
  { id: 'direct', label: 'Direct' },
  { id: 'chain_of_thought', label: 'Chain-of-Thought' },
  { id: 'atom_of_thought', label: 'Atom of Thought' },
]

export default function ParameterControls({ params, onChange }) {
  const update = (key, value) => {
    onChange({ ...params, [key]: value })
  }

  return (
    <div className="parameter-controls">
      <h3>Parameters</h3>

      <div className="control-group">
        <label>LLM Provider</label>
        <select
          value={params.provider}
          onChange={(e) => update('provider', e.target.value)}
        >
          {PROVIDERS.map((p) => (
            <option key={p.id} value={p.id}>
              {p.label}
            </option>
          ))}
        </select>
      </div>

      <div className="control-group">
        <label>Reasoning Mode</label>
        <select
          value={params.reasoningMode}
          onChange={(e) => update('reasoningMode', e.target.value)}
        >
          {REASONING_MODES.map((r) => (
            <option key={r.id} value={r.id}>
              {r.label}
            </option>
          ))}
        </select>
      </div>

      <div className="control-group slider-group">
        <label>
          Temperature <span className="value">{params.temperature.toFixed(1)}</span>
        </label>
        <input
          type="range"
          min="0"
          max="2"
          step="0.1"
          value={params.temperature}
          onChange={(e) => update('temperature', parseFloat(e.target.value))}
        />
      </div>

      <div className="control-group slider-group">
        <label>
          Top-p <span className="value">{params.topP.toFixed(2)}</span>
        </label>
        <input
          type="range"
          min="0"
          max="1"
          step="0.05"
          value={params.topP}
          onChange={(e) => update('topP', parseFloat(e.target.value))}
        />
      </div>

      <div className="control-group slider-group">
        <label>
          Max tokens <span className="value">{params.maxTokens}</span>
        </label>
        <input
          type="range"
          min="64"
          max="4096"
          step="64"
          value={params.maxTokens}
          onChange={(e) => update('maxTokens', parseInt(e.target.value, 10))}
        />
      </div>

      <div className="control-group slider-group">
        <label>
          Chunk size <span className="value">{params.chunkSize}</span>
        </label>
        <input
          type="range"
          min="128"
          max="1024"
          step="64"
          value={params.chunkSize}
          onChange={(e) => update('chunkSize', parseInt(e.target.value, 10))}
        />
      </div>

      <div className="control-group slider-group">
        <label>
          Top-K retrieval <span className="value">{params.topK}</span>
        </label>
        <input
          type="range"
          min="1"
          max="20"
          step="1"
          value={params.topK}
          onChange={(e) => update('topK', parseInt(e.target.value, 10))}
        />
      </div>
    </div>
  )
}
