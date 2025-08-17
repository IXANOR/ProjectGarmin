import React from 'react'

type FileRec = {
  id: string
  name: string
  session_id: string | null
  size_bytes: number
  created_at: string
  chunk_count?: number
  transcription_language?: string | null
}

type Tab = 'pdf' | 'image' | 'audio'

export const FilesPanel: React.FC = () => {
  const [tab, setTab] = React.useState<Tab>('pdf')
  const [files, setFiles] = React.useState<FileRec[]>([])
  const [loading, setLoading] = React.useState(true)
  const [q, setQ] = React.useState('')
  const [sort, setSort] = React.useState<'name'|'date'>('date')
  const [order, setOrder] = React.useState<'asc'|'desc'>('asc')
  const [sessionId, setSessionId] = React.useState('')

  async function load() {
    setLoading(true)
    const params = new URLSearchParams()
    params.set('type', tab)
    if (q) params.set('q', q)
    params.set('sort', sort)
    params.set('order', order)
    if (sessionId) params.set('session_id', sessionId)
    const res = await fetch(`/api/files?${params.toString()}`)
    const json = await res.json()
    setFiles(json)
    setLoading(false)
  }

  React.useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tab, sort, order])

  async function del(id: string, mode: 'soft'|'hard') {
    await fetch(`/api/files/${id}?mode=${mode}`, { method: 'DELETE' })
    await load()
  }

  async function onUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const filesSel = e.target.files
    if (!filesSel || filesSel.length === 0) return
    const fd = new FormData()
    for (const f of Array.from(filesSel)) {
      fd.append('files', f)
    }
    if (sessionId) fd.append('session_id', sessionId)
    await fetch('/api/files/upload', { method: 'POST', body: fd })
    e.target.value = ''
    await load()
  }

  return (
    <div className="overflow-hidden">
      <div className="flex gap-2 mb-3">
        {(['pdf','image','audio'] as Tab[]).map(t => (
          <button
            key={t}
            data-testid={`tab-${t}`}
            className={t===tab ? 'font-bold underline' : ''}
            onClick={() => setTab(t)}
          >{t.toUpperCase()}</button>
        ))}
      </div>
      <div className="flex flex-wrap gap-2 items-center mb-3">
        <input data-testid="files-search" placeholder="Search by name" value={q} onChange={(e)=>setQ(e.target.value)} />
        <select data-testid="files-sort" value={sort} onChange={(e)=>setSort(e.target.value as any)}>
          <option value="date">Date</option>
          <option value="name">Name</option>
        </select>
        <select data-testid="files-order" value={order} onChange={(e)=>setOrder(e.target.value as any)}>
          <option value="asc">Asc</option>
          <option value="desc">Desc</option>
        </select>
        <input data-testid="files-session" placeholder="Session ID (optional)" value={sessionId} onChange={(e)=>setSessionId(e.target.value)} />
        <button data-testid="files-apply" onClick={load}>Apply</button>
        <input data-testid="files-upload" type="file" multiple onChange={onUpload} />
      </div>
      {loading ? <div>Loading…</div> : (
        <div className="overflow-auto">
        <table className="w-full text-sm table-fixed">
          <thead>
            <tr className="text-left">
              <th className="w-6/12">Name</th>
              <th className="w-2/12 text-right">Size</th>
              <th className="w-2/12">Session</th>
              <th className="w-1/12">Chunks</th>
              <th className="w-1/12"></th>
            </tr>
          </thead>
          <tbody>
          {files.filter(f => !q || f.name.toLowerCase().includes(q.toLowerCase())).map(f => (
            <tr key={f.id} className="align-top">
              <td className="truncate" title={f.name}>{f.name}</td>
              <td className="text-right">{f.size_bytes}</td>
              <td className="truncate" title={f.session_id ?? 'GLOBAL'}>{f.session_id ?? 'GLOBAL'}</td>
              <td>{f.chunk_count ?? '-'}</td>
              <td>
                <button data-testid={`soft-${f.id}`} onClick={()=>del(f.id,'soft')}>Soft delete</button>{' '}
                <button data-testid={`hard-${f.id}`} onClick={()=>del(f.id,'hard')}>Hard delete</button>
              </td>
            </tr>
          ))}
          </tbody>
        </table>
        </div>
      )}
    </div>
  )
}

export default FilesPanel


