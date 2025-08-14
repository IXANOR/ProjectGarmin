import Chat from './components/Chat'

export default function App() {
  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 flex items-center justify-center">
      <div className="p-6 border rounded-lg shadow-sm bg-white w-full max-w-2xl">
        <h1 className="text-xl font-semibold mb-4">Chat</h1>
        <span style={{ display: 'none' }}>Chat placeholder</span>
        <Chat />
      </div>
    </div>
  )
}


