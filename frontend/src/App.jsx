import { useState } from 'react'
import DocumentUpload from './components/DocumentUpload'
import ParameterControls from './components/ParameterControls'
import ChatInterface from './components/ChatInterface'
import TheoryPanel from './components/TheoryPanel'
import './App.css'

function App() {
  const [sessionId, setSessionId] = useState(null)
  const [params, setParams] = useState({
    provider: 'groq',
    temperature: 0.7,
    topP: 1.0,
    maxTokens: 1024,
    reasoningMode: 'direct',
    chunkSize: 512,
    topK: 4,
  })

  return (
    <div className="app">
      <header className="app-header">
        <h1>RAG Context-Eng</h1>
        <p>Upload docs → Ask questions → Tune controls → Experiment in real-time</p>
      </header>

      <main className="app-main">
        <aside className="controls-panel">
          <DocumentUpload onUploaded={setSessionId} sessionId={sessionId} />
          <ParameterControls params={params} onChange={setParams} />
        </aside>

        <section className="chat-panel">
          <ChatInterface sessionId={sessionId} params={params} />
        </section>
        <TheoryPanel />
      </main>
    </div>
  )
}

export default App
