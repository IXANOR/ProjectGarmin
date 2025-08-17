import React from 'react'
import Chat from './components/Chat'
import ThemeSettings from './components/ThemeSettings'
import FilesPanel from './components/FilesPanel'
import { SearchSettings } from './components/SearchSettings'
import { PersonalitySettings } from './components/PersonalitySettings'
import ModelSettings from './components/ModelSettings'

export default function App() {
  const tabs = [
    { id: 'chat', label: 'Chat' },
    { id: 'appearance', label: 'Appearance' },
    { id: 'files', label: 'Files' },
    { id: 'settings', label: 'Settings' },
  ] as const
  type TabId = typeof tabs[number]['id']
  const [active, setActive] = React.useState<TabId>('chat')

  return (
    <div className="min-h-screen flex items-start justify-center py-10 px-4">
      <div className="w-full max-w-5xl">
        <nav className="mb-4">
          <div className="inline-flex rounded-full bg-[var(--app-panel)] border" style={{ borderColor: 'var(--app-border)' }}>
            {tabs.map((t, idx) => (
              <button
                key={t.id}
                onClick={() => setActive(t.id)}
                className={`px-4 py-2 text-sm ${active===t.id ? 'font-semibold' : 'opacity-70'} ${idx===0 ? 'rounded-l-full' : ''} ${idx===tabs.length-1 ? 'rounded-r-full' : ''}`}
                style={{ borderRight: idx<tabs.length-1 ? '1px solid var(--app-border)' : undefined }}
              >{t.label}</button>
            ))}
          </div>
        </nav>

        {active === 'chat' && (
          <div className="card p-4">
            <h1 className="section-title">Chat</h1>
            <span style={{ display: 'none' }}>Chat placeholder</span>
            <Chat />
          </div>
        )}

        {active === 'appearance' && (
          <div className="card p-4">
            <h2 className="section-title">Appearance</h2>
            <ThemeSettings />
          </div>
        )}

        {active === 'files' && (
          <div className="card p-4">
            <h2 className="section-title">Files</h2>
            <FilesPanel />
          </div>
        )}

        {active === 'settings' && (
          <div className="card p-4">
            <h2 className="section-title">Model Settings</h2>
            <ModelSettings />
            <h2 className="section-title" style={{ marginTop: 16 }}>Internet Search</h2>
            <SearchSettings />
            <h2 className="section-title" style={{ marginTop: 16 }}>Personality</h2>
            <PersonalitySettings />
          </div>
        )}
      </div>
    </div>
  )
}


