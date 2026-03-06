import { useState, useRef } from 'react'
import { uploadDocuments, indexDocuments } from '../api'
import './DocumentUpload.css'

const ALLOWED = ['.pdf', '.txt', '.md']

export default function DocumentUpload({ onUploaded, sessionId }) {
  const [files, setFiles] = useState([])
  const [loading, setLoading] = useState(false)
  const [loadingPhase, setLoadingPhase] = useState('')
  const [error, setError] = useState(null)
  const inputRef = useRef(null)

  const handleSelect = (e) => {
    const selected = Array.from(e.target.files || [])
    const valid = selected.filter((f) => {
      const ext = '.' + (f.name || '').split('.').pop().toLowerCase()
      return ALLOWED.includes(ext)
    })
    setFiles((prev) => [...prev, ...valid])
    setError(null)
    e.target.value = ''
  }

  const remove = (i) => {
    setFiles((prev) => prev.filter((_, idx) => idx !== i))
  }

  const handleUpload = async () => {
    if (files.length === 0) {
      setError('Select at least one file (PDF, TXT, MD)')
      return
    }
    setLoading(true)
    setError(null)
    try {
      setLoadingPhase('uploading')
      const { session_id } = await uploadDocuments(files)
      onUploaded(session_id)
      setFiles([])
      setLoadingPhase('indexing')
      await indexDocuments(session_id)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
      setLoadingPhase('')
    }
  }

  return (
    <div className="document-upload">
      <h3>Documents</h3>
      <input
        ref={inputRef}
        type="file"
        multiple
        accept=".pdf,.txt,.md"
        onChange={handleSelect}
        style={{ display: 'none' }}
      />
      <button
        type="button"
        className="btn btn-outline"
        onClick={() => inputRef.current?.click()}
      >
        + Add files (PDF, TXT, MD)
      </button>
      {files.length > 0 && (
        <ul className="file-list">
          {files.map((f, i) => (
            <li key={i}>
              <span>{f.name}</span>
              <button type="button" className="btn-remove" onClick={() => remove(i)}>
                ×
              </button>
            </li>
          ))}
        </ul>
      )}
      {files.length > 0 && (
        <button
          type="button"
          className="btn btn-primary"
          onClick={handleUpload}
          disabled={loading}
        >
          {loading ? (loadingPhase === 'indexing' ? 'Indexing…' : 'Uploading…') : 'Upload & Index'}
        </button>
      )}
      {sessionId && (
        <p className="session-info">Session active — ready to chat</p>
      )}
      {error && <p className="error">{error}</p>}
    </div>
  )
}
